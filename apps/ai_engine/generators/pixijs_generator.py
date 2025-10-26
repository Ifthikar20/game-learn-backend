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
                model="gpt-3.5-turbo",
                temperature=0.9,  # Higher creativity
                api_key=getattr(settings, 'OPENAI_API_KEY')
            )
            print(f"✓ OpenAI enabled for game generation")

    def generate_game(self, user_prompt: str) -> Dict[str, Any]:
        """
        Generate a complete PixiJS game based on user prompt

        Args:
            user_prompt: User's description of desired game

        Returns:
            Dictionary containing title, description, pixijs_code, and game_data
        """
        # Step 1: Retrieve relevant templates using RAG
        templates = self.retriever.retrieve_relevant_templates(
            user_prompt=user_prompt,
            n_results=2
        )

        if not templates:
            # Fallback: Use simple quiz template if no templates found
            return self._generate_fallback_quiz(user_prompt)

        # Use the best matching template
        best_template = templates[0]

        # Step 2: Generate customized game using OpenAI (if available)
        if self.use_openai:
            try:
                print(f"🤖 Generating unique game with OpenAI for: '{user_prompt}'")
                print(f"📋 Using template: {best_template.get('name', 'Unknown')}")
                result = self._generate_with_openai(user_prompt, best_template, templates)
                print(f"✅ Generated game: {result.get('title', 'Unknown')}")
                return result
            except Exception as e:
                print(f"❌ OpenAI generation failed: {str(e)}")
                print(f"⚠️  Falling back to template: {best_template.get('name')}")
                # Fall back to template-based generation
                return self._generate_from_template(user_prompt, best_template)
        else:
            print(f"⚠️  OpenAI disabled, using template directly")
            # Use template directly with basic customization
            return self._generate_from_template(user_prompt, best_template)

    def _generate_with_openai(
        self,
        user_prompt: str,
        best_template: Dict[str, Any],
        all_templates: list
    ) -> Dict[str, Any]:
        """
        Generate game using OpenAI to customize the template

        Args:
            user_prompt: User's game description
            best_template: Best matching template
            all_templates: All retrieved templates for context

        Returns:
            Generated game data
        """
        # Create context from templates
        template_context = self.retriever.get_template_context(all_templates)

        # Create prompt for OpenAI
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert PixiJS game developer. You MUST create COMPLETELY UNIQUE games for EACH request.

🚨 CRITICAL RULES:
1. ANALYZE the user's request carefully - what game type do they want?
2. If they say "flying car", "space shooter", "platformer" - make THAT type of game, NOT a quiz!
3. DO NOT default to quiz games unless explicitly requested
4. Create BRAND NEW code from scratch based on the template mechanics
5. Change EVERYTHING: colors, shapes, text, UI, gameplay feel
6. Make it look and play completely different from any previous game

For different game types:
- FLYING/FLAPPY games: obstacles to avoid, tap to fly, scrolling
- QUIZ games: only if user asks for quiz/questions/trivia
- PLATFORMER games: jumping, platforms, gravity
- SHOOTER games: bullets, enemies, aiming
- PUZZLE games: matching, grid-based logic

Visual customization (REQUIRED):
- Change ALL colors to match theme
- Draw custom shapes (cars, spaceships, characters)
- Update ALL text and labels
- Theme-appropriate backgrounds
- Unique UI styling

Use PixiJS v8 API:
- PIXI.Graphics() for shapes
- PIXI.Text() for text
- PIXI.Container() for grouping
- app.ticker.add() for game loop"""),
            ("user", """User Request: {user_prompt}

Available Templates for Reference:
{template_context}

Task: Create a UNIQUE game that matches the user's request. Do NOT just copy the template!

If user says "flying car" → Create a FLYING GAME with car theme
If user says "quiz" → Create a QUIZ GAME
If user says "shooter" → Create a SHOOTER GAME

Return ONLY valid JSON:
{{
    "title": "Descriptive Title",
    "description": "What the game is about",
    "pixijs_code": "// Complete unique PixiJS code",
    "game_data": {{}}
}}""")
        ])

        # Generate with OpenAI
        chain = prompt | self.llm
        response = chain.invoke({
            "user_prompt": user_prompt,
            "template_context": template_context
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
                'pixijs_code': result.get('pixijs_code', best_template['code']),
                'game_data': result.get('game_data', {})
            }

        except json.JSONDecodeError as e:
            print(f"Failed to parse OpenAI response: {str(e)}")
            # Fallback to template
            return self._generate_from_template(user_prompt, best_template)

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
