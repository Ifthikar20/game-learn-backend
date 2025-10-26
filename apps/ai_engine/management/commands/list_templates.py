"""
Django management command to list all templates in ChromaDB
Run with: python manage.py list_templates
"""
from django.core.management.base import BaseCommand
from apps.ai_engine.rag.chroma_manager import ChromaManager
from rich.console import Console
from rich.table import Table


class Command(BaseCommand):
    help = 'List all PixiJS game templates in ChromaDB'

    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed information including code snippets',
        )
        parser.add_argument(
            '--id',
            type=str,
            help='Show detailed information for a specific template ID',
        )
        parser.add_argument(
            '--search',
            type=str,
            help='Search for templates matching a query',
        )

    def handle(self, *args, **kwargs):
        detailed = kwargs['detailed']
        template_id = kwargs['id']
        search_query = kwargs['search']

        chroma = ChromaManager()

        # Show specific template
        if template_id:
            self.show_template_detail(chroma, template_id)
            return

        # Search templates
        if search_query:
            self.search_templates(chroma, search_query)
            return

        # List all templates
        self.list_all_templates(chroma, detailed)

    def list_all_templates(self, chroma, detailed=False):
        """List all templates in the database"""
        templates = chroma.list_all_templates()
        total_count = chroma.count_templates()

        self.stdout.write(self.style.SUCCESS(f'\n📚 ChromaDB Templates ({total_count} total)\n'))

        if not templates:
            self.stdout.write(self.style.WARNING('No templates found in ChromaDB!'))
            self.stdout.write('\nRun: python manage.py populate_templates')
            return

        # Create table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", width=15)
        table.add_column("Name", style="green", width=25)
        table.add_column("Type", style="yellow", width=12)
        table.add_column("Tags", style="blue", width=30)
        table.add_column("Code Size", style="white", width=10)

        for template in templates:
            tags = ', '.join(template['tags'][:3])  # Show first 3 tags
            if len(template['tags']) > 3:
                tags += '...'

            table.add_row(
                template['id'],
                template['name'],
                template['game_type'],
                tags,
                f"{template['code_length']} chars"
            )

        console = Console()
        console.print(table)

        if detailed:
            self.stdout.write('\n' + '='*80 + '\n')
            for template in templates:
                self.stdout.write(self.style.SUCCESS(f"\n🎮 {template['name']} ({template['id']})"))
                self.stdout.write(f"Type: {template['game_type']}")
                self.stdout.write(f"Tags: {', '.join(template['tags'])}")
                self.stdout.write(f"Code length: {template['code_length']} characters")
                self.stdout.write('-'*80)

    def show_template_detail(self, chroma, template_id):
        """Show detailed information for a specific template"""
        template = chroma.get_template_by_id(template_id)

        if not template:
            self.stdout.write(self.style.ERROR(f'❌ Template "{template_id}" not found!'))
            return

        self.stdout.write(self.style.SUCCESS(f'\n🎮 Template: {template["name"]}'))
        self.stdout.write(f'ID: {template["id"]}')
        self.stdout.write(f'Type: {template["game_type"]}')
        self.stdout.write(f'Tags: {", ".join(template["tags"])}')
        self.stdout.write('\n' + '='*80)
        self.stdout.write('📝 Code Preview (first 500 characters):\n')
        self.stdout.write(template['code'][:500])
        if len(template['code']) > 500:
            self.stdout.write('\n... (truncated)')
        self.stdout.write('\n' + '='*80)

    def search_templates(self, chroma, query):
        """Search templates by query"""
        from apps.ai_engine.rag.retriever import RAGRetriever

        retriever = RAGRetriever()
        templates = retriever.retrieve_relevant_templates(query, n_results=5)

        self.stdout.write(self.style.SUCCESS(f'\n🔍 Search results for: "{query}"\n'))

        if not templates:
            self.stdout.write(self.style.WARNING('No matching templates found!'))
            return

        for i, template in enumerate(templates, 1):
            self.stdout.write(self.style.SUCCESS(f"\n{i}. {template['name']} ({template['id']})"))
            self.stdout.write(f"   Type: {template['game_type']}")
            self.stdout.write(f"   Tags: {', '.join(template['tags'])}")
            if 'distance' in template and template['distance'] is not None:
                similarity = 1 - template['distance']
                self.stdout.write(f"   Similarity: {similarity:.2%}")
            self.stdout.write('-'*60)
