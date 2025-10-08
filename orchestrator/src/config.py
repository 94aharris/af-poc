"""Configuration management for orchestrator service."""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application configuration."""

    # Azure AD Configuration
    AZURE_TENANT_ID: str = ""
    AZURE_CLIENT_ID: str = ""
    AZURE_CLIENT_SECRET: str = ""

    # JWT Configuration
    JWT_ALGORITHM: str = "RS256"
    JWT_AUDIENCE: str = ""  # Your API's App ID URI
    JWT_ISSUER: str = ""  # Azure AD issuer URL

    # Sub-Agent Endpoints
    PYTHON_AGENT_URL: str = "http://localhost:8000"
    DOTNET_AGENT_URL: str = "http://localhost:5000"

    # OBO Scopes for sub-agents
    PYTHON_AGENT_SCOPES: List[str] = ["api://python-agent/.default"]
    DOTNET_AGENT_SCOPES: List[str] = ["api://dotnet-agent/.default"]

    # API Configuration
    API_PORT: int = 8001  # Orchestrator port
    API_HOST: str = "0.0.0.0"

    # Enable/Disable Authentication (for testing)
    REQUIRE_AUTH: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
