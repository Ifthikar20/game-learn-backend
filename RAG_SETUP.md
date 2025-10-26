# RAG-Powered PixiJS Game Generation Setup

This document explains how the RAG (Retrieval-Augmented Generation) system works for generating PixiJS games.

## Overview

The backend now uses a sophisticated RAG system that:
1. Stores PixiJS game templates in a ChromaDB vector database
2. Uses semantic search to find relevant templates based on user prompts
3. Customizes templates using OpenAI GPT models
4. Generates complete, playable PixiJS games ready for frontend rendering

## Architecture

```
User Prompt
    ↓
[RAG Retriever]
    ↓
[Semantic Search in ChromaDB]
    ↓
[Retrieve Relevant Templates]
    ↓
[PixiJS Generator + OpenAI]
    ↓
[Customized Game Code + Data]
    ↓
Frontend Renders Game
```

## Components

### 1. ChromaDB Manager (`apps/ai_engine/rag/chroma_manager.py`)
- Manages vector database for game templates
- Handles adding, searching, and retrieving templates
- Uses sentence-transformers for embeddings

### 2. RAG Retriever (`apps/ai_engine/rag/retriever.py`)
- Performs semantic search for relevant templates
- Detects game type from user prompts
- Formats template context for LLM

### 3. PixiJS Generator (`apps/ai_engine/generators/pixijs_generator.py`)
- Main game generation engine
- Combines RAG retrieval with OpenAI customization
- Falls back to template-based generation if OpenAI unavailable
- Supports multiple game types: quiz, platformer, puzzle, arcade

## Setup Instructions

### 1. Install Dependencies

All required dependencies are in `requirements.txt`:
```bash
pip install -r requirements.txt
```

Key packages:
- `chromadb==0.4.22` - Vector database
- `sentence-transformers==2.3.1` - Embeddings
- `langchain==0.1.7` - LLM orchestration
- `openai==1.12.0` - OpenAI API

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Required
SECRET_KEY=your-django-secret-key
OPENAI_API_KEY=your-openai-api-key

# Optional
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CHROMA_PERSIST_DIRECTORY=./data/chroma_db
```

### 3. Run Migrations

```bash
python manage.py migrate
```

### 4. Populate Game Templates

This is a critical step that populates ChromaDB with PixiJS game templates:

```bash
python manage.py populate_templates
```

This command adds 4 pre-built templates:
- **Educational Quiz** - Multiple choice questions with scoring
- **Simple Platformer** - Side-scrolling platform game with physics
- **Color Match Puzzle** - Tile matching game
- **Arcade Clicker** - Fast-paced clicking game

### 5. Start the Server

```bash
python manage.py runserver
```

## API Usage

### Generate a Game

**Endpoint:** `POST /api/games/generate/`

**Headers:**
```
Authorization: Bearer <your-jwt-token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "prompt": "Create a quiz about Python programming"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid-here",
    "title": "Educational Quiz - Python Programming",
    "description": "A quiz game about Python programming",
    "status": "ready",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### Play a Game

**Endpoint:** `GET /api/games/<game_id>/play/`

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid-here",
    "title": "Educational Quiz - Python Programming",
    "pixijs_code": "// Complete PixiJS game code",
    "game_data": {
      "questions": [
        {
          "question": "What is Python?",
          "answers": ["A", "B", "C", "D"],
          "correctIndex": 0
        }
      ]
    }
  }
}
```

## Frontend Integration

The frontend should:

1. **Create a container** for the game:
```html
<div id="game-container"></div>
```

2. **Inject game data and code**:
```javascript
// Fetch game from API
const response = await fetch(`/api/games/${gameId}/play/`, {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const { data } = await response.json();

// Inject GAME_DATA as global variable
window.GAME_DATA = data.game_data;

// Load PixiJS library
const pixiScript = document.createElement('script');
pixiScript.src = 'https://cdn.jsdelivr.net/npm/pixi.js@7/dist/pixi.min.js';
pixiScript.onload = () => {
  // Execute game code
  const gameScript = document.createElement('script');
  gameScript.textContent = data.pixijs_code;
  document.body.appendChild(gameScript);
};
document.head.appendChild(pixiScript);
```

3. **Handle game rendering**:
The PixiJS code automatically appends the canvas to `document.body`. You can modify the generated code to append to a specific container if needed.

## Game Types Supported

### Quiz
- Multiple choice questions
- Score tracking
- Visual feedback
- Keywords: quiz, question, trivia, test, exam

### Platformer
- Side-scrolling movement
- Jump mechanics
- Platform collisions
- Gravity physics
- Keywords: platform, jump, run, side-scroller

### Puzzle
- Tile matching
- Grid-based gameplay
- Color matching
- Keywords: puzzle, match, tile, logic

### Arcade/Clicker
- Fast-paced clicking
- Timed gameplay
- Score challenges
- Keywords: arcade, clicker, fast-paced

## RAG System Details

### How Template Matching Works

1. **User submits prompt**: "Create a quiz about math"

2. **Embedding generation**: The prompt is converted to a vector embedding using sentence-transformers

3. **Semantic search**: ChromaDB finds the most similar templates based on vector similarity

4. **Game type detection**: Keywords in the prompt are analyzed to determine game type

5. **Template retrieval**: Top 2 most relevant templates are retrieved

6. **OpenAI customization**: The templates are sent to GPT-3.5 with instructions to customize based on the user's specific requirements

7. **Code generation**: Complete PixiJS code and game data are returned

### Fallback Mechanism

If RAG fails or no templates are found:
1. System falls back to basic quiz template
2. Generic game data is generated
3. User still receives a functional game

## Adding New Templates

You can add custom templates programmatically:

```python
from apps.ai_engine.rag.chroma_manager import ChromaManager

chroma = ChromaManager()

chroma.add_template(
    template_id='my_custom_game',
    name='My Custom Game',
    description='A detailed description of the game mechanics',
    code='// Your PixiJS code here',
    game_type='puzzle',  # quiz, platformer, puzzle, arcade, etc.
    tags=['tag1', 'tag2', 'tag3']
)
```

## Performance Considerations

- **ChromaDB Persistence**: Templates are stored persistently in `data/chroma_db/`
- **Embedding Model**: First run downloads `all-MiniLM-L6-v2` model (~80MB)
- **OpenAI API**: Uses GPT-3.5-turbo (fast and cost-effective)
- **Caching**: ChromaDB maintains efficient vector indexes

## Troubleshooting

### Templates not found
```bash
# Re-populate templates
python manage.py populate_templates
```

### OpenAI errors
- Check `OPENAI_API_KEY` in `.env`
- System falls back to template-based generation without OpenAI
- Set `use_openai=False` in PixiJSGenerator to skip OpenAI

### ChromaDB errors
- Ensure `data/chroma_db/` directory has write permissions
- Delete and recreate: `rm -rf data/chroma_db && python manage.py populate_templates`

### Import errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: Python 3.11+ recommended

## Future Enhancements

- [ ] Async game generation with Celery
- [ ] User-uploaded custom templates
- [ ] Template versioning and A/B testing
- [ ] Multi-language game support
- [ ] Advanced game types (multiplayer, RPG, etc.)
- [ ] Template quality ratings and feedback
- [ ] Fine-tuned models for game generation

## License

This RAG system is part of the PlayStudy educational platform.
