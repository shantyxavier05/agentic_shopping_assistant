<<<<<<< HEAD
# 🛒 Agentic Shopping Assistant

A comprehensive AI-powered shopping assistant system with three intelligent agents that manage inventory, suggest recipes, and generate shopping lists. Features voice assistant capabilities with speech-to-text and text-to-speech support.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Usage Examples](#usage-examples)
- [Testing](#testing)
- [Scalability & Enhancements](#scalability--enhancements)

## ✨ Features

### Three Intelligent Agents

1. **Planner Agent** 📅
   - Reads inventory from SQLite database
   - Uses LLM to suggest recipes based on available ingredients
   - Applies recipes by removing used ingredients

2. **Inventory Agent** 📦
   - Manages inventory items in SQLite database
   - Add/remove/update quantities
   - Real-time inventory tracking

3. **Shopping Agent** 🛍️
   - Identifies missing or low-quantity ingredients
   - Generates prioritized shopping lists
   - Customizable low-quantity thresholds

### Voice Assistant 🎤

- **Speech-to-Text**: Browser-based voice recognition
- **Text-to-Speech**: Automated voice responses
- **Natural Language Processing**: Understands commands like:
  - "Add flour to inventory"
  - "Suggest a recipe"
  - "What's my shopping list?"
  - "Remove eggs from inventory"

### Modern UI

- React-based frontend with Vite
- Beautiful, responsive design
- Real-time updates
- Tabbed interface for easy navigation

## 🏗️ Architecture

```
┌─────────────────┐
│   React UI      │
│   (Frontend)    │
└────────┬────────┘
         │ HTTP/REST API
┌────────▼────────────────────────┐
│      FastAPI Backend            │
│  ┌──────────────────────────┐   │
│  │   Voice Assistant        │   │
│  └──────────────────────────┘   │
│  ┌──────────┐  ┌──────────┐    │
│  │ Planner  │  │Inventory │    │
│  │  Agent   │  │  Agent   │    │
│  └──────────┘  └──────────┘    │
│  ┌──────────┐                  │
│  │ Shopping │                  │
│  │  Agent   │                  │
│  └─────┬────┘                  │
└────────┼────────────────────────┘
         │
┌────────▼────────┐
│   SQLite DB     │
│   (Database)    │
└─────────────────┘
```

## 📁 Project Structure

```
project/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── planner_agent.py    # Recipe suggestion agent
│   │   ├── inventory_agent.py  # Inventory management agent
│   │   └── shopping_agent.py   # Shopping list generator
│   ├── llm/
│   │   ├── __init__.py
│   │   └── llm_client.py       # LLM integration (OpenAI/Mock)
│   └── voice/
│       ├── __init__.py
│       └── voice_assistant.py  # Voice command processor
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── App.css
│       ├── index.css
│       ├── components/
│       │   ├── VoiceAssistant.jsx
│       │   ├── InventoryList.jsx
│       │   ├── RecipeSuggestion.jsx
│       │   └── ShoppingList.jsx
│       └── services/
│           └── api.js           # API client
│
├── database/
│   ├── schema.sql               # Database schema
│   ├── seed_data.sql            # Sample data
│   ├── db_helper.py             # Database operations
│   └── init_db.py               # Database initialization script
│
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🚀 Installation

### Prerequisites

- **Python 3.8+**
- **Node.js 16+** and npm
- (Optional) OpenAI API key for real LLM recipes

### Backend Setup

1. **Navigate to project root:**
   ```bash
   cd "path/to/AI Project"
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize database:**
   ```bash
   python database/init_db.py
   ```

5. **Set environment variables (optional):**
   ```bash
   # For OpenAI API (if not using mock)
   set OPENAI_API_KEY=your_api_key_here  # Windows
   # or
   export OPENAI_API_KEY=your_api_key_here  # macOS/Linux
   
   # To force mock LLM even with API key:
   set USE_MOCK_LLM=true  # Windows
   # or
   export USE_MOCK_LLM=true  # macOS/Linux
   ```

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

## 🏃 Running the Application

### Start Backend Server

1. **Activate virtual environment** (if not already active)

2. **Navigate to project root** and run:
   ```bash
   cd backend
   python main.py
   ```
   
   Or use uvicorn directly:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Backend will start on:** `http://localhost:8000`
   - API docs available at: `http://localhost:8000/docs`

### Start Frontend Development Server

1. **Open a new terminal** and navigate to frontend:
   ```bash
   cd frontend
   ```

2. **Start the dev server:**
   ```bash
   npm run dev
   ```

3. **Frontend will start on:** `http://localhost:3000`

### Access the Application

Open your browser and navigate to: **http://localhost:3000**

## 📚 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### Inventory Management

**GET `/api/inventory`**
- Get all inventory items
- Response: `{ "inventory": [...] }`

**POST `/api/inventory/add`**
- Add or update inventory item
- Body: `{ "item_name": "flour", "quantity": 2.5, "unit": "cups" }`

**POST `/api/inventory/remove`**
- Remove item or reduce quantity
- Body: `{ "item_name": "flour", "quantity": 0.5 }` (quantity optional)

#### Planner Agent

**POST `/api/planner/suggest-recipe`**
- Get recipe suggestion
- Body: `{ "preferences": "vegetarian", "servings": 4 }`
- Response: Recipe object with ingredients and instructions

**POST `/api/planner/apply-recipe`**
- Apply recipe (remove ingredients)
- Body: `{ "recipe_name": "Pasta with Vegetables" }`

#### Shopping Agent

**GET `/api/shopping/list`**
- Get current shopping list
- Response: `{ "shopping_list": [...] }`

#### Voice Assistant

**POST `/api/voice/process`**
- Process voice/text command
- Body: `{ "text": "Add flour to inventory" }`
- Response: `{ "text": "...", "action": "...", "data": {...} }`

**GET `/api/voice/supported-commands`**
- Get list of supported commands

### Interactive API Documentation

FastAPI provides interactive Swagger UI:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 💡 Usage Examples

### Using the Web UI

1. **Add Inventory Items:**
   - Click "Inventory" tab
   - Click "+ Add Item"
   - Enter name, quantity, and unit
   - Click "Add"

2. **Get Recipe Suggestion:**
   - Click "Recipe" tab
   - Click "🎲 Suggest Recipe"
   - View suggested recipe
   - Click "Apply Recipe" to remove used ingredients

3. **View Shopping List:**
   - Click "Shopping List" tab
   - See items that need to be purchased

4. **Use Voice Assistant:**
   - Click "🎤 Start Voice" button
   - Speak commands like:
     - "Add 2 cups of flour to inventory"
     - "Suggest a recipe"
     - "What's my shopping list?"
   - Or type commands in the text input

### Using API Directly

#### Example: Add item via curl
```bash
curl -X POST "http://localhost:8000/api/inventory/add" \
  -H "Content-Type: application/json" \
  -d '{"item_name": "flour", "quantity": 2.5, "unit": "cups"}'
```

#### Example: Get recipe suggestion
```bash
curl -X POST "http://localhost:8000/api/planner/suggest-recipe" \
  -H "Content-Type: application/json" \
  -d '{"servings": 4}'
```

## 🧪 Testing

### Sample Test Prompts

#### Inventory Agent
1. "Add 3 cups of sugar to inventory"
2. "Remove 1 cup of flour from inventory"
3. "Update eggs quantity to 12"

#### Planner Agent
1. "Suggest a recipe for 4 people"
2. "What can I make with my ingredients?"
3. Apply a suggested recipe

#### Shopping Agent
1. "What's my shopping list?"
2. "What ingredients do I need to buy?"

#### Voice Assistant
1. "Add tomatoes to inventory"
2. "Remove eggs from inventory"
3. "Suggest a recipe"
4. "What ingredients do I have?"
5. "What's my shopping list?"

### Manual Testing Checklist

- [ ] Add inventory items via UI
- [ ] Add inventory items via voice
- [ ] Remove inventory items
- [ ] Get recipe suggestion
- [ ] Apply recipe (removes ingredients)
- [ ] View shopping list
- [ ] Test voice commands (if browser supports)
- [ ] Test text-to-speech responses

## 🚀 Scalability & Enhancements

### Current Limitations

1. **Mock LLM**: Default uses mock recipe generation
2. **Single SQLite DB**: Not optimized for high concurrency
3. **Browser Voice**: Limited by browser compatibility

### Suggested Enhancements

#### 1. Database Scaling
- Migrate to PostgreSQL for production
- Add connection pooling
- Implement database migrations (Alembic)

#### 2. LLM Integration
- Support multiple LLM providers (OpenAI, Anthropic, local models)
- Recipe caching to reduce API calls
- Fine-tuned recipe models

#### 3. User Management
- Multi-user support with authentication
- User-specific inventories
- Recipe favorites and history

#### 4. Advanced Features
- Meal planning (weekly/monthly)
- Nutritional information
- Ingredient substitution suggestions
- Price tracking and budget management
- Barcode scanning for inventory

#### 5. Mobile App
- React Native mobile app
- Push notifications for low stock
- Offline mode support

#### 6. Voice Assistant Improvements
- Better NLP with spaCy or similar
- Multi-language support
- Wake word detection
- Integration with smart speakers

#### 7. Real-time Features
- WebSocket for real-time updates
- Collaborative shopping lists
- Live inventory sync

#### 8. Analytics
- Usage analytics
- Popular recipes tracking
- Shopping pattern analysis

#### 9. Integration
- Connect with grocery delivery APIs
- Calendar integration for meal planning
- Smart home device integration

### Production Deployment

1. **Backend:**
   - Use Gunicorn/Uvicorn with multiple workers
   - Add Redis for caching
   - Set up proper logging (ELK stack)
   - Add monitoring (Prometheus/Grafana)

2. **Frontend:**
   - Build for production: `npm run build`
   - Serve with Nginx or similar
   - Enable HTTPS
   - Add CDN for static assets

3. **Database:**
   - Regular backups
   - Replication for high availability
   - Connection pooling

4. **Security:**
   - Add authentication/authorization
   - Rate limiting
   - Input validation and sanitization
   - CORS configuration
   - API key management

## 🐛 Troubleshooting

### Backend Issues

**Port already in use:**
```bash
# Find process using port 8000
netstat -ano | findstr :8000  # Windows
lsof -i :8000  # macOS/Linux

# Kill process or change port in main.py
```

**Database errors:**
- Ensure database directory exists
- Run `python database/init_db.py` to reinitialize

**Module not found:**
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### Frontend Issues

**Port 3000 already in use:**
- Change port in `vite.config.js`
- Or kill the process using port 3000

**API connection errors:**
- Ensure backend is running on port 8000
- Check CORS settings in `backend/main.py`
- Verify API_BASE_URL in `frontend/src/services/api.js`

**Voice not working:**
- Check browser compatibility (Chrome/Edge recommended)
- Ensure microphone permissions are granted
- HTTPS may be required in production

## 📝 License

This project is provided as-is for educational and demonstration purposes.

## 👤 Author

Agentic Shopping Assistant System

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- React and Vite for the modern frontend
- OpenAI for LLM capabilities (optional)

---

**Happy Shopping! 🛒✨**







=======
# agentic_shopping_assistant
ai project
>>>>>>> 1f1bc1768e2f35c52fe82c905e97ddf729dadec0
