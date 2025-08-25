import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

from .db.fts import ensure_fts
from .db.session import SessionLocal
from .routers import (
    auth_router,
    entries_router,
    export_router,
    hobbies_router,
    hobby_types_router,
    search_router,
    users_router,
)
from .services.uploads import _resolve_upload_dir


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for FastAPI application"""
    # Startup - initialize FTS5 tables and triggers
    session = SessionLocal()
    try:
        ensure_fts(session)
    finally:
        session.close()
    yield
    # Shutdown
    pass


app = FastAPI(
    title="Hobby Showcase API",
    description="A portable, single-user hobby journal API",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers for standardized error envelope
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTPException with standardized error envelope"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": exc.status_code,
            "code": f"HTTP_{exc.status_code}",
            "message": exc.detail,
            "details": None
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors with standardized error envelope"""
    return JSONResponse(
        status_code=422,
        content={
            "status": 422,
            "code": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": exc.errors()
        }
    )


@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors with standardized error envelope"""
    return JSONResponse(
        status_code=422,
        content={
            "status": 422,
            "code": "VALIDATION_ERROR",
            "message": "Data validation failed",
            "details": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors with standardized error envelope"""
    return JSONResponse(
        status_code=500,
        content={
            "status": 500,
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "details": None
        }
    )


# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(hobbies_router, prefix="/api")
app.include_router(hobby_types_router, prefix="/api")
app.include_router(entries_router, prefix="/api")
app.include_router(search_router, prefix="/api")
app.include_router(export_router, prefix="/api")

"""Serve uploaded files under /api/uploads"""
uploads_dir: Path = _resolve_upload_dir()
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/api/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")


@app.get("/")
async def root():
    return {"message": "Hobby Showcase API", "version": "0.1.0"}


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

# Lightweight CSRF protection for cookie-auth (bypass in local)
from starlette.middleware.base import BaseHTTPMiddleware


def _csrf_enabled() -> bool:
    return os.getenv("APP_ENV", "local").lower() not in {"local", "development", "dev"}


async def _csrf_middleware(request: Request, call_next):
    if not _csrf_enabled():
        return await call_next(request)
    if request.method in {"GET", "HEAD", "OPTIONS"}:
        return await call_next(request)
    # Allow login to set initial tokens
    if request.url.path.endswith("/api/auth/login"):
        return await call_next(request)
    header = request.headers.get("X-CSRF-Token")
    cookie = request.cookies.get("csrf_token")
    if not header or not cookie or header != cookie:
        return JSONResponse(
            status_code=403,
            content={
                "status": 403,
                "code": "CSRF_FORBIDDEN",
                "message": "CSRF token missing or invalid",
                "details": None,
            },
        )
    return await call_next(request)


app.add_middleware(BaseHTTPMiddleware, dispatch=_csrf_middleware)
