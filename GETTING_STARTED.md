# Getting Started - Microsoft Agent Framework POC

This guide will help you get all three services running and test the orchestrator + OBO flow.

## 🎯 What You Have

A complete **3-service architecture** demonstrating JWT On-Behalf-Of (OBO) flow:

1. **Orchestrator** (Port 3000) - Python/FastAPI - Validates JWT, exchanges for OBO tokens, delegates to sub-agents
2. **Python Sub-Agent** (Port 8000) - Python/FastAPI - Receives OBO tokens, executes as user
3. **.NET Sub-Agent** (Port 5000) - .NET 8/ASP.NET Core - Receives OBO tokens, executes as user

## 📋 Prerequisites

- **Python 3.11+**
- **UV package manager**: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **.NET 8 SDK**: `brew install dotnet` (macOS) or download from [dotnet.microsoft.com](https://dotnet.microsoft.com/download)

## 🚀 Quick Start (3 Terminals)

### Terminal 1: Python Sub-Agent

```bash
cd python-agent

# Install dependencies (first time only)
uv sync

# Run the service
uv run uvicorn src.main:app --reload --port 8000

# You should see:
# INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Test it:**
```bash
curl http://localhost:8000/agent
# Response: {"message":"it's alive","status":"healthy","agent_type":"python-fastapi"}
```

---

### Terminal 2: .NET Sub-Agent

```bash
cd dotnet-agent

# Restore dependencies (first time only)
dotnet restore

# Run the service
dotnet run --project AgentService

# You should see:
# Now listening on: http://localhost:5000
# Now listening on: https://localhost:5001
```

**Test it:**
```bash
curl http://localhost:5000/agent
# Response: {"message":"it's alive","status":"healthy","agentType":"dotnet-aspnet"}
```

---

### Terminal 3: Orchestrator

```bash
cd orchestrator

# Install dependencies (first time only)
uv sync

# Run the service
uv run uvicorn src.main:app --reload --port 3000

# You should see:
# INFO:     Uvicorn running on http://127.0.0.1:3000
```

**Test it:**
```bash
curl http://localhost:3000/agent
# Response: {"message":"Orchestrator is alive","status":"healthy",...}
```

---

## ✅ Test the Complete Flow

Once all three services are running:

### 1. Check All Services Are Healthy

```bash
curl http://localhost:3000/health/agents
```

**Expected response:**
```json
{
  "orchestrator": "healthy",
  "sub_agents": {
    "python": "healthy",
    "dotnet": "healthy"
  }
}
```

### 2. Test Auto Agent Selection (Python)

Messages with keywords like `pandas`, `numpy`, `data` will route to Python agent:

```bash
curl -X POST http://localhost:3000/agent \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Help me analyze data with pandas",
    "preferred_agent": "auto"
  }'
```

**Expected response:**
```json
{
  "message": "it's alive",
  "status": "success",
  "selected_agent": "python",  // ← Auto-selected Python
  "conversation_id": null,
  "sub_agent_responses": [
    {
      "agent_type": "python",
      "message": "it's alive",
      "status": "healthy",
      "metadata": {}
    }
  ],
  "metadata": {
    "user_id": "test-user-id",
    "user_name": "Test User",
    "auth_enabled": false,
    "obo_token_acquired": false
  }
}
```

### 3. Test Auto Agent Selection (.NET)

Messages with keywords like `c#`, `.net`, `asp.net` will route to .NET agent:

```bash
curl -X POST http://localhost:3000/agent \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Help me build an ASP.NET Core API",
    "preferred_agent": "auto"
  }'
```

**Expected response:**
```json
{
  "message": "it's alive",
  "status": "success",
  "selected_agent": "dotnet",  // ← Auto-selected .NET
  "sub_agent_responses": [
    {
      "agent_type": "dotnet",
      "message": "it's alive",
      "status": "healthy"
    }
  ]
}
```

### 4. Test Explicit Agent Selection

Override auto-selection by specifying `preferred_agent`:

```bash
# Force .NET agent even with Python keywords
curl -X POST http://localhost:3000/agent \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Help me with pandas",
    "preferred_agent": "dotnet"
  }'
```

**Response will show:** `"selected_agent": "dotnet"` (preference overrides intent)

---

## 🔍 Understanding the Flow

### Current State (Phase 1 - No Auth)

```
Frontend/curl → Orchestrator (Port 3000)
                    ↓
                Analyzes message
                    ↓
                Selects agent (Python or .NET)
                    ↓
                Calls sub-agent via HTTP
                    ↓
                Python Agent (Port 8000) OR .NET Agent (Port 5000)
                    ↓
                Returns "it's alive"
                    ↓
                Orchestrator aggregates response
                    ↓
                Returns to frontend/curl
```

**Currently:** `REQUIRE_AUTH=false` in orchestrator - testing mode, no JWT validation

### Future State (Phase 2+ - With OBO)

