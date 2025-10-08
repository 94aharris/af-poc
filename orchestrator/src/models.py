"""Data models for orchestrator requests and responses."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum


class AgentType(str, Enum):
    """Available sub-agent types."""

    PYTHON = "python"
    DOTNET = "dotnet"
    AUTO = "auto"  # Orchestrator decides


class OrchestratorRequest(BaseModel):
    """Request model for orchestrator endpoint."""

    message: str = Field(..., description="User message/query")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    preferred_agent: AgentType = Field(
        default=AgentType.AUTO, description="Preferred agent or auto-select"
    )
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class SubAgentResponse(BaseModel):
    """Response from a sub-agent."""

    agent_type: str
    message: str
    status: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class OrchestratorResponse(BaseModel):
    """Response model from orchestrator endpoint."""

    message: str
    status: str
    selected_agent: str
    conversation_id: Optional[str] = None
    sub_agent_responses: List[SubAgentResponse] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class TokenInfo(BaseModel):
    """Information about JWT token processing."""

    user_id: Optional[str] = None
    user_name: Optional[str] = None
    scopes: List[str] = Field(default_factory=list)
    token_acquired: bool = False
