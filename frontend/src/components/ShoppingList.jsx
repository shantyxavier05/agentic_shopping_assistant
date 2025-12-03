import React from 'react'
import './ShoppingList.css'

const ShoppingList = ({ shoppingList, onUpdate }) => {
  if (!shoppingList || shoppingList.length === 0) {
    return (
      <div className="shopping-list">
        <h2>🛍️ Shopping List</h2>
        <div className="empty-state">
          <p>Great! You have all the items you need. Your inventory looks good! 🎉</p>
        </div>
      </div>
    )
  }

  return (
    <div className="shopping-list">
      <div className="shopping-header">
        <h2>🛍️ Shopping List</h2>
        <p className="shopping-count">{shoppingList.length} item(s) needed</p>
      </div>

      <div className="shopping-items">
        {shoppingList.map((item, index) => (
          <div 
            key={index} 
            className={`shopping-item ${item.priority === 'high' ? 'high-priority' : ''}`}
          >
            <div className="item-main">
              <h3>{item.name}</h3>
              <div className="item-details">
                <span className="current">
                  Current: {item.current_quantity} {item.unit}
                </span>
                {item.threshold > 0 && (
                  <span className="threshold">
                    Threshold: {item.threshold} {item.unit}
                  </span>
                )}
              </div>
            </div>
            <div className="item-action">
              <div className="suggested-quantity">
                Suggested: {item.suggested_quantity} {item.unit}
              </div>
              {item.priority === 'high' && (
                <span className="priority-badge">High Priority</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default ShoppingList













