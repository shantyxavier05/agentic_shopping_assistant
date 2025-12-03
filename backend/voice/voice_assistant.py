"""
Voice Assistant: Processes voice commands and provides responses
Uses tokenization and synonym matching for better natural language understanding
"""
import logging
import re
import sys
import os
from typing import Dict, Optional, List, Tuple

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.db_helper import DatabaseHelper
from backend.agents.planner_agent import PlannerAgent
from backend.agents.inventory_agent import InventoryAgent
from backend.agents.shopping_agent import ShoppingAgent
from backend.utils.unit_converter import UnitConverter

logger = logging.getLogger(__name__)


class VoiceAssistant:
    """Voice assistant for processing natural language commands with tokenization and synonym matching"""
    
    # Synonym dictionaries for action words
    ADD_SYNONYMS = {
        'add', 'insert', 'include', 'put', 'place', 'store', 'keep', 
        'save', 'enter', 'register', 'record', 'append', 'deposit'
    }
    
    REMOVE_SYNONYMS = {
        'remove', 'delete', 'take', 'exclude', 'eliminate', 'drop', 
        'discard', 'withdraw', 'extract', 'pull', 'clear', 'erase'
    }
    
    UPDATE_SYNONYMS = {
        'update', 'change', 'modify', 'set', 'adjust', 'alter', 
        'edit', 'revise', 'amend', 'correct'
    }
    
    RECIPE_SYNONYMS = {
        'suggest', 'recommend', 'recipe', 'cook', 'make', 'prepare',
        'dish', 'meal', 'food', 'what can', 'what to make'
    }
    
    SHOPPING_SYNONYMS = {
        'shopping', 'buy', 'purchase', 'need', 'list', 'grocery',
        'shop', 'market', 'store', 'what to buy'
    }
    
    INVENTORY_SYNONYMS = {
        'inventory', 'ingredients', 'stock', 'items', 'have', 'what',
        'show', 'list', 'display', 'current'
    }
    
    # Common units
    UNITS = {
        'cup', 'cups', 'cupful', 'cupfuls',
        'tablespoon', 'tablespoons', 'tbsp', 'tbsps',
        'teaspoon', 'teaspoons', 'tsp', 'tsps',
        'liter', 'liters', 'l', 'litre', 'litres',
        'milliliter', 'milliliters', 'ml', 'mls',
        'gram', 'grams', 'g', 'gs',
        'kilogram', 'kilograms', 'kg', 'kgs',
        'ounce', 'ounces', 'oz', 'ozs',
        'pound', 'pounds', 'lb', 'lbs',
        'piece', 'pieces', 'pc', 'pcs',
        'item', 'items',
        'unit', 'units',
        'bottle', 'bottles',
        'can', 'cans',
        'pack', 'packs', 'package', 'packages',
        'head', 'heads',
        'clove', 'cloves',
        'loaf', 'loaves',
        'bag', 'bags',
        'box', 'boxes'
    }
    
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
        self.unit_converter = UnitConverter()
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into words, handling punctuation"""
        # Remove punctuation and split into words
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        tokens = text.split()
        return tokens
    
    def find_synonym_match(self, word: str, synonym_set: set) -> bool:
        """Check if word matches any synonym in the set"""
        word_lower = word.lower()
        # Direct match
        if word_lower in synonym_set:
            return True
        # Check if word contains any synonym
        for synonym in synonym_set:
            if synonym in word_lower or word_lower in synonym:
                return True
        return False
    
    def word_to_number(self, word: str) -> Optional[float]:
        """Convert word numbers to numeric values"""
        word_lower = word.lower().strip()
        word_numbers = {
            'one': 1.0, 'two': 2.0, 'three': 3.0, 'four': 4.0, 'five': 5.0,
            'six': 6.0, 'seven': 7.0, 'eight': 8.0, 'nine': 9.0, 'ten': 10.0,
            'eleven': 11.0, 'twelve': 12.0, 'thirteen': 13.0, 'fourteen': 14.0,
            'fifteen': 15.0, 'sixteen': 16.0, 'seventeen': 17.0, 'eighteen': 18.0,
            'nineteen': 19.0, 'twenty': 20.0, 'thirty': 30.0, 'forty': 40.0,
            'fifty': 50.0, 'sixty': 60.0, 'seventy': 70.0, 'eighty': 80.0,
            'ninety': 90.0, 'hundred': 100.0
        }
        return word_numbers.get(word_lower)
    
    def extract_quantity_and_unit(self, tokens: List[str], start_idx: int) -> Tuple[Optional[float], Optional[str], int]:
        """Extract quantity and unit from tokens starting at start_idx"""
        quantity = None
        unit = None
        consumed = 0
        
        # Look for number (numeric or word)
        if start_idx < len(tokens):
            # Try numeric first
            try:
                quantity = float(tokens[start_idx])
                consumed = 1
            except ValueError:
                # Try word number
                word_qty = self.word_to_number(tokens[start_idx])
                if word_qty is not None:
                    quantity = word_qty
                    consumed = 1
            
            # If we found a quantity, look for unit
            if quantity is not None and start_idx + consumed < len(tokens):
                next_token = tokens[start_idx + consumed]
                
                # Handle "full" before unit (e.g., "one cup full of milk")
                if next_token == 'full' and start_idx + consumed + 1 < len(tokens):
                    if tokens[start_idx + consumed + 1] in self.UNITS:
                        unit = tokens[start_idx + consumed + 1]
                        consumed += 2  # Skip "full" and unit
                    elif start_idx + consumed + 2 < len(tokens) and tokens[start_idx + consumed + 2] in self.UNITS:
                        # "one full cup of milk"
                        unit = tokens[start_idx + consumed + 2]
                        consumed += 3
                # Check if next token is a unit
                elif next_token in self.UNITS:
                    unit = next_token
                    consumed += 1
                
                # Check if there's "of" after the unit (e.g., "1 liter of milk")
                if start_idx + consumed < len(tokens) and tokens[start_idx + consumed] == 'of':
                    consumed += 1  # Skip "of"
        
        return quantity, unit, consumed
    
    def find_item_name(self, tokens: List[str], skip_indices: set) -> Optional[str]:
        """Extract item name from tokens, skipping quantity/unit/action words"""
        item_words = []
        
        for i, token in enumerate(tokens):
            if i in skip_indices:
                continue
            # Skip action words, prepositions, units, and common words
            if (token in self.ADD_SYNONYMS or 
                token in self.REMOVE_SYNONYMS or 
                token in self.UPDATE_SYNONYMS or
                token in self.UNITS or  # Skip all unit words
                token in ['to', 'from', 'in', 'the', 'a', 'an', 'my', 'your', 'inventory', 'stock', 'of', 'full']):  # Skip "of" and "full"
                continue
            # Skip word numbers
            word_qty = self.word_to_number(token)
            if word_qty is not None:
                continue
            item_words.append(token)
        
        if item_words:
            return ' '.join(item_words).strip()
        return None
    
    def process_command(self, text: str) -> Dict:
        """
        Process a voice/text command using tokenization and synonym matching
        
        Args:
            text: The command text
            
        Returns:
            Dictionary with response text, action, and optional data
        """
        tokens = self.tokenize(text)
        logger.info(f"Tokenized command: {tokens}")
        
        if not tokens:
            return {
                "text": "I didn't understand that command. Please try again.",
                "action": None,
                "data": None
            }
        
        try:
            # Check for action type using synonym matching
            action_type = None
            action_idx = -1
            
            for i, token in enumerate(tokens):
                if self.find_synonym_match(token, self.ADD_SYNONYMS):
                    action_type = 'add'
                    action_idx = i
                    break
                elif self.find_synonym_match(token, self.REMOVE_SYNONYMS):
                    action_type = 'remove'
                    action_idx = i
                    break
                elif self.find_synonym_match(token, self.UPDATE_SYNONYMS):
                    action_type = 'update'
                    action_idx = i
                    break
                elif self.find_synonym_match(token, self.RECIPE_SYNONYMS):
                    action_type = 'recipe'
                    break
                elif self.find_synonym_match(token, self.SHOPPING_SYNONYMS):
                    action_type = 'shopping'
                    break
                elif self.find_synonym_match(token, self.INVENTORY_SYNONYMS):
                    action_type = 'inventory'
                    break
            
            # Route to appropriate handler
            if action_type == 'add':
                return self._handle_add_item_improved(tokens, action_idx)
            elif action_type == 'remove':
                return self._handle_remove_item_improved(tokens, action_idx)
            elif action_type == 'update':
                return self._handle_update_quantity_improved(tokens)
            elif action_type == 'recipe':
                return self._handle_suggest_recipe(text)
            elif action_type == 'shopping':
                return self._handle_shopping_list()
            elif action_type == 'inventory':
                return self._handle_get_inventory()
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
    
    def _handle_add_item_improved(self, tokens: List[str], action_idx: int) -> Dict:
        """Handle add item command with improved tokenization and unit standardization"""
        skip_indices = {action_idx}
        
        # Try to extract quantity and unit
        quantity, unit, consumed = self.extract_quantity_and_unit(tokens, action_idx + 1)
        if quantity is not None:
            for i in range(action_idx + 1, action_idx + 1 + consumed):
                skip_indices.add(i)
            # Standardize unit
            standardized_qty, standardized_unit = self.unit_converter.standardize_quantity(quantity, unit or "units")
            quantity = standardized_qty
            unit = standardized_unit
        else:
            quantity = 1.0
            unit = "units"
        
        # Extract item name
        item_name = self.find_item_name(tokens, skip_indices)
        
        if not item_name:
            return {
                "text": "I couldn't identify what item to add. Please say something like 'add milk' or 'insert 2 cups of flour'.",
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
    
    def _handle_remove_item_improved(self, tokens: List[str], action_idx: int) -> Dict:
        """Handle remove item command with improved tokenization and unit conversion"""
        skip_indices = {action_idx}
        
        # Try to extract quantity and unit
        quantity, unit, consumed = self.extract_quantity_and_unit(tokens, action_idx + 1)
        if quantity is not None:
            for i in range(action_idx + 1, action_idx + 1 + consumed):
                skip_indices.add(i)
        else:
            quantity = None
            unit = None
            # Even if quantity extraction failed, check if next token is a unit and skip it
            if action_idx + 1 < len(tokens) and tokens[action_idx + 1] in self.UNITS:
                skip_indices.add(action_idx + 1)
        
        # Extract item name
        item_name = self.find_item_name(tokens, skip_indices)
        
        if not item_name:
            return {
                "text": "I couldn't identify what item to remove. Please say something like 'remove milk' or 'delete 2 cups of flour'.",
                "action": None,
                "data": None
            }
        
        try:
            # Use remove_item_with_unit to handle unit conversion
            item = self.inventory_agent.remove_item_with_unit(item_name, quantity, unit)
            
            if item.get("removed"):
                return {
                    "text": f"Removed {item_name} from your inventory.",
                    "action": "inventory_updated",
                    "data": item
                }
            else:
                removed_text = f"{quantity} {unit}" if quantity and unit else "some"
                return {
                    "text": f"Removed {removed_text} of {item_name}. Remaining: {item['quantity']} {item['unit']}.",
                    "action": "inventory_updated",
                    "data": item
                }
        except ValueError as e:
            # Handle insufficient quantity error
            return {
                "text": str(e),
                "action": None,
                "data": None
            }
        except Exception as e:
            return {
                "text": f"Sorry, I couldn't remove {item_name}: {str(e)}",
                "action": None,
                "data": None
            }
    
    def _handle_update_quantity_improved(self, tokens: List[str]) -> Dict:
        """Handle update quantity command with improved tokenization"""
        # Look for pattern: update [item] quantity to [number]
        # or: change [item] to [number] [unit]
        
        item_name = None
        quantity = None
        unit = "units"
        
        # Find "to" keyword which usually precedes the new quantity
        to_idx = -1
        for i, token in enumerate(tokens):
            if token == 'to':
                to_idx = i
                break
        
        if to_idx > 0:
            # Extract item name before "to"
            item_words = []
            for i in range(len(tokens)):
                if i >= to_idx:
                    break
                token = tokens[i]
                if (token not in self.UPDATE_SYNONYMS and 
                    token not in ['quantity', 'amount', 'the', 'a', 'an']):
                    item_words.append(token)
            item_name = ' '.join(item_words).strip() if item_words else None
            
            # Extract quantity and unit after "to"
            if to_idx + 1 < len(tokens):
                qty, unit_found, _ = self.extract_quantity_and_unit(tokens, to_idx + 1)
                if qty is not None:
                    quantity = qty
                    if unit_found:
                        unit = unit_found
        
        if not item_name or quantity is None:
            return {
                "text": "I couldn't understand the quantity update. Please say something like 'update milk quantity to 5' or 'change flour to 2 cups'.",
                "action": None,
                "data": None
            }
        
        try:
            # Standardize unit
            standardized_qty, standardized_unit = self.unit_converter.standardize_quantity(quantity, unit)
            item = self.inventory_agent.update_quantity(item_name, standardized_qty, standardized_unit)
            return {
                "text": f"Updated {item_name} quantity to {standardized_qty} {item['unit']}.",
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
