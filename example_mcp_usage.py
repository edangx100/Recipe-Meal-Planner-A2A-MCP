"""
Example Usage of Recipe MCP Server

This script demonstrates different ways to use the Recipe MCP Server:
1. Direct MCP client usage
2. Using the RecipeMCPClient wrapper
3. Integration with LangGraph agent
"""

import asyncio
from fastmcp import Client


async def example_1_direct_mcp_client():
    """Example 1: Using FastMCP Client directly"""
    print("=" * 80)
    print("EXAMPLE 1: Direct MCP Client Usage")
    print("=" * 80)

    async with Client("recipe_mcp_server.py") as client:
        print("\n1. List all available tools:")
        tools = await client.list_tools()
        for tool in tools:
            print(f"   - {tool.name}")

        print("\n2. Search for vegetarian recipes:")
        result = await client.call_tool(
            "filter_recipes_by_tags",
            {"tags": ["vegetarian"]}
        )
        print(result.content[0].text[:300] + "...")

        print("\n3. Get details for a specific recipe:")
        result = await client.call_tool(
            "get_recipe_details",
            {"recipe_name": "Lentil Soup"}
        )
        print(result.content[0].text)

        print("\n4. Find recipes under $10:")
        result = await client.call_tool(
            "get_recipes_by_budget",
            {"max_budget": 10.0}
        )
        print(result.content[0].text[:300] + "...")

        print("\n5. Read database summary resource:")
        summary = await client.read_resource("recipe://database/summary")
        print(summary[0].text)


async def example_2_mcp_client_wrapper():
    """Example 2: Using the RecipeMCPClient wrapper class"""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Using RecipeMCPClient Wrapper")
    print("=" * 80)

    from agents.langgraph_agent_mcp import RecipeMCPClient
    import os

    server_path = os.path.join(os.path.dirname(__file__), "recipe_mcp_server.py")
    client = RecipeMCPClient(server_path)

    await client.connect()

    print("\n1. Filter vegan recipes:")
    result = await client.filter_recipes_by_tags(["vegan"])
    print(result[:400] + "...")

    print("\n2. Search for recipes with 'chicken':")
    result = await client.search_recipes_by_name("chicken")
    print(result)

    print("\n3. List all recipes:")
    result = await client.list_all_recipes()
    print(result[:400] + "...")

    await client.disconnect()


def example_3_langgraph_integration():
    """Example 3: Using MCP with LangGraph Agent"""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: LangGraph Agent Integration")
    print("=" * 80)

    from agents.langgraph_agent_mcp import get_recipe_graph
    from langchain_core.messages import HumanMessage

    graph = get_recipe_graph()

    # Test Case 1: Vegetarian meal plan
    print("\n1. Test Case: Plan 3 vegetarian dinners under $30")
    print("-" * 80)

    initial_state = {
        "messages": [HumanMessage(content="Plan 3 vegetarian dinners under $30 total")],
        "dietary_preferences": "",
        "num_recipes": 0,
        "recipe_suggestions": [],
        "ingredient_list": [],
        "needs_cost_calculation": False
    }

    thread_config = {"configurable": {"thread_id": "example_thread_1"}}

    for event in graph.stream(initial_state, thread_config):
        for node_name, node_output in event.items():
            if "messages" in node_output and node_output["messages"]:
                last_message = node_output["messages"][-1]
                print(f"\n[{node_name}]: {last_message.content[:200]}...")

    # Test Case 2: General meal plan
    print("\n\n2. Test Case: Plan 5 dinners under $50")
    print("-" * 80)

    initial_state = {
        "messages": [HumanMessage(content="Plan 5 dinners under $50 total")],
        "dietary_preferences": "",
        "num_recipes": 0,
        "recipe_suggestions": [],
        "ingredient_list": [],
        "needs_cost_calculation": False
    }

    thread_config = {"configurable": {"thread_id": "example_thread_2"}}

    for event in graph.stream(initial_state, thread_config):
        for node_name, node_output in event.items():
            if "messages" in node_output and node_output["messages"]:
                last_message = node_output["messages"][-1]
                print(f"\n[{node_name}]: {last_message.content[:200]}...")


async def main():
    """Run all examples"""
    print("\n" + "=" * 80)
    print("RECIPE MCP SERVER - USAGE EXAMPLES")
    print("=" * 80)

    # Example 1: Direct MCP client
    await example_1_direct_mcp_client()

    # Example 2: MCP client wrapper
    await example_2_mcp_client_wrapper()

    # Example 3: LangGraph integration (synchronous)
    example_3_langgraph_integration()

    print("\n" + "=" * 80)
    print("ALL EXAMPLES COMPLETED!")
    print("=" * 80)
    print("\nKey Takeaways:")
    print("1. MCP server provides standardized access to recipe database")
    print("2. Multiple client options available (direct, wrapper, LangGraph)")
    print("3. No direct imports of recipes.py in client code")
    print("4. Easy to test, extend, and maintain")
    print()


if __name__ == "__main__":
    asyncio.run(main())
