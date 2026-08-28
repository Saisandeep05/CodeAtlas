# CodeAtlas — Verified Architecture Explorer for Python Repositories

[![CodeAtlas CI](https://github.com/codeatlas/CodeAtlas/actions/workflows/ci.yml/badge.svg)](https://github.com/codeatlas/CodeAtlas/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-2.0.0-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev)

> **Separate verified code facts from AI-generated explanations.**
> Unlike repository chatbots that send code chunks to an LLM and let it infer structural relationships, CodeAtlas analyzes the repository deterministically using Python AST parsing. The LLM is never treated as the authority on structural relationships.

---

## 🏛️ Core Principle & System Architecture

```text
GitHub Repository URL
        ↓
Secure Shallow Clone (30s timeout, max 150 MB clone, max 800 files, max 3 MB/file)
        ↓
Python AST Parsing & Fact Extraction (Pass 1)
        ↓
Global Symbol Index Construction
        ↓
Two-Pass Symbol Resolution (Pass 2)
[VERIFIED | EXTERNAL | UNRESOLVED | AMBIGUOUS]
        ↓
NetworkX Graph Construction & Validation Pass
        ↓
┌─────────────────────────────────┴─────────────────────────────────┐
↓                                                                   ↓
Deterministic Graph Query Engine                    Grounded LLM Explanation Service
(GRAPH ANSWER: Zero LLM Calls)                      (LLM EXPLANATION: GRAPH GROUNDED)
        ↓                                                                   ↓
└─────────────────────────────────┬─────────────────────────────────┘
                                  ↓
                        FastAPI REST API
                                  ↓
                React + Vite Interactive Frontend
```

---

## 🚀 Key Features

1. **Deterministic Static Analysis**: Extract exact imports, function calls, class definitions, and inheritance trees without executing code.
2. **Two-Pass Symbol Resolver**: Classifies relationship certainty into 4 strict categories:
   - **`VERIFIED`**: Proven by static AST analysis with line-level evidence.
   - **`EXTERNAL`**: References standard library or third-party package.
   - **`UNRESOLVED`**: Statically indeterminate reference.
   - **`AMBIGUOUS`**: Multiple symbol candidates match.
3. **Deterministic Structural Queries (Zero LLM Calls)**: Structural questions (*"What calls function X?"*, *"What does class Y inherit from?"*) bypass the LLM entirely and return 100% verified facts directly from the NetworkX graph.
4. **Interactive Architecture Graph**:
   - Filter by mode (`FILES`, `CLASSES`, `FUNCTIONS`, `FULL`).
   - Real-time search, zoom, pan, neighbor highlighting, and focus mode.
   - Accessible resolution status indicators (solid, dashed, dotted, and warning link styles with visual badges).
5. **Prompt Injection Safety Boundary**: Treats source code strictly as **UNTRUSTED DATA**, resisting prompt hijacking instructions embedded in comments or docstrings.
6. **SQLite Graph Caching**: Keyed by `repo_url + commit_hash + analyzer_version` (`2.0.0`). Re-analyzes automatically when analyzer logic changes.

---

## ⚡ Quick Start

### 1. Local Development (Without Docker)

#### Prerequisites:
- Python 3.10+
- Node.js 18+
- Git

#### Backend Setup:
```bash
# Navigate to backend directory
cd backend

# Copy environment template
cp .env.example .env

# Install Python dependencies
pip install -r requirements.txt

# Run backend API server
uvicorn app.main:app --reload --port 8000
```
Backend API will run at `http://localhost:8000`. Interactive OpenAPI documentation is available at `http://localhost:8000/docs`.

#### Frontend Setup:
```bash
# Open a new terminal in the frontend directory
cd frontend

# Install Node dependencies
npm install

# Start Vite development server
npm run dev
```
Frontend web interface will run at `http://localhost:5173`.

---

### 2. Single-Command Docker Deployment

```bash
# Clone repository
git clone https://github.com/codeatlas/CodeAtlas.git
cd CodeAtlas

# Copy environment config
cp .env.example .env

# Build and launch multi-container stack
docker compose up --build
```
Access the application at `http://localhost:5173`.

---

## 🧪 Testing & Verification

Run the comprehensive test suite (unit, integration, security):

```bash
cd backend
python -m pytest
```

---

## 🛡️ Security & Safety Guarantees

1. **No Code Execution**: Cloned code is statically parsed into an AST. Code is **never** executed.
2. **Repository Cloning Guardrails**: Accepts only `https://github.com/owner/repo` URLs. Rejects non-HTTPS schemes, command injection characters, and non-GitHub hosts.
3. **Strict Resource Limits**: Max 800 files, max 3 MB per file, max 150 MB clone size, 30s timeout.
4. **Guaranteed Cleanup**: Temporary workspace directories are strictly deleted in `finally` blocks even upon analysis failure.
5. **Rate Limiting**: Per-IP throttling on `POST /api/analyze` (max 10 requests/minute/IP).
