# Python Agent - Microsoft Agent Framework Implementation

## Overview

This Python agent implementation uses the **Microsoft Agent Framework** following best practices from the official framework documentation. It replaces the previous Claude Code shell integration with a production-ready agent service.

## What Changed

### Previous Implementation (Deprecated)
- ❌ Claude Code CLI shell integration (`src/agent.py`)
- ❌ Subprocess-based agent execution
- ❌ Limited tool ecosystem
- ❌ No workflow orchestration

### New Implementation (Current)
- ✅ Microsoft Agent Framework with Azure OpenAI (`src/agent_framework_impl.py`)
- ✅ Thread-based conversation management
- ✅ Function tools with automatic schema generation
- ✅ Workflow orchestration (sequential & concurrent) (`src/workflows.py`)
- ✅ Production-ready authentication (Azure credentials)
- ✅ Enterprise observability and logging

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Application                     │
│                         (src/main.py)                        │
└─────────────────┬────────────────────────┬──────────────────┘
                  │                        │
        ┌─────────▼──────────┐   ┌────────▼──────────┐
        │   API Endpoints    │   │   Health Check    │
        │    (src/api.py)    │   │                   │
        └─────────┬──────────┘   └───────────────────┘
                  │
      ┌───────────┴────────────┐
      │                        │
┌─────▼──────────────┐  ┌─────▼──────────────┐
│  Agent Framework   │  │     Workflows      │
│  Implementation    │  │  (src/workflows.py)│
│ (src/agent_        │  │                    │
│  framework_impl.py)│  │  - Document        │
│                    │  │    Processing      │
│ - Azure OpenAI     │  │  - Concurrent      │
│ - Function Tools   │  │    Analysis        │
│ - Thread State     │  │                    │
└────────────────────┘  └────────────────────┘
```

## Key Components

### 1. AgentFrameworkService (`src/agent_framework_impl.py`)

The core agent implementation following Microsoft Agent Framework best practices:

**Features:**
- Azure OpenAI integration with proper credential management
- Thread-based conversation state (multi-turn conversations)
- Function tools with type-hint based schema generation
- Streaming response support

**Tools Implemented:**
- `get_weather(location)` - Weather information (demo)
- `calculate(expression)` - Math expression evaluation
- `search_files(pattern, directory)` - File search (demo)

**Authentication Priority:**
1. `AzureCliCredential` (local development with `az login`)
2. `ManagedIdentityCredential` (Azure deployments)
3. `DefaultAzureCredential` (fallback chain)

### 2. Workflows (`src/workflows.py`)

Workflow orchestration demonstrating both sequential and concurrent patterns:

**Sequential Workflow: Document Processing**
```
User Request → Writer Agent → Editor Agent → Final Document
```
- Writer creates initial content
- Editor improves grammar and clarity
- Returns polished document

**Concurrent Workflow: Multi-Perspective Analysis**
```
                    ┌─→ Technical Analyst
User Request → Split┤
                    └─→ Business Analyst → Aggregated Result
```
- Parallel execution for faster results
- Multiple specialized perspectives
- Ensemble reasoning

### 3. API Endpoints (`src/api.py`)

**Primary Endpoints:**

1. `POST /agent` - Main agent interaction
   - Single-agent responses with tool usage
   - Thread-based conversation continuity

2. `POST /workflow/document` - Document processing workflow
   - Sequential orchestration demo
   - Writer → Editor pipeline

3. `POST /workflow/analysis` - Multi-perspective analysis
   - Concurrent orchestration demo
   - Parallel agent execution

4. `GET /agent` - Status and health check
   - Shows available tools and workflows
   - Configuration information

## Installation & Setup

### Prerequisites

1. **Python 3.11+**
2. **Azure OpenAI Resource** with deployed model
3. **Azure CLI** (for local development): `az login`

### Quick Start

```bash
# 1. Navigate to python-agent directory
cd python-agent

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies (with prerelease flag for agent-framework)
pip install --pre -e ".[dev]"

# 4. Configure environment
cp .env.example .env
# Edit .env and set:
#   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
#   AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini

# 5. Authenticate with Azure (for local dev)
az login

# 6. Start the server
uvicorn src.main:app --reload --port 8000
```

### Environment Configuration

See `.env.example` for full configuration options. Minimum required:

```bash
# Required
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini

# Optional but recommended
AGENT_NAME=PythonSpecializedAgent
AGENT_INSTRUCTIONS=You are a specialized Python agent...
```

## Usage Examples

### 1. Simple Agent Query

```bash
curl -X POST http://localhost:8000/agent \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the weather in Seattle?"
  }'
```

**Response:**
```json
{
  "message": "The weather in Seattle is partly cloudy with a temperature of 18°C (64°F). Light winds from the northwest.",
  "status": "success",
  "agent_type": "microsoft-agent-framework",
  "conversation_id": null
}
```

### 2. Conversation with State

```bash
# First message
curl -X POST http://localhost:8000/agent \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My name is Alice",
    "conversation_id": "conv-123"
  }'

# Follow-up (agent remembers context)
curl -X POST http://localhost:8000/agent \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is my name?",
    "conversation_id": "conv-123"
  }'
```

### 3. Tool Usage - Calculator

```bash
curl -X POST http://localhost:8000/agent \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Calculate 15 * 24 + 100"
  }'
```

### 4. Document Processing Workflow

```bash
curl -X POST http://localhost:8000/workflow/document \
  -H "Content-Type: application/json" \
  -d '{
    "input": "artificial intelligence in healthcare"
  }'
