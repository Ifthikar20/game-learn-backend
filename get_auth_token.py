#!/usr/bin/env python
"""
Helper script to create a test user and generate an authentication token
for the game viewer.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User
from rest_framework_simplejwt.tokens import RefreshToken


def main():
    print("\n" + "="*60)
    print("Game Viewer Authentication Token Generator")
    print("="*60 + "\n")

    # Get or create test user
    email = input("Enter email (default: test@example.com): ").strip() or "test@example.com"

    try:
        user = User.objects.get(email=email)
        print(f"✓ Found existing user: {user.email}")
    except User.DoesNotExist:
        username = input("Enter username (default: testuser): ").strip() or "testuser"
        password = input("Enter password (default: testpass123): ").strip() or "testpass123"

        user = User.objects.create_user(
            email=email,
            username=username,
            password=password
        )
        print(f"✓ Created new user: {user.email}")

    # Generate tokens
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)

    print("\n" + "="*60)
    print("ACCESS TOKEN (valid for 60 minutes):")
    print("="*60)
    print(access_token)
    print("="*60)

    print("\n" + "="*60)
    print("REFRESH TOKEN (valid for 1 day):")
    print("="*60)
    print(refresh_token)
    print("="*60)

    print("\n📋 Next Steps:")
    print("1. Copy the ACCESS TOKEN above")
    print("2. Open game_viewer.html in a text editor")
    print("3. Replace 'YOUR_TOKEN_HERE' with the access token")
    print("4. Save the file")
    print("5. Start a web server: python -m http.server 8080")
    print("6. Open http://localhost:8080/game_viewer.html")
    print("")


if __name__ == '__main__':
    main()
