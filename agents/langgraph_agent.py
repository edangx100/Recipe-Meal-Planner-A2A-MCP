"""
LangGraph State Machine for Recipe Planning

This module contains the LangGraph state machine components for the recipe meal planner.
It defines the state, nodes, and workflow for recipe selection and meal planning.

Workflow:
1. Gather dietary preferences from user request using LLM structured output
2. Suggest recipes based on preferences and requested count
3. Check for ingredient overlap across recipes
4. Optimize the grocery list by consolidating ingredients
5. Flag when cost calculation is needed
"""

from typing import TypedDict, Annotated, Sequence, List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver


# Constants
COST_CALCULATION_FLAG = "[CALCULATE_COST]"

# Initialize module-level variables
LANGGRAPH_SETUP_SUCCESS = False
recipe_graph = None

# --- LangGraph State Machine Setup ---
try:
    class RecipePlannerState(TypedDict):
        """State for the recipe planning workflow"""
        messages: Annotated[Sequence[BaseMessage], lambda x, y: x + y]
        dietary_preferences: str
        num_recipes: int
        recipe_suggestions: List[str]
        ingredient_list: List[dict]
        needs_cost_calculation: bool

    def gather_preferences_node(state: RecipePlannerState):
        """Gathers dietary preferences and number of recipes from the user request using LLM structured output"""
        from pydantic import BaseModel
        from google import genai
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from utils import DEFAULT_LLM

        class MealPlanRequest(BaseModel):
            num_recipes: int
            dietary_preferences: list[str]
            budget: float

        last_message = state['messages'][-1]

        if isinstance(last_message, HumanMessage):
            user_input = last_message.content

            # Use LLM with structured output to parse the request
            client = genai.Client()
            prompt = f"""Extract the meal planning requirements from this user request:
"{user_input}"

Identify:
- num_recipes: How many meals/dinners/recipes they want (default: 5)
- dietary_preferences: List any dietary restrictions mentioned (vegetarian, vegan, gluten-free, low-carb, etc.)
- budget: Budget amount in dollars (default: 50.0)
"""

            response_obj = client.models.generate_content(
                model=DEFAULT_LLM,
                contents=prompt,
                config={
                    'response_mime_type': 'application/json',
                    'response_schema': MealPlanRequest
                }
            )

            parsed_request = MealPlanRequest.model_validate_json(response_obj.text)

            pref_str = ", ".join(parsed_request.dietary_preferences) if parsed_request.dietary_preferences else "no specific restrictions"

            response = f"I'll plan {parsed_request.num_recipes} dinners under ${parsed_request.budget:.0f} total. Dietary preferences detected: {pref_str}. Moving to recipe suggestions."
            print(f"DEBUG: gather_preferences_node - {response}")

            return {
                "messages": [AIMessage(content=response)],
                "dietary_preferences": pref_str,
                "num_recipes": parsed_request.num_recipes,
                "needs_cost_calculation": False
            }

        return {"messages": [AIMessage(content="Processing preferences...")]}

    def suggest_recipes_node(state: RecipePlannerState):
        """Suggests dinner recipes based on preferences and requested count"""
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from recipes import all_recipes

        preferences = state.get('dietary_preferences', 'no specific restrictions')
        num_recipes = state.get('num_recipes', 5)

        # Filter recipes based on preferences
        selected_recipes = []
        if 'vegetarian' in preferences or 'vegan' in preferences:
            for recipe_name, recipe_data in all_recipes.items():
                if any(tag in recipe_data['tags'] for tag in ['vegetarian', 'vegan']):
                    selected_recipes.append(recipe_name)
                    if len(selected_recipes) >= num_recipes:
                        break
        else:
            selected_recipes = list(all_recipes.keys())[:num_recipes]

        # Ensure we have the requested number of recipes
        if len(selected_recipes) < num_recipes:
            for recipe_name in all_recipes.keys():
                if recipe_name not in selected_recipes:
                    selected_recipes.append(recipe_name)
                    if len(selected_recipes) >= num_recipes:
                        break

        selected_recipes = selected_recipes[:num_recipes]

        # Collect ingredients
        all_ingredients = []
        for recipe_name in selected_recipes:
            if recipe_name in all_recipes:
                recipe_data = all_recipes[recipe_name]
                all_ingredients.extend(recipe_data['ingredients'])

        recipe_list = "\n".join([f"  {i+1}. {r}" for i, r in enumerate(selected_recipes)])
        response = f"Selected {len(selected_recipes)} recipes:\n{recipe_list}\n\nMoving to ingredient overlap check."

        print(f"DEBUG: suggest_recipes_node - Selected {len(selected_recipes)} recipes")

        return {
            "messages": [AIMessage(content=response)],
            "recipe_suggestions": selected_recipes,
            "ingredient_list": all_ingredients,
            "needs_cost_calculation": False
        }

    def check_ingredient_overlap_node(state: RecipePlannerState):
        """Checks for ingredient overlap to optimize shopping list"""
        ingredients = state.get('ingredient_list', [])

        # Group ingredients by item name
        ingredient_groups = {}
        for ingredient in ingredients:
            item_name = ingredient['item']
            if item_name not in ingredient_groups:
                ingredient_groups[item_name] = []
            ingredient_groups[item_name].append(ingredient)

        # Calculate consolidated quantities
        overlaps = []
        for item_name, item_list in ingredient_groups.items():
            if len(item_list) > 1:
                overlaps.append(f"{item_name} (used in {len(item_list)} recipes)")

        overlap_msg = ""
        if overlaps:
            overlap_msg = f"\n\nIngredient overlap found for: {', '.join(overlaps[:5])}"

        response = f"Checked ingredient overlap across recipes.{overlap_msg}\n\nPreparing to optimize grocery list and calculate costs. {COST_CALCULATION_FLAG}"

        print(f"DEBUG: check_ingredient_overlap_node - Found {len(overlaps)} overlapping ingredients")

        return {
            "messages": [AIMessage(content=response)],
            "needs_cost_calculation": True
        }

    def optimize_grocery_list_node(state: RecipePlannerState):
        """Optimizes the grocery list and requests cost calculation"""
        ingredients = state.get('ingredient_list', [])
        recipes = state.get('recipe_suggestions', [])

        # Consolidate ingredients
        ingredient_groups = {}
        for ingredient in ingredients:
            item_name = ingredient['item']
            if item_name not in ingredient_groups:
                ingredient_groups[item_name] = {
                    'quantities': [],
                    'total_price': 0.0,
                    'consolidated_quantity': ''
                }
            ingredient_groups[item_name]['quantities'].append(ingredient['quantity'])
            ingredient_groups[item_name]['total_price'] += ingredient.get('price', 0.0)

        # Build shopping list summary
        shopping_list = []
        for item_name, data in ingredient_groups.items():
            qty = data['quantities'][0] if len(data['quantities']) == 1 else f"{len(data['quantities'])}x portions"
            shopping_list.append(f"{item_name}: {qty}")

        shopping_summary = "\n".join([f"  - {item}" for item in shopping_list[:10]])

        # Include all selected recipes in the response
        recipe_list = "\n".join([f"  {i+1}. {r}" for i, r in enumerate(recipes)])
        response = f"Selected {len(recipes)} recipes:\n{recipe_list}\n\nOptimized grocery list ready:\n{shopping_summary}\n\nRequesting cost calculation from code agent. {COST_CALCULATION_FLAG}"

        print(f"DEBUG: optimize_grocery_list_node - Created shopping list with {len(ingredient_groups)} items")

        return {
            "messages": [AIMessage(content=response)],
            "needs_cost_calculation": True
        }

    def should_calculate_cost(state: RecipePlannerState):
        """Routing function to determine if cost calculation is needed"""
        if state['messages'] and isinstance(state['messages'][-1], AIMessage):
            last_ai_content = state['messages'][-1].content
            print(f"DEBUG: should_calculate_cost checking: '{last_ai_content[:100]}...'")
            if COST_CALCULATION_FLAG in last_ai_content:
                print("DEBUG: should_calculate_cost -> routing to END (cost calculation needed)")
                return END
        print("DEBUG: should_calculate_cost -> continuing workflow")
        return "suggest_recipes"

    def build_recipe_graph():
        """Builds and compiles the LangGraph state machine for recipe planning"""
        # Build the LangGraph state machine
        builder = StateGraph(RecipePlannerState)

        # Add nodes
        builder.add_node("gather_preferences", gather_preferences_node)
        builder.add_node("suggest_recipes", suggest_recipes_node)
        builder.add_node("check_overlap", check_ingredient_overlap_node)
        builder.add_node("optimize_list", optimize_grocery_list_node)

        # Define edges
        builder.set_entry_point("gather_preferences")
        builder.add_edge("gather_preferences", "suggest_recipes")
        builder.add_edge("suggest_recipes", "check_overlap")
        builder.add_edge("check_overlap", "optimize_list")

        # Conditional edge from optimize_list
        builder.add_conditional_edges(
            "optimize_list",
            should_calculate_cost,
            {"suggest_recipes": "suggest_recipes", END: END}
        )

        memory = MemorySaver()
        graph = builder.compile(checkpointer=memory)
        print("Recipe planner LangGraph state machine compiled successfully.")
        return graph

    # Build the graph
    recipe_graph = build_recipe_graph()
    LANGGRAPH_SETUP_SUCCESS = True

except ImportError as e:
    print(f"LangGraph or LangChain components not found: {e}")
    print("Install with: pip install langgraph langchain_core")
    LANGGRAPH_SETUP_SUCCESS = False
    recipe_graph = None
except Exception as e:
    print(f"Error during LangGraph setup: {e}")
    LANGGRAPH_SETUP_SUCCESS = False
    recipe_graph = None


def get_recipe_graph():
    """Returns the compiled recipe planning graph"""
    return recipe_graph


def is_langgraph_available():
    """Returns whether LangGraph setup was successful"""
    return LANGGRAPH_SETUP_SUCCESS
