"""Application configuration management using pydantic-settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="allow")

    # Application
    APP_NAME: str = "Document Intelligence"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    # API
    API_PREFIX: str = "/api/v1"
    API_KEY: str = Field(..., description="API key for authentication")
    CORS_ORIGINS: list[str] = Field(default_factory=lambda: ["*"])

    # Database
    DATABASE_URL: str = Field(..., description="PostgreSQL connection URL")
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Storage (S3/MinIO)
    STORAGE_TYPE: Literal["s3", "local"] = "s3"
    S3_ENDPOINT_URL: str | None = None
    S3_ACCESS_KEY: str | None = None
    S3_SECRET_KEY: str | None = None
    S3_BUCKET_NAME: str = "documents"
    S3_REGION: str = "us-east-1"
    LOCAL_STORAGE_PATH: str = "./storage"

    # AI Models
    ANTHROPIC_API_KEY: str = Field(..., description="Anthropic API key for Claude")
    OPENAI_API_KEY: str | None = None

    DEFAULT_EXTRACTION_MODEL: str = "claude-sonnet-4-20250514"
    FALLBACK_EXTRACTION_MODEL: str = "gpt-4o"

    # Processing
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_MIME_TYPES: list[str] = Field(
        default_factory=lambda: [
            "application/pdf",
            "image/jpeg",
            "image/png",
            "image/webp",
            "image/tiff",
        ]
    )
    MAX_PAGES_PER_DOCUMENT: int = 100
    EXTRACTION_TIMEOUT_SECONDS: int = 120
    PDF_DPI: int = 200
    IMAGE_MAX_DIMENSION: int = 2000

    # Queue
    WORKER_CONCURRENCY: int = 10
    JOB_TIMEOUT: int = 300

    # Webhooks
    WEBHOOK_TIMEOUT_SECONDS: int = 30
    WEBHOOK_MAX_RETRIES: int = 3

    @field_validator("MAX_FILE_SIZE_MB")
    @classmethod
    def validate_max_file_size(cls, v: int) -> int:
        """Ensure max file size is reasonable."""
        if v > 100:
            raise ValueError("MAX_FILE_SIZE_MB cannot exceed 100MB")
        return v

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            import json

            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("ALLOWED_MIME_TYPES", mode="before")
    @classmethod
    def parse_allowed_mime_types(cls, v: str | list[str]) -> list[str]:
        """Parse allowed MIME types from string or list."""
        if isinstance(v, str):
            import json

            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [mime.strip() for mime in v.split(",")]
        return v

    @property
    def max_file_size_bytes(self) -> int:
        """Get max file size in bytes."""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
