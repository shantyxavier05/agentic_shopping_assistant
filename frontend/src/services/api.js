import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Inventory APIs
export const fetchInventory = async () => {
  const response = await api.get('/api/inventory')
  return response.data
}

export const addInventoryItem = async (itemName, quantity, unit = 'units') => {
  const response = await api.post('/api/inventory/add', {
    item_name: itemName,
    quantity,
    unit
  })
  return response.data
}

export const removeInventoryItem = async (itemName, quantity = null) => {
  const response = await api.post('/api/inventory/remove', {
    item_name: itemName,
    quantity
  })
  return response.data
}

// Planner APIs
export const suggestRecipe = async (preferences = null, servings = 4) => {
  const response = await api.post('/api/planner/suggest-recipe', {
    preferences,
    servings
  })
  return response.data
}

export const applyRecipe = async (recipeName) => {
  const response = await api.post('/api/planner/apply-recipe', {
    recipe_name: recipeName
  })
  return response.data
}

// Shopping APIs
export const fetchShoppingList = async () => {
  const response = await api.get('/api/shopping/list')
  return response.data
}

// Voice APIs
export const processVoiceCommand = async (text) => {
  const response = await api.post('/api/voice/process', {
    text
  })
  return response.data
}

export default api

