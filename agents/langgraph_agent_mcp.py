"""
LangGraph State Machine for Recipe Planning with MCP Client

This module contains the LangGraph state machine components for the recipe meal planner.
It uses an MCP client to connect to the Recipe MCP Server for accessing recipe data.

Workflow:
1. Gather dietary preferences from user request using LLM structured output
2. Suggest recipes based on preferences and requested count (via MCP)
3. Check for ingredient overlap across recipes
4. Optimize the grocery list by consolidating ingredients
5. Flag when cost calculation is needed
"""

import sys
import os
import asyncio
from typing import TypedDict, Annotated, Sequence, List, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from fastmcp import Client

# Constants
COST_CALCULATION_FLAG = "[CALCULATE_COST]"

# Initialize module-level variables
LANGGRAPH_SETUP_SUCCESS = False
recipe_graph = None
mcp_client = None

# MCP Server path - should point to the recipe MCP server
MCP_SERVER_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "recipe_mcp_server.py")


# --- MCP Client Wrapper ---
class RecipeMCPClient:
    """Wrapper for MCP client to access recipe database"""

    def __init__(self, server_path: str):
        self.server_path = server_path
        self.client = None
        self._client_context = None

    async def connect(self):
        """Initialize connection to MCP server"""
        if self.client is None:
            self.client = Client(self.server_path)
            self._client_context = await self.client.__aenter__()
        return self

    async def disconnect(self):
        """Close connection to MCP server"""
        if self._client_context is not None:
            await self.client.__aexit__(None, None, None)
            self.client = None
            self._client_context = None

    async def filter_recipes_by_tags(self, tags: List[str]) -> str:
        """Filter recipes by dietary tags using MCP tool"""
        if self.client is None:
            await self.connect()

        result = await self.client.call_tool(
            "filter_recipes_by_tags",
            {"tags": tags}
        )
        return result.content[0].text if result.content else "No results"

    async def list_all_recipes(self) -> str:
        """List all recipes using MCP tool"""
        if self.client is None:
            await self.connect()

        result = await self.client.call_tool("list_all_recipes", {})
        return result.content[0].text if result.content else "No results"

    async def get_recipe_details(self, recipe_name: str) -> str:
        """Get detailed recipe information using MCP tool"""
        if self.client is None:
            await self.connect()

        result = await self.client.call_tool(
            "get_recipe_details",
            {"recipe_name": recipe_name}
        )
        return result.content[0].text if result.content else "Recipe not found"

    async def search_recipes_by_name(self, query: str) -> str:
        """Search recipes by name using MCP tool"""
        if self.client is None:
            await self.connect()

        result = await self.client.call_tool(
            "search_recipes_by_name",
            {"query": query}
        )
        return result.content[0].text if result.content else "No results"

    async def get_recipes_by_budget(self, max_budget: float) -> str:
        """Get recipes within budget using MCP tool"""
        if self.client is None:
            await self.connect()

        result = await self.client.call_tool(
            "get_recipes_by_budget",
            {"max_budget": max_budget}
        )
        return result.content[0].text if result.content else "No results"


# Global MCP client instance
mcp_recipe_client = RecipeMCPClient(MCP_SERVER_PATH)


# --- Helper function to parse recipe list from MCP response ---
def parse_recipe_names_from_mcp_response(mcp_response: str) -> List[str]:
    """
    Parse recipe names from MCP tool response.
    Looks for lines starting with ** (markdown bold) which indicate recipe names.
    """
    recipe_names = []
    lines = mcp_response.split('\n')

    for line in lines:
        line = line.strip()
        # Look for markdown bold pattern: **Recipe Name**
        if line.startswith('**') and line.endswith('**'):
            recipe_name = line.strip('*').strip()
            # Remove any additional text after the recipe name (like cost)
            if ' - $' in recipe_name:
                recipe_name = recipe_name.split(' - $')[0].strip()
            recipe_names.append(recipe_name)

    return recipe_names


def parse_ingredients_from_recipe_details(recipe_details: str) -> List[dict]:
    """
    Parse ingredient information from recipe details response.
    Returns list of dicts with item, quantity, and price.
    """
    ingredients = []
    lines = recipe_details.split('\n')
    in_ingredients_section = False

    for line in lines:
        line = line.strip()

        # Check if we're in the ingredients section
        if line.startswith('Ingredients:'):
            in_ingredients_section = True
            continue

        # Parse ingredient lines (format: "  - item: quantity ($price)")
        if in_ingredients_section and line.startswith('- '):
            # Extract item, quantity, and price
            # Format: "  - chicken breast: 1 lb ($4.99)"
            try:
                parts = line[2:].split('($')  # Split by ($
                if len(parts) == 2:
                    item_and_qty = parts[0].strip()
                    price_str = parts[1].rstrip(')')

                    # Split item and quantity
                    item_qty_parts = item_and_qty.split(': ')
                    if len(item_qty_parts) == 2:
                        item = item_qty_parts[0].strip()
                        quantity = item_qty_parts[1].strip()
                        price = float(price_str)

                        ingredients.append({
                            'item': item,
                            'quantity': quantity,
                            'price': price
                        })
            except (ValueError, IndexError):
                continue

    return ingredients


