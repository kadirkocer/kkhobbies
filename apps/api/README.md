# Hobby Showcase API

FastAPI backend for the Hobby Showcase application.

## Features

- FastAPI with SQLAlchemy ORM
- SQLite database with FTS5 search
- JWT authentication
- Media file upload
- JSON Schema validation for dynamic types
- Comprehensive REST API

## Development

```bash
# Install dependencies
pip install -e .

# Run development server
uvicorn app.main:app --reload

# Initialize database
python -m app.cli init
```