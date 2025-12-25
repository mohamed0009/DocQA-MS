"""
RAG (Retrieval Augmented Generation) pipeline
"""

import httpx
from typing import List, Dict, Any
import structlog

from ..config import settings
from ..llm import get_llm

logger = structlog.get_logger()


class RAGPipeline:
    """RAG pipeline for question answering"""
    
    def __init__(self):
        self.llm = get_llm()
        self.search_url = f"{settings.SEARCH_SERVICE_URL}/api/v1/search/search"
    
    async def retrieve_context(self, query: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant document chunks for query with optional filters
        
        Args:
            query: User question
            filters: Optional metadata filters
            
        Returns:
            List of relevant chunks with metadata
        """
        try:
            logger.info("Retrieving context", query=query, filters=filters)
            
            payload = {
                "query": query,
                "top_k": settings.RETRIEVAL_TOP_K,
                "similarity_threshold": settings.RETRIEVAL_MIN_SIMILARITY
            }
            
            if filters:
                payload["filters"] = filters
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.search_url,
                    json=payload,
                    timeout=30.0
                )
                
                response.raise_for_status()
                data = response.json()
                
                chunks = data.get("results", [])


                
                logger.info("Context retrieved", chunks_found=len(chunks))
                
                return chunks
                
        except Exception as e:
            logger.error("Context retrieval failed", error=str(e))
            raise

    # ... (format_context and build_prompt unchanged)

    # Re-adding missing methods
    def format_context(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Format retrieved chunks into context string
        """
        context = ""
        for i, chunk in enumerate(chunks):
            context += f"[Source {i+1}] (Relevance: {chunk.get('similarity', 0):.2f})\n"
            context += f"{chunk.get('chunk_text', '').strip()}\n\n"
        return context

    def build_prompt(self, question: str, context: str) -> str:
        """
        Build prompt for LLM
        """
        return f"""Use the following medical context to answer the question.
If the context doesn't contain the answer, say "I don't have enough information".
Always cite sources using [Source X] notation.

Context:
{context}

Question: {question}
Answer:"""

    async def answer_question(
        self,
        question: str,
        include_sources: bool = True,
        filters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Answer question using RAG pipeline
        
        Args:
            question: User question
            include_sources: Whether to include source citations
            filters: Optional metadata filters
            
        Returns:
            Dict with answer, sources, and metadata
        """
        try:
            # 1. Retrieve relevant chunks
            chunks = await self.retrieve_context(question, filters)

            # 2. ML Prediction Integration (EARLY INJECTION)
            if filters and "patient_id" in filters:
                try:
                    patient_id = filters["patient_id"]
                    prediction = await self._get_prediction(patient_id)
                    if prediction:
                        risk_level = prediction.get("risk_category", "unknown").upper()
                        score = prediction.get("prediction", 0)
                        factors = prediction.get("top_risk_factors", [])
                        
                        factor_text = ", ".join([f"{f['feature']} (contrib: {f['contribution']:.2f})" for f in factors[:3]])
                        
                        ml_context = (
                            f"[ML PREDICTION REPORT]\n"
                            f"Patient: {patient_id}\n"
                            f"Readmission Risk: {risk_level} ({score:.1%})\n"
                            f"Top Risk Factors: {factor_text}\n"
                            f"Model Confidence: {prediction.get('confidence', 0):.1%}\n"
                        )
                        logger.info("ML Prediction fetched", patient_id=patient_id, risk=risk_level)
                        
                        # Add as a priority chunk
                        chunks.insert(0, {
                            "chunk_id": "cccccccc-cccc-cccc-cccc-cccccccccc01",
                            "document_id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
                            "chunk_text": ml_context,
                            "similarity": 1.0,
                            "metadata": {"type": "ml_report"}
                        })
                        
                except Exception as e:
                    print(f"CRITICAL ML ERROR: {e}")
                    logger.warning("Failed to fetch ML prediction", error=str(e))
            
            if not chunks:
                return {
                    "answer": "I don't have enough information in the available documents to answer this question.",
                    "sources": [],
                    "chunks_retrieved": 0,
                    "has_answer": False
                }
            
            # 2. Format context
            context = self.format_context(chunks)
            
            
            # 7. Format context (now includes ML report)
            context = self.format_context(chunks)
            prompt = self.build_prompt(question, context)
            
            # 8. Generate answer
            llm_response = self.llm.generate(
                prompt=prompt,
                system_prompt=settings.SYSTEM_PROMPT
            )
            
            # 9. Extract citations
            citations = self._extract_citations(
                llm_response["response"],
                chunks
            ) if include_sources else []
            
            return {
                "answer": llm_response["response"],
                "sources": citations,
                "chunks_retrieved": len(chunks),
                "tokens_used": llm_response.get("tokens_used", 0),
                "model": llm_response.get("model"),
                "has_answer": True,
                "retrieved_chunks": [
                    {
                        "chunk_id": c.get("chunk_id"),
                        "document_id": c.get("document_id"),
                        "similarity": c.get("similarity"),
                        "text": c.get("chunk_text", "")[:200] + "..."  # Preview
                    }
                    for c in chunks
                ]
            }
            
        except Exception as e:
            logger.error("Question answering failed", error=str(e))
            raise
    
    async def _get_prediction(self, patient_id: str) -> Dict[str, Any]:
        """
        Get prediction from ML service
        """
        # Real patient features fetching needs to be implemented here.
        # Previously relied on mock data which has been removed.
        return None



    # ... (rest of methods)
    
    def _extract_citations(
        self,
        answer: str,
        chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extract citations from LLM response
        
        Args:
            answer: LLM generated answer
            chunks: Retrieved chunks
            
        Returns:
            List of citation objects
        """
        import re
        
        citations = []
        
        # Find all [Source X] patterns
        pattern = r'\[Source (\d+)\]'
        matches = re.findall(pattern, answer)
        
        for match in matches:
            source_idx = int(match) - 1  # Convert to 0-indexed
            
            if 0 <= source_idx < len(chunks):
                chunk = chunks[source_idx]
                
                citation = {
                    "source_id": f"Source {match}",
                    "chunk_id": chunk.get("chunk_id"),
                    "document_id": chunk.get("document_id"),
                    "chunk_text": chunk.get("chunk_text", ""),
                    "similarity": chunk.get("similarity", 0)
                }
                
                citations.append(citation)
        
        return citations
    
    async def answer_question_stream(self, question: str):
        """
        Stream answer for real-time display
        
        Args:
            question: User question
            
        Yields:
            Chunks of generated answer
        """
        # 1. Retrieve context
        chunks = await self.retrieve_context(question)
        
        if not chunks:
            yield {
                "type": "error",
                "content": "No relevant information found"
            }
            return
        
        # 2. Build prompt
        context = self.format_context(chunks)
        prompt = self.build_prompt(question, context)
        
        # 3. Stream response
        yield {"type": "sources", "content": chunks}
        
        for chunk in self.llm.generate_stream(prompt, settings.SYSTEM_PROMPT):
            yield {"type": "text", "content": chunk}


# Global RAG pipeline instance
_rag_pipeline = None


def get_rag_pipeline() -> RAGPipeline:
    """Get RAG pipeline singleton"""
    global _rag_pipeline
    if _rag_pipeline is None:
        _rag_pipeline = RAGPipeline()
    return _rag_pipeline
