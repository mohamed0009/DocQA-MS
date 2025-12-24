"""
Embedding service supporting multiple providers (SentenceTransformers, Ollama)
"""

from typing import List
import numpy as np
import structlog
from sentence_transformers import SentenceTransformer

from ..config import settings

logger = structlog.get_logger()


class EmbeddingService:
    """Unified embedding interface supporting multiple providers"""
    
    def __init__(self):
        self.provider = settings.EMBEDDING_PROVIDER
        self.model = None
        self.dimension = settings.EMBEDDING_DIMENSION
        self._initialize()
    
    def _initialize(self):
        """Initialize embedding model based on provider"""
        try:
            if self.provider == "sentence-transformers":
                self._initialize_sentence_transformers()
            elif self.provider == "ollama":
                self._initialize_ollama()
            else:
                raise ValueError(f"Unsupported embedding provider: {self.provider}")
            
            logger.info(
                "Embedding model initialized",
                provider=self.provider,
                model=settings.EMBEDDING_MODEL,
                dimension=self.dimension
            )
            
        except Exception as e:
            logger.error("Embedding model initialization failed", error=str(e))
            raise
    
    def _initialize_sentence_transformers(self):
        """Initialize SentenceTransformers model"""
        logger.info(
            "Loading SentenceTransformers model",
            model=settings.EMBEDDING_MODEL,
            device=settings.EMBEDDING_DEVICE
        )
        
        self.model = SentenceTransformer(
            settings.EMBEDDING_MODEL,
            device=settings.EMBEDDING_DEVICE
        )
        
        # Verify dimension matches
        actual_dim = self.model.get_sentence_embedding_dimension()
        if actual_dim != settings.EMBEDDING_DIMENSION:
            logger.warning(
                "Embedding dimension mismatch",
                expected=settings.EMBEDDING_DIMENSION,
                actual=actual_dim
            )
            self.dimension = actual_dim
    
    def _initialize_ollama(self):
        """Initialize Ollama embeddings"""
        import ollama
        
        logger.info(
            "Using Ollama embeddings",
            model=settings.EMBEDDING_MODEL
        )
        
        # Test connection
        try:
            test_result = ollama.embeddings(
                model=settings.EMBEDDING_MODEL,
                prompt="test"
            )
            actual_dim = len(test_result['embedding'])
            
            if actual_dim != settings.EMBEDDING_DIMENSION:
                logger.warning(
                    "Embedding dimension mismatch",
                    expected=settings.EMBEDDING_DIMENSION,
                    actual=actual_dim
                )
                self.dimension = actual_dim
            
            logger.info("Ollama connection successful")
        except Exception as e:
            logger.error("Ollama connection test failed", error=str(e))
            raise
    
    def encode(
        self,
        texts: List[str],
        show_progress: bool = False
    ) -> np.ndarray:
        """
        Generate embeddings for texts
        
        Args:
            texts: List of text strings to embed
            show_progress: Show progress bar (for sentence-transformers)
            
        Returns:
            NumPy array of shape (len(texts), dimension)
        """
        if not texts:
            return np.array([])
        
        try:
            if self.provider == "sentence-transformers":
                return self._encode_sentence_transformers(texts, show_progress)
            elif self.provider == "ollama":
                return self._encode_ollama(texts)
        except Exception as e:
            logger.error("Encoding failed", error=str(e), num_texts=len(texts))
            raise
    
    def _encode_sentence_transformers(
        self,
        texts: List[str],
        show_progress: bool = False
    ) -> np.ndarray:
        """Encode using SentenceTransformers"""
        embeddings = self.model.encode(
            texts,
            batch_size=settings.EMBEDDING_BATCH_SIZE,
            show_progress_bar=show_progress,
            convert_to_numpy=True,
            normalize_embeddings=False  # FAISS will handle normalization if needed
        )
        
        return embeddings
    
    def _encode_ollama(self, texts: List[str]) -> np.ndarray:
        """Encode using Ollama"""
        import ollama
        
        embeddings = []
        for text in texts:
            response = ollama.embeddings(
                model=settings.EMBEDDING_MODEL,
                prompt=text
            )
            embeddings.append(response['embedding'])
        
        return np.array(embeddings, dtype=np.float32)
    
    def encode_single(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text
        
        Args:
            text: Single text string
            
        Returns:
            1D NumPy array of shape (dimension,)
        """
        result = self.encode([text])
        return result[0] if len(result) > 0 else np.array([])
    
    def get_dimension(self) -> int:
        """Get embedding dimension"""
        return self.dimension
    
    def get_model_info(self) -> dict:
        """Get information about the current embedding model"""
        return {
            "provider": self.provider,
            "model": settings.EMBEDDING_MODEL,
            "dimension": self.dimension,
            "device": settings.EMBEDDING_DEVICE if self.provider == "sentence-transformers" else "ollama",
            "batch_size": settings.EMBEDDING_BATCH_SIZE
        }


# Singleton instance
_embedding_service = None


def get_embedding_service() -> EmbeddingService:
    """Get embedding service singleton"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
