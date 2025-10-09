# pip install agent-framework --pre
# Use `az login` to authenticate with Azure CLI
from agent_framework.azure import AzureOpenAIResponsesClient
from agent_framework.devui import serve
from azure.identity import AzureCliCredential
from config import settings


# Initialize a chat agent with Azure OpenAI Responses
# Configuration is loaded from .env via config.py
agent = AzureOpenAIResponsesClient(
    endpoint=settings.azure_openai_endpoint,
    deployment_name=settings.azure_openai_deployment,
    api_key=settings.azure_openai_api_key or None,
    api_version="2025-03-01-preview",
    credential=AzureCliCredential(),
).create_agent(
    name="HaikuBot",
    instructions="You are an upbeat assistant that writes beautifully.",
)
