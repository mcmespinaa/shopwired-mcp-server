"""Configuration management using pydantic-settings."""

from __future__ import annotations

import sys
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


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
    # Use SecretStr for safer handling and make fields required
    api_key: SecretStr
    api_secret: SecretStr
    # API base URL
    api_base_url: str = "https://api.ecommerceapi.uk/v1"

    # Rate limiting (leaky bucket)
    rate_limit_burst: int = 40
    rate_limit_rate: float = 2.0  # requests per second

    # HTTP client settings
    request_timeout: float = 30.0
    max_retries: int = 3
    max_response_size: int = 10_000_000  # bytes
    max_connections: int = 20
    max_keepalive_connections: int = 10

    # Circuit breaker
    circuit_breaker_threshold: int = 5   # consecutive failures to open circuit
    circuit_breaker_timeout: float = 30.0  # seconds before half-open probe

    # Response cache
    cache_ttl: float = 120.0  # seconds

    def validate_credentials(self) -> bool:
        """Check that API credentials are configured."""
        # SecretStr fields will raise if they are missing, but we still
        # provide a human-friendly check and message before the server starts.
        key = self.api_key.get_secret_value() if self.api_key else ""
        secret = self.api_secret.get_secret_value() if self.api_secret else ""
        if not key or not secret:
            print(
                "ERROR: SHOPWIRED_API_KEY and SHOPWIRED_API_SECRET must be set.\n"
                "Copy .env.example to .env and fill in your credentials.",
                file=sys.stderr,
            )
            return False
        return True


# Singleton — import this from other modules
settings = Settings()
