# CodeAtlas Testing Framework Guide

## Test Suite Structure

```text
backend/tests/
├── unit/
│   ├── test_domain_models.py
│   ├── test_stage1_resolvers.py
│   ├── test_stage2_graph_engine.py
│   └── test_stage2_query_engine.py
├── integration/
│   └── test_api_flow_integration.py
├── security/
│   ├── test_cloning_and_limits.py
│   ├── test_prompt_injection.py
│   └── test_security_limits.py
└── fixtures/
    ├── cross_file/
    └── inheritance/
```

## Running Tests

### 1. Run Complete Pytest Suite:
```bash
cd backend
python -m pytest
```

### 2. Run Security Tests Only:
```bash
cd backend
python -m pytest tests/security
```

### 3. Run Integration Tests Only:
```bash
cd backend
python -m pytest tests/integration
```

### 4. Run Frontend Production Build Check:
```bash
cd frontend
npm run build
```
