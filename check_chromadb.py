#!/usr/bin/env python
"""
Standalone script to check ChromaDB contents without Django
Run with: python check_chromadb.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.ai_engine.rag.chroma_manager import ChromaManager
from apps.ai_engine.rag.retriever import RAGRetriever


def main():
    print("\n" + "="*80)
    print("📚 ChromaDB Template Inspector")
    print("="*80 + "\n")

    # Initialize ChromaDB manager
    chroma = ChromaManager()

    # Get template count
    count = chroma.count_templates()
    print(f"Total templates in database: {count}\n")

    if count == 0:
        print("⚠️  No templates found!")
        print("Run: python manage.py populate_templates")
        return

    # List all templates
    print("📋 Template List:")
    print("-"*80)
    templates = chroma.list_all_templates()

    for i, template in enumerate(templates, 1):
        print(f"\n{i}. Template ID: {template['id']}")
        print(f"   Name: {template['name']}")
        print(f"   Type: {template['game_type']}")
        print(f"   Tags: {', '.join(template['tags'])}")
        print(f"   Code Size: {template['code_length']} characters")

    print("\n" + "="*80)

    # Test search functionality
    print("\n🔍 Testing Search Functionality:")
    print("-"*80)

    test_queries = [
        "quiz game for learning",
        "platformer with jumping",
        "puzzle matching game",
        "fast clicking game"
    ]

    retriever = RAGRetriever()

    for query in test_queries:
        print(f"\nQuery: '{query}'")
        results = retriever.retrieve_relevant_templates(query, n_results=1)
        if results:
            result = results[0]
            print(f"  → Best match: {result['name']} (type: {result['game_type']})")
            if 'distance' in result and result['distance'] is not None:
                similarity = (1 - result['distance']) * 100
                print(f"  → Similarity: {similarity:.1f}%")

    print("\n" + "="*80)
    print("✅ ChromaDB inspection complete!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
