"""Agent Framework integration for the Python agent."""

import os
import json
import asyncio
from typing import Optional, Dict
import httpx
from src.config import settings


class AgentService:
    """Service for managing different agent backends."""

    def __init__(self):
        """Initialize the agent service."""
        self.claude_sessions: Dict[str, str] = {}  # conversation_id -> session_id mapping

    async def run_shell_agent(self, message: str, conversation_id: Optional[str] = None) -> str:
        """
        Run a custom shell command (claude CLI) and return output.

        Args:
            message: The user's message
            conversation_id: Optional conversation ID for session resumption

        Returns:
            The agent's response
        """
        # Build command arguments
        args = ["claude", "-p", message, "--output-format", "json"]

        # Resume session if we have one for this conversation
        session_id = self.claude_sessions.get(conversation_id) if conversation_id else None
        if session_id:
            args.extend(["--resume", session_id])

        # Prepare environment (inherit current env)
        process_env = os.environ.copy()

        try:
            # Execute the claude CLI command
            process = await asyncio.create_subprocess_exec(
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=process_env,
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                response_text = f"Error invoking Claude: {stderr.decode().strip()}"
            else:
                try:
                    payload = json.loads(stdout.decode())
                except json.JSONDecodeError:
                    payload = {}

                response_text = payload.get("result") or stdout.decode().strip()

                # Store session ID for conversation continuity
                new_session = payload.get("session_id")
                if new_session and conversation_id:
                    self.claude_sessions[conversation_id] = new_session

            return response_text

        except FileNotFoundError:
            return "Error: 'claude' CLI not found. Please install it first."
        except Exception as e:
            return f"Error executing shell agent: {str(e)}"

    async def run_local_llm_http(self, message: str, conversation_id: Optional[str] = None) -> str:
        """
        Call a local LLM via HTTP (e.g., Ollama).

        Args:
            message: The user's message
            conversation_id: Optional conversation ID (unused for now)

        Returns:
            The LLM's response
        """
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "http://localhost:11434/api/generate",  # Ollama default endpoint
                    json={
                        "model": "llama2",  # Configure via settings if needed
                        "prompt": message,
                        "stream": False
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data.get("response", "No response from local LLM")
        except httpx.ConnectError:
            return "Error: Could not connect to local LLM at http://localhost:11434"
        except Exception as e:
            return f"Error calling local LLM: {str(e)}"

    async def run_openai_compatible(self, message: str, conversation_id: Optional[str] = None) -> str:
        """
        Use a local LLM with OpenAI-compatible API (e.g., LM Studio, vLLM, etc.).

        Args:
            message: The user's message
            conversation_id: Optional conversation ID (unused for now)

        Returns:
            The LLM's response
        """
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "http://localhost:1234/v1/chat/completions",  # LM Studio default
                    json={
                        "model": "local-model",  # Model name doesn't matter for most local servers
                        "messages": [
                            {"role": "system", "content": settings.agent_instructions},
                            {"role": "user", "content": message}
                        ],
                        "temperature": 0.7,
                    },
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except httpx.ConnectError:
            return "Error: Could not connect to OpenAI-compatible endpoint at http://localhost:1234"
        except Exception as e:
            return f"Error calling OpenAI-compatible API: {str(e)}"

    async def run_agent(self, message: str, conversation_id: Optional[str] = None) -> str:
        """
        Run the agent with a message using the configured backend.

        Currently configured to use: Shell Agent (Claude CLI)

        Args:
            message: The user's message
            conversation_id: Optional conversation ID for context

        Returns:
            The agent's response
        """
        # Use shell agent (claude CLI) as the active backend
        return await self.run_shell_agent(message, conversation_id)


# Global agent service instance
agent_service = AgentService()
