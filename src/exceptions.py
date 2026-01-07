from fastapi import HTTPException, status, Request
from fastapi.responses import RedirectResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from src.logger import logger
from src.settings import settings
import re


class RepositoryError(Exception): ...


class DomainError(Exception): ...


class NotFoundDomainError(DomainError): ...


class ForbiddenDomainError(DomainError): ...


async def domain_error_handler(request: Request, exc):
    if isinstance(exc, NotFoundDomainError):
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc))
    if isinstance(exc, ForbiddenDomainError):
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(exc))
    raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc))


class PagesError(Exception):

    def __init__(
        self,
        message: str,
        redirect_path: str | None = None,
        status_code: int = 303,
    ):
        self.message = message
        self.redirect_path = redirect_path
        self.status_code = status_code


class PageValidationError(PagesError):
    def __init__(self, errors: list[str], redirect_path: str | None = None):
        super().__init__("Validation error", redirect_path)
        self.errors = errors


class PageCsrfError(PagesError):
    def __init__(self, error: str, redirect_path: str | None = None):
        super().__init__("CSRF error", redirect_path)
        self.error = error


def _replace_after_uuids(text) -> str:
    uuid_pattern = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
    matches = list(re.finditer(uuid_pattern, text, re.IGNORECASE))
    if not matches:
        return text
    last_match = matches[-1]
    return text[: last_match.end()]


def pages_error_handler(request: Request, exc):
    base_path = exc.redirect_path or str(request.url.path)
    base_path = settings.custom_error_redirects.get(base_path, base_path)
    base_path = _replace_after_uuids(base_path)
    errors = getattr(exc, "errors", [exc.message])
    logger.error("Pages errors: %s", errors)
    request.session["errors"] = errors
    return RedirectResponse(base_path, status_code=exc.status_code)


def csrf_exception_handler(request: Request, exc):
    raise PageCsrfError(str(exc), redirect_path=request.url.path)


def validation_exception_handler(request: Request, exc):
    errors = []
    if isinstance(exc, RequestValidationError):
        for error in exc.errors():
            field = "→".join(map(str, error["loc"]))
            errors.append(f"{field}: {error['msg']}")
    elif isinstance(exc, ValidationError):
        for error in exc.errors():
            field = "→".join(map(str, error["loc"]))
            errors.append(f"{field}: {error['msg']}")

    raise PageValidationError(errors=errors, redirect_path=request.url.path)
