import logging
from logging.config import dictConfig
from fastapi.encoders import jsonable_encoder

from src.settings import settings
import json


class LogConfig:
    """Logging configuration to be set for the FastAPI application."""

    version = 1
    disable_existing_loggers = False
    formatters = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(asctime)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "use_colors": True,
        },
    }
    handlers = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    }
    loggers = {
        "uvicorn": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.error": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
        settings.app_name: {
            "handlers": ["default"],
            "level": settings.log_level,
            "propagate": False,
        },
        "sqlalchemy": {
            "handlers": ["default"],
            "level": "WARNING",
            "propagate": False,
        },
    }


def setup_logger() -> None:
    dictConfig(LogConfig.__dict__)  # type: ignore[arg-type]


class ServiceOutputLoggerMixin:
    def __init__(self, **kwargs):
        logger.debug("Attempting to return response with service output: ")
        logger.debug(
            "\n%s",
            json.dumps(
                jsonable_encoder(kwargs),
                indent=4,
                sort_keys=True,
                ensure_ascii=False,
            ),
        )
        super().__init__(**kwargs)


logger = logging.getLogger(settings.app_name)
