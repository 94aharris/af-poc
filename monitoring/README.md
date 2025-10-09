# Agent Framework Observability Stack

This directory contains the complete observability and monitoring infrastructure for the Microsoft Agent Framework POC.

## Overview

The monitoring stack provides comprehensive telemetry collection, storage, and visualization for agent operations:

- **OpenTelemetry Collector**: Receives traces and metrics from the orchestrator
- **Tempo**: Distributed tracing backend for storing and querying traces
- **Jaeger**: Dedicated trace visualization UI with powerful search capabilities
- **Prometheus**: Time-series database for metrics storage
- **Grafana**: Visualization and dashboarding platform

## Quick Start

### 1. Start the Monitoring Stack

```bash
make monitoring-up
```

This will start all monitoring services in Docker containers.

### 2. Enable Telemetry in Orchestrator

Update your `orchestrator/.env` file with:

```bash
ENABLE_OTEL=true
OTLP_ENDPOINT=http://localhost:4317
ENABLE_SENSITIVE_DATA=false  # Set to true to log prompts/responses (use with caution)
```

### 3. Start the Orchestrator

```bash
make run-orchestrator
```

### 4. Access Trace Viewers

**Jaeger UI** (Recommended for trace exploration):
- Open http://localhost:16686 in your browser
- Select "agent-framework" from the Service dropdown
- Click "Find Traces" to see all traces
- No login required

**Grafana** (For dashboards and metrics):
- Open http://localhost:3001 in your browser
- Username: `admin`
- Password: `admin`
- The Agent Framework dashboard will be pre-loaded in the "Agent Framework" folder

## Available Commands

All commands are available via the Makefile:

```bash
make monitoring-up         # Start the monitoring stack
make monitoring-down       # Stop the monitoring stack
make monitoring-restart    # Restart the monitoring stack
make monitoring-logs       # View logs from all monitoring containers
make monitoring-status     # Check status of monitoring containers
make monitoring-clean      # Remove stack and all data volumes
```

## Service Endpoints

| Service | URL | Purpose |
|---------|-----|---------|
| **Jaeger UI** | http://localhost:16686 | **Trace visualization and exploration** |
| Grafana | http://localhost:3001 | Dashboards and visualization |
| Prometheus | http://localhost:9090 | Metrics database and query UI |
| Tempo | http://localhost:3200 | Distributed tracing backend |
| OTEL Collector | grpc://localhost:4317 | Telemetry ingestion (gRPC) |
| OTEL Collector | http://localhost:4318 | Telemetry ingestion (HTTP) |

## Architecture

```
┌─────────────────┐
│  Orchestrator   │
│  (agent-fwk)    │
└────────┬────────┘
         │ OTLP/gRPC
         │ :4317
         ▼
┌─────────────────┐
│ OTEL Collector  │
│                 │
└────┬───┬────┬───┘
     │   │    │
     │   │    │ Prometheus format
     │   │    ▼
     │   │  ┌─────────────┐
     │   │  │ Prometheus  │
     │   │  │  (Metrics)  │
     │   │  └──────┬──────┘
     │   │         │
     │   │ OTLP    │
     │   ▼         │
     │ ┌─────────┐ │
     │ │ Jaeger  │ │
     │ │(Traces) │ │
     │ └────┬────┘ │
     │      │      │
     │ OTLP │      │
     ▼      │      │
┌─────────┐ │      │
│  Tempo  │ │      │
│(Traces) │ │      │
└────┬────┘ │      │
     │      │      │
     └──┬───┴──────┘
        │
        ▼
  ┌──────────┐
  │ Grafana  │
  │Dashboard │
  └──────────┘
```

## What Gets Monitored

The agent-framework automatically instruments:

### Traces (Spans)

- `invoke_agent <agent_name>` - Agent invocation operations
- `chat <model_name>` - LLM chat completions
- `execute_tool <function_name>` - Function/tool executions

### Metrics

- Chat operation duration
- Token usage (prompt, completion, total)
- Function invocation duration
- Success/error rates

