import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.database import Database

client = TestClient(app)
db = Database()


def test_analyze_invalid_url():
    response = client.post("/api/analyze", json={"repo_url": "https://evil.com/malicious/repo"})
    assert response.status_code == 400
    assert "Only GitHub repositories are supported" in response.json()["detail"]


def test_repo_metadata_not_found():
    response = client.get("/api/repo/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Repository not found."


def test_repo_tree_not_found():
    response = client.get("/api/repo/999999/tree")
    assert response.status_code == 404


def test_repo_graph_not_found():
    response = client.get("/api/repo/999999/graph")
    assert response.status_code == 404


def test_chat_repo_not_found():
    response = client.post("/api/chat", json={
        "repo_id": 999999,
        "question": "What does this repo do?"
    })
    assert response.status_code == 404


def test_mock_repo_flow_and_phase_2_endpoints():
    repo_id = db.create_or_update_repo(
        "https://github.com/test/dummy-repo",
        "abc1234",
        repository_name="dummy-repo",
        analysis_duration=0.5
    )

    mock_graph = {
        "nodes": [
            {"id": "file:main.py", "name": "main.py", "type": "FILE", "file": "main.py"},
            {"id": "file:utils.py", "name": "utils.py", "type": "FILE", "file": "utils.py"},
            {"id": "class:main.py:App", "name": "App", "type": "CLASS", "file": "main.py"},
            {"id": "function:main.py:run", "name": "run", "type": "FUNCTION", "file": "main.py"},
            {"id": "function:utils.py:helper", "name": "helper", "type": "FUNCTION", "file": "utils.py"}
        ],
        "links": [
            {
                "source": "file:main.py",
                "target": "file:utils.py",
                "type": "IMPORTS",
                "resolution_status": "VERIFIED"
            },
            {
                "source": "function:main.py:run",
                "target": "function:utils.py:helper",
                "type": "CALLS",
                "resolution_status": "VERIFIED"
            }
        ]
    }
    mock_tree = {"name": "root", "type": "directory", "children": [{"name": "main.py", "type": "file", "path": "main.py"}]}
    mock_stats = {"total_python_files": 2, "total_classes": 1, "total_functions": 2, "verified_count": 2}

    db.cache_analysis(repo_id, mock_graph, {"main.py": "print('hello')"}, mock_tree, mock_stats)

    # Test metadata
    res = client.get(f"/api/repo/{repo_id}")
    assert res.status_code == 200
    assert res.json()["repository_name"] == "dummy-repo"

    # Test tree
    res = client.get(f"/api/repo/{repo_id}/tree")
    assert res.status_code == 200
    assert res.json()["name"] == "root"

    # Test graph mode filtering (FILES)
    res = client.get(f"/api/repo/{repo_id}/graph?mode=FILES")
    assert res.status_code == 200
    assert len(res.json()["nodes"]) == 2

    # Test Subgraph Endpoint
    res = client.get(f"/api/repo/{repo_id}/subgraph/function:main.py:run?depth=1")
    assert res.status_code == 200
    assert len(res.json()["nodes"]) == 2

    # Test Dependencies Endpoint
    res = client.get(f"/api/repo/{repo_id}/dependencies/function:main.py:run")
    assert res.status_code == 200
    assert len(res.json()["nodes"]) == 2

    # Test Callers Endpoint
    res = client.get(f"/api/repo/{repo_id}/callers/function:utils.py:helper")
    assert res.status_code == 200
    assert len(res.json()["nodes"]) == 2

    # Test Path Endpoint
    res = client.get(f"/api/repo/{repo_id}/path?source=function:main.py:run&target=function:utils.py:helper")
    assert res.status_code == 200
    assert res.json()["path"] == ["function:main.py:run", "function:utils.py:helper"]

    # Test Node Details Endpoint
    res = client.get(f"/api/repo/{repo_id}/node/function:main.py:run")
    assert res.status_code == 200
    assert res.json()["node"]["id"] == "function:main.py:run"
    assert len(res.json()["dependencies"]) == 2

    # Test Edge Evidence Endpoint
    res = client.get(f"/api/repo/{repo_id}/evidence/edge_1")
    assert res.status_code == 200 or res.status_code == 404

    # Test structural question
    res = client.post("/api/chat", json={
        "repo_id": repo_id,
        "node_id": "file:main.py",
        "question": "Show imports for this file"
    })
    assert res.status_code == 200
    assert res.json()["answer_type"] == "GRAPH"
    assert res.json()["llm_used"] is False
