# Regulars API

The backend for Regulars, a social iOS app for sharing restaurant, bar, and café reviews and check-ins. This initial milestone provides a minimal FastAPI service, ready for local development.

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
| `GET` | `/docs` | FastAPI interactive API documentation |

## Railway deployment (planned)

The next milestone is to deploy this service from GitHub to Railway. The production start command will be `uv run uvicorn main:app --host 0.0.0.0 --port $PORT`; deployment configuration will ensure Railway installs uv and uses the committed `uv.lock`. PostgreSQL integration will follow after the API deployment is confirmed.
