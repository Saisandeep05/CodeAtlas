import pytest
from app.services.code_parser import parse_file
from app.services.graph_builder import build_graph, project_graph_mode
from app.services.graph_query_service import GraphQueryService
import os

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")

def load_fixture_graph(fixture_name: str):
    root = os.path.join(FIXTURES_DIR, fixture_name)
    parsed_files = []
    for r, _, files in os.walk(root):
        for file in files:
            if file.endswith(".py"):
                full = os.path.join(r, file)
                res = parse_file(full, root)
                parsed_files.append(res)
    graph_data = build_graph(parsed_files)
    return graph_data

def test_graph_builder_structure():
    graph_data = load_fixture_graph("cross_file")
    assert "nodes" in graph_data
    assert "links" in graph_data
    assert len(graph_data["nodes"]) >= 3  # files + functions

    # Verify edge fields
    link = graph_data["links"][0]
    assert "id" in link
    assert "source" in link
    assert "target" in link
    assert "type" in link
    assert "resolution_status" in link
    assert "reasoning" in link
    assert "evidence" in link

def test_get_neighborhood():
    graph_data = load_fixture_graph("cross_file")
    service = GraphQueryService(graph_data)

    # Neighborhood around main.py
    nh_1 = service.get_neighborhood("file:main.py", depth=1)
    assert len(nh_1["nodes"]) >= 2

    nh_2 = service.get_neighborhood("file:main.py", depth=2)
    assert len(nh_2["nodes"]) >= len(nh_1["nodes"])

def test_find_path():
    graph_data = load_fixture_graph("cross_file")
    service = GraphQueryService(graph_data)

    src = "function:main.py:run"
    tgt = "function:utils.py:format_data"
    path_info = service.find_path(src, tgt)

    assert path_info is not None
    assert path_info["hop_count"] >= 1
    assert "nodes" in path_info
    assert "edges" in path_info
    assert path_info["nodes"][0]["id"] == src

def test_filter_graph():
    graph_data = load_fixture_graph("inheritance")
    service = GraphQueryService(graph_data)

    # Filter only CLASS nodes and VERIFIED edges
    filtered = service.filter_graph(node_types=["CLASS"], resolution_statuses=["VERIFIED"])
    for n in filtered["nodes"]:
        assert n["type"] == "CLASS"
    for l in filtered["links"]:
        assert l["resolution_status"] == "VERIFIED"

def test_get_statistics():
    graph_data = load_fixture_graph("inheritance")
    service = GraphQueryService(graph_data)

    stats = service.get_statistics()
    assert stats["total_nodes"] > 0
    assert stats["total_edges"] > 0
    assert "nodes_by_type" in stats
    assert "edges_by_status" in stats
    assert "density" in stats
    assert "connected_components" in stats
    assert stats["nodes_by_type"].get("CLASS", 0) >= 2

def test_graph_mode_projections():
    graph_data = load_fixture_graph("inheritance")

    files_proj = project_graph_mode(graph_data, "FILES")
    assert all(n["type"] in ["FILE", "EXTERNAL", "UNRESOLVED", "AMBIGUOUS"] for n in files_proj["nodes"])

    classes_proj = project_graph_mode(graph_data, "CLASSES")
    assert all(n["type"] in ["FILE", "CLASS", "EXTERNAL", "UNRESOLVED", "AMBIGUOUS"] for n in classes_proj["nodes"])

    funcs_proj = project_graph_mode(graph_data, "FUNCTIONS")
    assert all(n["type"] in ["FILE", "FUNCTION", "METHOD", "EXTERNAL", "UNRESOLVED", "AMBIGUOUS"] for n in funcs_proj["nodes"])
