from pydantic import Field
from pydantic_settings import BaseSettings

from datetime import datetime, timedelta, timezone


class Settings(BaseSettings):
    secret_key: str = Field("", alias="SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_lifetime_seconds: int = 3600

    alembic_ini_file: str = "alembic.ini"

    app_name: str = "CRM FastAPI"
    debug: bool = False
    database_driver: str = "postgresql+asyncpg"
    database_url: str = Field("", alias="POSTGRES_URL")
    log_level: str = "DEBUG"

    jwt_login_endpoint: str = "/api/auth/login"

    timezone_info: timezone = timezone.utc

    def datetime_now(self) -> datetime:
        """datetime.now() with predefined timezone_info from settings"""
        return datetime.now(self.timezone_info)

    @property
    def full_database_url(self) -> str:
        return f"{self.database_driver}://{self.database_url}"

    invite_expiration_time: timedelta = Field(
        default=timedelta(days=7),
    )
    max_invite_uses: int = Field(default=1)
    jinja2_templates_path: str = "src/web/templates"
    session_cookie_name: str = "session_cookie"

    custom_error_redirects: dict[str, str] = {"/teams/join": "/teams"}


settings = Settings()
