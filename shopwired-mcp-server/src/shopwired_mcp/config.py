"""Configuration management using pydantic-settings."""

from __future__ import annotations

import sys
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """ShopWired MCP Server configuration.

    Values are loaded from environment variables or a .env file.
    """

    model_config = SettingsConfigDict(
        env_prefix="SHOPWIRED_",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # Required — ShopWired API credentials
    api_key: str = ""
    api_secret: str = ""

    # API base URL
    api_base_url: str = "https://api.ecommerceapi.uk/v1"

    # Rate limiting (leaky bucket)
    rate_limit_burst: int = 40
    rate_limit_rate: float = 2.0  # requests per second

    # HTTP client settings
    request_timeout: float = 30.0
    max_retries: int = 3

    def validate_credentials(self) -> bool:
        """Check that API credentials are configured."""
        if not self.api_key or not self.api_secret:
            print(
                "ERROR: SHOPWIRED_API_KEY and SHOPWIRED_API_SECRET must be set.\n"
                "Copy .env.example to .env and fill in your credentials.",
                file=sys.stderr,
            )
            return False
        return True


# Singleton — import this from other modules
settings = Settings()
