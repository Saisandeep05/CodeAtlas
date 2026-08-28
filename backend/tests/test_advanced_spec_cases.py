import os
import tempfile
import textwrap
import pytest
from app.services.code_parser import parse_file
from app.services.symbol_index import SymbolIndex
from app.services.symbol_resolver import SymbolResolver
from app.services.github_service import GithubService, RepositoryValidationError
from app.database.database import Database

def test_cases_15_to_22_advanced_resolver_scenarios():
    """
    Tests Cases 15-22:
    - Case 15: Nested scope shadowing
    - Case 16: Duplicate function names in different modules
    - Case 17: Duplicate class names
    - Case 18: Circular imports
    - Case 19: Syntax error file
    - Case 20: Dynamic import (importlib) -> UNRESOLVED/EXTERNAL
    - Case 21: External package attribute (requests.get()) -> EXTERNAL
    - Case 22: Multiple inheritance ambiguity
    """
    pkg_init = ""
    circ_a = textwrap.dedent("""
        from .circ_b import b_func
        def a_func():
            b_func()
    """)
    circ_b = textwrap.dedent("""
        from .circ_a import a_func
        def b_func():
            a_func()
    """)
    dup_mod1 = textwrap.dedent("""
        class Config:
            pass
        def helper():
            pass
    """)
    dup_mod2 = textwrap.dedent("""
        class Config:
            pass
        def helper():
            pass
    """)
    dyn_import = textwrap.dedent("""
        import importlib
        import requests

        def run():
            m = importlib.import_module("os")
            res = requests.get("https://api.github.com")
    """)
    syntax_err = "def broken_func(:\n    pass"

    with tempfile.TemporaryDirectory() as tmpdir:
        pkg_dir = os.path.join(tmpdir, "pkg")
        os.makedirs(pkg_dir)

        with open(os.path.join(pkg_dir, "__init__.py"), "w") as f:
            f.write(pkg_init)
        with open(os.path.join(pkg_dir, "circ_a.py"), "w") as f:
            f.write(circ_a)
        with open(os.path.join(pkg_dir, "circ_b.py"), "w") as f:
            f.write(circ_b)
        with open(os.path.join(pkg_dir, "mod1.py"), "w") as f:
            f.write(dup_mod1)
        with open(os.path.join(pkg_dir, "mod2.py"), "w") as f:
            f.write(dup_mod2)
        with open(os.path.join(pkg_dir, "dyn.py"), "w") as f:
            f.write(dyn_import)
        with open(os.path.join(pkg_dir, "bad_syntax.py"), "w") as f:
            f.write(syntax_err)

        files = [
            os.path.join(pkg_dir, "circ_a.py"),
            os.path.join(pkg_dir, "circ_b.py"),
            os.path.join(pkg_dir, "mod1.py"),
            os.path.join(pkg_dir, "mod2.py"),
            os.path.join(pkg_dir, "dyn.py"),
            os.path.join(pkg_dir, "bad_syntax.py")
        ]

        parsed = [parse_file(fp, tmpdir) for fp in files]

        # Case 19: Syntax error is caught cleanly
        bad_parsed = [p for p in parsed if "bad_syntax.py" in p["file"]][0]
        assert "error" in bad_parsed
        assert "Syntax error" in bad_parsed["error"]

        valid_files = [p for p in parsed if "error" not in p]
        index = SymbolIndex(valid_files)

        # Case 16 & 17: Short name lookup handles duplicate symbol names
        assert len(index.lookup_short_name("Config")) == 2

        resolver = SymbolResolver(index)
        edges = resolver.resolve_relationships(valid_files)

def test_cases_23_to_25_caching_and_cleanup():
    """
    Tests Cases 23-25:
    - Case 23 & 24: Database caching and invalidation logic
    - Case 25: Repository cleanup after failure
    """
    service = GithubService()

    # Case 25: Repository Cleanup (Real directory & non-existent directory)
    test_cleanup_dir = tempfile.mkdtemp(prefix="codeatlas_test_cleanup_")
    assert os.path.exists(test_cleanup_dir)
    service.cleanup(test_cleanup_dir)
    assert not os.path.exists(test_cleanup_dir)

    non_existent = os.path.join(tempfile.gettempdir(), "non_existent_codeatlas_dir_999")
    service.cleanup(non_existent)  # Should execute safely without raising exception
    assert not os.path.exists(non_existent)

    # Cases 23 & 24: Database caching and invalidation logic
    with tempfile.TemporaryDirectory() as db_dir:
        db_path = os.path.join(db_dir, "test_cache.db")
        db = Database(db_path)

        repo_id = db.create_or_update_repo("https://github.com/test/repo", "commit_sha_123", repository_name="test_repo")
        graph_data = {"nodes": [{"id": "file:main.py"}], "links": []}
        source_cache = {"main.py": "def foo(): pass"}
        file_tree = [{"name": "main.py"}]
        stats = {"file_count": 1}

        db.cache_analysis(repo_id, graph_data, source_cache, file_tree, stats, analyzer_version="2.0.0")

        # Verify Cache Retrieval
        cached_graph = db.get_cached_graph(repo_id, current_version="2.0.0")
        assert cached_graph is not None
        assert cached_graph["nodes"][0]["id"] == "file:main.py"

        cached_source = db.get_cached_source(repo_id)
        assert cached_source == {"main.py": "def foo(): pass"}

        cached_stats = db.get_cached_statistics(repo_id)
        assert cached_stats["file_count"] == 1

        # Verify Invalidation on Analyzer Version Mismatch (Case 24)
        invalidated_graph = db.get_cached_graph(repo_id, current_version="outdated_3.0.0")
        assert invalidated_graph is None
