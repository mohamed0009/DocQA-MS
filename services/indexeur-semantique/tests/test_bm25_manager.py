"""
Unit tests for BM25 manager
"""

import pytest
import os
import tempfile
from app.services.bm25_manager import BM25Manager
from app.config import settings


@pytest.fixture
def temp_index_path(monkeypatch):
    """Create temporary directory for BM25 index"""
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setattr(settings, 'BM25_INDEX_PATH', tmpdir)
        yield tmpdir


@pytest.fixture
def bm25_manager(temp_index_path):
    """Create BM25 manager instance"""
    return BM25Manager()


def test_bm25_initialization(bm25_manager):
    """Test BM25 manager initialization"""
    assert bm25_manager is not None
    assert bm25_manager.corpus == []
    assert bm25_manager.metadata == []
    assert bm25_manager.bm25 is None


def test_tokenization(bm25_manager):
    """Test text tokenization"""
    text = "This is a test document about diabetes and insulin."
    tokens = bm25_manager._tokenize(text)
    
    assert isinstance(tokens, list)
    assert len(tokens) > 0
    # Stopwords should be removed
    assert "is" not in tokens
    assert "a" not in tokens
    # Content words should remain
    assert "test" in tokens or "diabetes" in tokens


def test_add_documents(bm25_manager):
    """Test adding documents to BM25 index"""
    texts = [
        "Diabetes is a chronic disease",
        "Insulin resistance causes high blood sugar",
        "Type 2 diabetes treatment options"
    ]
    
    metadata = [
        {"chunk_id": "1", "document_id": "doc1", "chunk_text": texts[0], "chunk_index": 0},
        {"chunk_id": "2", "document_id": "doc1", "chunk_text": texts[1], "chunk_index": 1},
        {"chunk_id": "3", "document_id": "doc2", "chunk_text": texts[2], "chunk_index": 0}
    ]
    
    bm25_manager.add_documents(texts, metadata)
    
    assert len(bm25_manager.corpus) == 3
    assert len(bm25_manager.metadata) == 3
    assert bm25_manager.bm25 is not None


def test_search(bm25_manager):
    """Test BM25 search"""
    texts = [
        "Diabetes is a chronic disease affecting blood sugar levels",
        "Insulin resistance is a key factor in type 2 diabetes",
        "Heart disease and stroke are common complications",
        "Regular exercise helps manage diabetes symptoms"
    ]
    
    metadata = [
        {"chunk_id": str(i), "document_id": f"doc{i}", "chunk_text": texts[i], "chunk_index": 0}
        for i in range(len(texts))
    ]
    
    bm25_manager.add_documents(texts, metadata)
    
    # Search for diabetes-related content
    results = bm25_manager.search("diabetes insulin", top_k=3)
    
    assert len(results) > 0
    assert len(results) <= 3
    # First result should have highest score
    assert results[0]["bm25_score"] >= results[-1]["bm25_score"]
    # Results should contain metadata
    assert "chunk_id" in results[0]
    assert "document_id" in results[0]


def test_search_empty_index(bm25_manager):
    """Test search on empty index"""
    results = bm25_manager.search("test query", top_k=5)
    assert results == []


def test_index_persistence(bm25_manager, temp_index_path):
    """Test saving and loading BM25 index"""
    texts = ["Test document one", "Test document two"]
    metadata = [
        {"chunk_id": "1", "document_id": "doc1", "chunk_text": texts[0], "chunk_index": 0},
        {"chunk_id": "2", "document_id": "doc1", "chunk_text": texts[1], "chunk_index": 1}
    ]
    
    bm25_manager.add_documents(texts, metadata)
    bm25_manager.save_index()
    
    # Create new manager instance (should load from disk)
    new_manager = BM25Manager()
    
    assert len(new_manager.corpus) == 2
    assert len(new_manager.metadata) == 2
    assert new_manager.bm25 is not None


def test_delete_by_document_id(bm25_manager):
    """Test deleting documents by document ID"""
    texts = [
        "Document 1 chunk 1",
        "Document 1 chunk 2",
        "Document 2 chunk 1"
    ]
    
    metadata = [
        {"chunk_id": "1", "document_id": "doc1", "chunk_text": texts[0], "chunk_index": 0},
        {"chunk_id": "2", "document_id": "doc1", "chunk_text": texts[1], "chunk_index": 1},
        {"chunk_id": "3", "document_id": "doc2", "chunk_text": texts[2], "chunk_index": 0}
    ]
    
    bm25_manager.add_documents(texts, metadata)
    assert len(bm25_manager.corpus) == 3
    
    # Delete doc1
    bm25_manager.delete_by_document_id("doc1")
    
    assert len(bm25_manager.corpus) == 1
    assert len(bm25_manager.metadata) == 1
    assert bm25_manager.metadata[0]["document_id"] == "doc2"


def test_get_stats(bm25_manager):
    """Test getting BM25 statistics"""
    stats = bm25_manager.get_stats()
    
    assert "total_documents" in stats
    assert "k1" in stats
    assert "b" in stats
    assert "has_index" in stats
    
    assert stats["total_documents"] == 0
    assert stats["has_index"] is False
    
    # Add documents
    texts = ["Test document"]
    metadata = [{"chunk_id": "1", "document_id": "doc1", "chunk_text": texts[0], "chunk_index": 0}]
    bm25_manager.add_documents(texts, metadata)
    
    stats = bm25_manager.get_stats()
    assert stats["total_documents"] == 1
    assert stats["has_index"] is True
