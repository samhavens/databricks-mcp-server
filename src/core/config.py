"""
Configuration settings for the Databricks MCP server.
"""

import os
from typing import Any, Dict, Optional

# Import dotenv first to ensure env vars/.env take priority
try:
    from dotenv import load_dotenv
    # Load .env file if it exists
    load_dotenv()
    print("Successfully loaded dotenv")
except ImportError:
    print("WARNING: python-dotenv not found, environment variables must be set manually")

# Use Databricks SDK configuration as fallback only if env vars not set
def get_databricks_defaults():
    host_from_env = os.environ.get("DATABRICKS_HOST")
    token_from_env = os.environ.get("DATABRICKS_TOKEN") 
    
    if host_from_env and token_from_env:
        print(f"Using environment configuration: {host_from_env}")
        return host_from_env, token_from_env
    
    # Try SDK config as fallback
    try:
        from databricks.sdk.core import Config as DatabricksConfig
        databricks_config = DatabricksConfig()
        sdk_host = databricks_config.host or "https://example.databricks.net"
        print(f"Falling back to Databricks CLI configuration: {sdk_host}")
        return sdk_host, "from_databricks_cli"
    except Exception as e:
        print(f"Could not load Databricks CLI config: {e}")
        return "https://example.databricks.net", "dapi_token_placeholder"

DATABRICKS_HOST_DEFAULT, DATABRICKS_TOKEN_DEFAULT = get_databricks_defaults()

from pydantic import field_validator
from pydantic_settings import BaseSettings

# Version
VERSION = "0.1.0"


class Settings(BaseSettings):
    """Base settings for the application."""

    # Databricks API configuration
    DATABRICKS_HOST: str = os.environ.get("DATABRICKS_HOST", DATABRICKS_HOST_DEFAULT)
    DATABRICKS_TOKEN: str = os.environ.get("DATABRICKS_TOKEN", DATABRICKS_TOKEN_DEFAULT)

    # Server configuration
    SERVER_HOST: str = os.environ.get("SERVER_HOST", "0.0.0.0") 
    SERVER_PORT: int = int(os.environ.get("SERVER_PORT", "8000"))
    DEBUG: bool = os.environ.get("DEBUG", "False").lower() == "true"

    # Logging
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")
    
    # Version
    VERSION: str = VERSION

    @field_validator("DATABRICKS_HOST")
    def validate_databricks_host(cls, v: str) -> str:
        """Validate Databricks host URL."""
        if not v.startswith(("https://", "http://")):
            raise ValueError("DATABRICKS_HOST must start with http:// or https://")
        return v

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables to prevent validation errors


# Create global settings instance
settings = Settings()


def get_api_headers() -> Dict[str, str]:
    """Get headers for Databricks API requests."""
    # Use env var/settings token first (PAT), fall back to SDK token (JWT)
    token = settings.DATABRICKS_TOKEN
    
    # Only use SDK token if we don't have a real token from env/settings
    if token in ("dapi_token_placeholder", "from_databricks_cli"):
        try:
            from databricks.sdk.core import Config as DatabricksConfig
            config = DatabricksConfig()
            if config.token:
                token = config.token
        except Exception:
            pass
    
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def get_databricks_api_url(endpoint: str) -> str:
    """
    Construct the full Databricks API URL.
    
    Args:
        endpoint: The API endpoint path, e.g., "/api/2.0/clusters/list"
    
    Returns:
        Full URL to the Databricks API endpoint
    """
    # Ensure endpoint starts with a slash
    if not endpoint.startswith("/"):
        endpoint = f"/{endpoint}"

    # Remove trailing slash from host if present
    host = settings.DATABRICKS_HOST.rstrip("/")
    
    return f"{host}{endpoint}" 