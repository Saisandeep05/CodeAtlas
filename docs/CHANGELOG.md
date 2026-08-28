# Changelog

All notable changes to the CodeAtlas project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-08-28

### Added
- **Impact Analysis Engine**: Added transitive caller calculation (`GET /api/v1/repo/{repo_id}/impact/{node_id}`) ranking affected callers by shortest graph path distance using NetworkX.
- **Static Method Resolution**: `@staticmethod` call resolution (`ClassName.method()`) returning `VERIFIED` status with line-level reasoning.
- **API Versioning**: Mounted router under `/api/v1` alongside `/api`.
- **Structured Logging**: Production JSON/standard logging via `logging.getLogger("codeatlas")`.
- **Sample Repos Quick-Select**: Interactive 1-click sample repository loading on the frontend (`pallets/flask`, `psf/requests`, `fastapi/fastapi`).
- **Resolver Test Suite Additions**: Added diamond inheritance (`D(B, C) -> A`) and `if TYPE_CHECKING:` import guard test cases.
- **Dependabot Automation**: Automated dependency maintenance config in `.github/dependabot.yml`.

### Security & Hardening
- Per-IP rate limiting (`10 req/min/IP`) on repository analysis.
- Prompt injection isolation boundary treating cloned source code strictly as untrusted data.
- Strict cloning limits (max 800 files, max 3MB per file, max 150MB total, 30s timeout).
- Automated directory cleanup in `finally` blocks upon analysis failure.

---

## [1.0.0] - 2026-08-27

### Added
- Initial core architecture release: Python AST static parser, symbol indexer, two-pass symbol resolver, NetworkX graph builder, and React 19 interactive visualizer.
