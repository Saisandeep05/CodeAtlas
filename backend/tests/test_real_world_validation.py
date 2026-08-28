import os
import tempfile
import textwrap
import pytest
from app.services.code_parser import parse_file
from app.services.symbol_index import SymbolIndex
from app.services.symbol_resolver import SymbolResolver
from app.services.graph_builder import build_graph, project_graph_mode
from app.services.graph_query_service import GraphQueryService

def test_real_world_multi_module_benchmark():
    """
    Simulates a real-world multi-module architecture (Core, Auth, Database, API, Utilities)
    with complex relationships including relative imports, class inheritance, super() calls,
    alias bindings, and method invocation chains.
    """
    base_module = textwrap.dedent("""
        class BaseEntity:
            def __init__(self, id_val: str):
                self.id = id_val

            def get_id(self) -> str:
                return self.id
    """)

    auth_module = textwrap.dedent("""
        from .base import BaseEntity

        class User(BaseEntity):
            def __init__(self, user_id: str, email: str):
                super().__init__(user_id)
                self.email = email

            def authenticate(self, password: str) -> bool:
                return True

        class AdminUser(User):
            def __init__(self, user_id: str, email: str, role: str):
                super().__init__(user_id, email)
                self.role = role

            def get_permissions(self):
                if self.authenticate("admin_pass"):
                    return ["all"]
                return []
    """)

    db_module = textwrap.dedent("""
        from .auth import User as UserModel, AdminUser

        class DatabaseConnection:
            def connect(self):
                pass

            def query_user(self, user_id: str) -> UserModel:
                u = UserModel(user_id, "user@example.com")
                u.get_id()
                return u
    """)

    service_module = textwrap.dedent("""
        import json
        from .db import DatabaseConnection
        from .auth import AdminUser as Admin

        class AuthService:
            def __init__(self):
                self.db = DatabaseConnection()

            def login_admin(self, admin_id: str):
                self.db.connect()
                admin = Admin(admin_id, "admin@system.com", "superuser")
                perms = admin.get_permissions()
                return perms
    """)

    with tempfile.TemporaryDirectory() as tmpdir:
        core_dir = os.path.join(tmpdir, "core")
        os.makedirs(core_dir)

        base_p = os.path.join(core_dir, "base.py")
        auth_p = os.path.join(core_dir, "auth.py")
        db_p = os.path.join(core_dir, "db.py")
        service_p = os.path.join(core_dir, "service.py")

        with open(base_p, "w") as f:
            f.write(base_module)
        with open(auth_p, "w") as f:
            f.write(auth_module)
        with open(db_p, "w") as f:
            f.write(db_module)
        with open(service_p, "w") as f:
            f.write(service_module)

        parsed = [
            parse_file(base_p, tmpdir),
            parse_file(auth_p, tmpdir),
            parse_file(db_p, tmpdir),
            parse_file(service_p, tmpdir)
        ]

        for p in parsed:
            assert "error" not in p, f"Failed to parse {p['file']}: {p.get('error')}"

        index = SymbolIndex(parsed)
        resolver = SymbolResolver(index)
        edges = resolver.resolve_relationships(parsed)

        # Calculate Verified Resolution Ratio for internal references
        internal_edges = [e for e in edges if e["resolution_status"] in ["VERIFIED", "UNRESOLVED"]]
        verified_edges = [e for e in edges if e["resolution_status"] == "VERIFIED"]
        
        verified_ratio = len(verified_edges) / len(internal_edges) if internal_edges else 0.0
        assert verified_ratio >= 0.80, f"Expected verified ratio >= 80%, got {verified_ratio * 100:.1f}%"

        graph_data = build_graph(parsed)
        gqs = GraphQueryService(graph_data)

        # Test transitive dependency query
        deps = gqs.get_dependencies("class:core/auth.py:AdminUser", transitive=True)
        dep_names = {n["name"] for n in deps["nodes"]}
        assert "User" in dep_names or "BaseEntity" in dep_names

        # Test file mode projection
        files_g = project_graph_mode(graph_data, "FILES")
        assert len(files_g["nodes"]) >= 4
        assert len(files_g["links"]) >= 3
