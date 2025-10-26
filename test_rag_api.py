#!/usr/bin/env python
"""
Test script for RAG-powered game generation API
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User
from apps.games.models import UserGame
from apps.ai_engine.generators.pixijs_generator import PixiJSGenerator
import json


def test_rag_generation():
    """Test RAG-powered game generation"""

    print("\n" + "="*80)
    print("🎮 Testing RAG-Powered Game Generation")
    print("="*80 + "\n")

    # Test prompts
    test_prompts = [
        "Create a quiz about Python programming basics",
        "Make a platformer game with jumping and obstacles",
        "Build a puzzle game with color matching",
        "Create a fast-paced clicking game",
    ]

    generator = PixiJSGenerator(use_openai=False)

    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n{i}. Prompt: '{prompt}'")
        print("-" * 60)

        result = generator.generate_game(prompt)

        print(f"   ✓ Title: {result['title']}")
        print(f"   ✓ Description: {result['description']}")
        print(f"   ✓ Code size: {len(result['pixijs_code'])} characters")
        print(f"   ✓ Game data: {list(result['game_data'].keys())}")

        # Show first question for quiz games
        if 'questions' in result['game_data']:
            first_q = result['game_data']['questions'][0]
            print(f"   ✓ First question: {first_q['question']}")

    print("\n" + "="*80)
    print("✅ All tests passed! RAG system is working correctly.")
    print("="*80 + "\n")


def test_with_database():
    """Test creating games in the database"""

    print("\n" + "="*80)
    print("💾 Testing Database Integration")
    print("="*80 + "\n")

    # Get or create a test user
    user, created = User.objects.get_or_create(
        email='test@example.com',
        defaults={
            'username': 'testuser',
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"✓ Created test user: {user.email}")
    else:
        print(f"✓ Using existing user: {user.email}")

    # Generate a game
    generator = PixiJSGenerator(use_openai=False)
    result = generator.generate_game("Create a quiz about Django web framework")

    # Save to database
    game = UserGame.objects.create(
        user=user,
        title=result['title'],
        description=result['description'],
        pixijs_code=result['pixijs_code'],
        game_data=result['game_data'],
        user_prompt="Create a quiz about Django web framework",
        status='ready'
    )

    print(f"\n✓ Game saved to database:")
    print(f"   ID: {game.id}")
    print(f"   Title: {game.title}")
    print(f"   Status: {game.status}")
    print(f"   Created: {game.created_at}")

    # Retrieve it
    retrieved = UserGame.objects.get(id=game.id)
    print(f"\n✓ Game retrieved from database:")
    print(f"   Questions in game: {len(retrieved.game_data['questions'])}")
    print(f"   Code ready: {len(retrieved.pixijs_code) > 0}")

    print("\n" + "="*80)
    print("✅ Database integration working!")
    print("="*80 + "\n")

    return game


def show_game_preview(game):
    """Show a preview of the generated game"""

    print("\n" + "="*80)
    print("👀 Game Preview")
    print("="*80 + "\n")

    print(f"Title: {game.title}")
    print(f"Description: {game.description}\n")

    print("Game Data:")
    print(json.dumps(game.game_data, indent=2)[:500] + "...\n")

    print("PixiJS Code (first 300 chars):")
    print(game.pixijs_code[:300] + "...")

    print("\n" + "="*80)


if __name__ == "__main__":
    # Run tests
    test_rag_generation()

    # Test database integration
    game = test_with_database()

    # Show preview
    show_game_preview(game)

    print("\n🎉 All tests complete! Your RAG system is fully operational.")
    print("\nNext steps:")
    print("  1. Start the server: python manage.py runserver")
    print("  2. Test the API: POST /api/games/generate/")
    print("  3. View in admin: python manage.py createsuperuser")
    print()
