"""Test script to debug agent responses"""

import asyncio
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
from utils import load_environment_variables
from agents.orchestrator import orchestrator

load_environment_variables()

async def test_agent():
    if not orchestrator:
        print("ERROR: Orchestrator not initialized")
        return

    runner = InMemoryRunner(agent=orchestrator)

    # Test query
    query = "Plan 3 vegetarian dinners under $50 total with a focus on protein"
    print(f"Query: {query}\n")
    print("Response:\n")

    try:
        response = await runner.run_debug(query)
        print(f"\nDone!")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_agent())
