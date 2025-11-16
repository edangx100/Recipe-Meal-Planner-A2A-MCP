"""
Recipe Meal Planner
Creates a meal plan for 5 dinners under $50 total budget.

Architecture:
- Orchestrator: Receives meal planning requests
- langgraph_adk_agent: State machine for recipe selection logic
  * Gathers dietary preferences
  * Suggests recipes
  * Checks ingredient overlap
  * Optimizes grocery list
- code_savvy_agent_builtin: Performs calculations
  * Calculates total costs
  * Optimizes for budget constraints
  * Generates shopping list with quantities
"""

from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
import asyncio

from utils import load_environment_variables, create_session
from agents.orchestrator import orchestrator

load_environment_variables()

# --- Main Execution ---
if __name__ == "__main__":
    if not orchestrator:
        print("ERROR: Could not initialize orchestrator. Check LangGraph setup.")
        exit(1)

    runner = InMemoryRunner(agent=orchestrator, app_name="RecipeMealPlannerApp")
    session_id = "s_recipe_planner"
    user_id = "recipe_user"
    create_session(runner, user_id=user_id, session_id=session_id)

    prompts = [
        "Plan 5 dinners under $50 total",
        "Plan 3 vegetarian dinners under $50 total with a focus on protein"
    ]

    async def main():
        for i, prompt_text in enumerate(prompts):
            print(f"\n{'='*80}")
            print(f"--- Meal Planning Request {i+1} ---")
            print(f"{'='*80}")
            print(f"YOU: {prompt_text}")
            print()
            user_message_adk = Content(parts=[Part(text=prompt_text)], role="user")

            print("ORCHESTRATOR: ", end="", flush=True)
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=user_message_adk
            ):
                for part in event.content.parts:
                    if part.text:
                        print(part.text, end="", flush=True)
            print("\n")

    asyncio.run(main())
