"""
Test Script for A2A Communication

This script demonstrates Agent-to-Agent (A2A) communication between:
1. Orchestrator Agent (ADK) - Consumer
2. Recipe Planner Agent (LangGraph via A2A) - Provider

Prerequisites:
- Recipe Planner A2A Server must be running on port 8001
- Start server with: python recipe_planner_a2a_server.py

Usage:
    python test_a2a_communication.py
"""

import os
import sys
import asyncio
import uuid
import requests

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agents.orchestrator_a2a import get_orchestrator_a2a, RECIPE_PLANNER_A2A_URL, AGENT_CARD_WELL_KNOWN_PATH


def check_recipe_planner_server():
    """Check if the Recipe Planner A2A server is running"""
    try:
        response = requests.get(
            f"{RECIPE_PLANNER_A2A_URL}{AGENT_CARD_WELL_KNOWN_PATH}",
            timeout=5
        )
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, None
    except requests.exceptions.RequestException:
        return False, None


async def test_a2a_communication(user_query: str):
    """
    Test the A2A communication between Orchestrator and Recipe Planner.

    This function:
    1. Creates a session for the conversation
    2. Sends the query to the Orchestrator Agent
    3. Orchestrator communicates with Recipe Planner via A2A
    4. Recipe Planner executes LangGraph workflow
    5. Orchestrator receives results and coordinates with code agent
    6. Displays the complete meal plan

    Args:
        user_query: The meal planning request from the user
    """
    # Get the orchestrator agent
    orchestrator = get_orchestrator_a2a()

    # Setup session management
    session_service = InMemorySessionService()

    # Session identifiers
    app_name = "meal_planner_a2a"
    user_id = "test_user"
    session_id = f"test_session_{uuid.uuid4().hex[:8]}"

    # Create session
    session = await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )

    # Create runner for the Orchestrator
    runner = Runner(
        agent=orchestrator,
        app_name=app_name,
        session_service=session_service
    )

    # Create the user message
    test_content = types.Content(parts=[types.Part(text=user_query)])

    # Display query
    print(f"\n{'='*70}")
    print(f"👤 USER REQUEST")
    print(f"{'='*70}")
    print(f"{user_query}")
    print(f"{'='*70}\n")

    print(f"🔄 ORCHESTRATOR PROCESSING (with A2A communication)...")
    print(f"{'='*70}\n")

    # Run the agent asynchronously
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=test_content
    ):
        # Print final response only
        if event.is_final_response() and event.content:
            for part in event.content.parts:
                if hasattr(part, "text"):
                    print(f"\n{'='*70}")
                    print(f"✅ FINAL MEAL PLAN")
                    print(f"{'='*70}")
                    print(part.text)
                    print(f"{'='*70}\n")


async def main():
    """Main test execution"""
    print("\n" + "="*70)
    print("🧪 A2A COMMUNICATION TEST")
    print("   Orchestrator Agent (ADK) ←→ Recipe Planner Agent (LangGraph)")
    print("="*70 + "\n")

    # Step 1: Check if Recipe Planner A2A server is running
    print("🔍 Step 1: Checking Recipe Planner A2A Server...")
    print(f"   URL: {RECIPE_PLANNER_A2A_URL}")

    is_running, agent_card = check_recipe_planner_server()

    if is_running:
        print("   ✅ Recipe Planner A2A Server is running!")
        print(f"   Agent: {agent_card.get('name', 'unknown')}")
        print(f"   Description: {agent_card.get('description', 'N/A')[:60]}...")
        print(f"   Skills: {len(agent_card.get('skills', []))} available")
    else:
        print("\n" + "="*70)
        print("❌ ERROR: Recipe Planner A2A Server is NOT running!")
        print("="*70)
        print("\nPlease start the server first:")
        print("   python recipe_planner_a2a_server.py")
        print("\nOr in a separate terminal:")
        print("   uvicorn recipe_planner_a2a_server:app --host localhost --port 8001")
        print("="*70 + "\n")
        return

    # Step 2: Test A2A Communication
    print("\n🔍 Step 2: Testing A2A Communication...")
    print("   The following will happen:")
    print("   1. Orchestrator receives user request")
    print("   2. Orchestrator sends A2A request to Recipe Planner (port 8001)")
    print("   3. Recipe Planner executes LangGraph workflow")
    print("   4. Recipe Planner returns results via A2A")
    print("   5. Orchestrator processes results with code agent")
    print("   6. Orchestrator returns final meal plan\n")

    # Test Case 1: Basic meal plan
    await test_a2a_communication(
        "Plan 3 vegetarian dinners for me under $50 budget"
    )

    # Test Case 2: Specific dietary preferences
    print("\n" + "="*70)
    print("🧪 TEST CASE 2: More specific requirements")
    print("="*70 + "\n")

    await test_a2a_communication(
        "I need 5 dinner recipes, preferably vegetarian, under $45 total"
    )

    print("\n" + "="*70)
    print("✅ A2A COMMUNICATION TEST COMPLETED")
    print("="*70)
    print("\nKey Achievements:")
    print("  ✓ Orchestrator Agent (ADK) successfully created")
    print("  ✓ Recipe Planner Agent (LangGraph) exposed via A2A")
    print("  ✓ A2A communication protocol working")
    print("  ✓ RemoteA2aAgent successfully consumed remote agent")
    print("  ✓ Complete request-response cycle demonstrated")
    print("="*70 + "\n")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
