"""
ChromaDB Manager for PixiJS Game Templates
Manages storage and retrieval of game templates using vector embeddings
"""
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from django.conf import settings
import os
import json
from typing import List, Dict, Any


class ChromaManager:
    """Manages ChromaDB collection for PixiJS game templates"""

    def __init__(self, collection_name: str = "pixijs_templates"):
        """
        Initialize ChromaDB manager

        Args:
            collection_name: Name of the collection to use
        """
        self.collection_name = collection_name

        # Initialize ChromaDB client with persistent storage
        persist_directory = getattr(settings, 'CHROMA_PERSIST_DIRECTORY', './data/chroma_db')
        os.makedirs(persist_directory, exist_ok=True)

        # Use PersistentClient for disk persistence (not in-memory Client)
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )

        # Initialize embedding model (using sentence-transformers)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "PixiJS game templates for RAG"}
        )

    def add_template(
        self,
        template_id: str,
        name: str,
        description: str,
        code: str,
        game_type: str,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Add a game template to the collection

        Args:
            template_id: Unique identifier for the template
            name: Template name
            description: Template description
            code: PixiJS code template
            game_type: Type of game (quiz, platformer, puzzle, etc.)
            tags: List of tags for categorization
            metadata: Additional metadata

        Returns:
            bool: Success status
        """
        try:
            # Prepare metadata
            template_metadata = {
                'name': name,
                'game_type': game_type,
                'tags': json.dumps(tags or []),
                'code_length': len(code)
            }

            if metadata:
                template_metadata.update(metadata)

            # Create searchable text (description + tags)
            searchable_text = f"{description} {game_type} {' '.join(tags or [])}"

            # Generate embedding
            embedding = self.embedding_model.encode(searchable_text).tolist()

            # Add to collection
            self.collection.add(
                ids=[template_id],
                embeddings=[embedding],
                documents=[code],
                metadatas=[template_metadata]
            )

            return True

        except Exception as e:
            print(f"Error adding template {template_id}: {str(e)}")
            return False

    def search_templates(
        self,
        query: str,
        n_results: int = 3,
        game_type: str = None
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant templates using semantic search

        Args:
            query: User's game description/prompt
            n_results: Number of results to return
            game_type: Filter by game type (optional)

        Returns:
            List of matching templates with code and metadata
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()

            # Prepare where filter for game_type
            where_filter = None
            if game_type:
                where_filter = {"game_type": game_type}

            # Search in collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_filter
            )

            # Format results
            templates = []
            if results and results['documents']:
                for i, code in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    templates.append({
                        'id': results['ids'][0][i] if results['ids'] else None,
                        'code': code,
                        'name': metadata.get('name', 'Unknown'),
                        'game_type': metadata.get('game_type', 'unknown'),
                        'tags': json.loads(metadata.get('tags', '[]')),
                        'distance': results['distances'][0][i] if results.get('distances') else None
                    })

            return templates

        except Exception as e:
            print(f"Error searching templates: {str(e)}")
            return []

    def get_template_by_id(self, template_id: str) -> Dict[str, Any]:
        """
        Retrieve a specific template by ID

        Args:
            template_id: Template identifier

        Returns:
            Template data or None
        """
        try:
            result = self.collection.get(ids=[template_id])

            if result and result['documents']:
                metadata = result['metadatas'][0] if result['metadatas'] else {}
                return {
                    'id': template_id,
                    'code': result['documents'][0],
                    'name': metadata.get('name', 'Unknown'),
                    'game_type': metadata.get('game_type', 'unknown'),
                    'tags': json.loads(metadata.get('tags', '[]'))
                }

            return None

        except Exception as e:
            print(f"Error getting template {template_id}: {str(e)}")
            return None

    def delete_template(self, template_id: str) -> bool:
        """
        Delete a template from the collection

        Args:
            template_id: Template identifier

        Returns:
            bool: Success status
        """
        try:
            self.collection.delete(ids=[template_id])
            return True
        except Exception as e:
            print(f"Error deleting template {template_id}: {str(e)}")
            return False

    def count_templates(self) -> int:
        """Get total number of templates in collection"""
        try:
            return self.collection.count()
        except:
            return 0

    def list_all_templates(self) -> List[Dict[str, Any]]:
        """List all templates (metadata only, without full code)"""
        try:
            results = self.collection.get()
            templates = []

            if results and results['ids']:
                for i, template_id in enumerate(results['ids']):
                    metadata = results['metadatas'][i] if results['metadatas'] else {}
                    templates.append({
                        'id': template_id,
                        'name': metadata.get('name', 'Unknown'),
                        'game_type': metadata.get('game_type', 'unknown'),
                        'tags': json.loads(metadata.get('tags', '[]')),
                        'code_length': metadata.get('code_length', 0)
                    })

            return templates

        except Exception as e:
            print(f"Error listing templates: {str(e)}")
            return []
