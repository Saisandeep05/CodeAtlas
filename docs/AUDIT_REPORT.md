# Stage 1 Audit Report — CodeAtlas Static Analysis Engine & Data Contracts

## 1. Executive Summary & Existing Architecture

This audit inspects the current codebase of **CodeAtlas** repository for Stage 1 of the implementation roadmap (Static Analysis Engine, Dataclass Domain Contracts, and Fixture Test Suite).

### Current Component Blueprint:
1. `code_parser.py`: Implements `RawAstExtractor(ast.NodeVisitor)`. Extracts classes, functions, imports, and calls.
   - **Gaps Identified**: Decorators (`@staticmethod`, `@property`, `@app.route`) are not extracted. Property definitions are not flagged to prevent misclassifying property accesses as function calls.
2. `symbol_index.py`: Indexes symbols in `self.symbols` and `self.short_name_index`.
   - **Gaps Identified**: Package re-exports via `__init__.py` (e.g. `from .sub import X` inside `pkg/__init__.py`) are not indexed as package-level exported symbols (`pkg.X`).
3. `symbol_resolver.py`: Two-pass symbol resolver.
   - **Gaps Identified**: Uses loose dictionary objects instead of type-safe dataclasses. Edges lack explicit `reasoning` strings explaining classification logic.
4. `domain_models.py`: Basic dataclass contracts exist but missing `RawImport`, `RawClass`, `RawFunction`, `CanonicalNode`, `Evidence`, `ResolutionResult`, `RepositoryAnalysisResult`.

---

## 2. Actual Implemented vs. Stubbed/Missing Features (Stage 1 Scope)

| Feature | Implemented Status | Required Action for Stage 1 |
| :--- | :---: | :--- |
| **Dataclass Domain Contracts** | Partial | Implement 11 strongly-typed dataclasses consistently (`ImportBinding`, `RawCall`, `RawImport`, `RawClass`, `RawFunction`, `SymbolMetadata`, `CanonicalNode`, `ResolvedRelationship`, `ResolutionResult`, `Evidence`, `RepositoryAnalysisResult`). |
| **Canonical Node IDs** | Implemented | Enforce collision-proof ID format: `file:<path>`, `class:<path>:<Name>`, `function:<path>:<func>`. |
| **Reasoning Strings** | Missing | Attach explicit, human-readable `reasoning` string to every `ResolvedRelationship`. |
| **Local & Cross-File Function Calls** | Implemented | Add fixture-backed TDD unit tests asserting status AND reasoning string. |
| **Import Aliases & Relative Imports** | Implemented | Add fixture-backed TDD unit tests. |
| **`self.method()` & `super().method()`** | Implemented | Add fixture-backed TDD unit tests. |
| **Class Inheritance Edges** | Implemented | Add fixture-backed TDD unit tests. |
| **Package Re-Exports (`__init__.py`)** | Missing | Add indexing & resolution for `__init__.py` re-exported symbols (e.g., `from package import X`). |
| **Decorator-Aware Resolution** | Missing | Capture decorators (`@staticmethod`, `@property`, generic decorators). Prevent property access from misclassifying as function calls. |
| **External Library & Ambiguous Symbols**| Implemented | Ensure `requests` is `EXTERNAL` and non-unique matches are `AMBIGUOUS`. |
| **Dynamic Symbol Resolution** | Implemented | Ensure `getattr`, `globals`, `importlib` resolve to `UNRESOLVED`. |

---

## 3. Concrete Stage 1 Roadmap

1. **Step 2 — Data Contracts**: Standardize all 11 dataclasses in `domain_models.py`.
2. **Step 3 — Static Analysis Engine**:
   - Update `code_parser.py` to extract decorators and property flags.
   - Update `symbol_index.py` to index `__init__.py` package re-exports.
   - Update `symbol_resolver.py` to produce typed `ResolvedRelationship` objects with stored `reasoning` strings.
3. **Step 4 — Fixture Test Suite**: Create 15 fixture repositories under `backend/tests/unit/fixtures/` and test cases in `backend/tests/unit/test_stage1_resolvers.py`.
