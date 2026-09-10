import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000

        # Add server header for enterprise trace ID
        response.headers["X-Enterprise-Processing-Time-MS"] = f"{process_time:.2f}"
        response.headers["X-Enterprise-Security-Level"] = "AES-256-Local"

        return response
