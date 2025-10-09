# Orchestrator Service - Microsoft Agent Framework POC

## Overview

The **Orchestrator Service** is the central component of this POC, demonstrating:
1. **Microsoft Agent Framework Integration** - AI-powered orchestration with intelligent tool use
2. **JWT On-Behalf-Of (OBO) Authentication Flow** - Secure token exchange for multi-service access
3. **Payroll API Integration** - Secure access to user payroll data with OBO tokens
4. **Sub-Agent Delegation** - Routes specialized tasks to domain-specific agents

This service receives user requests, uses an AI agent to determine what tools/services are needed, exchanges JWT tokens using OBO flow for secure API access, and orchestrates responses while maintaining user identity and authorization context.

## 🎯 Core POC Functionality

This orchestrator demonstrates:

1. **Microsoft Agent Framework**: AI agent with specialized tools for intelligent task execution
2. **JWT Token Validation**: Validates incoming user JWT tokens from the frontend
3. **OBO Token Exchange**: **THE CORE POC** - Exchanges user JWT for scoped OBO tokens for downstream services
4. **Payroll API Tools**: Secure access to user information and PTO data via OBO authentication
5. **Calculator Tool**: Delegates mathematics questions to specialized Python agent

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
- **AI/Agent Framework**:
  - `agent-framework` - Microsoft Agent Framework for intelligent tool use
  - **Azure OpenAI** - LLM for agent reasoning
- **Authentication**:
  - `msal` - MSAL Python for OBO flow
  - `python-jose[cryptography]` - JWT validation
  - `azure-identity` - Azure credential management
- **HTTP Client**: `httpx` - For calling downstream services and APIs
- **Configuration**: `pydantic-settings`

## Project Structure

```
orchestrator/
├── README.md                       # This file
├── pyproject.toml                 # UV project configuration
├── .python-version                # Python version
├── docs/                          # Documentation folder
│   ├── AZURE_AD_SETUP.md          # Azure AD setup guide
│   ├── OBO_SETUP_INDEX.md         # OBO setup index
│   └── ... (other setup guides)
├── src/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry
│   ├── api.py                     # API endpoints ⭐
│   ├── agent_framework_impl.py    # Agent Framework integration ⭐⭐
│   ├── auth.py                    # JWT validation & OBO flow ⭐⭐
│   ├── constants.py               # Application constants
│   ├── agent_selector.py          # Intent analysis (optional)
│   ├── sub_agent_client.py        # Sub-agent HTTP client (optional)
│   ├── audit.py                   # Audit logging
│   ├── authorization.py           # Authorization service
│   ├── intelligent_routing.py     # Claude-based routing (optional)
│   ├── config.py                  # Configuration management
│   └── models.py                  # Pydantic models
├── tests/
│   ├── test_api.py
│   └── test_agent_selector.py
└── .env.example                   # Environment template
```

## Getting Started

### Prerequisites

1. **Install UV**:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Azure OpenAI Setup** (Required for Agent Framework):
   - Create an Azure OpenAI resource in Azure Portal
   - Deploy a model (e.g., gpt-4, gpt-4o)
   - Get your endpoint, deployment name, and API key
   - See [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)

