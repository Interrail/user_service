import secrets
from typing import List, Union, Optional, Dict, Any

from pydantic import BaseSettings, AnyHttpUrl, validator, HttpUrl, PostgresDsn, EmailStr


class Settings(BaseSettings):
    API_V1_STR: str = '/api/v1'
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    SERVER_NAME: str = "user_service"
    SERVER_HOST: AnyHttpUrl = 'http://localhost'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str = "user_service"
    SENTRY_DSN: Optional[
        HttpUrl] = "https://stackoverflow.com/questions/417142/what-is-the-maximum-length-of-a-url-in-different-browsers"

    @validator("SENTRY_DSN", pre=True)
    def sentry_dsn_can_be_blank(cls, v: str) -> Optional[str]:
        if len(v) == 0:
            return None
        return v

    POSTGRES_SERVER: str = ""
    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = 587
    SMTP_HOST: Optional[str] = 'smtp.gmail.com'
    SMTP_USER: Optional[str] = 'izzattilla706@gmail.com'
    SMTP_PASSWORD: Optional[str] = 'qyppvtappbugemjh'
    EMAILS_FROM_EMAIL: Optional[EmailStr] = 'izzattilla706@gmail.com'
    EMAILS_FROM_NAME: Optional[str] = None

    @validator("EMAILS_FROM_NAME")
    def get_project_name(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if not v:
            return values["PROJECT_NAME"]
        return v

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_TEMPLATES_DIR: str = "app/email-templates/build"
    EMAILS_ENABLED: bool = False

    @validator("EMAILS_ENABLED", pre=True)
    def get_emails_enabled(cls, v: bool, values: Dict[str, Any]) -> bool:
        return bool(
            values.get("SMTP_HOST")
            and values.get("SMTP_PORT")
            and values.get("EMAILS_FROM_EMAIL")
        )

    EMAIL_TEST_USER: EmailStr = "test@example.com"  # type: ignore
    FIRST_SUPERUSER: EmailStr = "superuser@example.com"  # type: ignore
    FIRST_SUPERUSER_PASSWORD: str = "12345"
    USERS_OPEN_REGISTRATION: bool = True

    class Config:
        env_file = '.env'
        case_sensitive = True


settings = Settings()
