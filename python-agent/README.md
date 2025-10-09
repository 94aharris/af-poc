# Python Agent Implementation - Microsoft Agent Framework POC

## Overview

This Python implementation demonstrates a FastAPI-based agent service using the Microsoft Agent Framework with JWT On-Behalf-Of (OBO) authentication flow.

## Technology Stack

- **Python**: 3.11+
- **Package Manager**: UV (ultra-fast Python package installer and resolver)
- **Web Framework**: FastAPI + Uvicorn
- **Agent Framework**: `agent-framework` (Microsoft Agent Framework)
- **LLM Provider**: Azure OpenAI
- **Authentication**: `azure-identity` - Azure credential management
- **Validation**: `pydantic` - Data validation (built into FastAPI)

## Project Structure

```
python-agent/
├── README.md                      # This file
├── README_AGENT_FRAMEWORK.md      # Microsoft Agent Framework documentation
├── pyproject.toml                 # UV project configuration & dependencies
├── .python-version                # Python version specification
├── src/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── api.py                     # API endpoints
│   ├── agent_framework_impl.py    # Microsoft Agent Framework implementation
│   ├── workflows.py               # Workflow orchestration examples
│   ├── config.py                  # Configuration management
│   └── models.py                  # Pydantic models for requests/responses
├── tests/
│   └── __init__.py
├── examples/
│   ├── agent_example.py           # Simple agent example
│   ├── workflow_agent_example.py  # Multi-agent workflow example
│   └── workflow_simple_example.py # Basic workflow example
├── test_agent.py                  # Quick agent configuration test
└── .env.example                   # Environment variable template
```

## Getting Started

### Prerequisites

1. **Install UV**:
   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Or via pip
   pip install uv
   ```

2. **Azure Resources** (for full OBO implementation):
   - Azure AD App Registration (for API)
   - Azure OpenAI Service instance
   - Configured API permissions and scopes

### Project Initialization

The project has already been initialized with the following structure and dependencies:

**Installed Packages:**
- `fastapi` (>=0.110.0) - Web framework
- `uvicorn[standard]` (>=0.27.0) - ASGI server
- `pydantic` (>=2.6.0) - Data validation
- `pydantic-settings` (>=2.1.0) - Configuration management
- `agent-framework` - Microsoft Agent Framework (installed with prerelease flag)
- `azure-identity` (>=1.15.0) - Azure credential management

To build and run:

```bash
# Navigate to the python-agent directory
cd python-agent

# Activate the virtual environment (already created)
source .venv/bin/activate

# Install/update dependencies (use --prerelease=allow for agent-framework)
uv pip install --prerelease=allow -e ".[dev]"

# Run the application
uvicorn src.main:app --reload --port 8000
```

### Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# Optional variables:
# - AZURE_OPENAI_ENDPOINT
# - AZURE_OPENAI_DEPLOYMENT
# - AZURE_OPENAI_API_KEY
# - AGENT_NAME
# - AGENT_INSTRUCTIONS
# - API_PORT
# - API_HOST
# - REQUIRE_AUTH
```

### Running the Service

```bash
# Development mode with auto-reload
uv run uvicorn src.main:app --reload --port 8000

# Production mode
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Testing

```bash
# Quick agent configuration test
python test_agent.py

# Test the health endpoint
curl http://localhost:8000/health

# Test the agent status endpoint
curl http://localhost:8000/agent

# Test the agent endpoint with a message
curl -X POST http://localhost:8000/agent \
  -H "Content-Type: application/json" \
  -d '{"message": "What is 2 + 2?"}'

# Test workflow endpoints
curl -X POST http://localhost:8000/workflow/document \
  -H "Content-Type: application/json" \
  -d '{"input": "Write about artificial intelligence"}'

curl -X POST http://localhost:8000/workflow/analysis \
  -H "Content-Type: application/json" \
  -d '{"input": "Cloud computing migration"}'
```

## Implementation Status

### ✅ Phase 1: Basic FastAPI Service

**File: `src/main.py`**
```python
from fastapi import FastAPI
from src.api import router

app = FastAPI(
    title="Python Agent Service",
    description="Microsoft Agent Framework with OBO authentication",
    version="0.1.0"
)

