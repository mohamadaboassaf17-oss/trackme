import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.database import engine, Base
from app.routers import auth, attendance, salary, expenses, goals, settings, wealth
from app.utils.limiter import limiter

Base.metadata.create_all(bind=engine)
try:
    from sqlalchemy import inspect, text as sql_text
    inspector = inspect(engine)
    existing_columns = [c["name"] for c in inspector.get_columns("users")]
    if "email" not in existing_columns:
        with engine.connect() as conn:
            conn.execute(sql_text("ALTER TABLE users ADD COLUMN email VARCHAR(255) UNIQUE"))
            conn.commit()
            print("Added missing email column to users table")
    if "work_days_per_week" not in existing_columns:
        with engine.connect() as conn:
            conn.execute(sql_text("ALTER TABLE users ADD COLUMN work_days_per_week INTEGER DEFAULT 6"))
            conn.commit()
            print("Added missing work_days_per_week column to users table")
    if "oauth_provider" not in existing_columns:
        with engine.connect() as conn:
            conn.execute(sql_text("ALTER TABLE users ADD COLUMN oauth_provider VARCHAR(50)"))
            conn.commit()
            print("Added missing oauth_provider column to users table")
    if "oauth_id" not in existing_columns:
        with engine.connect() as conn:
            conn.execute(sql_text("ALTER TABLE users ADD COLUMN oauth_id VARCHAR(255)"))
            conn.commit()
            print("Added missing oauth_id column to users table")
    if "expected_days_per_month" not in existing_columns:
        with engine.connect() as conn:
            conn.execute(sql_text("ALTER TABLE users ADD COLUMN expected_days_per_month INTEGER DEFAULT 26"))
            conn.commit()
            print("Added missing expected_days_per_month column to users table")
    if "avatar_url" not in existing_columns:
        with engine.connect() as conn:
            conn.execute(sql_text("ALTER TABLE users ADD COLUMN avatar_url VARCHAR(500)"))
            conn.commit()
            print("Added missing avatar_url column to users table")
except Exception as e:
    print(f"Migration note: {e}")

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
