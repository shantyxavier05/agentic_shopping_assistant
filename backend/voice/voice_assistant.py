"""
Voice Assistant: Processes voice commands and provides responses
"""
import logging
import re
import sys
import os
from typing import Dict, Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.db_helper import DatabaseHelper
from backend.agents.planner_agent import PlannerAgent
from backend.agents.inventory_agent import InventoryAgent
from backend.agents.shopping_agent import ShoppingAgent

logger = logging.getLogger(__name__)


class VoiceAssistant:
    """Voice assistant for processing natural language commands"""
    
    def __init__(
        self,
        db_helper: DatabaseHelper,
        planner_agent: PlannerAgent,
        inventory_agent: InventoryAgent,
        shopping_agent: ShoppingAgent
    ):
        self.db_helper = db_helper
        self.planner_agent = planner_agent
        self.inventory_agent = inventory_agent
        self.shopping_agent = shopping_agent
    
    def process_command(self, text: str) -> Dict:
        """
        Process a voice/text command and return response
        
        Args:
            text: The command text
            
        Returns:
            Dictionary with response text, action, and optional data
        """
        text_lower = text.lower().strip()
        
        try:
            # Add item to inventory
            if re.search(r'add|put|insert', text_lower) and re.search(r'inventory|stock', text_lower):
                return self._handle_add_item(text)
            
            # Remove item from inventory
            elif re.search(r'remove|delete|take out', text_lower) and re.search(r'inventory|stock', text_lower):
                return self._handle_remove_item(text)
            
            # Update quantity
            elif re.search(r'update|change|set|modify', text_lower) and re.search(r'quantity|amount', text_lower):
                return self._handle_update_quantity(text)
            
            # Suggest recipe
            elif re.search(r'suggest|recommend|recipe|what.*can.*cook|what.*make', text_lower):
                return self._handle_suggest_recipe(text)
            
            # Get shopping list
            elif re.search(r'shopping.*list|what.*need.*buy|buy|purchase', text_lower):
                return self._handle_shopping_list()
            
            # Get inventory
            elif re.search(r'inventory|ingredients|what.*have|stock', text_lower):
                return self._handle_get_inventory()
            
            # Default response
            else:
                return {
                    "text": "I didn't understand that command. You can ask me to add items, remove items, suggest recipes, or show your shopping list.",
                    "action": None,
                    "data": None
                }
                
        except Exception as e:
            logger.error(f"Error processing command: {str(e)}")
            return {
                "text": f"Sorry, I encountered an error: {str(e)}",
                "action": None,
                "data": None
            }
    
    def _handle_add_item(self, text: str) -> Dict:
        """Handle add item command"""
        # Extract item name and quantity using regex
        # Patterns: "add 2 cups of flour" or "add flour to inventory"
        patterns = [
            r'add\s+(\d+\.?\d*)\s+(\w+)?\s+(?:of\s+)?([a-zA-Z\s]+?)(?:\s+to\s+inventory|$)',
            r'add\s+([a-zA-Z\s]+?)(?:\s+to\s+inventory|$)',
        ]
        
        item_name = None
        quantity = 1.0
        unit = "units"
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                if len(match.groups()) >= 3:
                    quantity = float(match.group(1))
                    unit = match.group(2) or "units"
                    item_name = match.group(3).strip()
                elif len(match.groups()) >= 1:
                    item_name = match.group(1).strip()
                break
        
        if not item_name:
            return {
                "text": "I couldn't identify what item to add. Please say something like 'add 2 cups of flour'.",
                "action": None,
                "data": None
            }
        
        try:
            item = self.inventory_agent.add_item(item_name, quantity, unit)
            return {
                "text": f"Added {quantity} {unit} of {item_name} to your inventory.",
                "action": "inventory_updated",
                "data": item
            }
        except Exception as e:
            return {
                "text": f"Sorry, I couldn't add {item_name}: {str(e)}",
                "action": None,
                "data": None
            }
    
    def _handle_remove_item(self, text: str) -> Dict:
        """Handle remove item command"""
        patterns = [
            r'remove\s+(\d+\.?\d*)\s+(\w+)?\s+(?:of\s+)?([a-zA-Z\s]+?)(?:\s+from\s+inventory|$)',
            r'remove\s+([a-zA-Z\s]+?)(?:\s+from\s+inventory|$)',
        ]
        
        item_name = None
        quantity = None
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                if len(match.groups()) >= 3:
                    quantity = float(match.group(1))
                    item_name = match.group(3).strip()
                elif len(match.groups()) >= 1:
                    item_name = match.group(1).strip()
                break
        
        if not item_name:
            return {
                "text": "I couldn't identify what item to remove. Please say something like 'remove flour' or 'remove 2 cups of flour'.",
                "action": None,
                "data": None
            }
        
        try:
            item = self.inventory_agent.remove_item(item_name, quantity)
            if item.get("removed"):
                return {
                    "text": f"Removed {item_name} from your inventory.",
                    "action": "inventory_updated",
                    "data": item
                }
            else:
                return {
                    "text": f"Removed {quantity or 'some'} of {item_name}. Remaining: {item['quantity']} {item['unit']}.",
                    "action": "inventory_updated",
                    "data": item
                }
        except Exception as e:
            return {
                "text": f"Sorry, I couldn't remove {item_name}: {str(e)}",
                "action": None,
                "data": None
            }
    
    def _handle_update_quantity(self, text: str) -> Dict:
        """Handle update quantity command"""
        match = re.search(r'update\s+([a-zA-Z\s]+?)\s+quantity\s+to\s+(\d+\.?\d*)', text.lower())
        
        if not match:
            return {
                "text": "I couldn't understand the quantity update. Please say something like 'update flour quantity to 5'.",
                "action": None,
                "data": None
            }
        
        item_name = match.group(1).strip()
        quantity = float(match.group(2))
        
        try:
            item = self.inventory_agent.update_quantity(item_name, quantity)
            return {
                "text": f"Updated {item_name} quantity to {quantity} {item['unit']}.",
                "action": "inventory_updated",
                "data": item
            }
        except Exception as e:
            return {
                "text": f"Sorry, I couldn't update {item_name}: {str(e)}",
                "action": None,
                "data": None
            }
    
    def _handle_suggest_recipe(self, text: str) -> Dict:
        """Handle recipe suggestion command"""
        try:
            recipe = self.planner_agent.suggest_recipe()
            recipe_text = f"I suggest making {recipe['name']}. {recipe['description']} "
            recipe_text += f"It serves {recipe.get('servings', 4)} people. "
            ingredients_list = [f"{ing['quantity']} {ing.get('unit', 'units')} of {ing['name']}" for ing in recipe.get('ingredients', [])]
            recipe_text += f"You'll need: {', '.join(ingredients_list)}."
            
            return {
                "text": recipe_text,
                "action": "recipe_suggested",
                "data": recipe
            }
        except Exception as e:
            return {
                "text": f"Sorry, I couldn't suggest a recipe: {str(e)}",
                "action": None,
                "data": None
            }
    
    def _handle_shopping_list(self) -> Dict:
        """Handle shopping list request"""
        try:
            shopping_list = self.shopping_agent.generate_shopping_list()
            
            if not shopping_list:
                return {
                    "text": "Great! You have all the items you need. Your inventory looks good.",
                    "action": "shopping_list",
                    "data": shopping_list
                }
            
            items_text = ", ".join([
                f"{item['name']} (need {item['suggested_quantity']} {item['unit']})"
                for item in shopping_list[:5]  # Limit to 5 items for voice response
            ])
            
            if len(shopping_list) > 5:
                items_text += f", and {len(shopping_list) - 5} more items"
            
            return {
                "text": f"Here's your shopping list: {items_text}.",
                "action": "shopping_list",
                "data": shopping_list
            }
        except Exception as e:
            return {
                "text": f"Sorry, I couldn't generate your shopping list: {str(e)}",
                "action": None,
                "data": None
            }
    
    def _handle_get_inventory(self) -> Dict:
        """Handle get inventory request"""
        try:
            inventory = self.db_helper.get_all_inventory()
            
            if not inventory:
                return {
                    "text": "Your inventory is empty. You can add items by saying 'add [item] to inventory'.",
                    "action": "inventory_list",
                    "data": inventory
                }
            
            items_text = ", ".join([
                f"{item['quantity']} {item['unit']} of {item['name']}"
                for item in inventory[:5]  # Limit to 5 items for voice response
            ])
            
            if len(inventory) > 5:
                items_text += f", and {len(inventory) - 5} more items"
            
            return {
                "text": f"You have: {items_text}.",
                "action": "inventory_list",
                "data": inventory
            }
        except Exception as e:
            return {
                "text": f"Sorry, I couldn't get your inventory: {str(e)}",
                "action": None,
                "data": None
            }

