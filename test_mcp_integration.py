"""
Test script for Recipe MCP Server and Client Integration

This script tests:
1. MCP server tools individually
2. MCP client connection
3. Integration with LangGraph agent
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def test_mcp_server_tools():
    """Test individual MCP server tools"""
    print("=" * 80)
    print("TEST 1: MCP Server Tools")
    print("=" * 80)

    from fastmcp import Client

    # Connect to the MCP server
    server_path = os.path.join(os.path.dirname(__file__), "recipe_mcp_server.py")
    print(f"\nConnecting to MCP server: {server_path}")

    async with Client(server_path) as client:
        print("✓ Successfully connected to MCP server\n")

        # Test 1: List all tools
        print("-" * 80)
        print("Listing available tools...")
        print("-" * 80)
        tools = await client.list_tools()
        print(f"Available tools: {len(tools)}")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")

        # Test 2: List all recipes
        print("\n" + "-" * 80)
        print("Test: list_all_recipes")
        print("-" * 80)
        result = await client.call_tool("list_all_recipes", {})
        print(result.content[0].text[:500] + "...\n")

        # Test 3: Filter by tags
        print("-" * 80)
        print("Test: filter_recipes_by_tags (vegetarian)")
        print("-" * 80)
        result = await client.call_tool("filter_recipes_by_tags", {"tags": ["vegetarian"]})
        print(result.content[0].text[:500] + "...\n")

        # Test 4: Get recipe details
        print("-" * 80)
        print("Test: get_recipe_details (Spaghetti Aglio e Olio)")
        print("-" * 80)
        result = await client.call_tool("get_recipe_details", {"recipe_name": "Spaghetti Aglio e Olio"})
        print(result.content[0].text + "\n")

        # Test 5: Search by ingredient
        print("-" * 80)
        print("Test: search_by_ingredient (chicken)")
        print("-" * 80)
        result = await client.call_tool("search_by_ingredient", {"ingredient": "chicken"})
        print(result.content[0].text + "\n")

        # Test 6: Get recipes by budget
        print("-" * 80)
        print("Test: get_recipes_by_budget ($10)")
        print("-" * 80)
        result = await client.call_tool("get_recipes_by_budget", {"max_budget": 10.0})
        print(result.content[0].text[:500] + "...\n")

        # Test 7: List resources
        print("-" * 80)
        print("Listing available resources...")
        print("-" * 80)
        resources = await client.list_resources()
        print(f"Available resources: {len(resources)}")
        for resource in resources:
            print(f"  - {resource.uri}: {resource.name}")

        # Test 8: Read resource
        print("\n" + "-" * 80)
        print("Test: Read resource (recipe://database/summary)")
        print("-" * 80)
        result = await client.read_resource("recipe://database/summary")
        print(result[0].text + "\n")

    print("✓ All MCP server tool tests passed!\n")


async def test_mcp_client_wrapper():
    """Test the RecipeMCPClient wrapper class"""
    print("=" * 80)
    print("TEST 2: MCP Client Wrapper")
    print("=" * 80)

    from agents.langgraph_agent_mcp import RecipeMCPClient

    server_path = os.path.join(os.path.dirname(__file__), "recipe_mcp_server.py")
    client = RecipeMCPClient(server_path)

    print("\nConnecting to MCP server via wrapper...")
    await client.connect()
    print("✓ Connected\n")

    # Test filter by tags
    print("-" * 80)
    print("Test: filter_recipes_by_tags (vegan)")
    print("-" * 80)
    result = await client.filter_recipes_by_tags(["vegan"])
    print(result[:400] + "...\n")

    # Test get recipe details
    print("-" * 80)
    print("Test: get_recipe_details (Lentil Soup)")
    print("-" * 80)
    result = await client.get_recipe_details("Lentil Soup")
    print(result + "\n")

    # Test search by name
    print("-" * 80)
    print("Test: search_recipes_by_name (tacos)")
    print("-" * 80)
    result = await client.search_recipes_by_name("tacos")
    print(result + "\n")

    # Disconnect
    print("Disconnecting...")
    await client.disconnect()
    print("✓ Disconnected\n")

    print("✓ All MCP client wrapper tests passed!\n")


def test_langgraph_integration():
    """Test LangGraph agent with MCP client"""
    print("=" * 80)
    print("TEST 3: LangGraph Integration with MCP")
    print("=" * 80)

    from agents.langgraph_agent_mcp import get_recipe_graph, is_langgraph_available
    from langchain_core.messages import HumanMessage

    if not is_langgraph_available():
        print("✗ LangGraph setup failed")
        return

    print("\n✓ LangGraph setup successful")

    # Get the graph
    graph = get_recipe_graph()

    # Test case 1: Basic meal plan request
    print("\n" + "-" * 80)
    print("Test Case: Plan 3 vegetarian dinners")
    print("-" * 80)

    initial_state = {
        "messages": [HumanMessage(content="Plan 3 vegetarian dinners under $30 total")],
        "dietary_preferences": "",
        "num_recipes": 0,
        "recipe_suggestions": [],
        "ingredient_list": [],
        "needs_cost_calculation": False
    }

    thread_config = {"configurable": {"thread_id": "test_thread_1"}}

    print("\nExecuting LangGraph workflow...\n")
    try:
        for event in graph.stream(initial_state, thread_config):
            for node_name, node_output in event.items():
                print(f"Node: {node_name}")
                if "messages" in node_output and node_output["messages"]:
                    last_message = node_output["messages"][-1]
                    print(f"Output: {last_message.content[:200]}...")
                print()

        print("✓ LangGraph workflow completed successfully!\n")
    except Exception as e:
        print(f"✗ LangGraph workflow error: {e}\n")
        import traceback
        traceback.print_exc()


async def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("RECIPE MCP SERVER AND CLIENT INTEGRATION TESTS")
    print("=" * 80 + "\n")

    try:
        # Test 1: MCP Server Tools
        await test_mcp_server_tools()

        # Test 2: MCP Client Wrapper
        await test_mcp_client_wrapper()

        # Test 3: LangGraph Integration (sync)
        test_langgraph_integration()

        print("=" * 80)
        print("ALL TESTS COMPLETED!")
        print("=" * 80 + "\n")

    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
