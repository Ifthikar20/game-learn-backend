# Game Viewer Setup Instructions

## Problem

When opening `game_viewer.html` directly, you encounter these issues:
- Backend server not running → API requests fail
- No .env file → OpenAI API key missing
- Database not initialized → No games to load
- CORS errors → `file://` protocol not allowed
- Missing auth token → Authentication fails

## Solution

Follow these steps to get the game viewer working:

### Step 1: Set up Environment Variables

1. Copy the example .env file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your OpenAI API key:
   ```bash
   OPENAI_API_KEY=sk-your-actual-openai-api-key-here
   ```

### Step 2: Initialize Database

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run migrations
python manage.py migrate

# Create a superuser (for admin access)
python manage.py createsuperuser
# Username: admin
# Email: admin@example.com
# Password: (choose a password)
```

### Step 3: Populate ChromaDB with Templates

```bash
# Load game templates into ChromaDB for RAG
python manage.py populate_templates
```

### Step 4: Start the Backend Server

```bash
# Make sure you're in the virtual environment
python manage.py runserver
```

The server will start at `http://localhost:8000`

### Step 5: Get Your Authentication Token

Open a new terminal and run:

```bash
# Create a test user and get token
python manage.py shell

# In the shell, run:
from apps.users.models import User
from rest_framework_simplejwt.tokens import RefreshToken

# Create or get user
user, created = User.objects.get_or_create(
    email='test@example.com',
    defaults={'username': 'testuser'}
)
if created:
    user.set_password('testpass123')
    user.save()

# Get token
refresh = RefreshToken.for_user(user)
access_token = str(refresh.access_token)
print(f"\n{'='*60}")
print(f"ACCESS TOKEN (copy this):")
print(f"{'='*60}")
print(access_token)
print(f"{'='*60}\n")
```

### Step 6: Update game_viewer.html

1. Open `game_viewer.html` in a text editor
2. Find this line (around line 114):
   ```javascript
   const TOKEN = 'YOUR_TOKEN_HERE';
   ```
3. Replace `YOUR_TOKEN_HERE` with your actual access token from Step 5

### Step 7: Serve the HTML File (IMPORTANT!)

**DON'T** open the file directly with `open game_viewer.html`!

Instead, serve it through a web server to avoid CORS issues:

```bash
# Option 1: Python HTTP server (easiest)
python -m http.server 8080

# Option 2: Node.js http-server (if you have Node)
npx http-server -p 8080
```

Then open your browser to: `http://localhost:8080/game_viewer.html`

### Step 8: Generate a Game

1. First, generate a game using the API:
   ```bash
   # In a new terminal
   curl -X POST http://localhost:8000/api/games/generate/ \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Create a simple platformer game with a player that can jump"}'
   ```

2. Or use the test script:
   ```bash
   python test_rag_api.py
   ```

### Step 9: Load the Game

1. In the game viewer at `http://localhost:8080/game_viewer.html`
2. Click "List My Games" to see your games
3. Click on a game to load it, or paste the game ID
4. Click "Load Game"
5. Click "Play Game" to start

## Quick Test Script

I've also created `run_game_viewer.sh` to automate all of this:

```bash
chmod +x run_game_viewer.sh
./run_game_viewer.sh
```

## Troubleshooting

### CORS Errors
- Make sure you're accessing via `http://localhost:8080`, NOT `file://`
- Check that the backend server is running on port 8000

### 401 Unauthorized
- Your access token may have expired (tokens last 60 minutes)
- Generate a new token using Step 5

### Game Not Loading
- Check browser console (F12) for errors
- Verify the game status is 'ready' (not 'generating' or 'failed')
- Check backend logs for errors

### "Game is generating..."
- RAG + GPT generation takes 10-30 seconds
- Wait and then refresh the game list
