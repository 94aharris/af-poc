# Python Agent Implementation - Microsoft Agent Framework POC

## Overview

This Python implementation demonstrates a FastAPI-based agent service using the Microsoft Agent Framework with JWT On-Behalf-Of (OBO) authentication flow.

## Technology Stack

- **Python**: 3.11+
- **Package Manager**: UV (ultra-fast Python package installer and resolver)
- **Web Framework**: FastAPI + Uvicorn
- **Agent Framework**: `agent-framework` (Microsoft Agent Framework - unified framework)
- **Agent Backends**:
  - Claude CLI (default) - Shell command integration
  - Local LLM via HTTP (Ollama support)
  - OpenAI-compatible APIs (LM Studio, vLLM, etc.)
- **Authentication**:
  - `msal` - Microsoft Authentication Library for Python (Phase 3)
  - `python-jose[cryptography]` - JWT validation (Phase 3)
  - `azure-identity` - Azure credential management
- **HTTP Client**: `httpx` - For async API calls
- **Validation**: `pydantic` - Data validation (built into FastAPI)

## Project Structure

```
python-agent/
├── README.md                   # This file
├── pyproject.toml             # UV project configuration & dependencies
├── .python-version            # Python version specification
├── src/
│   ├── __init__.py
│   ├── main.py               # FastAPI application entry point
│   ├── api.py                # API endpoints (/agent)
│   ├── agent.py              # Microsoft Agent Framework integration
│   ├── auth.py               # JWT validation & OBO flow
│   ├── config.py             # Configuration management
│   └── models.py             # Pydantic models for requests/responses
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   └── test_auth.py
└── .env.example              # Environment variable template
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
- `httpx` - Async HTTP client for local LLM integration

**Note:** Authentication packages (`msal`, `python-jose`) for OBO flow will be added in Phase 3.

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
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Test the /agent endpoint
curl http://localhost:8000/agent
# Expected response: {"message": "it's alive", "status": "healthy"}
```

## Implementation Details

### Phase 1: Basic API Endpoint (Current)

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

### Phase 2: Agent Framework Integration ✅ IMPLEMENTED

The agent now supports **multiple backend options** for flexibility:

**File: `src/agent.py`**
```python
import os
import json
import asyncio
from typing import Optional, Dict
import httpx
from src.config import settings

class AgentService:
    """Service for managing different agent backends."""

    def __init__(self):
        self.claude_sessions: Dict[str, str] = {}  # conversation_id -> session_id

    async def run_shell_agent(self, message: str, conversation_id: Optional[str] = None) -> str:
        """Run Claude Code in headless mode using the CLI (DEFAULT BACKEND)"""
        args = ["claude", "-p", "--output-format", "json"]

        session_id = self.claude_sessions.get(conversation_id) if conversation_id else None
        if session_id:
            args.extend(["--resume", session_id])

        process_env = os.environ.copy()

        process = await asyncio.create_subprocess_exec(
            *args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=process_env,
        )

        stdout, stderr = await process.communicate(input=message.encode())

        if process.returncode != 0:
            return f"Error invoking Claude: {stderr.decode().strip()}"

        try:
            payload = json.loads(stdout.decode())
            response_text = payload.get("result", "")

            if not response_text:
                response_text = stdout.decode().strip()

            # Store session for conversation continuity
            new_session = payload.get("session_id")
            if new_session and conversation_id:
                self.claude_sessions[conversation_id] = new_session
        except json.JSONDecodeError:
            response_text = stdout.decode().strip()

        return response_text

    async def run_local_llm_http(self, message: str, conversation_id: Optional[str] = None) -> str:
        """Call local LLM via HTTP (Ollama)"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "http://localhost:11434/api/generate",
                    json={"model": "llama2", "prompt": message, "stream": False}
                )
                response.raise_for_status()
                data = response.json()
                return data.get("response", "No response from local LLM")
        except httpx.ConnectError:
            return "Error: Could not connect to local LLM at http://localhost:11434"
        except Exception as e:
            return f"Error calling local LLM: {str(e)}"

    async def run_openai_compatible(self, message: str, conversation_id: Optional[str] = None) -> str:
        """Use OpenAI-compatible API (LM Studio, vLLM, etc.)"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "http://localhost:1234/v1/chat/completions",
                    json={
                        "model": "local-model",
                        "messages": [
                            {"role": "system", "content": settings.agent_instructions},
                            {"role": "user", "content": message}
                        ],
                        "temperature": 0.7,
                    },
                    headers={"Content-Type": "application/json"},
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except httpx.ConnectError:
            return "Error: Could not connect to OpenAI-compatible endpoint at http://localhost:1234"
        except Exception as e:
            return f"Error calling OpenAI-compatible API: {str(e)}"

    async def run_agent(self, message: str, conversation_id: Optional[str] = None) -> str:
        """Main entry point - currently uses Claude CLI backend"""
        return await self.run_shell_agent(message, conversation_id)
```

