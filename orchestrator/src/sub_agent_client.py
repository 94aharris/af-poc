"""Client for calling sub-agent services."""

import httpx
from typing import Optional, Dict, Any
from src.models import AgentType, SubAgentResponse
from src.config import settings
import logging

logger = logging.getLogger(__name__)


class SubAgentClient:
    """Handles communication with sub-agent services."""

    def __init__(self):
        self.timeout = httpx.Timeout(30.0)

    def _get_agent_url(self, agent_type: AgentType) -> str:
        """Get the URL for a specific agent."""
        if agent_type == AgentType.PYTHON:
            return settings.PYTHON_AGENT_URL
        elif agent_type == AgentType.DOTNET:
            return settings.DOTNET_AGENT_URL
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")

    async def call_sub_agent(
        self,
        agent_type: AgentType,
        message: str,
        obo_token: Optional[str] = None,
        conversation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SubAgentResponse:
        """
        Call a sub-agent with the OBO token.

        This demonstrates the critical OBO flow:
        1. Orchestrator has already exchanged user JWT for OBO token
        2. Orchestrator calls sub-agent with OBO token in Authorization header
        3. Sub-agent validates OBO token and processes request with user context

        Args:
            agent_type: Which sub-agent to call
            message: User's message
            obo_token: OBO token for authentication (if auth enabled)
            conversation_id: Optional conversation ID
            metadata: Additional metadata

        Returns:
            SubAgentResponse from the called agent
        """
        url = self._get_agent_url(agent_type)
        endpoint = f"{url}/agent"

        # Prepare request payload
        payload = {
            "message": message,
            "conversation_id": conversation_id,
            "metadata": metadata or {},
        }

        # Prepare headers
        headers = {"Content-Type": "application/json"}

        # Extract request ID from metadata for tracing
        request_id = metadata.get("request_id", "unknown") if metadata else "unknown"

        if obo_token and settings.REQUIRE_AUTH:
            # Pass OBO token to sub-agent
            headers["Authorization"] = f"Bearer {obo_token}"
            logger.info(f"[{request_id}] [ORCHESTRATOR→{agent_type.value.upper()}] Calling with OBO token")
        else:
            logger.info(f"[{request_id}] [ORCHESTRATOR→{agent_type.value.upper()}] Calling without auth (testing mode)")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(endpoint, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()

                logger.info(f"[{request_id}] [{agent_type.value.upper()}→ORCHESTRATOR] Response received successfully")

                return SubAgentResponse(
                    agent_type=agent_type.value,
                    message=data.get("message", ""),
                    status=data.get("status", "unknown"),
                    metadata=data.get("metadata", {}),
                )

        except httpx.HTTPStatusError as e:
            logger.error(f"Sub-agent {agent_type.value} returned error: {e.response.status_code}")
            return SubAgentResponse(
                agent_type=agent_type.value,
                message=f"Error calling {agent_type.value} agent: {e.response.status_code}",
                status="error",
                metadata={"error": str(e)},
            )

        except httpx.RequestError as e:
            logger.error(f"Failed to reach sub-agent {agent_type.value}: {str(e)}")
            return SubAgentResponse(
                agent_type=agent_type.value,
                message=f"Failed to reach {agent_type.value} agent: {str(e)}",
                status="error",
                metadata={"error": str(e)},
            )

    async def health_check(self, agent_type: AgentType) -> bool:
        """Check if a sub-agent is healthy and reachable."""
        try:
            url = self._get_agent_url(agent_type)
            async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
                response = await client.get(f"{url}/health")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed for {agent_type.value}: {str(e)}")
            return False
