#!/usr/bin/env python
"""
Test script to verify Claude Sonnet 4 setup
Run this to check if everything is configured correctly
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings

print("=" * 60)
print("🔍 Claude Sonnet 4 Setup Verification")
print("=" * 60)

# Check 1: Import packages
print("\n1️⃣ Checking package imports...")
try:
    from langchain_anthropic import ChatAnthropic
    print("   ✅ langchain_anthropic imported successfully")
except ImportError as e:
    print(f"   ❌ Failed to import langchain_anthropic: {e}")
    print("   💡 Run: pip install langchain-anthropic")
    sys.exit(1)

try:
    import anthropic
    print(f"   ✅ anthropic package imported (version: {anthropic.__version__})")
except ImportError as e:
    print(f"   ❌ Failed to import anthropic: {e}")
    print("   💡 Run: pip install anthropic")
    sys.exit(1)

# Check 2: API Key
print("\n2️⃣ Checking API key configuration...")
api_key = getattr(settings, 'ANTHROPIC_API_KEY', '')

if not api_key:
    print("   ❌ ANTHROPIC_API_KEY not found in settings")
    print("   💡 Add to .env file: ANTHROPIC_API_KEY=sk-ant-api03-...")
    sys.exit(1)
elif api_key == 'your-anthropic-api-key-here':
    print("   ❌ ANTHROPIC_API_KEY is still the placeholder")
    print("   💡 Edit .env file with your real API key from:")
    print("   💡 https://console.anthropic.com/settings/keys")
    sys.exit(1)
elif api_key.startswith('sk-ant-'):
    print(f"   ✅ API key found: {api_key[:20]}...{api_key[-5:]}")
else:
    print(f"   ⚠️  API key found but doesn't start with 'sk-ant-': {api_key[:20]}...")
    print("   💡 Make sure you're using the correct Anthropic API key")

# Check 3: Initialize Claude
print("\n3️⃣ Testing Claude initialization...")
try:
    llm = ChatAnthropic(
        model="claude-sonnet-4-20250514",
        temperature=1.0,
        max_tokens=100,
        api_key=api_key
    )
    print("   ✅ Claude Sonnet 4 initialized successfully")
except Exception as e:
    print(f"   ❌ Failed to initialize Claude: {e}")
    sys.exit(1)

# Check 4: Test API call
print("\n4️⃣ Testing API connection...")
try:
    response = llm.invoke("Say 'Hello from Claude!'")
    print(f"   ✅ API call successful!")
    print(f"   📝 Response: {response.content[:50]}...")
except Exception as e:
    print(f"   ❌ API call failed: {e}")
    print("   💡 Check your API key is valid and has credits")
    sys.exit(1)

# Check 5: Generator import
print("\n5️⃣ Testing PixiJSGenerator...")
try:
    from apps.ai_engine.generators.pixijs_generator import PixiJSGenerator
    generator = PixiJSGenerator(use_claude=True)
    print("   ✅ PixiJSGenerator initialized with Claude")
except Exception as e:
    print(f"   ❌ Failed to initialize generator: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Success!
print("\n" + "=" * 60)
print("✅ ALL CHECKS PASSED!")
print("=" * 60)
print("\nYour Claude Sonnet 4 setup is working correctly! 🎉")
print("\nYou can now:")
print("  1. Start Django: python manage.py runserver")
print("  2. Generate games using Claude Sonnet 4")
print("\n" + "=" * 60)
