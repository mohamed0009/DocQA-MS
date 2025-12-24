"""
Hybrid search service combining BM25 and semantic search
"""

from typing import List, Dict, Any, Optional
import structlog
import numpy as np

from ..config import settings

logger = structlog.get_logger()


class HybridSearchService:
    """Orchestrates hybrid search combining BM25 and semantic search"""
    
    def __init__(self):
        self.rrf_k = settings.RRF_K
        self.semantic_weight = settings.HYBRID_SEMANTIC_WEIGHT
        self.lexical_weight = settings.HYBRID_LEXICAL_WEIGHT
    
    def reciprocal_rank_fusion(
        self,
        semantic_results: List[Dict[str, Any]],
        lexical_results: List[Dict[str, Any]],
        k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Combine results using Reciprocal Rank Fusion (RRF)
        
        RRF formula: score = sum(1 / (k + rank))
        
        Args:
            semantic_results: Results from semantic search
            lexical_results: Results from BM25 search
            k: RRF constant (default: 60)
            
        Returns:
            Merged and re-ranked results
        """
        k = k or self.rrf_k
        
        # Create mapping of chunk_id to RRF score
        rrf_scores = {}
        all_results = {}
        
        # Process semantic results
        for rank, result in enumerate(semantic_results, start=1):
            chunk_id = str(result['chunk_id'])
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0) + (1 / (k + rank))
            all_results[chunk_id] = result
        
        # Process lexical results
        for rank, result in enumerate(lexical_results, start=1):
            chunk_id = str(result['chunk_id'])
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0) + (1 / (k + rank))
            
            # If not already in results, add it
            if chunk_id not in all_results:
                all_results[chunk_id] = result
        
        # Sort by RRF score
        sorted_chunks = sorted(
            rrf_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Build final results
        merged_results = []
        for chunk_id, rrf_score in sorted_chunks:
            result = all_results[chunk_id].copy()
            result['hybrid_score'] = float(rrf_score)
            result['fusion_method'] = 'rrf'
            merged_results.append(result)
        
        logger.info(
            "RRF fusion completed",
            semantic_count=len(semantic_results),
            lexical_count=len(lexical_results),
            merged_count=len(merged_results)
        )
        
        return merged_results
    
    def weighted_fusion(
        self,
        semantic_results: List[Dict[str, Any]],
        lexical_results: List[Dict[str, Any]],
        semantic_weight: Optional[float] = None,
        lexical_weight: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Combine results using weighted score fusion
        
        Args:
            semantic_results: Results from semantic search
            lexical_results: Results from BM25 search
            semantic_weight: Weight for semantic scores (0-1)
            lexical_weight: Weight for lexical scores (0-1)
            
        Returns:
            Merged and re-ranked results
        """
        semantic_weight = semantic_weight or self.semantic_weight
        lexical_weight = lexical_weight or self.lexical_weight
        
        # Normalize weights
        total_weight = semantic_weight + lexical_weight
        semantic_weight = semantic_weight / total_weight
        lexical_weight = lexical_weight / total_weight
        
        # Normalize scores for each result set
        semantic_scores = self._normalize_scores(
            semantic_results,
            score_key='similarity'
        )
        lexical_scores = self._normalize_scores(
            lexical_results,
            score_key='bm25_score'
        )
        
        # Combine scores
        combined_scores = {}
        all_results = {}
        
        # Add semantic scores
        for result, norm_score in zip(semantic_results, semantic_scores):
            chunk_id = str(result['chunk_id'])
            combined_scores[chunk_id] = semantic_weight * norm_score
            all_results[chunk_id] = result
        
        # Add lexical scores
        for result, norm_score in zip(lexical_results, lexical_scores):
            chunk_id = str(result['chunk_id'])
            combined_scores[chunk_id] = combined_scores.get(chunk_id, 0) + (lexical_weight * norm_score)
            
            if chunk_id not in all_results:
                all_results[chunk_id] = result
        
        # Sort by combined score
        sorted_chunks = sorted(
            combined_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Build final results
        merged_results = []
        for chunk_id, combined_score in sorted_chunks:
            result = all_results[chunk_id].copy()
            result['hybrid_score'] = float(combined_score)
            result['fusion_method'] = 'weighted'
            result['semantic_weight'] = semantic_weight
            result['lexical_weight'] = lexical_weight
            merged_results.append(result)
        
        logger.info(
            "Weighted fusion completed",
            semantic_count=len(semantic_results),
            lexical_count=len(lexical_results),
            merged_count=len(merged_results),
            semantic_weight=semantic_weight,
            lexical_weight=lexical_weight
        )
        
        return merged_results
    
    def _normalize_scores(
        self,
        results: List[Dict[str, Any]],
        score_key: str
    ) -> List[float]:
        """
        Normalize scores to 0-1 range using min-max normalization
        
        Args:
            results: List of results
            score_key: Key to extract scores from
            
        Returns:
            List of normalized scores
        """
        if not results:
            return []
        
        scores = [result.get(score_key, 0) for result in results]
        
        min_score = min(scores)
        max_score = max(scores)
        
        # Avoid division by zero
        if max_score == min_score:
            return [1.0] * len(scores)
        
        normalized = [
            (score - min_score) / (max_score - min_score)
            for score in scores
        ]
        
        return normalized
    
    def hybrid_search(
        self,
        semantic_results: List[Dict[str, Any]],
        lexical_results: List[Dict[str, Any]],
        fusion_strategy: Optional[str] = None,
        top_k: Optional[int] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining semantic and lexical results
        
        Args:
            semantic_results: Results from semantic search
            lexical_results: Results from BM25 search
            fusion_strategy: "rrf" or "weighted" (default: from config)
            top_k: Number of final results to return
            **kwargs: Additional parameters for fusion methods
            
        Returns:
            Merged and re-ranked results
        """
        fusion_strategy = fusion_strategy or settings.HYBRID_SEARCH_MODE
        top_k = top_k or settings.SEARCH_TOP_K
        
        # Handle edge cases
        if not semantic_results and not lexical_results:
            logger.warning("Both semantic and lexical results are empty")
            return []
        
        if not semantic_results:
            logger.info("Only lexical results available, returning BM25 results")
            return lexical_results[:top_k]
        
        if not lexical_results:
            logger.info("Only semantic results available, returning semantic results")
            return semantic_results[:top_k]
        
        # Perform fusion
        if fusion_strategy == "rrf":
            merged_results = self.reciprocal_rank_fusion(
                semantic_results,
                lexical_results,
                k=kwargs.get('rrf_k')
            )
        elif fusion_strategy == "weighted":
            merged_results = self.weighted_fusion(
                semantic_results,
                lexical_results,
                semantic_weight=kwargs.get('semantic_weight'),
                lexical_weight=kwargs.get('lexical_weight')
            )
        else:
            raise ValueError(f"Unknown fusion strategy: {fusion_strategy}")
        
        # Return top-k results
        return merged_results[:top_k]


# Global hybrid search service instance
_hybrid_search_service = None


def get_hybrid_search_service() -> HybridSearchService:
    """Get hybrid search service singleton"""
    global _hybrid_search_service
    if _hybrid_search_service is None:
        _hybrid_search_service = HybridSearchService()
    return _hybrid_search_service
