"""
FAISS index manager for vector storage and search
"""

import faiss
import numpy as np
import os
import pickle
from typing import List, Tuple, Dict, Any
import structlog

from ..config import settings

logger = structlog.get_logger()


class FAISSManager:
    """FAISS index management for semantic search"""
    
    def __init__(self):
        self.index = None
        self.index_type = settings.FAISS_INDEX_TYPE
        self.dimension = settings.EMBEDDING_DIMENSION
        self.index_path = os.path.join(settings.FAISS_INDEX_PATH, "faiss.index")
        self.metadata_path = os.path.join(settings.FAISS_INDEX_PATH, "metadata.pkl")
        self.id_to_chunk = {}  # Mapping FAISS ID to chunk metadata
        self.next_id = 0
        
        self._initialize_index()
    
    def _initialize_index(self):
        """Initialize or load FAISS index"""
        try:
            # Create directory if needed
            os.makedirs(settings.FAISS_INDEX_PATH, exist_ok=True)
            
            # Try to load existing index
            if os.path.exists(self.index_path):
                self._load_index()
            else:
                self._create_index()
                
        except Exception as e:
            logger.error("Index initialization failed", error=str(e))
            raise
    
    def _create_index(self):
        """Create new FAISS index"""
        try:
            logger.info("Creating new FAISS index", type=self.index_type, dimension=self.dimension)
            
            if self.index_type == "IndexFlatL2":
                # Simple flat index (exact search)
                self.index = faiss.IndexFlatL2(self.dimension)
                
            elif self.index_type == "IndexIVFFlat":
                # Inverted file index (approximate search, faster for large datasets)
                quantizer = faiss.IndexFlatL2(self.dimension)
                self.index = faiss.IndexIVFFlat(
                    quantizer,
                    self.dimension,
                    settings.FAISS_NLIST
                )
                # Need to train before adding vectors
                self.index.nprobe = settings.FAISS_NPROBE
                
            else:
                raise ValueError(f"Unsupported index type: {self.index_type}")
            
            logger.info("FAISS index created successfully")
            
        except Exception as e:
            logger.error("Index creation failed", error=str(e))
            raise
    
    def _load_index(self):
        """Load existing FAISS index"""
        try:
            logger.info("Loading existing FAISS index", path=self.index_path)
            
            self.index = faiss.read_index(self.index_path)
            
            # Load metadata
            if os.path.exists(self.metadata_path):
                with open(self.metadata_path, 'rb') as f:
                    metadata = pickle.load(f)
                    self.id_to_chunk = metadata['id_to_chunk']
                    self.next_id = metadata['next_id']
            
            logger.info(
                "Index loaded successfully",
                total_vectors=self.index.ntotal,
                next_id=self.next_id
            )
            
        except Exception as e:
            logger.error("Index loading failed", error=str(e))
            # If loading fails, create new index
            self._create_index()
    
    def save_index(self):
        """Save FAISS index to disk"""
        try:
            logger.info("Saving FAISS index", path=self.index_path)
            
            faiss.write_index(self.index, self.index_path)
            
            # Save metadata
            metadata = {
                'id_to_chunk': self.id_to_chunk,
                'next_id': self.next_id
            }
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(metadata, f)
            
            logger.info("Index saved successfully")
            
        except Exception as e:
            logger.error("Index saving failed", error=str(e))
            raise
    
    def add_vectors(
        self,
        embeddings: np.ndarray,
        chunk_metadata: List[Dict[str, Any]]
    ) -> List[int]:
        """
        Add vectors to FAISS index
        
        Args:
            embeddings: Array of embedding vectors
            chunk_metadata: List of metadata for each chunk
            
        Returns:
            List of FAISS IDs assigned
        """
        try:
            if embeddings.shape[0] != len(chunk_metadata):
                raise ValueError("Embeddings and metadata count mismatch")
            
            # Train index if needed (for IVF indexes)
            if isinstance(self.index, faiss.IndexIVFFlat) and not self.index.is_trained:
                logger.info("Training IVF index", vectors=embeddings.shape[0])
                self.index.train(embeddings)
            
            # Add vectors
            start_id = self.next_id
            self.index.add(embeddings.astype('float32'))
            
            # Store metadata
            assigned_ids = []
            for i, metadata in enumerate(chunk_metadata):
                faiss_id = start_id + i
                self.id_to_chunk[faiss_id] = metadata
                assigned_ids.append(faiss_id)
            
            self.next_id += len(embeddings)
            
            logger.info(
                "Vectors added to index",
                count=len(embeddings),
                total_vectors=self.index.ntotal
            )
            
            # Save index
            self.save_index()
            
            return assigned_ids
            
        except Exception as e:
            logger.error("Adding vectors failed", error=str(e))
            raise
    
    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of results with scores and metadata
        """
        try:
            top_k = top_k or settings.SEARCH_TOP_K
            
            # Ensure query is 2D array
            if query_embedding.ndim == 1:
                query_embedding = query_embedding.reshape(1, -1)
            
            # Search
            distances, indices = self.index.search(
                query_embedding.astype('float32'),
                top_k
            )
            try:
                with open(r"c:\Users\HP\Desktop\MedBot-Intelligence\debug_log_ABS.txt", "a") as f_log:
                    f_log.write(f"DEBUG FAISS SEARCH: k={top_k}\n")
                    f_log.write(f"INDICES: {indices}\n")
                    f_log.write(f"DISTS: {distances}\n")
            except Exception as e:
                print(f"CONFIRMED LOG ERROR: {e}")
            
            # Format results
            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx == -1:  # No more results
                    break
                
                # Convert L2 distance to similarity score (0-1)
                similarity = 1 / (1 + dist)
                
                # Filter by threshold - MOVED TO API LAYER
                # if similarity < settings.SIMILARITY_THRESHOLD:
                #    continue
                
                metadata = self.id_to_chunk.get(int(idx), {})
                
                results.append({
                    "faiss_id": int(idx),
                    "similarity": float(similarity),
                    "distance": float(dist),
                    **metadata
                })
            
            logger.info("Search completed", results_found=len(results), top_k=top_k)
            
            return results
            
        except Exception as e:
            logger.error("Search failed", error=str(e))
            raise
    
    def delete_by_document_id(self, document_id: str):
        """
        Delete all vectors for a document
        Note: FAISS doesn't support deletion, so we need to rebuild index
        """
        # This is a placeholder - in production, consider using IndexIDMap
        logger.warning("FAISS deletion not implemented - requires index rebuild")
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        return {
            "total_vectors": self.index.ntotal,
            "dimension": self.dimension,
            "index_type": self.index_type,
            "is_trained": getattr(self.index, 'is_trained', True),
            "total_chunks": len(self.id_to_chunk)
        }


# Global FAISS manager instance
_manager = None


def get_faiss_manager() -> FAISSManager:
    """Get FAISS manager singleton"""
    global _manager
    if _manager is None:
        _manager = FAISSManager()
    return _manager
