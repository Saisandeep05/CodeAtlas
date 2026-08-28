from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.middleware.rate_limiter import rate_limit_middleware
from config import ALLOWED_ORIGINS

app = FastAPI(title="CodeAtlas API", version="2.0.0")

app.middleware("http")(rate_limit_middleware)

# Enable configured CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/")
def read_root():
    return {
        "name": "CodeAtlas Verified Architecture Explorer API",
        "version": "2.0.0",
        "status": "online",
        "docs_url": "/docs"
    }