app.include_router(router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

**File: `src/api.py`**
```python
from fastapi import APIRouter, HTTPException
from src.models import AgentRequest, AgentResponse

router = APIRouter()

@router.post("/agent")
async def agent_endpoint(request: AgentRequest):
    """
    Main agent endpoint - receives chat requests and returns responses.
    Phase 1: Returns 'it's alive' message
    Phase 2+: Integrates with Agent Framework and OBO flow
    """
    return AgentResponse(
        message="it's alive",
        status="healthy",
        agent_type="python-fastapi"
    )

@router.get("/agent")
async def agent_status():
    """Simple GET endpoint for health checks"""
    return {"message": "it's alive", "status": "healthy"}
```

**File: `src/models.py`**
```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class AgentRequest(BaseModel):
    """Request model for agent endpoint"""
    message: str = Field(..., description="User message/query")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class AgentResponse(BaseModel):
    """Response model from agent endpoint"""
    message: str
    status: str
    agent_type: str
    conversation_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
```

### ✅ Phase 2: Microsoft Agent Framework Integration

The service uses Azure OpenAI through the Microsoft Agent Framework with function tools.

**File: `src/agent_framework_impl.py`**

Key features:
- Azure OpenAI client with API key or Azure credential authentication
- Thread-based conversation state management
- Function tools: `get_weather`, `calculate`, `search_files`
- Streaming and non-streaming response support

Example usage:
```python
from src.agent_framework_impl import agent_framework_service

# Run agent with conversation context
response = await agent_framework_service.run_agent(
    message="What's the weather in Seattle?",
    conversation_id="user-123"
)
```

### ✅ Phase 3: Workflow Orchestration

The service includes workflow examples for multi-agent coordination.

**File: `src/workflows.py`**

Two workflow types implemented:

1. **Document Processing Workflow** (Sequential)
   - Writer agent creates content
   - Editor agent improves content
   - Returns polished document

2. **Multi-Perspective Analysis** (Concurrent)
   - Technical analyst provides technical view
   - Business analyst provides business view
   - Results aggregated in parallel

Example:
```python
from src.workflows import document_workflow_service

result = await document_workflow_service.run_document_workflow(
    "Write about cloud computing"
)
```

### ⏳ Future: JWT Validation & OBO Flow

**Planned: `src/auth.py`**
```python
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import msal
import httpx
from typing import Optional, Dict
from src.config import settings

security = HTTPBearer()

class JWTValidator:
    """Validates JWT tokens from Azure AD"""

    def __init__(self):
        self.jwks_client = None
        self.jwks_cache = None

    async def get_signing_keys(self) -> Dict:
        """Fetch JWKS from Azure AD"""
        if self.jwks_cache:
            return self.jwks_cache

        metadata_url = (
            f"https://login.microsoftonline.com/{settings.AZURE_TENANT_ID}/"
            f"v2.0/.well-known/openid-configuration"
        )

        async with httpx.AsyncClient() as client:
            metadata = await client.get(metadata_url)
            jwks_uri = metadata.json()["jwks_uri"]
            jwks_response = await client.get(jwks_uri)
            self.jwks_cache = jwks_response.json()

        return self.jwks_cache

    async def validate_token(self, token: str) -> Dict:
        """Validate JWT token and return claims"""
        try:
            # Get signing keys
            jwks = await self.get_signing_keys()

            # Decode and validate token
            claims = jwt.decode(
                token,
                jwks,
                algorithms=[settings.JWT_ALGORITHM],
                audience=settings.JWT_AUDIENCE,
                issuer=settings.JWT_ISSUER,
                options={"verify_signature": True}
            )

            return claims

        except JWTError as e:
            raise HTTPException(
                status_code=401,
                detail=f"Invalid authentication credentials: {str(e)}"
            )

class OBOTokenService:
    """Handles On-Behalf-Of token exchange"""

    def __init__(self):
        self.msal_app = msal.ConfidentialClientApplication(
            client_id=settings.AZURE_CLIENT_ID,
            client_credential=settings.AZURE_CLIENT_SECRET,
            authority=f"https://login.microsoftonline.com/{settings.AZURE_TENANT_ID}"
        )

    async def acquire_token_on_behalf_of(
        self,
        user_token: str,
        scopes: list[str]
    ) -> Optional[str]:
        """
        Exchange user token for a new token with different scopes.
        This is the core OBO flow implementation.

        Args:
            user_token: The incoming JWT token from the user
            scopes: The scopes required for the downstream API

        Returns:
            Access token for the downstream API with user context
        """
        try:
            # Acquire token on behalf of the user
            result = self.msal_app.acquire_token_on_behalf_of(
                user_assertion=user_token,
                scopes=scopes
            )

            if "access_token" in result:
                return result["access_token"]
            else:
                error = result.get("error_description", "Unknown error")
                raise HTTPException(
                    status_code=401,
                    detail=f"Failed to acquire OBO token: {error}"
                )

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"OBO token acquisition failed: {str(e)}"
            )

# Dependency injection for FastAPI
jwt_validator = JWTValidator()
obo_service = OBOTokenService()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> Dict:
    """FastAPI dependency to validate JWT and extract user claims"""
    token = credentials.credentials
    claims = await jwt_validator.validate_token(token)
    return claims

async def get_obo_token(
    user_token: str,
    target_scopes: list[str]
) -> str:
    """Helper to acquire OBO token"""
    return await obo_service.acquire_token_on_behalf_of(user_token, target_scopes)
```

### ⏳ Future: Full Integration with Authentication

**Planned: Update `src/api.py` with authentication**
```python
from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi.security import HTTPAuthorizationCredentials
from src.models import AgentRequest, AgentResponse
from src.auth import get_current_user, get_obo_token, security
from src.agent import AgentService

router = APIRouter()
agent_service = AgentService()

@router.post("/agent")
async def agent_endpoint(
    request: AgentRequest,
    current_user: Dict = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """
    Authenticated agent endpoint with OBO flow.

    1. Validates incoming JWT token
    2. Acquires OBO token for downstream services
    3. Processes message through Agent Framework
    4. Returns response maintaining user context
    """
    user_token = credentials.credentials

    # Acquire OBO token for calling downstream APIs
    # (e.g., Microsoft Graph, custom APIs)
    downstream_scopes = ["api://your-api/.default"]
    obo_token = await get_obo_token(user_token, downstream_scopes)

    # Process through agent with user context
    response = await agent_service.process_message(
        message=request.message,
        user_token=obo_token
    )

    return AgentResponse(
        message=response,
        status="success",
        agent_type="python-fastapi",
        conversation_id=request.conversation_id,
        metadata={
            "user_id": current_user.get("oid"),
            "user_name": current_user.get("name")
        }
    )
```

## Environment Variables

Create a `.env` file:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com
AZURE_OPENAI_DEPLOYMENT=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_API_KEY=your-api-key

# Agent Configuration
AGENT_NAME=PythonSpecializedAgent
AGENT_INSTRUCTIONS=You are a specialized Python agent that helps with data analysis, machine learning, and Python ecosystem tasks.

# API Configuration
API_PORT=8000
API_HOST=0.0.0.0
REQUIRE_AUTH=false
```

## Development Commands

```bash
# Install/update dependencies
uv sync

# Run development server
uv run uvicorn src.main:app --reload

# Format code
uv run black src/
uv run ruff check src/ --fix

# Type checking
uv run mypy src/

# Run tests
uv run pytest

# Run specific test
uv run pytest tests/test_api.py -v

# Build for deployment
uv build
```

## Examples

The `examples/` folder contains sample implementations demonstrating different Agent Framework patterns:

### `agent_example.py`
Simple agent with Azure OpenAI Responses client. Shows basic agent creation and configuration.

```bash
# Run with devui
cd examples
python agent_example.py
```

### `workflow_simple_example.py`
Foundation workflow patterns showing:
- Custom executor classes vs function-based executors
- Workflow builder API (edges, start executor)
- Message passing between nodes
- Yielding workflow outputs

**Key concepts**:
- `UpperCase` executor (class-based)
- `reverse_text` executor (function-based)
- Sequential processing: uppercase → reverse

### `workflow_agent_example.py`
Multi-agent workflow coordination demonstrating:
- Writer and Reviewer agents working sequentially
- Agent-based executors in workflows
- Non-streaming workflow execution

**Example workflow**:
1. Writer agent creates/edits content
2. Reviewer agent evaluates and provides feedback
3. Workflow completes when idle

### Running Examples with DevUI

The Microsoft Agent Framework includes a visual workflow debugger:

```bash
# Autodiscover and visualize agents/workflows
uv run devui examples/ --port 8181

# Or run specific examples with built-in serve() calls
# (uncomment serve() line in the example file first)
python examples/workflow_agent_example.py
```

**Note**: Authenticate with `az login` before running examples.

## API Endpoints

### `GET /health`
Health check endpoint.

**Response**:
```json
{
  "status": "healthy"
}
```

### `GET /agent`
Agent status and feature information.

**Response**:
```json
{
  "message": "Microsoft Agent Framework enabled",
  "status": "healthy",
  "agent_type": "microsoft-agent-framework",
  "agent_name": "PythonSpecializedAgent",
  "features": {
    "tools": ["get_weather", "calculate", "search_files"],
    "workflows": ["document_processing", "concurrent_analysis"],
    "authentication": "Azure OpenAI with DefaultAzureCredential"
  }
}
```

### `POST /agent`
Main agent interaction endpoint with Microsoft Agent Framework.

**Request**:
```json
{
  "message": "What is the weather in Seattle?",
  "conversation_id": "optional-uuid",
  "metadata": {"request_id": "abc123"}
}
```

**Response**:
```json
{
  "message": "The weather in Seattle is partly cloudy with a temperature of 18°C (64°F)...",
  "status": "success",
  "agent_type": "microsoft-agent-framework",
  "conversation_id": "optional-uuid",
  "metadata": {"request_id": "abc123"}
}
```

### `POST /workflow/document`
Sequential document processing workflow.

**Request**:
```json
{
  "input": "Write about artificial intelligence",
  "workflow_params": {},
  "metadata": {}
}
```

**Response**:
```json
{
  "result": "Artificial Intelligence: A Comprehensive Overview\n\n[Generated and edited content...]",
  "status": "success",
  "workflow_type": "sequential-document-processing",
  "metadata": {"steps": ["writer", "editor"]}
}
```

### `POST /workflow/analysis`
Concurrent multi-perspective analysis workflow.

**Request**:
```json
{
  "input": "Cloud computing migration",
  "workflow_params": {},
  "metadata": {}
}
```

**Response**:
```json
{
  "result": "Multi-Perspective Analysis: Cloud computing migration\n\n=== Technical Perspective ===\n...\n\n=== Business Perspective ===\n...",
  "status": "success",
  "workflow_type": "concurrent-multi-perspective-analysis",
  "metadata": {
    "perspectives": ["technical", "business"],
    "execution": "parallel"
  }
}
```

## Security Notes

1. **Never commit** `.env` files or secrets to git
2. **Validate all tokens** before processing requests
3. **Use HTTPS** in production
4. **Implement rate limiting** for production deployments
5. **Log OBO exchanges** for audit trails (without exposing tokens)
6. **Set appropriate CORS** policies

## Implementation Roadmap

1. ✅ **Phase 1**: Basic FastAPI service with health checks
2. ✅ **Phase 2**: Microsoft Agent Framework integration
   - Azure OpenAI client with authentication
   - Function tools (weather, calculate, search)
   - Thread-based conversation management
3. ✅ **Phase 3**: Workflow orchestration
   - Sequential document processing
   - Concurrent multi-perspective analysis
4. ⏳ **Phase 4**: JWT validation and OBO authentication flow
5. ⏳ **Phase 5**: Production hardening and deployment

## Troubleshooting

### UV Installation Issues
```bash
# Verify UV is installed
uv --version

# Reinstall if needed
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Dependency Conflicts
```bash
# Clear UV cache
uv cache clean

# Recreate virtual environment
rm -rf .venv
uv sync
```

### Azure Authentication Issues
- Verify Azure AD app registration settings
- Check client secret hasn't expired
- Ensure correct tenant ID
- Verify API permissions are granted and admin consented

## References

- [UV Documentation](https://github.com/astral-sh/uv)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
- [MSAL Python](https://github.com/AzureAD/microsoft-authentication-library-for-python)
- [Azure Identity SDK](https://learn.microsoft.com/en-us/python/api/azure-identity/)
