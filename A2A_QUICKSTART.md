# A2A Communication Quick Start Guide

## What You'll Build

A distributed multi-agent system where:
- **Recipe Planner Agent** (LangGraph) runs as an independent A2A server
- **Orchestrator Agent** (ADK) consumes it via A2A protocol
- Communication happens over HTTP using the A2A standard

## Prerequisites

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up your Google API key
export GOOGLE_API_KEY="your_api_key_here"

# 3. Verify MCP server exists
ls recipe_mcp_server.py
```

## Quick Start (3 Steps)

### Step 1: Start the Recipe Planner A2A Server

Open **Terminal 1**:

```bash
python recipe_planner_a2a_server.py
```

**Expected output:**
```
🚀 Starting Recipe Planner A2A Server
============================================================
   Agent: recipe_planner_agent
   Description: Recipe planning agent that creates meal plans...
   Server URL: http://localhost:8001
   Agent Card: http://localhost:8001/.well-known/agent-card.json
   Protocol: A2A (Agent-to-Agent)
============================================================

Server is starting...
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://localhost:8001
```

✅ **Server is ready when you see "Uvicorn running on..."**

### Step 2: Verify the Server (Optional)

Open **Terminal 2**:

```bash
# Check the agent card
curl http://localhost:8001/.well-known/agent-card.json | python -m json.tool
```

**Expected output:**
```json
{
  "name": "recipe_planner_agent",
  "description": "Recipe planning agent that creates meal plans based on dietary preferences...",
  "protocolVersion": "0.3.0",
  "url": "http://localhost:8001",
  "skills": [
    {
      "id": "recipe_planner_agent",
      "name": "model",
      "description": "...",
      "tags": ["llm"]
    },
    {
      "id": "recipe_planner_agent-run_recipe_planner",
      "name": "run_recipe_planner",
      "description": "Tool function that runs the LangGraph recipe planning workflow.",
      "tags": ["llm", "tools"]
    }
  ]
}
```

✅ **If you see JSON with the agent details, the server is working!**

### Step 3: Run the Test

In **Terminal 2** (or keep Terminal 1 running and open a new terminal):

```bash
python test_a2a_communication.py
```

**Expected flow:**

1. **Server Check:**
```
🧪 A2A COMMUNICATION TEST
   Orchestrator Agent (ADK) ←→ Recipe Planner Agent (LangGraph)
======================================================================

🔍 Step 1: Checking Recipe Planner A2A Server...
   URL: http://localhost:8001
   ✅ Recipe Planner A2A Server is running!
   Agent: recipe_planner_agent
   Skills: 2 available
```

2. **A2A Communication:**
```
🔍 Step 2: Testing A2A Communication...
   The following will happen:
   1. Orchestrator receives user request
   2. Orchestrator sends A2A request to Recipe Planner (port 8001)
   3. Recipe Planner executes LangGraph workflow
   4. Recipe Planner returns results via A2A
   5. Orchestrator processes results with code agent
   6. Orchestrator returns final meal plan
```

3. **Test Case Execution:**
```
======================================================================
👤 USER REQUEST
======================================================================
Plan 3 vegetarian dinners for me under $50 budget
======================================================================

🔄 ORCHESTRATOR PROCESSING (with A2A communication)...
======================================================================

[... agent processing ...]

======================================================================
✅ FINAL MEAL PLAN
======================================================================
Here is your meal plan:

1. Vegetable Stir-Fry
2. Margherita Pizza
3. Chickpea Curry

Here is your shopping list:

* bell pepper: 2 cups
* soy sauce: 2 tbsp
* pizza dough: 1 lb
* mozzarella: 8 oz
...

And here are the estimated prices:

* bell pepper (2 cups): $3.98
* soy sauce (2 tbsp): $0.60
...

Total cost: $42.50
Enjoy your meals!
======================================================================
```

4. **Test Completion:**
```
✅ A2A COMMUNICATION TEST COMPLETED
======================================================================

Key Achievements:
  ✓ Orchestrator Agent (ADK) successfully created
  ✓ Recipe Planner Agent (LangGraph) exposed via A2A
  ✓ A2A communication protocol working
  ✓ RemoteA2aAgent successfully consumed remote agent
  ✓ Complete request-response cycle demonstrated
======================================================================
```

## What Just Happened?

### The A2A Communication Flow

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│    User     │────1───▶│ Orchestrator │────2───▶│   Recipe    │
│             │         │  Agent (ADK) │   A2A   │   Planner   │
│             │         │              │◀───3────│ (LangGraph) │
│             │         │              │         │  Server     │
│             │         │     +        │         │   :8001     │
│             │         │     │        │         └─────────────┘
│             │         │     │4       │
│             │         │     ▼        │
│             │         │   Code       │
│             │         │   Agent      │
│             │◀───5────│  (Local)     │
└─────────────┘         └──────────────┘
```

**Step by step:**

1. **User Request** → Orchestrator Agent
   - "Plan 3 vegetarian dinners under $50"

