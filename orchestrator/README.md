# Orchestrator Service - Microsoft Agent Framework POC

## Overview

The **Orchestrator Service** is the central component of this POC, demonstrating the **JWT On-Behalf-Of (OBO) authentication flow** for multi-agent orchestration. This service receives user requests, selects the appropriate sub-agent, exchanges JWT tokens using OBO flow, and delegates work while maintaining user identity and authorization context.

## 🎯 Core POC Functionality

This orchestrator demonstrates:

1. **JWT Token Validation**: Validates incoming user JWT tokens from the frontend
2. **Intelligent Agent Selection**: Analyzes user intent to select the best sub-agent (Python or .NET)
3. **OBO Token Exchange**: **THE CORE POC** - Exchanges user JWT for scoped OBO tokens for sub-agents
4. **Delegated Execution**: Calls sub-agents with OBO tokens, maintaining user context
5. **Response Aggregation**: Collects and returns sub-agent responses to the frontend

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Application                     │
│                  (Authenticated with JWT)                    │
└────────────────────────┬────────────────────────────────────┘
                         │ User JWT Token
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                  ORCHESTRATOR SERVICE                        │
│                  (This Service - Port 8001)                  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 1. JWT Validator                                     │  │
│  │    - Validates user token                            │  │
│  │    - Extracts user claims (oid, name, scopes)       │  │
│  └──────────────────────────────────────────────────────┘  │
│                         ↓                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 2. Agent Selector                                    │  │
│  │    - Analyzes message intent                         │  │
│  │    - Selects Python or .NET sub-agent               │  │
│  └──────────────────────────────────────────────────────┘  │
│                         ↓                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 3. OBO Token Service ⭐ CORE POC COMPONENT ⭐       │  │
│  │    - Receives user's JWT token                       │  │
│  │    - Calls MSAL: acquire_token_on_behalf_of()       │  │
│  │    - Requests scopes for target sub-agent            │  │
│  │    - Returns OBO token with user context             │  │
│  └──────────────────────────────────────────────────────┘  │
│                         ↓                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 4. Sub-Agent Client                                  │  │
│  │    - Calls sub-agent with OBO token                  │  │
│  │    - Passes token in Authorization header            │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────┬───────────────────────────────┬───────────────┘
             │ OBO Token (Python scopes)      │ OBO Token (.NET scopes)
             ↓                                ↓
┌────────────────────────┐        ┌────────────────────────┐
│  Python Sub-Agent      │        │  .NET Sub-Agent        │
│  (Port 8000)           │        │  (Port 5000)           │
│                        │        │                        │
│  - Validates OBO token │        │  - Validates OBO token │
│  - Executes with user  │        │  - Executes with user  │
│    identity preserved  │        │    identity preserved  │
└────────────────────────┘        └────────────────────────┘
```

## Technology Stack

- **Python**: 3.11+
- **Package Manager**: UV
- **Web Framework**: FastAPI + Uvicorn
- **Authentication**:
  - `msal` - MSAL Python for OBO flow
  - `python-jose[cryptography]` - JWT validation
  - `azure-identity` - Azure credential management
- **HTTP Client**: `httpx` - For calling sub-agents
- **Configuration**: `pydantic-settings`

## Project Structure

```
orchestrator/
├── README.md                    # This file
├── pyproject.toml              # UV project configuration
├── .python-version             # Python version
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry
│   ├── api.py                  # Main /agent endpoint ⭐
│   ├── auth.py                 # JWT validation & OBO flow ⭐⭐
│   ├── agent_selector.py       # Intent analysis & agent selection
│   ├── sub_agent_client.py     # Sub-agent HTTP client
│   ├── config.py               # Configuration management
│   └── models.py               # Pydantic models
├── tests/
│   ├── test_api.py
│   └── test_agent_selector.py
└── .env.example                # Environment template
```

## Getting Started

### Prerequisites

1. **Install UV**:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Start Sub-Agents** (in separate terminals):
   ```bash
   # Terminal 1: Python agent
   cd ../python-agent
   uv sync
   uv run uvicorn src.main:app --reload --port 8000

   # Terminal 2: .NET agent
   cd ../dotnet-agent
   dotnet run --project AgentService
   ```

### Installation & Setup

The project has already been initialized with the following structure and dependencies:

**Installed Packages:**
- `fastapi` (>=0.110.0) - Web framework
- `uvicorn[standard]` (>=0.27.0) - ASGI server
- `pydantic` (>=2.6.0) - Data validation
- `pydantic-settings` (>=2.1.0) - Configuration management
- `httpx` (>=0.27.0) - Async HTTP client for sub-agent calls
- `msal` (>=1.28.0) - MSAL Python for OBO flow ⭐
- `python-jose[cryptography]` (>=3.3.0) - JWT validation
- `azure-identity` (>=1.15.0) - Azure credential management

**Dev Dependencies:**
- `pytest` (>=8.0.0) - Testing framework
- `pytest-asyncio` (>=0.23.0) - Async test support
- `black` (>=24.0.0) - Code formatter
- `ruff` (>=0.2.0) - Linter
- `mypy` (>=1.8.0) - Type checker

To build and run:

```bash
# Navigate to orchestrator directory
cd orchestrator

