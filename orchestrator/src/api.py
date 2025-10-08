"""API endpoints for the orchestrator service."""

from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi.security import HTTPAuthorizationCredentials
from src.models import OrchestratorRequest, OrchestratorResponse, TokenInfo
from src.auth import get_current_user, get_obo_token, security
from src.agent_selector import AgentSelector
from src.sub_agent_client import SubAgentClient
from src.config import settings
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

agent_selector = AgentSelector()
sub_agent_client = SubAgentClient()


@router.post("/agent", response_model=OrchestratorResponse)
async def orchestrator_endpoint(
    request: OrchestratorRequest,
    current_user: Optional[Dict] = Depends(get_current_user),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
):
    """
    Main orchestrator endpoint - THE CORE OF THE POC.

    This endpoint demonstrates the complete OBO flow:

    1. Receives user's JWT token from frontend
    2. Validates the JWT token (extracts user identity)
    3. Analyzes the message to select appropriate sub-agent
    4. Exchanges user JWT for OBO token scoped for sub-agent
    5. Calls sub-agent with OBO token
    6. Sub-agent validates OBO token and executes with user context
    7. Returns aggregated response to frontend

    Args:
        request: OrchestratorRequest with user's message
        current_user: User claims from validated JWT (dependency injection)
        credentials: JWT credentials from Authorization header

    Returns:
        OrchestratorResponse with sub-agent results
    """
    logger.info(
        f"Orchestrator received request from user: {current_user.get('name', 'unknown') if current_user else 'test'}"
    )

    # Step 1: Select the appropriate sub-agent
    selected_agent = agent_selector.select_agent(request.message, request.preferred_agent)
    logger.info(f"Selected agent: {selected_agent.value}")

    # Step 2: Acquire OBO token for the selected sub-agent
    obo_token = None
    if settings.REQUIRE_AUTH and credentials:
        user_token = credentials.credentials

        # Determine which scopes to request based on selected agent
        if selected_agent.value == "python":
            target_scopes = settings.PYTHON_AGENT_SCOPES
        else:
            target_scopes = settings.DOTNET_AGENT_SCOPES

        logger.info(f"Acquiring OBO token for scopes: {target_scopes}")

        try:
            obo_token = await get_obo_token(user_token, target_scopes)
            logger.info("OBO token acquired successfully")
        except HTTPException as e:
            logger.error(f"Failed to acquire OBO token: {e.detail}")
            raise

    # Step 3: Call the selected sub-agent with OBO token
    sub_agent_response = await sub_agent_client.call_sub_agent(
        agent_type=selected_agent,
        message=request.message,
        obo_token=obo_token,
        conversation_id=request.conversation_id,
        metadata=request.metadata,
    )

    # Step 4: Return orchestrated response
    return OrchestratorResponse(
        message=sub_agent_response.message,
        status="success",
        selected_agent=selected_agent.value,
        conversation_id=request.conversation_id,
        sub_agent_responses=[sub_agent_response],
        metadata={
            "user_id": current_user.get("oid") if current_user else "test",
            "user_name": current_user.get("name") if current_user else "Test User",
            "auth_enabled": settings.REQUIRE_AUTH,
            "obo_token_acquired": obo_token is not None,
        },
    )


@router.get("/agent")
async def orchestrator_status():
    """Simple GET endpoint for health checks."""
    return {
        "message": "Orchestrator is alive",
        "status": "healthy",
        "service": "orchestrator",
        "auth_required": settings.REQUIRE_AUTH,
    }


@router.get("/health/agents")
async def check_sub_agents():
    """Check health of all sub-agents."""
    from src.models import AgentType

    python_health = await sub_agent_client.health_check(AgentType.PYTHON)
    dotnet_health = await sub_agent_client.health_check(AgentType.DOTNET)

    return {
        "orchestrator": "healthy",
        "sub_agents": {
            "python": "healthy" if python_health else "unreachable",
            "dotnet": "healthy" if dotnet_health else "unreachable",
        },
    }
