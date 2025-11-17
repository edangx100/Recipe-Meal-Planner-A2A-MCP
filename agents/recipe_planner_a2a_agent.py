"""
Recipe Planner Agent for A2A Communication

This module creates an ADK-compatible agent wrapper around the LangGraph state machine
for recipe planning. This agent can be exposed via A2A protocol without using LangGraphAgent.

The wrapper:
1. Takes user requests as input
2. Runs the LangGraph state machine
3. Returns the recipe plan results
4. Can be exposed via to_a2a() for remote access
"""

import os
import sys
import asyncio
from typing import Optional
from langchain_core.messages import HumanMessage

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.adk.agents import Agent as AdkAgent
from google.adk.models.google_llm import Gemini
from google.genai import types

from agents.langgraph_helper import (
    get_recipe_graph,
    is_langgraph_available,
    RecipePlannerState
)

# Retry configuration for Gemini model
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)


def run_recipe_planner(user_request: str) -> str:
    """
    Tool function that runs the LangGraph recipe planning workflow.

    This function wraps the LangGraph state machine execution and makes it
    accessible as a standard Python function that can be used by ADK agents.

    Args:
        user_request: User's meal planning request (e.g., "Plan 5 vegetarian dinners")

    Returns:
        String containing the recipe plan with selected recipes and optimized grocery list
    """
    import nest_asyncio
    nest_asyncio.apply()

    # Get the compiled LangGraph state machine
    recipe_graph = get_recipe_graph()

    if not recipe_graph:
        return "Error: Recipe planning system not available. Please check LangGraph setup."

    # Create initial state with user's message
    initial_state: RecipePlannerState = {
        "messages": [HumanMessage(content=user_request)],
        "dietary_preferences": "",
        "num_recipes": 5,
        "recipe_suggestions": [],
        "ingredient_list": [],
        "needs_cost_calculation": False
    }

    # Run the graph synchronously
    loop = asyncio.get_event_loop()

    try:
        # Invoke the graph with the initial state
        config = {"configurable": {"thread_id": "recipe_planning_thread"}}
        final_state = loop.run_until_complete(
            asyncio.to_thread(recipe_graph.invoke, initial_state, config)
        )

        # Extract the final message content
        if final_state and 'messages' in final_state:
            messages = final_state['messages']
            # Get all AI messages
            ai_messages = [msg.content for msg in messages if hasattr(msg, 'content')]

            # Combine messages for comprehensive response
            response = "\n\n".join(ai_messages)

            # Include recipe list and ingredient summary
            if 'recipe_suggestions' in final_state and final_state['recipe_suggestions']:
                recipe_list = "\n".join([f"  {i+1}. {r}" for i, r in enumerate(final_state['recipe_suggestions'])])
                response += f"\n\n📝 Selected Recipes:\n{recipe_list}"

            if 'ingredient_list' in final_state and final_state['ingredient_list']:
                num_ingredients = len(set([ing['item'] for ing in final_state['ingredient_list']]))
                response += f"\n\n🛒 Total unique ingredients: {num_ingredients}"

            return response
        else:
            return "Recipe planning completed but no output was generated."

    except Exception as e:
        return f"Error running recipe planner: {str(e)}"


# Create the Recipe Planner Agent using ADK
# This agent wraps the LangGraph execution as a tool
recipe_planner_agent = AdkAgent(
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    name="recipe_planner_agent",
    description="Recipe planning agent that creates meal plans based on dietary preferences and requirements using a LangGraph state machine workflow.",
    instruction="""
    You are a recipe planning specialist powered by a LangGraph state machine.

    When users request meal plans:
    1. Use the run_recipe_planner tool with their complete request
    2. The tool will execute the full workflow:
       - Gather dietary preferences and number of recipes
       - Suggest appropriate recipes from the database
       - Check for ingredient overlap across recipes
       - Optimize the grocery list by consolidating ingredients
    3. Return the complete recipe plan with selected recipes and shopping list

    The workflow is fully automated - just pass the user's request to the tool.
    Be professional and helpful in presenting the results.
    """,
    tools=[run_recipe_planner]  # Register the LangGraph wrapper as a tool
)


def get_recipe_planner_agent():
    """Returns the Recipe Planner Agent for use in other modules"""
    if not is_langgraph_available():
        raise RuntimeError("LangGraph is not available. Cannot create Recipe Planner Agent.")
    return recipe_planner_agent


if __name__ == "__main__":
    print("✅ Recipe Planner Agent (A2A-compatible) created successfully!")
    print("   Agent name:", recipe_planner_agent.name)
    print("   Description:", recipe_planner_agent.description)
    print("   Tools:", [tool.__name__ if callable(tool) else str(tool) for tool in recipe_planner_agent.tools])
    print("\nThis agent can be exposed via A2A using to_a2a()")