# --- LangGraph State Machine Setup ---
class RecipePlannerState(TypedDict):
    """State for the recipe planning workflow"""
    messages: Annotated[Sequence[BaseMessage], lambda x, y: x + y]
    dietary_preferences: str
    num_recipes: int
    recipe_suggestions: List[str]
    ingredient_list: List[dict]
    needs_cost_calculation: bool


def gather_preferences_node(state: RecipePlannerState):
    """Gathers dietary preferences and number of recipes from the user request using LLM structured output"""
    from pydantic import BaseModel
    from google import genai
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils import DEFAULT_LLM

    class MealPlanRequest(BaseModel):
        num_recipes: int
        dietary_preferences: list[str]
        budget: float

    last_message = state['messages'][-1]

    if isinstance(last_message, HumanMessage):
        user_input = last_message.content

        # Use LLM with structured output to parse the request
        client = genai.Client()
        prompt = f"""Extract the meal planning requirements from this user request:
"{user_input}"

Identify:
- num_recipes: How many meals/dinners/recipes they want (default: 5)
- dietary_preferences: List any dietary restrictions mentioned (vegetarian, vegan, gluten-free, low-carb, etc.)
- budget: Budget amount in dollars (default: 50.0)
"""

        response_obj = client.models.generate_content(
            model=DEFAULT_LLM,
            contents=prompt,
            config={
                'response_mime_type': 'application/json',
                'response_schema': MealPlanRequest
            }
        )

        parsed_request = MealPlanRequest.model_validate_json(response_obj.text)

        pref_str = ", ".join(parsed_request.dietary_preferences) if parsed_request.dietary_preferences else "no specific restrictions"

        response = f"I'll plan {parsed_request.num_recipes} dinners under ${parsed_request.budget:.0f} total. Dietary preferences detected: {pref_str}. Moving to recipe suggestions."
        print(f"DEBUG: gather_preferences_node - {response}")

        return {
            "messages": [AIMessage(content=response)],
            "dietary_preferences": pref_str,
            "num_recipes": parsed_request.num_recipes,
            "needs_cost_calculation": False
        }

    return {"messages": [AIMessage(content="Processing preferences...")]}


async def suggest_recipes_node_async(preferences: str, num_recipes: int):
    """Async helper function to interact with MCP client"""
    # Filter recipes based on preferences using MCP
    selected_recipes = []

    if 'vegetarian' in preferences or 'vegan' in preferences:
        # Get vegetarian/vegan recipes via MCP
        tags = []
        if 'vegetarian' in preferences:
            tags.append('vegetarian')
        if 'vegan' in preferences:
            tags.append('vegan')

        mcp_response = await mcp_recipe_client.filter_recipes_by_tags(tags)
        selected_recipes = parse_recipe_names_from_mcp_response(mcp_response)[:num_recipes]
    else:
        # Get all recipes via MCP
        mcp_response = await mcp_recipe_client.list_all_recipes()
        selected_recipes = parse_recipe_names_from_mcp_response(mcp_response)[:num_recipes]

    # Ensure we have the requested number
    selected_recipes = selected_recipes[:num_recipes]

    # Collect ingredients for all selected recipes
    all_ingredients = []
    for recipe_name in selected_recipes:
        recipe_details = await mcp_recipe_client.get_recipe_details(recipe_name)
        ingredients = parse_ingredients_from_recipe_details(recipe_details)
        all_ingredients.extend(ingredients)

    return selected_recipes, all_ingredients


def suggest_recipes_node(state: RecipePlannerState):
    """Suggests dinner recipes based on preferences and requested count using MCP client"""

    preferences = state.get('dietary_preferences', 'no specific restrictions')
    num_recipes = state.get('num_recipes', 5)

    # Run async code in thread-safe manner
    import nest_asyncio
    nest_asyncio.apply()

    loop = asyncio.get_event_loop()
    selected_recipes, all_ingredients = loop.run_until_complete(
        suggest_recipes_node_async(preferences, num_recipes)
    )

    recipe_list = "\n".join([f"  {i+1}. {r}" for i, r in enumerate(selected_recipes)])
    response = f"Selected {len(selected_recipes)} recipes:\n{recipe_list}\n\nMoving to ingredient overlap check."

    print(f"DEBUG: suggest_recipes_node - Selected {len(selected_recipes)} recipes via MCP")

    return {
        "messages": [AIMessage(content=response)],
        "recipe_suggestions": selected_recipes,
        "ingredient_list": all_ingredients,
        "needs_cost_calculation": False
    }


