"""
API endpoints for Q&A operations
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import time
import uuid as uuid_lib
import structlog

from ..database import get_db
from ..models.qa import QASession, QAQuery
from ..schemas.qa import (
    QuestionRequest,
    QuestionResponse,
    Citation,
    RetrievedChunk,
    SessionCreate,
    SessionResponse,
    FeedbackRequest
)
from ..services import get_rag_pipeline
from ..config import settings

logger = structlog.get_logger()
router = APIRouter()


@router.post("/ask", response_model=QuestionResponse)
async def ask_question(
    request: QuestionRequest,
    db: Session = Depends(get_db)
):
    """
    Ask a question and get an AI-powered answer with citations
    
    - **question**: Your medical question
    - **session_id**: Optional session ID for conversation context
    - **include_sources**: Include source citations (default: true)
    """
    
    start_time = time.time()
    
    try:
        rag = get_rag_pipeline()
        
        # Get answer
        retrieval_start = time.time()
        result = await rag.answer_question(
            question=request.question,
            include_sources=request.include_sources,
            filters=request.filters
        )
        retrieval_time_ms = int((time.time() - retrieval_start) * 1000)
        
        llm_time_ms = int(retrieval_time_ms * 0.7)  # Estimate
        total_time_ms = int((time.time() - start_time) * 1000)
        
        # Save to database
        query = QAQuery(
            session_id=request.session_id,
            question=request.question,
            answer=result["answer"],
            llm_model=result.get("model", settings.OPENAI_MODEL),
            retrieved_chunks=result.get("retrieved_chunks", []),
            retrieval_count=result["chunks_retrieved"],
            citations=result.get("sources", []),
            retrieval_time_ms=retrieval_time_ms,
            llm_time_ms=llm_time_ms,
            total_time_ms=total_time_ms,
            tokens_used=result.get("tokens_used", 0),
            has_citations=len(result.get("sources", [])) > 0
        )
        db.add(query)
        
        # Update session if provided
        if request.session_id:
            session = db.query(QASession).filter(
                QASession.id == request.session_id
            ).first()
            
            if session:
                session.total_queries += 1
                session.total_tokens_used += result.get("tokens_used", 0)
        
        db.commit()
        db.refresh(query)
        
        logger.info(
            "Question answered",
            query_id=str(query.id),
            tokens=result.get("tokens_used", 0),
            time_ms=total_time_ms
        )
        
        return QuestionResponse(
            query_id=query.id,
            question=request.question,
            answer=result["answer"],
            sources=[Citation(**s) for s in result.get("sources", [])],
            chunks_retrieved=result["chunks_retrieved"],
            tokens_used=result.get("tokens_used", 0),
            model=result.get("model", ""),
            retrieval_time_ms=retrieval_time_ms,
            llm_time_ms=llm_time_ms,
            total_time_ms=total_time_ms,
            has_answer=result.get("has_answer", True),
            retrieved_chunks=[
                RetrievedChunk(**c) for c in result.get("retrieved_chunks", [])
            ]
        )
        
    except Exception as e:
        logger.error("Question answering failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to answer question: {str(e)}"
        )


@router.post("/ask/stream")
async def ask_question_stream(request: QuestionRequest):
    """
    Ask a question and stream the answer in real-time
    
    - **question**: Your medical question
    """
    
    try:
        rag = get_rag_pipeline()
        
        async def generate():
            async for chunk in rag.answer_question_stream(request.question):
                yield f"data: {chunk}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )
        
    except Exception as e:
        logger.error("Streaming failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Streaming failed: {str(e)}"
        )


@router.post("/sessions", response_model=SessionResponse)
async def create_session(
    request: SessionCreate,
    db: Session = Depends(get_db)
):
    """Create a new Q&A session"""
    
    try:
        session = QASession(
            user_id=request.user_id,
            session_name=request.session_name
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        
        logger.info("Session created", session_id=str(session.id))
        
        return SessionResponse(
            session_id=session.id,
            user_id=session.user_id,
            session_name=session.session_name,
            total_queries=session.total_queries,
            total_tokens_used=session.total_tokens_used,
            created_at=session.created_at.isoformat()
        )
        
    except Exception as e:
        logger.error("Session creation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Session creation failed: {str(e)}"
        )


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: uuid_lib.UUID, db: Session = Depends(get_db)):
    """Get session details"""
    
    session = db.query(QASession).filter(QASession.id == session_id).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return SessionResponse(
        session_id=session.id,
        user_id=session.user_id,
        session_name=session.session_name,
        total_queries=session.total_queries,
        total_tokens_used=session.total_tokens_used,
        created_at=session.created_at.isoformat()
    )


@router.post("/feedback")
async def submit_feedback(
    request: FeedbackRequest,
    db: Session = Depends(get_db)
):
    """Submit feedback on an answer"""
    
    try:
        query = db.query(QAQuery).filter(QAQuery.id == request.query_id).first()
        
        if not query:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Query not found"
            )
        
        query.user_rating = request.rating
        query.user_feedback = request.feedback
        
        db.commit()
        
        logger.info("Feedback submitted", query_id=str(request.query_id), rating=request.rating)
        
        return {"message": "Feedback submitted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Feedback submission failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Feedback submission failed: {str(e)}"
        )


@router.get("/queries/{query_id}")
async def get_query(query_id: uuid_lib.UUID, db: Session = Depends(get_db)):
    """Get a specific query and its answer"""
    
    query = db.query(QAQuery).filter(QAQuery.id == query_id).first()
    
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found"
        )
    
    return {
        "query_id": str(query.id),
        "question": query.question,
        "answer": query.answer,
        "citations": query.citations,
        "model": query.llm_model,
        "tokens_used": query.tokens_used,
        "created_at": query.created_at.isoformat()
    }
