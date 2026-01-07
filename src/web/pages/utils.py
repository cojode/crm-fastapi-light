from fastapi import Request, HTTPException, Response, status
from fastapi.responses import RedirectResponse

from src.web.pages.templates import templates
from src.exceptions import PagesError
from src.logger import logger
from src.settings import settings
from pydantic_settings import BaseSettings

import datetime

from fastapi_csrf_protect import CsrfProtect

from http.cookies import SimpleCookie

from typing import Any

from src.exceptions import (
    NotFoundDomainError,
    ForbiddenDomainError,
    DomainError,
)


class FragileSession:
    def __init__(self, request):
        self.request: Request = request

    def __getattribute__(self, name: str) -> Any:
        if name == "request":
            return super().__getattribute__(name)
        return self.request.session.pop(name, None)

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "request":
            super().__setattr__(name, value)
        else:
            self.request.session[name] = value


class CsrfSettings(BaseSettings):
    secret_key: str = settings.secret_key
    token_key: str = "csrf_token"
    token_location: str = "body"


@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings()


def auto_templated_response(
    request: Request,
    template_name: str,
    csrf_protect: CsrfProtect,
    current_user: Any | None = None,
    **kwargs,
):
    csrf_token, signed_token = csrf_protect.generate_csrf_tokens()
    fs = FragileSession(request)
    response = templates.TemplateResponse(
        template_name,
        {
            "request": request,
            "csrf_token": csrf_token,
            "message": fs.message,
            "errors": fs.errors,
            "current_user": current_user,
            **kwargs,
        },
    )
    csrf_protect.set_csrf_cookie(signed_token, response)
    return response


def auto_redirect_response(response: Response, redirect_path: str):
    return RedirectResponse(
        redirect_path,
        status_code=status.HTTP_303_SEE_OTHER,
        headers=dict(response.headers),
    )


async def attempt_response_with_pages_errors(
    response_coro, redirect_path: str, unexpected_error_message: str
):
    try:
        return await response_coro
    except (NotFoundDomainError, ForbiddenDomainError):
        raise
    except (DomainError, HTTPException) as e:
        raise PagesError(str(e), redirect_path=redirect_path) from e
    except Exception as e:
        logger.error("Unexpected error: %s", str(e))
        raise PagesError(unexpected_error_message, redirect_path=redirect_path) from e


def set_cookie_as_requested(
    inner_response: Response, outer_response: Response
) -> Response:
    cookies = SimpleCookie()
    for header in inner_response.raw_headers:
        if header[0].decode().lower() == "set-cookie":
            cookies.load(header[1].decode())

    for _, cookie in cookies.items():
        outer_response.set_cookie(
            key=cookie.key,
            value=cookie.value,
            max_age=cookie.get("max-age", None),
            expires=cookie.get("expires", None),
            path=cookie.get("path", "/"),
            domain=cookie.get("domain", None),
            secure=cookie.get("secure", False),
            httponly=cookie.get("httponly", False),
            samesite=cookie.get("samesite", "lax"),
        )
    return outer_response


def query_daterange_as_datetime(
    raw_start_date: str | None,
    raw_end_date: str | None,
    date_format: str = "%Y-%m-%d",
) -> tuple[datetime.datetime | None, datetime.datetime | None]:
    start_date, end_date = None, None
    try:
        start_date = datetime.datetime.strptime(raw_start_date, date_format)
        start_date = datetime.datetime.combine(start_date, datetime.time.min)
    except Exception:
        pass
    try:
        end_date = datetime.datetime.strptime(raw_end_date, date_format)
        end_date = datetime.datetime.combine(end_date, datetime.time.max)
    except Exception:
        pass
    return start_date, end_date
