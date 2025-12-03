"""
Database initialization script
Creates database and populates with seed data
"""
import sqlite3
import os
import sys

# Add parent directory to path to import db_helper
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_helper import DatabaseHelper


def init_database():
    """Initialize database with seed data"""
    db_path = "database/inventory.db"
    db_helper = DatabaseHelper(db_path)
    
    # Check if database already has data
    existing_items = db_helper.get_all_inventory()
    
    if existing_items:
        print(f"Database already contains {len(existing_items)} items.")
        response = input("Do you want to clear and reinitialize? (y/n): ")
        if response.lower() != 'y':
            print("Keeping existing data.")
            return
    
    # Clear existing data
    db_helper.clear_inventory()
    
    # Seed data
    seed_items = [
        ('flour', 2.5, 'cups'),
        ('sugar', 1.0, 'cups'),
        ('eggs', 6, 'pieces'),
        ('milk', 2, 'liters'),
        ('butter', 0.5, 'cups'),
        ('tomatoes', 5, 'pieces'),
        ('onions', 3, 'pieces'),
        ('garlic', 10, 'cloves'),
        ('olive oil', 1, 'bottles'),
        ('salt', 0.5, 'cups'),
        ('pepper', 0.2, 'cups'),
        ('chicken breast', 0.8, 'kilograms'),
        ('rice', 3, 'cups'),
        ('pasta', 500, 'grams'),
        ('cheese', 0.3, 'kilograms'),
        ('lettuce', 1, 'head'),
        ('cucumber', 2, 'pieces'),
        ('carrots', 4, 'pieces'),
        ('potatoes', 6, 'pieces'),
        ('bread', 1, 'loaf'),
    ]
    
    print("Adding seed data...")
    for name, quantity, unit in seed_items:
        try:
            db_helper.add_item(name, quantity, unit)
            print(f"✓ Added {name}: {quantity} {unit}")
        except Exception as e:
            print(f"✗ Error adding {name}: {str(e)}")
    
    print(f"\nDatabase initialized successfully with {len(seed_items)} items!")
    print(f"Database location: {os.path.abspath(db_path)}")


if __name__ == "__main__":
    init_database()













