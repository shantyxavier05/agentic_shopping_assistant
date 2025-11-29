import React from 'react'
import './RecipeSuggestion.css'
import { applyRecipe } from '../services/api'

const RecipeSuggestion = ({ recipe, onSuggest, onApply }) => {
  const handleApplyRecipe = async () => {
    if (!recipe || !recipe.name) {
      alert('No recipe selected to apply')
      return
    }

    try {
      await applyRecipe(recipe.name)
      alert('Recipe applied! Ingredients have been removed from inventory.')
      onApply()
    } catch (error) {
      console.error('Error applying recipe:', error)
      alert('Error applying recipe. Please try again.')
    }
  }

  return (
    <div className="recipe-suggestion">
      <div className="recipe-header">
        <h2>👨‍🍳 Recipe Suggestion</h2>
        <button className="suggest-button" onClick={onSuggest}>
          🎲 Suggest Recipe
        </button>
      </div>

      {!recipe ? (
        <div className="empty-state">
          <p>Click "Suggest Recipe" to get a recipe based on your available ingredients!</p>
        </div>
      ) : (
        <div className="recipe-card">
          <h3 className="recipe-name">{recipe.name}</h3>
          <p className="recipe-description">{recipe.description}</p>
          
          <div className="recipe-info">
            <span className="servings">Serves: {recipe.servings || 4}</span>
          </div>

          <div className="recipe-section">
            <h4>Ingredients:</h4>
            <ul className="ingredients-list">
              {recipe.ingredients && recipe.ingredients.map((ingredient, index) => (
                <li key={index}>
                  {ingredient.quantity} {ingredient.unit || 'units'} of {ingredient.name}
                </li>
              ))}
            </ul>
          </div>

          <div className="recipe-section">
            <h4>Instructions:</h4>
            <ol className="instructions-list">
              {recipe.instructions && recipe.instructions.map((step, index) => (
                <li key={index}>{step}</li>
              ))}
            </ol>
          </div>

          <button 
            className="apply-button"
            onClick={handleApplyRecipe}
          >
            ✅ Apply Recipe (Remove Ingredients from Inventory)
          </button>
        </div>
      )}
    </div>
  )
}

export default RecipeSuggestion







