# Game Viewer Fix Summary

## What Was Wrong

When you ran `open game_viewer.html` and entered a game ID, the game didn't load because of **5 critical issues**:

### 1. Backend Server Not Running ⚠️
The Django backend API server wasn't running, so all API calls failed.

### 2. Missing Authentication Token ⚠️
The `game_viewer.html` file had a placeholder token that needed to be replaced with a real JWT token.

### 3. CORS Issue ⚠️
Opening the HTML file directly with `open game_viewer.html` uses the `file://` protocol, which causes CORS (Cross-Origin) errors. The file needs to be served via HTTP.

### 4. Missing OpenAI API Key ⚠️
No `.env` file was configured with your OpenAI API key for the RAG model.

### 5. Database Not Set Up ⚠️
The SQLite database hadn't been initialized with migrations.

## What I Fixed

I've made the following improvements to solve these issues:

### Files Created:
1. **`.env`** - Environment configuration (you need to add your OpenAI key)
2. **`.env.example`** - Template for environment variables
3. **`get_auth_token.py`** - Script to generate JWT authentication tokens
4. **`setup_and_run.sh`** - Automated setup script
5. **`QUICKSTART.md`** - 5-minute quick start guide
6. **`SETUP_INSTRUCTIONS.md`** - Detailed setup instructions
7. **`README_GAME_VIEWER.md`** - Comprehensive troubleshooting guide
8. **`FIX_SUMMARY.md`** - This file

### Files Updated:
1. **`game_viewer.html`** - Added better error messages and debugging
2. **`config/settings.py`** - Updated CORS to allow all origins in DEBUG mode

## What You Need to Do Now

Follow these steps **ON YOUR MAC** (in the order shown):

### Step 1: Pull the Latest Code
```bash
cd /path/to/game-learn-backend
git pull origin claude/investigate-game-viewer-011CUWPt2qRsRKFjSCSonqGX
```

### Step 2: Add Your OpenAI API Key
```bash
# Edit the .env file
nano .env  # or use your preferred editor

# Add your actual OpenAI API key where it says:
OPENAI_API_KEY=sk-your-actual-key-here
```

### Step 3: Set Up the Database
```bash
# Make sure you're in your virtual environment
source venv/bin/activate

# Run migrations to create the database
python manage.py migrate

# Populate the ChromaDB with game templates
python manage.py populate_templates
```

### Step 4: Generate Your Authentication Token
```bash
# Run the token generator script
python get_auth_token.py

# Follow the prompts (you can use the defaults):
#   Email: test@example.com
#   Username: testuser
#   Password: testpass123

# Copy the ACCESS TOKEN that's printed
```

### Step 5: Update game_viewer.html with Your Token
```bash
# Open game_viewer.html in your text editor
# Find line 114 that says:
#   const TOKEN = 'YOUR_TOKEN_HERE';
#
# Replace 'YOUR_TOKEN_HERE' with the token from Step 4
# Save the file
```

### Step 6: Start the Backend Server
```bash
# In Terminal 1
source venv/bin/activate
python manage.py runserver
```

The server will start at `http://localhost:8000`

### Step 7: Start Web Server for the HTML File
```bash
# In Terminal 2 (new terminal window)
cd /path/to/game-learn-backend
python -m http.server 8080
```

This serves the HTML file at `http://localhost:8080`

### Step 8: Generate a Test Game
```bash
# In Terminal 3 (new terminal window)
cd /path/to/game-learn-backend
source venv/bin/activate
python test_rag_api.py
```

This will generate a sample game using the RAG model.

### Step 9: Open the Game Viewer
Open your browser and go to:
```
http://localhost:8080/game_viewer.html
```

**DO NOT** use `open game_viewer.html` - you must use the HTTP URL!

### Step 10: Load and Play Your Game
1. Click **"📋 List My Games"**
2. You should see the game you generated (with a ✅ status)
3. Click on the game to select it
4. Click **"🎮 Load Game"**
5. Click **"▶️ Play Game"**

## Key Points to Remember

### ✅ DO:
- Access via `http://localhost:8080/game_viewer.html`
- Keep both servers running (ports 8000 and 8080)
- Use a valid authentication token
- Make sure your OpenAI API key is in `.env`

### ❌ DON'T:
- Use `open game_viewer.html` (causes CORS errors)
- Forget to activate the virtual environment
- Use an expired token (they last 60 minutes)
- Skip the database migration step

## Improved Error Messages

The updated `game_viewer.html` now shows helpful error messages if something goes wrong:

- **"Cannot connect to backend"** → Start the Django server
- **"401 Unauthorized"** → Generate a new token with `python get_auth_token.py`
- **"Token not configured"** → Update the TOKEN in game_viewer.html
- **"Game is generating..."** → Wait 10-30 seconds, the RAG + GPT process takes time

## Quick Command Reference

```bash
# Get a new auth token
python get_auth_token.py

# Start backend (Terminal 1)
python manage.py runserver

# Start game viewer server (Terminal 2)
python -m http.server 8080

# Generate a test game (Terminal 3)
python test_rag_api.py

# Check what games exist
python manage.py shell
>>> from apps.games.models import UserGame
>>> for game in UserGame.objects.all():
...     print(f"{game.title} - {game.status} - {game.id}")
```

## Architecture

Here's how everything works together:

```
Browser (http://localhost:8080/game_viewer.html)
    ↓ [HTTP Request + JWT Token]
Django API (http://localhost:8000)
    ↓ [User prompt]
RAG System (ChromaDB + LangChain)
    ↓ [Retrieved templates + prompt]
OpenAI GPT
    ↓ [Generated PixiJS code]
Database (SQLite)
    ↓ [Stored game]
Browser (Loads and plays PixiJS game)
```

## Verification Checklist

Before trying to load a game, make sure:

- [ ] `.env` file has your OpenAI API key
- [ ] Virtual environment is activated in all terminals
- [ ] Database migrations completed (`python manage.py migrate`)
- [ ] ChromaDB populated (`python manage.py populate_templates`)
- [ ] Backend server running on port 8000 ✓
- [ ] HTTP server running on port 8080 ✓
- [ ] Valid JWT token in `game_viewer.html` ✓
- [ ] Accessing via `http://localhost:8080/game_viewer.html` ✓
- [ ] At least one game generated ✓

## Troubleshooting

If you still have issues:

1. **Check browser console** (F12 → Console tab) for detailed errors
2. **Check backend terminal** for Django error messages
3. **Re-generate token** if you get 401 errors (tokens expire after 60 minutes)
4. **Verify OpenAI key** is correct in `.env`
5. **Check all servers are running** (Django on 8000, HTTP on 8080)

## Files to Review

- **`QUICKSTART.md`** - Fastest way to get started
- **`SETUP_INSTRUCTIONS.md`** - Detailed step-by-step guide
- **`README_GAME_VIEWER.md`** - Complete troubleshooting reference

## What's Different Now

### Before:
- Opening `game_viewer.html` → CORS errors
- No helpful error messages
- Had to manually figure out what was wrong

### After:
- Serve via HTTP → No CORS errors
- Clear error messages with solutions
- Scripts to automate setup
- Comprehensive documentation

## Next Steps

1. Follow Steps 1-10 above **on your Mac**
2. If you get stuck, check the error message in the browser - it will tell you what to do
3. Keep both servers running while using the game viewer
4. Generate new tokens when they expire (every 60 minutes)

All the changes have been committed and are ready for you to pull!
