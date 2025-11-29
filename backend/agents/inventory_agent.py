"""
Inventory Agent: Manages inventory items in the database
"""
import logging
import sys
import os
from typing import Dict, Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.db_helper import DatabaseHelper

logger = logging.getLogger(__name__)


class InventoryAgent:
    """Agent that manages inventory operations"""
    
    def __init__(self, db_helper: DatabaseHelper):
        self.db_helper = db_helper
    
    def add_item(self, item_name: str, quantity: float, unit: str = "units") -> Dict:
        """
        Add or update an inventory item
        
        Args:
            item_name: Name of the item
            quantity: Quantity to add
            unit: Unit of measurement
            
        Returns:
            Dictionary with item details
        """
        try:
            # Check if item exists
            existing = self.db_helper.get_item(item_name)
            
            if existing:
                # Update quantity
                new_quantity = existing["quantity"] + quantity
                self.db_helper.update_item(item_name, new_quantity, unit)
                logger.info(f"Updated {item_name}: {existing['quantity']} + {quantity} = {new_quantity}")
            else:
                # Add new item
                self.db_helper.add_item(item_name, quantity, unit)
                logger.info(f"Added new item: {item_name} ({quantity} {unit})")
            
            return self.db_helper.get_item(item_name)
            
        except Exception as e:
            logger.error(f"Error adding item {item_name}: {str(e)}")
            raise
    
    def remove_item(self, item_name: str, quantity: Optional[float] = None) -> Dict:
        """
        Remove an item or reduce its quantity
        
        Args:
            item_name: Name of the item
            quantity: Quantity to remove (None = remove all)
            
        Returns:
            Dictionary with remaining item details or None if removed
        """
        try:
            existing = self.db_helper.get_item(item_name)
            
            if not existing:
                raise ValueError(f"Item '{item_name}' not found in inventory")
            
            if quantity is None:
                # Remove item completely
                self.db_helper.delete_item(item_name)
                logger.info(f"Removed item: {item_name}")
                return {"name": item_name, "quantity": 0, "unit": existing["unit"], "removed": True}
            else:
                # Reduce quantity
                new_quantity = max(0, existing["quantity"] - quantity)
                
                if new_quantity == 0:
                    self.db_helper.delete_item(item_name)
                    logger.info(f"Removed item {item_name} (quantity reached 0)")
                    return {"name": item_name, "quantity": 0, "unit": existing["unit"], "removed": True}
                else:
                    self.db_helper.update_item(item_name, new_quantity, existing["unit"])
                    logger.info(f"Reduced {item_name}: {existing['quantity']} - {quantity} = {new_quantity}")
                    return self.db_helper.get_item(item_name)
                    
        except Exception as e:
            logger.error(f"Error removing item {item_name}: {str(e)}")
            raise
    
    def update_quantity(self, item_name: str, quantity: float, unit: str = "units") -> Dict:
        """
        Update item quantity (set to specific value)
        
        Args:
            item_name: Name of the item
            quantity: New quantity
            unit: Unit of measurement
            
        Returns:
            Dictionary with updated item details
        """
        try:
            existing = self.db_helper.get_item(item_name)
            
            if not existing:
                # Add new item if doesn't exist
                self.db_helper.add_item(item_name, quantity, unit)
            else:
                # Update existing item
                self.db_helper.update_item(item_name, quantity, unit)
            
            logger.info(f"Updated {item_name} quantity to {quantity} {unit}")
            return self.db_helper.get_item(item_name)
            
        except Exception as e:
            logger.error(f"Error updating quantity for {item_name}: {str(e)}")
            raise

