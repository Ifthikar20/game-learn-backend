# Claude Sonnet 4 API Key Setup

The game generator now uses **Claude Sonnet 4** (Anthropic's latest model) instead of OpenAI GPT-4.

## How to Get Your API Key

1. **Visit Anthropic Console**:
   - Go to: https://console.anthropic.com/settings/keys
   - Sign in or create an account

2. **Create API Key**:
   - Click "Create Key"
   - Give it a name (e.g., "Game Generator")
   - Copy the key (starts with `sk-ant-...`)

3. **Important**: Save this key immediately - you won't be able to see it again!

## Where to Add Your API Key

### Option 1: Environment File (.env)

1. **Copy the example file**:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file**:
   ```bash
   nano .env
   # or
   code .env
   ```

3. **Replace the placeholder**:
   ```bash
   # Change this:
   ANTHROPIC_API_KEY=your-anthropic-api-key-here

   # To your actual key:
   ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxx
   ```

4. **Save and close**

### Option 2: Export Environment Variable

```bash
export ANTHROPIC_API_KEY="sk-ant-api03-xxxxxxxxxxxxxxxxxxxxx"
```

**Note**: This only works for the current terminal session.

## Verify Setup

1. **Install/Update Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the server**:
   ```bash
   python manage.py runserver
   ```

3. **Check console output**:
   ```
   ✓ Claude Sonnet 4 enabled for game generation
   ```

   If you see this, you're all set! ✅

## Troubleshooting

### Error: "ANTHROPIC_API_KEY not found"
- Make sure `.env` file exists in the project root
- Check the variable name is exactly `ANTHROPIC_API_KEY`
- Restart the Django server after adding the key

### Error: "Invalid API key"
- Verify you copied the complete key (starts with `sk-ant-`)
- Check for extra spaces or quotes
- Generate a new key if needed

### Error: "Claude disabled, using fallback"
- The API key wasn't loaded properly
- Check `.env` file exists and contains your key
- Restart the server

## API Key Security

⚠️ **IMPORTANT**:
- Never commit `.env` file to git (it's in `.gitignore`)
- Don't share your API key publicly
- Rotate keys if accidentally exposed
- Use separate keys for development and production

## Pricing

- Claude Sonnet 4 pricing: https://www.anthropic.com/api
- Monitor usage: https://console.anthropic.com/settings/usage

## Why Claude Sonnet 4?

- **Better game generation**: More creative and detailed
- **Longer context**: Can generate more complex games
- **Better instruction following**: Follows format requirements better
- **Latest AI technology**: Released May 2025

---

**Need Help?**
- Anthropic Docs: https://docs.anthropic.com/
- API Status: https://status.anthropic.com/
