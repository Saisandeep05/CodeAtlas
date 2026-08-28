# CodeAtlas — Two-Pass Analysis Pipeline Manual

## 1. Pipeline Lifecycle

```
[GitHub Repo]
     │
     ▼
[GitHubService.clone_repo]
 ├── URL Validation (github.com only)
 └── Safety Limits (500 files, 1MB file, 25MB total)
     │
     ▼
[Pass 1: AST Extraction (code_parser.py)]
 ├── Visit Import / ImportFrom (extract module, name, asname, level)
 ├── Visit ClassDef (extract name, bases, line)
 └── Visit FunctionDef / Call (extract caller, callee, line, evidence)
     │
     ▼
[Global Indexing (symbol_index.py)]
 ├── Store module -> file path
 ├── Index fully-qualified symbols (module.Class.method)
 └── Build class_bases hierarchy mapping
     │
     ▼
[Pass 2: Symbol Resolution (symbol_resolver.py)]
 ├── Construct Canonical Node IDs
 ├── Resolve Import Aliases & Relative Dots
 ├── Resolve Inheritance & self.method() / super().method()
 └── Assign Status: VERIFIED | EXTERNAL | UNRESOLVED | AMBIGUOUS
     │
     ▼
[Graph Construction & Caching (graph_builder.py & database.py)]
```

---

## 2. Canonical Node ID Contract

| Entity | Format Pattern | Example |
| :--- | :--- | :--- |
| **File** | `file:<relative_path>` | `file:src/auth.py` |
| **Class** | `class:<relative_path>:<class_name>` | `class:src/auth.py:AuthService` |
| **Function** | `function:<relative_path>:<func_name>` | `function:src/utils.py:hash_password` |
| **Method** | `function:<relative_path>:<class_name>.<method_name>` | `function:src/auth.py:AuthService.login` |
