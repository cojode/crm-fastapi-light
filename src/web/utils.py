from fastapi.routing import APIRouter, APIRoute
from fastapi import Request

from typing import Sequence, Callable


def get_custom_endpoint_handler(
    target_router: APIRouter, path: str, methods: set[str]
) -> Callable:
    routes: Sequence[APIRoute] = target_router.routes
    for route in routes:
        if route.path == path and route.methods == methods:
            return route.endpoint
    raise RuntimeError(f"Custom route not found: {target_router} {path} {methods}")


def is_web_request(request: Request) -> bool:
    return "text/html" in request.headers.get("accept", "")
