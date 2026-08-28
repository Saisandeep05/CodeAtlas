import pytest
import os
from app.services.code_parser import parse_file
from app.services.graph_builder import build_graph
from app.services.graph_query_service import GraphQueryService

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")

def load_fixture_service(fixture_name: str) -> GraphQueryService:
    root = os.path.join(FIXTURES_DIR, fixture_name)
    parsed_files = []
    for r, _, files in os.walk(root):
        for file in files:
            if file.endswith(".py"):
                full = os.path.join(r, file)
                res = parse_file(full, root)
                parsed_files.append(res)
    graph_data = build_graph(parsed_files)
    return GraphQueryService(graph_data)

def test_structural_question_detection():
    service = load_fixture_service("cross_file")
    assert service.is_structural_question("what imports format_data?") is True
    assert service.is_structural_question("who calls run?") is True
    assert service.is_structural_question("explain the architectural design") is False

def test_query_structural_zero_llm():
    service = load_fixture_service("cross_file")
    res_dict = service.query_structural("function:main.py:run", "what does run call?")
    assert res_dict["response_source"] == "GRAPH"
    assert res_dict["verification_level"] == "VERIFIED_GRAPH_QUERY"
    ans = res_dict["answer"]
    assert "Verified Dependencies" in ans or "Structural Graph Facts" in ans or "format_data" in ans

def test_get_node_summary():
    service = load_fixture_service("cross_file")
    summary = service.get_node_summary("function:main.py:run")
    assert summary is not None
    assert summary["node"]["id"] == "function:main.py:run"
    assert "incoming_count" in summary
    assert "outgoing_count" in summary

def test_get_edge_evidence():
    service = load_fixture_service("cross_file")
    edge_id = service.graph_data["links"][0]["id"]
    evidence = service.get_edge_evidence(edge_id)
    assert evidence is not None
    assert evidence["id"] == edge_id
    assert "evidence" in evidence

def test_get_impact_analysis():
    service = load_fixture_service("inheritance")
    impact = service.get_impact_analysis("class:base.py:Parent")
    assert impact is not None
    assert impact["target_symbol"]["name"] == "Parent"
    assert impact["total_affected_sites"] >= 1
    assert "may be affected" in impact["impact_summary"]

