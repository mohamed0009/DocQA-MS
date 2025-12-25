"""
Pydantic schemas for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID


class QuestionRequest(BaseModel):
    """Request to ask a question"""
    question: str = Field(..., description="Question to ask", max_length=500)
    session_id: Optional[UUID] = Field(None, description="Session ID for context")
    include_sources: Optional[bool] = Field(True, description="Include source citations")
    stream: Optional[bool] = Field(False, description="Stream response")
    filters: Optional[Dict[str, Any]] = Field(None, description="Metadata filters (patient_id, date, type)")


class Citation(BaseModel):
    """Source citation"""
    source_id: str
    chunk_id: UUID
    document_id: UUID
    chunk_text: str
    similarity: float


class RetrievedChunk(BaseModel):
    """Retrieved chunk preview"""
    chunk_id: UUID
    document_id: UUID
    similarity: float
    text: str


class QuestionResponse(BaseModel):
    """Response to question"""
    query_id: UUID
    question: str
    answer: str
    sources: List[Citation]
    chunks_retrieved: int
    tokens_used: int
    model: str
    retrieval_time_ms: int
    llm_time_ms: int
    total_time_ms: int
    has_answer: bool
    retrieved_chunks: List[RetrievedChunk]


class SessionCreate(BaseModel):
    """Create new QA session"""
    user_id: str = Field(..., description="User identifier")
    session_name: Optional[str] = Field(None, description="Session name")


class SessionResponse(BaseModel):
    """QA session response"""
    session_id: UUID
    user_id: str
    session_name: Optional[str]
    total_queries: int
    total_tokens_used: int
    created_at: str


class FeedbackRequest(BaseModel):
    """User feedback on answer"""
    query_id: UUID
    rating: int = Field(..., ge=1, le=5, description="Rating 1-5")
    feedback: Optional[str] = Field(None, description="Text feedback")
