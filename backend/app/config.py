import secrets
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "BOS SYAMS API"
    app_env: str = "development"
    secret_key: str = Field(default_factory=lambda: secrets.token_urlsafe(48))
    access_token_minutes: int = Field(default=60, ge=1, le=1440)
    database_url: str = "postgresql+psycopg2://bos:bos@db:5432/bos_syams"
    seed_demo: bool = False
    cors_origins: list[str] = []
    login_max_attempts: int = Field(default=10, ge=1)
    login_window_seconds: int = Field(default=900, ge=60)
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @model_validator(mode="after")
    def secure_configuration(self):
        if self.app_env not in {"development", "testing", "production"}:
            raise ValueError("APP_ENV must be development, testing or production")
        if self.seed_demo and self.app_env != "development":
            raise ValueError("SEED_DEMO is only permitted in development")
        if self.app_env != "production" and not self.secret_key:
            self.secret_key = secrets.token_urlsafe(48)
        if self.app_env == "production":
            weak = ("change", "replace", "ganti", "example", "secret_key")
            if "secret_key" not in self.model_fields_set or len(self.secret_key) < 48 or any(x in self.secret_key.lower() for x in weak):
                raise ValueError("Production requires an explicit random SECRET_KEY of at least 48 characters")
            if "*" in self.cors_origins:
                raise ValueError("Production CORS origins must be explicit")
        return self


settings = Settings()