```
Frontend (with user JWT) → Orchestrator
                                ↓
                            Validates user JWT
                                ↓
                            Exchanges JWT for OBO token (MSAL) ⭐
                                ↓
                            Calls sub-agent with OBO token
                                ↓
                            Sub-agent validates OBO token
                                ↓
                            Sub-agent sees original user identity
                                ↓
                            Sub-agent executes with user permissions
```

**After Azure AD setup:** Set `REQUIRE_AUTH=true` in orchestrator's `.env`

---

## 📁 Project Structure

```
af-poc/
├── GETTING_STARTED.md          # ← You are here
├── README.md                    # Overall project documentation
│
├── orchestrator/                # ⭐ Orchestrator Service
│   ├── README.md               # Detailed orchestrator guide
│   ├── src/
│   │   ├── main.py            # FastAPI app
│   │   ├── api.py             # /agent endpoint
│   │   ├── auth.py            # JWT validation & OBO flow ⭐⭐
│   │   ├── agent_selector.py  # Auto-select Python vs .NET
│   │   └── sub_agent_client.py # HTTP client for sub-agents
│   └── tests/                  # pytest tests
│
├── python-agent/               # Python Sub-Agent
│   ├── README.md
│   ├── src/
│   │   ├── main.py            # FastAPI app
│   │   ├── api.py             # /agent endpoint (returns "it's alive")
│   │   └── models.py          # Request/response models
│   └── tests/
│
└── dotnet-agent/               # .NET Sub-Agent
    ├── README.md
    └── AgentService/
        ├── Program.cs          # ASP.NET Core setup
        ├── Controllers/
        │   └── AgentController.cs  # /agent endpoint
        └── Models/
```

---

## 🧪 Running Tests

### Python Agent Tests
```bash
cd python-agent
uv run pytest
```

### .NET Agent Tests
```bash
cd dotnet-agent
dotnet test  # (tests not yet created)
```

### Orchestrator Tests
```bash
cd orchestrator
uv run pytest -v
```

---

## 🐛 Troubleshooting

### "Port already in use"

Kill the process using the port:
```bash
# macOS/Linux
lsof -ti:3000 | xargs kill  # Orchestrator
lsof -ti:8000 | xargs kill  # Python agent
lsof -ti:5000 | xargs kill  # .NET agent
```

### Sub-agent not reachable

Check if services are running:
```bash
curl http://localhost:8000/health  # Python agent
curl http://localhost:5000/health  # .NET agent
```

If not running, start them following the Quick Start above.

### UV not found

Install UV:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# Restart terminal
uv --version
```

### .NET SDK not found

Install .NET 8:
```bash
# macOS
brew install dotnet

# Or download from https://dotnet.microsoft.com/download
dotnet --version  # Should show 8.x.x
```

---

## 🎯 What's Next?

Now that everything is running, you can:

1. **Explore the Code**:
   - `orchestrator/src/auth.py` - See OBO implementation
   - `orchestrator/src/agent_selector.py` - Understand agent selection logic
   - `orchestrator/src/sub_agent_client.py` - See how sub-agents are called

2. **Test Different Messages**:
   - Try messages with different keywords to see agent selection
   - Test explicit agent preferences

3. **Review Phase 2 Roadmap** (in main README.md):
   - Configure Azure AD for real OBO flow
   - Add Microsoft Agent Framework for AI responses
   - Implement conversation state

4. **Read Detailed Docs**:
   - [Orchestrator README](./orchestrator/README.md) - Deep dive into OBO flow
   - [Root README](./README.md) - Overall architecture and phases
   - [Python Agent README](./python-agent/README.md) - Python implementation details
   - [.NET Agent README](./dotnet-agent/README.md) - .NET implementation details

---

## 📚 Key Concepts

### What is OBO (On-Behalf-Of) Flow?

**Problem**: When Service A calls Service B, Service B only sees Service A's identity, not the original user.

**Solution**: OBO flow allows Service A to exchange the user's token for a new token that:
- Still contains the user's identity
- Has permissions for Service B
- Allows Service B to call APIs as the user

**In this POC**:
- **Orchestrator** receives user JWT
- **Orchestrator** exchanges it for OBO token (via MSAL + Azure AD)
- **Sub-agents** receive OBO token and see original user identity
- **Sub-agents** can call APIs with user's permissions (RBAC preserved)

### Agent Selection Logic

The orchestrator uses keyword matching to auto-select agents:

**Python Keywords**: `python`, `pandas`, `numpy`, `data`, `analysis`, `fastapi`, `ml`
**\.NET Keywords**: `.net`, `dotnet`, `c#`, `asp.net`, `entity framework`, `blazor`

If no clear match, defaults to Python.

---

## 🔗 Useful Links

- [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
- [OAuth 2.0 OBO Flow Docs](https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-on-behalf-of-flow)
- [MSAL Python Docs](https://github.com/AzureAD/microsoft-authentication-library-for-python)
- [UV Documentation](https://github.com/astral-sh/uv)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

**Ready to test?** Start all three services and run the curl commands above! 🚀
