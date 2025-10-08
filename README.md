# Microsoft Agent Framework POC - Multi-Agent Orchestration with JWT OBO

## Project Overview

This proof-of-concept demonstrates the Microsoft Agent Framework capabilities across Python and .NET implementations, with a specific focus on JWT On-Behalf-Of (OBO) authentication flow for secure, delegated API access.

**Repository**: https://github.com/microsoft/agent-framework

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│            Frontend (Next.js + assistant-ui)                 │
│                     (Port 3000)                              │
│  - User authentication & JWT acquisition                     │
│  - Chat interface with streaming support                     │
│  - ExternalStoreRuntime for backend integration              │
└────────────────────┬────────────────────────────────────────┘
                     │ User JWT Token
                     ↓
┌─────────────────────────────────────────────────────────────┐
│         ORCHESTRATOR SERVICE (Python/FastAPI - Port 3000)    │
│                                                              │
│  1. JWT Validator - Validates user token                    │
│  2. Agent Selector - Analyzes intent (Python vs .NET)       │
│  3. OBO Token Service ⭐ - Exchanges JWT for OBO tokens     │
│  4. Sub-Agent Client - Delegates work to sub-agents         │
└────────┬───────────────────────────────┬─────────────────────┘
         │ OBO Token (Python scopes)      │ OBO Token (.NET scopes)
         ↓                                ↓
┌────────────────────┐              ┌────────────────────────┐
│  Python Sub-Agent  │              │  .NET Sub-Agent        │
│  (Port 8000)       │              │  (Port 5000)           │
│                    │              │                        │
│  - Data analysis   │              │  - System integration  │
│  - ML/AI tasks     │              │  - Enterprise APIs     │
│  - Python ecosystem│              │  - Microsoft stack     │
│  - Validates OBO   │              │  - Validates OBO       │
│  - Calls APIs as   │              │  - Calls APIs as       │
│    original user   │              │    original user       │
└────────────────────┘              └──────────┬─────────────┘
                                               │ OBO Token
                                               ↓
                                    ┌──────────────────────────┐
                                    │  Payroll API (Port 5100) │
                                    │  - User-specific data    │
                                    │  - JWT authentication    │
                                    │  - Authorization checks  │
                                    │  - Audit logging         │
                                    └──────────────────────────┘
