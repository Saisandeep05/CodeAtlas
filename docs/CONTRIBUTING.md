# Contributing to CodeAtlas

Thank you for your interest in contributing to **CodeAtlas**! We welcome bug fixes, documentation improvements, and architectural enhancements.

---

## 🏛️ Core Design Principles

Before submitting code, please align with our architectural invariants:
1. **Fact-First Engineering**: Static code facts (imports, calls, inheritance) are extracted **deterministically** via Python AST. The LLM is used *only* for natural language explanations grounded in verified graph data.
2. **Zero Code Execution**: CodeAtlas never executes parsed code (`eval()`, `exec()`, or module imports are strictly prohibited).
3. **Line-Level Evidence**: Every graph relationship must carry an explicit `Evidence` object containing file path, line number, and source expression.
4. **Strict Resolution Certainty**: All symbol relationships must be classified as `VERIFIED`, `EXTERNAL`, `UNRESOLVED`, or `AMBIGUOUS`.

---

## 🛠️ Local Development Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- Git

### Backend Setup
```bash
cd backend
cp .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 Testing Guidelines

Always run the full test suite before creating a Pull Request:

```bash
cd backend
python -m pytest -v
```

New resolver rules or graph features MUST include corresponding unit tests in `backend/tests/unit/`.

---

## 📬 Pull Request Process

1. Fork the repository and create your feature branch (`git checkout -b feature/my-feature`).
2. Ensure all 60+ pytest tests pass cleanly.
3. Commit your changes with clear commit messages (`git commit -m "feat: add support for X"`).
4. Push to your branch and open a Pull Request against `main`.
