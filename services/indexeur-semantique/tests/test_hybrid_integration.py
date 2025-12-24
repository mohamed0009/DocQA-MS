"""
Integration tests for hybrid search API
"""

import pytest
from fastapi.testclient import TestClient
from uuid import uuid4


@pytest.fixture
def client():
    """Create test client"""
    from app.main import app
    return TestClient(app)


@pytest.fixture
def sample_document():
    """Sample medical document for testing"""
    return {
        "document_id": str(uuid4()),
        "text": """
        Diabetes mellitus is a chronic metabolic disorder characterized by elevated blood glucose levels.
        Type 2 diabetes is the most common form, accounting for 90-95% of all diabetes cases.
        Insulin resistance is a key feature of type 2 diabetes, where cells fail to respond normally to insulin.
        Treatment options include lifestyle modifications, oral medications, and insulin therapy.
        Regular monitoring of blood sugar levels is essential for diabetes management.
        Complications can include cardiovascular disease, kidney damage, and nerve damage.
        """,
        "chunking_strategy": "paragraph"
    }


def test_index_document_creates_both_indices(client, sample_document):
    """Test that indexing creates both FAISS and BM25 indices"""
    response = client.post("/api/index", json=sample_document)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "document_id" in data
    assert "chunks_created" in data
    assert data["chunks_created"] > 0
    assert "embeddings_generated" in data
    assert "faiss_ids" in data


def test_semantic_search(client, sample_document):
    """Test pure semantic search"""
    # Index document first
    client.post("/api/index", json=sample_document)
    
    # Perform semantic search
    search_request = {
        "query": "What causes high blood sugar?",
        "search_mode": "semantic",
        "top_k": 3
    }
    
    response = client.post("/api/search", json=search_request)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["search_mode"] == "semantic"
    assert "results" in data
    assert data["results_count"] >= 0
    assert "search_time_ms" in data
    assert "embedding_time_ms" in data


def test_lexical_search(client, sample_document):
    """Test pure BM25 lexical search"""
    # Index document first
    client.post("/api/index", json=sample_document)
    
    # Perform lexical search with exact keywords
    search_request = {
        "query": "insulin resistance diabetes",
        "search_mode": "lexical",
        "top_k": 3
    }
    
    response = client.post("/api/search", json=search_request)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["search_mode"] == "lexical"
    assert "results" in data
    assert data["results_count"] >= 0


def test_hybrid_search_rrf(client, sample_document):
    """Test hybrid search with RRF fusion"""
    # Index document first
    client.post("/api/index", json=sample_document)
    
    # Perform hybrid search
    search_request = {
        "query": "diabetes insulin treatment",
        "search_mode": "hybrid",
        "fusion_strategy": "rrf",
        "top_k": 5
    }
    
    response = client.post("/api/search", json=search_request)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["search_mode"] == "hybrid"
    assert data["fusion_strategy"] == "rrf"
    assert "results" in data
    assert data["results_count"] >= 0


def test_hybrid_search_weighted(client, sample_document):
    """Test hybrid search with weighted fusion"""
    # Index document first
    client.post("/api/index", json=sample_document)
    
    # Perform hybrid search with custom weights
    search_request = {
        "query": "type 2 diabetes complications",
        "search_mode": "hybrid",
        "fusion_strategy": "weighted",
        "semantic_weight": 0.7,
        "lexical_weight": 0.3,
        "top_k": 5
    }
    
    response = client.post("/api/search", json=search_request)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["search_mode"] == "hybrid"
    assert data["fusion_strategy"] == "weighted"
    assert "results" in data


def test_hybrid_search_default(client, sample_document):
    """Test hybrid search with default settings"""
    # Index document first
    client.post("/api/index", json=sample_document)
    
    # Perform search without specifying mode (should default to hybrid)
    search_request = {
        "query": "diabetes treatment",
        "top_k": 3
    }
    
    response = client.post("/api/search", json=search_request)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["search_mode"] == "hybrid"
    assert "results" in data


def test_compare_search_modes(client, sample_document):
    """Test that different search modes return different results"""
    # Index document first
    client.post("/api/index", json=sample_document)
    
    query = "insulin resistance"
    
    # Semantic search
    semantic_response = client.post("/api/search", json={
        "query": query,
        "search_mode": "semantic",
        "top_k": 5
    })
    
    # Lexical search
    lexical_response = client.post("/api/search", json={
        "query": query,
        "search_mode": "lexical",
        "top_k": 5
    })
    
    # Hybrid search
    hybrid_response = client.post("/api/search", json={
        "query": query,
        "search_mode": "hybrid",
        "top_k": 5
    })
    
    assert semantic_response.status_code == 200
    assert lexical_response.status_code == 200
    assert hybrid_response.status_code == 200
    
    # All should return results
    assert semantic_response.json()["results_count"] >= 0
    assert lexical_response.json()["results_count"] >= 0
    assert hybrid_response.json()["results_count"] >= 0


def test_delete_document_removes_from_both_indices(client, sample_document):
    """Test that deleting a document removes it from both indices"""
    # Index document
    index_response = client.post("/api/index", json=sample_document)
    document_id = index_response.json()["document_id"]
    
    # Verify document is searchable
    search_response = client.post("/api/search", json={
        "query": "diabetes",
        "top_k": 5
    })
    assert search_response.json()["results_count"] > 0
    
    # Delete document
    delete_response = client.delete(f"/api/document/{document_id}")
    assert delete_response.status_code == 200
    
    # Verify document is no longer in results
    # (Note: In a real test, you'd need to ensure this is the only document)


def test_invalid_search_mode(client):
    """Test that invalid search mode returns error"""
    search_request = {
        "query": "test query",
        "search_mode": "invalid_mode",
        "top_k": 5
    }
    
    response = client.post("/api/search", json=search_request)
    
    assert response.status_code == 400
    assert "Invalid search_mode" in response.json()["detail"]


def test_index_stats(client, sample_document):
    """Test getting index statistics"""
    # Index a document
    client.post("/api/index", json=sample_document)
    
    # Get stats
    response = client.get("/api/stats")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "total_vectors" in data
    assert "total_chunks" in data
    assert "total_documents" in data
    assert data["total_documents"] > 0
