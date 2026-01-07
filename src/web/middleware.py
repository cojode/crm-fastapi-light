from fastapi import Request, status
from fastapi.responses import RedirectResponse
from starlette.middleware.base import (
    BaseHTTPMiddleware,
)
from starlette.responses import Response
from src.web.utils import is_web_request
from fastapi_csrf_protect import CsrfProtect

from src.web.pages.templates import templates


class HTTPCustomStatusHandlerMiddleware(BaseHTTPMiddleware):

    def __init__(
        self,
        app,
        target_status: int,
        alt_response_or_template_name: Response | str,
    ):
        super().__init__(app)
        self.alt_response = alt_response_or_template_name
        self.target_status = target_status

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if response.status_code == self.target_status and is_web_request(request):
            if isinstance(self.alt_response, str):
                return templates.TemplateResponse(
                    request, self.alt_response, status_code=self.target_status
                )
            return self.alt_response
        return response


class RedirectUnauthorizedMiddleware(HTTPCustomStatusHandlerMiddleware):
    def __init__(self, app):
        super().__init__(
            app,
            status.HTTP_401_UNAUTHORIZED,
            RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER),
        )


class HandleBadRequestMiddleware(HTTPCustomStatusHandlerMiddleware):
    def __init__(self, app):
        super().__init__(app, status.HTTP_400_BAD_REQUEST, "errors/400.html")


class HandleForbiddenMiddleware(HTTPCustomStatusHandlerMiddleware):
    def __init__(self, app):
        super().__init__(app, status.HTTP_403_FORBIDDEN, "errors/403.html")


class HandleNotFoundMiddleware(HTTPCustomStatusHandlerMiddleware):
    def __init__(self, app):
        super().__init__(app, status.HTTP_404_NOT_FOUND, "errors/404.html")


class HandleMethodNotAllowedMiddleware(HTTPCustomStatusHandlerMiddleware):
    def __init__(self, app):
        super().__init__(app, status.HTTP_405_METHOD_NOT_ALLOWED, "errors/405.html")


class CsrfProtectionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, exempt_methods: set | None = None):
        super().__init__(app)
        self.exempt_methods = exempt_methods or {"GET", "HEAD", "OPTIONS"}
        self.csrf_protect = CsrfProtect()

    async def dispatch(self, request: Request, call_next):
        if request.method in self.exempt_methods:
            return await call_next(request)

        if not is_web_request(request):
            return await call_next(request)

        await self.csrf_protect.validate_csrf(request)
        response = await call_next(request)
        self.csrf_protect.unset_csrf_cookie(response)
        return response
