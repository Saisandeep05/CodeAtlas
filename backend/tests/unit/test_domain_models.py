import pytest
from app.services.domain_models import (
    get_canonical_node_id,
    Evidence,
    ResolvedRelationship,
    ImportBinding,
    RawCall,
    RawClass,
    RawFunction,
    SymbolMetadata
)

def test_canonical_id_collision_proofing():
    """Verify canonical node IDs prevent collisions across files, classes, and functions with identical names."""
    id1 = get_canonical_node_id("FILE", "src/auth.py", "")
    id2 = get_canonical_node_id("FILE", "src/utils.py", "")
    assert id1 == "file:src/auth.py"
    assert id2 == "file:src/utils.py"
    assert id1 != id2

    # Two classes named Config in different files
    cls1 = get_canonical_node_id("CLASS", "src/auth.py", "Config")
    cls2 = get_canonical_node_id("CLASS", "src/utils.py", "Config")
    assert cls1 == "class:src/auth.py:Config"
    assert cls2 == "class:src/utils.py:Config"
    assert cls1 != cls2

    # Two helper functions in different files
    func1 = get_canonical_node_id("FUNCTION", "src/auth.py", "helper")
    func2 = get_canonical_node_id("FUNCTION", "src/utils.py", "helper")
    assert func1 == "function:src/auth.py:helper"
    assert func2 == "function:src/utils.py:helper"
    assert func1 != func2

    # Method vs function in same file
    func_standalone = get_canonical_node_id("FUNCTION", "src/auth.py", "login")
    method_in_class = get_canonical_node_id("METHOD", "src/auth.py", "AuthService.login")
    assert func_standalone == "function:src/auth.py:login"
    assert method_in_class == "function:src/auth.py:AuthService.login"
    assert func_standalone != method_in_class

def test_resolved_relationship_structure():
    ev = Evidence(file="src/auth.py", line=15, expression="helper()")
    rel = ResolvedRelationship(
        source="function:src/auth.py:run",
        target="function:src/utils.py:helper",
        relationship_type="CALLS",
        resolution_status="VERIFIED",
        reasoning="Resolved via imported module symbol",
        evidence=ev
    )
    d = rel.to_dict()
    assert d["source"] == "function:src/auth.py:run"
    assert d["target"] == "function:src/utils.py:helper"
    assert d["type"] == "CALLS"
    assert d["resolution_status"] == "VERIFIED"
    assert d["reasoning"] == "Resolved via imported module symbol"
    assert d["evidence"]["line"] == 15
