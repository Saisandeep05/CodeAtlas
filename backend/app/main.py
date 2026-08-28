import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.middleware.rate_limiter import rate_limit_middleware
from config import ALLOWED_ORIGINS

# Configure structured logging for production
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("codeatlas")

app = FastAPI(
    title="CodeAtlas API",
    description="Verified Architecture Explorer for Python Repositories",
    version="2.0.0"
)

app.middleware("http")(rate_limit_middleware)

# Enable configured CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Mount router under both default /api and versioned /api/v1
app.include_router(router, prefix="/api")
app.include_router(router, prefix="/api/v1")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"An internal server error occurred: {str(exc)}", "error_code": "INTERNAL_SERVER_ERROR"}
    )

@app.get("/")
def read_root():
    return {
        "name": "CodeAtlas Verified Architecture Explorer API",
        "version": "2.0.0",
        "status": "online",
        "endpoints": ["/api/analyze", "/api/v1/analyze", "/docs"]
    }

