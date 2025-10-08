# Microsoft Agent Framework POC - Makefile
# Orchestrates build, run, and test for all subprojects

.PHONY: help install build test clean run run-all stop-all health check-deps setup dev

# Colors for output
CYAN := \033[0;36m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

##@ General

help: ## Display this help
	@echo "$(CYAN)Microsoft Agent Framework POC - Multi-Agent Orchestration$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "Usage:\n  make $(CYAN)<target>$(NC)\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  $(CYAN)%-20s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(YELLOW)%s$(NC)\n", substr($$0, 4) } ' $(MAKEFILE_LIST)

##@ Setup & Dependencies

check-deps: ## Check if required dependencies are installed
	@echo "$(CYAN)Checking dependencies...$(NC)"
	@command -v python3 >/dev/null 2>&1 || { echo "$(RED)✗ Python 3 not found$(NC)"; exit 1; }
	@command -v dotnet >/dev/null 2>&1 || { echo "$(RED)✗ .NET SDK not found$(NC)"; exit 1; }
	@command -v uv >/dev/null 2>&1 || { echo "$(RED)✗ UV not found. Install: pip install uv$(NC)"; exit 1; }
	@command -v npm >/dev/null 2>&1 || { echo "$(RED)✗ npm not found$(NC)"; exit 1; }
	@echo "$(GREEN)✓ Python 3:$(NC) $$(python3 --version)"
	@echo "$(GREEN)✓ .NET SDK:$(NC) $$(dotnet --version)"
	@echo "$(GREEN)✓ UV:$(NC) $$(uv --version)"
	@echo "$(GREEN)✓ npm:$(NC) $$(npm --version)"

setup: check-deps ## Initial project setup - install all dependencies
	@echo "$(CYAN)Setting up all projects...$(NC)"
	@$(MAKE) -s install

install: install-orchestrator install-python-agent install-dotnet-agent install-dotnet-payroll install-frontend ## Install dependencies for all projects

install-orchestrator: ## Install orchestrator dependencies
	@echo "$(CYAN)Installing orchestrator dependencies...$(NC)"
	@cd orchestrator && uv sync --prerelease=allow
	@echo "$(GREEN)✓ Orchestrator dependencies installed$(NC)"

install-python-agent: ## Install Python agent dependencies
	@echo "$(CYAN)Installing Python agent dependencies...$(NC)"
	@cd python-agent && uv sync --prerelease=allow
	@echo "$(GREEN)✓ Python agent dependencies installed$(NC)"

install-dotnet-agent: ## Install .NET agent dependencies
	@echo "$(CYAN)Restoring .NET agent dependencies...$(NC)"
	@cd dotnet-agent && dotnet restore
	@echo "$(GREEN)✓ .NET agent dependencies restored$(NC)"

install-dotnet-payroll: ## Install .NET payroll API dependencies
	@echo "$(CYAN)Restoring .NET payroll API dependencies...$(NC)"
	@cd dotnet-payroll-api && dotnet restore
	@echo "$(GREEN)✓ .NET payroll API dependencies restored$(NC)"

install-frontend: ## Install frontend dependencies
	@echo "$(CYAN)Installing frontend dependencies...$(NC)"
	@cd frontend && npm install
	@echo "$(GREEN)✓ Frontend dependencies installed$(NC)"

##@ Build

build: build-orchestrator build-python-agent build-dotnet-agent build-dotnet-payroll build-frontend ## Build all projects

build-orchestrator: ## Build orchestrator
	@echo "$(CYAN)Building orchestrator...$(NC)"
	@cd orchestrator && uv sync --prerelease=allow
	@echo "$(GREEN)✓ Orchestrator built$(NC)"

build-python-agent: ## Build Python agent
	@echo "$(CYAN)Building Python agent...$(NC)"
	@cd python-agent && uv sync --prerelease=allow
	@echo "$(GREEN)✓ Python agent built$(NC)"

build-dotnet-agent: ## Build .NET agent
	@echo "$(CYAN)Building .NET agent...$(NC)"
	@cd dotnet-agent && dotnet build --configuration Release
	@echo "$(GREEN)✓ .NET agent built$(NC)"

build-dotnet-payroll: ## Build .NET payroll API
	@echo "$(CYAN)Building .NET payroll API...$(NC)"
	@cd dotnet-payroll-api && dotnet build --configuration Release
	@echo "$(GREEN)✓ .NET payroll API built$(NC)"

build-frontend: ## Build frontend
	@echo "$(CYAN)Building frontend...$(NC)"
	@cd frontend && npm run build
	@echo "$(GREEN)✓ Frontend built$(NC)"

##@ Testing

test: test-orchestrator test-python-agent ## Run all tests

test-orchestrator: ## Run orchestrator tests
	@echo "$(CYAN)Running orchestrator tests...$(NC)"
	@cd orchestrator && uv run --prerelease=allow pytest
	@echo "$(GREEN)✓ Orchestrator tests passed$(NC)"

test-python-agent: ## Run Python agent tests
	@echo "$(CYAN)Running Python agent tests...$(NC)"
	@cd python-agent && uv run --prerelease=allow pytest
	@echo "$(GREEN)✓ Python agent tests passed$(NC)"

test-dotnet-agent: ## Run .NET agent tests (when available)
	@echo "$(YELLOW)⚠ .NET agent tests not yet implemented$(NC)"

test-dotnet-payroll: ## Run .NET payroll API tests (when available)
	@echo "$(YELLOW)⚠ .NET payroll API tests not yet implemented$(NC)"

##@ Run Individual Services

run-orchestrator: ## Run orchestrator service (port 8001)
	@echo "$(CYAN)Starting orchestrator on port 8001...$(NC)"
	@cd orchestrator && uv run --prerelease=allow uvicorn src.main:app --reload --port 8001

run-python-agent: ## Run Python agent service (port 8000)
	@echo "$(CYAN)Starting Python agent on port 8000...$(NC)"
	@cd python-agent && uv run --prerelease=allow uvicorn src.main:app --reload --port 8000

run-dotnet-agent: ## Run .NET agent service (port 5000)
	@echo "$(CYAN)Starting .NET agent on port 5000...$(NC)"
	@cd dotnet-agent && dotnet run --project AgentService

run-dotnet-payroll: ## Run .NET payroll API service (port 5100)
	@echo "$(CYAN)Starting .NET payroll API on port 5100...$(NC)"
	@cd dotnet-payroll-api && dotnet run --project PayrollApi

run-frontend: ## Run frontend development server (port 3001)
	@echo "$(CYAN)Starting frontend on port 3001...$(NC)"
	@cd frontend && npm run dev -- --port 3001

##@ Run All Services

run-all: ## Run all services concurrently (requires tmux or separate terminals)
	@echo "$(YELLOW)Starting all services...$(NC)"
	@echo "$(YELLOW)Note: This requires 5 separate terminals. Use 'make dev' for automatic tmux setup.$(NC)"
	@echo ""
	@echo "Terminal 1: $(CYAN)make run-python-agent$(NC)    (port 8000)"
	@echo "Terminal 2: $(CYAN)make run-dotnet-agent$(NC)    (port 5000)"
	@echo "Terminal 3: $(CYAN)make run-dotnet-payroll$(NC)  (port 5100)"
	@echo "Terminal 4: $(CYAN)make run-orchestrator$(NC)    (port 8001)"
	@echo "Terminal 5: $(CYAN)make run-frontend$(NC)        (port 3001)"

dev: check-tmux ## Start all services in tmux session (recommended)
	@echo "$(CYAN)Starting all services in tmux session 'af-poc'...$(NC)"
	@tmux new-session -d -s af-poc -n python-agent "cd python-agent && uv run --prerelease=allow uvicorn src.main:app --reload --port 8000"
	@tmux new-window -t af-poc -n dotnet-agent "cd dotnet-agent && dotnet run --project AgentService"
	@tmux new-window -t af-poc -n dotnet-payroll "cd dotnet-payroll-api && dotnet run --project PayrollApi"
	@tmux new-window -t af-poc -n orchestrator "cd orchestrator && uv run --prerelease=allow uvicorn src.main:app --reload --port 8001"
	@tmux new-window -t af-poc -n frontend "cd frontend && npm run dev -- --port 3001"
	@echo "$(GREEN)✓ All services started in tmux session 'af-poc'$(NC)"
	@echo ""
	@echo "$(CYAN)Attach to session:$(NC) tmux attach -t af-poc"
	@echo "$(CYAN)List windows:$(NC)      Ctrl+b w"
	@echo "$(CYAN)Switch windows:$(NC)    Ctrl+b 0-4"
	@echo "$(CYAN)Detach session:$(NC)    Ctrl+b d"
	@echo "$(CYAN)Stop all services:$(NC) make stop-all"

check-tmux: ## Check if tmux is installed
	@command -v tmux >/dev/null 2>&1 || { echo "$(RED)✗ tmux not found. Install: brew install tmux$(NC)"; exit 1; }

stop-all: ## Stop all services running in tmux session
	@echo "$(YELLOW)Stopping all services...$(NC)"
	@tmux kill-session -t af-poc 2>/dev/null || echo "$(YELLOW)No tmux session 'af-poc' found$(NC)"
	@echo "$(GREEN)✓ All services stopped$(NC)"

##@ Health & Status

health: ## Check health of all services
	@echo "$(CYAN)Checking service health...$(NC)"
	@echo ""
	@echo "$(CYAN)Python Agent (port 8000):$(NC)"
	@curl -s http://localhost:8000/health 2>/dev/null | python3 -m json.tool || echo "$(RED)✗ Not responding$(NC)"
	@echo ""
	@echo "$(CYAN).NET Agent (port 5000):$(NC)"
	@curl -s http://localhost:5000/health 2>/dev/null | python3 -m json.tool || echo "$(RED)✗ Not responding$(NC)"
	@echo ""
	@echo "$(CYAN).NET Payroll API (port 5100):$(NC)"
	@curl -s http://localhost:5100/health 2>/dev/null | python3 -m json.tool || echo "$(RED)✗ Not responding$(NC)"
	@echo ""
	@echo "$(CYAN)Orchestrator (port 8001):$(NC)"
	@curl -s http://localhost:8001/health/agents 2>/dev/null | python3 -m json.tool || echo "$(RED)✗ Not responding$(NC)"
	@echo ""
	@echo "$(CYAN)Frontend (port 3001):$(NC)"
	@curl -s -o /dev/null -w "%{http_code}" http://localhost:3001 2>/dev/null | grep -q "200" && echo "$(GREEN)✓ Responding$(NC)" || echo "$(RED)✗ Not responding$(NC)"

status: health ## Alias for health check

##@ Clean

clean: clean-orchestrator clean-python-agent clean-dotnet-agent clean-dotnet-payroll clean-frontend ## Clean all build artifacts

clean-orchestrator: ## Clean orchestrator build artifacts
	@echo "$(CYAN)Cleaning orchestrator...$(NC)"
	@cd orchestrator && rm -rf .pytest_cache __pycache__ src/__pycache__ tests/__pycache__
	@echo "$(GREEN)✓ Orchestrator cleaned$(NC)"

clean-python-agent: ## Clean Python agent build artifacts
	@echo "$(CYAN)Cleaning Python agent...$(NC)"
	@cd python-agent && rm -rf .pytest_cache __pycache__ src/__pycache__ tests/__pycache__
	@echo "$(GREEN)✓ Python agent cleaned$(NC)"

clean-dotnet-agent: ## Clean .NET agent build artifacts
	@echo "$(CYAN)Cleaning .NET agent...$(NC)"
	@cd dotnet-agent && dotnet clean
	@echo "$(GREEN)✓ .NET agent cleaned$(NC)"

clean-dotnet-payroll: ## Clean .NET payroll API build artifacts
	@echo "$(CYAN)Cleaning .NET payroll API...$(NC)"
	@cd dotnet-payroll-api && dotnet clean
	@echo "$(GREEN)✓ .NET payroll API cleaned$(NC)"

clean-frontend: ## Clean frontend build artifacts
	@echo "$(CYAN)Cleaning frontend...$(NC)"
	@cd frontend && rm -rf .next
	@echo "$(GREEN)✓ Frontend cleaned$(NC)"

clean-all: clean ## Remove all build artifacts and dependencies
	@echo "$(YELLOW)Removing all dependencies and build artifacts...$(NC)"
	@rm -rf orchestrator/.venv
	@rm -rf python-agent/.venv
	@rm -rf dotnet-agent/bin dotnet-agent/obj
	@rm -rf dotnet-payroll-api/bin dotnet-payroll-api/obj
	@rm -rf frontend/.next frontend/node_modules
	@echo "$(GREEN)✓ All artifacts removed$(NC)"

##@ Quick Tests

test-flow: ## Test the complete orchestration flow
	@echo "$(CYAN)Testing orchestration flow...$(NC)"
	@echo ""
	@echo "$(CYAN)Test 1: Python agent selection$(NC)"
	@curl -s -X POST http://localhost:8001/agent \
		-H "Content-Type: application/json" \
		-d '{"message": "Help me with pandas dataframes"}' | python3 -m json.tool
	@echo ""
	@echo "$(CYAN)Test 2: .NET agent selection$(NC)"
	@curl -s -X POST http://localhost:8001/agent \
		-H "Content-Type: application/json" \
		-d '{"message": "Help me with ASP.NET Core"}' | python3 -m json.tool
	@echo ""
	@echo "$(CYAN)Test 3: Explicit Python agent$(NC)"
	@curl -s -X POST http://localhost:8001/agent \
		-H "Content-Type: application/json" \
		-d '{"message": "Hello", "preferred_agent": "python"}' | python3 -m json.tool

lint: lint-orchestrator lint-python-agent ## Run linting for all Python projects

lint-orchestrator: ## Lint orchestrator code
	@echo "$(CYAN)Linting orchestrator...$(NC)"
	@cd orchestrator && uv run --prerelease=allow ruff check src/ tests/ || true
	@echo "$(GREEN)✓ Orchestrator linted$(NC)"

lint-python-agent: ## Lint Python agent code
	@echo "$(CYAN)Linting Python agent...$(NC)"
	@cd python-agent && uv run --prerelease=allow ruff check src/ tests/ || true
	@echo "$(GREEN)✓ Python agent linted$(NC)"

format: format-orchestrator format-python-agent ## Format all Python code

format-orchestrator: ## Format orchestrator code
	@echo "$(CYAN)Formatting orchestrator...$(NC)"
	@cd orchestrator && uv run --prerelease=allow black src/ tests/
	@echo "$(GREEN)✓ Orchestrator formatted$(NC)"

format-python-agent: ## Format Python agent code
	@echo "$(CYAN)Formatting Python agent...$(NC)"
	@cd python-agent && uv run --prerelease=allow black src/ tests/
	@echo "$(GREEN)✓ Python agent formatted$(NC)"

##@ Information

ports: ## Show port allocations
	@echo "$(CYAN)Service Port Allocation:$(NC)"
	@echo ""
	@echo "  $(GREEN)Python Agent:$(NC)      http://localhost:8000"
	@echo "  $(GREEN).NET Agent:$(NC)        http://localhost:5000"
	@echo "  $(GREEN).NET Payroll API:$(NC)  http://localhost:5100"
	@echo "  $(GREEN)Orchestrator:$(NC)      http://localhost:8001"
	@echo "  $(GREEN)Frontend:$(NC)          http://localhost:3001"

endpoints: ## Show available API endpoints
	@echo "$(CYAN)Available Endpoints:$(NC)"
	@echo ""
	@echo "$(GREEN)Orchestrator (port 8001):$(NC)"
	@echo "  POST /agent            - Main orchestration endpoint"
	@echo "  GET  /health/agents    - Health check for all agents"
	@echo ""
	@echo "$(GREEN)Python Agent (port 8000):$(NC)"
	@echo "  POST /agent            - Python agent endpoint"
	@echo "  GET  /health           - Health check"
	@echo ""
	@echo "$(GREEN).NET Agent (port 5000):$(NC)"
	@echo "  POST /agent            - .NET agent endpoint"
	@echo "  GET  /health           - Health check"
	@echo ""
	@echo "$(GREEN).NET Payroll API (port 5100):$(NC)"
	@echo "  GET  /payroll/user-info - Get user information"
	@echo "  GET  /payroll/user-pto  - Get PTO balance"
	@echo "  GET  /health            - Health check"
	@echo ""
	@echo "$(GREEN)Frontend (port 3001):$(NC)"
	@echo "  Web UI                 - Main application interface"

info: ports endpoints ## Show all service information
