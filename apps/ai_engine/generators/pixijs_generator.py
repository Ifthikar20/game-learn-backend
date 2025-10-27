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
        Generate a complete PixiJS game based on user prompt with retry logic

        NEW APPROACH: Direct GPT generation with validation and retry

        Args:
            user_prompt: User's description of desired game

        Returns:
            Dictionary containing title, description, pixijs_code, and game_data
        """
        if self.use_openai:
            print(f"🤖 Generating game directly from GPT-4 for: '{user_prompt}'")
            print(f"🚀 Creating from scratch with validation and retry")

            max_attempts = 3
            previous_errors = None

            for attempt in range(1, max_attempts + 1):
                try:
                    print(f"📝 Attempt {attempt}/{max_attempts}")
                    result = self._generate_direct_from_gpt(
                        user_prompt,
                        attempt=attempt,
                        previous_errors=previous_errors
                    )

                    # Validate the generated code
                    validation_errors = self._validate_game_code(result['pixijs_code'])

                    if not validation_errors:
                        print(f"✅ Generated valid game: {result.get('title', 'Unknown')}")
                        return result
                    else:
                        print(f"⚠️  Validation failed on attempt {attempt}:")
                        for error in validation_errors:
                            print(f"   - {error}")

                        if attempt < max_attempts:
                            print(f"🔄 Retrying with error feedback...")
                            # Store errors for next attempt
                            previous_errors = validation_errors
                        else:
                            print(f"❌ Max attempts reached, falling back to template")
                            return self._generate_fallback_quiz(user_prompt)

                except Exception as e:
                    print(f"❌ Generation attempt {attempt} failed: {str(e)}")
                    if attempt == max_attempts:
                        print(f"⚠️  All attempts failed, falling back to simple template")
                        return self._generate_fallback_quiz(user_prompt)
                    else:
                        # On retry, pass the exception as an error
                        previous_errors = [f"Exception: {str(e)}"]
        else:
            print(f"⚠️  OpenAI disabled, using fallback")
            return self._generate_fallback_quiz(user_prompt)

    def _validate_game_code(self, code: str) -> list:
        """
        Validate the generated JavaScript code for common issues

        Args:
            code: JavaScript code to validate

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Basic structure checks
        if not code or len(code) < 100:
            errors.append(f"Code too short ({len(code)} chars) - needs more content")

        if 'PIXI.Application' not in code:
            errors.append("Missing PIXI.Application initialization")

        if 'new PIXI.Application' not in code:
            errors.append("PIXI.Application not properly instantiated with 'new'")

        if 'game-container' not in code and 'document.body' not in code:
            errors.append("Missing canvas append logic (should append to game-container or body)")

        if 'app.ticker.add' not in code:
            errors.append("Missing game loop (app.ticker.add)")

        if '(async () =>' not in code and '(async()=>' not in code:
            errors.append("Code not wrapped in async IIFE")

        # Check for balanced braces
        open_braces = code.count('{')
        close_braces = code.count('}')
        if open_braces != close_braces:
            errors.append(f"Unbalanced braces: {open_braces} open, {close_braces} close")

        # Check for balanced parentheses
        open_parens = code.count('(')
        close_parens = code.count(')')
        if open_parens != close_parens:
            errors.append(f"Unbalanced parentheses: {open_parens} open, {close_parens} close")

        # Check for common syntax errors
        if '})();' not in code:
            errors.append("Missing IIFE closing: })();")

        # Check for required game elements
        if 'PIXI.Graphics' not in code and 'PIXI.Sprite' not in code:
            errors.append("No game graphics created (missing PIXI.Graphics or PIXI.Sprite)")

        if 'PIXI.Text' not in code:
            errors.append("No UI text elements (missing PIXI.Text for score/instructions)")

        # Check for empty or placeholder code
        if '// Your complete game code' in code or '...' in code:
            errors.append("Code contains placeholders - needs actual implementation")

        return errors

    def _generate_direct_from_gpt(self, user_prompt: str, attempt: int = 1, previous_errors: list = None) -> Dict[str, Any]:
        """
        Generate game directly from GPT without using any templates

        Args:
            user_prompt: User's game description
            attempt: Current attempt number
            previous_errors: List of validation errors from previous attempt

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

Make games FUN, COMPLETE, and DETAILED!""")
        ])

        # Build user message with optional error feedback
        user_message_parts = [f"Create a COMPLETE PixiJS game for this request:\n\n\"{user_prompt}\"\n"]

        if previous_errors and len(previous_errors) > 0:
            user_message_parts.append(f"\n⚠️ PREVIOUS ATTEMPT HAD THESE ERRORS - FIX THEM:\n")
            for i, error in enumerate(previous_errors, 1):
                user_message_parts.append(f"{i}. {error}\n")
            user_message_parts.append("\nMake sure to fix ALL the errors listed above!\n")

        user_message_parts.append("""
CRITICAL INSTRUCTIONS:
1. Follow the EXACT structure from the system template
2. Include ALL 8 sections: Setup, Game State, Graphics, UI, Functions, Input, Game Loop, Start
3. Use the gameState object pattern for all state variables
4. Make graphics detailed (not just rectangles - draw actual shapes!)
5. Include complete game loop with proper physics
6. Add restart functionality (press R to restart)
7. Include game over screen with instructions

Return your response in this EXACT format:

TITLE:
[One-line game title]

DESCRIPTION:
[One-line description of what makes it fun]

CODE_START
(async () => {{
  // ===== 1. SETUP =====
  const app = new PIXI.Application({{width: 800, height: 600, backgroundColor: 0x1099bb}});
  const container = document.getElementById('game-container');
  if (container) {{ container.appendChild(app.view); }} else {{ document.body.appendChild(app.view); }}

  // ... rest of complete code following the 8-section template
}})();
CODE_END

IMPORTANT: Code must be complete, syntactically valid JavaScript with no placeholders!
""")

        user_message = "".join(user_message_parts)

        # Generate with OpenAI - invoke with user_prompt
        chain = prompt | self.llm
        response = chain.invoke({"user_prompt": user_message})

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
