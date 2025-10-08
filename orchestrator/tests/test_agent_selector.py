"""Tests for agent selection logic."""

import pytest
from src.agent_selector import AgentSelector
from src.models import AgentType


def test_python_keyword_selection():
    """Test that Python keywords trigger Python agent selection."""
    selector = AgentSelector()

    messages = [
        "Help me with pandas dataframe",
        "I need to do some data analysis with numpy",
        "How do I use FastAPI?",
    ]

    for message in messages:
        agent = selector.select_agent(message, AgentType.AUTO)
        assert agent == AgentType.PYTHON


def test_dotnet_keyword_selection():
    """Test that .NET keywords trigger .NET agent selection."""
    selector = AgentSelector()

    messages = [
        "Help me with ASP.NET Core",
        "I need help with C# and Entity Framework",
        "How do I use Blazor?",
    ]

    for message in messages:
        agent = selector.select_agent(message, AgentType.AUTO)
        assert agent == AgentType.DOTNET


def test_explicit_preference():
    """Test that explicit preference overrides auto-selection."""
    selector = AgentSelector()

    # Message has Python keywords but .NET preference
    message = "Help me with pandas"
    agent = selector.select_agent(message, AgentType.DOTNET)
    assert agent == AgentType.DOTNET

    # Message has .NET keywords but Python preference
    message = "Help me with C#"
    agent = selector.select_agent(message, AgentType.PYTHON)
    assert agent == AgentType.PYTHON


def test_default_to_python():
    """Test that ambiguous messages default to Python."""
    selector = AgentSelector()

    message = "Hello, how are you?"
    agent = selector.select_agent(message, AgentType.AUTO)
    assert agent == AgentType.PYTHON
