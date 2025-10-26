# Game Viewer Setup & Usage

## Quick Start

### 1. Setup (One-time)
```bash
# Add your OpenAI API key
cp .env.example .env
# Edit .env: OPENAI_API_KEY=sk-your-key-here

# Activate virtual environment and setup database
source venv/bin/activate
python manage.py migrate
python manage.py populate_templates

# Get authentication token
python get_auth_token.py
# Copy the ACCESS TOKEN
```

### 2. Update game_viewer.html
```javascript
// Line 114 - Replace with your token from step 1
const TOKEN = 'your-actual-token-here';
```

### 3. Run Servers
```bash
# Terminal 1 - Backend
python manage.py runserver

# Terminal 2 - Game Viewer
python -m http.server 8080
```

### 4. Use It!
Open browser: `http://localhost:8080/game_viewer.html`

**Features:**
- ✨ **Generate games** - Enter a prompt and click "Generate Game"
- 📋 **List games** - See all your generated games
- 🎮 **Play games** - Load and play any game

## What You Can Do

### Generate a New Game
1. Enter a prompt like: "Create a space shooter with asteroids"
2. Click **"✨ Generate Game"**
3. Wait 10-30 seconds (RAG + GPT takes time)
4. Game appears in your list automatically

### Play an Existing Game
1. Click **"📋 List My Games"**
2. Click on a game to select it
3. Click **"🎮 Load Game"**
4. Click **"▶️ Play Game"**

## Troubleshooting

| Error | Solution |
|-------|----------|
| "Configure token" warning | Run `python get_auth_token.py` and update game_viewer.html |
| "Cannot connect to backend" | Start backend: `python manage.py runserver` |
| "401 Unauthorized" | Token expired - run `python get_auth_token.py` again |
| CORS errors | Use `http://localhost:8080/game_viewer.html` (not `file://`) |

## How It Works

```
User enters prompt → game_viewer.html → Django API → RAG (ChromaDB) → OpenAI GPT
                                                                            ↓
User plays game ← game_viewer.html ← Database ← Generated PixiJS code ← GPT
```

You can now generate and play games entirely from the web interface!
