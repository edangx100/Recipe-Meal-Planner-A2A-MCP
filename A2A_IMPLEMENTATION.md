# Agent-to-Agent (A2A) Communication Implementation

## Overview

This implementation demonstrates Agent-to-Agent (A2A) communication between an **Orchestrator Agent** (ADK) and a **Recipe Planner Agent** (LangGraph) without using the `LangGraphAgent` wrapper from `google.adk.agents.langgraph_agent`.

## Architecture

```
┌──────────────────────────────────┐         A2A Protocol         ┌──────────────────────────────────┐
│   Orchestrator Agent (ADK)       │ ◄────────────────────────── │   Recipe Planner Agent           │
│   - Coordinates meal planning    │      HTTP/JSON-RPC           │   (LangGraph State Machine)      │
│   - Consumes remote agent        │                              │   - Recipe selection workflow    │
│   - Uses RemoteA2aAgent          │                              │   - Exposed via to_a2a()         │
│   - Local code execution agent   │                              │   - MCP integration              │
│                                  │                              │                                  │
│   Port: N/A (client)             │                              │   Port: 8001 (server)            │
└──────────────────────────────────┘                              └──────────────────────────────────┘
```

## Key Components

### 1. Recipe Planner Agent (Provider/Server)

**File:** `recipe_planner_a2a_agent.py`

This module creates an ADK-compatible agent that wraps the LangGraph state machine without using `LangGraphAgent`:

- **Approach:** Created a tool function `run_recipe_planner()` that executes the LangGraph workflow
- **Agent Type:** `Agent` (ADK) with the tool function registered
- **LangGraph Integration:** Direct invocation of the compiled graph from `langgraph_agent_mcp.py`
- **Key Feature:** Wraps async LangGraph execution in a synchronous tool interface

**How it works:**
```python
def run_recipe_planner(user_request: str) -> str:
    """Tool that runs LangGraph state machine"""
    recipe_graph = get_recipe_graph()
    initial_state = {"messages": [HumanMessage(content=user_request)], ...}
    final_state = recipe_graph.invoke(initial_state, config)
    return formatted_response

recipe_planner_agent = AdkAgent(
    name="recipe_planner_agent",
    tools=[run_recipe_planner]  # LangGraph wrapped as a tool
)
```

### 2. Recipe Planner A2A Server

**File:** `recipe_planner_a2a_server.py`

Exposes the Recipe Planner Agent via A2A protocol:

```python
from google.adk.a2a.utils.agent_to_a2a import to_a2a

app = to_a2a(recipe_planner_agent, port=8001)
```

**What `to_a2a()` provides:**
- FastAPI/Starlette application with A2A endpoints
- Auto-generated agent card at `/.well-known/agent-card.json`
- JSON-RPC over HTTP protocol handling
- Task management endpoints (`/tasks`, `/tasks/{task_id}`)

**Agent Card:** Describes the agent's capabilities, skills, and protocol version

**Run the server:**
```bash
python recipe_planner_a2a_server.py
# or
uvicorn recipe_planner_a2a_server:app --host localhost --port 8001
```

### 3. Orchestrator Agent (Consumer/Client)

**File:** `agents/orchestrator_a2a.py`

Coordinates between the remote Recipe Planner Agent and local code execution agent:

```python
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

# Create client-side proxy for remote agent
remote_recipe_planner_agent = RemoteA2aAgent(
    name="recipe_planner_agent",
    agent_card="http://localhost:8001/.well-known/agent-card.json"
)

# Create orchestrator with both remote and local agents
orchestrator_a2a = AdkAgent(
    name="meal_plan_orchestrator_a2a",
    tools=[
        agent_tool.AgentTool(agent=remote_recipe_planner_agent),  # Remote via A2A
        agent_tool.AgentTool(agent=code_savvy_agent_builtin)      # Local
    ]
)
```

**How RemoteA2aAgent works:**
- Reads the remote agent's card from the URL
- Translates agent calls into A2A protocol requests (HTTP POST to `/tasks`)
- Handles all protocol details transparently
- Acts like a local agent from the orchestrator's perspective

### 4. Test Script

**File:** `test_a2a_communication.py`

Demonstrates the complete A2A communication flow:

1. Checks if Recipe Planner A2A server is running
2. Creates a session for the orchestrator
3. Sends user request to orchestrator
4. Orchestrator delegates to remote Recipe Planner via A2A
5. Recipe Planner executes LangGraph workflow
6. Orchestrator receives results and processes with code agent
7. Returns complete meal plan to user

**Run the test:**
```bash
# Terminal 1: Start the server
python recipe_planner_a2a_server.py

# Terminal 2: Run the test
python test_a2a_communication.py
```

## Communication Flow

### Detailed Request-Response Cycle

```
1. User → Orchestrator Agent
   "Plan 3 vegetarian dinners under $50"

2. Orchestrator → Remote Recipe Planner (via A2A)
   POST http://localhost:8001/tasks
   {
     "input": "Plan 3 vegetarian dinners...",
     "task_id": "..."
   }

3. Recipe Planner Server → LangGraph State Machine
   - gather_preferences_node: Extract preferences using LLM
   - suggest_recipes_node: Query recipes via MCP
   - check_overlap_node: Find ingredient overlap
   - optimize_list_node: Consolidate grocery list

4. Recipe Planner → Orchestrator (A2A response)
   {
     "result": "Selected 3 recipes:\n1. ...\n\nOptimized grocery list:\n..."
   }

5. Orchestrator → Local Code Agent
   "Calculate costs for this grocery list: ..."

6. Code Agent → Orchestrator
   "Total cost: $42.50\nDetailed breakdown: ..."

7. Orchestrator → User
   Complete meal plan with recipes, shopping list, and costs
```