### Custom Instrumentation

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

## Configuration Files

### `docker-compose.yml`
Main orchestration file defining all monitoring services and their configuration.

### `otel-collector-config.yml`
OpenTelemetry Collector configuration:
- Receives telemetry via OTLP (gRPC and HTTP)
- Exports traces to Tempo
- Exports metrics to Prometheus

### `tempo-config.yml`
Tempo distributed tracing backend configuration:
- Local storage for traces
- OTLP receiver on port 4317

### `prometheus-config.yml`
Prometheus metrics scraping configuration:
- Scrapes OTEL Collector metrics
- 15-second scrape interval

### `grafana-datasources.yml`
Grafana data source provisioning:
- Prometheus (metrics)
- Tempo (traces)

### `grafana-dashboards.yml`
Grafana dashboard provisioning configuration.

### `dashboards/agent-framework-dashboard.json`
Pre-built dashboard from https://grafana.com/grafana/dashboards/24156-agent-framework/

## Environment Variables Reference

Set these in `orchestrator/.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `ENABLE_OTEL` | `false` | Enable OpenTelemetry instrumentation |
| `ENABLE_SENSITIVE_DATA` | `false` | Log prompts, responses, and function arguments (use with caution) |
| `OTLP_ENDPOINT` | None | OTLP endpoint URL (e.g., `http://localhost:4317`) |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | None | Azure Application Insights connection string (optional) |
| `VS_CODE_EXTENSION_PORT` | `4317` | Port for VS Code AI Toolkit extension |

## Dashboard Features

The Agent Framework dashboard provides:

1. **Performance Monitoring**
   - Average, 95th, and 99th percentile latencies
   - Operations per minute
   - Response time trends

2. **Token Usage & Cost Analysis**
   - Token consumption by operation
   - Estimated costs (customizable per model)
   - Token usage trends

3. **Error Analysis**
   - Error rates and counts
   - Recent error details
   - Root cause analysis

4. **Trace Exploration**
   - Interactive trace selection
   - Detailed span information
   - Agent workflow visualization

## Troubleshooting

### No data appearing in Grafana

1. Check orchestrator is running with telemetry enabled:
   ```bash
   # In orchestrator/.env
   ENABLE_OTEL=true
   OTLP_ENDPOINT=http://localhost:4317
   ```

2. Verify OTEL Collector is receiving data:
   ```bash
   make monitoring-logs
   # Look for "Trace received" or "Metric received" messages
   ```

3. Check orchestrator logs for telemetry setup:
   ```bash
   # Should see telemetry initialization messages
   ```

### Containers not starting

```bash
# Check container status
make monitoring-status

# View logs for errors
make monitoring-logs

# Clean and restart
make monitoring-clean
make monitoring-up
```

### Port conflicts

If you see port binding errors:
- Grafana: Change `3001:3000` in docker-compose.yml
- Prometheus: Change `9090:9090` in docker-compose.yml
- OTEL Collector: Change `4317:4317` in docker-compose.yml

## Data Persistence

Data is stored in Docker volumes:
- `tempo-data`: Trace data
- `prometheus-data`: Metrics data
- `grafana-data`: Dashboard configurations and settings

To remove all data:
```bash
make monitoring-clean
```

## Integration with Azure Application Insights

To export telemetry to Azure Application Insights (in addition to local monitoring):

1. Get your connection string from Azure Portal
2. Add to `orchestrator/.env`:
   ```bash
   APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=your-key-here;...
   ```

Both local (OTLP) and Azure exporters will be active simultaneously.

## Further Reading

- [Microsoft Agent Framework Observability Docs](https://learn.microsoft.com/en-us/agent-framework/user-guide/agents/agent-observability?pivots=programming-language-python)
- [OpenTelemetry Python Documentation](https://opentelemetry.io/docs/instrumentation/python/)
- [Grafana Dashboard: Agent Framework](https://grafana.com/grafana/dashboards/24156-agent-framework/)
