"""Configuration management for the Python agent."""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Azure OpenAI Configuration
    azure_openai_endpoint: str = ""
    azure_openai_deployment: str = "gpt-4"
    azure_openai_api_version: str = "2024-02-15-preview"
    azure_openai_api_key: str = ""

    # Agent Configuration
    agent_name: str = "PythonSpecializedAgent"
    agent_instructions: str = "You are a specialized Python agent that helps with data analysis, machine learning, and Python ecosystem tasks."

    # API Configuration
    api_port: int = 8000
    api_host: str = "0.0.0.0"
    require_auth: bool = False


settings = Settings()