## Key Differences from LangGraphAgent Approach

| Aspect | Previous Approach | A2A Approach |
|--------|------------------|--------------|
| **Agent Wrapper** | Used `LangGraphAgent` class | Custom ADK agent with tool function |
| **LangGraph Integration** | Direct graph assignment | Wrapped in `run_recipe_planner()` tool |
| **Communication** | Local in-process calls | Remote A2A protocol over HTTP |
| **Deployment** | Single process | Distributed (server + client) |
| **Flexibility** | Framework-specific | Framework-agnostic (any A2A agent) |
| **Use Case** | Monolithic application | Microservices architecture |

## Advantages of A2A Approach

1. **Cross-Framework Integration:** Recipe Planner could be rebuilt in any framework that supports A2A
2. **Cross-Language Support:** Recipe Planner could be written in Java, Node.js, etc.
3. **Cross-Organization:** Recipe Planner could be an external vendor service
4. **Scalability:** Each agent can scale independently
5. **Separation of Concerns:** Clear boundaries between agents
6. **Microservices Architecture:** Agents as independent services
7. **Standard Protocol:** Uses A2A standard (https://a2a-protocol.org/)

## Files Created

1. **`recipe_planner_a2a_agent.py`** - ADK agent wrapper for LangGraph (without LangGraphAgent)
2. **`recipe_planner_a2a_server.py`** - A2A server that exposes the Recipe Planner
3. **`agents/orchestrator_a2a.py`** - Orchestrator that consumes Recipe Planner via A2A
4. **`test_a2a_communication.py`** - Test script demonstrating A2A communication

## Usage Instructions

### Step 1: Start the Recipe Planner A2A Server

```bash
# Make sure GOOGLE_API_KEY is set
export GOOGLE_API_KEY="your_api_key_here"

# Start the server
python recipe_planner_a2a_server.py
```

You should see:
```
🚀 Starting Recipe Planner A2A Server
   Agent: recipe_planner_agent
   Server URL: http://localhost:8001
   Agent Card: http://localhost:8001/.well-known/agent-card.json
```

### Step 2: Verify the Server is Running

```bash
# Check the agent card
curl http://localhost:8001/.well-known/agent-card.json

# You should see JSON with agent metadata
{
  "name": "recipe_planner_agent",
  "description": "Recipe planning agent...",
  "skills": [...],
  "url": "http://localhost:8001",
  ...
}
```

### Step 3: Run the Test Script

```bash
# In a new terminal
python test_a2a_communication.py
```

The test will:
1. Check if the server is running
2. Send test requests to the orchestrator
3. Demonstrate A2A communication
4. Display the complete meal plans

### Step 4: Use in Your Own Code

```python
from orchestrator_a2a import get_orchestrator_a2a
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# Get the orchestrator
orchestrator = get_orchestrator_a2a()

# Set up session
session_service = InMemorySessionService()
runner = Runner(agent=orchestrator, session_service=session_service)

# Send a request
async for event in runner.run_async(
    user_id="user123",
    session_id="session456",
    new_message="Plan 5 vegetarian dinners"
):
    if event.is_final_response():
        print(event.content)
```

## Troubleshooting

### Server not starting

**Issue:** `Address already in use`
**Solution:** Kill the process using port 8001:
```bash
lsof -ti:8001 | xargs kill -9
```

### A2A connection failed

**Issue:** `Failed to connect to Recipe Planner`
**Solution:**
1. Verify server is running: `curl http://localhost:8001/.well-known/agent-card.json`
2. Check firewall settings
3. Ensure correct URL in `agents/orchestrator_a2a.py`

### LangGraph not available

**Issue:** `LangGraph is not available`
**Solution:**
```bash
pip install langgraph==0.6.11 langchain-core==1.0.5
```

### MCP server errors

**Issue:** MCP client connection failed
**Solution:** Verify `recipe_mcp_server.py` exists and MCP is configured correctly

## References

- **A2A Protocol:** https://a2a-protocol.org/
- **ADK A2A Documentation:** https://google.github.io/adk-docs/a2a/
- **ADK Exposing Agents:** https://google.github.io/adk-docs/a2a/quickstart-exposing/
- **ADK Consuming Agents:** https://google.github.io/adk-docs/a2a/quickstart-consuming/
- **Reference Notebook:** `day-5a-agent2agent-communication.ipynb`

## Next Steps

1. **Deploy to Production:**
   - Deploy Recipe Planner to Cloud Run or Agent Engine
   - Update agent card URL to production endpoint
   - Add authentication (API keys, OAuth)

2. **Add More Agents:**
   - Create Inventory Agent via A2A
   - Create Nutrition Agent via A2A
   - Orchestrator coordinates all via A2A

3. **Enhance Error Handling:**
   - Add retry logic for A2A requests
   - Implement circuit breaker pattern
   - Add health check endpoints

4. **Monitoring and Logging:**
   - Add structured logging
   - Track A2A request/response times
   - Monitor agent performance

## Conclusion

This implementation demonstrates a clean separation between the Orchestrator Agent (ADK) and Recipe Planner Agent (LangGraph) using the A2A protocol, without relying on the `LangGraphAgent` wrapper. This approach provides maximum flexibility for distributed, cross-framework agent communication.
