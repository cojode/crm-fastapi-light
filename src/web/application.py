from fastapi import FastAPI
from src.web.api.router import api_router
from src.web.pages.router import pages_router
from src.web.lifespan import lifespan_setup
from starlette.middleware.sessions import SessionMiddleware

from src.settings import settings

from fastapi_csrf_protect.exceptions import CsrfProtectError
from src.exceptions import (
    DomainError,
    domain_error_handler,
    PagesError,
    pages_error_handler,
    ValidationError,
    RequestValidationError,
    validation_exception_handler,
    csrf_exception_handler,
)

from src.web.middleware import (
    RedirectUnauthorizedMiddleware,
    HandleForbiddenMiddleware,
    HandleMethodNotAllowedMiddleware,
    HandleNotFoundMiddleware,
)


def get_app() -> FastAPI:
    app = FastAPI(
        title="fastapi_crm_light",
        lifespan=lifespan_setup,
        docs_url="/api/docs",
        swagger_ui_parameters={"defaultModelsExpandDepth": -1},
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    app.include_router(router=api_router)
    app.include_router(router=pages_router)
    app.add_exception_handler(DomainError, domain_error_handler)
    app.add_exception_handler(PagesError, pages_error_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(CsrfProtectError, csrf_exception_handler)
    app.add_middleware(
        SessionMiddleware,
        same_site="strict",
        session_cookie=settings.session_cookie_name,
        secret_key=settings.secret_key,
    )
    app.add_middleware(RedirectUnauthorizedMiddleware)
    app.add_middleware(HandleForbiddenMiddleware)
    app.add_middleware(HandleNotFoundMiddleware)
    app.add_middleware(HandleMethodNotAllowedMiddleware)
    # app.add_middleware(HandleBadRequestMiddleware)

    return app
