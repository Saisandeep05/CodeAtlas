import pytest
import os
from app.services.code_parser import parse_file
from app.services.graph_builder import build_graph
from app.services.graph_validator import validate_graph, GraphValidationError

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
    return build_graph(parsed_files)

def test_graph_validation_pass():
    graph_data = load_fixture_graph("inheritance")
    is_valid, errors = validate_graph(graph_data)
    assert is_valid is True
    assert len(errors) == 0

def test_graph_validator_detects_duplicate_node():
    invalid_graph = {
        "nodes": [
            {"id": "file:a.py", "name": "a.py", "type": "FILE"},
            {"id": "file:a.py", "name": "a.py", "type": "FILE"}
        ],
        "links": []
    }
    is_valid, errors = validate_graph(invalid_graph)
    assert is_valid is False
    assert any("Duplicate node ID" in e for e in errors)

def test_graph_validator_detects_missing_evidence():
    invalid_graph = {
        "nodes": [
            {"id": "file:a.py", "name": "a.py", "type": "FILE"},
            {"id": "file:b.py", "name": "b.py", "type": "FILE"}
        ],
        "links": [
            {
                "id": "edge_0",
                "source": "file:a.py",
                "target": "file:b.py",
                "type": "IMPORTS",
                "resolution_status": "VERIFIED",
                "evidence": {}  # Missing file/line!
            }
        ]
    }
    is_valid, errors = validate_graph(invalid_graph)
    assert is_valid is False
    assert any("missing required evidence" in e for e in errors)

def test_node_types_present():
    graph_data = load_fixture_graph("inheritance")
    node_types = {n["type"] for n in graph_data["nodes"]}
    assert "FILE" in node_types
    assert "CLASS" in node_types
    assert "METHOD" in node_types or "FUNCTION" in node_types
