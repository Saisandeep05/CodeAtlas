# CodeAtlas — Final Verification Gate & Execution Log

This document records the actual, empirical terminal execution logs for the final quality gate of **CodeAtlas**.

---

## 1. Full Backend Test Suite Execution (`python -m pytest`)

```text
============================= test session starts =============================
platform win32 -- Python 3.13.9, pytest-8.4.2, pluggy-1.5.0
rootdir: CodeAtlas/backend
plugins: anyio-4.11.0
collected 59 items

tests\integration\test_api_flow_integration.py ..                        [  3%]
tests\security\test_cloning_and_limits.py ...                            [  8%]
tests\security\test_prompt_injection.py ..                               [ 11%]
tests\security\test_security_limits.py ..                                [ 15%]
tests\test_advanced_spec_cases.py ..                                     [ 18%]
tests\test_api_endpoints.py ......                                       [ 28%]
tests\test_backend.py .....                                              [ 37%]
tests\test_real_world_validation.py .                                    [ 38%]
tests\test_spec_cases.py .                                               [ 40%]
tests\unit\test_domain_models.py ..                                      [ 44%]
tests\unit\test_stage1_resolvers.py .............                        [ 66%]
tests\unit\test_stage2_api_caching.py ...                                [ 71%]
tests\unit\test_stage2_graph.py ......                                   [ 81%]
tests\unit\test_stage2_graph_engine.py ....                              [ 88%]
tests\unit\test_stage2_query_engine.py ....                              [ 94%]
tests\unit\test_stage3_api_llm.py ...                                    [100%]

============================= 59 passed in 1.98s ==============================
```

---

## 2. Security Test Subset Execution (`python -m pytest tests/security`)

```text
============================= test session starts =============================
platform win32 -- Python 3.13.9, pytest-8.4.2, pluggy-1.5.0
rootdir: CodeAtlas/backend
plugins: anyio-4.11.0
collected 7 items

tests\security\test_cloning_and_limits.py ...                            [ 42%]
tests\security\test_prompt_injection.py ..                               [ 71%]
tests\security\test_security_limits.py ..                                [100%]

============================== 7 passed in 0.45s ==============================
```

---

## 3. Frontend Production Asset Build (`npm run build`)

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

✓ built in 710ms
```

---

## 4. Verification Check Invariants Confirmed

- **No Code Execution**: Cloned code is analyzed purely via `ast.parse()`.
- **Evidence Integrity**: 100% of `VERIFIED` edges reference explicit `file` and `line` numbers.
- **Zero-LLM Structural Queries**: Structural questions bypass the LLM entirely (`response_source = "GRAPH"`, `verification_level = "VERIFIED_GRAPH_QUERY"`).
- **Prompt Injection Defense**: Repository code comments/docstrings are treated strictly as untrusted data.
- **No Secret Leaks**: API keys are passed via env vars (`GEMINI_API_KEY`, `OPENROUTER_API_KEY`) and never logged or sent to the client.
- **Clean Production Build**: 0 warnings or errors in frontend asset compilation.
