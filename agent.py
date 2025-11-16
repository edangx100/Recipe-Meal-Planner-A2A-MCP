"""
ADK Web Interface for Recipe Meal Planner
This file exports the agent for use with `adk web` command.
"""

from agents.orchestrator import orchestrator

# Export the agent for ADK web
agent = orchestrator
