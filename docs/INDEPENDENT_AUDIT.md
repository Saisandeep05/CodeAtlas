# CodeAtlas — Zero-Trust Re-Audit & Empirical Evidence Report

**Date of Audit:** August 28, 2026  
**Auditor System:** Independent Verification System (Antigravity AI)  
**Target Repository:** `CodeAtlas`  
**Audit Protocol:** Zero-Trust Empirical Verification (No assumptions, raw output only)  

---

## Executive Summary

An exhaustive zero-trust re-audit of **CodeAtlas** was conducted. Every high-risk claim regarding symbol resolution accuracy, dynamic execution invariants, API safety, per-IP rate limiting, and real-world repository parsing was tested by executing live commands and capturing unedited terminal outputs.

### Summary of Verdicts

| Section | Audit Domain | Status / Verdict | Summary of Verification Evidence |
| :--- | :--- | :--- | :--- |
| **1** | Full Test Suite Execution | **VERIFIED** | 59/59 pytest tests passed in 2.04s. 0 skipped, 0 xfailed. |
| **2** | Hardest Resolver Cases | **PARTIAL** | Cases 1, 2, 4, 5 fully verified. Case 3 parses AST property/staticmethod flags, but static call on `@staticmethod` yields UNRESOLVED. |
| **3** | Grep for Fake-Pass Patterns | **VERIFIED** | 0 hardcoded `VERIFIED` returns in source. 0 code TODOs in source (only HTML attributes). 1 `assert True` in cleanup test. |
| **4** | Real-World Validation | **PARTIAL / DISCREPANCY NOTED** | Live `psf/requests` archive run analyzed 37 files and 4,132 edges in 3.40s. Discrepancy noted vs doc's 22 files / 132 edges core src scope. |
| **5** | Per-IP Rate Limiting | **VERIFIED** | 12 rapid POST requests: Requests #1-#10 returned status 500 (mocked clone); Requests #11-#12 blocked with HTTP 429. |
| **6** | Performance Timing Breakdown | **VERIFIED** | `pallets/flask` (83 files) analyzed end-to-end in 4.5517s (Download: 2.97s, Parse: 1.48s, Resolve: 0.03s, Graph: 0.07s). |
| **7** | README Setup Verification | **VERIFIED** | `pip install`, `pytest`, `npm install`, and `npm run build` executed cleanly following literal README instructions. |

---

## 1. Full Test Suite Execution (Raw Output)

**Command Run:** `python -m pytest tests -v`  
**Execution Directory:** `CodeAtlas/backend`  

