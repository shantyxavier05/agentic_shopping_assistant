import React, { useState } from 'react'
import './RecipeSuggestion.css'
import { applyRecipe, suggestRecipe } from '../services/api'

const RecipeSuggestion = ({ recipe, onSuggest, onApply }) => {
  const [numPeople, setNumPeople] = useState(4)
  const [isSuggesting, setIsSuggesting] = useState(false)

  const handleSuggestRecipe = async () => {
    if (!numPeople || numPeople < 1) {
      alert('Please enter a valid number of people (at least 1)')
      return
    }

    try {
      setIsSuggesting(true)
      const data = await suggestRecipe(null, numPeople)
      onSuggest(data.recipe)
    } catch (error) {
      console.error('Error suggesting recipe:', error)
      alert('Error suggesting recipe. Please try again.')
    } finally {
      setIsSuggesting(false)
    }
  }

  const handleApplyRecipe = async () => {
    if (!recipe || !recipe.name) {
      alert('No recipe selected to apply')
      return
    }

    if (!numPeople || numPeople < 1) {
      alert('Please enter a valid number of people (at least 1)')
      return
    }

    try {
      await applyRecipe(recipe.name, numPeople)
      alert(`Recipe applied for ${numPeople} people! Ingredients have been removed from inventory.`)
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
        <div className="header-controls">
          <div className="people-input-container">
            <label htmlFor="numPeople">Number of People:</label>
            <input
              id="numPeople"
              type="number"
              min="1"
              value={numPeople}
              onChange={(e) => setNumPeople(parseInt(e.target.value) || 1)}
              className="people-input"
            />
          </div>
          <button 
            className="suggest-button" 
            onClick={handleSuggestRecipe}
            disabled={isSuggesting}
          >
            {isSuggesting ? '⏳ Suggesting...' : '🎲 Suggest Recipe'}
          </button>
        </div>
      </div>

      {!recipe ? (
        <div className="empty-state">
          <p>Enter the number of people and click "Suggest Recipe" to get a recipe based on your available ingredients!</p>
        </div>
      ) : (
        <div className="recipe-card">
          <h3 className="recipe-name">{recipe.name}</h3>
          <p className="recipe-description">{recipe.description}</p>
          
          <div className="recipe-info">
            <span className="servings">Serves: {recipe.servings || numPeople} people</span>
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
            ✅ Apply Recipe for {numPeople} People (Remove Ingredients from Inventory)
          </button>
        </div>
      )}
    </div>
  )
}

export default RecipeSuggestion












