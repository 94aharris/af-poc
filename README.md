# Microsoft Agent Framework POC - Multi-Agent Orchestration with JWT OBO

## Project Overview

This proof-of-concept demonstrates the Microsoft Agent Framework with JWT On-Behalf-Of (OBO) authentication flow for secure, delegated API access in a multi-agent architecture.

**Repository**: https://github.com/microsoft/agent-framework

## Architecture

### Current Working Demo Flow

```
┌─────────────────────────────────────────────────────────────┐
│            Frontend (Next.js + assistant-ui)                 │
│                     (Port 3000)                              │
│  - User authentication & JWT acquisition                     │
│  - Chat interface with assistant-ui                          │
│  - Auth.js (NextAuth v5) for Azure AD integration           │
└────────────────────┬────────────────────────────────────────┘
                     │ User JWT Token
                     ↓
┌─────────────────────────────────────────────────────────────┐
│         ORCHESTRATOR SERVICE (Python/FastAPI - Port 8001)    │
│                                                              │
│  1. JWT Validator - Validates user token                    │
│  2. Microsoft Agent Framework - AI-powered orchestration    │
│  3. OBO Token Service ⭐ - Exchanges JWT for OBO tokens     │
│  4. Intelligent Tools - Payroll API & Calculator delegation │
└────────┬───────────────────────────────┬─────────────────────┘
         │ OBO Token (Payroll scopes)     │ OBO Token (Python scopes)
         ↓                                ↓
┌────────────────────┐              ┌────────────────────────┐
│  Payroll API       │              │  Python Sub-Agent      │
│  (Port 5100)       │              │  (Port 8000)           │
│                    │              │                        │
│  - User info       │              │  - Calculator tool     │
│  - PTO data        │              │  - Math operations     │
│  - JWT auth        │              │  - Validates OBO       │
│  - OID validation  │              │  - Agent Framework     │
└────────────────────┘              └────────────────────────┘
```

### What's NOT in the Demo

- **dotnet-agent** (Port 5000) - ⚠️ **BROKEN** - Not currently part of the working application flow

## Core Requirements

1. **Multi-Agent Orchestration**: Single orchestrator delegates to specialized agents
2. **JWT OBO Flow**: Secure token exchange maintaining user identity across agent calls
3. **Cross-Platform**: Demonstrates functionality in Python; .NET partially implemented
4. **AAA & RBAC**: Full authentication, authorization, and access control
5. **API Endpoints**: Each agent exposes `/agent` endpoint for communication

## Key Features

### Agent Framework Capabilities

- **AI-Powered Orchestration**: Azure OpenAI-based agent with intelligent tool selection
- **Tool-Based Architecture**: Modular tools for payroll API access and calculations
- **Thread Management**: Conversation state management per user
- **OBO Integration**: All tools use OBO tokens for secure API access

### JWT On-Behalf-Of (OBO) Flow

- **Token Delegation**: Orchestrator exchanges user JWT for delegated access tokens
- **Identity Preservation**: Sub-agents call APIs maintaining original user context
- **Security Boundaries**: Each agent validates and processes tokens independently
- **Scope-Based Access**: Different scopes for different downstream services

## Project Structure

