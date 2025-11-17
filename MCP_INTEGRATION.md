# Recipe MCP Server Integration Guide

This document describes the MCP (Model Context Protocol) server implementation for the Recipe Meal Planner and how to integrate it with the LangGraph agent.

## Overview

The Recipe MCP Server provides a standardized interface to the recipe database using the Model Context Protocol. This allows:
- **Decoupling**: Recipe data access is separated from business logic
- **Reusability**: Any MCP-compatible client can access the recipe database
- **Extensibility**: Easy to add new tools and resources without modifying the agent
- **Standards Compliance**: Follows the MCP protocol for interoperability

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    LangGraph Agent                          │
│                (langgraph_agent_mcp.py)                     │
└────────────────────────┬────────────────────────────────────┘
                         │ MCP Client
                         │ (FastMCP)
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                  Recipe MCP Server                          │
│               (recipe_mcp_server.py)                        │
├─────────────────────────────────────────────────────────────┤
│  Tools:                                                     │
│  - search_recipes_by_name()                                 │
│  - filter_recipes_by_tags()                                 │
│  - get_recipe_details()                                     │
│  - list_all_recipes()                                       │
│  - search_by_ingredient()                                   │
│  - get_recipes_by_budget()                                  │
│                                                             │
│  Resources:                                                 │
│  - recipe://database/summary                                │
│  - recipe://tags/available                                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
                  ┌──────────────┐
                  │  recipes.py  │
                  │ (all_recipes)│
                  └──────────────┘
```

## Files

### 1. `recipe_mcp_server.py`

The MCP server that exposes recipe database functionality.

**Key Features:**
- **6 Tools** for recipe operations (search, filter, get details, etc.)
- **2 Resources** for database metadata
- Built with FastMCP framework
- Follows MCP protocol standards

**Available Tools:**

| Tool Name | Description | Parameters |
|-----------|-------------|------------|
| `search_recipes_by_name` | Search recipes by name (partial match) | `query: str` |
| `filter_recipes_by_tags` | Filter by dietary preferences | `tags: List[str]` |
| `get_recipe_details` | Get complete recipe information | `recipe_name: str` |
| `list_all_recipes` | List all available recipes | None |
| `search_by_ingredient` | Find recipes containing an ingredient | `ingredient: str` |
| `get_recipes_by_budget` | Find recipes within budget | `max_budget: float` |

**Available Resources:**

| Resource URI | Description |
|--------------|-------------|
| `recipe://database/summary` | Database statistics and recipe list |
| `recipe://tags/available` | Available dietary tags with counts |

### 2. `agents/langgraph_agent_mcp.py`

The LangGraph agent modified to use MCP client instead of direct imports.

**Key Components:**
- `RecipeMCPClient`: Wrapper class for MCP client operations
- `suggest_recipes_node_async`: Async helper for MCP interactions
- Uses `nest-asyncio` for running async code in sync LangGraph nodes

**Important Implementation Details:**
- Does NOT directly import from `recipes.py`
- All recipe data access goes through MCP server
- Uses FastMCP Client with stdio transport
- Handles async/sync integration with `nest-asyncio`

### 3. `test_mcp_integration.py`

Comprehensive test suite for MCP server and client.

**Test Coverage:**
- Individual MCP server tools (all 6 tools)
- MCP client wrapper functionality
- LangGraph integration with MCP
- Resource reading
- Error handling

## Installation

### Prerequisites

```bash
# Python 3.8+
# uv package manager (recommended)
```

### Install Dependencies

```bash
# Using uv (recommended)
uv pip install -r requirements.txt

# Or using pip
pip install -r requirements.txt
```

### New Dependencies Added

```
fastmcp>=2.0.0          # MCP server and client framework
nest-asyncio>=1.5.0     # Async/sync integration
```

## Usage

### Running the MCP Server Standalone

```bash
python recipe_mcp_server.py
```

Output:
```
Starting Recipe MCP Server...
Server name: Recipe Database Server
Total recipes available: 10

Available tools:
  - search_recipes_by_name
  - filter_recipes_by_tags
  - get_recipe_details
  - list_all_recipes
  - search_by_ingredient
  - get_recipes_by_budget

Starting server...
```

### Using the MCP Client Programmatically

```python
from fastmcp import Client
import asyncio

async def main():
    # Connect to the MCP server
    async with Client("recipe_mcp_server.py") as client:
        # List all tools
        tools = await client.list_tools()
        print(f"Available tools: {len(tools)}")

        # Call a tool
        result = await client.call_tool(
            "filter_recipes_by_tags",
            {"tags": ["vegetarian", "vegan"]}
        )
        print(result.content[0].text)

        # Read a resource
        summary = await client.read_resource("recipe://database/summary")
        print(summary[0].text)

asyncio.run(main())
```

### Using with LangGraph Agent

The LangGraph agent automatically connects to the MCP server:

```python
from agents.langgraph_agent_mcp import get_recipe_graph
from langchain_core.messages import HumanMessage

# Get the graph
graph = get_recipe_graph()

# Create initial state
initial_state = {
    "messages": [HumanMessage(content="Plan 5 vegetarian dinners under $50")],
    "dietary_preferences": "",
    "num_recipes": 0,
    "recipe_suggestions": [],
    "ingredient_list": [],
    "needs_cost_calculation": False
}

# Run the workflow
thread_config = {"configurable": {"thread_id": "user_123"}}
for event in graph.stream(initial_state, thread_config):
    for node_name, node_output in event.items():
        print(f"Node: {node_name}")
        if "messages" in node_output:
            print(node_output["messages"][-1].content)
```

## Testing

