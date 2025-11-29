"""
LLM Client for generating recipes
Supports OpenAI API or mock implementation
"""
import logging
import json
import os
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for LLM API calls (OpenAI or mock)"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.use_mock = os.getenv("USE_MOCK_LLM", "true").lower() == "true" or not self.api_key
    
    def generate_recipe(self, prompt: str) -> Dict:
        """
        Generate a recipe using LLM
        
        Args:
            prompt: Prompt for recipe generation
            
        Returns:
            Dictionary with recipe details
        """
        if self.use_mock:
            return self._mock_generate_recipe(prompt)
        else:
            return self._openai_generate_recipe(prompt)
    
    def _openai_generate_recipe(self, prompt: str) -> Dict:
        """Generate recipe using OpenAI API"""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful cooking assistant. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            
            # Try to parse JSON from response
            try:
                # Remove code blocks if present
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                recipe = json.loads(content)
                return recipe
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON from LLM response, using mock")
                return self._mock_generate_recipe(prompt)
                
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            logger.info("Falling back to mock implementation")
            return self._mock_generate_recipe(prompt)
    
    def _mock_generate_recipe(self, prompt: str) -> Dict:
        """Mock recipe generation for testing"""
        logger.info("Using mock LLM to generate recipe")
        
        # Extract available ingredients from prompt (simple parsing)
        ingredients_text = ""
        if "Available ingredients:" in prompt:
            ingredients_text = prompt.split("Available ingredients:")[1].split("\n\n")[0]
        
        # Sample recipes based on common ingredients
        sample_recipes = [
            {
                "name": "Pasta with Vegetables",
                "description": "A simple and healthy pasta dish using available ingredients",
                "servings": 4,
                "ingredients": [
                    {"name": "pasta", "quantity": 400, "unit": "grams"},
                    {"name": "tomatoes", "quantity": 4, "unit": "pieces"},
                    {"name": "garlic", "quantity": 3, "unit": "cloves"},
                    {"name": "olive oil", "quantity": 2, "unit": "tablespoons"}
                ],
                "instructions": [
                    "Cook pasta according to package instructions",
                    "Heat olive oil in a pan",
                    "Add garlic and sauté until fragrant",
                    "Add tomatoes and cook until soft",
                    "Mix with cooked pasta and serve"
                ]
            },
            {
                "name": "Vegetable Stir Fry",
                "description": "Quick and colorful vegetable stir fry",
                "servings": 4,
                "ingredients": [
                    {"name": "mixed vegetables", "quantity": 500, "unit": "grams"},
                    {"name": "garlic", "quantity": 2, "unit": "cloves"},
                    {"name": "soy sauce", "quantity": 3, "unit": "tablespoons"},
                    {"name": "oil", "quantity": 2, "unit": "tablespoons"}
                ],
                "instructions": [
                    "Heat oil in a wok or large pan",
                    "Add garlic and stir fry for 30 seconds",
                    "Add vegetables and cook for 5-7 minutes",
                    "Add soy sauce and stir well",
                    "Serve hot with rice or noodles"
                ]
            },
            {
                "name": "Simple Salad",
                "description": "Fresh and healthy salad",
                "servings": 4,
                "ingredients": [
                    {"name": "lettuce", "quantity": 1, "unit": "head"},
                    {"name": "tomatoes", "quantity": 3, "unit": "pieces"},
                    {"name": "cucumber", "quantity": 1, "unit": "piece"},
                    {"name": "olive oil", "quantity": 2, "unit": "tablespoons"}
                ],
                "instructions": [
                    "Wash and chop lettuce",
                    "Cut tomatoes and cucumber into pieces",
                    "Mix all vegetables in a bowl",
                    "Drizzle with olive oil",
                    "Season and serve"
                ]
            }
        ]
        
        # Select recipe based on ingredients (simple matching)
        recipe = sample_recipes[0]  # Default to first recipe
        
        # Try to match ingredients
        prompt_lower = prompt.lower()
        if "pasta" in prompt_lower:
            recipe = sample_recipes[0]
        elif "vegetable" in prompt_lower or "stir" in prompt_lower:
            recipe = sample_recipes[1]
        elif "lettuce" in prompt_lower or "salad" in prompt_lower:
            recipe = sample_recipes[2]
        
        return recipe
