from pydantic_settings import BaseSettings, SettingsConfigDict

from app.common.constants import Env


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ENV: Env

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

    # Email sending
    FROM_EMAIL: str
    RESEND_API_KEY: str
    FRONTEND_URL: str
    API_URL: str

    # Fee settings
    CURRENCY: str = "usd"
    SUBSCRIPTION_FEE: float = 5.0
    ARTICLE_FEE: float = 1.0


settings = Settings()