```

## Core Requirements

1. **Multi-Agent Orchestration**: Single orchestrator delegates to specialized agents
2. **JWT OBO Flow**: Secure token exchange maintaining user identity across agent calls
3. **Cross-Platform**: Demonstrate functionality in both Python and .NET
4. **AAA & RBAC**: Full authentication, authorization, and access control
5. **API Endpoint**: Each agent exposes `/agent` endpoint for communication

## Key Features

### Agent Framework Capabilities
- **Graph-based Workflows**: Connect agents with data flow pipelines
- **Multi-Language Support**: Consistent APIs across Python and .NET
- **Built-in Observability**: OpenTelemetry integration
- **Flexible Middleware**: Request/response processing
- **Credential Management**: Azure identity integration

### JWT On-Behalf-Of (OBO) Flow
- **Token Delegation**: Orchestrator exchanges user JWT for delegated access tokens
- **Identity Preservation**: Sub-agents call APIs maintaining original user context
- **Security Boundaries**: Each agent validates and processes tokens independently
- **.NET Implementation**: MSAL.NET `AcquireTokenOnBehalfOf` method
- **Python Implementation**: Manual OAuth2 flows or MSAL Python library

## Project Structure

```
af-poc/
├── README.md                           # This file - overall project plan
│
├── frontend/                           # 🎨 Frontend (Port 3000)
│   ├── README.md                      # Frontend documentation
│   ├── package.json                   # npm dependencies
│   ├── app/
│   │   ├── page.tsx                  # Main chat page
│   │   └── layout.tsx                # Root layout
│   ├── components/
│   │   ├── chat/
│   │   │   └── ChatInterface.tsx     # Custom chat component
│   │   └── assistant-ui/             # UI components from assistant-ui
│   ├── lib/
│   │   ├── api-client.ts             # Backend API client with JWT
│   │   ├── runtime.ts                # Custom ExternalStoreRuntime
│   │   ├── auth.ts                   # Token management utilities
│   │   └── utils.ts                  # Helper functions
│   └── .env.local                    # Environment variables
│
├── orchestrator/                       # ⭐ ORCHESTRATOR SERVICE (Port 3000)
│   ├── README.md                      # Orchestrator implementation details
│   ├── pyproject.toml                 # UV configuration
│   ├── src/
│   │   ├── main.py                   # FastAPI application
│   │   ├── api.py                    # Main /agent endpoint
│   │   ├── auth.py                   # JWT validation & OBO flow ⭐⭐
│   │   ├── agent_selector.py         # Intent analysis
│   │   ├── sub_agent_client.py       # Sub-agent HTTP client
│   │   ├── config.py                 # Configuration
│   │   └── models.py                 # Request/response models
│   └── tests/
│
├── python-agent/                       # Python Sub-Agent (Port 8000)
│   ├── README.md                      # Python-specific plan & details
│   ├── pyproject.toml                 # UV project configuration
│   ├── src/
│   │   ├── main.py                   # FastAPI application
│   │   ├── api.py                    # /agent endpoint
│   │   ├── models.py                 # Data models
│   │   └── (future: agent.py, auth.py for Phase 2+)
│   └── tests/
│
├── dotnet-agent/                       # .NET Sub-Agent (Port 5000)
│   ├── README.md                      # .NET-specific plan & details
│   ├── AgentService.sln               # Solution file
│   ├── AgentService/
│   │   ├── Program.cs                # ASP.NET Core setup
│   │   ├── Controllers/
│   │   │   └── AgentController.cs    # /agent endpoint
│   │   ├── Models/
│   │   │   ├── AgentRequest.cs
│   │   │   └── AgentResponse.cs
│   │   ├── Services/
│   │   │   ├── IAgentService.cs
│   │   │   └── AgentService.cs
│   │   └── AgentService.csproj
│   └── (future: tests/)
│
└── dotnet-payroll-api/                 # 🔒 Payroll API (Port 5100)
    ├── README.md                      # Payroll API documentation
    ├── PayrollApi.sln                 # Solution file
    ├── PayrollApi/
    │   ├── Program.cs                # ASP.NET Core setup with JWT auth
    │   ├── appsettings.json          # Configuration
    │   ├── Controllers/
    │   │   └── PayrollController.cs  # /payroll/user-info & /payroll/user-pto
    │   ├── Models/
    │   │   ├── UserInfo.cs           # User information model
    │   │   ├── UserPto.cs            # PTO balance model
    │   │   └── ErrorResponse.cs      # Error response model
    │   ├── Services/
    │   │   ├── IPayrollDataService.cs
    │   │   └── PayrollDataService.cs # Hardcoded test data
    │   └── PayrollApi.csproj
    └── (future: tests/)
