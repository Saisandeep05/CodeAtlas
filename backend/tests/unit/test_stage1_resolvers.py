import os
import pytest
from app.services.code_parser import parse_file
from app.services.symbol_index import SymbolIndex
from app.services.symbol_resolver import SymbolResolver

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")

def analyze_fixture(fixture_name: str):
    root = os.path.join(FIXTURES_DIR, fixture_name)
    parsed_files = []
    for r, _, files in os.walk(root):
        for file in files:
            if file.endswith(".py"):
                full = os.path.join(r, file)
                res = parse_file(full, root)
                parsed_files.append(res)
    index = SymbolIndex(parsed_files)
    resolver = SymbolResolver(index)
    edges = resolver.resolve_relationships(parsed_files)
    return parsed_files, index, edges

def test_case_1_local_calls():
    _, _, edges = analyze_fixture("local_calls")
    calls = [e for e in edges if e["type"] == "CALLS"]
    assert len(calls) == 1
    assert calls[0]["resolution_status"] == "VERIFIED"
    assert calls[0]["reasoning"] == "Local function definition in same file"
    assert calls[0]["target"] == "function:main.py:helper"

def test_case_2_cross_file():
    _, _, edges = analyze_fixture("cross_file")
    calls = [e for e in edges if e["type"] == "CALLS"]
    assert len(calls) == 1
    assert calls[0]["resolution_status"] == "VERIFIED"
    assert calls[0]["reasoning"] == "Imported from internal module"
    assert calls[0]["target"] == "function:utils.py:format_data"

def test_case_3_relative_imports():
    _, _, edges = analyze_fixture("relative_imports")
    imports = [e for e in edges if e["type"] == "IMPORTS"]
    rel_imp = [i for i in imports if i["source"] == "file:pkg/main.py"]
    assert len(rel_imp) == 1
    assert rel_imp[0]["resolution_status"] == "VERIFIED"
    assert rel_imp[0]["target"] == "function:pkg/sub.py:child_func"

def test_case_4_aliases():
    _, _, edges = analyze_fixture("aliases")
    calls = [e for e in edges if e["type"] == "CALLS"]
    assert len(calls) == 1
    assert calls[0]["resolution_status"] == "VERIFIED"
    assert calls[0]["reasoning"] == "Resolved via import alias mapping"
    assert calls[0]["target"] == "function:utils.py:compute"

def test_case_5_inheritance():
    _, _, edges = analyze_fixture("inheritance")
    inherits = [e for e in edges if e["type"] == "INHERITS"]
    assert len(inherits) == 1
    assert inherits[0]["resolution_status"] == "VERIFIED"
    assert inherits[0]["reasoning"] == "Direct base class definition in repository"
    assert inherits[0]["target"] == "class:base.py:Parent"

    calls = [e for e in edges if e["type"] == "CALLS"]
    assert len(calls) == 1
    assert calls[0]["resolution_status"] == "VERIFIED"
    assert calls[0]["reasoning"] == "Method resolved on parent class in inheritance hierarchy"
    assert calls[0]["target"] == "function:base.py:Parent.greet"

def test_case_6_super_calls():
    _, _, edges = analyze_fixture("super_calls")
    calls = [e for e in edges if e["type"] == "CALLS"]
    assert len(calls) == 1
    assert calls[0]["resolution_status"] == "VERIFIED"
    assert calls[0]["reasoning"] == "Resolved via super() parent class method lookup"
    assert calls[0]["target"] == "function:main.py:Base.setup"

def test_case_7_ambiguous():
    _, _, edges = analyze_fixture("ambiguous")
    calls = [e for e in edges if e["type"] == "CALLS"]
    assert len(calls) == 1
    assert calls[0]["resolution_status"] == "AMBIGUOUS"
    assert calls[0]["reasoning"] == "Multiple candidate symbols match without disambiguating scope"

def test_case_8_dynamic():
    _, _, edges = analyze_fixture("dynamic")
    calls = [e for e in edges if e["type"] == "CALLS"]
    dyn_calls = [c for c in calls if "getattr" in c["target"] or "importlib" in c["target"]]
    assert len(dyn_calls) >= 1
    for d in dyn_calls:
        assert d["resolution_status"] == "UNRESOLVED"
        assert d["reasoning"] == "Dynamic runtime symbol evaluation cannot be proven statically"

def test_case_9_async_func():
    parsed, _, edges = analyze_fixture("async_func")
    main_file = [p for p in parsed if p["file"] == "main.py"][0]
    funcs = main_file["functions"]
    assert len(funcs) == 2
    assert all(f["is_async"] for f in funcs)

def test_case_10_external():
    _, _, edges = analyze_fixture("external")
    imports = [e for e in edges if e["type"] == "IMPORTS"]
    assert len(imports) == 1
    assert imports[0]["resolution_status"] == "EXTERNAL"
    assert imports[0]["reasoning"] == "External library or standard library package"

def test_case_11_package_reexport():
    _, _, edges = analyze_fixture("package_reexport")
    calls = [e for e in edges if e["type"] == "CALLS"]
    assert len(calls) == 1
    assert calls[0]["resolution_status"] == "VERIFIED"

def test_case_12_decorators():
    parsed, _, edges = analyze_fixture("decorators")
    main_file = [p for p in parsed if p["file"] == "main.py"][0]
    funcs = main_file["functions"]
    status_func = [f for f in funcs if f["name"] == "status"][0]
    helper_func = [f for f in funcs if f["name"] == "helper"][0]

    assert status_func["is_property"] is True
    assert helper_func["is_staticmethod"] is True

    calls = [e for e in edges if e["type"] == "CALLS"]
    assert len(calls) == 1
    assert calls[0]["resolution_status"] == "VERIFIED"
    assert calls[0]["reasoning"] == "Resolved via static method lookup on a known class"
    assert calls[0]["target"] == "function:main.py:Service.helper"


def test_case_13_syntax_error_file():
    parsed, _, _ = analyze_fixture("syntax_error_file")
    assert len(parsed) == 1
    assert "error" in parsed[0]
    assert "Syntax error" in parsed[0]["error"]