3. **Monitoring Setup** (Optional - see [Monitoring & Observability](#monitoring--observability) section):
   ```bash
   # Start the monitoring stack (Jaeger, Grafana, Prometheus, Tempo)
   make monitoring-up
   ```

   **Alternative**: If running locally in VS Code, you can use the **AI Toolkit extension** for trace visualization instead of the full monitoring stack.

4. **Start Required Services** (in separate terminals):
   ```bash
   # Terminal 1: Python agent (for calculator tool)
   cd ../python-agent
   uv sync
   uv run uvicorn src.main:app --reload --port 8000

   # Terminal 2: Payroll API (for user info/PTO tools)
   cd ../dotnet-payroll-api
   dotnet run --project PayrollApi

   # Terminal 3 (optional): .NET agent (for legacy endpoint)
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
- `httpx` (>=0.27.0) - Async HTTP client for API calls
- `msal` (>=1.28.0) - MSAL Python for OBO flow ⭐
- `python-jose[cryptography]` (>=3.3.0) - JWT validation
- `azure-identity` (>=1.15.0) - Azure credential management
- `agent-framework` - Microsoft Agent Framework ⭐⭐ NEW

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
uv run uvicorn src.main:app --reload --port 8001
```

### Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
```

**Required Configuration (Azure OpenAI for Agent Framework)**:
```bash
# Azure OpenAI Configuration - REQUIRED for Agent Framework
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4
AZURE_OPENAI_API_KEY=your-api-key
```

**For TESTING without Azure AD Authentication**:
```bash
REQUIRE_AUTH=false
```

**For PRODUCTION with Azure AD Authentication**:
```bash
REQUIRE_AUTH=true
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-orchestrator-app-id
AZURE_CLIENT_SECRET=your-orchestrator-secret
JWT_AUDIENCE=api://your-orchestrator-api-id
JWT_ISSUER=https://login.microsoftonline.com/{tenant-id}/v2.0
PYTHON_AGENT_SCOPES=["api://python-agent-id/.default"]
DOTNET_AGENT_SCOPES=["api://dotnet-agent-id/.default"]
PAYROLL_API_SCOPES=["api://payroll-api-id/.default"]
```

**Service Endpoints**:
```bash
PYTHON_AGENT_URL=http://localhost:8000
DOTNET_AGENT_URL=http://localhost:5000
PAYROLL_API_URL=http://localhost:5100
```

**Monitoring & Observability** (Optional):
```bash
# Enable OpenTelemetry tracing and metrics
ENABLE_OTEL=true
# Enable logging of sensitive data (prompts, responses, function arguments)
ENABLE_SENSITIVE_DATA=false  # Set to true with caution
# OTLP endpoint for telemetry export (OpenTelemetry Collector)
OTLP_ENDPOINT=http://localhost:4317
# VS Code AI Toolkit extension port (for local development)
VS_CODE_EXTENSION_PORT=4317
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

### `POST /agent` ⭐ Microsoft Agent Framework Endpoint (Primary)

The primary endpoint using Microsoft Agent Framework with intelligent tool use and OBO authentication.

This endpoint uses an AI agent that intelligently selects and uses tools based on user requests:
- **get_user_info**: Retrieves user payroll information from Payroll API (with OBO)
- **get_user_pto**: Retrieves PTO balance and history from Payroll API (with OBO)
- **calculate**: Delegates mathematical calculations to Python agent (with OBO)

**Request**:
```json
{
  "message": "What is my current PTO balance?",
  "conversation_id": "optional-uuid",
  "metadata": {}
}
```

**Response**:
```json
{
  "message": "Based on the payroll system, you have 120 hours of PTO available. You've accrued 160 hours this year and used 40 hours. You also have 8 hours in pending requests.",
  "status": "success",
  "selected_agent": "agent-framework",
  "conversation_id": "optional-uuid",
  "metadata": {
    "user_id": "user-oid-from-jwt",
    "user_name": "Alice Johnson",
    "response_time_ms": 1523.45,
    "agent_type": "microsoft-agent-framework"
  }
}
```

**Example Requests**:

**1. Get User Information** (calls payroll API):
```bash
curl -X POST http://localhost:8001/agent \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is my employee information?"
  }'
```

**2. Get PTO Balance** (calls payroll API):
```bash
curl -X POST http://localhost:8001/agent \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How much PTO do I have?"
  }'
```

**3. Calculate** (routes to python-agent):
```bash
curl -X POST http://localhost:8001/agent \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is 1234 times 5678?"
  }'
```

**4. With Authentication** (when REQUIRE_AUTH=true):
```bash
curl -X POST http://localhost:8001/agent \
  -H "Authorization: Bearer YOUR_USER_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me my PTO information and calculate my remaining days at 8 hours per day"
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
  "auth_required": false,
  "agent_framework_available": true
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

## Microsoft Agent Framework Implementation

### Agent Framework with Tools

**File: `src/agent_framework_impl.py`** - Agent Framework integration

The orchestrator uses Microsoft Agent Framework to create an intelligent AI agent with access to specialized tools:

```python
class AgentFrameworkService:
    """Service for managing Microsoft Agent Framework agents."""

    def _get_agent_tools(self):
        """Get the list of tools available to the agent."""
        return [
            self.get_user_info,      # Payroll API: User information
            self.get_user_pto,       # Payroll API: PTO data
            self.calculate,          # Python Agent: Calculations
        ]
```

### Tool 1: Get User Info (Payroll API with OBO)

```python
async def get_user_info(self) -> str:
    """Get user's payroll information from the payroll API.

    Retrieves:
    - Name, Email, Department
    - Employee ID, Job Title
    - Manager name, Hire date

    Requires OBO authentication.
    """
    # Exchange user JWT for OBO token with payroll scopes
    obo_token = await get_obo_token(
        self._current_user_token,
        settings.PAYROLL_API_SCOPES
    )

    # Call payroll API with OBO token
    response = await self.http_client.get(
        f"{settings.PAYROLL_API_URL}/payroll/user-info",
        headers={"Authorization": f"Bearer {obo_token}"}
    )
```

### Tool 2: Get User PTO (Payroll API with OBO)

```python
async def get_user_pto(self) -> str:
    """Get user's PTO balance and history.

    Retrieves:
    - Current balance, accrued, used
    - Pending requests
    - Upcoming PTO schedule

    Requires OBO authentication.
    """
    # Exchange for OBO token
    obo_token = await get_obo_token(
        self._current_user_token,
        settings.PAYROLL_API_SCOPES
    )

    # Call payroll API
    response = await self.http_client.get(
        f"{settings.PAYROLL_API_URL}/payroll/user-pto",
        headers={"Authorization": f"Bearer {obo_token}"}
    )
```

### Tool 3: Calculate (Python Agent with OBO)

```python
async def calculate(self, expression: str) -> str:
    """Delegate mathematical calculations to Python agent.

    Routes mathematics to specialized python-agent with:
    - Mathematical calculations
    - Data analysis
    - Statistical operations

    Requires OBO authentication.
    """
    # Exchange for OBO token with python agent scopes
    obo_token = await get_obo_token(
        self._current_user_token,
        settings.PYTHON_AGENT_SCOPES
    )

    # Call python-agent
    response = await self.http_client.post(
        f"{settings.PYTHON_AGENT_URL}/agent",
        json={"message": f"Please calculate: {expression}"},
        headers={"Authorization": f"Bearer {obo_token}"}
    )
```

### How the Agent Works

1. **User sends message** to `POST /agent`
2. **AI Agent analyzes** the request using Azure OpenAI
3. **Agent selects tool(s)** based on request intent:
   - "What's my PTO?" → `get_user_pto` tool
   - "Who is my manager?" → `get_user_info` tool
   - "Calculate 5 * 10" → `calculate` tool
4. **Tool executes with OBO**:
   - Gets user's JWT token
   - Exchanges for OBO token with appropriate scopes
   - Calls downstream API/agent with OBO token
5. **Agent synthesizes response** from tool results
6. **Returns natural language** answer to user

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
uv run uvicorn src.main:app --reload --port 8001

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

### Scenario 1: Agent Framework - Payroll Information

```bash
# Start required services (in separate terminals)
cd orchestrator && uv run uvicorn src.main:app --reload --port 8001    # Terminal 1
cd dotnet-payroll-api && dotnet run --project PayrollApi               # Terminal 2

# Query user information
curl -X POST http://localhost:8001/agent \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is my current job title and department?"
  }'

# Response (AI agent uses get_user_info tool):
# "Based on your payroll information, you are a Senior Software Engineer
#  in the Engineering department. You report to Sarah Williams and have
#  been with the company since January 15, 2020."
```

### Scenario 2: Agent Framework - PTO Balance

```bash
# Query PTO balance
curl -X POST http://localhost:8001/agent \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How many vacation days do I have left?"
  }'

