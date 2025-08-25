# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A local-first hobby journal with FastAPI backend and Next.js frontend. Single-user application with SQLite + FTS5 search, media uploads, and schema-driven hobby types.

## Development Commands

### Initial Setup
```bash
make init          # Full project setup (deps, DB, seed data)
make quickstart     # Same as init with helpful next steps
```

### Development Servers
```bash
make dev            # Start both API (8000) and web (3000) with hot reload
make run            # Start production servers
```

### Database Operations
```bash
make db-init        # Initialize database with migrations
make db-seed        # Seed with default data
make db-reset       # Reset database (destructive)
make ai-starter     # Generate 10 demo entries
```

### Code Quality
```bash
make lint           # Run ruff + black (API), eslint (web)
make lint-fix       # Auto-fix linting issues
make test           # Run pytest (API) + playwright (web)
make test-api       # API tests only
make test-web       # Web tests only
```

### Individual Commands
- **API linting**: `ruff check .` and `black --check .` (from apps/api/)
- **API testing**: `python -m pytest` (from apps/api/)  
- **Web linting**: `npm run lint` (from apps/web/)
- **Web testing**: `npx playwright test` (from apps/web/)
- **Web type checking**: `npm run type-check` (from apps/web/)
- **API server**: `python -m uvicorn app.main:app --reload --port 8000` (from apps/api/)
- **Web server**: `PORT=3000 npm run dev` (from apps/web/)

## Architecture

### Backend (FastAPI)
- **Location**: `apps/api/`
- **Python**: 3.11+ required
- **Database**: SQLite with FTS5 virtual tables for search
- **Auth**: Single-user with bcrypt + JWT tokens
- **File structure**:
  - `app/models/` - SQLAlchemy ORM models
  - `app/schemas/` - Pydantic request/response schemas  
  - `app/routers/` - FastAPI route handlers
  - `app/services/` - Business logic
  - `app/auth/` - Authentication & authorization
  - `app/db/` - Database session & FTS5 setup

### Frontend (Next.js)
- **Location**: `apps/web/`
- **Framework**: Next.js 14 with App Router
- **Styling**: TailwindCSS
- **State**: React Query (@tanstack/react-query)
- **Forms**: React Hook Form + Zod validation
- **Testing**: Playwright

### Key Models
- **HobbyType**: Schema-driven type definitions (JSON Schema)
- **Hobby**: User's hobby instances
- **Entry**: Journal entries with dynamic properties
- **EntryMedia**: File attachments (images, videos, documents)
- **User**: Single admin user

### Schema System
Dynamic hobby types defined via JSON Schema stored in `HobbyType.schema_data`. Entry properties validated against hobby type schemas using `jsonschema` library.

## Environment Setup

Copy `.env.example` to `.env` and configure:
- `DB_PATH=./data/app.db` - SQLite database location
- `UPLOAD_DIR=./uploads` - Media file storage
- `SESSION_SECRET` - JWT signing secret (change in production)
- `ADMIN_INITIAL_*` - Initial admin credentials

## Database Migrations

Uses Alembic for schema migrations:
- **Create**: `alembic revision --autogenerate -m "description"` (from apps/api/)
- **Apply**: `alembic upgrade head` (from apps/api/)
- **History**: `alembic history`

## File Uploads

Media files stored in `./uploads/` directory, served via FastAPI static files at `/api/uploads/`. Upload validation includes file type checking and image processing with Pillow.

## Full-Text Search

FTS5 virtual tables automatically maintained via SQLite triggers. Search implementation in `app/db/fts.py` and `app/routers/search.py`.