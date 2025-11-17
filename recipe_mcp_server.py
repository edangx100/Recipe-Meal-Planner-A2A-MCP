"""
Recipe MCP Server

This MCP server provides access to the recipe database, allowing clients to:
- Search recipes by name
- Filter recipes by dietary preferences/tags
- Get detailed recipe information including ingredients and prices
- List all available recipes
- Search by ingredients

The server exposes tools following the Model Context Protocol (MCP) standard.
"""

from fastmcp import FastMCP
from typing import List, Dict, Optional
import sys
import os

# Add parent directory to path to import recipes
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recipes import all_recipes

# Initialize FastMCP server
mcp = FastMCP("Recipe Database Server")


@mcp.tool()
def search_recipes_by_name(query: str) -> str:
    """
    Search for recipes by name (case-insensitive partial match).

    Args:
        query: The search term to look for in recipe names

    Returns:
        JSON string containing matching recipe names and their details
    """
    query_lower = query.lower()
    matching_recipes = {}

    for recipe_name, recipe_data in all_recipes.items():
        if query_lower in recipe_name.lower():
            matching_recipes[recipe_name] = recipe_data

    if not matching_recipes:
        return f"No recipes found matching '{query}'"

    # Format results
    result = f"Found {len(matching_recipes)} recipe(s) matching '{query}':\n\n"
    for recipe_name, recipe_data in matching_recipes.items():
        ingredients_list = ", ".join([ing['item'] for ing in recipe_data['ingredients']])
        tags = ", ".join(recipe_data['tags'])
        result += f"**{recipe_name}**\n"
        result += f"  Tags: {tags}\n"
        result += f"  Ingredients: {ingredients_list}\n\n"

    return result


@mcp.tool()
def filter_recipes_by_tags(tags: List[str]) -> str:
    """
    Filter recipes by dietary tags/preferences.

    Args:
        tags: List of dietary tags to filter by (e.g., ['vegetarian', 'vegan', 'gluten-free', 'low-carb'])

    Returns:
        JSON string containing recipes that match ANY of the specified tags
    """
    if not tags:
        return "Please provide at least one tag to filter by"

    tags_lower = [tag.lower() for tag in tags]
    matching_recipes = {}

    for recipe_name, recipe_data in all_recipes.items():
        recipe_tags = [tag.lower() for tag in recipe_data['tags']]
        if any(tag in recipe_tags for tag in tags_lower):
            matching_recipes[recipe_name] = recipe_data

    if not matching_recipes:
        return f"No recipes found with tags: {', '.join(tags)}"

    # Format results
    result = f"Found {len(matching_recipes)} recipe(s) with tags [{', '.join(tags)}]:\n\n"
    for recipe_name, recipe_data in matching_recipes.items():
        total_cost = sum([ing['price'] for ing in recipe_data['ingredients']])
        tags_str = ", ".join(recipe_data['tags'])
        result += f"**{recipe_name}**\n"
        result += f"  Tags: {tags_str}\n"
        result += f"  Estimated Cost: ${total_cost:.2f}\n"
        result += f"  Ingredients: {len(recipe_data['ingredients'])} items\n\n"

    return result


@mcp.tool()
def get_recipe_details(recipe_name: str) -> str:
    """
    Get complete details for a specific recipe including all ingredients with quantities and prices.

    Args:
        recipe_name: The exact name of the recipe (case-insensitive)

    Returns:
        Detailed recipe information including ingredients, quantities, prices, and tags
    """
    # Case-insensitive lookup
    recipe_data = None
    actual_name = None

    for name, data in all_recipes.items():
        if name.lower() == recipe_name.lower():
            recipe_data = data
            actual_name = name
            break

    if not recipe_data:
        available = ", ".join(all_recipes.keys())
        return f"Recipe '{recipe_name}' not found. Available recipes: {available}"

    # Calculate total cost
    total_cost = sum([ing['price'] for ing in recipe_data['ingredients']])

    # Format result
    result = f"**{actual_name}**\n\n"
    result += f"Tags: {', '.join(recipe_data['tags'])}\n"
    result += f"Total Cost: ${total_cost:.2f}\n\n"
    result += "Ingredients:\n"

    for ing in recipe_data['ingredients']:
        result += f"  - {ing['item']}: {ing['quantity']} (${ing['price']:.2f})\n"

    return result


@mcp.tool()
def list_all_recipes() -> str:
    """
    List all available recipes in the database with their tags and estimated costs.

    Returns:
        Complete list of all recipes with summary information
    """
    result = f"Recipe Database - Total: {len(all_recipes)} recipes\n\n"

    for recipe_name, recipe_data in all_recipes.items():
        total_cost = sum([ing['price'] for ing in recipe_data['ingredients']])
        tags_str = ", ".join(recipe_data['tags'])
        result += f"**{recipe_name}**\n"
        result += f"  Tags: {tags_str}\n"
        result += f"  Cost: ${total_cost:.2f}\n"
        result += f"  Ingredients: {len(recipe_data['ingredients'])} items\n\n"

    return result


