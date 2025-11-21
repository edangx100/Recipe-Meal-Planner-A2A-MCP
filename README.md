# Recipe Meal Planner

<p align="center">
  <img src="image1.png" alt="Recipe Meal Planner" width="40%">
</p>

**🎥 [Watch Video Demo](https://youtu.be/asA3a4Aty1Q?si=-avvi_KOckVNIzhC)**

An intelligent meal planning system built with Google ADK (Agent Development Kit) and LangGraph that creates budget-conscious meal plans with optimized shopping lists.

## Overview

This project demonstrates a multi-agent architecture where specialized AI agents collaborate to plan meals, optimize grocery lists, and ensure budget compliance. The system takes user requests like "Plan 5 dinners under $50 total" and returns a complete meal plan with consolidated shopping lists and cost breakdowns.

## Features

- **Smart Dietary Filtering**: Automatically detects and filters recipes based on preferences (vegetarian, vegan, gluten-free, low-carb)
- **Ingredient Consolidation**: Identifies shared ingredients across recipes to optimize shopping efficiency
- **Budget Optimization**: Ensures meal plans stay within specified budget constraints (default: $50)
- **Cost Calculation**: Generates detailed shopping lists with quantities and prices

## Technical Features

### ✅1. Multi-agent System

**Three LLM-Powered Agents**

1. **Orchestrator Agent** (`agents/orchestrator_agent.py`)
2. **Recipe Planner Agent** (`recipe_planner_a2a_agent.py` with `agents/langgraph_agent_mcp.py`)
3. **Code Savvy Agent** (`agents/adk_agent.py`)

### ✅2. Tools

**Custom Tools:**
- **run_recipe_planner** (`recipe_planner_a2a_agent.py`) - Wraps LangGraph state machine as tool function used by Recipe Planner Agent

**Built-in Tools:**
- **BuiltInCodeExecutor** (`agents/adk_agent.py`) - Enables dynamic Python code generation and execution for budget calculations and cost optimization

### ✅3. Sessions & Memory

**Session Management:**
- **InMemorySessionService** (`utils.py`) - Creates and manages user sessions with session_id and user_id tracking

### ✅4. Agent2Agent (A2A) Communication 

**A2A Communication:**
- **RemoteA2aAgent** - Recipe Planner runs as independent server, Orchestrator as client. Orchestrator consumes Recipe Planner via A2A protocol

### ✅5. Model Context Protocol (MCP)

**MCP Integration:**
- **MCP Client** - Used in `langgraph_agent_mcp.py` to connect to MCP server for recipe data access
- **MCP Server** (`recipe_mcp_server.py`) - Provides 6 tools and 2 resources for recipe database operations

#### MCP Server Tools

The MCP server (`recipe_mcp_server.py`) exposes the following tools for recipe database operations:

**Tools (6):**
1. **search_recipes_by_name** - Search for recipes by name (case-insensitive partial match)
2. **filter_recipes_by_tags** - Filter recipes by dietary tags/preferences (vegetarian, vegan, gluten-free, low-carb)
3. **get_recipe_details** - Get complete details for a specific recipe including ingredients with quantities and prices
4. **list_all_recipes** - List all available recipes with tags and estimated costs
5. **search_by_ingredient** - Find all recipes that contain a specific ingredient
6. **get_recipes_by_budget** - Find all recipes within a specified budget per recipe

**Resources (2):**
1. **recipe://database/summary** - Provides database statistics (total recipes, available tags, average cost)
2. **recipe://tags/available** - Lists all available dietary tags with recipe counts


## Architecture (3-Agent System)

### 1. Orchestrator Agent (`meal_plan_orchestrator_a2a`)
**File**: `agents/orchestrator_agent.py`

- **Role**: Main coordinator that receives user requests and delegates tasks to other agents
- **Communication Pattern**:
  - Consumes Recipe Planner Agent via **RemoteA2aAgent** (using A2A protocol)
  - Invokes Code Savvy Agent locally via **AgentTool**
- **Capabilities**:
  - Routes meal planning requests to remote Recipe Planner Agent
  - Delegates cost calculations to local Code Savvy Agent
  - Ensures meal plans meet budget requirements
  - Formats final output with recipe lists and shopping details
- **Model**: Gemini 2.5 Flash (reasoning model)

### 2. Recipe Planner Agent (`recipe_planner_agent`)
**Files**: `agents/recipe_planner_a2a_agent.py`, `agents/langgraph_helper.py`

- **Role**: Handles recipe selection logic using a LangGraph state machine accessed via MCP
- **Deployment**: Runs as independent A2A server on port 8001 (`recipe_planner_a2a_server.py`)
- **Tool**: `run_recipe_planner()` function wraps the LangGraph state machine for ADK compatibility
- **Workflow**: 4-node LangGraph state machine
  1. `gather_preferences`: Extracts dietary requirements and recipe count using LLM structured output (Pydantic models)
  2. `suggest_recipes`: Selects recipes from database via MCP client (calls `filter_recipes_by_tags`, `list_all_recipes`, `get_recipe_details`)
  3. `check_overlap`: Identifies shared ingredients across selected recipes
  4. `optimize_list`: Consolidates ingredients into a unified shopping list and flags for cost calculation
- **MCP Integration**: Uses `RecipeMCPClient` to access recipe database via MCP protocol
- **Model**: Gemini 2.5 Flash Lite

<p align="center">
  <img src="langgraph_image.png" alt="LangGraph State Machine" width="16%">
</p>

### 3. Code Savvy Agent (`code_savvy_agent_builtin`)
**File**: `agents/code_savy_agent.py`

- **Role**: Budget optimization specialist with Python code execution capabilities
- **Deployment**: Runs locally within Orchestrator Agent process (not A2A)
- **Capabilities**:
  - Generates and executes Python code for cost calculations
  - Validates budget constraints (default: $50)
  - Suggests substitutions if over budget
  - Formats shopping lists with quantities and prices
  - Provides cost breakdowns and savings analysis
- **Code Executor**: BuiltInCodeExecutor for safe Python script execution
- **Model**: Gemini 2.0 Flash

## Recipe Database

The system includes 10 pre-configured recipes in `recipes.py`.  
Each recipe includes detailed ingredient lists with quantities and individual prices.

## Workflow

```
User: "Plan 5 dinners under $50 total"
              ↓
┌─────────────────────────────────────┐
│   Orchestrator Agent (ADK)          │
│   (agents/orchestrator_agent.py)    │
└─────────────────────────────────────┘
              ↓ RemoteA2aAgent (A2A Protocol)
              ↓ HTTP/JSON-RPC to port 8001
┌─────────────────────────────────────┐
│ Recipe Planner A2A Server           │
│ (recipe_planner_a2a_server.py)      │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ Recipe Planner Agent            │ │
│ │ (recipe_planner_a2a_agent.py)   │ │
│ │                                 │ │
│ │ Tool: run_recipe_planner()      │ │
│ │   ↓                             │ │
│ │ ┌─────────────────────────────┐ │ │
│ │ │ LangGraph State Machine     │ │ │
│ │ │ (langgraph_agent_mcp.py)    │ │ │
│ │ ├─────────────────────────────┤ │ │
│ │ │ 1. gather_preferences       │ │ │
│ │ │    - Parse user request     │ │ │
│ │ │    - Extract dietary info   │ │ │
│ │ ├─────────────────────────────┤ │ │
│ │ │ 2. suggest_recipes          │ │ │
│ │ │    - Filter via MCP ────────┼─┼─┼──> MCP Client
│ │ │    - Select N recipes       │ │ │         ↓
│ │ ├─────────────────────────────┤ │ │   ┌──────────────┐
│ │ │ 3. check_overlap            │ │ │   │  MCP Server  │
│ │ │    - Find shared items      │ │ │   │ (recipe_mcp_ │
│ │ ├─────────────────────────────┤ │ │   │  server.py)  │
│ │ │ 4. optimize_list            │ │ │   └──────┬───────┘
│ │ │    - Consolidate quantities │ │ │          ↓
│ │ │    - Flag: [CALCULATE_COST] │ │ │   ┌──────────────┐
│ │ └─────────────────────────────┘ │ │   │  recipes.py  │
│ └─────────────────────────────────┘ │   └──────────────┘
└─────────────────────────────────────┘
              ↓ A2A Response
┌─────────────────────────────────────┐
│   Orchestrator Agent (ADK)          │
└─────────────────────────────────────┘
              ↓ AgentTool invocation
┌─────────────────────────────────────┐
│   Code Savvy Agent (ADK)            │
│   (agents/adk_agent.py)             │
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
├── recipe_meal_planner.py          # Main CLI entry point with A2A
├── recipes.py                      # Recipe database
├── recipe_mcp_server.py            # MCP server for recipe database
├── utils.py                        # Environment variables & session management
├── __init__.py                     # Package initialization
├── agents/
│   ├── orchestrator_agent.py      # Orchestrator with A2A communication
│   ├── langgraph_helper.py        # LangGraph state machine with MCP
│   ├── code_savy_agent.py         # Code execution agent
│   └── recipe_planner_a2a_agent.py # Recipe planner ADK wrapper
├── recipe_planner_a2a_agent.py    # LangGraph wrapper for A2A
├── recipe_planner_a2a_server.py   # A2A server exposing Recipe Planner
├── start_a2a_web.sh               # Launch script for A2A web interface
├── agents_web/                     # ADK Web UI configuration
│   └── recipe_meal_planner/
│       ├── agent.py               # Web UI with A2A orchestrator
│       ├── README.md              # Web UI documentation
│       └── __init__.py            # Package initialization
├── .env                           # API keys
├── requirements.txt               # Python dependencies
├── image1.png                     # Project screenshot
└── README.md                      # This file
```

## Setup & Installation

### Prerequisites

- Python 3.8+
- Google API key with access to Gemini models

### Installation

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/edangx100/Recipe-Meal-Planner-A2A-MCP
cd Recipe-Meal-Planner-A2A-MCP

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

**IMPORTANT: Start the Recipe Planner A2A Server First**

Before using either option below, you must start the Recipe Planner A2A Server:

```bash
# Terminal 1: Start the Recipe Planner A2A Server (required for both options)
python recipe_planner_a2a_server.py
```

Keep this server running in the background. The server runs on port 8001 and provides the Recipe Planner agent via A2A protocol.

### Option 1: ADK Web UI (Recommended - Interactive Interface)

Run the interactive web interface to chat with your meal planner agent:

```bash
# Terminal 2: Start ADK web UI (default port 8000)
# Make sure you're in the project directory
cd /home/ed/kaggle/recipe

# Activate virtual environment
source .venv/bin/activate

# Start ADK web UI
adk web agents_web
```

Then open your browser to **http://localhost:8000**

**Using a custom port:**

```bash
# Use a different port if 8000 is already in use
adk web --port 8080 agents_web
```

Then open **http://localhost:8080**

**Try these queries in the web UI:**

- "Plan 5 dinners under $50 total"
- "Plan 3 vegetarian dinners under $50 total with a focus on protein"

**What you'll see:**
- Real-time streaming of agent responses
- Detailed trace of the LangGraph state machine workflow
- Complete meal plans with recipes, shopping lists, and price breakdowns

### Option 2: CLI Mode (Pre-configured Queries)

Run the command-line version with pre-configured test scenarios:

```bash
# Terminal 2: Run the meal planner client (A2A server must be running in Terminal 1)
python recipe_meal_planner.py
```

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

## Troubleshooting

### ADK Web UI Issues

**Problem: Port already in use**
```bash
ERROR: [Errno 98] address already in use
```

**Solution:** Use a different port or kill the existing process:
```bash
# Option 1: Use a different port
adk web --port 8001 agents_web

# Option 2: Find and kill the process using port 8000
lsof -i :8000  # Find the PID
kill -9 <PID>  # Replace <PID> with the actual process ID
```