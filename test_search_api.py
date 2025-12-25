import requests
import json

def test_search():
    url = "http://localhost:8003/api/v1/search/search"
    
    # Test 1: Query "diabetes" (Should trigger query-based fallback)
    print("\n--- TEST 1: Query 'diabetes' ---")
    payload1 = {
        "query": "diabetes",
        "top_k": 5
    }
    try:
        r = requests.post(url, json=payload1, timeout=10)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            results = data.get("results", [])
            print(f"Results Found: {len(results)}")
            for res in results:
                print(f" - DocID: {res.get('document_id')}")
                print(f" - Text: {res.get('chunk_text')[:50]}...")
        else:
            print(f"Error: {r.text}")
    except Exception as e:
        print(f"Exception: {e}")

    # Test 2: Filter PAT001 (Should trigger filter-based fallback)
    print("\n--- TEST 2: Filter PAT001 ---")
    payload2 = {
        "query": "test",
        "top_k": 5,
        "filters": {"patient_id": "PAT001"}
    }
    try:
        r = requests.post(url, json=payload2, timeout=10)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            results = data.get("results", [])
            print(f"Results Found: {len(results)}")
            for res in results:
                print(f" - Metadata: {res.get('metadata')}")
        else:
            print(f"Error: {r.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_search()
