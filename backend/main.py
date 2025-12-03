"""
Main FastAPI application for Agentic Shopping Assistant
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import sys
import os
from typing import Dict, List, Optional
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agents.planner_agent import PlannerAgent
from backend.agents.inventory_agent import InventoryAgent
from backend.agents.shopping_agent import ShoppingAgent
from database.db_helper import DatabaseHelper
from backend.voice.voice_assistant import VoiceAssistant

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backend.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Agentic Shopping Assistant API",
    description="API for shopping assistant with planner, inventory, and shopping agents",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database and agents
db_helper = DatabaseHelper()
planner_agent = PlannerAgent(db_helper)
inventory_agent = InventoryAgent(db_helper)
shopping_agent = ShoppingAgent(db_helper)
voice_assistant = VoiceAssistant(db_helper, planner_agent, inventory_agent, shopping_agent)


# Request/Response Models
class RecipeRequest(BaseModel):
    preferences: Optional[str] = None
    servings: Optional[int] = 4


class ApplyRecipeRequest(BaseModel):
    recipe_name: str
    servings: Optional[int] = None  # Optional: how many people to cook for


class InventoryUpdate(BaseModel):
    item_name: str
    quantity: float
    unit: str = "units"


class InventoryRemove(BaseModel):
    item_name: str
    quantity: Optional[float] = None  # If None, remove all


class VoiceCommand(BaseModel):
    text: str


class VoiceResponse(BaseModel):
    text: str
    action: Optional[str] = None
    data: Optional[Dict] = None


# Health Check
@app.get("/")
async def root():
    return {"message": "Agentic Shopping Assistant API", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


# Inventory Routes
@app.get("/api/inventory")
async def get_inventory():
    """Get all inventory items"""
    try:
        inventory = db_helper.get_all_inventory()
        return {"inventory": inventory}
    except Exception as e:
        logger.error(f"Error getting inventory: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/inventory/add")
async def add_inventory(item: InventoryUpdate):
    """Add or update inventory item"""
    try:
        result = inventory_agent.add_item(item.item_name, item.quantity, item.unit)
        return {"message": "Item added successfully", "item": result}
    except Exception as e:
        logger.error(f"Error adding inventory: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/inventory/remove")
async def remove_inventory(item: InventoryRemove):
    """Remove inventory item or reduce quantity"""
    try:
        result = inventory_agent.remove_item(item.item_name, item.quantity)
        return {"message": "Item removed successfully", "item": result}
    except Exception as e:
        logger.error(f"Error removing inventory: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Planner Agent Routes
@app.post("/api/planner/suggest-recipe")
async def suggest_recipe(request: RecipeRequest):
    """Get recipe suggestion based on available ingredients"""
    try:
        recipe = planner_agent.suggest_recipe(request.preferences, request.servings)
        return {"recipe": recipe}
    except Exception as e:
        logger.error(f"Error suggesting recipe: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/planner/apply-recipe")
async def apply_recipe(request: ApplyRecipeRequest):
    """Apply a recipe and update inventory with optional scaling"""
    try:
        result = planner_agent.apply_recipe(request.recipe_name, request.servings)
        return {"message": "Recipe applied successfully", "result": result}
    except Exception as e:
        logger.error(f"Error applying recipe: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Shopping Agent Routes
@app.get("/api/shopping/list")
async def get_shopping_list():
    """Get current shopping list"""
    try:
        shopping_list = shopping_agent.generate_shopping_list()
        return {"shopping_list": shopping_list}
    except Exception as e:
        logger.error(f"Error getting shopping list: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/shopping/update-threshold/{item_name}")
async def update_threshold(item_name: str, threshold: float):
    """Update low-quantity threshold for an item"""
    try:
        result = shopping_agent.update_threshold(item_name, threshold)
        return {"message": "Threshold updated", "item": result}
    except Exception as e:
        logger.error(f"Error updating threshold: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Voice Assistant Routes
@app.post("/api/voice/process", response_model=VoiceResponse)
async def process_voice_command(command: VoiceCommand):
    """Process voice command and return response"""
    try:
        response = voice_assistant.process_command(command.text)
        return response
    except Exception as e:
        logger.error(f"Error processing voice command: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/voice/supported-commands")
async def get_supported_commands():
    """Get list of supported voice commands"""
    return {
        "commands": [
            "Add [item] to inventory",
            "Remove [item] from inventory",
            "Update [item] quantity to [amount]",
            "Suggest a recipe",
            "What's my shopping list?",
            "What ingredients do I have?",
        ]
    }


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

