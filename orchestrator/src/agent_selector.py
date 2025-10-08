"""Agent selection logic - determines which sub-agent to use."""

from src.models import AgentType
from typing import List
import re


class AgentSelector:
    """Selects the appropriate sub-agent based on user message intent."""

    def __init__(self):
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
        ]

        # Keywords that indicate .NET sub-agent should handle
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
        ]

    def select_agent(self, message: str, preferred_agent: AgentType) -> AgentType:
        """
        Select the appropriate agent based on message content and preference.

        Args:
            message: The user's message
            preferred_agent: User's preferred agent or AUTO

        Returns:
            Selected agent type (PYTHON or DOTNET)
        """
        # If user specified a preference, use it
        if preferred_agent != AgentType.AUTO:
            return preferred_agent

        # Analyze message content
        message_lower = message.lower()

        # Count keyword matches
        python_score = sum(1 for keyword in self.python_keywords if keyword in message_lower)
        dotnet_score = sum(1 for keyword in self.dotnet_keywords if keyword in message_lower)

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
                "machine learning, FastAPI, and Python ecosystem"
            )
        elif agent_type == AgentType.DOTNET:
            return (
                ".NET specialist agent - expertise in C#, ASP.NET Core, "
                "Entity Framework, and Microsoft technologies"
            )
        else:
            return "Auto-select based on message content"
