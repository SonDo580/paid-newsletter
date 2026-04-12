from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ADMIN_EMAIL: str
    DB_PATH: str = "newsletter.db"

    @property
    def DB_URL(self) -> str:
        return f"sqlite:///{self.DB_PATH}"


settings = Settings()
