"""
RAG Retriever for PixiJS Game Generation
Handles semantic search and template retrieval for game generation
"""
from typing import List, Dict, Any, Optional
from .chroma_manager import ChromaManager


class RAGRetriever:
    """
    Retrieval-Augmented Generation retriever for PixiJS templates
    Uses semantic search to find relevant game templates
    """

    def __init__(self):
        """Initialize the retriever with ChromaDB manager"""
        self.chroma_manager = ChromaManager()

    def retrieve_relevant_templates(
        self,
        user_prompt: str,
        game_type: Optional[str] = None,
        n_results: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Retrieve the most relevant game templates based on user prompt

        Args:
            user_prompt: User's description of desired game
            game_type: Optional filter for specific game type
            n_results: Number of templates to retrieve

        Returns:
            List of relevant templates with code and metadata
        """
        # Detect game type from prompt if not specified
        if not game_type:
            game_type = self._detect_game_type(user_prompt)

        # Search for relevant templates
        templates = self.chroma_manager.search_templates(
            query=user_prompt,
            n_results=n_results,
            game_type=game_type
        )

        return templates

    def _detect_game_type(self, prompt: str) -> Optional[str]:
        """
        Detect game type from user prompt using keyword matching

        Args:
            prompt: User's game description

        Returns:
            Detected game type or None
        """
        prompt_lower = prompt.lower()

        # Game type keywords
        game_type_keywords = {
            'quiz': ['quiz', 'question', 'trivia', 'test', 'exam', 'knowledge'],
            'platformer': ['platform', 'jump', 'run', 'mario', 'side-scroller'],
            'puzzle': ['puzzle', 'match', 'tile', 'brain', 'logic'],
            'shooter': ['shoot', 'bullet', 'enemy', 'gun', 'fire'],
            'racing': ['race', 'car', 'speed', 'track', 'driving'],
            'adventure': ['adventure', 'explore', 'rpg', 'story'],
            'arcade': ['arcade', 'score', 'classic', 'retro'],
            'educational': ['learn', 'teach', 'study', 'education', 'practice']
        }

        # Find matching game type
        for game_type, keywords in game_type_keywords.items():
            if any(keyword in prompt_lower for keyword in keywords):
                return game_type

        return None

    def get_template_context(self, templates: List[Dict[str, Any]]) -> str:
        """
        Format retrieved templates into context for LLM

        Args:
            templates: List of retrieved templates

        Returns:
            Formatted context string
        """
        if not templates:
            return "No relevant templates found."

        context_parts = ["Here are relevant PixiJS game templates:\n"]

        for i, template in enumerate(templates, 1):
            context_parts.append(f"\n### Template {i}: {template['name']}")
            context_parts.append(f"Type: {template['game_type']}")
            context_parts.append(f"Tags: {', '.join(template['tags'])}")
            context_parts.append(f"\nCode:\n```javascript\n{template['code']}\n```\n")

        return "\n".join(context_parts)

    def get_best_template(self, user_prompt: str) -> Optional[Dict[str, Any]]:
        """
        Get the single best matching template

        Args:
            user_prompt: User's game description

        Returns:
            Best matching template or None
        """
        templates = self.retrieve_relevant_templates(user_prompt, n_results=1)
        return templates[0] if templates else None

    def get_all_game_types(self) -> List[str]:
        """
        Get list of all available game types in the database

        Returns:
            List of unique game types
        """
        templates = self.chroma_manager.list_all_templates()
        game_types = set(t['game_type'] for t in templates)
        return sorted(list(game_types))

    def count_templates(self) -> int:
        """Get total number of templates available"""
        return self.chroma_manager.count_templates()
