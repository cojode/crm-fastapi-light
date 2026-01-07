from src.web.utils import get_custom_endpoint_handler

from src.web.api.users.views import (
    pages_login_router,
    pages_register_router,
    pages_get_user_router,
)


def get_pages_login_handler():
    return get_custom_endpoint_handler(
        target_router=pages_login_router, path="/login", methods={"POST"}
    )


def get_pages_logout_handler():
    return get_custom_endpoint_handler(
        target_router=pages_login_router, path="/logout", methods={"POST"}
    )


def get_pages_register_handler():
    return get_custom_endpoint_handler(
        target_router=pages_register_router, path="/register", methods={"POST"}
    )


def get_pages_get_me_handler():
    return get_custom_endpoint_handler(
        target_router=pages_get_user_router, path="/me", methods={"GET"}
    )


def get_pages_update_me_handler():
    return get_custom_endpoint_handler(
        target_router=pages_get_user_router, path="/me", methods={"PATCH"}
    )
