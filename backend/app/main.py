import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import auth, attendance, salary, expenses, goals, settings, wealth

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TrackMe API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(attendance.router)
app.include_router(salary.router)
app.include_router(expenses.router)
app.include_router(goals.router)
app.include_router(settings.router)
app.include_router(wealth.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "TrackMe API is running"}


@app.get("/")
def root():
    return {
        "app": "TrackMe API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/api/health",
    }
