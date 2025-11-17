"""
Orchestrator Agent for Recipe Meal Planner

This module contains the main orchestrator agent that coordinates between:
- recipe_planner_agent: LangGraph state machine for recipe selection
- code_savvy_agent_builtin: Budget optimization with code execution
"""

# Compatibility shim for google-adk with LangGraph 1.0.x
# google-adk expects CompiledGraph from langgraph.graph.graph, but in newer versions it's in langgraph.graph.state
# This must be imported BEFORE google.adk modules
import sys
import os
from types import ModuleType

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from langgraph.graph.state import CompiledStateGraph
    # Create the old module path that google-adk expects
    if 'langgraph.graph.graph' not in sys.modules:
        graph_module = ModuleType('graph')
        graph_module.CompiledGraph = CompiledStateGraph
        sys.modules['langgraph.graph.graph'] = graph_module
except ImportError:
    pass

from google.adk.agents import Agent as AdkAgent
from google.adk.agents.langgraph_agent import LangGraphAgent
from google.adk.tools import agent_tool

from utils import DEFAULT_REASONING_LLM
from agents.langgraph_agent_mcp import (
    get_recipe_graph,
    is_langgraph_available
)
from agents.adk_agent import code_savvy_agent_builtin


# --- Create LangGraph Agent ---
recipe_graph = get_recipe_graph()
LANGGRAPH_SETUP_SUCCESS = is_langgraph_available()

langgraph_adk_agent = None
orchestrator = None

if LANGGRAPH_SETUP_SUCCESS and recipe_graph:
    langgraph_adk_agent = LangGraphAgent(
        name="recipe_planner_agent",
        graph=recipe_graph,
        instruction="""You are a recipe planning agent powered by a state machine.

Your workflow:
1. Gather dietary preferences and number of recipes from user requests using LLM structured output
2. Suggest dinner recipes based on preferences and requested count
3. Check for ingredient overlap across recipes
4. Optimize the grocery list by consolidating ingredients

After optimizing the list, pass it to the code agent for cost calculations."""
    )
    print("Recipe planner LangGraphAgent initialized.")

    # --- Create Orchestrator Agent ---
    orchestrator = AdkAgent(
        name="meal_plan_orchestrator",
        model=DEFAULT_REASONING_LLM,
        instruction="""You are a meal planning orchestrator.

When users request meal plans:
1. Delegate to recipe_planner_agent to handle the recipe selection workflow
2. Once the recipe_planner_agent provides an optimized grocery list, delegate to code_savvy_agent_builtin to:
   - Calculate total costs
   - Calculate total estimated_prices of the shopping list
   - Ensure budget compliance (under $50)
   - Generate final shopping list with quantities and prices
   - Suggest alternatives if over budget

Coordinate between both agents to deliver a complete meal plan.

IMPORTANT: When providing feedback to the user, you MUST list ALL the recipe names that were selected by the recipe_planner_agent. Extract the complete list of recipes from the recipe_planner_agent's response and include every single one in your final response to the user. Do not summarize or truncate the recipe list - show all recipes that were selected.

FORMAT YOUR RESPONSE EXACTLY AS FOLLOWS:

Here is your meal plan:

1.  [Recipe Name 1]
2.  [Recipe Name 2]
3.  [Recipe Name 3]

Here is your shopping list:

*   [Ingredient 1]: [quantity]
*   [Ingredient 2]: [quantity]
*   [Ingredient 3]: [quantity]

And here are the estimated prices:

*   [Ingredient 1] ([quantity]): $[price]
*   [Ingredient 2] ([quantity]): $[price]
*   [Ingredient 3] ([quantity]): $[price]

Total cost: $[total_estimated_prices]
Enjoy your meals!""",
        tools=[
            agent_tool.AgentTool(agent=langgraph_adk_agent),
            agent_tool.AgentTool(agent=code_savvy_agent_builtin)
        ]
    )
    print("Meal plan orchestrator initialized.")
else:
    print("WARNING: LangGraph not available. Orchestrator not initialized.")
