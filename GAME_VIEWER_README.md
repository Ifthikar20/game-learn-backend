# Game Viewer - Quick Start Guide

## Setup (One-time)

### 1. Install & Configure
```bash
# Add your OpenAI API key
cp .env.example .env
# Edit .env and add: OPENAI_API_KEY=sk-your-key-here

# Activate virtual environment and setup database
source venv/bin/activate
python manage.py migrate
python manage.py populate_templates
```

### 2. Create a User Account
```bash
# Run this to create test@example.com account
python get_auth_token.py
# Just press Enter to use defaults (test@example.com / testpass123)
```

### 3. Run Servers
```bash
# Terminal 1 - Backend API
python manage.py runserver

# Terminal 2 - Game Viewer
python -m http.server 8080
```

### 4. Open and Login
Open browser: **`http://localhost:8080/game_viewer.html`**

Login with:
- Email: `test@example.com`
- Password: `testpass123`

**That's it!** No need to copy/paste tokens - it handles authentication automatically!

---

## How to Use

### Generate a Game
1. Type a description: *"Create a space shooter where I dodge asteroids"*
2. Click **"✨ Generate Game"**
3. Wait 10-30 seconds
4. Game auto-loads when ready
5. Click **"▶️ Play Game"**

### Play Existing Games
1. Click **"📋 List My Games"**
2. Click on any game
3. Click **"▶️ Play Game"**

---

## Features

✅ **Auto Login** - Enter email/password once, token saved automatically
✅ **Generate Games** - Describe what you want, RAG + GPT creates it
✅ **Play Games** - Load and play directly in the browser
✅ **Session Management** - Stay logged in, auto-logout when token expires

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Cannot connect to backend" | Start server: `python manage.py runserver` |
| "Invalid email or password" | Run `python get_auth_token.py` to create account |
| "Session expired" | Just login again - token lasts 60 minutes |
| Blank page | Use `http://localhost:8080/game_viewer.html` not `file://` |

---

## How It Works

```
You login → Token saved in browser automatically
    ↓
Type game prompt → RAG finds best templates → GPT generates code
    ↓
Game created → Auto-loads → Play!
```

**No token copy/paste needed - it's all automatic!** 🎉