# Response (AI agent uses get_user_pto tool):
# "You currently have 120 hours (15 days) of PTO available. This year
#  you've accrued 160 hours and used 40 hours. You also have one pending
#  request for 8 hours."
```

### Scenario 3: Agent Framework - Calculations

```bash
# Start python-agent for calculator (in addition to orchestrator)
cd python-agent && uv run uvicorn src.main:app --reload --port 8000    # Terminal 3

# Mathematical calculation
curl -X POST http://localhost:8001/agent \
  -H "Content-Type: application/json" \
  -d '{
    "message": "If I have 120 hours of PTO and take 8 hours per day, how many days is that?"
  }'

# Response (AI agent uses calculate tool):
# "120 hours of PTO divided by 8 hours per day equals 15 days."
```

### Scenario 4: Agent Framework - Multi-Tool Request

```bash
# Complex query using multiple tools
curl -X POST http://localhost:8001/agent \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me my PTO balance and calculate how many days that is at 8 hours per day"
  }'

# Response (AI agent uses get_user_pto + calculate tools):
# "You have 120 hours of PTO available. At 8 hours per day, that equals
#  15 vacation days. You've used 40 hours (5 days) so far this year."
```

### Scenario 5: Testing With Auth (Full OBO Flow)

```bash
# 1. Obtain user JWT from frontend authentication
USER_JWT="eyJ0eXAiOiJKV1QiLCJhbGc..."

