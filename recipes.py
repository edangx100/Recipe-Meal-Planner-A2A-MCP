"""
Recipe Database

This module contains the recipe database with ingredients and dietary tags.
Each recipe includes a list of ingredients with quantities and prices, along with dietary tags.
"""

all_recipes = {
    'Spaghetti Aglio e Olio': {
        'ingredients': [
            {'item': 'spaghetti', 'quantity': '1 lb', 'price': 1.50},
            {'item': 'garlic', 'quantity': '1 bulb', 'price': 0.75},
            {'item': 'olive oil', 'quantity': '1/2 cup', 'price': 2.00},
            {'item': 'red pepper flakes', 'quantity': '1 tsp', 'price': 0.25}
        ],
        'tags': ['vegetarian', 'vegan']
    },
    'Chicken Stir-Fry': {
        'ingredients': [
            {'item': 'chicken breast', 'quantity': '1 lb', 'price': 4.99},
            {'item': 'mixed vegetables', 'quantity': '2 cups', 'price': 2.50},
            {'item': 'soy sauce', 'quantity': '3 tbsp', 'price': 0.50},
            {'item': 'rice', 'quantity': '2 cups', 'price': 1.00}
        ],
        'tags': ['gluten-free']
    },
    'Black Bean Tacos': {
        'ingredients': [
            {'item': 'black beans', 'quantity': '2 cans', 'price': 2.00},
            {'item': 'corn tortillas', 'quantity': '12 count', 'price': 2.50},
            {'item': 'avocado', 'quantity': '2 count', 'price': 3.00},
            {'item': 'salsa', 'quantity': '1 jar', 'price': 2.50}
        ],
        'tags': ['vegetarian', 'vegan', 'gluten-free']
    },
    'Lentil Soup': {
        'ingredients': [
            {'item': 'lentils', 'quantity': '1 lb', 'price': 2.00},
            {'item': 'carrots', 'quantity': '4 count', 'price': 1.50},
            {'item': 'celery', 'quantity': '3 stalks', 'price': 1.00},
            {'item': 'vegetable broth', 'quantity': '4 cups', 'price': 2.00}
        ],
        'tags': ['vegetarian', 'vegan', 'gluten-free']
    },
    'Baked Salmon with Veggies': {
        'ingredients': [
            {'item': 'salmon fillet', 'quantity': '1 lb', 'price': 7.99},
            {'item': 'broccoli', 'quantity': '1 lb', 'price': 2.00},
            {'item': 'lemon', 'quantity': '1 count', 'price': 0.50},
            {'item': 'olive oil', 'quantity': '2 tbsp', 'price': 0.50}
        ],
        'tags': ['gluten-free', 'low-carb']
    },
    'Veggie Fried Rice': {
        'ingredients': [
            {'item': 'rice', 'quantity': '2 cups', 'price': 1.00},
            {'item': 'mixed vegetables', 'quantity': '2 cups', 'price': 2.50},
            {'item': 'eggs', 'quantity': '3 count', 'price': 1.00},
            {'item': 'soy sauce', 'quantity': '3 tbsp', 'price': 0.50}
        ],
        'tags': ['vegetarian']
    },
    'Margherita Pizza': {
        'ingredients': [
            {'item': 'pizza dough', 'quantity': '1 lb', 'price': 2.00},
            {'item': 'mozzarella cheese', 'quantity': '8 oz', 'price': 3.50},
            {'item': 'tomato sauce', 'quantity': '1 cup', 'price': 1.50},
            {'item': 'fresh basil', 'quantity': '1 bunch', 'price': 2.00}
        ],
        'tags': ['vegetarian']
    },
    'Greek Salad': {
        'ingredients': [
            {'item': 'romaine lettuce', 'quantity': '1 head', 'price': 1.50},
            {'item': 'feta cheese', 'quantity': '6 oz', 'price': 3.00},
            {'item': 'cucumber', 'quantity': '2 count', 'price': 1.50},
            {'item': 'cherry tomatoes', 'quantity': '1 pint', 'price': 2.50},
            {'item': 'olives', 'quantity': '1/2 cup', 'price': 2.00},
            {'item': 'olive oil', 'quantity': '3 tbsp', 'price': 0.75}
        ],
        'tags': ['vegetarian', 'gluten-free', 'low-carb']
    },
    'Beef Chili': {
        'ingredients': [
            {'item': 'ground beef', 'quantity': '1 lb', 'price': 5.99},
            {'item': 'kidney beans', 'quantity': '2 cans', 'price': 2.00},
            {'item': 'diced tomatoes', 'quantity': '1 can', 'price': 1.50},
            {'item': 'onion', 'quantity': '1 count', 'price': 0.75},
            {'item': 'chili powder', 'quantity': '2 tbsp', 'price': 0.50}
        ],
        'tags': ['gluten-free']
    },
    'Mushroom Risotto': {
        'ingredients': [
            {'item': 'arborio rice', 'quantity': '1.5 cups', 'price': 3.00},
            {'item': 'mushrooms', 'quantity': '1 lb', 'price': 3.50},
            {'item': 'vegetable broth', 'quantity': '6 cups', 'price': 3.00},
            {'item': 'parmesan cheese', 'quantity': '1/2 cup', 'price': 2.50},
            {'item': 'white wine', 'quantity': '1/2 cup', 'price': 2.00},
            {'item': 'butter', 'quantity': '3 tbsp', 'price': 1.00}
        ],
        'tags': ['vegetarian', 'gluten-free']
    }
}