@mcp.tool()
def search_by_ingredient(ingredient: str) -> str:
    """
    Find all recipes that contain a specific ingredient.

    Args:
        ingredient: The ingredient to search for (case-insensitive)

    Returns:
        List of recipes containing the specified ingredient
    """
    ingredient_lower = ingredient.lower()
    matching_recipes = {}

    for recipe_name, recipe_data in all_recipes.items():
        for ing in recipe_data['ingredients']:
            if ingredient_lower in ing['item'].lower():
                matching_recipes[recipe_name] = recipe_data
                break

    if not matching_recipes:
        return f"No recipes found containing '{ingredient}'"

    # Format results
    result = f"Found {len(matching_recipes)} recipe(s) containing '{ingredient}':\n\n"
    for recipe_name, recipe_data in matching_recipes.items():
        # Find the matching ingredient details
        matching_ing = None
        for ing in recipe_data['ingredients']:
            if ingredient_lower in ing['item'].lower():
                matching_ing = ing
                break

        total_cost = sum([ing['price'] for ing in recipe_data['ingredients']])
        result += f"**{recipe_name}**\n"
        result += f"  Uses: {matching_ing['item']} ({matching_ing['quantity']})\n"
        result += f"  Total Cost: ${total_cost:.2f}\n"
        result += f"  Tags: {', '.join(recipe_data['tags'])}\n\n"

    return result


@mcp.tool()
def get_recipes_by_budget(max_budget: float) -> str:
    """
    Find all recipes within a specified budget.

    Args:
        max_budget: Maximum budget per recipe in dollars

    Returns:
        List of recipes that cost less than or equal to the budget
    """
    matching_recipes = {}

    for recipe_name, recipe_data in all_recipes.items():
        total_cost = sum([ing['price'] for ing in recipe_data['ingredients']])
        if total_cost <= max_budget:
            matching_recipes[recipe_name] = {
                'data': recipe_data,
                'cost': total_cost
            }

    if not matching_recipes:
        return f"No recipes found under ${max_budget:.2f}"

    # Sort by cost
    sorted_recipes = sorted(matching_recipes.items(), key=lambda x: x[1]['cost'])

    result = f"Found {len(matching_recipes)} recipe(s) under ${max_budget:.2f}:\n\n"
    for recipe_name, recipe_info in sorted_recipes:
        tags_str = ", ".join(recipe_info['data']['tags'])
        result += f"**{recipe_name}** - ${recipe_info['cost']:.2f}\n"
        result += f"  Tags: {tags_str}\n"
        result += f"  Ingredients: {len(recipe_info['data']['ingredients'])} items\n\n"

    return result


@mcp.resource("recipe://database/summary")
def get_database_summary() -> str:
    """
    Provides a summary of the recipe database including statistics.
    """
    total_recipes = len(all_recipes)

    # Collect all unique tags
    all_tags = set()
    total_cost = 0

    for recipe_data in all_recipes.values():
        all_tags.update(recipe_data['tags'])
        total_cost += sum([ing['price'] for ing in recipe_data['ingredients']])

    avg_cost = total_cost / total_recipes if total_recipes > 0 else 0

    summary = f"""Recipe Database Summary

Total Recipes: {total_recipes}
Available Dietary Tags: {', '.join(sorted(all_tags))}
Average Recipe Cost: ${avg_cost:.2f}
Total Database Value: ${total_cost:.2f}

Recipe List:
{chr(10).join(f"  - {name}" for name in all_recipes.keys())}
"""
    return summary


@mcp.resource("recipe://tags/available")
def get_available_tags() -> str:
    """
    Provides a list of all available dietary tags in the database.
    """
    all_tags = set()
    tag_counts = {}

    for recipe_data in all_recipes.values():
        for tag in recipe_data['tags']:
            all_tags.add(tag)
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    result = "Available Dietary Tags:\n\n"
    for tag in sorted(all_tags):
        count = tag_counts[tag]
        result += f"  - {tag}: {count} recipe(s)\n"

    return result


if __name__ == "__main__":
    print("Starting Recipe MCP Server...")
    print(f"Server name: {mcp.name}")
    print(f"Total recipes available: {len(all_recipes)}")
    print("\nAvailable tools:")
    print("  - search_recipes_by_name")
    print("  - filter_recipes_by_tags")
    print("  - get_recipe_details")
    print("  - list_all_recipes")
    print("  - search_by_ingredient")
    print("  - get_recipes_by_budget")
    print("\nStarting server...\n")
    mcp.run()
