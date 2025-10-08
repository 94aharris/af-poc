"""Configuration management for the Python agent."""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Azure OpenAI Configuration
    azure_openai_endpoint: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    azure_openai_deployment: str = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4")
    azure_openai_api_version: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    azure_openai_api_key: str = os.getenv("AZURE_OPENAI_API_KEY", "")

    # Agent Configuration
    agent_name: str = os.getenv("AGENT_NAME", "PythonSpecializedAgent")
    agent_instructions: str = os.getenv(
        "AGENT_INSTRUCTIONS",
        "You are a specialized Python agent that helps with data analysis, machine learning, and Python ecosystem tasks.",
    )

    # API Configuration
    api_port: int = int(os.getenv("API_PORT", "8000"))
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    require_auth: bool = os.getenv("REQUIRE_AUTH", "false").lower() == "true"

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields in .env file


settings = Settings()
