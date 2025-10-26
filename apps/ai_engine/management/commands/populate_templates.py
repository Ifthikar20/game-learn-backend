"""
Django management command to populate ChromaDB with PixiJS game templates
Run with: python manage.py populate_templates
"""
from django.core.management.base import BaseCommand
from apps.ai_engine.rag.chroma_manager import ChromaManager


class Command(BaseCommand):
    help = 'Populate ChromaDB with PixiJS game templates'

    def handle(self, *args, **kwargs):
        self.stdout.write('Populating ChromaDB with game templates...')

        chroma = ChromaManager()

        # Template 1: Quiz Game
        quiz_template = """
// Educational Quiz Game
const app = new PIXI.Application({
    width: 800,
    height: 600,
    backgroundColor: 0x1099bb
});
document.body.appendChild(app.view);

const questions = GAME_DATA.questions;
let currentQuestion = 0;
let score = 0;

// Title
const titleText = new PIXI.Text('Quiz Game', {
    fontFamily: 'Arial',
    fontSize: 32,
    fill: 0xffffff,
    fontWeight: 'bold'
});
titleText.anchor.set(0.5, 0);
titleText.position.set(400, 20);
app.stage.addChild(titleText);

// Question text
const questionText = new PIXI.Text('', {
    fontFamily: 'Arial',
    fontSize: 24,
    fill: 0xffffff,
    wordWrap: true,
    wordWrapWidth: 700,
    align: 'center'
});
questionText.anchor.set(0.5, 0);
questionText.position.set(400, 100);
app.stage.addChild(questionText);

// Score display
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
    const button = createButton(100, 250 + i * 70, 600, 50);
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
        fill: 0xffffff,
        align: 'center'
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
        button.bg.tint = 0xffffff;
        button.bg.removeAllListeners();
        button.bg.on('pointerdown', () => answerQuestion(index));
    });
}

function answerQuestion(answerIndex) {
    const q = questions[currentQuestion];

    // Visual feedback
    if (answerIndex === q.correctIndex) {
        buttons[answerIndex].bg.tint = 0x00ff00;
        score += 10;
        scoreText.text = `Score: ${score}`;
    } else {
        buttons[answerIndex].bg.tint = 0xff0000;
        buttons[q.correctIndex].bg.tint = 0x00ff00;
    }

    setTimeout(() => {
        currentQuestion++;
        loadQuestion();
    }, 1000);
}

function endGame() {
    questionText.text = `Game Over!\\nFinal Score: ${score}/${questions.length * 10}`;
    buttons.forEach(button => button.container.visible = false);
}

loadQuestion();
"""

        chroma.add_template(
            template_id='quiz_01',
            name='Educational Quiz',
            description='Interactive quiz game with multiple choice questions, score tracking, and visual feedback',
            code=quiz_template,
            game_type='quiz',
            tags=['education', 'trivia', 'questions', 'learning', 'test']
        )
        self.stdout.write(self.style.SUCCESS('✓ Added Quiz template'))

        # Template 2: Platformer Game
        platformer_template = """
// Simple Platformer Game
const app = new PIXI.Application({
    width: 800,
    height: 600,
    backgroundColor: 0x87CEEB
});
document.body.appendChild(app.view);

const levels = GAME_DATA.levels;
let currentLevel = 0;
let player = null;
let platforms = [];
let velocity = { x: 0, y: 0 };
const gravity = 0.5;
const jumpPower = -12;
const moveSpeed = 5;

function loadLevel(levelIndex) {
    // Clear previous level
    app.stage.removeChildren();
    platforms = [];

    const level = levels[levelIndex];

    // Create platforms
    level.platforms.forEach(p => {
        const platform = new PIXI.Graphics();
        platform.beginFill(0x228B22);
        platform.drawRect(p.x, p.y, p.width, p.height);
        platform.endFill();
        app.stage.addChild(platform);
        platforms.push({graphic: platform, ...p});
    });

    // Create player
    player = new PIXI.Graphics();
    player.beginFill(0xFF0000);
    player.drawRect(0, 0, 30, 30);
    player.endFill();
    player.x = 50;
    player.y = 400;
    app.stage.addChild(player);

    velocity = { x: 0, y: 0 };
}

// Keyboard controls
const keys = {};
window.addEventListener('keydown', e => keys[e.code] = true);
window.addEventListener('keyup', e => keys[e.code] = false);

app.ticker.add(() => {
    if (!player) return;

    // Horizontal movement
    if (keys['ArrowLeft']) velocity.x = -moveSpeed;
    else if (keys['ArrowRight']) velocity.x = moveSpeed;
    else velocity.x = 0;

    // Apply gravity
    velocity.y += gravity;

    // Check platform collisions
    let onGround = false;
    platforms.forEach(platform => {
        if (player.x < platform.x + platform.width &&
            player.x + 30 > platform.x &&
            player.y + 30 + velocity.y >= platform.y &&
            player.y + 30 <= platform.y) {
            velocity.y = 0;
            player.y = platform.y - 30;
            onGround = true;
        }
    });

    // Jump
    if (keys['Space'] && onGround) {
        velocity.y = jumpPower;
    }

    // Update position
    player.x += velocity.x;
    player.y += velocity.y;

    // Boundaries
    if (player.x < 0) player.x = 0;
    if (player.x > 770) player.x = 770;
    if (player.y > 600) {
        player.y = 400;
        velocity.y = 0;
    }
});

loadLevel(currentLevel);
"""

        chroma.add_template(
            template_id='platformer_01',
            name='Simple Platformer',
            description='Side-scrolling platformer game with jumping, gravity physics, and platform collisions',
            code=platformer_template,
            game_type='platformer',
            tags=['platform', 'jump', 'physics', 'side-scroller', 'action']
        )
        self.stdout.write(self.style.SUCCESS('✓ Added Platformer template'))

        # Template 3: Puzzle Match Game
        puzzle_template = """
// Color Match Puzzle Game
const app = new PIXI.Application({
    width: 800,
    height: 600,
    backgroundColor: 0x2C3E50
});
document.body.appendChild(app.view);

const gridSize = GAME_DATA.grid_size || 4;
const colors = GAME_DATA.colors || ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A'];
const tileSize = 80;
const gap = 10;
let grid = [];
let score = 0;

// Score display
const scoreText = new PIXI.Text('Score: 0', {
    fontFamily: 'Arial',
    fontSize: 28,
    fill: 0xffffff
});
scoreText.position.set(20, 20);
app.stage.addChild(scoreText);

// Create grid
const gridContainer = new PIXI.Container();
gridContainer.position.set(
    (800 - (gridSize * (tileSize + gap) - gap)) / 2,
    (600 - (gridSize * (tileSize + gap) - gap)) / 2 + 40
);
app.stage.addChild(gridContainer);

function createGrid() {
    grid = [];
    gridContainer.removeChildren();

    for (let row = 0; row < gridSize; row++) {
        grid[row] = [];
        for (let col = 0; col < gridSize; col++) {
            const tile = createTile(row, col);
            grid[row][col] = tile;
            gridContainer.addChild(tile.container);
        }
    }
}

function createTile(row, col) {
    const container = new PIXI.Container();
    container.position.set(
        col * (tileSize + gap),
        row * (tileSize + gap)
    );

    const color = colors[Math.floor(Math.random() * colors.length)];
    const bg = new PIXI.Graphics();
    bg.beginFill(parseInt(color.replace('#', '0x')));
    bg.drawRoundedRect(0, 0, tileSize, tileSize, 10);
    bg.endFill();
    bg.interactive = true;
    bg.buttonMode = true;

    bg.on('pointerdown', () => handleTileClick(row, col));

    container.addChild(bg);

    return {
        container,
        bg,
        color,
        row,
        col,
        matched: false
    };
}

let selectedTile = null;

function handleTileClick(row, col) {
    const tile = grid[row][col];

    if (tile.matched) return;

    if (!selectedTile) {
        // First selection
        selectedTile = tile;
        tile.bg.alpha = 0.7;
    } else {
        // Second selection
        if (selectedTile === tile) {
            // Deselect same tile
            selectedTile.bg.alpha = 1;
            selectedTile = null;
        } else if (selectedTile.color === tile.color) {
            // Match found
            selectedTile.matched = true;
            tile.matched = true;
            selectedTile.bg.alpha = 0.3;
            tile.bg.alpha = 0.3;
            score += 10;
            scoreText.text = `Score: ${score}`;
            selectedTile = null;

            // Check win condition
            checkWin();
        } else {
            // No match
            selectedTile.bg.alpha = 1;
            selectedTile = tile;
            tile.bg.alpha = 0.7;
        }
    }
}

function checkWin() {
    let allMatched = true;
    for (let row = 0; row < gridSize; row++) {
        for (let col = 0; col < gridSize; col++) {
            if (!grid[row][col].matched) {
                allMatched = false;
                break;
            }
        }
    }

    if (allMatched) {
        setTimeout(() => {
            alert('You Win! Score: ' + score);
            createGrid();
            score = 0;
            scoreText.text = 'Score: 0';
        }, 500);
    }
}

createGrid();
"""

        chroma.add_template(
            template_id='puzzle_01',
            name='Color Match Puzzle',
            description='Tile matching puzzle game where players match colored tiles to score points',
            code=puzzle_template,
            game_type='puzzle',
            tags=['puzzle', 'match', 'tiles', 'colors', 'logic']
        )
        self.stdout.write(self.style.SUCCESS('✓ Added Puzzle template'))

        # Template 4: Clicker/Arcade Game
        clicker_template = """
// Arcade Clicker Game
const app = new PIXI.Application({
    width: 800,
    height: 600,
    backgroundColor: 0x1a1a2e
});
document.body.appendChild(app.view);

let score = 0;
let timeLeft = 30;
let gameActive = true;

// Score display
const scoreText = new PIXI.Text('Score: 0', {
    fontFamily: 'Arial',
    fontSize: 36,
    fill: 0xffffff,
    fontWeight: 'bold'
});
scoreText.anchor.set(0.5, 0);
scoreText.position.set(400, 20);
app.stage.addChild(scoreText);

// Timer display
const timerText = new PIXI.Text('Time: 30', {
    fontFamily: 'Arial',
    fontSize: 28,
    fill: 0xffff00
});
timerText.anchor.set(0.5, 0);
timerText.position.set(400, 70);
app.stage.addChild(timerText);

// Create clickable targets
const targets = [];

function createTarget() {
    const target = new PIXI.Graphics();
    const radius = 30 + Math.random() * 20;
    const color = Math.random() * 0xffffff;

    target.beginFill(color);
    target.drawCircle(0, 0, radius);
    target.endFill();

    target.x = radius + Math.random() * (800 - radius * 2);
    target.y = 150 + Math.random() * (450 - radius * 2);

    target.interactive = true;
    target.buttonMode = true;

    target.on('pointerdown', () => {
        if (!gameActive) return;

        score += Math.floor(10 / radius * 30);
        scoreText.text = `Score: ${score}`;

        // Remove target
        app.stage.removeChild(target);
        const index = targets.indexOf(target);
        if (index > -1) targets.splice(index, 1);
    });

    app.stage.addChild(target);
    targets.push(target);
}

// Game timer
setInterval(() => {
    if (!gameActive) return;

    timeLeft--;
    timerText.text = `Time: ${timeLeft}`;

    if (timeLeft <= 0) {
        endGame();
    }
}, 1000);

// Spawn targets
setInterval(() => {
    if (!gameActive) return;
    if (targets.length < 5) {
        createTarget();
    }
}, 800);

function endGame() {
    gameActive = false;
    targets.forEach(t => app.stage.removeChild(t));
    targets.length = 0;

    const gameOverText = new PIXI.Text(`Game Over!\\nFinal Score: ${score}`, {
        fontFamily: 'Arial',
        fontSize: 48,
        fill: 0xff0000,
        align: 'center'
    });
    gameOverText.anchor.set(0.5);
    gameOverText.position.set(400, 300);
    app.stage.addChild(gameOverText);
}

// Initial targets
for (let i = 0; i < 3; i++) {
    createTarget();
}
"""

        chroma.add_template(
            template_id='clicker_01',
            name='Arcade Clicker',
            description='Fast-paced clicking game where players click targets before time runs out',
            code=clicker_template,
            game_type='arcade',
            tags=['clicker', 'arcade', 'fast-paced', 'reaction', 'timed']
        )
        self.stdout.write(self.style.SUCCESS('✓ Added Clicker template'))

        # Template 5: Flying/Flappy Bird Style Game
        flying_template = """
// Flying/Flappy Bird Style Game
const app = new PIXI.Application({
    width: 800,
    height: 600,
    backgroundColor: 0x87CEEB
});
document.body.appendChild(app.view);

let score = 0;
let highScore = 0;
let gameOver = false;
let gameStarted = false;
let playerVelocityY = 0;
const gravity = 0.5;
const jumpPower = -10;
const scrollSpeed = 5;

// Create player
const player = new PIXI.Graphics();
player.beginFill(0xFF0000);
player.drawRect(0, 0, 40, 40);
player.endFill();
player.x = 100;
player.y = 300;
app.stage.addChild(player);

// Obstacles container
const obstacles = new PIXI.Container();
app.stage.addChild(obstacles);

// Score text
const scoreText = new PIXI.Text('Score: 0', {
    fontFamily: 'Arial',
    fontSize: 32,
    fill: 0xffffff,
    fontWeight: 'bold',
    stroke: { color: 0x000000, width: 4 }
});
scoreText.position.set(20, 20);
app.stage.addChild(scoreText);

// High score text
const highScoreText = new PIXI.Text('High Score: 0', {
    fontFamily: 'Arial',
    fontSize: 24,
    fill: 0xffffff,
    fontWeight: 'bold',
    stroke: { color: 0x000000, width: 4 }
});
highScoreText.position.set(20, 60);
app.stage.addChild(highScoreText);

// Instructions
const instructions = new PIXI.Text('Press SPACE or Click to Fly!\\n\\nAvoid the obstacles!', {
    fontFamily: 'Arial',
    fontSize: 36,
    fill: 0xffffff,
    fontWeight: 'bold',
    stroke: { color: 0x000000, width: 5 },
    align: 'center'
});
instructions.anchor.set(0.5);
instructions.position.set(400, 300);
app.stage.addChild(instructions);

// Game over text
const gameOverText = new PIXI.Text('GAME OVER!\\n\\nPress SPACE or Click to Restart', {
    fontFamily: 'Arial',
    fontSize: 36,
    fill: 0xFF0000,
    fontWeight: 'bold',
    stroke: { color: 0x000000, width: 5 },
    align: 'center'
});
gameOverText.anchor.set(0.5);
gameOverText.position.set(400, 300);
gameOverText.visible = false;
app.stage.addChild(gameOverText);

// Create obstacle
function createObstacle() {
    const gap = 200;
    const minHeight = 50;
    const maxHeight = app.screen.height - gap - 100;
    const topHeight = Math.random() * (maxHeight - minHeight) + minHeight;

    const topObstacle = new PIXI.Graphics();
    topObstacle.beginFill(0x228B22);
    topObstacle.drawRect(0, 0, 60, topHeight);
    topObstacle.endFill();
    topObstacle.x = app.screen.width;
    topObstacle.y = 0;

    const bottomObstacle = new PIXI.Graphics();
    const bottomHeight = app.screen.height - topHeight - gap;
    bottomObstacle.beginFill(0x228B22);
    bottomObstacle.drawRect(0, 0, 60, bottomHeight);
    bottomObstacle.endFill();
    bottomObstacle.x = app.screen.width;
    bottomObstacle.y = topHeight + gap;

    const obstacleGroup = new PIXI.Container();
    obstacleGroup.addChild(topObstacle);
    obstacleGroup.addChild(bottomObstacle);
    obstacleGroup.scored = false;

    obstacles.addChild(obstacleGroup);
}

let obstacleTimer = 0;
const obstacleInterval = 120;

function checkCollision(player, obstacle) {
    const playerBounds = player.getBounds();
    const obstacleBounds = obstacle.getBounds();
    return playerBounds.x < obstacleBounds.x + obstacleBounds.width &&
           playerBounds.x + playerBounds.width > obstacleBounds.x &&
           playerBounds.y < obstacleBounds.y + obstacleBounds.height &&
           playerBounds.y + playerBounds.height > obstacleBounds.y;
}

function resetGame() {
    gameOver = false;
    gameStarted = true;
    score = 0;
    playerVelocityY = 0;
    player.y = 300;
    obstacles.removeChildren();
    scoreText.text = 'Score: 0';
    gameOverText.visible = false;
    instructions.visible = false;
}

function jump() {
    if (gameOver) {
        resetGame();
    } else if (!gameStarted) {
        gameStarted = true;
        instructions.visible = false;
    } else {
        playerVelocityY = jumpPower;
    }
}

// Input handling
window.addEventListener('keydown', (e) => {
    if (e.code === 'Space') {
        e.preventDefault();
        jump();
    }
});

app.canvas.addEventListener('click', () => jump());
app.canvas.addEventListener('touchstart', (e) => {
    e.preventDefault();
    jump();
});

// Game loop
app.ticker.add(() => {
    if (!gameStarted || gameOver) return;

    playerVelocityY += gravity;
    player.y += playerVelocityY;
    player.rotation = Math.min(Math.max(playerVelocityY * 0.05, -0.5), 0.5);

    if (player.y < 0 || player.y + player.height > app.screen.height) {
        gameOver = true;
        gameOverText.visible = true;
        if (score > highScore) {
            highScore = score;
            highScoreText.text = `High Score: ${highScore}`;
        }
    }

    obstacleTimer++;
    if (obstacleTimer > obstacleInterval) {
        createObstacle();
        obstacleTimer = 0;
    }

    for (let i = obstacles.children.length - 1; i >= 0; i--) {
        const obstacleGroup = obstacles.children[i];
        obstacleGroup.x -= scrollSpeed;

        for (let j = 0; j < obstacleGroup.children.length; j++) {
            if (checkCollision(player, obstacleGroup.children[j])) {
                gameOver = true;
                gameOverText.visible = true;
                if (score > highScore) {
                    highScore = score;
                    highScoreText.text = `High Score: ${highScore}`;
                }
            }
        }

        if (!obstacleGroup.scored && obstacleGroup.x + 60 < player.x) {
            obstacleGroup.scored = true;
            score++;
            scoreText.text = `Score: ${score}`;
        }

        if (obstacleGroup.x + 60 < 0) {
            obstacles.removeChild(obstacleGroup);
        }
    }
});
"""

        chroma.add_template(
            template_id='flying_01',
            name='Flying/Flappy Bird Game',
            description='Side-scrolling flying game where player navigates through obstacles by controlling vertical movement',
            code=flying_template,
            game_type='flying',
            tags=['flying', 'flappy', 'bird', 'obstacles', 'endless', 'runner', 'scrolling', 'car', 'plane']
        )
        self.stdout.write(self.style.SUCCESS('✓ Added Flying game template'))

        # Show summary
        count = chroma.count_templates()
        self.stdout.write(self.style.SUCCESS(f'\n✓ Successfully populated {count} templates'))
        self.stdout.write(self.style.SUCCESS('ChromaDB is ready for RAG-powered game generation!'))
