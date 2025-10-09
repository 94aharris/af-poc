"""API endpoints for the orchestrator service."""

from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi.security import HTTPAuthorizationCredentials
from src.models import OrchestratorRequest, OrchestratorResponse, TokenInfo
from src.auth import get_current_user, get_obo_token, security
from src.agent_selector import AgentSelector
from src.sub_agent_client import SubAgentClient
from src.config import settings
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


@router.post("/agent/legacy", response_model=OrchestratorResponse)
async def orchestrator_endpoint(
    request: OrchestratorRequest,
    current_user: Optional[Dict] = Depends(get_current_user),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
):
    """
    Main orchestrator endpoint with full AAA implementation.

    This endpoint demonstrates the complete OBO flow with:
    - AUTHENTICATION: JWT validation and user identity extraction
    - AUTHORIZATION: Role-based access control for agent selection
    - AUDITING: Comprehensive logging of all security events

    Flow:
    1. Receives user's JWT token from frontend
    2. Validates the JWT token (extracts user identity and roles)
    3. Analyzes the message to select appropriate sub-agent
    4. Checks if user has permission to access selected agent
    5. Exchanges user JWT for OBO token scoped for sub-agent
    6. Calls sub-agent with OBO token
    7. Sub-agent validates OBO token and executes with user context
    8. Returns aggregated response to frontend

    Args:
        request: OrchestratorRequest with user's message
        current_user: User claims from validated JWT (dependency injection)
        credentials: JWT credentials from Authorization header

    Returns:
        OrchestratorResponse with sub-agent results
    """
    start_time = time.time()

    # Extract request ID for tracing
    request_id = request.metadata.get("request_id", f"req_{id(request)}")
    user_id = current_user.get("oid", "test") if current_user else "test"
    user_name = current_user.get("name", "unknown") if current_user else "test"
    user_email = (
        current_user.get("preferred_username") or current_user.get("email", "unknown")
        if current_user
        else "test@example.com"
    )
    user_roles = current_user.get("roles", []) if current_user else []

    # === AUTHENTICATION ===
    # Already done by get_current_user dependency
    audit_logger.log_jwt_validation(current_user, success=True)

    # Determine user's role level
    user_role_level = authorization_service.get_user_role_level(current_user)
    has_special_role = authorization_service.has_special_role(current_user)

    logger.info(
        f"[{request_id}] [ORCHESTRATOR] [AUTH] User authenticated - ID: {user_id}, Name: {user_name}, Email: {user_email}, "
        f"Roles: {user_roles}, Role Level: {user_role_level}, Has Special Role: {has_special_role}"
    )

    # Step 1: Select the appropriate sub-agent using intelligent routing if available
    selected_agent = await agent_selector.select_agent_async(
        request.message, request.preferred_agent
    )

    logger.info(
        f"[{request_id}] [ORCHESTRATOR] [AGENT SELECTION] Selected agent: {selected_agent.value} for message: '{request.message[:50]}...'"
    )

    audit_logger.log_agent_selection(
        current_user,
        selected_agent.value,
        reason=f"Intent analysis for message: {request.message[:50]}...",
    )

    # === AUTHORIZATION ===
    # Check if user has permission to access the selected agent
    try:
        authorization_service.require_agent_access(current_user, selected_agent)
        logger.info(
            f"[{request_id}] [ORCHESTRATOR] [AUTHZ] User {user_name} authorized to access {selected_agent.value} agent"
        )
    except HTTPException as e:
        logger.warning(
            f"[{request_id}] [ORCHESTRATOR] [AUTHZ] Authorization denied for user {user_name} (roles: {user_roles}) to access {selected_agent.value} agent"
        )
        audit_logger.log_authorization_denied(
            current_user, resource=f"agent:{selected_agent.value}", reason=str(e.detail)
        )
        raise

    # Step 2: Acquire OBO token for the selected sub-agent
    obo_token = None
    if settings.REQUIRE_AUTH and credentials:
        user_token = credentials.credentials

        # Determine which scopes to request based on selected agent
        if selected_agent.value == "python":
            target_scopes = settings.PYTHON_AGENT_SCOPES
        else:
            target_scopes = settings.DOTNET_AGENT_SCOPES

        logger.info(
            f"[{request_id}] [ORCHESTRATOR] [OBO] Acquiring OBO token for scopes: {target_scopes}"
        )

        try:
            obo_token = await get_obo_token(user_token, target_scopes)
            logger.info(
                f"[{request_id}] [ORCHESTRATOR] [OBO] OBO token acquired successfully for {selected_agent.value} agent"
            )

            # === AUDITING: OBO Token Acquisition ===
            audit_logger.log_obo_exchange(
                current_user, selected_agent.value, target_scopes, success=True
            )
        except HTTPException as e:
            logger.error(
                f"[{request_id}] [ORCHESTRATOR] [OBO] Failed to acquire OBO token: {e.detail}"
            )

            audit_logger.log_obo_exchange(
                current_user,
                selected_agent.value,
                target_scopes,
                success=False,
                error=str(e.detail),
            )
            raise

    # Step 3: Call the selected sub-agent with OBO token
    try:
        logger.info(
            f"[{request_id}] [ORCHESTRATOR] [AGENT CALL] Calling {selected_agent.value} agent"
        )

        sub_agent_response = await sub_agent_client.call_sub_agent(
            agent_type=selected_agent,
            message=request.message,
            obo_token=obo_token,
            conversation_id=request.conversation_id,
            metadata=request.metadata,
        )

        elapsed_time = (time.time() - start_time) * 1000

        logger.info(
            f"[{request_id}] [ORCHESTRATOR] [AGENT CALL] {selected_agent.value} agent call succeeded in {elapsed_time:.2f}ms"
        )

        # === AUDITING: Agent Call Success ===
        audit_logger.log_agent_call(
            current_user, selected_agent.value, success=True, response_time_ms=elapsed_time
        )

    except Exception as e:
        elapsed_time = (time.time() - start_time) * 1000

        logger.error(
            f"[{request_id}] [ORCHESTRATOR] [AGENT CALL] {selected_agent.value} agent call failed after {elapsed_time:.2f}ms: {str(e)}"
        )

        # === AUDITING: Agent Call Failure ===
        audit_logger.log_agent_call(
            current_user,
            selected_agent.value,
            success=False,
            response_time_ms=elapsed_time,
            error=str(e),
        )
        raise

    # Step 4: Return orchestrated response
    return OrchestratorResponse(
        message=sub_agent_response.message,
        status="success",
        selected_agent=selected_agent.value,
        conversation_id=request.conversation_id,
        sub_agent_responses=[sub_agent_response],
        metadata={
            "user_id": user_id,
            "user_name": user_name,
            "user_email": user_email,
            "user_roles": user_roles,
            "user_role_level": user_role_level,
            "has_special_role": has_special_role,
            "auth_enabled": settings.REQUIRE_AUTH,
            "obo_token_acquired": obo_token is not None,
            "response_time_ms": (time.time() - start_time) * 1000,
        },
    )


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
    user_id = current_user.get("oid", "test") if current_user else "test"
    user_name = current_user.get("name", "unknown") if current_user else "test"
    user_email = (
        current_user.get("preferred_username") or current_user.get("email", "unknown")
        if current_user
        else "test@example.com"
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