```text
============================= test session starts =============================
platform win32 -- Python 3.13.9, pytest-8.4.2, pluggy-1.5.0 -- python.exe
cachedir: .pytest_cache
rootdir: CodeAtlas/backend
plugins: anyio-4.11.0
collecting ... collected 59 items

tests/integration/test_api_flow_integration.py::test_api_root_endpoint PASSED [  1%]
tests/integration/test_api_flow_integration.py::test_analyze_and_graph_query_flow PASSED [  3%]
tests/security/test_cloning_and_limits.py::test_url_validation_strict_safety PASSED [  5%]
tests/security/test_cloning_and_limits.py::test_cleanup_guarantee_on_failure PASSED [  6%]
tests/security/test_cloning_and_limits.py::test_rate_limiting_middleware PASSED [  8%]
tests/security/test_prompt_injection.py::test_prompt_injection_safety_prompt_formatting PASSED [ 10%]
tests/security/test_prompt_injection.py::test_prompt_injection_untrusted_data_isolation PASSED [ 11%]
tests/security/test_security_limits.py::test_url_validation_safety PASSED [ 13%]
tests/security/test_security_limits.py::test_repository_file_count_limits PASSED [ 15%]
tests/test_advanced_spec_cases.py::test_cases_15_to_22_advanced_resolver_scenarios PASSED [ 16%]
tests/test_advanced_spec_cases.py::test_cases_23_to_25_caching_and_cleanup PASSED [ 18%]
tests/test_api_endpoints.py::test_analyze_invalid_url PASSED             [ 20%]
tests/test_api_endpoints.py::test_repo_metadata_not_found PASSED         [ 22%]
tests/test_api_endpoints.py::test_repo_tree_not_found PASSED             [ 23%]
tests/test_api_endpoints.py::test_repo_graph_not_found PASSED            [ 25%]
tests/test_api_endpoints.py::test_chat_repo_not_found PASSED             [ 27%]
tests/test_api_endpoints.py::test_mock_repo_flow_and_phase_2_endpoints PASSED [ 28%]
tests/test_backend.py::test_github_service_validate_url PASSED           [ 30%]
tests/test_backend.py::test_code_parser_relative_imports PASSED          [ 32%]
tests/test_backend.py::test_symbol_resolver_relative_module PASSED       [ 33%]
tests/test_backend.py::test_stats_service_compute_statistics PASSED      [ 35%]
tests/test_backend.py::test_is_structural_question PASSED                [ 37%]
tests/test_real_world_validation.py::test_real_world_multi_module_benchmark PASSED [ 38%]
tests/test_spec_cases.py::test_section_17_and_phase_1_features PASSED    [ 40%]
tests/unit/test_domain_models.py::test_canonical_id_collision_proofing PASSED [ 42%]
tests/unit/test_domain_models.py::test_resolved_relationship_structure PASSED [ 44%]
tests/unit/test_stage1_resolvers.py::test_case_1_local_calls PASSED      [ 45%]
tests/unit/test_stage1_resolvers.py::test_case_2_cross_file PASSED       [ 47%]
tests/unit/test_stage1_resolvers.py::test_case_3_relative_imports PASSED [ 49%]
tests/unit/test_stage1_resolvers.py::test_case_4_aliases PASSED          [ 50%]
tests/unit/test_stage1_resolvers.py::test_case_5_inheritance PASSED      [ 52%]
tests/unit/test_stage1_resolvers.py::test_case_6_super_calls PASSED      [ 54%]
tests/unit/test_stage1_resolvers.py::test_case_7_ambiguous PASSED        [ 55%]
tests/unit/test_stage1_resolvers.py::test_case_8_dynamic PASSED          [ 57%]
tests/unit/test_stage1_resolvers.py::test_case_9_async_func PASSED       [ 59%]
tests/unit/test_stage1_resolvers.py::test_case_10_external PASSED        [ 61%]
tests/unit/test_stage1_resolvers.py::test_case_11_package_reexport PASSED [ 62%]
tests/unit/test_stage1_resolvers.py::test_case_12_decorators PASSED      [ 64%]
tests/unit/test_stage1_resolvers.py::test_case_13_syntax_error_file PASSED [ 66%]
tests/unit/test_stage2_api_caching.py::test_openapi_docs_render PASSED   [ 67%]
tests/unit/test_stage2_api_caching.py::test_openapi_json_spec PASSED     [ 69%]
tests/unit/test_stage2_api_caching.py::test_cache_hit_and_invalidation PASSED [ 71%]
tests/unit/test_stage2_graph.py::test_graph_builder_structure PASSED     [ 72%]
tests/unit/test_stage2_graph.py::test_get_neighborhood PASSED            [ 74%]
tests/unit/test_stage2_graph.py::test_find_path PASSED                   [ 76%]
tests/unit/test_stage2_graph.py::test_filter_graph PASSED                [ 77%]
tests/unit/test_stage2_graph.py::test_get_statistics PASSED              [ 79%]
tests/unit/test_stage2_graph.py::test_graph_mode_projections PASSED      [ 81%]
tests/unit/test_stage2_graph_engine.py::test_graph_validation_pass PASSED [ 83%]
tests/unit/test_stage2_graph_engine.py::test_graph_validator_detects_duplicate_node PASSED [ 84%]
tests/unit/test_stage2_graph_engine.py::test_graph_validator_detects_missing_evidence PASSED [ 86%]
tests/unit/test_stage2_graph_engine.py::test_node_types_present PASSED   [ 88%]
tests/unit/test_stage2_query_engine.py::test_structural_question_detection PASSED [ 89%]
tests/unit/test_stage2_query_engine.py::test_query_structural_zero_llm PASSED [ 91%]
tests/unit/test_stage2_query_engine.py::test_get_node_summary PASSED     [ 93%]
tests/unit/test_stage2_query_engine.py::test_get_edge_evidence PASSED    [ 94%]
tests/unit/test_stage3_api_llm.py::test_api_analyze_validation PASSED    [ 96%]
tests/unit/test_stage3_api_llm.py::test_llm_service_grounding_prompt PASSED [ 98%]
tests/unit/test_stage3_api_llm.py::test_chat_endpoint_structural_routing PASSED [100%]

============================= 59 passed in 2.04s ==============================
```

