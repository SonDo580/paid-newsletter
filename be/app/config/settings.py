from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

from app.common.constants import Env


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ENV: Env
    ALLOWED_ORIGINS: list[str]
    FRONTEND_URL: str
    BACKEND_URL: str
    API_PREFIX: str = "/api"
    STATIC_PREFIX: str = "/static"

    @property
    def API_URL(self) -> str:
        base = self.BACKEND_URL.rstrip("/")
        prefix = self.API_PREFIX.strip("/")
        return f"{base}/{prefix}"

    @property
    def STATIC_URL(self) -> str:
        base = self.BACKEND_URL.rstrip("/")
        prefix = self.STATIC_PREFIX.strip("/")
        return f"{base}/{prefix}"

    # Auth
    ADMIN_EMAIL: str
    MAGIC_TOKEN_SECRET_KEY: str
    MAGIC_TOKEN_EXPIRES_MINUTES: int = 15
    ACCESS_TOKEN_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRES_DAYS: int = 30
    OAUTH_STATE_SECRET_KEY: str
    OAUTH_STATE_EXPIRES_MINUTES: int = 10

    # DB
    DB_PATH: str = "newsletter.db"

    @property
    def DB_URL(self) -> str:
        return f"sqlite:///{self.DB_PATH}"

    # Redis
    REDIS_URL: str

    # Email sending
    FROM_EMAIL: str
    RESEND_API_KEY: str
    MAX_RECIPIENTS: int = 100  # Resend's constraint

    # Fee settings
    CURRENCY: str = "usd"
    ARTICLE_FEE_CENTS: int = 100

    # Stripe
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    STRIPE_SUBSCRIPTION_PRICE_ID: str

    # Google
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

    # File storage
    UPLOAD_DIR: Path  # use absolute path


settings = Settings()