def check_ingredient_overlap_node(state: RecipePlannerState):
    """Checks for ingredient overlap to optimize shopping list"""
    ingredients = state.get('ingredient_list', [])

    # Group ingredients by item name
    ingredient_groups = {}
    for ingredient in ingredients:
        item_name = ingredient['item']
        if item_name not in ingredient_groups:
            ingredient_groups[item_name] = []
        ingredient_groups[item_name].append(ingredient)

    # Calculate consolidated quantities
    overlaps = []
    for item_name, item_list in ingredient_groups.items():
        if len(item_list) > 1:
            overlaps.append(f"{item_name} (used in {len(item_list)} recipes)")

    overlap_msg = ""
    if overlaps:
        overlap_msg = f"\n\nIngredient overlap found for: {', '.join(overlaps[:5])}"

    response = f"Checked ingredient overlap across recipes.{overlap_msg}\n\nPreparing to optimize grocery list and calculate costs. {COST_CALCULATION_FLAG}"

    print(f"DEBUG: check_ingredient_overlap_node - Found {len(overlaps)} overlapping ingredients")

    return {
        "messages": [AIMessage(content=response)],
        "needs_cost_calculation": True
    }


def optimize_grocery_list_node(state: RecipePlannerState):
    """Optimizes the grocery list and requests cost calculation"""
    ingredients = state.get('ingredient_list', [])
    recipes = state.get('recipe_suggestions', [])

    # Consolidate ingredients
    ingredient_groups = {}
    for ingredient in ingredients:
        item_name = ingredient['item']
        if item_name not in ingredient_groups:
            ingredient_groups[item_name] = {
                'quantities': [],
                'total_price': 0.0,
                'consolidated_quantity': ''
            }
        ingredient_groups[item_name]['quantities'].append(ingredient['quantity'])
        ingredient_groups[item_name]['total_price'] += ingredient.get('price', 0.0)

    # Build shopping list summary
    shopping_list = []
    for item_name, data in ingredient_groups.items():
        qty = data['quantities'][0] if len(data['quantities']) == 1 else f"{len(data['quantities'])}x portions"
        shopping_list.append(f"{item_name}: {qty}")

    shopping_summary = "\n".join([f"  - {item}" for item in shopping_list[:10]])

    # Include all selected recipes in the response
    recipe_list = "\n".join([f"  {i+1}. {r}" for i, r in enumerate(recipes)])
    response = f"Selected {len(recipes)} recipes:\n{recipe_list}\n\nOptimized grocery list ready:\n{shopping_summary}\n\nRequesting cost calculation from code agent. {COST_CALCULATION_FLAG}"

    print(f"DEBUG: optimize_grocery_list_node - Created shopping list with {len(ingredient_groups)} items")

    return {
        "messages": [AIMessage(content=response)],
        "needs_cost_calculation": True
    }


def should_calculate_cost(state: RecipePlannerState):
    """Routing function to determine if cost calculation is needed"""
    if state['messages'] and isinstance(state['messages'][-1], AIMessage):
        last_ai_content = state['messages'][-1].content
        print(f"DEBUG: should_calculate_cost checking: '{last_ai_content[:100]}...'")
        if COST_CALCULATION_FLAG in last_ai_content:
            print("DEBUG: should_calculate_cost -> routing to END (cost calculation needed)")
            return END
    print("DEBUG: should_calculate_cost -> continuing workflow")
    return "suggest_recipes"


def build_recipe_graph():
    """Builds and compiles the LangGraph state machine for recipe planning"""
    # Build the LangGraph state machine
    builder = StateGraph(RecipePlannerState)

    # Add nodes
    builder.add_node("gather_preferences", gather_preferences_node)
    builder.add_node("suggest_recipes", suggest_recipes_node)
    builder.add_node("check_overlap", check_ingredient_overlap_node)
    builder.add_node("optimize_list", optimize_grocery_list_node)

    # Define edges
    builder.set_entry_point("gather_preferences")
    builder.add_edge("gather_preferences", "suggest_recipes")
    builder.add_edge("suggest_recipes", "check_overlap")
    builder.add_edge("check_overlap", "optimize_list")

    # Conditional edge from optimize_list
    builder.add_conditional_edges(
        "optimize_list",
        should_calculate_cost,
        {"suggest_recipes": "suggest_recipes", END: END}
    )

    memory = MemorySaver()
    graph = builder.compile(checkpointer=memory)
    print("Recipe planner LangGraph state machine (MCP version) compiled successfully.")
    return graph


# Build the graph
recipe_graph = build_recipe_graph()
LANGGRAPH_SETUP_SUCCESS = True


def get_recipe_graph():
    """Returns the compiled recipe planning graph"""
    return recipe_graph


def is_langgraph_available():
    """Returns whether LangGraph setup was successful"""
    return LANGGRAPH_SETUP_SUCCESS


def cleanup_mcp_client():
    """Cleanup MCP client connection"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(mcp_recipe_client.disconnect())
    finally:
        loop.close()