# Install dependencies
uv sync

# Run the application
uv run uvicorn src.main:app --reload --port 3000
```

### Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env
# For TESTING without Azure AD, set:
REQUIRE_AUTH=false

# For PRODUCTION with Azure AD, set:
REQUIRE_AUTH=true
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-orchestrator-app-id
AZURE_CLIENT_SECRET=your-orchestrator-secret
JWT_AUDIENCE=api://your-orchestrator-api-id
JWT_ISSUER=https://login.microsoftonline.com/{tenant-id}/v2.0
PYTHON_AGENT_SCOPES=["api://python-agent-id/.default"]
DOTNET_AGENT_SCOPES=["api://dotnet-agent-id/.default"]
```

### Running the Orchestrator

```bash
# Development mode with auto-reload
uv run uvicorn src.main:app --reload --port 8001

# Production mode
uv run uvicorn src.main:app --host 0.0.0.0 --port 8001 --workers 4

# Or using Python directly
uv run python -m src.main
```

### Testing

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_agent_selector.py -v
```

## API Endpoints

### `POST /agent` ⭐ Main Orchestrator Endpoint

The primary endpoint demonstrating the complete OBO flow.

**Request**:
```json
{
  "message": "Help me with Python data analysis",
  "conversation_id": "optional-uuid",
  "preferred_agent": "auto",  // "auto", "python", or "dotnet"
  "metadata": {}
}
```

**Response**:
```json
{
  "message": "it's alive",
  "status": "success",
  "selected_agent": "python",
  "conversation_id": "optional-uuid",
  "sub_agent_responses": [
    {
      "agent_type": "python",
      "message": "it's alive",
      "status": "healthy",
      "metadata": {}
    }
  ],
  "metadata": {
    "user_id": "user-oid-from-jwt",
    "user_name": "John Doe",
    "auth_enabled": false,
    "obo_token_acquired": false
  }
}
```

**With Authentication** (when REQUIRE_AUTH=true):
```bash
curl -X POST http://localhost:8001/agent \
  -H "Authorization: Bearer YOUR_USER_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Help me analyze data with pandas",
    "preferred_agent": "auto"
  }'
```

**Without Authentication** (testing mode, REQUIRE_AUTH=false):
```bash
curl -X POST http://localhost:8001/agent \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Help me with C# and ASP.NET",
    "preferred_agent": "auto"
  }'
```

### `GET /agent`

Simple status check endpoint.

**Response**:
```json
{
  "message": "Orchestrator is alive",
  "status": "healthy",
  "service": "orchestrator",
  "auth_required": false
}
```

### `GET /health`

Health check for the orchestrator service.

**Response**:
```json
{
  "status": "healthy",
  "service": "orchestrator",
  "auth_required": false
}
```

### `GET /health/agents`

Check health of all sub-agents.

**Response**:
```json
{
  "orchestrator": "healthy",
  "sub_agents": {
    "python": "healthy",
    "dotnet": "healthy"
  }
}
```

### `GET /`

Root endpoint with service information.

**Response**:
```json
{
  "service": "Microsoft Agent Framework Orchestrator",
  "version": "0.1.0",
  "description": "Orchestrator service demonstrating JWT OBO flow with sub-agents",
  "endpoints": {
    "main": "POST /agent",
    "status": "GET /agent",
    "health": "GET /health",
    "sub_agent_health": "GET /health/agents"
  },
  "configuration": {
    "auth_required": false,
    "python_agent": "http://localhost:8000",
    "dotnet_agent": "http://localhost:5000"
  }
}
```

## OBO Flow Implementation Details

### The Complete OBO Flow (Step by Step)

**File: `src/auth.py`** - Core OBO implementation

```python
class OBOTokenService:
    async def acquire_token_on_behalf_of(
        self, user_token: str, scopes: list[str]
    ) -> Optional[str]:
        """
        THE CORE OF THE POC - JWT On-Behalf-Of Token Exchange

        What happens here:
        1. Frontend sends user's JWT (with user identity)
        2. Orchestrator validates this JWT
        3. Orchestrator calls Azure AD with:
           - user_assertion: The user's original JWT
           - scopes: The permissions needed for the sub-agent
        4. Azure AD validates:
           - The user's token is valid
           - The orchestrator is authorized to act on behalf of user
           - The requested scopes are permitted
        5. Azure AD returns new JWT token with:
           - Same user identity (oid, name, etc.)
           - Different audience (sub-agent API)
           - Different scopes (sub-agent permissions)
        6. Orchestrator passes this OBO token to sub-agent
        7. Sub-agent validates token and sees original user identity
        8. Sub-agent can now call APIs on behalf of the user with full RBAC
        """
        result = self.msal_app.acquire_token_on_behalf_of(
            user_assertion=user_token,
            scopes=scopes
        )
        return result["access_token"]
