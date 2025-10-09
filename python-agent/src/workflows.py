"""Microsoft Agent Framework workflow implementations.

This module demonstrates workflow-based orchestration using the Microsoft Agent Framework.
Workflows provide structured, graph-based coordination of agents and functions.
"""

import asyncio
from typing import Optional, Dict, Any
from typing_extensions import Never
from agent_framework import WorkflowBuilder, WorkflowContext, WorkflowOutputEvent, executor
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import DefaultAzureCredential
from src.config import settings
import logging

logger = logging.getLogger(__name__)


# Sequential Workflow Demo: Text Processing Pipeline
# This demonstrates a simple sequential workflow that processes text through multiple stages


@executor(id="uppercase_executor")
async def uppercase_executor(text: str, ctx: WorkflowContext[str]) -> None:
    """Transform text to uppercase and forward to next step."""
    result = text.upper()
    logger.info(f"Uppercase executor: '{text}' -> '{result}'")
    await ctx.send_message(result)


@executor(id="reverse_executor")
async def reverse_executor(text: str, ctx: WorkflowContext[Never, str]) -> None:
    """Reverse text and yield as workflow output."""
    result = text[::-1]
    logger.info(f"Reverse executor: '{text}' -> '{result}'")
    await ctx.yield_output(result)


# Build the sequential text processing workflow
text_processing_workflow = (
    WorkflowBuilder()
    .add_edge(uppercase_executor, reverse_executor)
    .set_start_executor(uppercase_executor)
    .build()
)


# Multi-Agent Workflow Demo: Document Processing Pipeline
# This demonstrates a workflow coordinating multiple AI agents


class DocumentWorkflowService:
    """
    Service for document processing workflows.

    Demonstrates:
    - Sequential orchestration of multiple agents
    - Agent specialization (writer -> editor -> formatter)
    - State management across workflow steps
    """

    def __init__(self):
        """Initialize the workflow service."""
        self.writer_agent = None
        self.editor_agent = None
        self.initialized = False

    def _initialize_agents(self):
        """Initialize specialized agents for the workflow."""
        if self.initialized or not settings.azure_openai_endpoint:
            return

        try:
            credential = DefaultAzureCredential()
            client = AzureOpenAIChatClient(
                credential=credential,
                endpoint=settings.azure_openai_endpoint,
                deployment_name=settings.azure_openai_deployment,
            )

            # Create specialized agents
            self.writer_agent = client.create_agent(
                name="Writer",
                instructions="You are a creative writer. Write concise, engaging content based on user requests.",
            )

            self.editor_agent = client.create_agent(
                name="Editor",
                instructions="You are an editor. Improve the writing you receive by fixing grammar, enhancing clarity, and making it more professional.",
            )

            self.initialized = True
            logger.info("Document workflow agents initialized")

        except Exception as e:
            logger.error(f"Failed to initialize workflow agents: {e}")

    async def run_document_workflow(self, topic: str) -> str:
        """
        Run a document processing workflow.

        Pipeline:
        1. Writer agent creates initial content
        2. Editor agent improves the content
        3. Return final result

        Args:
            topic: The topic to write about

        Returns:
            The final processed document
        """
        self._initialize_agents()

        if not self.initialized:
            return "Workflow agents not initialized. Please check Azure OpenAI configuration."

        try:
            # Step 1: Writer creates content
            logger.info(f"Step 1: Writer creating content for topic: {topic}")
            writer_result = await self.writer_agent.run(
                f"Write a brief (2-3 paragraph) article about: {topic}"
            )
            draft = writer_result.text

            logger.info(f"Writer produced draft ({len(draft)} chars)")

            # Step 2: Editor improves content
            logger.info("Step 2: Editor improving content")
            editor_result = await self.editor_agent.run(
                f"Please improve this article:\n\n{draft}"
            )
            final = editor_result.text

            logger.info(f"Editor produced final version ({len(final)} chars)")

            return final

        except Exception as e:
            logger.error(f"Error in document workflow: {e}")
            return f"Error processing document: {str(e)}"


# Concurrent Workflow Demo: Multi-Perspective Analysis
# This demonstrates parallel agent execution


class AnalysisWorkflowService:
    """
    Service for multi-perspective analysis workflows.

    Demonstrates:
    - Concurrent orchestration (parallel agent execution)
    - Ensemble reasoning from multiple viewpoints
    - Result aggregation
    """

    def __init__(self):
        """Initialize the analysis workflow service."""
        self.technical_agent = None
        self.business_agent = None
        self.initialized = False

    def _initialize_agents(self):
        """Initialize specialized analysis agents."""
        if self.initialized or not settings.azure_openai_endpoint:
            return

        try:
            credential = DefaultAzureCredential()
            client = AzureOpenAIChatClient(
                credential=credential,
                endpoint=settings.azure_openai_endpoint,
                deployment_name=settings.azure_openai_deployment,
            )

            # Create specialized analysts
            self.technical_agent = client.create_agent(
                name="TechnicalAnalyst",
                instructions="You are a technical analyst. Analyze topics from a technical perspective, focusing on implementation, architecture, and feasibility.",
            )

            self.business_agent = client.create_agent(
                name="BusinessAnalyst",
                instructions="You are a business analyst. Analyze topics from a business perspective, focusing on value, ROI, and market impact.",
            )

            self.initialized = True
            logger.info("Analysis workflow agents initialized")

        except Exception as e:
            logger.error(f"Failed to initialize analysis agents: {e}")

    async def run_concurrent_analysis(self, topic: str) -> Dict[str, str]:
        """
        Run concurrent analysis from multiple perspectives.

        Args:
            topic: The topic to analyze

        Returns:
            Dictionary with analyses from each perspective
        """
        self._initialize_agents()

        if not self.initialized:
            return {
                "error": "Analysis agents not initialized. Please check Azure OpenAI configuration."
            }

        try:
            # Run analyses in parallel for faster execution
            logger.info(f"Running concurrent analysis for: {topic}")

            technical_task = self.technical_agent.run(
                f"Provide a technical analysis of: {topic}"
            )
            business_task = self.business_agent.run(
                f"Provide a business analysis of: {topic}"
            )

            # Await both concurrently
            technical_result, business_result = await asyncio.gather(
                technical_task, business_task
            )

            return {
                "technical_analysis": technical_result.text,
                "business_analysis": business_result.text,
                "topic": topic,
            }

        except Exception as e:
            logger.error(f"Error in concurrent analysis: {e}")
            return {"error": f"Error in analysis: {str(e)}"}


# Global workflow service instances
document_workflow_service = DocumentWorkflowService()
analysis_workflow_service = AnalysisWorkflowService()