**Backend Switching**: Change line 184 in `src/agent.py`:
- `return await self.run_shell_agent(message, conversation_id)` ← **Current (Claude CLI)**
- `return await self.run_local_llm_http(message, conversation_id)`
- `return await self.run_openai_compatible(message, conversation_id)`

**File: `src/config.py`**
```python
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Azure OpenAI Configuration
    azure_openai_endpoint: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    azure_openai_deployment: str = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4")
    azure_openai_api_version: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    azure_openai_api_key: str = os.getenv("AZURE_OPENAI_API_KEY", "")

    # Agent Configuration
    agent_name: str = os.getenv("AGENT_NAME", "PythonSpecializedAgent")
    agent_instructions: str = os.getenv(
        "AGENT_INSTRUCTIONS",
        "You are a specialized Python agent that helps with data analysis, machine learning, and Python ecosystem tasks.",
    )

    # API Configuration
    api_port: int = int(os.getenv("API_PORT", "8000"))
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    require_auth: bool = os.getenv("REQUIRE_AUTH", "false").lower() == "true"

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields in .env file

settings = Settings()
```

### Phase 3: JWT Validation & OBO Flow

**File: `src/auth.py`**
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

### Phase 4: Full Integration

**Updated `src/api.py` with authentication**
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
Simple agent status check (Phase 1).

**Response**:
```json
{
  "message": "it's alive",
  "status": "healthy"
}
```

### `POST /agent`
Main agent interaction endpoint.

**Request**:
```json
{
  "message": "Hello, I need help with Python",
  "conversation_id": "optional-uuid",
  "metadata": {}
}
```

**Response**:
```json
{
  "message": "it's alive",
  "status": "healthy",
  "agent_type": "python-fastapi",
  "conversation_id": "optional-uuid",
  "metadata": {}
}
```

**With Authentication (Phase 4)**:
```bash
curl -X POST http://localhost:8000/agent \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Help me with Python"}'
```

## Security Notes

1. **Never commit** `.env` files or secrets to git
2. **Validate all tokens** before processing requests
3. **Use HTTPS** in production
4. **Implement rate limiting** for production deployments
5. **Log OBO exchanges** for audit trails (without exposing tokens)
6. **Set appropriate CORS** policies

## Next Steps

1. ✅ Phase 1: Basic `/agent` endpoint returning "it's alive"
2. ✅ Phase 2: Integrate Microsoft Agent Framework with multiple backend options
   - ✅ Claude CLI integration (shell command)
   - ✅ Local LLM HTTP support (Ollama)
   - ✅ OpenAI-compatible API support (LM Studio, etc.)
3. ⏳ Phase 3: Implement JWT validation and OBO flow
4. ⏳ Phase 4: Full multi-agent orchestration
5. ⏳ Phase 5: Production hardening and deployment

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
