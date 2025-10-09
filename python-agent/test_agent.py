#!/usr/bin/env python3
"""
Quick test script to verify Agent Framework configuration.

Run this to test your Azure OpenAI connection before starting the full server.
"""

import asyncio
import sys
from src.config import settings
from src.agent_framework_impl import agent_framework_service


async def test_agent():
    """Test the agent configuration and basic functionality."""
    print("=" * 60)
    print("Microsoft Agent Framework - Configuration Test")
    print("=" * 60)
    print()

    # Check configuration
    print("Configuration:")
    print(f"  Endpoint: {settings.azure_openai_endpoint}")
    print(f"  Deployment: {settings.azure_openai_deployment}")
    print(f"  API Version: {settings.azure_openai_api_version}")
    print(f"  Using API Key: {'Yes' if settings.azure_openai_api_key else 'No (using Azure credentials)'}")
    print(f"  Agent Name: {settings.agent_name}")
    print()

    # Check if agent initialized
    if not agent_framework_service.agent:
        print("❌ ERROR: Agent not initialized!")
        print()
        print("Possible issues:")
        print("  1. Check AZURE_OPENAI_ENDPOINT is set correctly in .env")
        print("  2. Check AZURE_OPENAI_DEPLOYMENT matches your deployment name")
        print("  3. If using API key, verify it's correct")
        print("  4. If using Azure credentials, run 'az login'")
        sys.exit(1)

    print("✅ Agent initialized successfully!")
    print()

    # Test a simple query
    print("Testing agent with simple query...")
    print("Query: 'What is 2 + 2?'")
    print()

    try:
        response = await agent_framework_service.run_agent(
            message="What is 2 + 2?",
            conversation_id=None,
        )

        print("Response:")
        print("-" * 60)
        print(response)
        print("-" * 60)
        print()
        print("✅ Test successful! Agent is working correctly.")
        print()
        print("Next steps:")
        print("  1. Start the server: uvicorn src.main:app --reload --port 8000")
        print("  2. Test the endpoint: curl http://localhost:8000/agent")
        print("  3. Try the agent: curl -X POST http://localhost:8000/agent \\")
        print("       -H 'Content-Type: application/json' \\")
        print("       -d '{\"message\": \"What is the weather in Seattle?\"}'")

    except Exception as e:
        print(f"❌ ERROR: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Verify your Azure OpenAI endpoint is accessible")
        print("  2. Check your API key or Azure credentials are valid")
        print("  3. Ensure the deployment name exists in Azure OpenAI Studio")
        print("  4. Check network connectivity to Azure")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(test_agent())
