"""Configuration management for orchestrator service."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="allow"
    )

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
    PAYROLL_API_URL: str = "http://localhost:5100"

    # OBO Scopes for sub-agents
    # Use 'access_as_user' for delegated permissions (preserves user identity)
    # These should match the API scopes exposed by each service
    PYTHON_AGENT_SCOPES: List[str] = ["api://python-agent/access_as_user"]
    DOTNET_AGENT_SCOPES: List[str] = ["api://dotnet-agent/access_as_user"]
    PAYROLL_API_SCOPES: List[str] = ["api://payroll-api/access_as_user"]

    # API Configuration
    API_PORT: int = 8001  # Orchestrator port
    API_HOST: str = "0.0.0.0"

    # Enable/Disable Authentication (for testing)
    REQUIRE_AUTH: bool = False

    # Enable Claude Code intelligent routing for orchestrator
    # Requires Claude CLI to be installed: https://claude.com/claude-code
    ENABLE_INTELLIGENT_ROUTING: bool = False

    # Azure OpenAI Configuration (for Microsoft Agent Framework)
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_DEPLOYMENT: str = ""
    AZURE_OPENAI_API_KEY: str = ""

    # Agent Configuration
    agent_name: str = "OrchestratorAgent"
    agent_instructions: str = (
        "You are an intelligent orchestrator agent that helps users with payroll information and calculations. "
        "Use the get_user_info tool to retrieve user information from the payroll system. "
        "Use the get_user_pto tool to get PTO (Paid Time Off) balance and history. "
        "Use the calculate tool for mathematical calculations and data analysis. "
        "Always provide clear and helpful responses."
    )


settings = Settings()
