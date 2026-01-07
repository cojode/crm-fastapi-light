from fastapi import APIRouter, Request, Depends, Form, Response
from src.services.users.user_manager import get_user_manager
from src.web.dependency import get_delete_me_use_case
from src.web.api.dependency import (
    get_pages_get_me_handler,
    get_pages_update_me_handler,
)
from src.services.users.dependency import current_active_verified_user_pages

from src.web.pages.utils import (
    auto_templated_response,
    auto_redirect_response,
    attempt_response_with_pages_errors,
    FragileSession,
)
from src.web.api.users.schemas import UserUpdate

from fastapi_csrf_protect import CsrfProtect

from pydantic import EmailStr

router = APIRouter()


@router.get("/profile")
async def view_profile(
    request: Request,
    profile_handler=Depends(get_pages_get_me_handler),
    current_user=Depends(current_active_verified_user_pages),
    csrf_protect: CsrfProtect = Depends(),
):
    profile_response = await profile_handler(user=current_user)
    return auto_templated_response(
        request,
        "user/profile.html",
        csrf_protect,
        current_user=profile_response,
    )


async def get_user_update_from_form(
    email: EmailStr = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
) -> UserUpdate:
    return UserUpdate(email=email, first_name=first_name, last_name=last_name)


@router.post("/profile")
async def edit_profile(
    request: Request,
    response: Response,
    user_update: UserUpdate = Depends(get_user_update_from_form),
    update_handler=Depends(get_pages_update_me_handler),
    user=Depends(current_active_verified_user_pages),
    user_manager=Depends(get_user_manager),
    csrf_protect: CsrfProtect = Depends(),
):
    await attempt_response_with_pages_errors(
        update_handler(
            request=request,
            user_update=user_update,
            user=user,
            user_manager=user_manager,
        ),
        "/profile",
        "Profile update error",
    )
    FragileSession(request).message = "Profile update success"
    return auto_redirect_response(response, "/profile")


@router.post("/profile/delete")
async def delete_profile(
    request: Request,
    response: Response,
    user=Depends(current_active_verified_user_pages),
    use_case=Depends(get_delete_me_use_case),
):
    await attempt_response_with_pages_errors(
        use_case.execute(user.id), "/profile", "Can not delete profile"
    )
    FragileSession(request).message = "Account successfully deleted"
    return auto_redirect_response(response, "/login")
