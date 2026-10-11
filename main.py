from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from database import get_engine

app = FastAPI(
    title="Regulars API",
    version="0.1.0",
)


class TestTableUpdate(BaseModel):
    content: str


@app.get("/")
def home():
    return {"message": "Regulars API is running!"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/db-check")
def database_check():
    try:
        with get_engine().connect() as connection:
            connection.execute(text("SELECT 1"))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed",
        ) from exc

    return {"database": "connected"}


@app.get("/test-table")
def get_test_rows():
    with get_engine().connect() as connection:
        rows = connection.execute(
            text('SELECT id, content FROM "test-table" ORDER BY id')
        ).mappings().all()

    return [dict(row) for row in rows]


@app.post("/test-table", status_code=201)
def create_test_row(new_row: TestTableUpdate):
    with get_engine().begin() as connection:
        row = connection.execute(
            text(
                'INSERT INTO "test-table" (content) VALUES (:content) '
                'RETURNING id, content'
            ),
            {"content": new_row.content},
        ).mappings().one()

    return dict(row)


@app.get("/test-table/{row_id}")
def get_test_row(row_id: int):
    with get_engine().connect() as connection:
        row = connection.execute(
            text('SELECT id, content FROM "test-table" WHERE id = :id'),
            {"id": row_id},
        ).mappings().first()

    if row is None:
        raise HTTPException(status_code=404, detail="Row not found")

    return dict(row)


@app.put("/test-table/{row_id}")
def update_test_row(row_id: int, update: TestTableUpdate):
    with get_engine().begin() as connection:
        row = connection.execute(
            text(
                'UPDATE "test-table" SET content = :content '
                'WHERE id = :id RETURNING id, content'
            ),
            {"id": row_id, "content": update.content},
        ).mappings().first()

    if row is None:
        raise HTTPException(status_code=404, detail="Row not found")

    return dict(row)


@app.delete("/test-table/{row_id}")
def delete_test_row(row_id: int):
    with get_engine().begin() as connection:
        deleted_id = connection.execute(
            text('DELETE FROM "test-table" WHERE id = :id RETURNING id'),
            {"id": row_id},
        ).scalar_one_or_none()

    if deleted_id is None:
        raise HTTPException(status_code=404, detail="Row not found")

    return {"deleted": True, "id": deleted_id}
