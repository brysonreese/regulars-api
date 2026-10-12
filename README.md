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

## Local development

The API runs directly on your Mac; Docker Compose runs a separate local PostgreSQL database. Install and start Docker Desktop, then copy the example settings once (this checkout already includes an ignored local `.env`):

```bash
cp .env.example .env
```

Set `POSTGRES_IMAGE` in `.env` to the same major version as your Railway PostgreSQL service if it differs from the example. You can check the Railway server version in pgAdmin with `SHOW server_version;`. The `.env` file is loaded by both the API and Alembic; it contains only local development credentials and is ignored by Git.

If you previously exported a Railway tunnel's `DATABASE_URL` in this Terminal, run `unset DATABASE_URL` before starting local commands so the local `.env` value is used.

Start the local database and apply the schema:

```bash
docker compose up -d db
uv run alembic upgrade head
```

Then start the API with hot reload:

```bash
uv run uvicorn main:app --reload
```

The API is available at `http://127.0.0.1:8000`. FastAPI's interactive documentation is at `http://127.0.0.1:8000/docs`.

Stop the database with `docker compose down`; its named volume keeps local data between runs. This database is separate from Railway, so local work will not change deployed data. The Docker port is bound only to your Mac's loopback interface.

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
| `GET` | `/users` | Returns all users |
| `POST` | `/users` | Creates a user from JSON body `{"username": "...", "display_name": "..."}` |
| `GET` | `/users/{user_id}` | Returns one user by UUID, or 404 if it does not exist |
| `PUT` | `/users/{user_id}` | Updates username and display name from JSON body `{"username": "...", "display_name": "..."}` |
| `DELETE` | `/users/{user_id}` | Deletes a user; returns 204, or 404 if it does not exist |
| `GET` | `/docs` | FastAPI interactive API documentation |

## PostgreSQL connection demo

In Railway, add a PostgreSQL service to the same project. In the API service's Variables tab, add `DATABASE_URL` as a reference to the PostgreSQL service's `DATABASE_URL` variable (for example, `${{Postgres.DATABASE_URL}}`, using your database service's actual name). Railway's `DATABASE_URL` uses private networking for services in the same project, so the database does not need public access.

Redeploy the API, then request `https://your-api-domain.up.railway.app/db-check`. A successful response means SQLAlchemy connected through Psycopg and ran `SELECT 1`. The endpoint does not create tables or store data; it is just a connection check. `/health` remains independent of PostgreSQL.

Without `DATABASE_URL`, the rest of the API still runs, and `/db-check` responds with HTTP 503. For local development, the ignored `.env` file points the API at the Compose database. Never put Railway credentials in `.env.example` or commit them to Git.

## Railway deployment

The production start command is `uv run uvicorn main:app --host 0.0.0.0 --port $PORT`. Railway should install uv and use the committed `uv.lock` during its build.

## Database schema and migrations

Alembic tracks database structure changes in `migrations/versions/`. For local development, `uv run alembic upgrade head` applies any pending migrations to the database configured in `.env`.

### Run migrations against Railway through an SSH tunnel

If you connect to Railway PostgreSQL from your Mac using `railway connect Postgres --tunnel-only`, leave that command running in one Terminal window. It prints a temporary local host, port, username, password, and database name. In a **second** Terminal window, from this project directory, set `DATABASE_URL` using those printed values and run the migration:

```bash
export DATABASE_URL='postgresql://postgres:YOUR_TUNNEL_PASSWORD@127.0.0.1:YOUR_TUNNEL_PORT/railway'
uv run alembic upgrade head
```

Replace the placeholders with the values shown by the active tunnel. Keep the tunnel open until Alembic finishes. The exported variable applies only to that second Terminal session; close it and you will need to set it again. Do not put the real connection URL in the README, source code, or Git.

Use a disposable development database for experiments and resets; never drop or reset the Railway production database to start over. To create a migration after changing a SQLAlchemy model:

```bash
uv run alembic revision --autogenerate -m "describe the schema change"
```

Review and edit every generated migration before applying it. Autogeneration does not capture every database object (including this project's trigger), so trigger changes must be written explicitly in a migration. Apply reviewed migrations with `DATABASE_URL=... uv run alembic upgrade head`.

The first migration creates the `users` table and its `updated_at` trigger on a fresh database. Railway was initialized by applying this migration through the SSH tunnel above. For any other database where these objects were created manually, compare the table, constraints, defaults, and trigger with `migrations/versions/0001_users_baseline.py` before running migrations. If they already match, record the baseline with `DATABASE_URL=... uv run alembic stamp head` instead of running its create-table migration; stamping records the version without executing it.
