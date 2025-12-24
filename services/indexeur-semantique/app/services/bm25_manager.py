"""
BM25 index manager for lexical search
"""

import os
import pickle
from typing import List, Dict, Any, Optional
import structlog
from rank_bm25 import BM25Okapi
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

from ..config import settings

logger = structlog.get_logger()

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)


class BM25Manager:
    """BM25 index management for lexical search"""
    
    def __init__(self):
        self.bm25 = None
        self.corpus = []  # List of tokenized documents
        self.metadata = []  # Metadata for each document
        self.index_path = os.path.join(settings.BM25_INDEX_PATH, "bm25_index.pkl")
        self.stop_words = set(stopwords.words('english'))
        
        # BM25 parameters
        self.k1 = settings.BM25_K1
        self.b = settings.BM25_B
        
        self._initialize_index()
    
    def _initialize_index(self):
        """Initialize or load BM25 index"""
        try:
            # Create directory if needed
            os.makedirs(settings.BM25_INDEX_PATH, exist_ok=True)
            
            # Try to load existing index
            if os.path.exists(self.index_path):
                self._load_index()
            else:
                logger.info("No existing BM25 index found, starting fresh")
                
        except Exception as e:
            logger.error("BM25 index initialization failed", error=str(e))
            raise
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize and preprocess text
        
        Args:
            text: Input text
            
        Returns:
            List of tokens
        """
        try:
            # Tokenize
            tokens = word_tokenize(text.lower())
            
            # Remove stopwords and non-alphabetic tokens
            tokens = [
                token for token in tokens
                if token.isalnum() and token not in self.stop_words
            ]
            
            return tokens
            
        except Exception as e:
            logger.error("Tokenization failed", error=str(e))
            return []
    
    def add_documents(
        self,
        texts: List[str],
        chunk_metadata: List[Dict[str, Any]]
    ):
        """
        Add documents to BM25 index
        
        Args:
            texts: List of document texts
            chunk_metadata: List of metadata for each document
        """
        try:
            if len(texts) != len(chunk_metadata):
                raise ValueError("Texts and metadata count mismatch")
            
            # Tokenize all documents
            tokenized_docs = [self._tokenize(text) for text in texts]
            
            # Add to corpus
            self.corpus.extend(tokenized_docs)
            self.metadata.extend(chunk_metadata)
            
            # Rebuild BM25 index
            self.bm25 = BM25Okapi(
                self.corpus,
                k1=self.k1,
                b=self.b
            )
            
            logger.info(
                "Documents added to BM25 index",
                count=len(texts),
                total_documents=len(self.corpus)
            )
            
            # Save index
            self.save_index()
            
        except Exception as e:
            logger.error("Adding documents to BM25 failed", error=str(e))
            raise
    
    def search(
        self,
        query: str,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for documents using BM25
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of results with scores and metadata
        """
        try:
            if self.bm25 is None or len(self.corpus) == 0:
                logger.warning("BM25 index is empty")
                return []
            
            # Tokenize query
            tokenized_query = self._tokenize(query)
            
            if not tokenized_query:
                logger.warning("Query tokenization resulted in empty tokens")
                return []
            
            # Get BM25 scores
            scores = self.bm25.get_scores(tokenized_query)
            
            # Get top-k indices
            top_indices = scores.argsort()[-top_k:][::-1]
            
            # Format results
            results = []
            for idx in top_indices:
                score = float(scores[idx])
                
                # Skip zero scores
                if score <= 0:
                    continue
                
                metadata = self.metadata[idx]
                
                results.append({
                    "bm25_score": score,
                    "rank": len(results) + 1,
                    **metadata
                })
            
            logger.info(
                "BM25 search completed",
                query=query,
                results_found=len(results),
                top_k=top_k
            )
            
            return results
            
        except Exception as e:
            logger.error("BM25 search failed", error=str(e))
            raise
    
    def save_index(self):
        """Save BM25 index to disk"""
        try:
            logger.info("Saving BM25 index", path=self.index_path)
            
            index_data = {
                'corpus': self.corpus,
                'metadata': self.metadata,
                'k1': self.k1,
                'b': self.b
            }
            
            with open(self.index_path, 'wb') as f:
                pickle.dump(index_data, f)
            
            logger.info("BM25 index saved successfully")
            
        except Exception as e:
            logger.error("BM25 index saving failed", error=str(e))
            raise
    
    def _load_index(self):
        """Load BM25 index from disk"""
        try:
            logger.info("Loading existing BM25 index", path=self.index_path)
            
            with open(self.index_path, 'rb') as f:
                index_data = pickle.load(f)
            
            self.corpus = index_data['corpus']
            self.metadata = index_data['metadata']
            self.k1 = index_data.get('k1', self.k1)
            self.b = index_data.get('b', self.b)
            
            # Rebuild BM25 object
            if self.corpus:
                self.bm25 = BM25Okapi(
                    self.corpus,
                    k1=self.k1,
                    b=self.b
                )
            
            logger.info(
                "BM25 index loaded successfully",
                total_documents=len(self.corpus)
            )
            
        except Exception as e:
            logger.error("BM25 index loading failed", error=str(e))
            # If loading fails, start fresh
            self.corpus = []
            self.metadata = []
            self.bm25 = None
    
    def delete_by_document_id(self, document_id: str):
        """
        Delete all chunks for a document
        
        Args:
            document_id: Document UUID to delete
        """
        try:
            # Find indices to remove
            indices_to_remove = [
                i for i, meta in enumerate(self.metadata)
                if meta.get('document_id') == document_id
            ]
            
            if not indices_to_remove:
                logger.warning("No documents found to delete", document_id=document_id)
                return
            
            # Remove in reverse order to maintain indices
            for idx in sorted(indices_to_remove, reverse=True):
                del self.corpus[idx]
                del self.metadata[idx]
            
            # Rebuild BM25 index
            if self.corpus:
                self.bm25 = BM25Okapi(
                    self.corpus,
                    k1=self.k1,
                    b=self.b
                )
            else:
                self.bm25 = None
            
            logger.info(
                "Documents deleted from BM25 index",
                document_id=document_id,
                chunks_deleted=len(indices_to_remove)
            )
            
            # Save updated index
            self.save_index()
            
        except Exception as e:
            logger.error("BM25 deletion failed", error=str(e))
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get BM25 index statistics"""
        return {
            "total_documents": len(self.corpus),
            "k1": self.k1,
            "b": self.b,
            "has_index": self.bm25 is not None
        }


# Global BM25 manager instance
_bm25_manager = None


def get_bm25_manager() -> BM25Manager:
    """Get BM25 manager singleton"""
    global _bm25_manager
    if _bm25_manager is None:
        _bm25_manager = BM25Manager()
    return _bm25_manager
