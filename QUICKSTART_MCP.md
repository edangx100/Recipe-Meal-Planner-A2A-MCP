# MCP Integration - Quick Start Guide

Get started with the Recipe MCP Server in 5 minutes!

## What is MCP?

**Model Context Protocol (MCP)** is a standard protocol for connecting AI agents with data sources and tools. Think of it as an API that your LLM can use to access external data.

## Quick Start

### Step 1: Install Dependencies

```bash
# Install FastMCP and other dependencies
uv pip install -r requirements.txt
```

### Step 2: Test the MCP Server

```bash
# Run the comprehensive test suite
python test_mcp_integration.py
```

Expected output:
```
✓ Successfully connected to MCP server
✓ All MCP server tool tests passed!
✓ All MCP client wrapper tests passed!
✓ LangGraph workflow completed successfully!
ALL TESTS COMPLETED!
```

### Step 3: Try the Examples

```bash
# Run example usage demonstrations
python example_mcp_usage.py
```

## What You Get

### 1. MCP Server (`recipe_mcp_server.py`)

A standalone server that exposes recipe database through 6 tools:

```python
# Search by name
search_recipes_by_name(query="pasta")

# Filter by dietary tags
filter_recipes_by_tags(tags=["vegetarian", "vegan"])

# Get full recipe details
get_recipe_details(recipe_name="Lentil Soup")

# List everything
list_all_recipes()

# Search by ingredient
search_by_ingredient(ingredient="chicken")

# Budget-friendly recipes
get_recipes_by_budget(max_budget=10.0)
```

### 2. LangGraph Agent with MCP (`agents/langgraph_agent_mcp.py`)

The LangGraph agent now uses MCP instead of direct imports:

**Before (Direct Import):**
```python
from recipes import all_recipes
# Direct access to data
```

**After (MCP Client):**
```python
from fastmcp import Client
# Access via standardized protocol
```

## Use Cases

### Use Case 1: Search for Recipes

```python
import asyncio
from fastmcp import Client

async def search_recipes():
    async with Client("recipe_mcp_server.py") as client:
        # Find vegetarian recipes
        result = await client.call_tool(
            "filter_recipes_by_tags",
            {"tags": ["vegetarian"]}
        )
        print(result.content[0].text)

asyncio.run(search_recipes())
```

### Use Case 2: Get Recipe Details

```python
async def get_recipe():
    async with Client("recipe_mcp_server.py") as client:
        result = await client.call_tool(
            "get_recipe_details",
            {"recipe_name": "Spaghetti Aglio e Olio"}
        )
        print(result.content[0].text)

asyncio.run(get_recipe())
```

### Use Case 3: Use with LangGraph Agent

```python
from agents.langgraph_agent_mcp import get_recipe_graph
from langchain_core.messages import HumanMessage

# Get the graph (MCP client is automatically connected)
graph = get_recipe_graph()

# Create state
state = {
    "messages": [HumanMessage(content="Plan 3 vegetarian dinners")],
    "dietary_preferences": "",
    "num_recipes": 0,
    "recipe_suggestions": [],
    "ingredient_list": [],
    "needs_cost_calculation": False
}

# Run workflow
config = {"configurable": {"thread_id": "user_1"}}
for event in graph.stream(state, config):
    for node_name, node_output in event.items():
        print(f"{node_name}: {node_output}")
```

## Architecture Overview

```
┌──────────────────┐
│  Your LangGraph  │
│      Agent       │
└────────┬─────────┘
         │ MCP Client
         ↓
┌──────────────────┐
│   Recipe MCP     │
│     Server       │
│  (6 tools,       │
│   2 resources)   │
└────────┬─────────┘
         │
         ↓
┌──────────────────┐
│   recipes.py     │
│  (all_recipes)   │
└──────────────────┘
```

## Key Benefits

✅ **Standardized API** - Uses MCP protocol for consistency
✅ **Decoupled** - Agent doesn't directly import recipe data
✅ **Testable** - Easy to test server and client separately
✅ **Extensible** - Add new tools without changing agent
✅ **Reusable** - Any MCP client can use this server

## Running the Server Standalone

```bash
python recipe_mcp_server.py
```

This starts the MCP server in stdio mode, ready to accept connections.

## Available Tools

| Tool | What it does | Example |
|------|--------------|---------|
| `search_recipes_by_name` | Find recipes by name | `query="soup"` |
| `filter_recipes_by_tags` | Filter by diet type | `tags=["vegan"]` |
| `get_recipe_details` | Get full recipe info | `recipe_name="Lentil Soup"` |
| `list_all_recipes` | Show all recipes | No parameters |
| `search_by_ingredient` | Find recipes with ingredient | `ingredient="chicken"` |
| `get_recipes_by_budget` | Recipes under budget | `max_budget=10.0` |

## Available Resources

| Resource URI | What it provides |
|--------------|------------------|
| `recipe://database/summary` | Database stats and recipe list |
| `recipe://tags/available` | All dietary tags with counts |

## Next Steps

1. **Read the full documentation**: See `MCP_INTEGRATION.md`
2. **Run the tests**: `python test_mcp_integration.py`
3. **Try the examples**: `python example_mcp_usage.py`
4. **Extend the server**: Add your own tools and resources
5. **Build your agent**: Use the MCP client in your own agents

## Troubleshooting

**Q: Tests failing?**
A: Make sure all dependencies are installed: `uv pip install -r requirements.txt`

**Q: Event loop error?**
A: `nest-asyncio` should be installed and applied automatically

**Q: Server not found?**
A: Check that `recipe_mcp_server.py` exists in the project root

## Learn More

- **MCP Documentation**: https://modelcontextprotocol.io
- **FastMCP Docs**: https://gofastmcp.com
- **Full Integration Guide**: See `MCP_INTEGRATION.md`

---

**Ready to build?** Start with `python example_mcp_usage.py` to see everything in action!