---

## 2. Hardest Resolver Cases (Fixture, Test Code, and Raw Output)

### Case 1: `self.method()` Resolved via Inheritance
- **(a) Fixture Source Code:**
  - `base.py`:
    ```python
    class Parent:
        def greet(self):
            pass
    ```
  - `child.py`:
    ```python
    from base import Parent

    class Child(Parent):
        def run(self):
            self.greet()
    ```
- **(b) Test Assertion Code:**
  ```python
  def test_case_5_inheritance():
      _, _, edges = analyze_fixture("inheritance")
      calls = [e for e in edges if e["type"] == "CALLS"]
      assert len(calls) == 1
      assert calls[0]["resolution_status"] == "VERIFIED"
      assert calls[0]["reasoning"] == "Method resolved on parent class in inheritance hierarchy"
      assert calls[0]["target"] == "function:base.py:Parent.greet"
  ```
- **(c) Raw Execution Result:** `PASSED`
- **(d) Produced Attributes:**
  - `resolution_status`: `"VERIFIED"`
  - `reasoning`: `"Method resolved on parent class in inheritance hierarchy"`
  - `target`: `"function:base.py:Parent.greet"`

---

### Case 2: `super().method()` Resolution
- **(a) Fixture Source Code:**
  - `main.py`:
    ```python
    class Base:
        def setup(self):
            pass

    class Derived(Base):
        def setup(self):
            super().setup()
    ```
- **(b) Test Assertion Code:**
  ```python
  def test_case_6_super_calls():
      _, _, edges = analyze_fixture("super_calls")
      calls = [e for e in edges if e["type"] == "CALLS"]
      assert len(calls) == 1
      assert calls[0]["resolution_status"] == "VERIFIED"
      assert calls[0]["reasoning"] == "Resolved via super() parent class method lookup"
      assert calls[0]["target"] == "function:main.py:Base.setup"
  ```
- **(c) Raw Execution Result:** `PASSED`
- **(d) Produced Attributes:**
  - `resolution_status`: `"VERIFIED"`
  - `reasoning`: `"Resolved via super() parent class method lookup"`
  - `target`: `"function:main.py:Base.setup"`

---

### Case 3: Decorated Method (`@staticmethod` / `@property`)
- **(a) Fixture Source Code:**
  - `main.py`:
    ```python
    class Service:
        @property
        def status(self):
            return "active"

        @staticmethod
        def helper():
            pass

    def run():
        Service.helper()
    ```
- **(b) Test Assertion Code:**
  ```python
  def test_case_12_decorators():
      parsed, _, edges = analyze_fixture("decorators")
      main_file = [p for p in parsed if p["file"] == "main.py"][0]
      funcs = main_file["functions"]
      status_func = [f for f in funcs if f["name"] == "status"][0]
      helper_func = [f for f in funcs if f["name"] == "helper"][0]

      assert status_func["is_property"] is True
      assert helper_func["is_staticmethod"] is True
  ```
- **(c) Raw Execution Result:** `PASSED`
- **(d) Produced Attributes for `Service.helper()` Call:**
  - `resolution_status`: `"UNRESOLVED"`
  - `reasoning`: `"Symbol definition not found in repository index"`
  - `target`: `"unresolved:Service.helper"`
  > **Audit Finding:** The AST parser extracts property/staticmethod flags (`is_property: True`, `is_staticmethod: True`). Call resolution on un-imported class staticmethod (`Service.helper()`) returns `UNRESOLVED`.

---

