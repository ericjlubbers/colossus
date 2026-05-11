from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # ── App ───────────────────────────────────────────────────────────────────
    app_name: str = "colossus"
    app_version: str = "0.1.0"
    debug: bool = False

    # ── Database ──────────────────────────────────────────────────────────────
    postgres_url: str = "postgresql+asyncpg://colossus:changeme@localhost:5432/colossus"

    # ── Redis ─────────────────────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"

    # ── MinIO ─────────────────────────────────────────────────────────────────
    minio_user: str = "colossus"
    minio_password: str = "changeme"
    minio_endpoint: str = "localhost:9000"
    minio_bucket: str = "colossus"

    # ── JWT ───────────────────────────────────────────────────────────────────
    jwt_secret_key: str = "changeme"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30

    # ── Google OAuth (Phase 6 — Calendar integration) ─────────────────────────
    google_oauth_client_id: str = ""
    google_oauth_client_secret: str = ""


settings = Settings()
