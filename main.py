from fastapi import FastAPI

from routers import health, users

app = FastAPI(
    title="Regulars API",
    version="0.1.0",
)

app.include_router(health.router)
app.include_router(users.router)
