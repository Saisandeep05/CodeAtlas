import pytest
from app.services.github_service import GithubService, RepositoryValidationError
from app.services.code_parser import parse_file
from app.services.symbol_resolver import SymbolResolver
from app.services.symbol_index import SymbolIndex
from app.services.stats_service import compute_statistics
import tempfile
import os


def test_github_service_validate_url():
    service = GithubService()

    # Valid URLs
    owner, repo = service.validate_url("https://github.com/fastapi/fastapi")
    assert owner == "fastapi"
    assert repo == "fastapi"

    owner, repo = service.validate_url("https://github.com/psf/requests.git")
    assert owner == "psf"
    assert repo == "requests"

    # Invalid URLs (Security enforcement)
    with pytest.raises(RepositoryValidationError):
        service.validate_url("https://evil.com/repo.git")

    with pytest.raises(RepositoryValidationError):
        service.validate_url("file:///etc/passwd")

    with pytest.raises(RepositoryValidationError):
        service.validate_url("https://github.com/invalid")


def test_code_parser_relative_imports():
    code = """
from .utils import helper_func
from ..models import BaseUser
import os

class MyService(BaseUser):
    def run(self):
        return helper_func()
"""
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tmp:
        tmp.write(code)
        tmp_path = tmp.name

    try:
        res = parse_file(tmp_path, os.path.dirname(tmp_path))
        imports = res["imports"]

        rel_imports = [i for i in imports if i["type"] == "import_from"]
        assert len(rel_imports) == 2

        # Check level capturing
        helper_imp = next(i for i in rel_imports if i["name"] == "helper_func")
        assert helper_imp["level"] == 1
        assert helper_imp["module"] == "utils"

        user_imp = next(i for i in rel_imports if i["name"] == "BaseUser")
        assert user_imp["level"] == 2
        assert user_imp["module"] == "models"
    finally:
        os.remove(tmp_path)


def test_symbol_resolver_relative_module():
    index = SymbolIndex()
    resolver = SymbolResolver(index)

    # level 1 from pkg.sub.module -> pkg.sub.utils
    res = resolver._resolve_relative_module("pkg.sub.module", 1, "utils")
    assert res == "pkg.sub.utils"

    # level 2 from pkg.sub.module -> pkg.helpers
    res = resolver._resolve_relative_module("pkg.sub.module", 2, "helpers")
    assert res == "pkg.helpers"

    # level 1 from pkg.sub.__init__ -> pkg.sub.utils
    res = resolver._resolve_relative_module("pkg.sub.__init__", 1, "utils")
    assert res == "pkg.sub.utils"


def test_stats_service_compute_statistics():
    parsed_files = [
        {
            "file": "main.py",
            "module": "main",
            "classes": [{"name": "App"}],
            "functions": [{"name": "run"}],
            "imports": [{"name": "os"}]
        }
    ]
    resolved_edges = [
        {"type": "DEFINES", "resolution_status": "VERIFIED"},
        {"type": "IMPORTS", "resolution_status": "VERIFIED"},
        {"type": "CALLS", "resolution_status": "EXTERNAL"},
        {"type": "INHERITS", "resolution_status": "UNRESOLVED"},
    ]

    stats = compute_statistics(parsed_files, resolved_edges, analysis_duration=1.5)

    assert stats["total_python_files"] == 1
    assert stats["total_classes"] == 1
    assert stats["total_functions"] == 1
    assert stats["total_imports"] == 1
    assert stats["total_relationships"] == 4
    assert stats["verified_count"] == 2
    assert stats["external_count"] == 1
    assert stats["unresolved_count"] == 1
    assert stats["ambiguous_count"] == 0
    assert stats["analysis_duration_seconds"] == 1.5


def test_is_structural_question():
    from app.services.graph_query_service import GraphQueryService
    g = GraphQueryService({"nodes": [], "links": []})
    assert g.is_structural_question("Show imports for this file") is True
    assert g.is_structural_question("Explain what this class does") is False

