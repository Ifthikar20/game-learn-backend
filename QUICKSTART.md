# Quick Start Guide - Game Viewer

This guide will get you up and running in 5 minutes!

## The Problem You're Experiencing

When you run `open game_viewer.html`, you see the page but games don't load because:

1. **Backend server isn't running** → API requests fail
2. **No authentication token** → Requests are unauthorized
3. **CORS issues** → Opening file directly causes security errors
4. **Missing OpenAI key** → RAG model can't generate games

## Quick Fix (5 Steps)

### 1. Set Your OpenAI API Key

```bash
# Create .env file
cp .env.example .env

# Edit .env and set your key:
# OPENAI_API_KEY=sk-your-actual-key-here
```

### 2. Initialize Database

```bash
# Activate virtual environment
source venv/bin/activate

# Run migrations
python manage.py migrate

# Populate game templates for RAG
python manage.py populate_templates
```

### 3. Get Authentication Token

```bash
# Run the token generator
python get_auth_token.py

# Follow prompts (can use defaults):
# - Email: test@example.com
# - Username: testuser
# - Password: testpass123

# Copy the ACCESS TOKEN that's printed
```

### 4. Update game_viewer.html

```bash
# Open game_viewer.html in your editor
# Find line 114:
const TOKEN = 'YOUR_TOKEN_HERE';

# Replace with your actual token:
const TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGc...';  # Your token from step 3
```

### 5. Start Everything

**Terminal 1 - Backend Server:**
```bash
source venv/bin/activate
python manage.py runserver
```

**Terminal 2 - Web Server for HTML:**
```bash
python -m http.server 8080
```

**Browser:**
Open `http://localhost:8080/game_viewer.html`

## Usage

### Generate a Game

**Option 1: Using the test script**
```bash
# Terminal 3
python test_rag_api.py
```

**Option 2: Using curl**
```bash
curl -X POST http://localhost:8000/api/games/generate/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a simple space shooter game"}'
```

### Play the Game

1. Go to `http://localhost:8080/game_viewer.html`
2. Click **"📋 List My Games"**
3. Click on a game to auto-fill the ID
4. Click **"🎮 Load Game"**
5. Click **"▶️ Play Game"**

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Failed to fetch" error | Backend not running → Run `python manage.py runserver` |
| "401 Unauthorized" | Token missing/expired → Run `python get_auth_token.py` again |
| CORS errors | Using file:// → Must use `http://localhost:8080/game_viewer.html` |
| "Game is generating..." forever | Check backend terminal for errors, verify OpenAI key |
| Blank page | Check browser console (F12) for JavaScript errors |

## What Each Component Does

- **Django Backend** (port 8000): API server that handles game generation using RAG + GPT
- **HTTP Server** (port 8080): Serves the game_viewer.html file (avoids CORS issues)
- **ChromaDB**: Vector database that stores game templates for RAG retrieval
- **game_viewer.html**: Frontend that loads and plays PixiJS games

## Architecture Flow

```
User Input → game_viewer.html → Backend API → RAG Retriever → ChromaDB
                                      ↓
                                  OpenAI GPT
                                      ↓
                              PixiJS Game Code
                                      ↓
                              game_viewer.html (plays game)
```

## Need Help?

Check `SETUP_INSTRUCTIONS.md` for detailed troubleshooting and advanced configuration.
