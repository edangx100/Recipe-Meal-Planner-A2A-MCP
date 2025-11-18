"""
Orchestrator Agent for A2A Communication

This module contains the orchestrator agent that coordinates between:
- recipe_planner_agent: Remote LangGraph-based agent accessed via A2A
- code_savvy_agent_builtin: Local ADK agent for budget optimization

This demonstrates Agent-to-Agent (A2A) communication where the orchestrator
consumes a remote Recipe Planner Agent instead of using a local LangGraphAgent wrapper.
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from google.adk.agents import Agent as AdkAgent
from google.adk.agents.remote_a2a_agent import (
    RemoteA2aAgent,
    AGENT_CARD_WELL_KNOWN_PATH,
)
from google.adk.tools import agent_tool
# from google.adk.models.google_llm import Gemini
# from google.genai import types

from utils import DEFAULT_REASONING_LLM
from agents.code_savy_agent import code_savvy_agent_builtin

# Configuration
RECIPE_PLANNER_A2A_URL = "http://localhost:8001"

# # Retry configuration
# retry_config = types.HttpRetryOptions(
#     attempts=5,
#     exp_base=7,
#     initial_delay=1,
#     http_status_codes=[429, 500, 503, 504],
# )


# Create a RemoteA2aAgent that connects to the Recipe Planner Agent
# This acts as a client-side proxy - the Orchestrator can use it like a local agent
remote_recipe_planner_agent = RemoteA2aAgent(
    name="recipe_planner_agent",
    description="Remote recipe planning agent (LangGraph-based) that provides meal plans based on dietary preferences.",
    # Point to the agent card URL - this is where the A2A protocol metadata lives
    agent_card=f"{RECIPE_PLANNER_A2A_URL}{AGENT_CARD_WELL_KNOWN_PATH}",
)


# Orchestrator Agent uses both remote and local agents
orchestrator_a2a = AdkAgent(
    model=DEFAULT_REASONING_LLM,
    name="meal_plan_orchestrator_a2a",
    description="Orchestrator agent that coordinates meal planning using A2A communication with remote Recipe Planner Agent.",
    instruction="""
    You are a meal planning orchestrator that coordinates between multiple agents.

    When users request meal plans:
    1. Delegate to recipe_planner_agent (REMOTE via A2A) to handle the recipe selection workflow:
       - This agent runs a LangGraph state machine that gathers preferences
       - Suggests recipes based on dietary needs
       - Checks ingredient overlap
       - Optimizes the grocery list

    2. Once the recipe_planner_agent provides the recipe plan and ingredient list, delegate to code_savvy_agent_builtin (LOCAL) to:
       - Calculate total costs from the ingredient list
       - Ensure budget compliance (under $50)
       - Generate final shopping list with quantities and prices
       - Suggest alternatives if over budget

    Coordinate between both agents to deliver a complete meal plan.

    IMPORTANT: When providing feedback to the user, you MUST:
    - List ALL the recipe names that were selected by the recipe_planner_agent
    - Extract the complete list of recipes from the response
    - Include every single recipe in your final response
    - Show the complete shopping list with estimated prices

    FORMAT YOUR RESPONSE AS FOLLOWS:

    Here is your meal plan:

    1. [Recipe Name 1]
    2. [Recipe Name 2]
    3. [Recipe Name 3]
    ...

    Here is your shopping list:

    * [Ingredient 1]: [quantity]
    * [Ingredient 2]: [quantity]
    ...

    And here are the estimated prices:

    * [Ingredient 1] ([quantity]): $[price]
    * [Ingredient 2] ([quantity]): $[price]
    ...

    Total cost: $[total]
    Enjoy your meals!
    """,
    tools=[
        agent_tool.AgentTool(agent=remote_recipe_planner_agent),  # Remote A2A agent
        agent_tool.AgentTool(agent=code_savvy_agent_builtin)      # Local agent
    ]
)


def get_orchestrator_a2a():
    """Returns the A2A-enabled Orchestrator Agent"""
    return orchestrator_a2a


if __name__ == "__main__":
    print("✅ Orchestrator Agent (A2A-enabled) created successfully!")
    print(f"   Agent name: {orchestrator_a2a.name}")
    print(f"   Remote Recipe Planner URL: {RECIPE_PLANNER_A2A_URL}")
    print(f"   Agent card: {RECIPE_PLANNER_A2A_URL}{AGENT_CARD_WELL_KNOWN_PATH}")
    print(f"   Tools: {len(orchestrator_a2a.tools)} agents (1 remote via A2A, 1 local)")
    print("\nThe orchestrator will communicate with the Recipe Planner Agent via A2A protocol.")
    print("Make sure the Recipe Planner A2A server is running on port 8001.")
