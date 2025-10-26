# Game Viewer Troubleshooting Guide

## Your Current Issue

You're running `open game_viewer.html` and seeing the page, but when you enter a game ID, the game doesn't load.

## Root Causes

After analyzing your setup, here are the issues preventing the game viewer from working:

### 1. Backend Server Not Running ❌
- **Problem**: The Django backend server isn't running
- **Impact**: All API calls fail (no connection to `http://localhost:8000`)
- **Solution**: Run `python manage.py runserver`

### 2. Missing Authentication Token ❌
- **Problem**: `game_viewer.html` has `TOKEN = 'YOUR_TOKEN_HERE'` placeholder
- **Impact**: All API requests return 401 Unauthorized
- **Solution**: Generate and configure a valid JWT token

### 3. CORS Configuration Issue ❌
- **Problem**: Opening HTML directly with `open game_viewer.html` uses `file://` protocol
- **Impact**: CORS blocks API requests (security restriction)
- **Solution**: Serve the HTML via HTTP server on port 8080

### 4. Missing Environment Setup ❌
- **Problem**: No `.env` file with OpenAI API key
- **Impact**: RAG model can't generate games
- **Solution**: Create `.env` with your OpenAI key

### 5. Database Not Initialized ❌
- **Problem**: SQLite database doesn't exist
- **Impact**: No user accounts, no games stored
- **Solution**: Run `python manage.py migrate`

## Complete Fix - Step by Step

I've created helper scripts and documentation to fix all these issues. Here's what to do:

### Option A: Automated Setup (Recommended)

```bash
# 1. Set up your OpenAI API key
cp .env.example .env
# Edit .env and add: OPENAI_API_KEY=sk-your-key-here

# 2. Activate virtual environment
source venv/bin/activate

# 3. Run migrations
python manage.py migrate

# 4. Populate game templates for RAG
python manage.py populate_templates

# 5. Get authentication token
python get_auth_token.py
# Copy the ACCESS TOKEN that's printed

# 6. Update game_viewer.html
# Open game_viewer.html in editor
# Replace 'YOUR_TOKEN_HERE' with your token

# 7. Start backend server (Terminal 1)
python manage.py runserver

# 8. Start web server for HTML (Terminal 2)
python -m http.server 8080

# 9. Open browser
# Go to: http://localhost:8080/game_viewer.html
```

### Option B: Use the Setup Script

```bash
./setup_and_run.sh
# Follow the prompts
```

## Testing the Complete Flow

Once everything is set up:

### 1. Generate a Test Game

**Terminal 3:**
```bash
python test_rag_api.py
```

This will:
- Create a test user
- Generate a sample game using RAG + GPT
- Print the game ID

### 2. View and Play the Game

1. Open browser to `http://localhost:8080/game_viewer.html`
2. Click **"📋 List My Games"** button
3. You should see your generated game with status indicator:
   - ✅ = Ready to play
   - ⏳ = Still generating (wait 10-30 seconds)
   - ❌ = Generation failed
4. Click on the game to auto-fill the ID
5. Click **"🎮 Load Game"**
6. Click **"▶️ Play Game"**

## Architecture Overview

```
┌─────────────────┐
│  game_viewer.html  │ (Port 8080 - Python HTTP server)
│  - User interface  │
│  - PixiJS renderer │
└─────────┬─────────┘
          │ HTTP + JWT Auth
          ▼
┌─────────────────┐
│ Django Backend    │ (Port 8000)
│ - REST API        │
│ - Game generation │
└─────────┬─────────┘
          │
          ▼
┌─────────────────────┐
│   RAG System        │
│ - ChromaDB Vector DB│
│ - Template retrieval│
└─────────┬───────────┘
          │
          ▼
┌─────────────────┐
│   OpenAI GPT    │
│ - Code generation│
│ - Game logic    │
└─────────────────┘
```

## Common Errors and Solutions

| Error Message | Cause | Solution |
|--------------|-------|----------|
| "Failed to fetch" | Backend not running | Start: `python manage.py runserver` |
| "401 Unauthorized" | Invalid/missing token | Run: `python get_auth_token.py` |
| "CORS policy error" | Using file:// protocol | Use: `http://localhost:8080/game_viewer.html` |
| "Cannot connect" | Wrong port/URL | Check backend is on port 8000 |
| "Game is generating..." forever | OpenAI key issue or error | Check backend terminal for errors |
| No games in list | None generated yet | Run: `python test_rag_api.py` |
| Token expired | JWT expired (60 min) | Generate new token |

## Verification Checklist

Before trying to load a game, verify:

- [ ] `.env` file exists with valid `OPENAI_API_KEY`
- [ ] Virtual environment is activated
- [ ] Database exists (`db.sqlite3` file present)
- [ ] ChromaDB populated (`python manage.py list_templates` shows templates)
- [ ] Backend server running on port 8000 (Terminal 1)
- [ ] HTTP server running on port 8080 (Terminal 2)
- [ ] Valid JWT token configured in `game_viewer.html`
- [ ] Accessing via `http://localhost:8080/game_viewer.html` (not `file://`)
- [ ] At least one game generated (status: 'ready')

## Quick Reference Commands

```bash
# Get authentication token
python get_auth_token.py

# Start backend
python manage.py runserver

# Start game viewer web server
python -m http.server 8080

# Generate test game
python test_rag_api.py

# Check ChromaDB templates
python manage.py list_templates

# View database games (Django shell)
python manage.py shell
>>> from apps.games.models import UserGame
>>> UserGame.objects.all()
```

## File Structure

```
game-learn-backend/
├── game_viewer.html           # Frontend (open via http://localhost:8080)
├── get_auth_token.py          # Generate JWT tokens
├── setup_and_run.sh           # Automated setup script
├── test_rag_api.py           # Test game generation
├── QUICKSTART.md             # 5-minute setup guide
├── SETUP_INSTRUCTIONS.md     # Detailed setup guide
├── README_GAME_VIEWER.md     # This file
├── .env                       # Your API keys (create this!)
├── .env.example              # Template
├── db.sqlite3                # Database (created by migrate)
├── data/chroma_db/           # Vector database
└── apps/
    └── games/
        └── api/views.py      # Game API endpoints
```

## Next Steps

1. Read `QUICKSTART.md` for the fastest setup
2. Run through the setup steps above
3. Generate a test game with `python test_rag_api.py`
4. Load the game in your browser
5. If you encounter issues, check the error messages - they now include helpful hints!

## Need More Help?

- Check browser console (F12) for detailed error messages
- Check Django terminal for backend errors
- Verify all checklist items above
- Review `SETUP_INSTRUCTIONS.md` for troubleshooting

The game viewer now has improved error messages that will guide you if something goes wrong!
