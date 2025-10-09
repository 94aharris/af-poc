# Copyright (c) Microsoft. All rights reserved.

import asyncio

from agent_framework import AgentRunEvent, WorkflowBuilder
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential
from src.config import settings

"""
Step 2: Agents in a Workflow non-streaming

This sample uses two custom executors. A Writer agent creates or edits content,
then hands the conversation to a Reviewer agent which evaluates and finalizes the result.

Purpose:
Show how to wrap chat agents created by AzureOpenAIChatClient inside workflow executors. Demonstrate how agents
automatically yield outputs when they complete, removing the need for explicit completion events.
The workflow completes when it becomes idle.

Prerequisites:
- Azure OpenAI configured for AzureOpenAIChatClient with required environment variables.
- Authentication via azure-identity. Use AzureCliCredential and run az login before executing the sample.
- Basic familiarity with WorkflowBuilder, executors, edges, events, and streaming or non streaming runs.
"""


"""Build and run a simple two node agent workflow: Writer then Reviewer."""
# Create the Azure chat client. AzureCliCredential uses your current az login.
chat_client = AzureOpenAIChatClient(
    deployment_name=settings.azure_openai_deployment,
    endpoint=settings.azure_openai_endpoint,
    api_key=settings.azure_openai_api_key or None,
    # api_version="2025-03-01-preview",
    # credential=AzureCliCredential()
)
writer_agent = chat_client.create_agent(
    instructions=(
        "You are an excellent content writer. You create new content and edit contents based on the feedback."
    ),
    name="writer",
)

reviewer_agent = chat_client.create_agent(
    instructions=(
        "You are an excellent content reviewer."
        "Provide actionable feedback to the writer about the provided content."
        "Provide the feedback in the most concise manner possible."
    ),
    name="reviewer",
)

# Build the workflow using the fluent builder.
# Set the start node and connect an edge from writer to reviewer.
workflow = (
    WorkflowBuilder()
    .set_start_executor(writer_agent)
    .add_edge(writer_agent, reviewer_agent)
    .build()
)

from agent_framework.devui import serve

# Uncomment this line to run devui and interact with the workflow simply by running
# serve(entities=[workflow], auto_open=True, tracing_enabled=True)
