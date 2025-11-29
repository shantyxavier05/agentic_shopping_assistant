# Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Step 1: Install Dependencies

**Backend:**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### Step 2: Initialize Database

```bash
python database/init_db.py
```

### Step 3: Start Servers

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Step 4: Open Browser

Navigate to: **http://localhost:3000**

## 🎯 Quick Test

1. **Add an item:**
   - Click "Inventory" tab
   - Click "+ Add Item"
   - Enter: "flour", quantity: 2, unit: "cups"
   - Click "Add"

2. **Get recipe:**
   - Click "Recipe" tab
   - Click "🎲 Suggest Recipe"
   - View the suggested recipe

3. **Try voice:**
   - Click "🎤 Start Voice"
   - Say: "Add tomatoes to inventory"
   - Or type: "Suggest a recipe"

## 🐛 Troubleshooting

**Port already in use?**
- Backend: Change port in `backend/main.py` (line ~216)
- Frontend: Change port in `frontend/vite.config.js`

**Database errors?**
- Run `python database/init_db.py` again

**Import errors?**
- Make sure you're running from the correct directory
- Activate virtual environment

## 📖 Full Documentation

See [README.md](README.md) for complete documentation.







