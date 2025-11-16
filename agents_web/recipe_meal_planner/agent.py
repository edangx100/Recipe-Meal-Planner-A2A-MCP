"""
ADK Web Interface for Recipe Meal Planner
This file exports the agent for use with `adk web` command.
"""

import sys
import os

# Add the parent directory to the path so we can import from the main project
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from agents.orchestrator import orchestrator

# Export the agent for ADK web - must be named 'root_agent'
root_agent = orchestrator
