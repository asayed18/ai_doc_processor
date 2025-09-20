"""
Configuration settings for the AI Document Processor application.
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from pydantic import BaseModel


class Settings(BaseModel):
    """Application settings."""

    # Application
    app_name: str = "AI Document Processor"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True

    # Database
    database_url: str = "sqlite:///./documents.db"

    # CORS
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    # API Keys
    anthropic_api_key: str = ""

    # File Storage
    upload_directory: str = "uploads"
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    allowed_file_types: List[str] = [".pdf"]

    # Claude Configuration
    claude_model: str = "claude-3-5-sonnet-20241022"
    claude_max_tokens: int = 4000

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Load from dev.env first (try both current dir and parent dir), then .env as fallback

        load_dotenv()  # This will load .env if it exists
        # Load from environment variables
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./documents.db")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")

        if not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"

    @property
    def cors_origins(self) -> List[str]:
        """Get CORS origins based on environment."""
        if self.is_production:
            # In production, filter out localhost origins
            return [
                origin
                for origin in self.allowed_origins
                if "localhost" not in origin and "127.0.0.1" not in origin
            ]
        return self.allowed_origins + ["*"]  # Allow all in development


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
