from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "BOS SYAMS API"
    secret_key: str = "change-this-in-production"
    access_token_minutes: int = 720
    database_url: str = "postgresql+psycopg2://bos:bos@db:5432/bos_syams"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
