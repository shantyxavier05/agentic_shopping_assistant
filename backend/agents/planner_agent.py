"""
Planner Agent: Suggests recipes based on available ingredients
"""
import logging
import sys
import os
from typing import Dict, List, Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.db_helper import DatabaseHelper
from backend.llm.llm_client import LLMClient

logger = logging.getLogger(__name__)


class PlannerAgent:
    """Agent that suggests recipes based on inventory"""
    
    def __init__(self, db_helper: DatabaseHelper):
        self.db_helper = db_helper
        self.llm_client = LLMClient()
        self.recipe_cache: Dict[str, Dict] = {}
    
    def suggest_recipe(self, preferences: Optional[str] = None, servings: int = 4) -> Dict:
        """
        Suggest a recipe based on available ingredients
        
        Args:
            preferences: Optional dietary preferences or restrictions
            servings: Number of servings
            
        Returns:
            Dictionary containing recipe details
        """
        try:
            # Get current inventory
            inventory = self.db_helper.get_all_inventory()
            
            if not inventory:
                return {
                    "name": "No ingredients available",
                    "description": "Please add some ingredients to your inventory first.",
                    "ingredients": [],
                    "instructions": []
                }
            
            # Format inventory for LLM
            ingredients_text = "\n".join([
                f"- {item['name']}: {item['quantity']} {item['unit']}"
                for item in inventory
            ])
            
            # Generate recipe using LLM
            prompt = f"""Based on the following available ingredients, suggest a recipe.
            
Available ingredients:
{ingredients_text}

Preferences: {preferences if preferences else "None"}
Servings: {servings}

Please provide:
1. Recipe name
2. Brief description
3. List of required ingredients with quantities
4. Step-by-step cooking instructions

Format your response as JSON with the following structure:
{{
    "name": "Recipe Name",
    "description": "Brief description",
    "servings": {servings},
    "ingredients": [
        {{"name": "ingredient", "quantity": 2, "unit": "cups"}}
    ],
    "instructions": ["step 1", "step 2"]
}}"""
            
            recipe = self.llm_client.generate_recipe(prompt)
            
            # Cache the recipe for potential application
            self.recipe_cache[recipe.get("name", "Unknown Recipe")] = recipe
            
            logger.info(f"Generated recipe: {recipe.get('name', 'Unknown')}")
            return recipe
            
        except Exception as e:
            logger.error(f"Error suggesting recipe: {str(e)}")
            # Return a default recipe on error
            return {
                "name": "Error generating recipe",
                "description": f"Unable to generate recipe: {str(e)}",
                "ingredients": [],
                "instructions": []
            }
    
    def apply_recipe(self, recipe_name: str) -> Dict:
        """
        Apply a recipe (remove ingredients from inventory)
        
        Args:
            recipe_name: Name of the recipe to apply
            
        Returns:
            Dictionary with result of applying recipe
        """
        try:
            if recipe_name not in self.recipe_cache:
                return {
                    "success": False,
                    "message": "Recipe not found. Please generate a recipe first."
                }
            
            recipe = self.recipe_cache[recipe_name]
            used_items = []
            
            # Remove ingredients from inventory
            for ingredient in recipe.get("ingredients", []):
                try:
                    self.db_helper.reduce_quantity(
                        ingredient["name"],
                        ingredient.get("quantity", 0)
                    )
                    used_items.append(ingredient["name"])
                except Exception as e:
                    logger.warning(f"Could not remove {ingredient['name']}: {str(e)}")
            
            logger.info(f"Applied recipe: {recipe_name}, used items: {used_items}")
            return {
                "success": True,
                "message": f"Recipe '{recipe_name}' applied successfully",
                "used_items": used_items
            }
            
        except Exception as e:
            logger.error(f"Error applying recipe: {str(e)}")
            return {
                "success": False,
                "message": f"Error applying recipe: {str(e)}"
            }

