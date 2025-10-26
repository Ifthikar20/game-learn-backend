"""
PixiJS Game Generator using RAG and OpenAI
Generates customized PixiJS games based on user prompts and retrieved templates
"""
import os
import json
from typing import Dict, Any, Optional
from django.conf import settings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from apps.ai_engine.rag.retriever import RAGRetriever


class PixiJSGenerator:
    """
    Generates PixiJS games using Retrieval-Augmented Generation
    Combines template retrieval with LLM customization
    """

    def __init__(self, use_openai: bool = True):
        """
        Initialize the generator

        Args:
            use_openai: Whether to use OpenAI for customization (falls back to template if False)
        """
        self.retriever = RAGRetriever()
        self.use_openai = use_openai and bool(getattr(settings, 'OPENAI_API_KEY', ''))

        if self.use_openai:
            self.llm = ChatOpenAI(
                model="gpt-4",  # Use GPT-4 for better creativity
                temperature=0.9,
                api_key=getattr(settings, 'OPENAI_API_KEY')
            )
            print(f"✓ OpenAI GPT-4 enabled for game generation")

    def generate_game(self, user_prompt: str) -> Dict[str, Any]:
        """
        Generate a complete PixiJS game based on user prompt

        NEW APPROACH: Direct GPT generation from scratch (no RAG templates)

        Args:
            user_prompt: User's description of desired game

        Returns:
            Dictionary containing title, description, pixijs_code, and game_data
        """
        if self.use_openai:
            try:
                print(f"🤖 Generating game directly from GPT-4 for: '{user_prompt}'")
                print(f"🚀 Creating from scratch (no templates)")
                result = self._generate_direct_from_gpt(user_prompt)
                print(f"✅ Generated game: {result.get('title', 'Unknown')}")
                return result
            except Exception as e:
                print(f"❌ GPT generation failed: {str(e)}")
                print(f"⚠️  Falling back to simple template")
                return self._generate_fallback_quiz(user_prompt)
        else:
            print(f"⚠️  OpenAI disabled, using fallback")
            return self._generate_fallback_quiz(user_prompt)

    def _generate_direct_from_gpt(self, user_prompt: str) -> Dict[str, Any]:
        """
        Generate game directly from GPT without using any templates

        Args:
            user_prompt: User's game description

        Returns:
            Generated game data
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert PixiJS v7 game developer. Create COMPLETE, DETAILED, PLAYABLE games from scratch.

CRITICAL CODE STRUCTURE - FOLLOW THIS EXACTLY:

1. ALWAYS wrap code in IIFE: (async () => {{ ... }})();
2. ALWAYS initialize PIXI.Application properly
3. ALWAYS use global PIXI object (NO imports)
4. ALWAYS append to game-container div
5. ALWAYS include game loop with app.ticker.add()

REQUIRED GAME STRUCTURE:
```javascript
(async () => {{
  // ===== 1. SETUP =====
  const app = new PIXI.Application({{
    width: 800,
    height: 600,
    backgroundColor: 0x1099bb,
    antialias: true
  }});

  const container = document.getElementById('game-container');
  if (container) {{
    container.appendChild(app.view);
  }} else {{
    document.body.appendChild(app.view);
  }}

  // ===== 2. GAME STATE =====
  const gameState = {{
    score: 0,
    gameOver: false,
    paused: false
  }};

  // ===== 3. GRAPHICS OBJECTS =====
  const player = new PIXI.Graphics();
  const ui = new PIXI.Container();

  // Draw player (example - make it detailed!)
  player.beginFill(0xFF0000);
  player.drawRect(0, 0, 50, 50);
  player.endFill();
  player.x = 100;
  player.y = 100;
  app.stage.addChild(player);

  // ===== 4. UI ELEMENTS =====
  const scoreText = new PIXI.Text('Score: 0', {{
    fontFamily: 'Arial',
    fontSize: 24,
    fill: 0xFFFFFF
  }});
  scoreText.x = 10;
  scoreText.y = 10;
  app.stage.addChild(scoreText);

  // ===== 5. GAME FUNCTIONS =====
  function resetGame() {{
    gameState.score = 0;
    gameState.gameOver = false;
    // Reset positions, etc.
  }}

  function updateScore(points) {{
    gameState.score += points;
    scoreText.text = 'Score: ' + gameState.score;
  }}

  // ===== 6. INPUT HANDLING =====
  const keys = {{}};
  window.addEventListener('keydown', (e) => {{
    keys[e.key] = true;
  }});
  window.addEventListener('keyup', (e) => {{
    keys[e.key] = false;
  }});

  // ===== 7. GAME LOOP =====
  app.ticker.add((delta) => {{
    if (gameState.gameOver || gameState.paused) return;

    // Update player movement
    if (keys['ArrowRight']) player.x += 5 * delta;
    if (keys['ArrowLeft']) player.x -= 5 * delta;

    // Update game logic
    // Check collisions
    // Update score
  }});

  // ===== 8. START GAME =====
  resetGame();
}})();
```

REQUIREMENTS:
✅ Complete game mechanics (physics, collisions, scoring)
✅ Detailed graphics (shapes, colors, animations)
✅ Full UI (score, instructions, game over screen)
✅ Input handling (keyboard/mouse)
✅ Win/lose conditions
✅ Restart functionality
✅ Smooth animations

Make games FUN, COMPLETE, and DETAILED!"""),
            ("user", """Create a COMPLETE PixiJS game for this request:

"{user_prompt}"

CRITICAL INSTRUCTIONS:
1. Follow the EXACT structure from the system template
2. Include ALL 8 sections: Setup, Game State, Graphics, UI, Functions, Input, Game Loop, Start
3. Use the gameState object pattern for all state variables
4. Make graphics detailed (not just rectangles - draw actual shapes!)
5. Include complete game loop with proper physics
6. Add restart functionality (press R to restart)
7. Include game over screen with instructions

STRUCTURE YOUR CODE LIKE THIS:
- Section 1: App setup + canvas append
- Section 2: gameState object with all variables
- Section 3: Create and draw all graphics objects
- Section 4: UI elements (score, instructions, game over)
- Section 5: Game functions (reset, checkCollision, etc.)
- Section 6: Input handlers (keyboard/mouse)
- Section 7: Game loop with app.ticker.add()
- Section 8: Call resetGame() to start

Return your response in this EXACT format:

TITLE:
[One-line game title]

DESCRIPTION:
[One-line description of what makes it fun]

CODE_START
(async () => {{
  // ===== 1. SETUP =====
  const app = new PIXI.Application({{...}});
  // ... rest of structured code following the 8-section template
}})();
CODE_END

IMPORTANT: Code must be complete, syntactically valid JavaScript with no placeholders!""")
        ])

        # Generate with OpenAI
        chain = prompt | self.llm
        response = chain.invoke({
            "user_prompt": user_prompt
        })

        # Parse response using delimiter format
        try:
            content = response.content.strip()

            # Extract title (between TITLE: and DESCRIPTION:)
            title_match = content.find('TITLE:')
            desc_match = content.find('DESCRIPTION:')
            code_start = content.find('CODE_START')
            code_end = content.find('CODE_END')

            if title_match == -1 or desc_match == -1 or code_start == -1 or code_end == -1:
                raise ValueError("Response doesn't match expected delimiter format")

            # Extract each section
            title = content[title_match + 6:desc_match].strip()
            description = content[desc_match + 12:code_start].strip()
            pixijs_code = content[code_start + 10:code_end].strip()

            # Validate the extracted code
            if not pixijs_code or len(pixijs_code) < 50:
                raise ValueError(f"Generated code is too short ({len(pixijs_code)} chars)")

            # Check for basic structure
            if 'PIXI.Application' not in pixijs_code:
                raise ValueError("Code missing PIXI.Application initialization")

            if 'game-container' not in pixijs_code and 'document.body' not in pixijs_code:
                raise ValueError("Code missing canvas append logic")

            print(f"✓ Successfully parsed game: {title}")
            print(f"✓ Code length: {len(pixijs_code)} characters")
            print(f"✓ Code preview (first 200 chars): {pixijs_code[:200]}")

            return {
                'title': title,
                'description': description,
                'pixijs_code': pixijs_code,
                'game_data': {}
            }

        except Exception as e:
            print(f"Failed to parse GPT response: {str(e)}")
            print(f"Response content: {response.content[:500]}")
            raise

    def _generate_from_template(
        self,
        user_prompt: str,
        template: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate game using template with basic customization

        Args:
            user_prompt: User's game description
            template: Template to use

        Returns:
            Generated game data
        """
        game_type = template['game_type']

        # Generate game data based on type
        if game_type == 'quiz':
            game_data = self._generate_quiz_data(user_prompt)
        elif game_type == 'platformer':
            game_data = self._generate_platformer_data(user_prompt)
        elif game_type == 'puzzle':
            game_data = self._generate_puzzle_data(user_prompt)
        else:
            game_data = {'theme': user_prompt}

        return {
            'title': f"{template['name']} - {user_prompt[:30]}",
            'description': f"A {game_type} game about {user_prompt}",
            'pixijs_code': template['code'],
            'game_data': game_data
        }

    def _generate_quiz_data(self, topic: str) -> Dict[str, Any]:
        """Generate quiz game data"""
        return {
            'questions': [
                {
                    'question': f'What is an important concept in {topic}?',
                    'answers': ['Answer A', 'Answer B', 'Answer C', 'Answer D'],
                    'correctIndex': 0
                },
                {
                    'question': f'Which statement about {topic} is true?',
                    'answers': ['Statement A', 'Statement B', 'Statement C', 'Statement D'],
                    'correctIndex': 1
                },
                {
                    'question': f'How does {topic} work?',
                    'answers': ['Option A', 'Option B', 'Option C', 'Option D'],
                    'correctIndex': 2
                }
            ]
        }

    def _generate_platformer_data(self, theme: str) -> Dict[str, Any]:
        """Generate platformer game data"""
        return {
            'theme': theme,
            'levels': [
                {
                    'name': 'Level 1',
                    'platforms': [
                        {'x': 0, 'y': 500, 'width': 800, 'height': 20},
                        {'x': 100, 'y': 400, 'width': 200, 'height': 20},
                        {'x': 400, 'y': 300, 'width': 200, 'height': 20}
                    ],
                    'enemies': [
                        {'x': 200, 'y': 380, 'speed': 1}
                    ]
                }
            ]
        }

    def _generate_puzzle_data(self, theme: str) -> Dict[str, Any]:
        """Generate puzzle game data"""
        return {
            'theme': theme,
            'grid_size': 4,
            'colors': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F']
        }

    def _generate_fallback_quiz(self, user_prompt: str) -> Dict[str, Any]:
        """
        Fallback quiz generator when no templates are available

        Args:
            user_prompt: User's game description

        Returns:
            Basic quiz game
        """
        # Use the simple quiz template from SimpleGameGenerator
        pixijs_code = """
// Simple Quiz Game
const app = new PIXI.Application({
    width: 800,
    height: 600,
    backgroundColor: 0x1099bb
});
document.body.appendChild(app.view);

const questions = GAME_DATA.questions;
let currentQuestion = 0;
let score = 0;

// Create UI
const questionText = new PIXI.Text('', {
    fontFamily: 'Arial',
    fontSize: 24,
    fill: 0xffffff,
    wordWrap: true,
    wordWrapWidth: 700
});
questionText.position.set(50, 50);
app.stage.addChild(questionText);

const scoreText = new PIXI.Text('Score: 0', {
    fontFamily: 'Arial',
    fontSize: 20,
    fill: 0xffffff
});
scoreText.position.set(650, 20);
app.stage.addChild(scoreText);

// Answer buttons
const buttons = [];
for (let i = 0; i < 4; i++) {
    const button = createButton(50, 200 + i * 80, 700, 60);
    buttons.push(button);
    app.stage.addChild(button.container);
}

function createButton(x, y, width, height) {
    const container = new PIXI.Container();
    container.position.set(x, y);

    const bg = new PIXI.Graphics();
    bg.beginFill(0x3498db);
    bg.drawRoundedRect(0, 0, width, height, 10);
    bg.endFill();
    bg.interactive = true;
    bg.buttonMode = true;

    const text = new PIXI.Text('', {
        fontFamily: 'Arial',
        fontSize: 18,
        fill: 0xffffff
    });
    text.anchor.set(0.5);
    text.position.set(width / 2, height / 2);

    container.addChild(bg);
    container.addChild(text);

    return { container, bg, text };
}

function loadQuestion() {
    if (currentQuestion >= questions.length) {
        endGame();
        return;
    }

    const q = questions[currentQuestion];
    questionText.text = `Q${currentQuestion + 1}: ${q.question}`;

    q.answers.forEach((answer, index) => {
        const button = buttons[index];
        button.text.text = answer;
        button.bg.removeAllListeners();
        button.bg.on('pointerdown', () => answerQuestion(index));
    });
}

function answerQuestion(answerIndex) {
    const q = questions[currentQuestion];
    if (answerIndex === q.correctIndex) {
        score += 10;
        scoreText.text = `Score: ${score}`;
    }

    currentQuestion++;
    loadQuestion();
}

function endGame() {
    questionText.text = `Game Over! Final Score: ${score}/${questions.length * 10}`;
    buttons.forEach(button => button.container.visible = false);
}

// Start game
loadQuestion();
"""

        game_data = self._generate_quiz_data(user_prompt)

        return {
            'title': f'Quiz: {user_prompt[:50]}',
            'description': f'A quiz game about {user_prompt}',
            'pixijs_code': pixijs_code,
            'game_data': game_data
        }
