# How to Run Python Files - Step by Step

## ❌ WRONG Way (What's happening to you)
- Double-clicking `main.py` file → Opens in IDE/Editor
- This is for EDITING code, not RUNNING it

## ✅ CORRECT Way (How to run Python files)

### Option 1: Using Terminal/Command Prompt

1. **Open PowerShell or Command Prompt**
   - Press `Windows Key + X`
   - Choose "Windows PowerShell" or "Terminal"

2. **Navigate to your project folder**
   ```powershell
   cd "C:\Users\ShantyXavier(G10XIND\AI Project\backend"
   ```

3. **Run the Python file**
   ```powershell
   python main.py
   ```
   OR
   ```powershell
   python -m uvicorn main:app --reload
   ```

### Option 2: Using VS Code Terminal

1. Open your project in VS Code
2. Open Terminal: Press `` Ctrl + ` `` (backtick key) or View → Terminal
3. Navigate to backend folder: `cd backend`
4. Run: `python main.py`

### Option 3: Using the Batch File (Easiest)

Just double-click:
- `start_backend.bat` - This will run the server automatically

---

## 🔍 What happens when you run?

When you run `python main.py`, you should see output like:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

This means your server is RUNNING, not just opening in an editor!

---

## 💡 Key Difference

| Action | What Happens |
|--------|-------------|
| Double-click `main.py` | Opens file in editor (for editing) |
| `python main.py` in terminal | Actually RUNS the program |
| `python filename.py` | Executes the Python script |

---

## 🎯 Quick Test

Try this in your terminal:
```powershell
python -c "print('Hello from Python!')"
```

If you see "Hello from Python!" printed, then Python is working correctly in terminal!










