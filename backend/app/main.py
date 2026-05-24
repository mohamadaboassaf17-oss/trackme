import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.database import engine, Base
from app.routers import auth, attendance, salary, expenses, goals, settings, wealth

Base.metadata.create_all(bind=engine)

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="TrackMe API",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

app.include_router(auth.router)
app.include_router(attendance.router)
app.include_router(salary.router)
app.include_router(expenses.router)
app.include_router(goals.router)
app.include_router(settings.router)
app.include_router(wealth.router)


@app.get("/health")
async def health_check_root():
    return {"status": "ok", "app": "TrackMe", "version": "2.0.0"}


@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "TrackMe API is running"}


@app.get("/")
def root():
    return {
        "app": "TrackMe API",
        "version": "2.0.0",
        "docs": "/api/docs",
        "health": "/api/health",
    }
