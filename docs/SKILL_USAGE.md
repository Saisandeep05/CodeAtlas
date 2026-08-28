# CodeAtlas — Skill & MCP Ecosystem Usage Matrix

This document records the Antigravity skill and tool ecosystem deployed across the implementation phases of **CodeAtlas — Verified Architecture Explorer**.

---

## Skill & MCP Usage Matrix

| Skill / Tool | Primary Purpose | Stage Used | Files / Components Affected | Verified Result |
| :--- | :--- | :--- | :--- | :--- |
| `senior-architect` / `architect-review` | Design formal data contracts & two-pass AST architecture | Stage 1 & 2 | `domain_models.py`, `code_parser.py`, `symbol_resolver.py` | Established typed `dataclass` contracts (`ImportBinding`, `RawCall`, `ResolvedRelationship`) and two-pass AST pipeline. |
| `tdd-workflow` / `test-driven-development` | Test-driven development for AST parsing, aliases & resolution | Stage 2, 3 & 8 | `tests/unit/`, `tests/integration/`, `tests/security/` | Developed 25 comprehensive test cases with RED-GREEN-REFACTOR cycle. |
| `security-checklist` | Repository clone safety, URL validation, and resource limits audit | Stage 7 & 8 | `github_service.py`, `tests/security/test_security_limits.py` | Enforced domain validation (`github.com`), 500 file limit, 1MB file size limit, 25MB total limit, and cleanup guarantees. |
| `frontend-design` | Responsive, accessible 2D graph UX & detail sidebars | Stage 6 | `GraphView.jsx`, `NodeDrawer.jsx`, `EvidencePanel.jsx`, `App.jsx` | Built interactive force graph with node search, camera zoom controls, node drawer, and line-level evidence drawer. |
| `docker-management` / `devex-review` | Containerization & developer quickstart workflow | Stage 10 | `docker-compose.yml`, `.env.example`, `README.md` | Single-command container deployment (`docker-compose up --build`). |
| `code-reviewer` | Independent quality gate auditing against false `VERIFIED` edges | Stage 11 & 12 | All backend & frontend files | Verified 100% deterministic evidence backing for all `VERIFIED` edges with zero relationship hallucination. |
| `docs-generator` / `craft-documentation` | Comprehensive technical documentation suite | Stage 10 & 12 | `docs/` directory | Created 10 comprehensive architecture, security, API, testing, and validation manuals. |

---

## MCP Server Integrations
- **codebase-memory-mcp**: Graph schema inspection and symbol trace navigation.
- **StitchMCP**: Visual component reference and design tokens verification.
