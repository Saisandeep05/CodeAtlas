import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.llm_service import LLMService

client = TestClient(app)

def test_api_analyze_validation():
    # Invalid URL
    res = client.post("/api/analyze", json={"repo_url": "invalid-url"})
    assert res.status_code == 400
    assert "Only GitHub repositories are supported" in res.json()["detail"]

    # Non-github URL
    res = client.post("/api/analyze", json={"repo_url": "https://gitlab.com/user/repo"})
    assert res.status_code == 400
    assert "Only GitHub repositories are supported" in res.json()["detail"]

def test_llm_service_grounding_prompt():
    service = LLMService(api_key="test_dummy_key")
    graph_data = {
        "nodes": [{"id": "function:main.py:run", "name": "run", "type": "FUNCTION"}],
        "links": [{
            "source": "function:main.py:run",
            "target": "function:utils.py:helper",
            "type": "CALLS",
            "resolution_status": "VERIFIED"
        }]
    }
    
    # Check fallback message when invalid/dummy key is called
    res = service.answer_fuzzy_question(
        question="What does run do?",
        node_id="function:main.py:run",
        graph_data=graph_data,
        source_code="def run(): helper()",
        request_api_key="your_api_key_here"
    )
    assert "Gemini API key is not configured" in res

def test_chat_endpoint_structural_routing():
    # Chat with non-existent repo
    res = client.post("/api/chat", json={
        "repo_id": 999999,
        "question": "What calls helper?",
        "node_id": "function:main.py:run"
    })
    assert res.status_code == 404
