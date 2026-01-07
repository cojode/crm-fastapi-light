from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from src.db.database import AsyncDatabase
from src.db.models import load_all_models
from src.logger import setup_logger
from src.settings import settings
from fastapi import FastAPI
from sqladmin import Admin
from src.web.model_admin import admin_view_list


def _setup_db(app: FastAPI) -> AsyncDatabase:
    db = AsyncDatabase(settings.full_database_url)
    app.state.db_engine = db.engine
    app.state.db_session_factory = db.session_factory
    return db


def _setup_admin(app: FastAPI):
    admin = Admin(app, app.state.db_engine)
    for admin_view in admin_view_list:
        admin.add_view(admin_view)


@asynccontextmanager
async def lifespan_setup(
    app: FastAPI,
) -> AsyncGenerator[None, None]:
    """Actions to run on application startup."""
    setup_logger()
    _setup_db(app)
    _setup_admin(app)
    load_all_models()

    yield
    await app.state.db_engine.dispose()
