from fastapi import APIRouter, status

router = APIRouter()


@router.get("/health/", status_code=status.HTTP_200_OK)
def health_check() -> dict[str, str]:
    """
    Checks the health of a service.

    It returns 200 if the service is healthy.
    """
    return {}
