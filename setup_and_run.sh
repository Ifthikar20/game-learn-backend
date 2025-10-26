#!/bin/bash

# Setup and Run Script for Game Viewer Backend

set -e  # Exit on error

echo "======================================"
echo "Game Learn Backend Setup & Run"
echo "======================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo ""
    echo "Creating .env from .env.example..."
    cp .env.example .env

    echo ""
    echo "❗ IMPORTANT: Edit .env and add your OpenAI API key!"
    echo ""
    echo "  OPENAI_API_KEY=sk-your-actual-key-here"
    echo ""
    read -p "Press Enter after you've updated .env with your OpenAI key..."
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment not activated!"
    echo ""
    if [ -d "venv" ]; then
        echo "Activating virtual environment..."
        source venv/bin/activate
    else
        echo "❌ venv directory not found. Please create one first:"
        echo "   python -m venv venv"
        echo "   source venv/bin/activate"
        echo "   pip install -r requirements.txt"
        exit 1
    fi
fi

# Check if database exists
if [ ! -f db.sqlite3 ]; then
    echo ""
    echo "📦 Setting up database..."
    python manage.py migrate

    echo ""
    echo "👤 Creating superuser..."
    python manage.py createsuperuser
fi

# Populate templates if not already done
echo ""
echo "📚 Checking ChromaDB templates..."
python manage.py populate_templates

echo ""
echo "======================================"
echo "✅ Setup Complete!"
echo "======================================"
echo ""
echo "🚀 Starting Django development server..."
echo ""
echo "The server will run at: http://localhost:8000"
echo ""
echo "In another terminal, run:"
echo "  1. python get_auth_token.py    # Get your authentication token"
echo "  2. Update game_viewer.html with the token"
echo "  3. python -m http.server 8080  # Serve the HTML file"
echo "  4. Open http://localhost:8080/game_viewer.html"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the Django server
python manage.py runserver