### Case 4: Package Re-export (`from .sub import X` inside `__init__.py`)
- **(a) Fixture Source Code:**
  - `pkg/__init__.py`: `from .sub import exported_func`
  - `pkg/sub.py`: `def exported_func(): pass`
  - `main.py`: `from pkg import exported_func; def run(): exported_func()`
- **(b) Test Assertion Code:**
  ```python
  def test_case_11_package_reexport():
      _, _, edges = analyze_fixture("package_reexport")
      calls = [e for e in edges if e["type"] == "CALLS"]
      assert len(calls) == 1
      assert calls[0]["resolution_status"] == "VERIFIED"
  ```
- **(c) Raw Execution Result:** `PASSED`
- **(d) Produced Attributes:**
  - `resolution_status`: `"VERIFIED"`
  - `reasoning`: `"Resolved via __init__.py package re-export"`
  - `target`: `"function:pkg/sub.py:exported_func"`

---

### Case 5: Ambiguous Case (Same Function Name in Two Unrelated Modules)
- **(a) Fixture Source Code:**
  - `mod_a.py`: `def process(): pass`
  - `mod_b.py`: `def process(): pass`
  - `main.py`: `def run(): process()`
- **(b) Test Assertion Code:**
  ```python
  def test_case_7_ambiguous():
      _, _, edges = analyze_fixture("ambiguous")
      calls = [e for e in edges if e["type"] == "CALLS"]
      assert len(calls) == 1
      assert calls[0]["resolution_status"] == "AMBIGUOUS"
      assert calls[0]["reasoning"] == "Multiple candidate symbols match without disambiguating scope"
  ```
- **(c) Raw Execution Result:** `PASSED`
- **(d) Produced Attributes:**
  - `resolution_status`: `"AMBIGUOUS"`
  - `reasoning`: `"Multiple candidate symbols match without disambiguating scope"`
  - `target`: `"ambiguous:process"`

---

## 3. Grep for Fake-Pass Patterns (Raw Output)

### Grep 1: `return.*VERIFIED` in `backend/` (`*.py`)
```text
=== GREP 1: return.*VERIFIED in backend/ (*.py) ===
(No matches found)
```

### Grep 2: `TODO|FIXME|not implemented|hardcoded|placeholder|stub` in `backend/` & `frontend/src/`
```text
=== GREP 2: TODO|FIXME|not implemented|hardcoded|placeholder|stub in backend/ and frontend/src/ (*.py, *.jsx, *.tsx) ===
frontend\src\App.jsx:57:placeholder="GitHub Repo URL (Python)"
frontend\src\components\ChatPanel.jsx:119:placeholder="Paste Gemini API Key here..."
frontend\src\components\ChatPanel.jsx:203:placeholder={selectedNode ? `Ask about ${selectedNode.name}...` : "Select a node first..."}
frontend\src\components\GraphView.jsx:206:placeholder="Search symbols or files..."
```

### Grep 3: `assert True|pass  #|# always|# just return` in `backend/tests/`
```text
=== GREP 3: assert True|pass  #|# always|# just return in backend/tests/ (*.py) ===
backend\tests\test_advanced_spec_cases.py:122:assert True
```

---

## 4. Real-World Validation (Live Re-run Output)

**Target Repository:** `psf/requests` (`main` branch archive downloaded live)  

```text
=== REAL-WORLD VALIDATION LIVE RUN ===
Downloading psf/requests main.zip...
Fetch/Download Time: 2.632s
Files Analyzed: 37 (Time: 0.702s)
Symbol Index & Resolution Time: 0.019s
Graph Build Time: 0.047s
TOTAL RUNTIME: 3.400s

Edge Resolution Status Breakdown:
  VERIFIED: 1585
  EXTERNAL: 1371
  UNRESOLVED: 1173
  AMBIGUOUS: 3
  Total Edges: 4132

3 Example Edges with Evidence:
Example 1:
  Type: IMPORTS
  Source: file:setup.py
  Target: module:sys
  Status: EXTERNAL
  Reasoning: External library or standard library package
  Evidence: {
    "file": "setup.py",
    "line": 1,
    "expression": "import sys",
    "context": null
}

Example 2:
  Type: IMPORTS
  Source: file:setup.py
  Target: external:setuptools.setup
  Status: EXTERNAL
  Reasoning: External library or standard library package
  Evidence: {
    "file": "setup.py",
    "line": 7,
    "expression": "from setuptools import setup",
    "context": null
}

Example 3:
  Type: CALLS
  Source: file:setup.py
  Target: unresolved:write
  Status: UNRESOLVED
  Reasoning: Symbol definition not found in repository index
  Evidence: {
    "file": "setup.py",
    "line": 4,
    "expression": "sys.stderr.write(\"Requests requires Python 3.10 or later.\\n\")",
    "context": null
}
```

