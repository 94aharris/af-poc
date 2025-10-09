"""API endpoints for the agent service."""

from fastapi import APIRouter, HTTPException
from src.models import AgentRequest, AgentResponse, WorkflowRequest, WorkflowResponse
from src.agent_framework_impl import agent_framework_service
from src.workflows import document_workflow_service, analysis_workflow_service
from src.config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/agent", response_model=AgentResponse)
async def agent_endpoint(request: AgentRequest):
    """
    Main agent endpoint using Microsoft Agent Framework.

    Uses the new AgentFrameworkService which follows best practices:
    - Azure OpenAI integration with proper authentication
    - Thread-based conversation state management
    - Function tools for external capabilities

    Args:
        request: AgentRequest containing the user's message

    Returns:
        AgentResponse with the agent's reply
    """
    request_id = request.metadata.get("request_id", "unknown") if request.metadata else "unknown"
    logger.info(f"[{request_id}] [PYTHON-AGENT-FRAMEWORK] Processing message: {request.message[:100]}")

    try:
        # Use the new Agent Framework implementation
        response_message = await agent_framework_service.run_agent(
            message=request.message,
            conversation_id=request.conversation_id,
        )

        logger.info(f"[{request_id}] [PYTHON-AGENT-FRAMEWORK] Response generated successfully")

        return AgentResponse(
            message=response_message,
            status="success",
            agent_type="microsoft-agent-framework",
            conversation_id=request.conversation_id,
            metadata=request.metadata or {},
        )
    except Exception as e:
        logger.error(f"[{request_id}] Agent execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")


@router.post("/workflow/document", response_model=WorkflowResponse)
async def document_workflow_endpoint(request: WorkflowRequest):
    """
    Document processing workflow endpoint.

    Demonstrates sequential orchestration:
    1. Writer agent creates initial content
    2. Editor agent improves the content
    3. Returns final polished document

    Args:
        request: WorkflowRequest with topic/input

    Returns:
        WorkflowResponse with processed document
    """
    logger.info(f"[WORKFLOW] Document processing for: {request.input[:100]}")

    try:
        result = await document_workflow_service.run_document_workflow(request.input)

        return WorkflowResponse(
            result=result,
            status="success",
            workflow_type="sequential-document-processing",
            metadata={"steps": ["writer", "editor"]},
        )
    except Exception as e:
        logger.error(f"Document workflow failed: {e}")
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")


@router.post("/workflow/analysis", response_model=WorkflowResponse)
async def analysis_workflow_endpoint(request: WorkflowRequest):
    """
    Multi-perspective analysis workflow endpoint.

    Demonstrates concurrent orchestration:
    - Technical analyst provides technical perspective
    - Business analyst provides business perspective
    - Results aggregated and returned together

    Args:
        request: WorkflowRequest with topic to analyze

    Returns:
        WorkflowResponse with multi-perspective analysis
    """
    logger.info(f"[WORKFLOW] Concurrent analysis for: {request.input[:100]}")

    try:
        result = await analysis_workflow_service.run_concurrent_analysis(request.input)

        # Format the multi-perspective result
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])

        formatted_result = f"""
Multi-Perspective Analysis: {result['topic']}

=== Technical Perspective ===
{result['technical_analysis']}

=== Business Perspective ===
{result['business_analysis']}
"""

        return WorkflowResponse(
            result=formatted_result.strip(),
            status="success",
            workflow_type="concurrent-multi-perspective-analysis",
            metadata={
                "perspectives": ["technical", "business"],
                "execution": "parallel",
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis workflow failed: {e}")
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")


@router.get("/agent")
async def agent_status():
    """Agent status and health check endpoint."""
    return {
        "message": "Microsoft Agent Framework enabled",
        "status": "healthy",
        "agent_type": "microsoft-agent-framework",
        "agent_name": settings.agent_name,
        "features": {
            "tools": ["get_weather", "calculate", "search_files"],
            "workflows": ["document_processing", "concurrent_analysis"],
            "authentication": "Azure OpenAI with DefaultAzureCredential",
        },
    }
