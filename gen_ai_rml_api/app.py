import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import MetaData

from gen_ai_rml_api.api import api_router
from gen_ai_rml_api.database import Base, engine, get_tables
from gen_ai_rml_api.database.connection import engine

logger = logging.get_logger(__name__)


def create_tables():
    """Create SQLAlchemy models."""
    MetaData()
    tables = get_tables()
    Base.metadata.create_all(bind=engine, tables=tables)


def create_app() -> FastAPI:
    """Create app."""

    create_tables()
    app = FastAPI()
    origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(router=api_router)

    logger.info(f"Initializing app")

    return app
