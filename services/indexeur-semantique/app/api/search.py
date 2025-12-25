"""
API endpoints for semantic search operations
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
import time
import structlog
import uuid

from ..database import get_db
from ..models.document_chunk import DocumentChunk, SearchLog
from ..schemas.search import (
    IndexDocumentRequest,
    IndexDocumentResponse,
    SearchRequest,
    SearchResult,
    SearchResponse,
    IndexStatsResponse
)
from ..services import get_chunker, get_faiss_manager, get_bm25_manager, get_hybrid_search_service
from ..embeddings import get_embedding_generator
from ..config import settings

logger = structlog.get_logger()
router = APIRouter()


@router.post("/index", response_model=IndexDocumentResponse)
async def index_document(
    request: IndexDocumentRequest,
    db: Session = Depends(get_db)
):
    """
    Index a document for semantic search
    
    - **document_id**: UUID of the document
    - **text**: Full document text
    - **chunking_strategy**: paragraph, section, sliding_window, or semantic
    """
    
    start_time = time.time()
    
    try:
        # Get services
        chunker = get_chunker()
        embedding_generator = get_embedding_generator()
        faiss_manager = get_faiss_manager()
        bm25_manager = get_bm25_manager()
        
        # Chunk the text
        chunks = chunker.chunk_text(request.text, request.chunking_strategy)
        
        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No chunks generated from text"
            )
        
        # Generate embeddings
        chunk_texts = [chunk["text"] for chunk in chunks]
        embeddings = embedding_generator.generate_embeddings_batch(chunk_texts)
        
        # Prepare chunk metadata for FAISS
        chunk_metadata = []
        chunk_ids = []
        
        for chunk in chunks:
            # Save chunk to database
            db_chunk = DocumentChunk(
                document_id=str(request.document_id),
                chunk_index=chunk["index"],
                chunk_text=chunk["text"],
                chunking_strategy=request.chunking_strategy,
                start_position=chunk.get("start"),
                end_position=chunk.get("end"),
                embedding_model=settings.EMBEDDING_MODEL
            )
            db.add(db_chunk)
            db.flush()  # Get ID without committing
            
            chunk_meta = {
                "chunk_id": str(db_chunk.id),
                "document_id": str(request.document_id),
                "chunk_index": chunk["index"],
                "chunk_text": chunk["text"]
            }
            # Merge with request metadata (e.g. including patient_id)
            if request.metadata:
                chunk_meta.update(request.metadata)
                
            chunk_metadata.append(chunk_meta)
            chunk_ids.append(db_chunk.id)
        
        # Add to FAISS index
        faiss_ids = faiss_manager.add_vectors(embeddings, chunk_metadata)
        
        # Add to BM25 index (Lexical)
        try:
            bm25_manager.add_documents(chunk_texts, chunk_metadata)
        except Exception as e:
            logger.error("BM25 indexing failed (continuing with Semantic only)", error=str(e))
        
        # Update FAISS IDs in database
        for chunk_id, faiss_id in zip(chunk_ids, faiss_ids):
            db.query(DocumentChunk).filter(
                DocumentChunk.id == chunk_id
            ).update({"faiss_index_id": faiss_id})
        
        db.commit()
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        logger.info(
            "Document indexed successfully",
            document_id=str(request.document_id),
            chunks=len(chunks),
            processing_time_ms=processing_time_ms
        )
        
        return IndexDocumentResponse(
            document_id=request.document_id,
            chunks_created=len(chunks),
            embeddings_generated=len(embeddings),
            faiss_ids=faiss_ids,
            processing_time_ms=processing_time_ms
        )
        
    except Exception as e:
        db.rollback()
        logger.error("Indexing failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Indexing failed: {str(e)}"
        )


@router.post("/search", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    db: Session = Depends(get_db),
    user_id: str = None
):
    """
    Search for similar document chunks
    
    - **query**: Search query text
    - **top_k**: Number of results to return
    - **similarity_threshold**: Minimum similarity score (0-1)
    """
    
    search_mode = request.search_mode or "hybrid"
    


    # Force Reload Trigger
    start_time = time.time()
    
    try:
        # Get services
        embedding_generator = get_embedding_generator()
        faiss_manager = get_faiss_manager()
        bm25_manager = get_bm25_manager()
        hybrid_service = get_hybrid_search_service()
        
        search_mode = request.search_mode or "hybrid"
        embedding_time_ms = 0
        fusion_strategy = request.fusion_strategy
        
        # Adjust top_k if filters are present to account for filtering
        effective_top_k = request.top_k
        if request.filters:
            effective_top_k = request.top_k * 5  # Fetch more to allow for filtering
            
        # Perform search based on mode
        if search_mode == "semantic":
            # Pure semantic search
            embedding_start = time.time()
            query_embedding = embedding_generator.generate_embedding(request.query)
            embedding_time_ms = int((time.time() - embedding_start) * 1000)
            
            faiss_results = faiss_manager.search(
                query_embedding,
                top_k=effective_top_k
            )
            
            filtered_results = faiss_results # Disabled threshold filter
            
            raw_results = filtered_results
            
        elif search_mode == "lexical":
            # Pure BM25 search
            bm25_results = bm25_manager.search(
                request.query,
                top_k=effective_top_k
            )
            raw_results = bm25_results
            
        elif search_mode == "hybrid":
            # Hybrid search
            embedding_start = time.time()
            query_embedding = embedding_generator.generate_embedding(request.query)
            embedding_time_ms = int((time.time() - embedding_start) * 1000)
            
            # Get semantic results
            semantic_results = faiss_manager.search(
                query_embedding,
                top_k=effective_top_k * 2  # Get more for fusion
            )
            # semantic_results = [
            #     r for r in semantic_results
            #     if r["similarity"] >= request.similarity_threshold
            # ]
            
            # Get lexical results
            lexical_results = bm25_manager.search(
                request.query,
                top_k=effective_top_k * 2  # Get more for fusion
            )
            
            # Combine using hybrid search service
            raw_results = hybrid_service.hybrid_search(
                semantic_results=semantic_results,
                lexical_results=lexical_results,
                fusion_strategy=fusion_strategy,
                top_k=effective_top_k,
                semantic_weight=request.semantic_weight,
                lexical_weight=request.lexical_weight
            )
            
            fusion_strategy = fusion_strategy or settings.HYBRID_SEARCH_MODE
            
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid search_mode: {search_mode}. Must be 'semantic', 'lexical', or 'hybrid'"
            )
        
        # Apply Metadata Filters
        if request.filters:
            filtered_raw_results = []
            for result in raw_results:
                metadata = result.get("metadata", {})
                match = True
                for key, value in request.filters.items():
                    # Handle special date_range filter if needed, otherwise direct match
                    if key == "date_range":
                        # Skip sophisticated date logic for now, or implement basic check
                        pass 
                    elif key not in metadata or str(metadata[key]).lower() != str(value).lower():
                        # Try case-insensitive string comparison
                        match = False
                        break
                
                if match:
                    filtered_raw_results.append(result)
            
            # Slice to requested top_k after filtering
            raw_results = filtered_raw_results[:request.top_k]
        else:
             # Ensure we respect original top_k if we fetched more
             raw_results = raw_results[:request.top_k]


        # Format results
        results = []
        for result in raw_results:
            results.append(SearchResult(
                chunk_id=result["chunk_id"],
                document_id=result["document_id"],
                chunk_text=result["chunk_text"],
                similarity=result.get("similarity", result.get("hybrid_score", result.get("bm25_score", 0))),
                chunk_index=result.get("chunk_index", 0),
                metadata=result.get("metadata", {})
            ))
        
        search_time_ms = int((time.time() - start_time) * 1000)
        
        # Log search
        search_log = SearchLog(
            query=request.query,
            query_embedding_model=settings.EMBEDDING_MODEL,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold,
            results=[
                {
                    "chunk_id": str(r.chunk_id),
                    "document_id": str(r.document_id),
                    "similarity": r.similarity
                }
                for r in results
            ],
            results_count=len(results),
            search_time_ms=search_time_ms,
            embedding_time_ms=embedding_time_ms,
            user_id=user_id
        )
        db.add(search_log)
        db.commit()
        
        logger.info(
            "Search completed",
            query=request.query,
            search_mode=search_mode,
            results_found=len(results),
            search_time_ms=search_time_ms
        )
        
        return SearchResponse(
            query=request.query,
            results=results,
            results_count=len(results),
            search_time_ms=search_time_ms,
            embedding_time_ms=embedding_time_ms,
            search_mode=search_mode,
            fusion_strategy=fusion_strategy
        )
        
    except Exception as e:
        logger.error("Search failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/stats", response_model=IndexStatsResponse)
async def get_stats(db: Session = Depends(get_db)):
    """Get index statistics"""
    
    try:
        faiss_manager = get_faiss_manager()
        faiss_stats = faiss_manager.get_stats()
        
        # Count documents
        total_documents = db.query(DocumentChunk.document_id).distinct().count()
        
        return IndexStatsResponse(
            total_vectors=faiss_stats["total_vectors"],
            total_chunks=faiss_stats["total_chunks"],
            total_documents=total_documents,
            dimension=faiss_stats["dimension"],
            index_type=faiss_stats["index_type"],
            is_trained=faiss_stats["is_trained"]
        )
        
    except Exception as e:
        logger.error("Stats retrieval failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Stats retrieval failed: {str(e)}"
        )


@router.delete("/document/{document_id}")
async def delete_document(document_id: str, db: Session = Depends(get_db)):
    """Delete all chunks for a document"""
    
    try:
        # Delete from BM25 index
        bm25_manager = get_bm25_manager()
        bm25_manager.delete_by_document_id(document_id)
        
        # Delete from database
        deleted = db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document_id
        ).delete()
        
        db.commit()
        
        logger.info("Document deleted", document_id=document_id, chunks_deleted=deleted)
        
        return {"message": f"Deleted {deleted} chunks", "document_id": document_id}
        
    except Exception as e:
        db.rollback()
        logger.error("Deletion failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Deletion failed: {str(e)}"
        )