Run the comprehensive test suite:

```bash
python test_mcp_integration.py
```

**Test Results:**
```
================================================================================
RECIPE MCP SERVER AND CLIENT INTEGRATION TESTS
================================================================================

TEST 1: MCP Server Tools
✓ Successfully connected to MCP server
✓ All 6 tools tested successfully
✓ Resources accessible

TEST 2: MCP Client Wrapper
✓ Connected via wrapper
✓ Filter, search, and detail operations working

TEST 3: LangGraph Integration with MCP
✓ LangGraph setup successful
✓ Workflow completed successfully

ALL TESTS COMPLETED!
```

## Key Differences from Original Implementation

### Original (`agents/langgraph_agent.py`)

```python
# Direct import
from recipes import all_recipes

def suggest_recipes_node(state):
    # Direct access to all_recipes dictionary
    for recipe_name, recipe_data in all_recipes.items():
        if any(tag in recipe_data['tags'] for tag in ['vegetarian']):
            selected_recipes.append(recipe_name)
```

### MCP Version (`agents/langgraph_agent_mcp.py`)

```python
# No direct import from recipes.py
from fastmcp import Client

async def suggest_recipes_node_async(preferences, num_recipes):
    # Access via MCP client
    mcp_response = await mcp_recipe_client.filter_recipes_by_tags(['vegetarian'])
    selected_recipes = parse_recipe_names_from_mcp_response(mcp_response)
```

**Benefits:**
- ✅ Separation of concerns
- ✅ No direct coupling to data structure
- ✅ Can swap out backend without changing agent
- ✅ Standard protocol for tool access

## MCP Protocol Details

### Tool Execution Flow

1. **Client Request**: Agent calls `client.call_tool(tool_name, args)`
2. **Transport**: Request sent via stdio to MCP server
3. **Server Processing**: FastMCP routes to decorated function
4. **Tool Execution**: Function executes with provided args
5. **Response**: Result returned as MCP-formatted message
6. **Client Processing**: Agent parses and uses result

### Resource Access Flow

1. **Client Request**: Agent calls `client.read_resource(uri)`
2. **Server Lookup**: MCP server matches URI to resource function
3. **Resource Generation**: Function executes and returns data
4. **Response**: Data returned to client
5. **Client Processing**: Agent uses resource data

## Troubleshooting

### Issue: "RuntimeError: Cannot run the event loop while another loop is running"

**Solution**: Make sure `nest-asyncio` is installed and applied:

```python
import nest_asyncio
nest_asyncio.apply()
```

This is already handled in `langgraph_agent_mcp.py`.

### Issue: MCP server not found

**Solution**: Ensure the path to `recipe_mcp_server.py` is correct:

```python
MCP_SERVER_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "recipe_mcp_server.py"
)
```

### Issue: AttributeError with client responses

**Solution**: FastMCP 2.x returns lists directly, not objects:

```python
# Correct (FastMCP 2.x)
tools = await client.list_tools()  # Returns list
for tool in tools:
    print(tool.name)

# Incorrect (older versions)
for tool in tools.tools:  # No .tools attribute
    print(tool.name)
```

## Performance Considerations

### Connection Overhead

- MCP client maintains persistent connection during session
- First connection has ~100-200ms overhead
- Subsequent calls are fast (<10ms)

### Optimization Tips

1. **Connection Pooling**: Reuse the same client instance
2. **Batch Operations**: Use `list_all_recipes` then filter locally if multiple queries needed
3. **Resource Caching**: Database summary resource is static, can be cached

## Extending the MCP Server

### Adding a New Tool

```python
@mcp.tool()
def get_recipes_by_cuisine(cuisine: str) -> str:
    """
    Find recipes by cuisine type.

    Args:
        cuisine: Cuisine type (e.g., Italian, Asian, Mexican)

    Returns:
        List of recipes matching the cuisine
    """
    matching_recipes = {}
    # Implementation here
    return formatted_results
```

### Adding a New Resource

```python
@mcp.resource("recipe://ingredients/all")
def get_all_ingredients() -> str:
    """Provides a list of all unique ingredients across all recipes."""
    all_ingredients = set()
    for recipe_data in all_recipes.values():
        for ing in recipe_data['ingredients']:
            all_ingredients.add(ing['item'])

    return "\n".join(sorted(all_ingredients))
```

## Best Practices

1. **Tool Design**
   - Keep tools focused and single-purpose
   - Use clear parameter names and types
   - Provide detailed docstrings
   - Return formatted, readable strings

2. **Error Handling**
   - Validate inputs in tools
   - Return helpful error messages
   - Don't raise exceptions for user errors

3. **Resource Design**
   - Use descriptive URIs (e.g., `recipe://category/subcategory`)
   - Keep resources relatively static
   - Use tools for dynamic queries

4. **Client Integration**
   - Handle async/sync boundaries carefully
   - Parse MCP responses robustly
   - Log connection issues for debugging

## References

- **FastMCP Documentation**: https://gofastmcp.com
- **MCP Specification**: https://modelcontextprotocol.io
- **ADK MCP Docs**: https://google.github.io/adk-docs/mcp/
- **FastMCP GitHub**: https://github.com/jlowin/fastmcp

## Summary

The MCP integration provides:

✅ **Standardized API** for recipe database access
✅ **Protocol Compliance** following MCP standards
✅ **Separation of Concerns** between data and logic
✅ **Extensibility** for adding new tools/resources
✅ **Reusability** across different clients
✅ **Testability** with comprehensive test suite

The implementation successfully demonstrates how to build and integrate an MCP server with a LangGraph agent while maintaining clean architecture and following best practices.
