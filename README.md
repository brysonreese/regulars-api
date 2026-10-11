# Regulars API

The backend for Regulars, a social iOS app for sharing restaurant, bar, and café reviews and check-ins. It currently provides a minimal FastAPI service and a small PostgreSQL connectivity example.

## Prerequisites

- [uv](https://docs.astral.sh/uv/)
- Python 3.12 (uv can install and manage the required version)

## Install

From the project root, sync the locked dependencies:

```bash
uv sync --dev
```

## Run locally

```bash
uv run uvicorn main:app --reload
```

The API is available at `http://127.0.0.1:8000`. FastAPI's interactive documentation is at `http://127.0.0.1:8000/docs`.

## Run tests

```bash
uv run pytest
```

## Endpoints

| Method | Path | Response |
| --- | --- | --- |
| `GET` | `/` | `{"message": "Regulars API is running!"}` |
| `GET` | `/health` | `{"status": "ok"}` |
| `GET` | `/db-check` | Runs `SELECT 1` and returns `{"database": "connected"}` when PostgreSQL is reachable |
| `GET` | `/docs` | FastAPI interactive API documentation |

## PostgreSQL connection demo

In Railway, add a PostgreSQL service to the same project. In the API service's Variables tab, add `DATABASE_URL` as a reference to the PostgreSQL service's `DATABASE_URL` variable (for example, `${{Postgres.DATABASE_URL}}`, using your database service's actual name). Railway's `DATABASE_URL` uses private networking for services in the same project, so the database does not need public access.

Redeploy the API, then request `https://your-api-domain.up.railway.app/db-check`. A successful response means SQLAlchemy connected through Psycopg and ran `SELECT 1`. The endpoint does not create tables or store data; it is just a connection check. `/health` remains independent of PostgreSQL.

For local development, set `DATABASE_URL` to a PostgreSQL database reachable from your machine. Keep the value in an ignored `.env` file or your shell environment; never commit credentials. Without that variable, the rest of the API still runs, and `/db-check` responds with HTTP 503.

## Railway deployment

The production start command is `uv run uvicorn main:app --host 0.0.0.0 --port $PORT`. Railway should install uv and use the committed `uv.lock` during its build.
