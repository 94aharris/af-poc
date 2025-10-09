"""Intelligent routing using Claude Code for orchestrator decision making."""

import os
import json
import asyncio
from typing import Optional
from src.models import AgentType
import logging

logger = logging.getLogger(__name__)


class IntelligentRouter:
    """
    Uses Claude Code to intelligently route requests to the appropriate specialized agent.
    This provides AI-powered decision making for complex routing scenarios.
    """

    def __init__(self, enabled: bool = False):
        """
        Initialize the intelligent router.

        Args:
            enabled: Whether to use AI-powered routing (requires Claude CLI)
        """
        self.enabled = enabled
        self.claude_available = self._check_claude_available()

        if self.enabled and not self.claude_available:
            logger.warning(
                "Intelligent routing enabled but Claude CLI not available. "
                "Falling back to keyword-based routing."
            )
            self.enabled = False

    def _check_claude_available(self) -> bool:
        """Check if Claude CLI is available."""
        try:
            import shutil

            return shutil.which("claude") is not None
        except Exception:
            return False

    async def route_with_ai(self, message: str) -> Optional[AgentType]:
        """
        Use Claude Code to intelligently determine which agent should handle the request.

        Args:
            message: The user's message

        Returns:
            AgentType if AI routing is successful, None to fall back to keyword routing
        """
        if not self.enabled:
            return None

        routing_prompt = f"""You are an intelligent routing agent for a multi-agent system. Analyze the user's message and determine which specialized agent should handle it.

Available agents:
1. **dotnet** - Payroll Specialist Agent
   - Handles: Employee payroll information, PTO/vacation balance, time off requests, employee details (name, department, manager, job title, hire date), benefits inquiries
   - Tools: GetUserInfo, GetUserPto, CalculateAvailablePto
   - Use for: Any questions about payroll, PTO, employee information, time off, vacation days

2. **python** - General Purpose Agent
   - Handles: Programming questions, data analysis, code generation, general inquiries, technical questions not related to payroll
   - Tools: Claude Code headless mode with full programming capabilities
   - Use for: Everything else that's not payroll-related

User message: "{message}"

Analyze this message and respond with ONLY ONE WORD - either "dotnet" or "python" - indicating which agent should handle this request.

If the message is about:
- PTO, vacation, time off, employee info, payroll, benefits -> respond: dotnet
- Programming, coding, general questions, data analysis -> respond: python

Your response (one word only):"""

        try:
            # Build command arguments for headless mode
            args = ["claude", "-p", "--output-format", "json"]

            # Execute the claude CLI command in headless mode
            process = await asyncio.create_subprocess_exec(
                *args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=os.environ.copy(),
            )

            stdout, stderr = await process.communicate(input=routing_prompt.encode())

            if process.returncode != 0:
                logger.error(f"Claude routing failed: {stderr.decode()}")
                return None

            try:
                # Parse JSON output from Claude Code
                payload = json.loads(stdout.decode())
                response_text = payload.get("result", "").strip().lower()

                # Extract agent type from response
                if "dotnet" in response_text:
                    logger.info("AI Router selected: DOTNET (Payroll Specialist)")
                    return AgentType.DOTNET
                elif "python" in response_text:
                    logger.info("AI Router selected: PYTHON (General Purpose)")
                    return AgentType.PYTHON
                else:
                    logger.warning(
                        f"AI Router returned unexpected response: {response_text}"
                    )
                    return None

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Claude response: {e}")
                return None

        except FileNotFoundError:
            logger.error("Claude CLI not found")
            self.enabled = False
            return None
        except Exception as e:
            logger.error(f"Error in AI routing: {e}")
            return None
