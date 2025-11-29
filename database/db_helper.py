"""
Database helper for SQLite operations
"""
import sqlite3
import logging
import os
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class DatabaseHelper:
    """Helper class for database operations"""
    
    def __init__(self, db_path: Optional[str] = None):
        # Default path relative to project root
        if db_path is None:
            # Try to find database directory from current working directory
            if os.path.exists("database"):
                db_path = os.path.join("database", "inventory.db")
            elif os.path.exists("../database"):
                db_path = os.path.join("..", "database", "inventory.db")
            else:
                # Create database directory in current location
                db_path = os.path.join("database", "inventory.db")
        
        # Ensure database directory exists
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        # Use absolute path
        self.db_path = os.path.abspath(db_path)
        self._init_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    
    def _init_database(self):
        """Initialize database schema if not exists"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Create inventory table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS inventory (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        quantity REAL NOT NULL,
                        unit TEXT NOT NULL DEFAULT 'units',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def add_item(self, name: str, quantity: float, unit: str = "units") -> None:
        """Add a new item to inventory"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO inventory (name, quantity, unit)
                    VALUES (?, ?, ?)
                """, (name, quantity, unit))
                conn.commit()
                logger.info(f"Added item: {name}")
        except sqlite3.IntegrityError:
            raise ValueError(f"Item '{name}' already exists. Use update_item instead.")
        except Exception as e:
            logger.error(f"Error adding item: {str(e)}")
            raise
    
    def get_item(self, name: str) -> Optional[Dict]:
        """Get an item by name"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name, quantity, unit, created_at, updated_at
                    FROM inventory
                    WHERE name = ?
                """, (name,))
                row = cursor.fetchone()
                
                if row:
                    return {
                        "id": row["id"],
                        "name": row["name"],
                        "quantity": row["quantity"],
                        "unit": row["unit"],
                        "created_at": row["created_at"],
                        "updated_at": row["updated_at"]
                    }
                return None
                
        except Exception as e:
            logger.error(f"Error getting item: {str(e)}")
            raise
    
    def get_all_inventory(self) -> List[Dict]:
        """Get all inventory items"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name, quantity, unit, created_at, updated_at
                    FROM inventory
                    ORDER BY name ASC
                """)
                rows = cursor.fetchall()
                
                return [
                    {
                        "id": row["id"],
                        "name": row["name"],
                        "quantity": row["quantity"],
                        "unit": row["unit"],
                        "created_at": row["created_at"],
                        "updated_at": row["updated_at"]
                    }
                    for row in rows
                ]
                
        except Exception as e:
            logger.error(f"Error getting inventory: {str(e)}")
            raise
    
    def update_item(self, name: str, quantity: float, unit: str = "units") -> None:
        """Update an existing item"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE inventory
                    SET quantity = ?, unit = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE name = ?
                """, (quantity, unit, name))
                
                if cursor.rowcount == 0:
                    raise ValueError(f"Item '{name}' not found")
                
                conn.commit()
                logger.info(f"Updated item: {name}")
                
        except Exception as e:
            logger.error(f"Error updating item: {str(e)}")
            raise
    
    def reduce_quantity(self, name: str, amount: float) -> None:
        """Reduce quantity of an item"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Get current quantity
                cursor.execute("SELECT quantity FROM inventory WHERE name = ?", (name,))
                row = cursor.fetchone()
                
                if not row:
                    logger.warning(f"Item '{name}' not found, skipping reduction")
                    return
                
                current_quantity = row["quantity"]
                new_quantity = max(0, current_quantity - amount)
                
                if new_quantity == 0:
                    # Delete item if quantity reaches 0
                    cursor.execute("DELETE FROM inventory WHERE name = ?", (name,))
                    logger.info(f"Deleted item {name} (quantity reached 0)")
                else:
                    cursor.execute("""
                        UPDATE inventory
                        SET quantity = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE name = ?
                    """, (new_quantity, name))
                    logger.info(f"Reduced {name}: {current_quantity} - {amount} = {new_quantity}")
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error reducing quantity: {str(e)}")
            raise
    
    def delete_item(self, name: str) -> None:
        """Delete an item from inventory"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM inventory WHERE name = ?", (name,))
                
                if cursor.rowcount == 0:
                    raise ValueError(f"Item '{name}' not found")
                
                conn.commit()
                logger.info(f"Deleted item: {name}")
                
        except Exception as e:
            logger.error(f"Error deleting item: {str(e)}")
            raise
    
    def clear_inventory(self) -> None:
        """Clear all inventory items"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM inventory")
                conn.commit()
                logger.info("Cleared all inventory")
                
        except Exception as e:
            logger.error(f"Error clearing inventory: {str(e)}")
            raise

