# CodeAtlas Security & Safety Specification

CodeAtlas implements multi-layered security controls to protect the host environment and prevent abuse.

## 1. Repository Cloning & URL Validation Safety
- **Strict Hostname Whitelisting**: Only `https://github.com/owner/repo` URLs are accepted (`ALLOWED_HOSTS = ["github.com"]`).
- **Scheme Enforcement**: Only `https://` URLs are permitted. Schemes such as `file://`, `ftp://`, `ssh://`, `git@` are rejected.
- **Input Sanitization**: Rejects URLs containing embedded credentials (`user:pass@host`), null bytes, control characters, or command injection tokens (`;`, `&`, `|`, `` ` ``, `$`).

## 2. Hard Limits & Resource Protection
- **Max Python Files**: 800 files (`MAX_PYTHON_FILES = 800`).
- **Max File Size**: 3 MB per file (`MAX_FILE_SIZE_BYTES = 3_000_000`).
- **Max Total Clone Size**: 150 MB uncompressed code (`MAX_TOTAL_SIZE_BYTES = 150_000_000`).
- **Download Timeout**: 30 seconds (`CLONE_TIMEOUT_SECONDS = 30`).
- **Guaranteed Directory Cleanup**: Downloaded and extracted repository files are strictly deleted in `try/finally` blocks upon completion or error.

## 3. Rate Limiting & Abuse Prevention
- **Per-IP Rate Limiter**: Throttles `POST /api/analyze` to a maximum of 10 requests per minute per IP address. Exceeding requests return HTTP 429 (`Too Many Requests`).

## 4. LLM Prompt Injection Defense
- **Untrusted Input Boundary**: Source code from cloned repositories is treated strictly as **UNTRUSTED DATA ONLY**.
- **System Directives**: System prompt explicitly instructs the LLM that commands in code comments or docstrings (e.g. `ignore previous instructions`) must never be followed as commands.
