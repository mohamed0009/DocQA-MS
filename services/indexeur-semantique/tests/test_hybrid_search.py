"""
Unit tests for hybrid search service
"""

import pytest
from app.services.hybrid_search import HybridSearchService


@pytest.fixture
def hybrid_service():
    """Create hybrid search service instance"""
    return HybridSearchService()


@pytest.fixture
def sample_semantic_results():
    """Sample semantic search results"""
    return [
        {
            "chunk_id": "1",
            "document_id": "doc1",
            "chunk_text": "Diabetes is a chronic disease",
            "similarity": 0.95,
            "chunk_index": 0
        },
        {
            "chunk_id": "2",
            "document_id": "doc1",
            "chunk_text": "Insulin resistance causes problems",
            "similarity": 0.85,
            "chunk_index": 1
        },
        {
            "chunk_id": "3",
            "document_id": "doc2",
            "chunk_text": "Heart disease complications",
            "similarity": 0.75,
            "chunk_index": 0
        }
    ]


@pytest.fixture
def sample_lexical_results():
    """Sample BM25 search results"""
    return [
        {
            "chunk_id": "2",
            "document_id": "doc1",
            "chunk_text": "Insulin resistance causes problems",
            "bm25_score": 5.2,
            "chunk_index": 1
        },
        {
            "chunk_id": "4",
            "document_id": "doc3",
            "chunk_text": "Type 2 diabetes treatment",
            "bm25_score": 4.8,
            "chunk_index": 0
        },
        {
            "chunk_id": "1",
            "document_id": "doc1",
            "chunk_text": "Diabetes is a chronic disease",
            "bm25_score": 3.5,
            "chunk_index": 0
        }
    ]


def test_rrf_fusion(hybrid_service, sample_semantic_results, sample_lexical_results):
    """Test Reciprocal Rank Fusion"""
    results = hybrid_service.reciprocal_rank_fusion(
        sample_semantic_results,
        sample_lexical_results,
        k=60
    )
    
    assert len(results) > 0
    # Should have unique chunks from both result sets
    chunk_ids = [r["chunk_id"] for r in results]
    assert "1" in chunk_ids  # In both
    assert "2" in chunk_ids  # In both
    assert "3" in chunk_ids  # Only semantic
    assert "4" in chunk_ids  # Only lexical
    
    # Results should have hybrid_score
    assert all("hybrid_score" in r for r in results)
    assert all("fusion_method" in r for r in results)
    
    # Scores should be descending
    scores = [r["hybrid_score"] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_rrf_chunk_in_both_ranks_higher(hybrid_service):
    """Test that chunks appearing in both result sets rank higher with RRF"""
    semantic_results = [
        {"chunk_id": "1", "document_id": "doc1", "chunk_text": "text1", "similarity": 0.9, "chunk_index": 0},
        {"chunk_id": "2", "document_id": "doc1", "chunk_text": "text2", "similarity": 0.8, "chunk_index": 1}
    ]
    
    lexical_results = [
        {"chunk_id": "1", "document_id": "doc1", "chunk_text": "text1", "bm25_score": 5.0, "chunk_index": 0},
        {"chunk_id": "3", "document_id": "doc2", "chunk_text": "text3", "bm25_score": 4.5, "chunk_index": 0}
    ]
    
    results = hybrid_service.reciprocal_rank_fusion(semantic_results, lexical_results)
    
    # Chunk 1 appears in both, should rank highest
    assert results[0]["chunk_id"] == "1"


def test_weighted_fusion(hybrid_service, sample_semantic_results, sample_lexical_results):
    """Test weighted score fusion"""
    results = hybrid_service.weighted_fusion(
        sample_semantic_results,
        sample_lexical_results,
        semantic_weight=0.7,
        lexical_weight=0.3
    )
    
    assert len(results) > 0
    # Results should have hybrid_score and weights
    assert all("hybrid_score" in r for r in results)
    assert all("fusion_method" in r for r in results)
    assert all(r["fusion_method"] == "weighted" for r in results)
    
    # Scores should be descending
    scores = [r["hybrid_score"] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_weighted_fusion_equal_weights(hybrid_service, sample_semantic_results, sample_lexical_results):
    """Test weighted fusion with equal weights"""
    results = hybrid_service.weighted_fusion(
        sample_semantic_results,
        sample_lexical_results,
        semantic_weight=0.5,
        lexical_weight=0.5
    )
    
    assert len(results) > 0
    assert all(r["semantic_weight"] == 0.5 for r in results)
    assert all(r["lexical_weight"] == 0.5 for r in results)


def test_normalize_scores(hybrid_service):
    """Test score normalization"""
    results = [
        {"score": 10.0},
        {"score": 5.0},
        {"score": 2.0}
    ]
    
    normalized = hybrid_service._normalize_scores(results, "score")
    
    assert len(normalized) == 3
    assert normalized[0] == 1.0  # Max score
    assert normalized[2] == 0.0  # Min score
    assert 0.0 <= normalized[1] <= 1.0


def test_normalize_scores_same_values(hybrid_service):
    """Test normalization with identical scores"""
    results = [
        {"score": 5.0},
        {"score": 5.0},
        {"score": 5.0}
    ]
    
    normalized = hybrid_service._normalize_scores(results, "score")
    
    # All should be 1.0 when scores are identical
    assert all(score == 1.0 for score in normalized)


def test_hybrid_search_with_rrf(hybrid_service, sample_semantic_results, sample_lexical_results):
    """Test hybrid search with RRF strategy"""
    results = hybrid_service.hybrid_search(
        sample_semantic_results,
        sample_lexical_results,
        fusion_strategy="rrf",
        top_k=3
    )
    
    assert len(results) <= 3
    assert all("hybrid_score" in r for r in results)


def test_hybrid_search_with_weighted(hybrid_service, sample_semantic_results, sample_lexical_results):
    """Test hybrid search with weighted strategy"""
    results = hybrid_service.hybrid_search(
        sample_semantic_results,
        sample_lexical_results,
        fusion_strategy="weighted",
        top_k=3,
        semantic_weight=0.6,
        lexical_weight=0.4
    )
    
    assert len(results) <= 3
    assert all("hybrid_score" in r for r in results)


def test_hybrid_search_empty_semantic(hybrid_service, sample_lexical_results):
    """Test hybrid search with empty semantic results"""
    results = hybrid_service.hybrid_search(
        [],
        sample_lexical_results,
        top_k=5
    )
    
    # Should return lexical results only
    assert len(results) > 0
    assert len(results) <= 5


def test_hybrid_search_empty_lexical(hybrid_service, sample_semantic_results):
    """Test hybrid search with empty lexical results"""
    results = hybrid_service.hybrid_search(
        sample_semantic_results,
        [],
        top_k=5
    )
    
    # Should return semantic results only
    assert len(results) > 0
    assert len(results) <= 5


def test_hybrid_search_both_empty(hybrid_service):
    """Test hybrid search with both result sets empty"""
    results = hybrid_service.hybrid_search([], [], top_k=5)
    assert results == []


def test_hybrid_search_invalid_strategy(hybrid_service, sample_semantic_results, sample_lexical_results):
    """Test hybrid search with invalid fusion strategy"""
    with pytest.raises(ValueError, match="Unknown fusion strategy"):
        hybrid_service.hybrid_search(
            sample_semantic_results,
            sample_lexical_results,
            fusion_strategy="invalid_strategy"
        )
