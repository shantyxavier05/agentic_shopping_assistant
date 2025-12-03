import React, { useState } from 'react'
import './InventoryList.css'
import { addInventoryItem, removeInventoryItem } from '../services/api'

const InventoryList = ({ inventory, onUpdate }) => {
  const [showAddForm, setShowAddForm] = useState(false)
  const [formData, setFormData] = useState({
    item_name: '',
    quantity: '',
    unit: 'units'
  })

  const handleAdd = async (e) => {
    e.preventDefault()
    try {
      await addInventoryItem(formData.item_name, parseFloat(formData.quantity), formData.unit)
      setFormData({ item_name: '', quantity: '', unit: 'units' })
      setShowAddForm(false)
      onUpdate()
    } catch (error) {
      console.error('Error adding item:', error)
      alert('Error adding item. Please try again.')
    }
  }

  const handleRemove = async (itemName, quantity = null) => {
    try {
      await removeInventoryItem(itemName, quantity)
      onUpdate()
    } catch (error) {
      console.error('Error removing item:', error)
      alert('Error removing item. Please try again.')
    }
  }

  return (
    <div className="inventory-list">
      <div className="inventory-header">
        <h2>📦 Inventory</h2>
        <button 
          className="add-button"
          onClick={() => setShowAddForm(!showAddForm)}
        >
          {showAddForm ? 'Cancel' : '+ Add Item'}
        </button>
      </div>

      {showAddForm && (
        <form onSubmit={handleAdd} className="add-form">
          <input
            type="text"
            placeholder="Item name"
            value={formData.item_name}
            onChange={(e) => setFormData({ ...formData, item_name: e.target.value })}
            required
          />
          <input
            type="number"
            step="0.1"
            placeholder="Quantity"
            value={formData.quantity}
            onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
            required
          />
          <select
            value={formData.unit}
            onChange={(e) => setFormData({ ...formData, unit: e.target.value })}
          >
            <option value="units">units</option>
            <option value="cups">cups</option>
            <option value="grams">grams</option>
            <option value="kilograms">kilograms</option>
            <option value="liters">liters</option>
            <option value="pieces">pieces</option>
            <option value="tablespoons">tablespoons</option>
            <option value="bottles">bottles</option>
            <option value="cloves">cloves</option>
            <option value="head">head</option>
            <option value="loaf">loaf</option>
          </select>
          <button type="submit">Add</button>
        </form>
      )}

      {inventory.length === 0 ? (
        <div className="empty-state">
          <p>Your inventory is empty. Add some items to get started!</p>
        </div>
      ) : (
        <div className="inventory-grid">
          {inventory.map((item) => (
            <div key={item.id} className="inventory-item">
              <div className="item-info">
                <h3>{item.name}</h3>
                <p className="quantity">
                  {item.quantity} {item.unit}
                </p>
              </div>
              <div className="item-actions">
                <button
                  className="remove-button"
                  onClick={() => handleRemove(item.name)}
                  title="Remove all"
                >
                  🗑️
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default InventoryList













