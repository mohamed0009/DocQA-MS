"""
Pydantic schemas for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID


class IndexDocumentRequest(BaseModel):
    """Request to index a document"""
    document_id: UUID = Field(..., description="Document UUID")
    text: str = Field(..., description="Document text to index")
    chunking_strategy: Optional[str] = Field("paragraph", description="Chunking strategy")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class IndexDocumentResponse(BaseModel):
    """Response after indexing"""
    document_id: UUID
    chunks_created: int
    embeddings_generated: int
    faiss_ids: List[int]
    processing_time_ms: int


class SearchRequest(BaseModel):
    """Request to search for similar documents"""
    query: str = Field(..., description="Search query")
    top_k: Optional[int] = Field(10, description="Number of results to return")
    similarity_threshold: Optional[float] = Field(0.7, description="Minimum similarity score")
    search_mode: Optional[str] = Field("hybrid", description="Search mode: semantic, lexical, or hybrid")
    fusion_strategy: Optional[str] = Field(None, description="Fusion strategy: rrf or weighted (for hybrid mode)")
    semantic_weight: Optional[float] = Field(None, description="Weight for semantic search (0-1)")
    lexical_weight: Optional[float] = Field(None, description="Weight for lexical search (0-1)")


class SearchResult(BaseModel):
    """Single search result"""
    chunk_id: UUID
    document_id: UUID
    chunk_text: str
    similarity: float
    chunk_index: int
    metadata: Dict[str, Any]


class SearchResponse(BaseModel):
    """Response with search results"""
    query: str
    results: List[SearchResult]
    results_count: int
    search_time_ms: int
    embedding_time_ms: int
    search_mode: str
    fusion_strategy: Optional[str] = None


class IndexStatsResponse(BaseModel):
    """Index statistics"""
    total_vectors: int
    total_chunks: int
    total_documents: int
    dimension: int
    index_type: str
    is_trained: bool
