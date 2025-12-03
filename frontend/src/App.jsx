import React, { useState, useEffect } from 'react'
import './App.css'
import InventoryList from './components/InventoryList'
import RecipeSuggestion from './components/RecipeSuggestion'
import ShoppingList from './components/ShoppingList'
import VoiceAssistant from './components/VoiceAssistant'
import { fetchInventory, fetchShoppingList } from './services/api'

function App() {
  const [inventory, setInventory] = useState([])
  const [recipe, setRecipe] = useState(null)
  const [shoppingList, setShoppingList] = useState([])
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('inventory')

  // Load initial data
  useEffect(() => {
    loadInventory()
    loadShoppingList()
  }, [])

  const loadInventory = async () => {
    try {
      setLoading(true)
      const data = await fetchInventory()
      setInventory(data.inventory || [])
    } catch (error) {
      console.error('Error loading inventory:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadShoppingList = async () => {
    try {
      const data = await fetchShoppingList()
      setShoppingList(data.shopping_list || [])
    } catch (error) {
      console.error('Error loading shopping list:', error)
    }
  }

  const handleRecipeSuggestion = (recipeData) => {
    setRecipe(recipeData)
    setActiveTab('recipe')
  }

  const handleInventoryUpdate = () => {
    loadInventory()
    loadShoppingList()
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>🛒 Agentic Shopping Assistant</h1>
        <p>Smart inventory management and recipe suggestions</p>
      </header>

      <VoiceAssistant 
        onInventoryUpdate={handleInventoryUpdate}
        onRecipeUpdate={setRecipe}
        onShoppingListUpdate={loadShoppingList}
      />

      <nav className="tab-nav">
        <button 
          className={activeTab === 'inventory' ? 'active' : ''}
          onClick={() => setActiveTab('inventory')}
        >
          📦 Inventory
        </button>
        <button 
          className={activeTab === 'recipe' ? 'active' : ''}
          onClick={() => setActiveTab('recipe')}
        >
          👨‍🍳 Recipe
        </button>
        <button 
          className={activeTab === 'shopping' ? 'active' : ''}
          onClick={() => setActiveTab('shopping')}
        >
          🛍️ Shopping List
        </button>
      </nav>

      <main className="main-content">
        {loading && <div className="loading">Loading...</div>}
        
        {activeTab === 'inventory' && (
          <InventoryList 
            inventory={inventory} 
            onUpdate={handleInventoryUpdate}
          />
        )}
        
        {activeTab === 'recipe' && (
          <RecipeSuggestion 
            recipe={recipe}
            onSuggest={handleRecipeSuggestion}
            onApply={handleInventoryUpdate}
          />
        )}
        
        {activeTab === 'shopping' && (
          <ShoppingList 
            shoppingList={shoppingList}
            onUpdate={handleInventoryUpdate}
          />
        )}
      </main>
    </div>
  )
}

export default App












