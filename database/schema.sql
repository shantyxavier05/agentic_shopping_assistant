-- Database schema for Agentic Shopping Assistant
-- SQLite database schema

-- Inventory table
CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    quantity REAL NOT NULL,
    unit TEXT NOT NULL DEFAULT 'units',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster name lookups
CREATE INDEX IF NOT EXISTS idx_inventory_name ON inventory(name);

-- Sample data can be inserted using seed_data.sql







