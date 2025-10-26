# Fix: ES6 Import Statement Error

## Problem

The game viewer was showing this error:
```
Uncaught SyntaxError: Failed to execute 'appendChild' on 'Node': Cannot use import statement outside a module
```

## Root Cause

1. **GPT was generating ES6 imports**: The prompt instructed ChatGPT to generate code with:
   ```javascript
   import { Application, Graphics, Text } from 'pixi.js';
   ```

2. **HTML was injecting as regular script**: The viewer injected code as a normal script tag, not a module:
   ```javascript
   script.textContent = currentGameData.pixijs_code;
   document.body.appendChild(script);
   ```

3. **ES6 imports require module context**: Import statements only work in scripts with `type="module"`, but we're using the global PIXI object from CDN.

## Solution

Updated the GPT prompt to generate code using the **global PIXI object** instead of imports:

### Before (Broken)
```javascript
import { Application, Graphics } from 'pixi.js';

const app = new Application();
```

### After (Working)
```javascript
// No imports - use global PIXI object
const app = new PIXI.Application({
  width: 800,
  height: 600,
  backgroundColor: 0x1099bb
});
```

## Changes Made

### 1. Updated Generator Prompt (`apps/ai_engine/generators/pixijs_generator.py`)

**Lines 76-137**: Changed system prompt to:
- Use PixiJS v7 (matches CDN version)
- Use global `PIXI` object instead of imports
- Append canvas to `game-container` div instead of `document.body`
- Use `new PIXI.Application()`, `new PIXI.Graphics()`, etc.

**Lines 138-158**: Updated user prompt to:
- Explicitly state "DO NOT use import statements"
- Show example using global PIXI object
- Specify proper canvas placement

### 2. Improved HTML Viewer (`game_viewer.html`)

**Lines 487-528**: Enhanced playGame() function:
- Better error handling with `script.onerror`
- Cleanup script tag after execution
- Improved console logging for debugging
- Better error messages to user

## How the Flow Works Now

```
User describes game
    ↓
GPT generates PixiJS code (using global PIXI object)
    ↓
Backend returns JSON with pixijs_code
    ↓
HTML injects code as regular script tag
    ↓
Code executes using pre-loaded PIXI from CDN
    ↓
Game renders in game-container div
```

## Testing

To verify the fix:

1. **Start Backend Server**:
   ```bash
   python manage.py runserver
   ```

2. **Start Game Viewer**:
   ```bash
   python -m http.server 8080
   ```

3. **Login & Generate Game**:
   - Open: `http://localhost:8080/game_viewer.html`
   - Login with: `test@example.com / testpass123`
   - Generate a game: "Create a simple platformer game"
   - Click "Play Game"

4. **Expected Result**:
   - ✅ No import statement error
   - ✅ Game renders in the container
   - ✅ Console shows: "Game script injected successfully!"

5. **Check Console**:
   - Should NOT see: "Cannot use import statement"
   - Should see: "Starting game...", "Game Data:", "Game script injected successfully!"

## Why This Approach?

1. **Simpler**: No need for ES6 module complexity
2. **Compatible**: Works with CDN-loaded PixiJS
3. **Consistent**: Matches fallback quiz template pattern
4. **Reliable**: No CORS issues with modules

## Files Changed

- `apps/ai_engine/generators/pixijs_generator.py` - Updated GPT prompt
- `game_viewer.html` - Improved error handling and cleanup

## Commit

```
f1553f4 - Fix: Remove ES6 import statements to fix module error
```

## Related Issues

This fix resolves the "Cannot use import statement outside a module" error that was preventing games from loading in the viewer.
