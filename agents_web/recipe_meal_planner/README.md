# Recipe Meal Planner - A2A Web Interface

This is the A2A (Agent-to-Agent) version of the Recipe Meal Planner web interface.

## Architecture

```
┌─────────────┐         ┌──────────────────┐         ┌─────────────────────┐
│   Browser   │────────▶│   ADK Web UI     │────────▶│   Orchestrator      │
│   (User)    │         │   (Frontend)     │   A2A   │   (orchestrator_    │
│             │         │                  │◄────────│    agent.py)        │
└─────────────┘         └──────────────────┘         └──────────┬──────────┘
                                                                 │
                                                                 │ A2A Protocol
                                                                 │ (HTTP/JSON-RPC)
                                                                 ▼
                                                      ┌─────────────────────┐
                                                      │  Recipe Planner     │
                                                      │  A2A Server         │
                                                      │  (LangGraph)        │
                                                      │  Port: 8001         │
                                                      └─────────────────────┘
```

## Prerequisites

1. **Recipe Planner A2A Server must be running on port 8001**
2. Environment variables loaded (GOOGLE_API_KEY)

## How to Run

### Step 1: Start the Recipe Planner A2A Server

Open **Terminal 1**:

```bash
cd /home/ed/kaggle/recipe
python recipe_planner_a2a_server.py
```

You should see:
```
🚀 Starting Recipe Planner A2A Server
============================================================
   Agent: recipe_planner_agent
   Server URL: http://localhost:8001
   Agent Card: http://localhost:8001/.well-known/agent-card.json
============================================================
INFO:     Uvicorn running on http://localhost:8001
```

### Step 2: Start the ADK Web Interface

Open **Terminal 2**:

```bash
cd /home/ed/kaggle/recipe
adk web --agent_path agents_web/recipe_meal_planner
```

You should see:
```
================================================================================
✅ Recipe Planner A2A Server detected!
================================================================================
   Server URL: http://localhost:8001
   Agent Card: http://localhost:8001/.well-known/agent-card.json
   Architecture: Distributed (A2A)
================================================================================

ADK Web UI starting...
```

### Step 3: Access the Web Interface

Open your browser and navigate to:
```
http://localhost:8000
```

## What Makes This A2A?

### Traditional Approach (agents/orchestrator.py):
- Uses `LangGraphAgent` wrapper
- In-process communication
- Monolithic architecture
- Recipe Planner embedded in orchestrator

### A2A Approach (agents/orchestrator_agent.py):
- ✅ **No LangGraphAgent** - Recipe Planner wrapped as a tool function
- ✅ **Network communication** - HTTP/JSON-RPC via A2A protocol
- ✅ **Distributed architecture** - Recipe Planner runs as independent server
- ✅ **RemoteA2aAgent** - Orchestrator consumes Recipe Planner remotely
- ✅ **Microservices** - Each agent can scale independently

## Key Components

### 1. Recipe Planner A2A Server (`recipe_planner_a2a_server.py`)
- Exposes Recipe Planner agent via A2A protocol
- Runs on port 8001
- Auto-generates agent card at `/.well-known/agent-card.json`
- Uses `to_a2a()` to create A2A-compatible server

### 2. Orchestrator A2A (`agents/orchestrator_agent.py`)
- Uses `RemoteA2aAgent` to connect to Recipe Planner
- Coordinates between Recipe Planner (remote) and Code Agent (local)
- Translates agent calls to A2A HTTP requests

### 3. Web Interface (`agent.py`)
- Exports `root_agent = orchestrator_a2a`
- Checks if A2A server is running on startup
- Displays helpful error messages if server is not available

## Benefits

1. **Separation of Concerns**: Recipe planning logic isolated from orchestration
2. **Independent Scaling**: Recipe Planner can scale separately from orchestrator
3. **Framework Agnostic**: Recipe Planner could be rebuilt in any framework
4. **Language Agnostic**: Could replace with Java, Node.js, etc. (as long as A2A compatible)
5. **Deployment Flexibility**: Can deploy to different infrastructure

## Troubleshooting

### Web UI shows "Recipe Planner A2A Server is NOT running"

**Solution:**
1. Check if server is running:
   ```bash
   curl http://localhost:8001/.well-known/agent-card.json
   ```
2. If not running, start it:
   ```bash
   python recipe_planner_a2a_server.py
   ```

### Server fails to start

**Issue:** Missing API key

**Solution:**
```bash
# Check if .env file exists and contains GOOGLE_API_KEY
cat .env | grep GOOGLE_API_KEY

# If not, create it:
echo "GOOGLE_API_KEY=your_api_key_here" >> .env
```

### Port 8001 already in use

**Solution:**
```bash
# Kill existing process
lsof -ti:8001 | xargs kill -9

# Or change port in agents/orchestrator_agent.py
# RECIPE_PLANNER_A2A_URL = "http://localhost:8002"
```

## Testing the A2A Setup

Test that A2A communication is working:

```bash
# Check server health
curl http://localhost:8001/.well-known/agent-card.json | python -m json.tool

# Run CLI test
python recipe_meal_planner_a2a.py

# Run full test suite
python test_a2a_communication.py
```

## Switching Between Traditional and A2A

### To use Traditional (with LangGraphAgent):
```python
# In agent.py
from agents.orchestrator import orchestrator
root_agent = orchestrator
```

### To use A2A (current):
```python
# In agent.py
from agents.orchestrator_agent import get_orchestrator_a2a
root_agent = get_orchestrator_a2a()
```

## References

- **A2A Protocol:** https://a2a-protocol.org/
- **ADK A2A Docs:** https://google.github.io/adk-docs/a2a/
- **Implementation Guide:** `../A2A_IMPLEMENTATION.md`
- **Quick Start Guide:** `../A2A_QUICKSTART.md`

## Summary

This web interface demonstrates a production-ready A2A architecture where:
- Recipe Planner runs as an independent microservice
- Orchestrator consumes it via standard A2A protocol
- No dependency on framework-specific wrappers (LangGraphAgent)
- Ready for distributed deployment
