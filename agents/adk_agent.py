"""
ADK Agent Components for Recipe Meal Planner

This module contains the code_savvy_agent_builtin used for budget optimization
with Python code execution capabilities.
"""

from google.adk.agents import Agent as AdkAgent
from google.adk.code_executors import BuiltInCodeExecutor

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import DEFAULT_LLM


# --- Code Savvy Agent for Cost Calculations ---
code_savvy_agent_builtin = AdkAgent(
    name="code_savvy_agent_builtin",
    model=DEFAULT_LLM,
    instruction="""You are a budget optimization specialist that can write and execute Python code.

Your tasks:
1. Calculate total costs for meal plans and shopping lists
2. Optimize for budget constraints (ensure total stays under $50)
3. Generate detailed shopping lists with quantities and prices
4. Provide cost breakdowns and savings analysis

When you receive ingredient lists or meal plans, write Python code to:
- Calculate total costs
- Check if within budget
- Suggest substitutions if over budget
- Format shopping lists with quantities and prices

Your code will be automatically executed.""",
    code_executor=BuiltInCodeExecutor()
)