# 2. Call orchestrator with user JWT
curl -X POST http://localhost:8001/agent \
  -H "Authorization: Bearer $USER_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is my PTO balance?",
  }'

# What happens:
# 1. Orchestrator validates USER_JWT
# 2. AI Agent analyzes message, selects get_user_pto tool
# 3. Tool exchanges USER_JWT for OBO token with Payroll API scopes
# 4. Tool calls Payroll API with OBO token
# 5. Payroll API validates OBO token, sees original user identity
# 6. Payroll API returns user-specific PTO data (RBAC enforced)
# 7. AI Agent synthesizes natural language response
# 8. Orchestrator returns response to user
```

## Key Files Explained

| File | Purpose |
|------|---------|
| `src/api.py` | API endpoints - Agent Framework orchestration |
| `src/agent_framework_impl.py` | **⭐** Microsoft Agent Framework with OBO-secured tools |
| `src/auth.py` | **⭐ CORE POC** - JWT validation & OBO token acquisition using MSAL |
| `src/constants.py` | Application constants (test user values, etc.) |
| `src/agent_selector.py` | Intent analysis (optional, for advanced routing) |
| `src/sub_agent_client.py` | HTTP client for sub-agent calls (optional) |
| `src/audit.py` | Audit logging for security events |
| `src/authorization.py` | Role-based access control |
| `src/config.py` | Configuration management (env vars, URLs, scopes) |
| `src/models.py` | Pydantic models for requests/responses |
| `src/intelligent_routing.py` | Claude-based intelligent routing (optional) |

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
curl http://localhost:5100/health  # Payroll API

# Check orchestrator can reach them
curl http://localhost:8001/health/agents
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

## Monitoring & Observability

The orchestrator includes comprehensive OpenTelemetry instrumentation for traces and metrics. You have **two options** for viewing telemetry:

### Option 1: Full Monitoring Stack (Recommended for Teams)

The `monitoring/` directory contains a complete observability stack with Docker Compose:

- **Jaeger UI** - Dedicated trace visualization (http://localhost:16686)
- **Grafana** - Dashboards and metrics (http://localhost:3001)
- **Tempo** - Distributed tracing backend
- **Prometheus** - Metrics storage
- **OpenTelemetry Collector** - Telemetry ingestion

**Quick Start:**
```bash
# Start the full monitoring stack
make monitoring-up

# Configure orchestrator to send telemetry
# In orchestrator/.env:
ENABLE_OTEL=true
OTLP_ENDPOINT=http://localhost:4317
ENABLE_SENSITIVE_DATA=false

# Restart orchestrator
make run-orchestrator

