import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.database import Database
from config import ANALYZER_VERSION

client = TestClient(app)

def test_openapi_docs_render():
    res = client.get("/docs")
    assert res.status_code == 200
    assert "Swagger UI" in res.text or "swagger-ui" in res.text

def test_openapi_json_spec():
    res = client.get("/openapi.json")
    assert res.status_code == 200
    spec = res.json()
    assert "/api/analyze" in spec["paths"]
    assert "/api/repo/{repo_id}/graph" in spec["paths"]
    assert "/api/repo/{repo_id}/path" in spec["paths"]
    assert "/api/repo/{repo_id}/evidence/{edge_id}" in spec["paths"]

def test_cache_hit_and_invalidation():
    db = Database("test_codeatlas.db")
    repo_id = db.create_or_update_repo(
        "https://github.com/user/testrepo",
        "sha123",
        repository_name="testrepo",
        analyzer_version=ANALYZER_VERSION
    )
    db.cache_analysis(
        repo_id,
        graph_data={"nodes": [], "links": []},
        source_cache={},
        file_tree={"name": "root"},
        statistics={},
        analyzer_version=ANALYZER_VERSION
    )

    # Valid cache lookup
    graph = db.get_cached_graph(repo_id, current_version=ANALYZER_VERSION)
    assert graph is not None

    # Stale version invalidation
    stale_graph = db.get_cached_graph(repo_id, current_version="9.9.9")
    assert stale_graph is None
