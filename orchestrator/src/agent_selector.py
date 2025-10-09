"""Agent selection logic - determines which sub-agent to use."""

from src.models import AgentType
from src.intelligent_routing import IntelligentRouter
from typing import List, Optional
import re
import logging

logger = logging.getLogger(__name__)


class AgentSelector:
    """Selects the appropriate sub-agent based on user message intent."""

    def __init__(self, use_intelligent_routing: bool = False):
        """
        Initialize the agent selector.

        Args:
            use_intelligent_routing: Whether to use Claude-powered AI routing
        """
        self.intelligent_router = IntelligentRouter(enabled=use_intelligent_routing)
        # Keywords that indicate Python sub-agent should handle
        self.python_keywords = [
            "python",
            "pandas",
            "numpy",
            "data",
            "analysis",
            "dataframe",
            "plot",
            "visualization",
            "machine learning",
            "ml",
            "fastapi",
            "django",
            "jupyter",
            "notebook",
        ]

        # Keywords that indicate .NET/Payroll sub-agent should handle
        # The dotnet agent is specialized for payroll queries
        self.dotnet_keywords = [
            ".net",
            "dotnet",
            "c#",
            "csharp",
            "asp.net",
            "aspnet",
            "entity framework",
            "ef core",
            "blazor",
            "xamarin",
            "maui",
            # Payroll-specific keywords
            "payroll",
            "pto",
            "paid time off",
            "vacation",
            "time off",
            "employee",
            "salary",
            "benefits",
            "my info",
            "my information",
            "my manager",
            "my department",
            "hire date",
            "job title",
            "available pto",
            "how much pto",
            "pto balance",
            "upcoming time off",
        ]

    async def select_agent_async(
        self, message: str, preferred_agent: AgentType
    ) -> AgentType:
        """
        Select the appropriate agent based on message content and preference (async).

        Args:
            message: The user's message
            preferred_agent: User's preferred agent or AUTO

        Returns:
            Selected agent type (PYTHON or DOTNET)
        """
        # If user specified a preference, use it
        if preferred_agent != AgentType.AUTO:
            logger.info(f"Using user-preferred agent: {preferred_agent.value}")
            return preferred_agent

        # Try intelligent AI-powered routing first
        if self.intelligent_router.enabled:
            ai_selection = await self.intelligent_router.route_with_ai(message)
            if ai_selection:
                logger.info(
                    f"AI Router selected {ai_selection.value} for message: {message[:50]}..."
                )
                return ai_selection

        # Fall back to keyword-based routing
        logger.info("Using keyword-based routing")
        return self._select_by_keywords(message)

    def select_agent(self, message: str, preferred_agent: AgentType) -> AgentType:
        """
        Select the appropriate agent based on message content and preference (sync wrapper).

        Args:
            message: The user's message
            preferred_agent: User's preferred agent or AUTO

        Returns:
            Selected agent type (PYTHON or DOTNET)
        """
        # If user specified a preference, use it
        if preferred_agent != AgentType.AUTO:
            return preferred_agent

        # Use keyword-based routing (sync fallback)
        return self._select_by_keywords(message)

    def _select_by_keywords(self, message: str) -> AgentType:
        """
        Select agent using keyword matching.

        Args:
            message: The user's message

        Returns:
            Selected agent type
        """
        # Analyze message content
        message_lower = message.lower()

        # Count keyword matches
        python_score = sum(
            1 for keyword in self.python_keywords if keyword in message_lower
        )
        dotnet_score = sum(
            1 for keyword in self.dotnet_keywords if keyword in message_lower
        )

        logger.info(
            f"Keyword scores - Python: {python_score}, Dotnet/Payroll: {dotnet_score}"
        )

        # Select based on scores
        if python_score > dotnet_score:
            return AgentType.PYTHON
        elif dotnet_score > python_score:
            return AgentType.DOTNET
        else:
            # Default to Python if no clear winner
            return AgentType.PYTHON

    def get_agent_capabilities(self, agent_type: AgentType) -> str:
        """Get a description of an agent's capabilities."""
        if agent_type == AgentType.PYTHON:
            return (
                "Python specialist agent - expertise in data analysis, "
                "machine learning, FastAPI, and Python ecosystem. "
                "Uses Claude Code for general programming and data tasks."
            )
        elif agent_type == AgentType.DOTNET:
            return (
                "Payroll specialist agent - expertise in employee payroll information, "
                "PTO (paid time off) management, employee details, and benefits. "
                "Built with Microsoft Agent Framework and specialized tools for payroll API access."
            )
        else:
            return "Auto-select based on message content"