```

## Implementation Phases

### Phase 1: Basic Setup ✅ COMPLETE
- [x] Research Microsoft Agent Framework
- [x] Research JWT OBO patterns
- [x] Create project structure (orchestrator + 2 sub-agents)
- [x] Initialize Python agent with UV (venv + dependencies)
- [x] Initialize .NET agent with dotnet CLI
- [x] Initialize orchestrator service with UV
- [x] Implement orchestrator with OBO flow
- [x] Implement basic `/agent` endpoint in Python
- [x] Implement basic `/agent` endpoint in .NET (returns "it's alive")
- [x] Implement agent selection logic
- [x] Implement sub-agent delegation
- [x] **Integrate Microsoft Agent Framework with Python agent**
- [x] **Add multiple backend support (Claude CLI, Ollama, OpenAI-compatible)**
- [x] **Configure conversation session management**

### Phase 2: Testing the OBO Flow (Current Phase)
- [ ] Configure Azure AD application registrations (3 apps)
- [ ] Test orchestrator → Python agent flow with OBO
- [ ] Test orchestrator → .NET agent flow with OBO
- [ ] Verify user identity preservation across all hops
- [ ] Test without authentication (REQUIRE_AUTH=false)
- [ ] Test with authentication (REQUIRE_AUTH=true)

### Phase 3: Agent Framework Integration
- [ ] Add Azure OpenAI clients to orchestrator
- [ ] Add Agent Framework to Python sub-agent
- [ ] Add Agent Framework to .NET sub-agent
- [ ] Replace "it's alive" with actual AI responses
- [ ] Test AI-powered responses through OBO flow

### Phase 4: Advanced Orchestration
- [ ] Implement conversation state management
- [ ] Add support for calling multiple sub-agents in one request
- [ ] Implement agent-to-agent communication
- [ ] Add graph-based workflow capabilities
- [ ] Implement retry and fallback logic

### Phase 5: Production Hardening
- [ ] Add comprehensive error handling
- [ ] Implement request rate limiting
- [ ] Add observability (OpenTelemetry, logging)
- [ ] Security hardening (CORS, validation, timeouts)
- [ ] Create deployment configurations
- [ ] Add monitoring and alerting

### Phase 6: Frontend Integration ✅ COMPLETE
- [x] Create Next.js frontend with assistant-ui
- [x] Implement ExternalStoreRuntime for backend integration
- [x] Add JWT token management utilities
- [x] Build chat interface with streaming support
- [x] Create API client with token injection
- [ ] Connect to orchestrator service
- [ ] Implement user authentication flow (Azure AD)
- [ ] Display multi-agent conversation flow
- [ ] Show which sub-agent handled each request

### Phase 7: Payroll API Integration ✅ COMPLETE
- [x] Create secure payroll API with JWT authentication
- [x] Implement user-specific data endpoints
- [x] Add authorization checks (oid claim validation)
- [x] Hardcode test data for 5 users
- [x] Add audit logging for security events
- [ ] Integrate with .NET agent
- [ ] Test full OBO flow: Frontend → Orchestrator → .NET Agent → Payroll API
- [ ] Verify user identity preserved throughout chain

## Technology Stack

### Frontend
- **Framework**: Next.js 15+ (React 19)
- **UI Library**: [assistant-ui](https://github.com/assistant-ui/assistant-ui)
- **Runtime**: ExternalStoreRuntime for custom backend integration
- **Styling**: Tailwind CSS
- **Language**: TypeScript
- **Features**: Streaming SSE support, JWT token management
- **Port**: 3000

### Orchestrator Service (Python)
- **Package Manager**: UV
- **Web Framework**: FastAPI + Uvicorn
- **Authentication**: `msal` (MSAL Python), `python-jose[cryptography]`
- **HTTP Client**: `httpx` (async)
- **Configuration**: `pydantic-settings`
- **Port**: 3000 (same as frontend - will need port change)

### Python Sub-Agent
- **Package Manager**: UV
- **Web Framework**: FastAPI + Uvicorn
- **Agent Framework**: `agent-framework` (Microsoft Agent Framework - unified)
- **Agent Backends**:
  - Claude CLI (default) - Shell command integration
  - Local LLM via HTTP (Ollama support)
  - OpenAI-compatible APIs (LM Studio, vLLM, etc.)
- **Authentication** (Phase 3): `msal`, `python-jose`
- **Azure SDK**: `azure-identity`, `httpx`
- **Port**: 8000

### .NET Sub-Agent
- **Framework**: .NET 8+ / ASP.NET Core
- **Agent Framework** (Phase 3): `Azure.AI.Agents` NuGet
- **Authentication** (Phase 2): `Microsoft.Identity.Web`, `Microsoft.Identity.Client`
- **Web API**: ASP.NET Core Web API
- **Port**: 5000

### Payroll API (.NET)
- **Framework**: .NET 8 (LTS) / ASP.NET Core Web API
- **Authentication**: `Microsoft.Identity.Web` (3.2.1), `Microsoft.AspNetCore.Authentication.JwtBearer` (8.0.11)
- **Features**: JWT validation, user-specific data access, audit logging
- **Security**: OID claim validation, cross-user access prevention
- **Ports**: HTTP 5100, HTTPS 5101

## OBO Flow Explained

The **On-Behalf-Of (OBO) flow** is the core of this POC. Here's how it works:

### Without OBO (Traditional API Call)
```
User → Service A → Service B
       (loses user identity)
```
Service B doesn't know who the original user is. Service B uses Service A's identity.

### With OBO Flow ✅
```
User (JWT) → Orchestrator (validates JWT)
                ↓ OBO Token Exchange
             Azure AD (validates orchestrator can act on behalf of user)
                ↓ Returns new JWT
             Orchestrator → Sub-Agent (OBO JWT)
                              ↓
                         Sub-Agent sees original user's identity
                         Sub-Agent calls APIs as the user
