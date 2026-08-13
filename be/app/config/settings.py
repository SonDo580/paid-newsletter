from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

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
    API_URL: str

    # Auth
    ADMIN_EMAIL: str
    MAGIC_TOKEN_SECRET_KEY: str
    MAGIC_TOKEN_EXPIRES_MINUTES: int = 15
    ACCESS_TOKEN_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRES_DAYS: int = 30

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


settings = Settings()
