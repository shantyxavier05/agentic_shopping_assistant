"""
Recipe Application Agent: Handles applying recipes with scaling based on servings
"""
import logging
import sys
import os
from typing import Dict, List, Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.db_helper import DatabaseHelper
from backend.utils.unit_converter import UnitConverter

logger = logging.getLogger(__name__)


class RecipeApplicationAgent:
    """Agent that applies recipes and scales ingredients based on number of servings"""
    
    def __init__(self, db_helper: DatabaseHelper):
        self.db_helper = db_helper
        self.unit_converter = UnitConverter()
    
    def apply_recipe(
        self, 
        recipe: Dict, 
        servings: Optional[int] = None,
        original_servings: Optional[int] = None
    ) -> Dict:
        """
        Apply a recipe by removing scaled ingredients from inventory
        
        Args:
            recipe: Recipe dictionary with ingredients
            servings: Number of people to cook for (if None, uses recipe's servings)
            original_servings: Original servings the recipe was designed for
            
        Returns:
            Dictionary with result of applying recipe
        """
        try:
            # Determine target servings
            if servings is None:
                servings = recipe.get('servings', 4)
            
            # Determine original servings (from recipe or parameter)
            if original_servings is None:
                original_servings = recipe.get('servings', 4)
            
            # Calculate scaling factor
            if original_servings == 0:
                scaling_factor = 1.0
            else:
                scaling_factor = servings / original_servings
            
            logger.info(f"Applying recipe '{recipe.get('name', 'Unknown')}' for {servings} people "
                       f"(scaling from {original_servings} servings, factor: {scaling_factor:.2f})")
            
            ingredients = recipe.get('ingredients', [])
            used_items = []
            failed_items = []
            
            # Process each ingredient
            for ingredient in ingredients:
                ingredient_name = ingredient.get('name', '')
                original_quantity = ingredient.get('quantity', 0)
                unit = ingredient.get('unit', 'units')
                
                # Scale the quantity
                scaled_quantity = original_quantity * scaling_factor
                
                # Standardize unit
                standardized_qty, standardized_unit = self.unit_converter.standardize_quantity(
                    scaled_quantity, unit
                )
                
                try:
                    # Check if item exists in inventory
                    existing_item = self.db_helper.get_item(ingredient_name)
                    
                    if not existing_item:
                        logger.warning(f"Ingredient '{ingredient_name}' not found in inventory")
                        failed_items.append({
                            'name': ingredient_name,
                            'reason': 'not_in_inventory',
                            'required': f"{scaled_quantity:.2f} {unit}"
                        })
                        continue
                    
                    # Check if enough quantity available
                    available_qty = existing_item['quantity']
                    available_unit = existing_item['unit']
                    
                    # For now, we'll reduce by the scaled quantity
                    # In a more sophisticated system, you'd convert units first
                    if available_qty >= scaled_quantity:
                        self.db_helper.reduce_quantity(ingredient_name, scaled_quantity)
                        used_items.append({
                            'name': ingredient_name,
                            'used': scaled_quantity,
                            'unit': unit,
                            'remaining': available_qty - scaled_quantity
                        })
                        logger.info(f"Used {scaled_quantity} {unit} of {ingredient_name}")
                    else:
                        # Not enough available
                        logger.warning(f"Insufficient {ingredient_name}: need {scaled_quantity}, have {available_qty}")
                        failed_items.append({
                            'name': ingredient_name,
                            'reason': 'insufficient_quantity',
                            'required': f"{scaled_quantity:.2f} {unit}",
                            'available': f"{available_qty} {available_unit}"
                        })
                        # Still remove what's available
                        if available_qty > 0:
                            self.db_helper.reduce_quantity(ingredient_name, available_qty)
                            used_items.append({
                                'name': ingredient_name,
                                'used': available_qty,
                                'unit': available_unit,
                                'remaining': 0,
                                'note': 'partial'
                            })
                
                except Exception as e:
                    logger.error(f"Error processing ingredient {ingredient_name}: {str(e)}")
                    failed_items.append({
                        'name': ingredient_name,
                        'reason': 'error',
                        'error': str(e)
                    })
            
            # Build response
            success = len(failed_items) == 0
            message = f"Recipe '{recipe.get('name', 'Unknown')}' applied for {servings} people"
            
            if failed_items:
                message += f" (with {len(failed_items)} issues)"
            
            return {
                'success': success,
                'message': message,
                'recipe_name': recipe.get('name', 'Unknown'),
                'servings': servings,
                'scaling_factor': scaling_factor,
                'used_items': used_items,
                'failed_items': failed_items,
                'total_ingredients': len(ingredients),
                'successful_ingredients': len(used_items)
            }
            
        except Exception as e:
            logger.error(f"Error applying recipe: {str(e)}")
            return {
                'success': False,
                'message': f"Error applying recipe: {str(e)}",
                'error': str(e)
            }