```

**Key Benefits**:
1. **Identity Preservation**: Sub-agents know the original user's identity
2. **RBAC Enforcement**: Sub-agents enforce permissions for the actual user
3. **Audit Trail**: All actions are logged with the correct user identity
4. **Security**: Each service validates tokens independently

### Implementation in This POC

| Component | Port | Role | Token Handling |
|-----------|------|------|----------------|
| **Frontend** | 3000 | User authentication | Obtains user JWT from Azure AD |
| **Orchestrator** | 3000* | Token exchange | Validates user JWT, acquires OBO tokens |
| **Python Agent** | 8000 | Specialized work | Validates OBO token, executes as user |
| **.NET Agent** | 5000 | Specialized work | Validates OBO token, executes as user |
| **Payroll API** | 5100 | User data access | Validates OBO token, enforces user authorization |

_*Note: Orchestrator and Frontend both use port 3000 - port conflict will be resolved in integration phase_

## Security Considerations

1. **Token Validation**: All endpoints must validate incoming JWTs
2. **Scope Verification**: Verify required scopes before granting access
3. **Token Lifetime**: Implement proper token caching and refresh
4. **Audit Logging**: Track all OBO token exchanges and API calls
5. **Error Handling**: Never expose token contents in error messages
6. **Network Security**: Use HTTPS in production, implement timeouts
7. **Least Privilege**: Request minimum necessary scopes for each sub-agent

## Quick Start

### Running All Services

**Terminal 1: Frontend** (Next.js with assistant-ui)
```bash
cd frontend
npm install  # First time only
npm run dev  # Runs on port 3000
```

**Terminal 2: Python Sub-Agent** (uses Claude CLI by default)
```bash
cd python-agent
source .venv/bin/activate  # Already initialized with uv
uvicorn src.main:app --reload --port 8000

# Note: Requires 'claude' CLI to be installed and configured
# To switch backends, edit src/agent.py line 149
```

**Terminal 3: .NET Sub-Agent**
```bash
cd dotnet-agent
dotnet run --project AgentService  # Runs on port 5000
```

**Terminal 4: Payroll API**
```bash
cd dotnet-payroll-api
dotnet run  # Runs on port 5100 (HTTP) and 5101 (HTTPS)
```

**Terminal 5: Orchestrator**
```bash
cd orchestrator
source .venv/bin/activate  # Already initialized with uv
uvicorn src.main:app --reload --port 3001  # Changed to avoid port conflict with frontend
```

### Testing the Flow

**Frontend Testing:**
```bash
# Open browser to http://localhost:3000
# Use the chat interface to interact with the backend
```

**Orchestrator Testing:**
```bash
# Check all services are healthy
curl http://localhost:3001/health/agents

# Test orchestration (will auto-select Python agent)
curl -X POST http://localhost:3001/agent \
  -H "Content-Type: application/json" \
  -d '{"message": "Help me with pandas dataframes"}'

# Test orchestration (will auto-select .NET agent)
curl -X POST http://localhost:3001/agent \
  -H "Content-Type: application/json" \
  -d '{"message": "Help me with ASP.NET Core"}'

# Explicit agent selection
curl -X POST http://localhost:3001/agent \
  -H "Content-Type: application/json" \
  -d '{"message": "Test", "preferred_agent": "python"}'
```

**Payroll API Testing (without auth):**
```bash
# Get user info (returns Alice Johnson's data in testing mode)
curl http://localhost:5100/payroll/user-info

# Get PTO balance
curl http://localhost:5100/payroll/user-pto

# Health check
curl http://localhost:5100/health
```

## Getting Started

See detailed implementation guides:
- [**Frontend**](./frontend/README.md) 🎨 **Chat interface with assistant-ui**
- [**Orchestrator Service**](./orchestrator/README.md) ⭐ **Start here for OBO flow**
- [Python Sub-Agent](./python-agent/README.md)
- [.NET Sub-Agent](./dotnet-agent/README.md)
- [Payroll API](./dotnet-payroll-api/README.md) 🔒 **Secure user data access**

## References

### Agent Framework & Orchestration
- [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
- [Microsoft Agent Framework User Guide](https://learn.microsoft.com/en-us/agent-framework/user-guide/overview)

### Authentication & Security
- [OAuth 2.0 On-Behalf-Of Flow](https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-on-behalf-of-flow)
- [MSAL.NET OBO Documentation](https://learn.microsoft.com/en-us/entra/msal/dotnet/acquiring-tokens/web-apps-apis/on-behalf-of-flow)
- [Microsoft.Identity.Web Documentation](https://learn.microsoft.com/en-us/entra/msal/dotnet/microsoft-identity-web/)

### Frontend & UI
- [assistant-ui](https://github.com/assistant-ui/assistant-ui)
- [assistant-ui Documentation](https://www.assistant-ui.com/docs)
- [ExternalStoreRuntime](https://www.assistant-ui.com/docs/runtimes/custom/external-store)

### Tools & Package Managers
- [UV Package Manager](https://github.com/astral-sh/uv)
- [Next.js Documentation](https://nextjs.org/docs)

## License

This is a proof-of-concept project. Review the Microsoft Agent Framework license (MIT) for production use.
