<div align="center">

# 🗺️ CodeAtlas

### Verified Architecture Explorer for Python Repositories

[![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&size=19&pause=1000&color=38BDF8&center=true&vCenter=true&width=600&lines=Verified%2C+not+guessed.;Static+analysis%2C+not+LLM+hallucination.;See+exactly+what+breaks+before+you+change+it.)](https://git.io/typing-svg)

[![CodeAtlas CI](https://github.com/Saisandeep05/CodeAtlas/actions/workflows/ci.yml/badge.svg)](https://github.com/Saisandeep05/CodeAtlas/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-2.0.0-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev)
[![Tests Passing](https://img.shields.io/badge/tests-62%20passed-brightgreen.svg)](docs/TESTING.md)

</div>

---

## 💡 Pitch

**CodeAtlas** turns complex Python codebases into interactive, mathematically verified dependency and call graphs using deterministic Abstract Syntax Tree (AST) static analysis. Unlike typical repository chatbots that chunk code text into an LLM and let it guess structural relationships, CodeAtlas extracts line-level facts first—ensuring every imports link, method call, and inheritance boundary is proven before an LLM ever narrates it.

---

## 🖼️ Interface Preview

<!-- TODO: replace with real demo GIF before publishing further -->
![CodeAtlas Interactive Architecture Explorer](frontend/src/assets/hero.png)

---

## 📋 Table of Contents

- [Why CodeAtlas](#-why-codeatlas)
- [Key Features](#-key-features)
- [Architecture & Data Pipeline](#-architecture--data-pipeline)
- [Quick Start](#-quick-start)
- [API Usage Examples](#-api-usage-examples)
- [Testing & Quality Verification](#-testing--quality-verification)
- [Real-World Validation](#-real-world-validation)
- [Known Limitations](#-known-limitations)
- [Future Roadmap](#-future-roadmap)
- [License](#-license)

---

## ⚡ Why CodeAtlas

Most repository assistant tools rely entirely on Retrieval-Augmented Generation (RAG) over raw code chunks. When asked *"What components call function X?"*, an LLM guesses relationships based on text similarity, often producing plausible-sounding but incorrect structural assertions.

| Architectural Dimension | Typical RAG Repo Chatbot | CodeAtlas Deterministic Parser |
| :--- | :--- | :--- |
| **Relationship Extraction** | LLM guesses from text chunks | Deterministic Python AST parsing |
| **Structural Answers** | Probabilistic (prone to hallucination) | 100% verified graph traversal (Zero LLM calls) |
| **Relationship Evidence** | Vague text snippets | Exact file path, line number, & source expression |
| **Inheritance & Imports** | Inferred from context | Two-pass symbol index & resolution engine |
| **Impact Analysis** | Cannot calculate distance | Transitive graph reachability & shortest paths |

---

## ✨ Key Features

1. **Deterministic AST Static Analysis**: Parses Python codebases into exact syntax trees without executing any code.
2. **Two-Pass Symbol Resolver**: Classifies every structural edge into four strict certainty statuses:
   - `VERIFIED`: Proven by static AST analysis with line-level evidence.
   - `EXTERNAL`: References standard library or third-party packages.
   - `UNRESOLVED`: Statically indeterminate reference.
   - `AMBIGUOUS`: Multiple symbol candidates match without disambiguating scope.
3. **Zero-LLM Structural Q&A**: Questions inquiring about structural reachability (*"What calls function X?"*, *"What inherits from BaseClass?"*) bypass the LLM entirely and return 100% verified graph data in milliseconds.
4. **Grounded LLM Explanations**: When conceptual explanations are requested, the prompt is strictly bound to verified graph edges, resisting prompt injection hijacking.
5. **Transitive Impact Analysis**: Evaluates *"What breaks if I change node X?"* by computing NetworkX transitive ancestors and shortest distance paths.
6. **Interactive Visual Explorer**: Built with React 19 and ForceGraph2D featuring neighborhood highlighting, graph mode filtering (`FILES`, `CLASSES`, `FUNCTIONS`, `FULL`), and 1-click sample repo loading (`flask`, `requests`, `fastapi`).

---

## 🏛️ Architecture & Data Pipeline

```mermaid
flowchart TD
    A[GitHub Repo URL] -->|Shallow Clone & Limits Check| B[Code Parser]
    B -->|Pass 1: AST Extraction| C[Raw Symbols & Imports]
    C --> D[Global Symbol Index]
    D -->|Pass 2: Resolution Rules| E[Symbol Resolver]
    E -->|Classified Edges| F[NetworkX Graph Engine]
    
    F -->|Structural Question| G[Deterministic Query Engine]
    F -->|Explanation Request| H[Grounded LLM Service]
    
    G -->|Zero-LLM Fact Response| I[FastAPI REST API /api/v1]
    H -->|Narrated Explanation| I
    
    I --> J[React 19 Interactive Visualizer]
```

---

## 🚀 Quick Start

### 1. Local Development Setup

#### Prerequisites
- Python 3.10+
- Node.js 18+
- Git

#### Backend Setup
```bash
# Navigate to backend directory
cd backend

# Copy environment configuration
cp .env.example .env

# Install dependencies
pip install -r requirements.txt

# Start FastAPI development server
uvicorn app.main:app --reload --port 8000
```
API endpoints will run at `http://localhost:8000`. Interactive OpenAPI documentation is accessible at `http://localhost:8000/docs`.

#### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Start Vite development server
npm run dev
```
Access the web explorer interface at `http://localhost:5173`.

---

### 2. Single-Command Docker Deployment

```bash
# Copy environment configuration
cp .env.example .env

# Build and launch multi-container stack
docker compose up --build
```
Access the application at `http://localhost:5173`.

---

## 📡 API Usage Examples

### 1. Analyze Repository (`POST /api/v1/analyze`)
```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
     -H "Content-Type: application/json" \
     -d '{"repository_url": "https://github.com/pallets/flask"}'
```
**Sample Response (Abbreviated):**
```json
{
  "repository_name": "flask",
  "commit_hash": "a1b2c3d",
  "status": "COMPLETED",
  "statistics": {
    "total_files": 83,
    "total_classes": 42,
    "total_functions": 312,
    "total_relationships": 1204,
    "verified_percentage": 78.4
  }
}
```

### 2. Transitive Impact Analysis (`GET /api/v1/repo/{repo_id}/impact/{node_id}`)
```bash
curl -X GET "http://localhost:8000/api/v1/repo/flask_a1b2c3d/impact/function:src/flask/app.py:Flask.dispatch_request"
```
**Sample Response:**
```json
{
  "target_node": "function:src/flask/app.py:Flask.dispatch_request",
  "affected_caller_count": 14,
  "impacted_nodes": [
    {
      "id": "function:src/flask/app.py:Flask.full_dispatch_request",
      "distance": 1,
      "relationship_type": "CALLS"
    }
  ]
}
```

---

## 🧪 Testing & Quality Verification

CodeAtlas maintains a zero-trust automated test suite covering unit invariants, API integrations, and security boundary conditions:

```bash
cd backend
python -m pytest -v
```

### Test Suite Summary
- **Total Tests**: **62 Passed** (0 failed, 0 skipped)
- **Execution Time**: ~2.71s
- **Breakdown**:
  - **Unit Tests (35)**: Dataclass domain models, symbol indexing, 15 resolver edge cases (aliases, super calls, decorators, `@staticmethod`, diamond inheritance, `if TYPE_CHECKING:` guards), NetworkX graph engine.
  - **Integration Tests (18)**: REST API flow, database cache hit/invalidation, rate limiter middleware, OpenAPI specification rendering.
  - **Security & Limits Tests (9)**: URL safety regex validation, shallow clone limits, prompt injection data isolation, temporary workspace cleanup.

---

## 📊 Real-World Validation

Benchmarked against leading open-source Python repositories (detailed evaluation logs in [`docs/REAL_WORLD_VALIDATION.md`](docs/REAL_WORLD_VALIDATION.md)):

| Repository | Scope / Target | Analyzed Files | Extracted Edges | Analysis Time | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`psf/requests`** | Core Package (`src/requests`) | 19 files | 1,773 edges | 1.12s | **VERIFIED** |
| **`psf/requests`** | Full Repository Archive | 37 files | 4,132 edges | 3.40s | **VERIFIED** |
| **`pallets/flask`** | Full Repository Archive | 83 files | 5,412 edges | 4.55s | **VERIFIED** |

---

## ⚠️ Known Limitations

1. **Language Scope**: Current parser supports Python codebases (`.py`). Multi-language AST parsing (TypeScript, Go) is planned.
2. **Dynamic Metaprogramming**: Fully dynamic runtime expressions (e.g. `getattr(obj, var)()`, `eval()`, `exec()`) cannot be resolved statically and are classified as `UNRESOLVED`.
3. **Single LLM Provider**: Current explanation pipeline connects to a single configured LLM provider (Google Gemini or OpenRouter) per instance session.

---

## 🗺️ Future Roadmap

Pulled from our architectural audit ([`docs/PORTFOLIO_AUDIT.md`](docs/PORTFOLIO_AUDIT.md)):

- [ ] **Hosted Live Demo**: Deploy public frontend on Vercel and backend container on Render/Fly.io.
- [ ] **Frontend Testing Suite**: Add Vitest + React Testing Library component tests.
- [ ] **Large Graph Visual Clustering**: Implement Louvain community collapsing & Degree-Centrality filtering for 1,000+ node codebases.
- [ ] **Multi-Language AST Parsers**: Extend two-pass symbol resolution to TypeScript and Go.

---

## 📄 License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for complete terms.
