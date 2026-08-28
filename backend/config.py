"""
CodeAtlas Configuration
Central configuration module with all safety limits and constants.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# --- Analyzer Version (Invalidates Cache When Version Changes) ---
ANALYZER_VERSION = "2.0.0"

# --- Repository Safety Limits ---
MAX_PYTHON_FILES = 800
MAX_FILE_SIZE_BYTES = 3_000_000       # 3 MB per file
MAX_TOTAL_SIZE_BYTES = 150_000_000    # 150 MB total Python code
CLONE_TIMEOUT_SECONDS = 30            # 30s clone timeout

# --- Allowed Hosts ---
ALLOWED_HOSTS = ["github.com"]

# --- CORS Allowed Origins ---
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173").split(",")
    if origin.strip()
]

# --- Directories to Skip During Walk ---
SKIP_DIRECTORIES = {
    ".git", ".hg", ".svn", "__pycache__", ".tox", ".nox",
    ".eggs", "node_modules", ".venv", "venv", "env",
    ".mypy_cache", ".pytest_cache", ".ruff_cache",
    "dist", "build", "egg-info"
}

# --- LLM Configuration ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
GEMINI_MODEL = "gemini-2.5-pro"

# --- Database ---
DATABASE_PATH = os.environ.get("DATABASE_PATH", "codeatlas.db")
