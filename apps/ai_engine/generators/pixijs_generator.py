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
            ("system", """You are an expert PixiJS v8 game developer. Create complete, playable games from scratch based on user requests.

Your task: Analyze the request and create a FULLY FUNCTIONAL PixiJS game with appropriate mechanics.

Examples:

"flying ship game" →
- Spaceship that moves/rotates
- Obstacles to avoid
- Space background with stars
- Tap/click to thrust upward
- Gravity pulling down
- Scrolling obstacles
- Score tracking

"car racing game" →
- 3-lane system
- Player car switches lanes (arrow keys)
- Enemy cars spawn and scroll
- Collision detection
- Speed increases
- Score for distance

"puzzle game" →
- Grid-based gameplay
- Matching/clicking mechanics
- Win/lose conditions
- Score system

CRITICAL RULES:
1. Create the EXACT game type requested (flying ship = FLYING game, NOT quiz!)
2. Include ALL necessary mechanics
3. Use modern PixiJS v8 API with import statement
4. Make it FULLY PLAYABLE with controls, game over, restart
5. Include instructions on screen
6. Return COMPLETE working code

PixiJS v8 Code Structure:
```javascript
import {{ Application, Graphics, Text, Container }} from 'pixi.js';

(async () => {{
  const app = new Application();
  await app.init({{
    background: '#colorcode',
    resizeTo: window,
    antialias: true
  }});
  document.body.appendChild(app.canvas);

  // Game variables
  let score = 0;
  let gameOver = false;
  let gameStarted = false;

  // Create graphics using Graphics, Text, Container
  // Add input handling (keyboard, mouse, touch)
  // Use app.ticker.add() for game loop
  // Include collision detection
  // Add game over and restart logic
}})();
```

Make it creative, fun, and COMPLETE!"""),
            ("user", """Create a complete PixiJS game for this request:

"{user_prompt}"

Return ONLY valid JSON (no markdown, no code blocks):
{{
    "title": "Game Title",
    "description": "Brief description of gameplay",
    "pixijs_code": "import {{ Application, Graphics, Text, Container }} from 'pixi.js';\\n\\n(async () => {{\\n  // Complete game code here\\n}})();",
    "game_data": {{}}
}}""")
        ])

        # Generate with OpenAI
        chain = prompt | self.llm
        response = chain.invoke({
            "user_prompt": user_prompt
        })

        # Parse response
        try:
            # Extract JSON from response (handle markdown code blocks)
            content = response.content.strip()
            if content.startswith('```'):
                # Remove markdown code block markers
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
                content = content.strip()

            result = json.loads(content)

            return {
                'title': result.get('title', 'Generated Game'),
                'description': result.get('description', 'A PixiJS game'),
                'pixijs_code': result.get('pixijs_code', ''),
                'game_data': result.get('game_data', {})
            }

        except json.JSONDecodeError as e:
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
