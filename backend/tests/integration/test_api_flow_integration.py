import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.database import Database
from config import ANALYZER_VERSION

client = TestClient(app)

def test_api_root_endpoint():
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert data["version"] == "2.0.0"

def test_analyze_and_graph_query_flow():
    # End-to-end API test with standard database
    db = Database()
    repo_url = "https://github.com/integration_user/integration_test_repo_99"
    commit_hash = "commit_hash_999"

    repo_id = db.create_or_update_repo(
        repo_url,
        commit_hash,
        repository_name="integration_test_repo_99",
        analyzer_version=ANALYZER_VERSION
    )

    sample_graph = {
        "nodes": [
            {"id": "file:main.py", "name": "main.py", "type": "FILE"},
            {"id": "function:main.py:run", "name": "run", "type": "FUNCTION"},
            {"id": "function:utils.py:helper", "name": "helper", "type": "FUNCTION"}
        ],
        "links": [
            {
                "id": "edge99",
                "source": "function:main.py:run",
                "target": "function:utils.py:helper",
                "type": "CALLS",
                "resolution_status": "VERIFIED",
                "reasoning": "Direct AST call",
                "evidence": {"file": "main.py", "line": 10, "expression": "helper()"}
            }
        ]
    }

    db.cache_analysis(
        repo_id,
        graph_data=sample_graph,
        source_cache={"main.py": "def run():\n    helper()"},
        file_tree={"name": "root", "type": "directory", "children": []},
        statistics={"total_nodes": 3, "total_edges": 1},
        analyzer_version=ANALYZER_VERSION
    )

    # 1. Test GET /api/repo/{id}
    res_meta = client.get(f"/api/repo/{repo_id}")
    assert res_meta.status_code == 200
    assert res_meta.json()["repository_name"] == "integration_test_repo_99"

    # 2. Test GET /api/repo/{id}/graph
    res_graph = client.get(f"/api/repo/{repo_id}/graph?mode=FULL")
    assert res_graph.status_code == 200
    assert len(res_graph.json()["nodes"]) == 3

    # 3. Test GET /api/repo/{id}/node/{node_id}
    res_node = client.get(f"/api/repo/{repo_id}/node/function:main.py:run")
    assert res_node.status_code == 200
    assert res_node.json()["node"]["name"] == "run"

    # 4. Test GET /api/repo/{id}/evidence/{edge_id}
    res_ev = client.get(f"/api/repo/{repo_id}/evidence/edge99")
    assert res_ev.status_code == 200
    assert res_ev.json()["resolution_status"] == "VERIFIED"
    assert res_ev.json()["evidence"]["line"] == 10

    # 5. Test POST /api/chat structural query (zero LLM call)
    res_chat_struct = client.post("/api/chat", json={
        "repo_id": repo_id,
        "node_id": "function:main.py:run",
        "question": "What does run depend on?"
    })
    assert res_chat_struct.status_code == 200
    chat_data = res_chat_struct.json()
    assert chat_data["response_source"] == "GRAPH"
    assert chat_data["verification_level"] == "VERIFIED_GRAPH_QUERY"
    assert chat_data["llm_used"] is False
