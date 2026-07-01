from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..database import init_db
from .errors import register_exception_handlers
from .logging_config import configure_logging
from .routers import documents_router, router, transitions_router
from seed import main as seed_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    init_db()
    seed_db()
    yield


app = FastAPI(
    title="Compliance Obligations Tracker",
    description=("Track compliance obligations: state, due dates, documents, history."),
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://lazo-take-home.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(router)
app.include_router(transitions_router)
app.include_router(documents_router)


@app.get("/api/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}
