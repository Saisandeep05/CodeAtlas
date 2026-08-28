import pytest
import tempfile
import os
import textwrap
from app.services.code_parser import parse_file
from app.services.symbol_index import SymbolIndex
from app.services.symbol_resolver import SymbolResolver
from app.services.graph_builder import build_graph, project_graph_mode
from app.services.graph_query_service import GraphQueryService


def test_section_17_and_phase_1_features():
    utils_code = textwrap.dedent("""
        def helper():
            pass
    """)
    models_code = textwrap.dedent("""
        class User:
            def save(self):
                pass

        class Admin(User):
            def update(self):
                self.save()

            def refresh(self):
                super().save()
    """)
    main_code = textwrap.dedent("""
        import requests
        from .utils import helper as h
        import utils as u

        def a():
            b()

        def b():
            pass

        def run():
            h()
            u.helper()
            user = None
            user.save()

        async def fetch():
            pass
    """)
    with tempfile.TemporaryDirectory() as tmpdir:
        pkg_dir = os.path.join(tmpdir, "pkg")
        os.makedirs(pkg_dir)

        utils_path = os.path.join(pkg_dir, "utils.py")
        models_path = os.path.join(pkg_dir, "models.py")
        main_path = os.path.join(pkg_dir, "main.py")

        with open(utils_path, "w") as f:
            f.write(utils_code)
        with open(models_path, "w") as f:
            f.write(models_code)
        with open(main_path, "w") as f:
            f.write(main_code)

        parsed_files = [
            parse_file(utils_path, tmpdir),
            parse_file(models_path, tmpdir),
            parse_file(main_path, tmpdir)
        ]

        for pf in parsed_files:
            assert "error" not in pf, f"Parsing error in {pf['file']}: {pf.get('error')}"

        symbol_index = SymbolIndex()
        symbol_index.build_index(parsed_files)

        # Case 8: Async function correctly indexed
        assert "pkg.main.fetch" in symbol_index.symbols

        resolver = SymbolResolver(symbol_index)
        edges = resolver.resolve_relationships(parsed_files)

        # Case 1: Local function call a -> b (CALLS, VERIFIED)
        local_call = next(e for e in edges if e["source"] == "function:pkg/main.py:a" and e["target"] == "function:pkg/main.py:b")
        assert local_call["type"] == "CALLS"
        assert local_call["resolution_status"] == "VERIFIED"

        # Case 2: External import requests (IMPORTS, EXTERNAL)
        ext_imp = next(e for e in edges if e["source"] == "file:pkg/main.py" and e["target"] == "module:requests")
        assert ext_imp["type"] == "IMPORTS"
        assert ext_imp["resolution_status"] == "EXTERNAL"

        # Case 3 & 4: Relative & Alias import (from .utils import helper as h -> h())
        alias_imp = next(e for e in edges if e["source"] == "file:pkg/main.py" and "function:pkg/utils.py:helper" in e["target"])
        assert alias_imp["resolution_status"] == "VERIFIED"

        # Phase 1 D & E: self.save() inside Admin(User) resolves up hierarchy to User.save()
        self_call = next(e for e in edges if e["source"] == "function:pkg/models.py:Admin.update" and e["target"] == "function:pkg/models.py:User.save")
        assert self_call["type"] == "CALLS"
        assert self_call["resolution_status"] == "VERIFIED"

        # Phase 1 F: super().save() inside Admin resolves to User.save()
        super_call = next(e for e in edges if e["source"] == "function:pkg/models.py:Admin.refresh" and e["target"] == "function:pkg/models.py:User.save")
        assert super_call["type"] == "CALLS"
        assert super_call["resolution_status"] == "VERIFIED"

        # Case 5: Dynamic attribute call user.save() (CALLS, UNRESOLVED)
        dyn_call = next(e for e in edges if e["source"] == "function:pkg/main.py:run" and e["target"] == "unresolved:user.save")
        assert dyn_call["type"] == "CALLS"
        assert dyn_call["resolution_status"] == "UNRESOLVED"

        # Case 7: Class inheritance class Admin(User) (INHERITS, VERIFIED)
        inh_edge = next(e for e in edges if e["source"] == "class:pkg/models.py:Admin" and e["target"] == "class:pkg/models.py:User")
        assert inh_edge["type"] == "INHERITS"
        assert inh_edge["resolution_status"] == "VERIFIED"

        # Build full graph & test Phase 2 projections
        graph_data = build_graph(parsed_files)
        files_proj = project_graph_mode(graph_data, "FILES")
        assert len(files_proj["nodes"]) > 0
        assert len(files_proj["links"]) > 0

        # Check ANY file link exists
        file_link = files_proj["links"][0]
        assert file_link["verified_count"] >= 0

        # Test Phase 2 Graph Intelligence Queries
        gqs = GraphQueryService(graph_data)
        subgraph = gqs.get_subgraph("class:pkg/models.py:Admin", depth=2)
        assert len(subgraph["nodes"]) >= 2

        path = gqs.get_shortest_path("function:pkg/main.py:a", "function:pkg/main.py:b")
        assert path == ["function:pkg/main.py:a", "function:pkg/main.py:b"]
