"""
ADK Web Interface for Recipe Meal Planner - A2A Version

This file exports the agent for use with `adk web` command.

IMPORTANT: This version uses A2A (Agent-to-Agent) communication.
Before starting the web interface, you MUST start the Recipe Planner A2A Server:

    Terminal 1: python recipe_planner_a2a_server.py
    Terminal 2: adk web --agent_path agents_web/recipe_meal_planner

Architecture:
- Uses orchestrator_a2a (with RemoteA2aAgent)
- Communicates with Recipe Planner via A2A protocol on port 8001
- Recipe Planner runs LangGraph WITHOUT using LangGraphAgent
"""

import sys
import os
import requests

# Add the parent directory to the path so we can import from the main project
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from agents.orchestrator_a2a import get_orchestrator_a2a, RECIPE_PLANNER_A2A_URL, AGENT_CARD_WELL_KNOWN_PATH

# Check if Recipe Planner A2A Server is running
def check_server():
    """Check if Recipe Planner A2A server is running"""
    try:
        response = requests.get(
            f"{RECIPE_PLANNER_A2A_URL}{AGENT_CARD_WELL_KNOWN_PATH}",
            timeout=2
        )
        return response.status_code == 200
    except:
        return False

# Verify server is running
if not check_server():
    print("\n" + "="*80)
    print("⚠️  WARNING: Recipe Planner A2A Server is NOT running!")
    print("="*80)
    print("\nThe A2A web interface requires the Recipe Planner server to be running.")
    print("\nTo start the server, open a new terminal and run:")
    print("   python recipe_planner_a2a_server.py")
    print("\nOr run in background:")
    print("   python recipe_planner_a2a_server.py > /tmp/a2a_server.log 2>&1 &")
    print("\nThen restart the web interface.")
    print("="*80 + "\n")
    # Don't exit - let the user see the error in the web UI
else:
    print("\n" + "="*80)
    print("✅ Recipe Planner A2A Server detected!")
    print("="*80)
    print(f"   Server URL: {RECIPE_PLANNER_A2A_URL}")
    print(f"   Agent Card: {RECIPE_PLANNER_A2A_URL}{AGENT_CARD_WELL_KNOWN_PATH}")
    print("   Architecture: Distributed (A2A)")
    print("="*80 + "\n")

# Get the A2A orchestrator
orchestrator_a2a = get_orchestrator_a2a()

# Export the agent for ADK web - must be named 'root_agent'
root_agent = orchestrator_a2a
