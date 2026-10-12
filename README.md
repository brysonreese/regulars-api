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
| `POST` | `/places` | Gets or creates a place from `{"apple_place_id": "..."}` and returns its UUID and Apple Place ID |
| `POST` | `/reviews` | Creates a review using a user UUID, Apple Place ID, rating, body, and visibility |
| `GET` | `/reviews` | Lists public reviews, newest first; optionally filter by `user_id`, `place_id`, or `apple_place_id`, and set `limit` |
| `GET` | `/reviews/{review_id}` | Returns a public review, or 404 for a private or missing review |
| `PUT` | `/reviews/{review_id}` | Replaces a review's rating, body, and visibility |
| `DELETE` | `/reviews/{review_id}` | Deletes a review |
| `GET` | `/users` | Returns all users |
| `POST` | `/users` | Creates a user from JSON body `{"username": "...", "display_name": "..."}` |
| `GET` | `/users/{user_id}` | Returns one user by UUID, or 404 if it does not exist |
| `PUT` | `/users/{user_id}` | Updates username and display name from JSON body `{"username": "...", "display_name": "..."}` |
| `DELETE` | `/users/{user_id}` | Deletes a user; returns 204, or 404 if it does not exist |
| `GET` | `/docs` | FastAPI interactive API documentation |

## Project structure

`main.py` creates the FastAPI application and registers routers. HTTP endpoints are grouped by resource in `routers/`, shared database operations are in `services/`, Pydantic request/response types are in `schemas/`, and SQLAlchemy models share the `Base` metadata exported from `models/`. Alembic imports the model package so every model is registered before migration autogeneration.

### Review API notes

Ratings use integer half-stars: `1` means 0.5 stars and `10` means 5 stars. Visibility is `0` for private and `1` for public. A review body may be `null`. Creating a review looks up or creates its place from `apple_place_id`; responses include both the internal place UUID and its Apple Place ID under `place`.

For example, `POST /reviews` accepts:

```json
{"user_id":"USER_UUID","apple_place_id":"APPLE_PLACE_ID","rating":7,"body":"Great coffee","visibility":1}
```

`PUT /reviews/{review_id}` replaces `rating`, `body`, and `visibility`; send `"body": null` to clear the text. Apply the reviews migration to each database before using these routes.

Users can post multiple reviews of the same place. To show the current public review for one user and place, request `GET /reviews?user_id=USER_UUID&apple_place_id=APPLE_PLACE_ID&limit=1` and use the first result, if any. You can also filter with `place_id`, which is Regulars' UUID returned under `place.id`. Older public reviews remain in the unfiltered list. Results use `created_at` (then `id` to break ties), so editing an older review does not make it the newest. Apply the `allow multiple reviews per place` migration before using this behavior. Once duplicate reviews exist, downgrading to the old one-review constraint requires resolving those duplicates first.

The public `GET` routes hide private reviews. There is no authentication or ownership check yet: callers can supply any existing `user_id` when creating a review, and anyone who knows a review UUID can update or delete it. Add authentication and owner-only access before using these write routes with real users. The API also does not verify that an Apple Place ID is genuine. The list route does not paginate yet.

## PostgreSQL connection demo

In Railway, add a PostgreSQL service to the same project. In the API service's Variables tab, add `DATABASE_URL` as a reference to the PostgreSQL service's `DATABASE_URL` variable (for example, `${{Postgres.DATABASE_URL}}`, using your database service's actual name). Railway's `DATABASE_URL` uses private networking for services in the same project, so the database does not need public access.

Redeploy the API, then request `https://your-api-domain.up.railway.app/db-check`. A successful response means SQLAlchemy connected through Psycopg and ran `SELECT 1`. The endpoint does not create tables or store data; it is just a connection check. `/health` remains independent of PostgreSQL.

Without `DATABASE_URL`, the rest of the API still runs, and `/db-check` responds with HTTP 503. For local development, the ignored `.env` file points the API at the Compose database. Never put Railway credentials in `.env.example` or commit them to Git.

## Railway deployment

The production start command is `uv run uvicorn main:app --host 0.0.0.0 --port $PORT`. Railway should install uv and use the committed `uv.lock` during its build.

## Database schema and migrations

Alembic tracks database structure changes in `migrations/versions/`. For local development, `uv run alembic upgrade head` applies any pending migrations to the database configured in `.env`.

### Add a new table

Follow this order when adding a table, as with `places`:

1. Start the local database and bring it up to the current migration. Check that `DATABASE_URL` points to your local database, not a Railway tunnel.

   ```bash
   docker compose up -d db
   uv run alembic upgrade head
   ```

2. Add a SQLAlchemy model in `models/` using the shared `Base` from `models/base.py`. Import the new model in `models/__init__.py`; Alembic imports that package to discover all tables.
3. Generate a migration against the local database:

   ```bash
   uv run alembic revision --autogenerate -m "add <table name>"
   ```

   Open the new file in `migrations/versions/`. Confirm that `upgrade()` creates the intended table, columns, constraints, and indexes; `downgrade()` reverses it; and there are no unrelated changes. Add database objects that autogenerate misses, such as triggers, by hand. Do not edit a migration that has already been applied; create another revision for later changes.
4. Apply and check the reviewed migration locally:

   ```bash
   uv run alembic upgrade head
   uv run alembic check
   ```

5. If the table needs API access, add request/response types in `schemas/`, endpoints in `routers/`, and register the router in `main.py`. A table does not automatically need full CRUD; add the operations the app uses. Test the behavior with `uv run pytest` and try the endpoint locally.
6. Commit the model, migration, API changes, and tests together. Apply the migration to Railway using the tunnel instructions below before deploying API code that requires the new table. Deploying the API does not run Alembic automatically.

### Run migrations against Railway through an SSH tunnel

If you connect to Railway PostgreSQL from your Mac using `railway connect Postgres --tunnel-only`, leave that command running in one Terminal window. It prints a temporary local host, port, username, password, and database name. In a **second** Terminal window, from this project directory, set `DATABASE_URL` using those printed values and run the migration:

```bash
export DATABASE_URL='postgresql://postgres:YOUR_TUNNEL_PASSWORD@127.0.0.1:YOUR_TUNNEL_PORT/railway'
uv run alembic upgrade head
```

Replace the placeholders with the values shown by the active tunnel. Keep the tunnel open until Alembic finishes. The exported variable applies only to that second Terminal session; close it and you will need to set it again. Do not put the real connection URL in the README, source code, or Git.

Use a disposable development database for experiments and resets; never drop or reset the Railway production database to start over. Review every generated migration before applying it. Apply reviewed migrations with `DATABASE_URL=... uv run alembic upgrade head`.

The first migration creates the `users` table and its `updated_at` trigger on a fresh database. Railway was initialized by applying this migration through the SSH tunnel above. If a database already has a manually created `users` table but no Alembic version, compare its columns, constraints, defaults, and trigger with `migrations/versions/0001_users_baseline.py` first. Only if they match, run `uv run alembic stamp 0001_users_baseline` to record that specific migration without executing it, followed by `uv run alembic upgrade head` to create later tables. Do not stamp `head` unless every migration's schema changes are already present; doing so would skip creating missing tables.
