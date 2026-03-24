import os
import time
from collections import defaultdict
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from starlette.middleware.base import BaseHTTPMiddleware
from dotenv import load_dotenv
from app.routes.chat import router as chat_router

load_dotenv()

# Disable docs/openapi endpoints — NullShield finding: OpenAPI Spec Exposed
app = FastAPI(
    title="Pixel - Pantoja Digital Chatbot",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "https://pantojadigital.com,http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Rate limiting middleware — NullShield finding: No Rate Limiting
class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 30, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "unknown")
        now = time.time()

        # Health endpoint gets a more generous limit (60 req/min for uptime monitors)
        if request.url.path == "/health":
            health_key = f"health:{client_ip}"
            self.requests[health_key] = [
                t for t in self.requests[health_key]
                if now - t < self.window_seconds
            ]
            if len(self.requests[health_key]) >= 60:
                return JSONResponse(
                    status_code=429,
                    content={"error": "Too many requests."}
                )
            self.requests[health_key].append(now)
            return await call_next(request)
        
        # Clean old requests
        self.requests[client_ip] = [
            t for t in self.requests[client_ip] 
            if now - t < self.window_seconds
        ]
        
        if len(self.requests[client_ip]) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={"error": "Too many requests. Please try again later."}
            )
        
        self.requests[client_ip].append(now)
        response = await call_next(request)
        return response


app.add_middleware(RateLimitMiddleware, max_requests=30, window_seconds=60)


# Security headers middleware — NullShield findings: HSTS, Cache-Control
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'none'"
    response.headers["X-XSS-Protection"] = "0"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), interest-cohort=()"
    response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
    # Note: Cross-Origin-Embedder-Policy omitted — require-corp breaks CORS fetch from pantojadigital.com
    
    # Suppress proxy disclosure headers
    for header in ["Via", "X-Powered-By", "Server"]:
        if header in response.headers:
            del response.headers[header]
    
    # Don't cache chat responses
    if "/api/chat" in str(request.url.path):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    
    return response


app.include_router(chat_router, prefix="/api")


@app.get("/robots.txt")
async def robots():
    return PlainTextResponse("User-agent: *\nDisallow: /\n")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "pixel-chatbot"}