```

**File: `src/api.py`** - Using OBO in the endpoint

```python
@router.post("/agent")
async def orchestrator_endpoint(
    request: OrchestratorRequest,
    current_user: Dict = Depends(get_current_user),  # Validates user JWT
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    # Step 1: Get user's original JWT token
    user_token = credentials.credentials

    # Step 2: Select which sub-agent to call
    selected_agent = agent_selector.select_agent(
        request.message,
        request.preferred_agent
    )

    # Step 3: Determine required scopes for that sub-agent
    if selected_agent.value == "python":
        target_scopes = settings.PYTHON_AGENT_SCOPES  # ["api://python-agent/.default"]
    else:
        target_scopes = settings.DOTNET_AGENT_SCOPES  # ["api://dotnet-agent/.default"]

    # Step 4: Exchange user JWT for OBO token ⭐
    obo_token = await get_obo_token(user_token, target_scopes)

    # Step 5: Call sub-agent with OBO token
    response = await sub_agent_client.call_sub_agent(
        agent_type=selected_agent,
        message=request.message,
        obo_token=obo_token  # Pass OBO token to sub-agent
    )

    return response
```

**File: `src/sub_agent_client.py`** - Passing OBO token to sub-agent

```python
async def call_sub_agent(
    self,
    agent_type: AgentType,
    message: str,
    obo_token: Optional[str] = None,
):
    """Call sub-agent with OBO token in Authorization header."""

    headers = {"Content-Type": "application/json"}

    if obo_token:
        # Pass OBO token to sub-agent
        headers["Authorization"] = f"Bearer {obo_token}"

    # Sub-agent will validate this OBO token
    # and see the original user's identity
    response = await client.post(endpoint, json=payload, headers=headers)
    return response.json()
```

## Agent Selection Logic

The orchestrator intelligently selects sub-agents based on message content:

**File: `src/agent_selector.py`**

- **Python Keywords**: `python`, `pandas`, `numpy`, `data`, `analysis`, `fastapi`, `ml`, etc.
- **\.NET Keywords**: `.net`, `dotnet`, `c#`, `asp.net`, `entity framework`, `blazor`, etc.

**Examples**:
- "Help me with pandas dataframe" → Selects **Python** agent
- "I need help with ASP.NET Core" → Selects **.NET** agent
- "Generic question" → Defaults to **Python** agent
- Explicit preference overrides auto-selection

## Testing Without Azure AD

For local development and testing without setting up Azure AD:

**Set in `.env`**:
```bash
REQUIRE_AUTH=false
```

This will:
- Skip JWT validation
- Skip OBO token acquisition
- Use mock user identity
- Still call sub-agents (without auth headers)
- Allow you to test the orchestration flow

## Testing With Azure AD (Production Flow)

### Azure AD Setup Required

1. **Register 3 Azure AD Applications**:
   - **Orchestrator API** (this service)
   - **Python Agent API** (exposes scope `api://python-agent/.default`)
   - **.NET Agent API** (exposes scope `api://dotnet-agent/.default`)

2. **Configure API Permissions**:
   - Orchestrator needs permission to:
     - `api://python-agent/.default`
     - `api://dotnet-agent/.default`
   - Admin consent required

3. **Configure Application Settings**:
   ```bash
   REQUIRE_AUTH=true
   AZURE_TENANT_ID=your-tenant-id
   AZURE_CLIENT_ID=orchestrator-app-id
   AZURE_CLIENT_SECRET=orchestrator-secret
   JWT_AUDIENCE=api://orchestrator-app-id
   PYTHON_AGENT_SCOPES=["api://python-agent-id/.default"]
   DOTNET_AGENT_SCOPES=["api://dotnet-agent-id/.default"]
   ```

## Development Commands

```bash
# Install/update dependencies
uv sync

# Run development server
uv run uvicorn src.main:app --reload --port 3000

# Format code
uv run black src/
uv run ruff check src/ --fix

# Type checking
uv run mypy src/

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src --cov-report=html

# Check sub-agent health
curl http://localhost:8001/health/agents
```

## Example Usage Scenarios

### Scenario 1: Testing Without Auth (Local Development)

```bash
# 1. Start all services
# Terminal 1: Python agent (port 8000)
# Terminal 2: .NET agent (port 5000)
# Terminal 3: Orchestrator (port 8001)

# 2. Test orchestrator
curl -X POST http://localhost:8001/agent \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Help me with pandas",
    "preferred_agent": "auto"
  }'

# Response will show:
# - selected_agent: "python"
# - sub_agent called: Python agent
# - auth_enabled: false
```

### Scenario 2: Testing With Auth (Full OBO Flow)

```bash
# 1. Obtain user JWT from frontend authentication
USER_JWT="eyJ0eXAiOiJKV1QiLCJhbGc..."

# 2. Call orchestrator with user JWT
curl -X POST http://localhost:8001/agent \
  -H "Authorization: Bearer $USER_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Analyze this dataset with pandas",
    "preferred_agent": "auto"
  }'

# What happens:
# 1. Orchestrator validates USER_JWT
# 2. Orchestrator selects Python agent (pandas keyword)
# 3. Orchestrator exchanges USER_JWT for OBO token with Python scopes
# 4. Orchestrator calls Python agent with OBO token
# 5. Python agent validates OBO token, sees original user identity
# 6. Python agent executes and responds
# 7. Orchestrator returns aggregated response
```

### Scenario 3: Explicit Agent Selection

```bash
# Force .NET agent even with Python keywords
curl -X POST http://localhost:8001/agent \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Help me with pandas",
    "preferred_agent": "dotnet"
  }'

# Response will show:
# - selected_agent: "dotnet" (preference overrides intent)
```

## Key Files Explained

| File | Purpose |
|------|---------|
| `src/api.py` | Main orchestrator endpoint - coordinates the entire OBO flow |
| `src/auth.py` | **⭐ CORE POC** - JWT validation & OBO token acquisition using MSAL |
| `src/agent_selector.py` | Intent analysis to select Python or .NET sub-agent |
| `src/sub_agent_client.py` | HTTP client for calling sub-agents with OBO tokens |
| `src/config.py` | Configuration management (env vars, URLs, scopes) |
| `src/models.py` | Pydantic models for requests/responses |

## Security Considerations

1. **Token Handling**:
   - Never log full JWT tokens
   - Validate all tokens before use
   - Handle token expiration gracefully

2. **OBO Flow Security**:
   - Only request minimum required scopes
   - Validate that orchestrator has permission to request OBO tokens
   - Ensure sub-agents validate OBO tokens properly

3. **Network Security**:
   - Use HTTPS in production
   - Implement rate limiting
   - Add request timeouts

4. **Error Handling**:
   - Never expose token details in errors
   - Log security events for audit
   - Handle sub-agent failures gracefully

## Troubleshooting

### Sub-agents not reachable
```bash
# Check if sub-agents are running
curl http://localhost:8000/health  # Python agent
curl http://localhost:5000/health  # .NET agent

# Check orchestrator can reach them
curl http://localhost:3000/health/agents
```

### OBO token acquisition fails
- Verify Azure AD app registrations
- Check API permissions and admin consent
- Verify client secret hasn't expired
- Check scopes are correctly configured
- Ensure `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET` are correct

### JWT validation fails
- Verify `JWT_AUDIENCE` matches your orchestrator's App ID URI
- Verify `JWT_ISSUER` matches Azure AD tenant
- Check token hasn't expired
- Ensure frontend is requesting correct audience

## Next Steps

1. ✅ **Phase 1 Complete**: Orchestrator setup with OBO flow
2. ⏳ **Phase 2**: Integrate Microsoft Agent Framework for AI responses
3. ⏳ **Phase 3**: Add conversation state management
4. ⏳ **Phase 4**: Implement multi-agent collaboration (calling multiple sub-agents)
5. ⏳ **Phase 5**: Production hardening and monitoring

## References

- [Microsoft Identity Platform OBO Flow](https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-on-behalf-of-flow)
- [MSAL Python Documentation](https://github.com/AzureAD/microsoft-authentication-library-for-python)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