```

**Response:**
```json
{
  "result": "<polished article created by Writer then improved by Editor>",
  "status": "success",
  "workflow_type": "sequential-document-processing",
  "metadata": {
    "steps": ["writer", "editor"]
  }
}
```

### 5. Multi-Perspective Analysis Workflow

```bash
curl -X POST http://localhost:8000/workflow/analysis \
  -H "Content-Type: application/json" \
  -d '{
    "input": "implementing GraphQL in microservices architecture"
  }'
```

**Response:**
```json
{
  "result": "Multi-Perspective Analysis: implementing GraphQL...\n\n=== Technical Perspective ===\n<technical analysis>\n\n=== Business Perspective ===\n<business analysis>",
  "status": "success",
  "workflow_type": "concurrent-multi-perspective-analysis",
  "metadata": {
    "perspectives": ["technical", "business"],
    "execution": "parallel"
  }
}
```

## Best Practices Implemented

### From Microsoft Agent Framework Research

1. **Separation of Concerns**
   - ✅ AI Agents for autonomous decision-making
   - ✅ Workflows for structured orchestration
   - ✅ Clear distinction between tools and agents

2. **Authentication**
   - ✅ DefaultAzureCredential chain (best practice)
   - ✅ No hardcoded secrets in code
   - ✅ Managed Identity support for production

3. **Tool Design**
   - ✅ Type hints with `Annotated` and `Field` descriptions
   - ✅ Automatic schema generation (no manual JSON)
   - ✅ Single-purpose, focused tools
   - ✅ Clear docstrings for LLM understanding

4. **State Management**
   - ✅ Thread-based conversation state
   - ✅ Conversation ID mapping
   - ✅ Stateless service design (threads stored externally)

5. **Orchestration Patterns**
   - ✅ Sequential for dependent steps (document processing)
   - ✅ Concurrent for independent analysis (multi-perspective)
   - ✅ Type-safe workflow context
   - ✅ Event-based execution monitoring

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Test specific endpoint
pytest tests/test_api.py::test_agent_endpoint -v

# Health check
curl http://localhost:8000/health

# Agent status
curl http://localhost:8000/agent
```

## Project Structure

```
python-agent/
├── src/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry point
│   ├── api.py                     # API endpoints (updated)
│   ├── config.py                  # Configuration management
│   ├── models.py                  # Pydantic models (updated)
│   ├── agent_framework_impl.py    # NEW: Microsoft Agent Framework
│   ├── workflows.py               # NEW: Workflow orchestrations
│   └── agent.py                   # DEPRECATED: Claude Code shell integration
├── tests/
│   ├── test_api.py
│   └── test_agent_framework.py    # TODO: Add tests
├── .env.example                   # UPDATED: Comprehensive config
├── pyproject.toml
└── README_AGENT_FRAMEWORK.md      # This file
```

## Migration from Claude Code

The old Claude Code implementation (`src/agent.py`) is **deprecated but kept for reference**.

**To migrate:**
1. Update `src/api.py` imports (already done)
2. Configure Azure OpenAI in `.env` (see above)
3. Run `az login` for authentication
4. Start server - it now uses Agent Framework automatically

**Old endpoint behavior preserved:**
- `POST /agent` still works with same request/response format
- Conversation continuity maintained via `conversation_id`

## Production Deployment Checklist

- [ ] Set `REQUIRE_AUTH=true` in production `.env`
- [ ] Configure Managed Identity for Azure deployments
- [ ] Set up Application Insights for observability
- [ ] Enable HTTPS (configure reverse proxy/load balancer)
- [ ] Implement rate limiting (nginx/API Gateway)
- [ ] Set appropriate CORS origins
- [ ] Configure log aggregation
- [ ] Set up health check monitoring
- [ ] Review and limit CORS_ORIGINS
- [ ] Use separate Azure OpenAI deployments for dev/prod

## Advanced Configuration

### Custom Tools

Add new tools to `src/agent_framework_impl.py`:

```python
def your_custom_tool(
    self,
    param: Annotated[str, Field(description="Parameter description")],
) -> str:
    """Tool description for the LLM."""
    # Implementation
    return result

# Register in _get_agent_tools()
return [
    self.get_weather,
    self.calculate,
    self.your_custom_tool,  # Add here
]
```

### Custom Workflows

Create new workflows in `src/workflows.py`:

```python
@executor(id="your_executor")
async def your_executor(input: str, ctx: WorkflowContext) -> None:
    # Process input
    await ctx.send_message(result)

# Build workflow
your_workflow = (
    WorkflowBuilder()
    .add_edge(executor1, executor2)
    .set_start_executor(executor1)
    .build()
)
```

## Troubleshooting

### "Agent not initialized"
- Check `AZURE_OPENAI_ENDPOINT` is set correctly
- Verify deployment name exists in Azure OpenAI Studio
- Ensure you've run `az login` for local dev

### Authentication Errors
```bash
# Check Azure CLI authentication
az account show

# Re-login if needed
az login

# Verify you have access to the OpenAI resource
az cognitiveservices account show --name <your-resource> --resource-group <rg>
```

### Import Errors
```bash
# Reinstall with prerelease flag
pip install --pre -e ".[dev]"
```

## References

- [Microsoft Agent Framework GitHub](https://github.com/microsoft/agent-framework)
- [AGENT_FRAMEWORK_RESEARCH.md](../AGENT_FRAMEWORK_RESEARCH.md) - Comprehensive research
- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [Azure Identity SDK](https://learn.microsoft.com/en-us/python/api/azure-identity/)

## License

Same as parent project.
