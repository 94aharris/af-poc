"""Data models for agent requests and responses."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class AgentRequest(BaseModel):
    """Request model for agent endpoint."""

    message: str = Field(..., description="User message/query")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class AgentResponse(BaseModel):
    """Response model from agent endpoint."""

    message: str
    status: str
    agent_type: str
    conversation_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class WorkflowRequest(BaseModel):
    """Request model for workflow endpoints."""

    input: str = Field(..., description="Input data for the workflow")
    workflow_params: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional workflow parameters"
    )
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class WorkflowResponse(BaseModel):
    """Response model from workflow endpoints."""

    result: str = Field(..., description="Workflow execution result")
    status: str
    workflow_type: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
