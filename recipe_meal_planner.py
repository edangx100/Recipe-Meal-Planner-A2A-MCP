"""
Recipe Meal Planner - A2A Version

This version uses Agent-to-Agent (A2A) communication architecture.

Architecture:
- Orchestrator: Receives meal planning requests (uses RemoteA2aAgent)
- Recipe Planner Agent: Remote LangGraph-based agent via A2A (port 8001)
  * Gathers dietary preferences
  * Suggests recipes
  * Checks ingredient overlap
  * Optimizes grocery list
- Code Savvy Agent: Local agent for calculations
  * Calculates total costs
  * Optimizes for budget constraints
  * Generates shopping list with quantities

Prerequisites:
  1. Start the Recipe Planner A2A Server:
     python recipe_planner_a2a_server.py

  2. Then run this script:
     python recipe_meal_planner_a2a.py

Usage:
  python recipe_meal_planner_a2a.py
"""

from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
import asyncio
import requests

from utils import load_environment_variables, create_session
from agents.orchestrator_agent import get_orchestrator_a2a, RECIPE_PLANNER_A2A_URL, AGENT_CARD_WELL_KNOWN_PATH

load_environment_variables()


def check_recipe_planner_server():
    """Check if Recipe Planner A2A server is running"""
    try:
        response = requests.get(
            f"{RECIPE_PLANNER_A2A_URL}{AGENT_CARD_WELL_KNOWN_PATH}",
            timeout=5
        )
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


# --- Main Execution ---
if __name__ == "__main__":
    print("\n" + "="*80)
    print("🍽️  RECIPE MEAL PLANNER - A2A VERSION")
    print("="*80)

    # Check if Recipe Planner A2A Server is running
    print("\n🔍 Checking Recipe Planner A2A Server...")
    print(f"   Server URL: {RECIPE_PLANNER_A2A_URL}")

    if not check_recipe_planner_server():
        print("\n" + "="*80)
        print("❌ ERROR: Recipe Planner A2A Server is NOT running!")
        print("="*80)
        print("\nThe A2A version requires the Recipe Planner to be running as a server.")
        print("\nTo start the server, open a new terminal and run:")
        print("   python recipe_planner_a2a_server.py")
        print("\nOr run in background:")
        print("   python recipe_planner_a2a_server.py > /tmp/a2a_server.log 2>&1 &")
        print("\nThen run this script again.")
        print("="*80 + "\n")
        exit(1)

    print("   ✅ Recipe Planner A2A Server is running!")
    print(f"   Agent Card: {RECIPE_PLANNER_A2A_URL}{AGENT_CARD_WELL_KNOWN_PATH}")

    # Get the A2A-enabled orchestrator
    print("\n🤖 Initializing A2A Orchestrator...")
    orchestrator = get_orchestrator_a2a()
    print(f"   ✅ Orchestrator: {orchestrator.name}")
    print(f"   ✅ Architecture: Distributed (A2A)")
    print(f"   ✅ Recipe Planner: Remote via A2A")
    print(f"   ✅ Code Agent: Local")

    # Create runner
    runner = InMemoryRunner(agent=orchestrator, app_name="RecipeMealPlannerA2A")
    session_id = "s_recipe_planner_a2a"
    user_id = "recipe_user_a2a"
    create_session(runner, user_id=user_id, session_id=session_id)

    # Test prompts
    prompts = [
        "Plan 5 dinners under $50 total",
        "Plan 3 vegetarian dinners under $50 total with a focus on protein"
    ]

    async def main():
        for i, prompt_text in enumerate(prompts):
            print(f"\n{'='*80}")
            print(f"--- Meal Planning Request {i+1} (via A2A) ---")
            print(f"{'='*80}")
            print(f"YOU: {prompt_text}")
            print()
            print("🔄 Communication Flow:")
            print(f"   User → Orchestrator → RemoteA2aAgent → HTTP/A2A → Recipe Planner Server")
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

    print("\n" + "="*80)
    print("🚀 Starting A2A Meal Planning...")
    print("="*80)

    asyncio.run(main())

    print("\n" + "="*80)
    print("✅ A2A MEAL PLANNING COMPLETED")
    print("="*80)
    print("\nArchitecture Used:")
    print("  • Orchestrator: orchestrator_agent.py (with RemoteA2aAgent)")
    print("  • Recipe Planner: Remote A2A server on port 8001")
    print("  • Code Agent: Local execution")
    print("  • Communication: A2A Protocol (HTTP/JSON-RPC)")
    print("="*80 + "\n")
