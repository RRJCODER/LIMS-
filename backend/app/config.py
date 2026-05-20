from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://lims:limsdev@localhost/olive_lims"
    SYNC_DATABASE_URL: str = "postgresql+psycopg2://lims:limsdev@localhost/olive_lims"
    REDIS_URL: str = "redis://localhost:6379"

    SECRET_KEY: str = "changeme"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    MEDIA_ROOT: str = "/app/media"
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    ENVIRONMENT: str = "development"

    # Lab profile defaults (overridable via Settings UI)
    LAB_NAME: str = "Laboratorio de Análisis de Aceite de Oliva"
    LAB_ACCREDITATION_NUMBER: str = ""

    # Email (optional)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@olivelims.local"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]


settings = Settings()
