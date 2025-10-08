# Quick Start - Frontend to Orchestrator Integration

This guide will help you quickly test the integration between the frontend chat interface and the orchestrator service.

## Architecture Overview

```
Frontend (Next.js)          Orchestrator (FastAPI)        Sub-Agents
Port 3000                   Port 3001*                     Port 8000/5000
    │                            │                              │
    │  POST /api/chat            │                              │
    │  { messages: [...] }       │                              │
    │                            │                              │
    │  → Converts last msg  →    │  POST /agent                 │
    │                            │  { message: "...", ... }     │
    │                            │                              │
    │                            │  → Selects agent        →    │
    │                            │                              │
    │                            │  ← Agent response       ←    │
    │                            │                              │
    │  ← Streaming response ←    │                              │
    │    with agent metadata     │                              │
```

_*Note: Orchestrator uses port 3001 to avoid conflict with frontend on port 3000_

## Prerequisites

1. **Python agent** or **.NET agent** must be running on port 8000 or 5000
2. **Orchestrator** must be running on port 3001 (not 3000 - avoid port conflict!)
3. **Frontend** dependencies installed (`npm install`)
4. **Payroll API** (optional) can run on port 5100 for testing .NET agent integration

## Step-by-Step Setup

### Terminal 1: Start Python Agent (or .NET Agent)

```bash
cd python-agent
source .venv/bin/activate
uvicorn src.main:app --reload --port 8000
```

Wait for: `Application startup complete.`

### Terminal 2: Start Orchestrator

```bash
cd orchestrator
source .venv/bin/activate
uvicorn src.main:app --reload --port 3001  # Changed to avoid port conflict with frontend
```

**⚠️ IMPORTANT:** Use port **3001**, not 3000! The frontend uses port 3000.

Wait for: `Application startup complete.`

### Terminal 3: Start Frontend

```bash
cd frontend
npm install  # First time only
npm run dev
```

Wait for: `Ready in X.Xms`

### Terminal 4: Start Payroll API (Optional)

```bash
cd dotnet-payroll-api
dotnet run  # Runs on port 5100 (HTTP) and 5101 (HTTPS)
```

This is optional but required if testing the full .NET agent → Payroll API flow.

### Terminal 5: Test the Integration (Optional)

```bash
./test-integration.sh
```

## Using the Chat Interface

1. Open your browser to: **http://localhost:3000**
2. Type a message in the chat interface
3. Click send or press Enter
4. You should see:
   - The assistant's response from the orchestrator
   - Metadata showing which agent handled the request
   - Status information

### Example Messages to Try

- `"Help me with pandas dataframes"` → Routes to Python agent
- `"Help me with ASP.NET Core"` → Routes to .NET agent
- `"What's the weather?"` → Auto-selects appropriate agent

## What's Happening Under the Hood

1. **Frontend** (`/app/api/chat/route.ts`):
   - Receives messages from chat UI
   - Extracts last user message
   - Calls orchestrator at `POST http://localhost:3001/agent`
   - Converts response to streaming format for UI

2. **Orchestrator** (`/orchestrator/src/api.py`):
   - Validates request (no auth required in POC mode)
   - Analyzes message to select Python or .NET agent
   - Calls selected sub-agent
   - Returns response with metadata

3. **Sub-Agent** (Python or .NET):
   - Receives message from orchestrator
   - Processes with Agent Framework (Python) or returns mock response (.NET)
   - Returns result to orchestrator

## Troubleshooting

### Frontend can't connect to orchestrator

**Error:** `Failed to connect to orchestrator`

**Solutions:**
1. Check orchestrator is running on port 3001: `curl http://localhost:3001/health`
2. Check `.env.local` in frontend has: `ORCHESTRATOR_URL=http://localhost:3001`
3. Restart frontend: `npm run dev`

### Orchestrator can't reach sub-agents

**Error:** `Sub-agent unreachable`

**Solutions:**
1. Check Python agent is running: `curl http://localhost:8000/health`
2. Check .NET agent is running: `curl http://localhost:5000/health`
3. Check orchestrator health: `curl http://localhost:3001/health/agents`

### Port 3001 already in use

**Solutions:**
1. Kill process on port 3001: `lsof -ti:3001 | xargs kill -9`
2. Or use different port: `uvicorn src.main:app --reload --port 3002`
3. Update frontend `.env.local` to match

### Chat interface not loading

**Solutions:**
1. Check frontend dev server is running
2. Check browser console for errors (F12)
3. Clear browser cache and reload
4. Check port 3000 is available: `lsof -i:3000`

## Testing Without Frontend

You can test the orchestrator directly:

```bash
curl -X POST http://localhost:3001/agent \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello from curl!",
    "preferred_agent": "python"
  }'
```

Expected response:
```json
{
  "message": "Response from agent...",
  "status": "success",
  "selected_agent": "python",
  "conversation_id": null,
  "sub_agent_responses": [...],
  "metadata": {
    "user_id": "test",
    "user_name": "Test User",
    "auth_enabled": false,
    "obo_token_acquired": false
  }
}
```

## Next Steps

Once basic integration is working:

1. **Add Authentication:** Enable Azure AD JWT tokens
2. **Implement Streaming:** Stream responses from agents instead of returning full message
3. **Add Conversation History:** Track conversation_id across messages
4. **Error Handling:** Better error messages in UI
5. **Agent Selection UI:** Show user which agent will handle their request
6. **Response Metadata:** Display agent type, processing time, etc.

## Files Modified

- `frontend/app/api/chat/route.ts` - Routes chat to orchestrator
- `frontend/.env.local` - Orchestrator URL configuration
- `orchestrator/src/config.py` - Changed default port to 3001

## Environment Variables

### Frontend (`frontend/.env.local`)
```bash
ORCHESTRATOR_URL=http://localhost:3001
```

### Orchestrator (`orchestrator/.env` - optional, has defaults)
```bash
API_PORT=3001
API_HOST=0.0.0.0
REQUIRE_AUTH=false
PYTHON_AGENT_URL=http://localhost:8000
DOTNET_AGENT_URL=http://localhost:5000
```

**Note:** The orchestrator will use port 3001 by default. You can override with environment variables or command-line arguments.

## Additional Resources

- [**Main README**](../README.md) - Full project documentation and architecture
- [**Orchestrator Service**](../orchestrator/README.md) ⭐ Start here for OBO flow details
- [**Frontend**](../frontend/README.md) 🎨 Chat interface with assistant-ui
- [**Python Agent**](../python-agent/README.md) - Agent framework setup
- [**.NET Agent**](../dotnet-agent/README.md) - .NET sub-agent implementation
- [**Payroll API**](../dotnet-payroll-api/README.md) 🔒 Secure user data access
