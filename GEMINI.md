## Project Overview

This project is a "Hobby Showcase," a single-user, local-first hobby journal application. It features a schema-driven type registry, local media storage, and a Next.js-based admin UI. The backend is built with FastAPI and SQLAlchemy, using a SQLite database with FTS5 for full-text search.

The architecture is composed of two main parts:

*   **Backend (`apps/api`):** A Python-based API built with the FastAPI framework. It handles data storage, user authentication, and file uploads.
*   **Frontend (`apps/web`):** A TypeScript-based web application built with Next.js and React. It provides the user interface for managing hobbies and entries.

The project is designed to be run using Docker, with a `docker-compose.yml` file for orchestrating the backend and frontend services. A `Makefile` is also provided for easy access to common development tasks.

## Building and Running

The project can be run using either Docker or local development servers.

### Docker (Recommended)

To run the application using Docker, use the following commands:

*   **Build the images:** `make docker-build`
*   **Start the services:** `make docker-up`
*   **Stop the services:** `make docker-down`

### Local Development

To run the application locally, you will need to have Python and Node.js installed.

*   **Initialize the project:** `make init`
*   **Run the development servers:** `make dev`
*   **Run the production servers:** `make run`

The API will be available at `http://localhost:8000` and the web application at `http://localhost:3000`.

## Development Conventions

### Linting

The project uses `ruff` and `black` for Python code linting and formatting, and `eslint` and `prettier` for the frontend.

*   **Run linters:** `make lint`
*   **Fix linting issues:** `make lint-fix`

### Testing

The project uses `pytest` for backend testing and `playwright` for frontend testing.

*   **Run all tests:** `make test`
*   **Run API tests:** `make test-api`
*   **Run web tests:** `make test-web`
