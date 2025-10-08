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
