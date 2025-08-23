import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .db import init_db
from .routers import (
    auth_router,
    users_router,
    hobbies_router,
    hobby_types_router,
    entries_router,
    search_router,
    export_router
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for FastAPI application"""
    # Startup
    init_db()
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

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(hobbies_router, prefix="/api")
app.include_router(hobby_types_router, prefix="/api")
app.include_router(entries_router, prefix="/api")
app.include_router(search_router, prefix="/api")
app.include_router(export_router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Hobby Showcase API", "version": "0.1.0"}


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}