2. **Orchestrator** → Recipe Planner via **A2A Protocol**
   - HTTP POST to `http://localhost:8001/tasks`
   - Request: `{"input": "Plan 3 vegetarian dinners...", "task_id": "..."}`

3. **Recipe Planner** executes **LangGraph State Machine**:
   - `gather_preferences_node`: Extract preferences using LLM
   - `suggest_recipes_node`: Query recipes via MCP client
   - `check_overlap_node`: Find ingredient overlap
   - `optimize_list_node`: Consolidate grocery list
   - Returns via **A2A response**

4. **Orchestrator** → Local Code Agent
   - Calculate costs from ingredient list
   - Verify budget compliance

5. **Orchestrator** → User
   - Complete meal plan with recipes, shopping list, prices

## Key Files Explained

### 1. `recipe_planner_a2a_agent.py`
**Purpose:** Wraps LangGraph in an ADK agent (without LangGraphAgent)

**Key code:**
```python
def run_recipe_planner(user_request: str) -> str:
    """Tool that executes LangGraph workflow"""
    recipe_graph = get_recipe_graph()
    initial_state = {"messages": [HumanMessage(content=user_request)], ...}
    final_state = recipe_graph.invoke(initial_state, config)
    return response

recipe_planner_agent = AdkAgent(
    name="recipe_planner_agent",
    tools=[run_recipe_planner]  # LangGraph as a tool!
)
```

### 2. `recipe_planner_a2a_server.py`
**Purpose:** Exposes Recipe Planner via A2A protocol

**Key code:**
```python
from google.adk.a2a.utils.agent_to_a2a import to_a2a

app = to_a2a(recipe_planner_agent, port=8001)
# Creates FastAPI app with:
# - A2A endpoints (/tasks, /tasks/{task_id})
# - Agent card at /.well-known/agent-card.json
# - JSON-RPC over HTTP protocol
```

### 3. `agents/orchestrator_a2a.py`
**Purpose:** Orchestrator that consumes Recipe Planner via A2A

**Key code:**
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

### 4. `test_a2a_communication.py`
**Purpose:** Test script demonstrating A2A communication

**Key code:**
```python
# Check server
is_running, agent_card = check_recipe_planner_server()

# Run test
orchestrator = get_orchestrator_a2a()
runner = Runner(agent=orchestrator, ...)
async for event in runner.run_async(...):
    print(event.content)  # Final meal plan
```

## Common Issues

### Issue 1: Server not starting

**Error:** `Address already in use`

**Solution:**
```bash
# Kill process on port 8001
lsof -ti:8001 | xargs kill -9

# Or use a different port in recipe_planner_a2a_server.py
app = to_a2a(recipe_planner_agent, port=8002)
```

### Issue 2: Connection refused

**Error:** `Failed to connect to Recipe Planner`

**Solution:**
1. Verify server is running: `curl http://localhost:8001/.well-known/agent-card.json`
2. Check server terminal for errors
3. Restart the server

### Issue 3: LangGraph not available

**Error:** `LangGraph is not available`

**Solution:**
```bash
pip install langgraph==0.6.11 langchain-core==1.0.5
```

### Issue 4: MCP errors

**Error:** `MCP client connection failed`

**Solution:**
1. Verify `recipe_mcp_server.py` exists
2. Check MCP dependencies: `pip install fastmcp>=2.0.0`

### Issue 5: API key errors

**Error:** `GOOGLE_API_KEY not set`

**Solution:**
```bash
export GOOGLE_API_KEY="your_api_key_here"
# Or create a .env file:
echo "GOOGLE_API_KEY=your_api_key_here" > .env
```

## Stopping the Server

Press **Ctrl+C** in Terminal 1 where the server is running:

```
^C
INFO:     Shutting down
INFO:     Finished server process [12345]
```

## Next Steps

1. **Read the full documentation:** `A2A_IMPLEMENTATION.md`
2. **Explore the code:** Look at each file to understand the implementation
3. **Modify and experiment:**
   - Change the number of recipes
   - Add different dietary preferences
   - Modify the LangGraph workflow
4. **Deploy to production:**
   - Deploy Recipe Planner to Cloud Run
   - Update agent card URL
   - Add authentication

## Resources

- **A2A Protocol:** https://a2a-protocol.org/
- **ADK A2A Docs:** https://google.github.io/adk-docs/a2a/
- **Reference Notebook:** `day-5a-agent2agent-communication.ipynb`

## Summary

You've successfully set up A2A communication between:
- ✅ Recipe Planner Agent (LangGraph) as an A2A server
- ✅ Orchestrator Agent (ADK) as an A2A consumer
- ✅ Complete request-response cycle over HTTP
- ✅ No `LangGraphAgent` wrapper needed!

**The key insight:** By wrapping the LangGraph execution in a tool function and exposing it via `to_a2a()`, we achieve clean separation and A2A compatibility without the framework-specific wrapper.
