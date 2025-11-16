# Recipe Meal Planner

An intelligent meal planning system built with Google ADK (Agent Development Kit) and LangGraph that creates budget-conscious meal plans with optimized shopping lists.

## Overview

This project demonstrates a multi-agent architecture where specialized AI agents collaborate to plan meals, optimize grocery lists, and ensure budget compliance. The system takes user requests like "Plan 5 dinners under $50 total" and returns a complete meal plan with consolidated shopping lists and cost breakdowns.

## Features

- **Smart Dietary Filtering**: Automatically detects and filters recipes based on preferences (vegetarian, vegan, gluten-free, low-carb)
- **Ingredient Consolidation**: Identifies shared ingredients across recipes to optimize shopping efficiency
- **Budget Optimization**: Ensures meal plans stay within specified budget constraints (default: $50)
- **Cost Calculation**: Generates detailed shopping lists with quantities and prices
- **Structured Output Parsing**: Uses LLM structured output to extract meal planning requirements from natural language

## Architecture (3-Agent System)

### 1. Orchestrator Agent (`meal_plan_orchestrator`)
- **Role**: Main coordinator that receives user requests and delegates tasks
- **Capabilities**:
  - Routes requests to appropriate specialized agents
  - Ensures meal plans meet budget requirements
  - Formats final output with recipe lists and shopping details
- **Model**: Gemini 2.5 Flash (reasoning model)

### 2. Recipe Planner Agent (`recipe_planner_agent`)
- **Role**: Handles recipe selection logic using a LangGraph state machine
- **Workflow**: 4-node state machine
  1. `gather_preferences`: Extracts dietary requirements and recipe count using LLM structured output (Pydantic models)
  2. `suggest_recipes`: Selects recipes from database based on preferences
  3. `check_overlap`: Identifies shared ingredients across selected recipes
  4. `optimize_list`: Consolidates ingredients into a unified shopping list
- **State Management**: Uses MemorySaver for checkpointing between nodes
- **Output**: Triggers `[CALCULATE_COST]` flag when ready for cost calculation

### 3. Code Savvy Agent (`code_savvy_agent_builtin`)
- **Role**: Budget optimization specialist with Python code execution
- **Capabilities**:
  - Calculates total costs using executable Python code
  - Validates budget constraints
  - Suggests substitutions if over budget
  - Generates formatted shopping lists with quantities and prices
- **Code Executor**: BuiltInCodeExecutor for running Python scripts

## Recipe Database

The system includes 10 pre-configured recipes in `recipes.py`:

| Recipe | Estimated Cost | Dietary Tags |
|--------|---------------|--------------|
| Spaghetti Aglio e Olio | $4.50 | vegetarian, vegan |
| Chicken Stir-Fry | $8.99 | gluten-free |
| Black Bean Tacos | $10.00 | vegetarian, vegan, gluten-free |
| Lentil Soup | $6.50 | vegetarian, vegan, gluten-free |
| Baked Salmon with Veggies | $10.99 | gluten-free, low-carb |
| Veggie Fried Rice | $5.00 | vegetarian |
| Margherita Pizza | $9.00 | vegetarian |
| Greek Salad | $11.25 | vegetarian, gluten-free, low-carb |
| Beef Chili | $10.74 | gluten-free |
| Mushroom Risotto | $15.00 | vegetarian, gluten-free |

Each recipe includes detailed ingredient lists with quantities and individual prices.

## Workflow

```
User: "Plan 5 dinners under $50 total"
              ↓
┌─────────────────────────────────────┐
│   Orchestrator Agent                │
│   (meal_plan_orchestrator)          │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   Recipe Planner Agent              │
│   (LangGraph State Machine)         │
├─────────────────────────────────────┤
│ 1. gather_preferences               │
│    - Parse user request             │
│    - Extract dietary restrictions   │
│    - Determine recipe count         │
├─────────────────────────────────────┤
│ 2. suggest_recipes                  │
│    - Filter by dietary tags         │
│    - Select N recipes               │
├─────────────────────────────────────┤
│ 3. check_overlap                    │
│    - Identify shared ingredients    │
│    - Group by item name             │
├─────────────────────────────────────┤
│ 4. optimize_list                    │
│    - Consolidate quantities         │
│    - Set [CALCULATE_COST] flag      │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   Code Savvy Agent                  │
│   (code_savvy_agent_builtin)        │
├─────────────────────────────────────┤
│ - Generate Python code              │
│ - Calculate total costs             │
│ - Verify budget constraints         │
│ - Format shopping list              │
└─────────────────────────────────────┘
              ↓
        Final Meal Plan
        (Recipes + Shopping List + Costs)
```

## Project Structure

```
/home/ed/kaggle/recipe/
├── recipe_meal_planner.py      # Main entry point
├── recipes.py                   # Recipe database with 10 recipes
├── utils.py                     # Environment variables & session management
├── agents/
│   ├── orchestrator.py         # Main orchestrator agent
│   ├── langgraph_agent.py      # LangGraph state machine for recipe planning
│   └── adk_agent.py            # Code execution agent
├── .env                        # API keys (not included)
└── README.md                   # This file
```

## Setup & Installation

### Prerequisites

- Python 3.8+
- Google API key with access to Gemini models

### Installation

[uv](https://github.com/astral-sh/uv) is an extremely fast Python package installer and resolver.

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/edangx100/Recipe-Meal-Planner.git
cd Recipe-Meal-Planner

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies from requirements.txt
uv pip install -r requirements.txt
```

**Important: Configure your API key**

Edit the `.env` file and replace the placeholder `GOOGLE_API_KEY` with your own Google API key:

```bash
# .env file
GOOGLE_API_KEY=your_actual_api_key_here  # Replace with your real API key

# Model configuration (optional - defaults provided)
DEFAULT_LLM=gemini-2.0-flash              # For general tasks
DEFAULT_REASONING_LLM=gemini-2.5-flash    # For orchestrator
```

To get a Google API key, visit: https://aistudio.google.com/app/apikey

These values are loaded from environment variables with sensible defaults in `utils.py`.

## Usage

### Running the Application

```bash
python recipe_meal_planner.py
```

### Example Requests

The script includes two test scenarios:

1. **Basic meal plan**:
   ```
   "Plan 5 dinners under $50 total"
   ```

2. **Vegetarian with protein focus**:
   ```
   "Plan 3 vegetarian dinners under $50 total with a focus on protein"
   ```

### Expected Output

```
===========================================
--- Meal Planning Request 1 ---
===========================================
YOU: Plan 5 dinners under $50 total

ORCHESTRATOR: Here is your meal plan:

1. Spaghetti Aglio e Olio
2. Chicken Stir-Fry
3. Black Bean Tacos
4. Lentil Soup
5. Baked Salmon with Veggies

Here is your shopping list:

* spaghetti: 1 lb
* garlic: 1 bulb
* olive oil: 1/2 cup + 2 tbsp
* chicken breast: 1 lb
...

Total Cost: $47.23

Enjoy your meals!
```

## Key Technical Features

- **LangGraph State Machine**: Stateful workflow with 4 nodes and conditional routing
- **Structured Output Parsing**: Uses Pydantic models to parse natural language requests
- **Memory Checkpointing**: MemorySaver enables state persistence across nodes
- **Code Execution**: BuiltInCodeExecutor allows agents to run Python for calculations
- **Async Architecture**: Uses `asyncio` for non-blocking agent communication
- **Agent-to-Agent Communication**: Orchestrator delegates to specialized agents using AgentTool
