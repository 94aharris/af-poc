"""Microsoft Agent Framework implementation for orchestrator.

This module implements the core agent functionality using the Microsoft Agent Framework,
with specialized tools for payroll API integration and delegating calculations to the python-agent.
"""

import asyncio
import httpx
from typing import Annotated, Optional, Dict, Any, List
from pydantic import Field
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential, ManagedIdentityCredential, DefaultAzureCredential
from src.config import settings
from src.auth import get_obo_token
import logging

logger = logging.getLogger(__name__)


class AgentFrameworkService:
    """
    Service for managing Microsoft Agent Framework agents in the orchestrator.

    This implementation provides specialized tools for:
    - Payroll API integration (user info, PTO data) with OBO authentication
    - Calculator routing to python-agent for mathematics
    """

    def __init__(self):
        """Initialize the Agent Framework service."""
        self.agent = None
        self.threads: Dict[str, Any] = {}  # conversation_id -> thread mapping
        self.http_client = httpx.AsyncClient(timeout=30.0)
        self._current_user_token: Optional[str] = None  # Store current user token for tool calls
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
        if hasattr(settings, "azure_openai_api_key") and settings.azure_openai_api_key:
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
            client = AzureOpenAIChatClient(
                endpoint=settings.AZURE_OPENAI_ENDPOINT,
                deployment_name=settings.AZURE_OPENAI_DEPLOYMENT,
                api_key=settings.AZURE_OPENAI_API_KEY,
            )

            # Create agent with instructions and tools
            self.agent = client.create_agent(
                name=settings.agent_name,
                instructions=settings.agent_instructions,
                tools=self._get_agent_tools(),
            )

            logger.info("Agent initialized successfully")

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
            self.get_user_info,
            self.get_user_pto,
            self.calculate,
        ]

    # Tool Implementations
    # Following Microsoft Agent Framework best practices:
    # - Use Annotated type hints with Field descriptions
    # - Return strings for LLM consumption
    # - Keep logic simple and deterministic

    async def get_user_info(self) -> str:
        """Get the current user's payroll information from the payroll API.

        This tool retrieves comprehensive user information including:
        - Name, Email, Department
        - Employee ID, Job Title
        - Manager name
        - Hire date

        Requires OBO authentication token to access the payroll API.
        """
        try:
            # Acquire OBO token for payroll API
            payroll_scopes = settings.PAYROLL_API_SCOPES

            logger.debug(f"OBO Token Check - REQUIRE_AUTH: {settings.REQUIRE_AUTH}, "
                        f"Has user token: {self._current_user_token is not None}, "
                        f"Payroll scopes: {payroll_scopes}")

            # Get OBO token from stored user token
            headers = {}
            if settings.REQUIRE_AUTH and self._current_user_token:
                logger.info("Acquiring OBO token for payroll API")
                # Exchange for OBO token for payroll API
                obo_token = await get_obo_token(self._current_user_token, payroll_scopes)
                headers["Authorization"] = f"Bearer {obo_token}"
                logger.debug("OBO token acquired and added to Authorization header")
            else:
                logger.warning("Skipping OBO token - calling API without authentication")

            # Call payroll API
            url = f"{settings.PAYROLL_API_URL}/payroll/user-info"

            logger.info(f"Calling payroll API for user info: {url}")
            response = await self.http_client.get(url, headers=headers)
            response.raise_for_status()

            user_info = response.json()

            # Format for LLM
            return (
                f"User Information:\n"
                f"- Name: {user_info.get('name', 'N/A')}\n"
                f"- Email: {user_info.get('email', 'N/A')}\n"
                f"- Employee ID: {user_info.get('employeeId', 'N/A')}\n"
                f"- Job Title: {user_info.get('jobTitle', 'N/A')}\n"
                f"- Department: {user_info.get('department', 'N/A')}\n"
                f"- Manager: {user_info.get('manager', 'N/A')}\n"
                f"- Hire Date: {user_info.get('hireDate', 'N/A')}"
            )

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling payroll API: {e}")
            return (
                f"Error retrieving user information: {e.response.status_code} - {e.response.text}"
            )
        except Exception as e:
            logger.error(f"Error calling payroll API: {e}")
            return f"Error retrieving user information: {str(e)}"

    async def get_user_pto(self) -> str:
        """Get the current user's PTO (Paid Time Off) balance and history from the payroll API.

        This tool retrieves PTO information including:
        - Current balance in hours
        - Total accrued this year
        - Total used this year
        - Pending requests
        - Maximum carryover allowed
        - List of upcoming PTO requests

        Requires OBO authentication token to access the payroll API.
        """
        try:
            # Acquire OBO token for payroll API
            payroll_scopes = settings.PAYROLL_API_SCOPES

            # Get OBO token from stored user token
            headers = {}
            if settings.REQUIRE_AUTH and self._current_user_token:
                obo_token = await get_obo_token(self._current_user_token, payroll_scopes)
                headers["Authorization"] = f"Bearer {obo_token}"

            # Call payroll API
            url = f"{settings.PAYROLL_API_URL}/payroll/user-pto"

            logger.info(f"Calling payroll API for PTO data: {url}")
            response = await self.http_client.get(url, headers=headers)
            response.raise_for_status()

            pto_data = response.json()

            # Format upcoming PTO
            upcoming_pto_str = ""
            if pto_data.get("upcomingPto"):
                upcoming_pto_str = "\nUpcoming PTO:\n"
                for pto in pto_data["upcomingPto"]:
                    upcoming_pto_str += (
                        f"  - {pto.get('startDate', 'N/A')} to {pto.get('endDate', 'N/A')}: "
                        f"{pto.get('hours', 0)} hours ({pto.get('type', 'N/A')}) - {pto.get('status', 'N/A')}\n"
                    )

            # Format for LLM
            return (
                f"PTO Information:\n"
                f"- Current Balance: {pto_data.get('currentBalanceHours', 0)} hours\n"
                f"- Accrued This Year: {pto_data.get('accruedThisYearHours', 0)} hours\n"
                f"- Used This Year: {pto_data.get('usedThisYearHours', 0)} hours\n"
                f"- Pending Requests: {pto_data.get('pendingRequestsHours', 0)} hours\n"
                f"- Max Carryover: {pto_data.get('maxCarryoverHours', 0)} hours"
                f"{upcoming_pto_str}"
            )

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling payroll API: {e}")
            return f"Error retrieving PTO information: {e.response.status_code} - {e.response.text}"
        except Exception as e:
            logger.error(f"Error calling payroll API: {e}")
            return f"Error retrieving PTO information: {str(e)}"

    async def calculate(
        self,
        expression: Annotated[
            str, Field(description="Mathematical expression or calculation question to evaluate")
        ],
    ) -> str:
        """Delegate mathematical calculations to the specialized Python agent.

        This tool routes mathematics-related questions to the python-agent service,
        which has specialized capabilities for:
        - Mathematical calculations
        - Data analysis
        - Statistical operations

        The python-agent will process the calculation and return the result.
        """
        try:
            # Get OBO token for python agent if auth is enabled
            headers = {"Content-Type": "application/json"}
            if settings.REQUIRE_AUTH and self._current_user_token:
                obo_token = await get_obo_token(
                    self._current_user_token, settings.PYTHON_AGENT_SCOPES
                )
                headers["Authorization"] = f"Bearer {obo_token}"

            # Call python-agent
            url = f"{settings.PYTHON_AGENT_URL}/agent"

            payload = {
                "message": f"Please calculate: {expression}",
                "conversation_id": None,
                "metadata": {},
            }

            logger.info(f"Routing calculation to python-agent: {url}")
            response = await self.http_client.post(url, json=payload, headers=headers)
            response.raise_for_status()

            result = response.json()

            # Return the agent's response
            return (
                f"Calculation result: {result.get('message', 'No response from calculator agent')}"
            )

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling python-agent: {e}")
            return f"Error performing calculation: {e.response.status_code} - {e.response.text}"
        except Exception as e:
            logger.error(f"Error calling python-agent: {e}")
            return f"Error performing calculation: {str(e)}"

    async def run_agent(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        user_token: Optional[str] = None,
    ) -> str:
        """
        Run the agent with a message.

        Args:
            message: The user's message
            conversation_id: Optional conversation ID for maintaining context
            user_token: Optional user token for OBO authentication

        Returns:
            The agent's response text
        """
        if not self.agent:
            return "Agent not initialized. Please check Azure OpenAI configuration."

        try:
            # Store the user token for tool calls
            self._current_user_token = user_token

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
        finally:
            # Clear the user token after execution
            self._current_user_token = None

    async def run_agent_stream(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        user_token: Optional[str] = None,
    ):
        """
        Run the agent with streaming responses.

        Args:
            message: The user's message
            conversation_id: Optional conversation ID for maintaining context
            user_token: Optional user token for OBO authentication

        Yields:
            Streaming updates from the agent
        """
        if not self.agent:
            yield {"error": "Agent not initialized. Please check Azure OpenAI configuration."}
            return

        try:
            # Store the user token for tool calls
            self._current_user_token = user_token

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
        finally:
            # Clear the user token after execution
            self._current_user_token = None

    async def close(self):
        """Clean up resources."""
        await self.http_client.aclose()


# Global agent service instance
agent_framework_service = AgentFrameworkService()