### Scope Discrepancy Note:
- `docs/REAL_WORLD_VALIDATION.md` recorded **22 files** and **132 edges** (analyzing strictly `src/requests`).
- Live archive run parsed **37 files** (including `tests/`, `setup.py`, `docs/conf.py`) and extracted **4,132 edges**.

---

## 5. Rate Limiting — Raw HTTP Responses (12 Rapid Requests)

```text
=== RATE LIMITING RAW RESPONSES (12 RAPID REQUESTS) ===
Request #1: Status = 500, Body = {"detail":"Mocked clone failure"}
Request #2: Status = 500, Body = {"detail":"Mocked clone failure"}
Request #3: Status = 500, Body = {"detail":"Mocked clone failure"}
Request #4: Status = 500, Body = {"detail":"Mocked clone failure"}
Request #5: Status = 500, Body = {"detail":"Mocked clone failure"}
Request #6: Status = 500, Body = {"detail":"Mocked clone failure"}
Request #7: Status = 500, Body = {"detail":"Mocked clone failure"}
Request #8: Status = 500, Body = {"detail":"Mocked clone failure"}
Request #9: Status = 500, Body = {"detail":"Mocked clone failure"}
Request #10: Status = 500, Body = {"detail":"Mocked clone failure"}
Request #11: Status = 429, Body = {"detail":"Rate limit exceeded. Maximum 10 analysis requests per minute per IP. Retry after 58 seconds."}
Request #12: Status = 429, Body = {"detail":"Rate limit exceeded. Maximum 10 analysis requests per minute per IP. Retry after 58 seconds."}
```

---

## 6. End-to-End Performance Timing Breakdown

**Target Repository:** `pallets/flask` (`main` branch archive)  

```text
Target Repo: pallets/flask (main branch archive)
Files Analyzed: 83
1. Fetch/Download (Shallow Clone equivalent): 2.9733 s
2. AST Parse & Fact Extraction (Pass 1): 1.4796 s
3. Symbol Index & Resolution (Pass 2): 0.0291 s
4. NetworkX Graph Build & Validation Pass: 0.0697 s
TOTAL END-TO-END PIPELINE TIME: 4.5517 s
```

---

## 7. Literal Step-by-Step README Verification

### 7.1 Backend Setup (`pip install -r requirements.txt`)
```text
Requirement already satisfied: fastapi>=0.115.0 in ... (0.120.4)
Requirement already satisfied: uvicorn>=0.34.0 in ... (0.35.0)
Requirement already satisfied: python-dotenv>=1.1.0 in ... (1.2.1)
Requirement already satisfied: networkx>=3.4 in ... (3.5)
Requirement already satisfied: pytest>=8.3.0 in ... (8.4.2)
Installing collected packages: google-auth, google-genai
Successfully installed google-auth-2.57.0 google-genai-2.20.0
```

### 7.2 Backend Test Suite (`python -m pytest`)
```text
============================= 59 passed in 2.04s ==============================
```

### 7.3 Frontend Setup (`npm install`)
```text
up to date, audited 96 packages in 3s
found 0 vulnerabilities
```

### 7.4 Frontend Build (`npm run build`)
```text
> frontend@0.0.0 build
> vite build

vite v8.2.2 building client environment for production...
transforming...
✓ 2892 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                   0.45 kB │ gzip:   0.29 kB
dist/assets/index-BHABdZX6.css    4.68 kB │ gzip:   1.46 kB
dist/assets/index-DQFRHcKg.js   462.26 kB │ gzip: 148.56 kB

✓ built in 1.09s
```
