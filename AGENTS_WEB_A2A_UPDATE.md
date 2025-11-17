# agents_web A2A Update Summary

## Overview

The `/home/ed/kaggle/recipe/agents_web/recipe_meal_planner` directory has been updated to use the new A2A (Agent-to-Agent) architecture instead of the traditional `LangGraphAgent` wrapper.

## Changes Made

### 1. Updated `agent.py`

**Before:**
```python
from agents.orchestrator import orchestrator
root_agent = orchestrator
```

**After:**
```python
from orchestrator_a2a import get_orchestrator_a2a
orchestrator_a2a = get_orchestrator_a2a()
root_agent = orchestrator_a2a
```

**Key Changes:**
- ✅ Imports `orchestrator_a2a` instead of `orchestrator`
- ✅ Adds server health check on startup
- ✅ Displays helpful error messages if A2A server is not running
- ✅ Shows architecture information when server is detected

### 2. Created `README.md`

Comprehensive documentation including:
- Architecture diagram
- Prerequisites
- Step-by-step setup instructions
- Troubleshooting guide
- Benefits of A2A approach
- Reference links

### 3. Created `start_a2a_web.sh`

Convenience script that:
- Checks for `.env` file and `GOOGLE_API_KEY`
- Starts Recipe Planner A2A Server (port 8001)
- Waits for server to be ready
- Starts ADK Web Interface (port 8000)
- Handles cleanup on exit

## How to Use

### Quick Start

```bash
# Run the startup script
./start_a2a_web.sh
```

This will:
1. Start Recipe Planner A2A Server on port 8001
2. Start ADK Web Interface on port 8000
3. Open browser to http://localhost:8000

### Manual Start (2 Terminals)

**Terminal 1 - Start A2A Server:**
```bash
python recipe_planner_a2a_server.py
```

**Terminal 2 - Start Web Interface:**
```bash
adk web --agent_path agents_web/recipe_meal_planner
```

### Access

Open browser: http://localhost:8000

## Architecture Comparison

### Traditional Setup (Before)

```
Browser → ADK Web UI → Orchestrator → LangGraphAgent → LangGraph
                           ↓
                      Code Agent (Local)
```

**Characteristics:**
- In-process communication
- Monolithic architecture
- Uses `google.adk.agents.langgraph_agent.LangGraphAgent`

### A2A Setup (After)

```
Browser → ADK Web UI → Orchestrator → RemoteA2aAgent → [A2A/HTTP] → Recipe Planner Server
                           ↓                                           ↓
                      Code Agent (Local)                         LangGraph
```

**Characteristics:**
- Network communication (HTTP/JSON-RPC)
- Distributed microservices architecture
- **No `LangGraphAgent` dependency**
- Recipe Planner runs as independent server on port 8001

## Benefits of A2A Web Setup

1. **Separation of Concerns**
   - Recipe planning logic isolated in separate service
   - Orchestrator only coordinates

2. **Independent Scaling**
   - Recipe Planner can scale horizontally
   - Web UI can scale independently

3. **Framework Agnostic**
   - Recipe Planner could be rebuilt in any framework
   - As long as it exposes A2A protocol

4. **Development Flexibility**
   - Can update Recipe Planner without touching web UI
   - Can test Recipe Planner independently

5. **Deployment Options**
   - Recipe Planner can be deployed to Cloud Run, Kubernetes, etc.
   - Web UI can be deployed separately
   - Different teams can own different services

## Key Components

### Recipe Planner A2A Server (`recipe_planner_a2a_server.py`)

```python
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from recipe_planner_a2a_agent import get_recipe_planner_agent

recipe_planner_agent = get_recipe_planner_agent()
app = to_a2a(recipe_planner_agent, port=8001)
```

**What it does:**
- Wraps LangGraph state machine in ADK agent (without LangGraphAgent)
- Exposes via A2A protocol on port 8001
- Auto-generates agent card at `/.well-known/agent-card.json`

### Orchestrator A2A (`agents/orchestrator_a2a.py`)

```python
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

remote_recipe_planner_agent = RemoteA2aAgent(
    name="recipe_planner_agent",
    agent_card="http://localhost:8001/.well-known/agent-card.json"
)

orchestrator_a2a = AdkAgent(
    tools=[
        agent_tool.AgentTool(agent=remote_recipe_planner_agent),  # Remote!
        agent_tool.AgentTool(agent=code_savvy_agent_builtin)      # Local
    ]
)
```