```
af-poc/
├── README.md                           # This file - overall project documentation
│
├── frontend/                           # 🎨 Frontend (Port 3000)
│   ├── README.md                      # Frontend documentation
│   ├── package.json                   # npm dependencies
│   ├── app/
│   │   ├── page.tsx                  # Main chat page
│   │   ├── assistant.tsx             # Chat interface with useLocalRuntime
│   │   ├── layout.tsx                # Root layout
│   │   ├── auth.ts                   # Auth.js configuration
│   │   └── api/
│   │       └── chat/route.ts         # Backend API proxy
│   ├── components/
│   │   ├── assistant-ui/             # UI components from assistant-ui
│   │   └── ui/                       # shadcn/ui components
│   ├── lib/
│   │   └── auth-provider.tsx         # Auth provider
│   └── .env.local                    # Environment variables
│
├── orchestrator/                       # ⭐ ORCHESTRATOR SERVICE (Port 8001)
│   ├── README.md                      # Orchestrator implementation details
│   ├── pyproject.toml                 # UV configuration
│   ├── src/
│   │   ├── main.py                   # FastAPI application
│   │   ├── api.py                    # Main /agent endpoint
│   │   ├── agent_framework_impl.py   # ⭐⭐ Microsoft Agent Framework with tools
│   │   ├── auth.py                   # ⭐⭐ JWT validation & OBO flow
│   │   ├── agent_selector.py         # Intent analysis (optional)
│   │   ├── sub_agent_client.py       # Sub-agent HTTP client
│   │   ├── config.py                 # Configuration
│   │   └── models.py                 # Request/response models
│   └── tests/
│
├── python-agent/                       # Python Sub-Agent (Port 8000)
│   ├── README.md                      # Python agent details
│   ├── pyproject.toml                 # UV project configuration
│   ├── src/
│   │   ├── main.py                   # FastAPI application
│   │   ├── api.py                    # /agent endpoint
│   │   ├── agent_framework_impl.py   # Microsoft Agent Framework
│   │   ├── workflows.py              # Workflow examples
│   │   ├── config.py                 # Configuration
│   │   └── models.py                 # Data models
│   ├── examples/                     # Agent Framework examples
│   └── tests/
│
├── dotnet-payroll-api/                 # 🔒 Payroll API (Port 5100)
│   ├── README.md                      # Payroll API documentation
│   ├── PayrollApi.sln                 # Solution file
│   ├── PayrollApi/
│   │   ├── Program.cs                # ASP.NET Core setup with JWT auth
│   │   ├── appsettings.json          # Configuration
│   │   ├── Controllers/
│   │   │   └── PayrollController.cs  # /user-info & /user-pto endpoints
│   │   ├── Models/
│   │   │   ├── UserInfo.cs           # User information model
│   │   │   └── UserPto.cs            # PTO balance model
│   │   └── Services/
│   │       └── PayrollDataService.cs # In-memory data service
│   └── tests/
│
├── dotnet-agent/                       # ⚠️ BROKEN - NOT PART OF DEMO
│   ├── README.md                      # .NET agent (non-functional)
│   └── AgentService/                  # Basic structure only
│
├── setup-azure-apps.sh                 # Azure AD setup automation
├── setup-payroll-api-azure.sh          # Payroll API Azure setup
├── Makefile                            # Development commands
└── .env                                # Environment configuration
```

## Technology Stack

