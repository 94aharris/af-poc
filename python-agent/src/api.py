"""API endpoints for the agent service."""

from fastapi import APIRouter, HTTPException
from src.models import AgentRequest, AgentResponse
from src.agent import agent_service
from src.config import settings

router = APIRouter()


@router.post("/agent", response_model=AgentResponse)
async def agent_endpoint(request: AgentRequest):
    """
    Main agent endpoint - receives chat requests and returns responses.

    Integrates with Microsoft Agent Framework for AI-powered responses.

    Args:
        request: AgentRequest containing the user's message

    Returns:
        AgentResponse with the agent's reply
    """
    try:
        # Run the agent with the user's message
        response_message = await agent_service.run_agent(
            message=request.message,
            conversation_id=request.conversation_id,
        )

        return AgentResponse(
            message=response_message,
            status="success",
            agent_type="python-agent-framework",
            conversation_id=request.conversation_id,
            metadata=request.metadata or {},
        )
    except Exception as e:
        # Log the error and return a user-friendly message
        error_msg = f"Agent execution failed: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg)


@router.get("/agent")
async def agent_status():
    """Simple GET endpoint for health checks."""
    return {
        "message": "Agent Framework enabled",
        "status": "healthy",
        "agent_type": "python-agent-framework",
        "agent_name": settings.agent_name,
    }
