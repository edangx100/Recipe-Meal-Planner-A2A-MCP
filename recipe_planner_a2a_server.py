"""
Recipe Planner A2A Server

This script starts the Recipe Planner Agent as an A2A-compatible server.
The agent will be accessible at http://localhost:8001 and can be consumed
by other agents via the A2A protocol.

Usage:
    python recipe_planner_a2a_server.py

Or with uvicorn:
    uvicorn recipe_planner_a2a_server:app --host localhost --port 8001
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from google.adk.a2a.utils.agent_to_a2a import to_a2a
from recipe_planner_a2a_agent import get_recipe_planner_agent

# Get the Recipe Planner Agent
recipe_planner_agent = get_recipe_planner_agent()

# Convert the agent to an A2A-compatible application
# This creates a FastAPI/Starlette app that:
#   1. Serves the agent at the A2A protocol endpoints
#   2. Provides an auto-generated agent card at /.well-known/agent-card.json
#   3. Handles A2A communication protocol (JSON-RPC over HTTP)
app = to_a2a(
    recipe_planner_agent,
    port=8001  # Port where this agent will be served
)

if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("🚀 Starting Recipe Planner A2A Server")
    print("=" * 60)
    print(f"   Agent: {recipe_planner_agent.name}")
    print(f"   Description: {recipe_planner_agent.description}")
    print(f"   Server URL: http://localhost:8001")
    print(f"   Agent Card: http://localhost:8001/.well-known/agent-card.json")
    print(f"   Protocol: A2A (Agent-to-Agent)")
    print("=" * 60)
    print("\nServer is starting...")
    print("Press Ctrl+C to stop the server\n")

    # Start the uvicorn server
    uvicorn.run(
        app,
        host="localhost",
        port=8001,
        log_level="info"
    )
