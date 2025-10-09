"""API endpoints for the orchestrator service."""

from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi.security import HTTPAuthorizationCredentials
from src.models import OrchestratorRequest, OrchestratorResponse, TokenInfo
from src.auth import get_current_user, get_obo_token, security
from src.agent_selector import AgentSelector
from src.sub_agent_client import SubAgentClient
from src.config import settings
from src.constants import TEST_USER_ID, TEST_USER_NAME, TEST_USER_EMAIL
from src.audit import audit_logger
from src.authorization import authorization_service
from typing import Optional, Dict
import logging
import time

logger = logging.getLogger(__name__)
router = APIRouter()

# Import agent framework service (will be initialized if Azure OpenAI is configured)
try:
    from src.agent_framework_impl import agent_framework_service

    AGENT_FRAMEWORK_AVAILABLE = True
except Exception as e:
    logger.warning(f"Agent Framework not available: {e}")
    AGENT_FRAMEWORK_AVAILABLE = False
    agent_framework_service = None

# Initialize agent selector with intelligent routing enabled (requires Claude CLI)
# Set to False to use keyword-based routing only
USE_INTELLIGENT_ROUTING = (
    settings.ENABLE_INTELLIGENT_ROUTING
    if hasattr(settings, "ENABLE_INTELLIGENT_ROUTING")
    else False
)

agent_selector = AgentSelector(use_intelligent_routing=USE_INTELLIGENT_ROUTING)
sub_agent_client = SubAgentClient()


@router.post("/agent", response_model=OrchestratorResponse)
async def agent_framework_endpoint(
    request: OrchestratorRequest,
    current_user: Optional[Dict] = Depends(get_current_user),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
):
    """
    Agent Framework endpoint using Microsoft Agent Framework.

    This endpoint uses the Microsoft Agent Framework with specialized tools for:
    - Payroll API integration (user info, PTO data)
    - Calculator routing to python-agent for mathematics

    The agent will automatically select and use the appropriate tools based on the user's message.
    """
    start_time = time.time()

    # Check if agent framework is available
    if (
        not AGENT_FRAMEWORK_AVAILABLE
        or not agent_framework_service
        or not agent_framework_service.agent
    ):
        raise HTTPException(
            status_code=503,
            detail="Agent Framework not available. Please configure Azure OpenAI settings.",
        )

    # Extract request ID for tracing
    request_id = request.metadata.get("request_id", f"req_{id(request)}")
    user_id = current_user.get("oid", TEST_USER_ID) if current_user else TEST_USER_ID
    user_name = current_user.get("name", "unknown") if current_user else TEST_USER_NAME
    user_email = (
        current_user.get("preferred_username") or current_user.get("email", "unknown")
        if current_user
        else TEST_USER_EMAIL
    )
    user_roles = current_user.get("roles", []) if current_user else []

    logger.info(
        f"[{request_id}] [AGENT FRAMEWORK] User authenticated - ID: {user_id}, Name: {user_name}, "
        f"Email: {user_email}, Roles: {user_roles}"
    )

    # Get user token if available
    user_token = None
    if settings.REQUIRE_AUTH and credentials:
        user_token = credentials.credentials

    # Run agent with the message
    try:
        logger.info(
            f"[{request_id}] [AGENT FRAMEWORK] Running agent with message: '{request.message[:100]}...'"
        )

        response_message = await agent_framework_service.run_agent(
            message=request.message,
            conversation_id=request.conversation_id,
            user_token=user_token,
        )

        elapsed_time = (time.time() - start_time) * 1000

        logger.info(
            f"[{request_id}] [AGENT FRAMEWORK] Agent completed successfully in {elapsed_time:.2f}ms"
        )

        # Return response
        return OrchestratorResponse(
            message=response_message,
            status="success",
            selected_agent="agent-framework",
            conversation_id=request.conversation_id,
            sub_agent_responses=[],
            metadata={
                "user_id": user_id,
                "user_name": user_name,
                "user_email": user_email,
                "user_roles": user_roles,
                "response_time_ms": elapsed_time,
                "agent_type": "microsoft-agent-framework",
            },
        )

    except Exception as e:
        elapsed_time = (time.time() - start_time) * 1000
        logger.error(
            f"[{request_id}] [AGENT FRAMEWORK] Agent failed after {elapsed_time:.2f}ms: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=f"Agent Framework error: {str(e)}")


@router.get("/agent")
async def orchestrator_status():
    """Simple GET endpoint for health checks."""
    return {
        "message": "Orchestrator is alive",
        "status": "healthy",
        "service": "orchestrator",
        "auth_required": settings.REQUIRE_AUTH,
        "agent_framework_available": AGENT_FRAMEWORK_AVAILABLE,
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