**What it does:**
- Creates `RemoteA2aAgent` proxy for Recipe Planner
- Translates agent calls to A2A HTTP requests
- Coordinates between remote and local agents

### Web Interface Agent (`agents_web/recipe_meal_planner/agent.py`)

```python
from orchestrator_a2a import get_orchestrator_a2a

# Check if server is running
if not check_server():
    print("WARNING: Recipe Planner A2A Server is NOT running!")
else:
    print("✅ Recipe Planner A2A Server detected!")

orchestrator_a2a = get_orchestrator_a2a()
root_agent = orchestrator_a2a
```

**What it does:**
- Loads A2A orchestrator for web UI
- Checks server health on startup
- Displays helpful messages

## Verification

### Test Server is Running

```bash
curl http://localhost:8001/.well-known/agent-card.json | python -m json.tool
```

Expected output:
```json
{
  "name": "recipe_planner_agent",
  "description": "Recipe planning agent that creates meal plans...",
  "protocolVersion": "0.3.0",
  "url": "http://localhost:8001",
  "skills": [...]
}
```

### Test Web Agent Loads

```bash
python -c "
import sys
sys.path.insert(0, 'agents_web/recipe_meal_planner')
from agent import root_agent
print(f'Agent: {root_agent.name}')
"
```

Expected output:
```
✅ Recipe Planner A2A Server detected!
   Server URL: http://localhost:8001
   ...
Agent: meal_plan_orchestrator_a2a
```

## Troubleshooting

### Web UI shows "Recipe Planner A2A Server is NOT running"

**Cause:** A2A server not started

**Solution:**
```bash
# Start the server
python recipe_planner_a2a_server.py
```

### Server fails with "Missing key inputs argument"

**Cause:** GOOGLE_API_KEY not set

**Solution:**
```bash
# Check .env file
cat .env | grep GOOGLE_API_KEY

# If missing, add it
echo "GOOGLE_API_KEY=your_api_key_here" >> .env
```

### Port 8001 already in use

**Solution:**
```bash
# Kill existing process
lsof -ti:8001 | xargs kill -9
```

## Rollback to Traditional Setup

If you need to switch back to the traditional setup:

```python
# In agents_web/recipe_meal_planner/agent.py
from agents.orchestrator import orchestrator
root_agent = orchestrator
```

Then restart the web interface:
```bash
adk web --agent_path agents_web/recipe_meal_planner
```

## Files Summary

### Modified Files
- `agents_web/recipe_meal_planner/agent.py` - Updated to use orchestrator_a2a

### New Files
- `agents_web/recipe_meal_planner/README.md` - Documentation
- `start_a2a_web.sh` - Startup script

### Related Files (Already Created)
- `recipe_planner_a2a_agent.py` - LangGraph wrapper without LangGraphAgent
- `recipe_planner_a2a_server.py` - A2A server
- `agents/orchestrator_a2a.py` - A2A orchestrator
- `recipe_meal_planner_a2a.py` - CLI version with A2A
- `test_a2a_communication.py` - Test suite

## Next Steps

1. **Test the web interface:**
   ```bash
   ./start_a2a_web.sh
   ```

2. **Try a meal plan:**
   - Open http://localhost:8000
   - Enter: "Plan 5 vegetarian dinners under $50"
   - Watch A2A communication in action

3. **Monitor A2A traffic:**
   ```bash
   # In another terminal, watch server logs
   tail -f /tmp/a2a_server.log
   ```

4. **Deploy to production:**
   - Deploy Recipe Planner to Cloud Run
   - Update `RECIPE_PLANNER_A2A_URL` in `agents/orchestrator_a2a.py`
   - Deploy Web UI separately

## Conclusion

The agents_web directory now uses the A2A architecture, demonstrating:
- ✅ No dependency on `LangGraphAgent`
- ✅ Distributed microservices architecture
- ✅ A2A protocol communication
- ✅ Production-ready setup
- ✅ Easy to scale and deploy

The web interface works exactly the same from the user's perspective, but the underlying architecture is now distributed and A2A-compliant.
