from fastapi import (
    APIRouter,
    Request,
    Depends,
    Form,
    Response,
)
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from src.web.api.users.schemas import UserCreate

from src.services.users.user_manager import get_user_manager
from src.services.users.dependency import (
    get_jwt_strategy,
)
from src.web.api.dependency import (
    get_pages_register_handler,
    get_pages_login_handler,
    get_pages_logout_handler,
)
from fastapi_csrf_protect import CsrfProtect
from src.web.api.users.views import pages_current_user_token

from pydantic import EmailStr

from src.web.pages.utils import (
    auto_templated_response,
    auto_redirect_response,
    attempt_response_with_pages_errors,
    set_cookie_as_requested,
    FragileSession,
)


router = APIRouter(tags=["auth pages"], default_response_class=HTMLResponse)


@router.get("/register")
async def register_page(
    request: Request,
    csrf_protect: CsrfProtect = Depends(),
):
    return auto_templated_response(
        request,
        "auth/register.html",
        csrf_protect,
    )


async def get_user_create_from_form(
    email: EmailStr = Form(...),
    password: str = Form(...),
) -> UserCreate:
    return UserCreate(email=email, password=password)


@router.post("/register")
async def register_submit(
    request: Request,
    response: Response,
    user_create: UserCreate = Depends(get_user_create_from_form),
    register_handler=Depends(get_pages_register_handler),
    user_manager=Depends(get_user_manager),
):
    await attempt_response_with_pages_errors(
        register_handler(request, user_create, user_manager),
        "/register",
        "Registration failed",
    )

    FragileSession(request).message = "Succesfull registration"

    return auto_redirect_response(response, "/login")


@router.get("/login")
async def login_page(request: Request, csrf_protect: CsrfProtect = Depends()):
    return auto_templated_response(
        request,
        "auth/login.html",
        csrf_protect,
    )


async def get_credentials_from_form(
    email: str = Form(...),
    password: str = Form(...),
) -> OAuth2PasswordRequestForm:
    return OAuth2PasswordRequestForm(username=email, password=password)


@router.post("/login")
async def login_submit(
    request: Request,
    response: Response,
    credentials: OAuth2PasswordRequestForm = Depends(get_credentials_from_form),
    login_handler=Depends(get_pages_login_handler),
    user_manager=Depends(get_user_manager),
    strategy=Depends(get_jwt_strategy),
):
    login_response: Response = await attempt_response_with_pages_errors(
        login_handler(request, credentials, user_manager, strategy),
        "/login",
        "Login failed",
    )
    set_cookie_as_requested(login_response, response)
    return auto_redirect_response(response, "/")


@router.get("/logout")
async def logout_action(
    request: Request,
    response: Response,
    logout_handler=Depends(get_pages_logout_handler),
    current_user_token=Depends(pages_current_user_token),
    strategy=Depends(get_jwt_strategy),
):
    logout_response: Response = await attempt_response_with_pages_errors(
        logout_handler(current_user_token, strategy),
        redirect_path="/profile",
        unexpected_error_message="Logout error",
    )
    set_cookie_as_requested(logout_response, response)
    return auto_redirect_response(response, "/login")
