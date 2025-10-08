"""Main FastAPI application entry point for orchestrator."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api import router
from src.config import settings
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app = FastAPI(
    title="Orchestrator Service",
    description="Microsoft Agent Framework POC - Orchestrator with OBO Flow",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "orchestrator",
        "auth_required": settings.REQUIRE_AUTH,
    }


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Microsoft Agent Framework Orchestrator",
        "version": "0.1.0",
        "description": "Orchestrator service demonstrating JWT OBO flow with sub-agents",
        "endpoints": {
            "main": "POST /agent",
            "status": "GET /agent",
            "health": "GET /health",
            "sub_agent_health": "GET /health/agents",
        },
        "configuration": {
            "auth_required": settings.REQUIRE_AUTH,
            "python_agent": settings.PYTHON_AGENT_URL,
            "dotnet_agent": settings.DOTNET_AGENT_URL,
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)
