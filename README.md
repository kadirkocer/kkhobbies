# Hobby Showcase — Local-First (Single User) v2

A portable, single-user hobby journal with a schema-driven type registry, local media storage, SQLite + FTS5 search, and a Next.js admin UI. Future-proofed for multi-user cloud.

## Features

- **Local-First**: SQLite database with local file storage
- **Schema-Driven**: Dynamic hobby types via JSON Schema registry
- **Full-Text Search**: Fast FTS5 search across entries
- **Media Support**: Image, video, audio, and document uploads
- **Type System**: Extensible entry properties with validation
- **Import/Export**: Portable data with optional encryption

## Quick Start

```bash
# Initialize the project
make init

# Run development servers
make run

# Access the application
# API: http://localhost:8000
# Web: http://localhost:3000
```

## Architecture

- **Backend**: FastAPI + SQLAlchemy + SQLite + FTS5
- **Frontend**: Next.js (App Router) + React + TailwindCSS
- **Database**: SQLite with FTS5 virtual tables
- **Auth**: Single user with bcrypt password hashing
- **Storage**: Local filesystem for media uploads

## Project Structure

```
apps/
├── api/          # FastAPI backend
└── web/          # Next.js frontend
packages/
└── shared/       # Shared types and schemas
data/             # SQLite database (gitignored)
uploads/          # Media files (gitignored)
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

- `APP_ENV=local`
- `API_PORT=8000` 
- `WEB_PORT=3000`
- `DB_PATH=./data/app.db`
- `UPLOAD_DIR=./uploads`
- `SESSION_SECRET=your-secret-key`
- `ADMIN_INITIAL_USERNAME=admin`
- `ADMIN_INITIAL_PASSWORD=change_me`# kkhobbies
