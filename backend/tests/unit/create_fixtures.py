import os

FIXTURES = {
    "local_calls/main.py": """def helper():
    return "ok"

def run():
    helper()
""",
    "cross_file/utils.py": """def format_data():
    return "formatted"
""",
    "cross_file/main.py": """from utils import format_data

def run():
    format_data()
""",
    "relative_imports/pkg/sub.py": """def child_func():
    pass
""",
    "relative_imports/pkg/main.py": """from .sub import child_func

def run():
    child_func()
""",
    "aliases/utils.py": """def compute():
    pass
""",
    "aliases/main.py": """from utils import compute as calc

def run():
    calc()
""",
    "inheritance/base.py": """class Parent:
    def greet(self):
        pass
""",
    "inheritance/child.py": """from base import Parent

class Child(Parent):
    def run(self):
        self.greet()
""",
    "super_calls/main.py": """class Base:
    def setup(self):
        pass

class Derived(Base):
    def setup(self):
        super().setup()
""",
    "ambiguous/mod_a.py": """def process():
    pass
""",
    "ambiguous/mod_b.py": """def process():
    pass
""",
    "ambiguous/main.py": """def run():
    process()
""",
    "dynamic/main.py": """import importlib

def run():
    func = getattr(obj, "method")
    mod = importlib.import_module("os")
""",
    "async_func/main.py": """async def fetch_data():
    return 42

async def run():
    await fetch_data()
""",
    "external/main.py": """import requests

def run():
    requests.get("https://example.com")
""",
    "package_reexport/pkg/sub.py": """def exported_func():
    pass
""",
    "package_reexport/pkg/__init__.py": """from .sub import exported_func
""",
    "package_reexport/main.py": """from pkg import exported_func

def run():
    exported_func()
""",
    "decorators/main.py": """class Service:
    @property
    def status(self):
        return "active"

    @staticmethod
    def helper():
        pass

def run():
    Service.helper()
""",
    "duplicate_names/a/module.py": """def execute():
    pass
""",
    "duplicate_names/b/module.py": """def execute():
    pass
""",
    "circular_imports/a.py": """import b
def ping():
    b.pong()
""",
    "circular_imports/b.py": """import a
def pong():
    a.ping()
""",
    "syntax_error_file/broken.py": """def broken_func(
"""
}

def create_all():
    base_dir = os.path.join(os.path.dirname(__file__), "fixtures")
    for rel_path, content in FIXTURES.items():
        full_path = os.path.normpath(os.path.join(base_dir, rel_path))
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
    print("Created 15 fixture repositories successfully!")

if __name__ == "__main__":
    create_all()
