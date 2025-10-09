"""Microsoft Agent Framework implementation following best practices.

This module implements the core agent functionality using the Microsoft Agent Framework,
replacing the previous Claude Code shell integration approach.
"""

import asyncio
from typing import Annotated, Optional, Dict, Any, List
from pydantic import Field
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential, ManagedIdentityCredential, DefaultAzureCredential
from src.config import settings
import logging

logger = logging.getLogger(__name__)


class AgentFrameworkService:
    """
    Service for managing Microsoft Agent Framework agents.

    This implementation follows the best practices from the Microsoft Agent Framework:
    - Uses Azure OpenAI for production-grade LLM access
    - Implements thread-based state management for conversations
    - Provides function tools for external capabilities
    - Supports multiple authentication mechanisms
    """

    def __init__(self):
        """Initialize the Agent Framework service."""
        self.agent = None
        self.threads: Dict[str, Any] = {}  # conversation_id -> thread mapping
        self._initialize_agent()

    def _get_credential(self):
        """
        Get appropriate Azure credential based on environment.

        Priority:
        1. API Key if provided (simplest for development)
        2. AzureCliCredential for local development (after `az login`)
        3. ManagedIdentityCredential for Azure deployments
        4. DefaultAzureCredential as fallback
        """
        # If API key is provided, return None (will use api_key parameter instead)
        if settings.azure_openai_api_key:
            logger.info("Using API key authentication")
            return None

        try:
            # Try Azure CLI credential first (best for local dev)
            credential = AzureCliCredential()
            logger.info("Using AzureCliCredential for authentication")
            return credential
        except Exception as e:
            logger.warning(f"AzureCliCredential failed: {e}, trying DefaultAzureCredential")
            # Fallback to default credential chain
            return DefaultAzureCredential()

    def _initialize_agent(self):
        """Initialize the Azure OpenAI agent with tools."""
        try:
            if not settings.azure_openai_endpoint:
                logger.warning("Azure OpenAI endpoint not configured. Agent will not be available.")
                return

            # Create Azure OpenAI client with authentication
            credential = self._get_credential()

            # Build client parameters
            client_params = {
                "endpoint": settings.azure_openai_endpoint,
                "deployment_name": settings.azure_openai_deployment,
            }

            # Use API key if provided, otherwise use credential
            if settings.azure_openai_api_key:
                client_params["api_key"] = settings.azure_openai_api_key
            else:
                client_params["credential"] = credential

            client = AzureOpenAIChatClient(**client_params)

            # Create agent with instructions and tools
            self.agent = client.create_agent(
                name=settings.agent_name,
                instructions=settings.agent_instructions,
                tools=self._get_agent_tools(),
            )

            logger.info(f"Agent '{settings.agent_name}' initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            self.agent = None

    def _get_agent_tools(self):
        """
        Get the list of tools available to the agent.

        Following best practices:
        - Use type hints for automatic schema generation
        - Provide clear descriptions for LLM understanding
        - Keep tools focused and single-purpose
        """
        return [
            self.get_weather,
            self.calculate,
            self.search_files,
        ]

    # Tool Implementations
    # Following Microsoft Agent Framework best practices:
    # - Use Annotated type hints with Field descriptions
    # - Return strings for LLM consumption
    # - Keep logic simple and deterministic

    def get_weather(
        self,
        location: Annotated[str, Field(description="The city or location to get weather for")],
    ) -> str:
        """Get the current weather for a given location.

        Note: This is a demo implementation. In production, integrate with a real weather API.
        """
        # Demo implementation - in production, call a real weather API
        return f"The weather in {location} is partly cloudy with a temperature of 18°C (64°F). Light winds from the northwest."

    def calculate(
        self,
        expression: Annotated[str, Field(description="Mathematical expression to evaluate (e.g., '2 + 2', '10 * 5')")],
    ) -> str:
        """Evaluate a mathematical expression and return the result.

        Supports basic arithmetic operations: +, -, *, /, **, (), etc.
        """
        try:
            # Use eval safely for simple math expressions
            # In production, use a proper math expression parser
            result = eval(expression, {"__builtins__": {}}, {})
            return f"The result of {expression} is {result}"
        except Exception as e:
            return f"Error evaluating expression '{expression}': {str(e)}"

    def search_files(
        self,
        pattern: Annotated[str, Field(description="File name pattern to search for (e.g., '*.py', 'README.md')")],
        directory: Annotated[str, Field(description="Directory to search in")] = ".",
    ) -> str:
        """Search for files matching a pattern in a directory.

        Note: This is a demo implementation. In production, implement proper file search.
        """
        # Demo implementation
        return f"Searching for files matching '{pattern}' in directory '{directory}'. This is a demo - implement real file search in production."

    async def run_agent(
        self,
        message: str,
        conversation_id: Optional[str] = None,
    ) -> str:
        """
        Run the agent with a message.

        Args:
            message: The user's message
            conversation_id: Optional conversation ID for maintaining context

        Returns:
            The agent's response text
        """
        if not self.agent:
            return "Agent not initialized. Please check Azure OpenAI configuration."

        try:
            # Get or create thread for conversation continuity
            thread = None
            if conversation_id:
                if conversation_id in self.threads:
                    thread = self.threads[conversation_id]
                else:
                    thread = self.agent.get_new_thread()
                    self.threads[conversation_id] = thread

            # Run the agent
            result = await self.agent.run(message, thread=thread)

            return result.text

        except Exception as e:
            logger.error(f"Error running agent: {e}")
            return f"Error processing request: {str(e)}"

    async def run_agent_stream(
        self,
        message: str,
        conversation_id: Optional[str] = None,
    ):
        """
        Run the agent with streaming responses.

        Args:
            message: The user's message
            conversation_id: Optional conversation ID for maintaining context

        Yields:
            Streaming updates from the agent
        """
        if not self.agent:
            yield {"error": "Agent not initialized. Please check Azure OpenAI configuration."}
            return

        try:
            # Get or create thread for conversation continuity
            thread = None
            if conversation_id:
                if conversation_id in self.threads:
                    thread = self.threads[conversation_id]
                else:
                    thread = self.agent.get_new_thread()
                    self.threads[conversation_id] = thread

            # Stream agent responses
            async for update in self.agent.run_stream(message, thread=thread):
                if update.text:
                    yield {"delta": update.text}

        except Exception as e:
            logger.error(f"Error streaming agent response: {e}")
            yield {"error": f"Error processing request: {str(e)}"}


# Global agent service instance
agent_framework_service = AgentFrameworkService()