### Frontend
- **Framework**: Next.js 15+ (React 19)
- **UI Library**: [assistant-ui](https://github.com/assistant-ui/assistant-ui)
- **Runtime**: `useLocalRuntime` with custom `ChatModelAdapter`
- **Authentication**: Auth.js (NextAuth v5) with Azure AD provider
- **Styling**: Tailwind CSS + shadcn/ui
- **Language**: TypeScript
- **Port**: 3000

### Orchestrator Service (Python)
- **Package Manager**: UV
- **Web Framework**: FastAPI + Uvicorn
- **Agent Framework**: Microsoft Agent Framework with Azure OpenAI
- **Authentication**: `msal` (MSAL Python), `python-jose[cryptography]`
- **HTTP Client**: `httpx` (async)
- **Configuration**: `pydantic-settings`
- **Port**: 8001

### Python Sub-Agent
- **Package Manager**: UV
- **Web Framework**: FastAPI + Uvicorn
- **Agent Framework**: Microsoft Agent Framework
- **LLM Backend**: Azure OpenAI (default)
- **Authentication**: `azure-identity`, `msal`
- **Port**: 8000

### Payroll API (.NET)
- **Framework**: .NET 8 (LTS) / ASP.NET Core Web API
- **Authentication**: `Microsoft.Identity.Web` (3.2.1), JWT Bearer
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
Service B doesn't know who the original user is.

### With OBO Flow ✅
```
User (JWT) → Orchestrator (validates JWT)
                ↓ OBO Token Exchange via MSAL
             Azure AD (validates orchestrator can act on behalf of user)
                ↓ Returns new JWT
             Orchestrator → Sub-Agent/API (OBO JWT)
                              ↓
                         Sub-Agent sees original user's identity
                         Sub-Agent enforces user's permissions
```

**Key Benefits**:
1. **Identity Preservation**: Sub-agents know the original user's identity
2. **RBAC Enforcement**: Sub-agents enforce permissions for the actual user
3. **Audit Trail**: All actions are logged with the correct user identity
4. **Security**: Each service validates tokens independently

### Implementation in This POC

| Component        | Port | Role                | Token Handling                                   |
| ---------------- | ---- | ------------------- | ------------------------------------------------ |
| **Frontend**     | 3000 | User authentication | Obtains user JWT from Azure AD via Auth.js      |
| **Orchestrator** | 8001 | Token exchange      | Validates user JWT, acquires OBO tokens via MSAL |
| **Python Agent** | 8000 | Math operations     | Validates OBO token, executes as user            |
| **Payroll API**  | 5100 | User data access    | Validates OBO token, enforces user authorization |

## Quick Start

### Prerequisites

1. **Install UV** (Python package manager):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Install .NET SDK 8.0+**:
   ```bash
   brew install dotnet  # macOS
   # Or download from https://dotnet.microsoft.com/download
   ```

3. **Install Node.js 18+**:
   ```bash
   brew install node  # macOS
   # Or download from https://nodejs.org/
   ```

4. **Azure Resources** (required for full OBO flow):
   - Azure AD tenant with app registrations
   - Azure OpenAI service instance
   - See `setup-azure-apps.sh` for automated setup

### Running the Demo (Development Mode)

Run these commands in **separate terminals**:

**Terminal 1: Payroll API**
```bash
cd dotnet-payroll-api
dotnet run
# Runs on http://localhost:5100
```

**Terminal 2: Python Agent**
```bash
cd python-agent
uv sync
uv run uvicorn src.main:app --reload --port 8000
```

**Terminal 3: Orchestrator**
```bash
cd orchestrator
uv sync
uv run uvicorn src.main:app --reload --port 8001
```

**Terminal 4: Frontend**
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

### Quick Health Checks

```bash
# Check all services are running
curl http://localhost:3000              # Frontend
curl http://localhost:8001/health       # Orchestrator
curl http://localhost:8000/health       # Python Agent
curl http://localhost:5100/health       # Payroll API
```

### Testing the Flow

**1. Test Orchestrator directly:**
```bash
# Get user PTO information (via Payroll API tool)
curl -X POST http://localhost:8001/agent \
  -H "Content-Type: application/json" \
  -d '{"message": "What is my current PTO balance?"}'

# Perform calculation (via Python Agent tool)
curl -X POST http://localhost:8001/agent \
  -H "Content-Type: application/json" \
  -d '{"message": "What is 1234 times 5678?"}'

# Multi-tool request
curl -X POST http://localhost:8001/agent \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me my PTO and calculate how many days at 8 hours per day"}'
```

**2. Test via Frontend:**
- Open http://localhost:3000
- Use the chat interface to interact with the orchestrator
- Try questions like:
  - "What is my PTO balance?"
  - "Who is my manager?"
  - "Calculate 15 times 24"

## Configuration

### Environment Setup

Each service requires environment variables. Examples are provided in `.env.example` files:

**For Testing Without Authentication** (default):
```bash
# In orchestrator/.env
REQUIRE_AUTH=false
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4
AZURE_OPENAI_API_KEY=your-key

# In dotnet-payroll-api/appsettings.json
"Auth": {
  "RequireAuthentication": false
}
```

**For Production With Azure AD**:
```bash
# Use setup scripts
./setup-azure-apps.sh
./setup-payroll-api-azure.sh

# Update environment files with generated credentials
```

See individual service READMEs for detailed configuration:
- [Orchestrator Configuration](./orchestrator/README.md#configuration)
- [Python Agent Configuration](./python-agent/README.md#environment-configuration)
- [Payroll API Configuration](./dotnet-payroll-api/README.md#configuration)
- [Frontend Configuration](./frontend/README.md#2-configure-environment)

## Implementation Status

### ✅ Completed Features

**Phase 1: Basic Infrastructure**
- [x] Project structure (orchestrator + python-agent + payroll-api)
- [x] Python agent with UV (venv + dependencies)
- [x] Orchestrator service with UV
- [x] Payroll API with .NET
- [x] Basic `/agent` endpoints in all services

**Phase 2: Microsoft Agent Framework Integration**
- [x] Orchestrator with Agent Framework + Azure OpenAI
- [x] Python agent with Agent Framework
- [x] Tool-based architecture (get_user_info, get_user_pto, calculate)
- [x] Thread-based conversation management
- [x] Intelligent tool selection via AI

**Phase 3: Authentication & OBO**
- [x] JWT validation in orchestrator
- [x] MSAL-based OBO token exchange
- [x] Payroll API with JWT authentication
- [x] User-scoped data access with OID validation
- [x] Cross-user access prevention

**Phase 4: Frontend Integration**
- [x] Next.js frontend with assistant-ui
- [x] Auth.js (NextAuth v5) with Azure AD
- [x] useLocalRuntime with ChatModelAdapter
- [x] JWT token forwarding to backend
- [x] Chat interface with markdown rendering

### 🚧 In Progress

- [ ] Streaming responses for real-time feedback
- [ ] Error handling and retry logic improvements
- [ ] Comprehensive logging and monitoring

### 🎯 Future Enhancements

**Agent Capabilities**:
- [ ] Multi-agent parallel execution
- [ ] Graph-based workflow orchestration
- [ ] Additional tools (calendar, email, documents)
- [ ] Tool access control based on user roles

**Production Hardening**:
- [ ] Rate limiting
- [ ] API response caching
- [ ] Distributed tracing (OpenTelemetry)
- [ ] Health check monitoring
- [ ] Deployment configurations

**Authentication**:
- [ ] Token refresh handling
- [ ] Session management
- [ ] Role-based access control (RBAC)
- [ ] Multi-tenant support

**Dotnet Agent** (Currently Broken):
- [ ] Fix .NET agent implementation
- [ ] Integrate with Agent Framework
- [ ] Add to orchestrator routing logic

## Development

### Makefile Commands

The project includes a Makefile for common development tasks:

```bash
# Start all services
make dev

# Stop all services
make stop

# Run tests
make test

# Format code
make format

# Check service health
make health

# Clean build artifacts
make clean
```

See `Makefile` for all available commands.

### Project Guidelines

1. **Python Services**: Use UV for package management
2. **.NET Services**: Use dotnet CLI
3. **Configuration**: Never commit `.env` or `appsettings.Development.json`
4. **Secrets**: Use Azure Key Vault for production, user secrets for development
5. **Testing**: Write tests for all new features
6. **Documentation**: Update README files when adding features

## Security Considerations

1. **Token Validation**: All endpoints must validate incoming JWTs
2. **Scope Verification**: Verify required scopes before granting access
3. **Token Lifetime**: Implement proper token caching and refresh
4. **Audit Logging**: Track all OBO token exchanges and API calls
5. **Error Handling**: Never expose token contents in error messages
6. **Network Security**: Use HTTPS in production, implement timeouts
7. **Least Privilege**: Request minimum necessary scopes for each service

## Architecture Decisions

### Why Microsoft Agent Framework?
- Native Azure OpenAI integration
- Built-in conversation state management
- Tool-based architecture for modularity
- Production-ready patterns

### Why UV for Python?
- Faster than pip/poetry
- Better dependency resolution
- Integrated virtual environment management
- Modern Python package management

### Why Auth.js for Frontend?
- Native Next.js App Router integration
- Automatic token refresh
- Secure server-side session management
- Better than MSAL for React server components

### Why Separate Orchestrator from Agents?
- Clean separation of concerns
- Independent scaling
- Language flexibility (Python orchestrator, .NET/Python agents)
- Easier to add new agents

## Troubleshooting

### Services Won't Start

**Port conflicts:**
```bash
# Check what's using a port
lsof -ti:8001 | xargs kill  # Kill process on port 8001
```

**Python dependency issues:**
```bash
cd orchestrator  # or python-agent
uv cache clean
rm -rf .venv
uv sync
```

**.NET build issues:**
```bash
cd dotnet-payroll-api
dotnet clean
dotnet restore --force
dotnet build
```

### Authentication Issues

**JWT validation fails:**
- Verify `AzureAd:TenantId` matches your Azure AD tenant
- Check `AzureAd:ClientId` matches app registration
- Ensure token audience matches expected value
- Verify token hasn't expired

**OBO token acquisition fails:**
- Check API permissions are granted and admin consented
- Verify client secret hasn't expired
- Ensure correct scopes are configured
- Check MSAL logs for detailed errors

**User not found in Payroll API:**
- Add your user to `appsettings.Development.json` in `DeveloperUser` section
- Verify email in JWT matches user email in database
- Check OID claim is being properly validated

### Agent Framework Issues

**Azure OpenAI connection fails:**
```bash
# Verify credentials
echo $AZURE_OPENAI_ENDPOINT
echo $AZURE_OPENAI_DEPLOYMENT

# Test connectivity
curl "$AZURE_OPENAI_ENDPOINT/openai/deployments?api-version=2024-02-15-preview" \
  -H "api-key: $AZURE_OPENAI_API_KEY"
```

**Tools not executing:**
- Check agent logs for tool selection
- Verify tool functions are properly decorated
- Ensure OBO tokens have correct scopes
- Check downstream API connectivity

## Documentation Links

### Component Documentation
- [Orchestrator Service](./orchestrator/README.md) - Core orchestration with OBO flow
- [Python Sub-Agent](./python-agent/README.md) - Calculator and math operations
- [Payroll API](./dotnet-payroll-api/README.md) - Secure user data access
- [Frontend](./frontend/README.md) - Chat interface and authentication
- [.NET Agent](./dotnet-agent/README.md) - (Currently broken, not in demo)

### External References

**Agent Framework & Orchestration:**
- [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
- [Agent Framework User Guide](https://learn.microsoft.com/en-us/agent-framework/user-guide/overview)

**Authentication & Security:**
- [OAuth 2.0 On-Behalf-Of Flow](https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-on-behalf-of-flow)
- [MSAL.NET OBO Documentation](https://learn.microsoft.com/en-us/entra/msal/dotnet/acquiring-tokens/web-apps-apis/on-behalf-of-flow)
- [Microsoft.Identity.Web](https://learn.microsoft.com/en-us/entra/msal/dotnet/microsoft-identity-web/)

**Frontend & UI:**
- [assistant-ui](https://github.com/assistant-ui/assistant-ui)
- [assistant-ui Documentation](https://www.assistant-ui.com/docs)
- [Auth.js (NextAuth v5)](https://authjs.dev/)
- [Next.js Documentation](https://nextjs.org/docs)

**Tools & Package Managers:**
- [UV Package Manager](https://github.com/astral-sh/uv)
- [.NET CLI Documentation](https://learn.microsoft.com/en-us/dotnet/core/tools/)

## Contributing

This is a proof-of-concept project for demonstrating Microsoft Agent Framework capabilities with OBO authentication. Feel free to:

1. Fork the repository
2. Create feature branches
3. Submit pull requests
4. Report issues

## License

This is a proof-of-concept project. Review the Microsoft Agent Framework license (MIT) for production use.