# Access trace viewers
# Jaeger UI: http://localhost:16686 (recommended for trace exploration)
# Grafana: http://localhost:3001 (login: admin/admin)
```

**What Gets Monitored:**
- `invoke_agent <agent_name>` - Agent invocation operations
- `chat <model_name>` - LLM chat completions
- `execute_tool <function_name>` - Tool executions (get_user_info, get_user_pto, calculate)
- Token usage (prompt, completion, total)
- Operation duration and success/error rates

**Available Commands:**
```bash
make monitoring-up         # Start the monitoring stack
make monitoring-down       # Stop the monitoring stack
make monitoring-restart    # Restart the monitoring stack
make monitoring-logs       # View logs from all monitoring containers
make monitoring-status     # Check status of monitoring containers
make monitoring-clean      # Remove stack and all data volumes
```

See [monitoring/README.md](../monitoring/README.md) for complete documentation.

### Option 2: VS Code AI Toolkit Extension (For Local Development)

If you're running the orchestrator locally in **VS Code**, you can use the **AI Toolkit extension** for lightweight trace visualization without Docker:

1. **Install the AI Toolkit extension** in VS Code
2. **Configure orchestrator** to send traces to the extension:
   ```bash
   # In orchestrator/.env:
   ENABLE_OTEL=true
   OTLP_ENDPOINT=http://localhost:4317
   VS_CODE_EXTENSION_PORT=4317
   ```
3. **Open AI Toolkit panel** in VS Code to view traces in real-time

**When to use each option:**
- **VS Code AI Toolkit**: Solo development, quick debugging, minimal setup
- **Full Monitoring Stack**: Team environments, production-like monitoring, historical analysis, dashboards

### Telemetry Configuration

**Environment Variables:**
```bash
# Enable/disable OpenTelemetry instrumentation
ENABLE_OTEL=true

# Log prompts, responses, and function arguments (use with caution in production)
ENABLE_SENSITIVE_DATA=false

# OTLP endpoint for the collector or VS Code extension
OTLP_ENDPOINT=http://localhost:4317

# Azure Application Insights (optional, for cloud export)
APPLICATIONINSIGHTS_CONNECTION_STRING=
```

**Custom Instrumentation:**

You can add custom spans and metrics in your code:

```python
from agent_framework.observability import get_tracer, get_meter

tracer = get_tracer()
meter = get_meter()

# Custom span
with tracer.start_as_current_span("my_custom_operation"):
    # Your code here
    pass

# Custom counter
counter = meter.create_counter("my_custom_counter")
counter.add(1, {"operation": "process_request"})
```

**Troubleshooting:**

If telemetry isn't appearing:
1. Check `ENABLE_OTEL=true` in `.env`
2. Verify monitoring stack is running: `make monitoring-status`
3. Check collector logs: `make monitoring-logs`
4. Ensure orchestrator restarted after config changes

## Feature Highlights

### ✅ Implemented Features

1. **Microsoft Agent Framework Integration**
   - AI-powered agent with Azure OpenAI
   - Intelligent tool selection based on user requests
   - Thread-based conversation management
   - Three specialized tools with OBO authentication

2. **OBO Authentication Flow**
   - JWT validation for user identity
   - MSAL-based token exchange
   - Scope-based access control
   - Support for multiple downstream services

3. **Payroll API Integration**
   - Secure user information retrieval
   - PTO balance and history
   - User-scoped data access with OBO tokens

4. **Calculator Tool**
   - Delegates mathematics to Python agent
   - Maintains user context via OBO

### 🚀 Potential Enhancements

1. **Advanced Agent Capabilities**
   - Streaming responses for real-time feedback
   - Multi-tool orchestration (parallel tool execution)
   - Context-aware follow-up questions

2. **Additional Tools**
   - Calendar integration (schedule PTO)
   - Email notifications
   - Document generation
   - Database queries

3. **Production Hardening**
   - Rate limiting
   - Caching layer for API responses
   - Comprehensive error handling
   - Performance monitoring

4. **Enterprise Features**
   - Role-based tool access
   - Audit logging enhancement
   - Compliance reporting
   - Multi-tenant support

## References

- [Microsoft Identity Platform OBO Flow](https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-on-behalf-of-flow)
- [MSAL Python Documentation](https://github.com/AzureAD/microsoft-authentication-library-for-python)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
