import time
from typing import Dict, Tuple
from fastapi import Request, status
from fastapi.responses import JSONResponse

class RateLimiter:
    def __init__(self, requests_per_minute: int = 10):
        self.requests_per_minute = requests_per_minute
        self.window_seconds = 60
        self.client_records: Dict[str, list] = {}

    def is_allowed(self, client_ip: str) -> Tuple[bool, int]:
        now = time.time()
        window_start = now - self.window_seconds

        if client_ip not in self.client_records:
            self.client_records[client_ip] = []

        # Remove requests older than 1 minute
        self.client_records[client_ip] = [
            t for t in self.client_records[client_ip] if t > window_start
        ]

        if len(self.client_records[client_ip]) >= self.requests_per_minute:
            oldest = self.client_records[client_ip][0]
            retry_after = int(self.window_seconds - (now - oldest)) + 1
            return False, retry_after

        self.client_records[client_ip].append(now)
        return True, 0

global_rate_limiter = RateLimiter(requests_per_minute=10)

async def rate_limit_middleware(request: Request, call_next):
    if request.url.path in ("/api/analyze", "/api/v1/analyze") and request.method == "POST":
        client_ip = request.client.host if request.client else "127.0.0.1"
        allowed, retry_after = global_rate_limiter.is_allowed(client_ip)
        if not allowed:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": f"Rate limit exceeded. Maximum 10 analysis requests per minute per IP. Retry after {retry_after} seconds."},
                headers={"Retry-After": str(retry_after)}
            )
    return await call_next(request)

