#!/usr/bin/env python3
"""
PlayStudy Backend Project Structure Generator
Creates a complete Django backend with RAG-powered game generation
"""

import os
import sys
from pathlib import Path


def create_directory_structure():
    """Create the complete project directory structure"""
    
    base_structure = {
        'config': [],
        'apps': {
            'users': {
                'migrations': [],
                'management': {
                    'commands': []
                },
                'api': []
            },
            'games': {
                'migrations': [],
                'management': {
                    'commands': []
                },
                'api': []
            },
            'ai_engine': {
                'migrations': [],
                'rag': [],
                'generators': [],
                'templates': []
            }
        },
        'data': {
            'chroma_db': [],
            'uploads': [],
            'game_templates': []
        },
        'logs': [],
        'media': {
            'documents': [],
            'games': []
        },
        'static': [],
        'staticfiles': [],
        'templates': [],
        'tests': {
            'unit': [],
            'integration': []
        },
        'scripts': [],
        'docs': []
    }
    
    def create_dirs(base_path, structure):
        """Recursively create directory structure"""
        for name, content in structure.items():
            current_path = base_path / name
            current_path.mkdir(parents=True, exist_ok=True)
            print(f"✓ Created: {current_path}")
            
            # Create __init__.py for Python packages
            if name in ['apps', 'config'] or current_path.parent.name in ['apps', 'api', 'management', 'commands', 'rag', 'generators', 'templates']:
                init_file = current_path / '__init__.py'
                init_file.touch()
                print(f"  ✓ Created: {init_file}")
            
            if isinstance(content, dict):
                create_dirs(current_path, content)
            elif isinstance(content, list):
                for subdir in content:
                    sub_path = current_path / subdir
                    sub_path.mkdir(parents=True, exist_ok=True)
    
    project_root = Path.cwd()
    print(f"\n📁 Creating project structure at: {project_root}\n")
    create_dirs(project_root, base_structure)
    print("\n✅ Directory structure created successfully!\n")


def create_file_templates():
    """Create all necessary file templates"""
    
    files = {
        # Root level files
        'manage.py': '''#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
''',
        
        'requirements.txt': '''# Django Core
Django==5.0.1
djangorestframework==3.14.0
django-cors-headers==4.3.1
django-environ==0.11.2

# Authentication & Security
djangorestframework-simplejwt==5.3.1
cryptography==42.0.2

# Database
psycopg2-binary==2.9.9
dj-database-url==2.1.0

# AI & ML
openai==1.12.0
langchain==0.1.7
langchain-openai==0.0.5
chromadb==0.4.22
sentence-transformers==2.3.1
tiktoken==0.5.2

# Data Processing
PyPDF2==3.0.1
python-docx==1.1.0
python-pptx==0.6.23
pandas==2.1.4
numpy==1.26.3

# Storage & Files
boto3==1.34.34
django-storages==1.14.2
Pillow==10.2.0

# Task Queue
celery==5.3.6
redis==5.0.1

# API & Web
requests==2.31.0
httpx==0.26.0

# Utilities
python-dotenv==1.0.1
pydantic==2.5.3

# Development
black==24.1.1
flake8==7.0.0
pytest==8.0.0
pytest-django==4.7.0

# Production
gunicorn==21.2.0
whitenoise==6.6.0
''',
        
        '.env.example': '''# Django Settings
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/playstudy_db

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# OpenAI
OPENAI_API_KEY=your-openai-api-key-here

# Celery & Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# AWS S3 (Optional - for file storage)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=playstudy-files
AWS_S3_REGION_NAME=us-east-1

# ChromaDB
CHROMA_PERSIST_DIRECTORY=./data/chroma_db
CHROMA_COLLECTION_NAME=pixijs_game_templates

# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME=60  # minutes
JWT_REFRESH_TOKEN_LIFETIME=1440  # minutes (24 hours)
''',
        
        '.gitignore': '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/
env.bak/
venv.bak/

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
/media
/staticfiles
/static

# Environment variables
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Data directories
/data/chroma_db/*
/data/uploads/*
!/data/chroma_db/.gitkeep
!/data/uploads/.gitkeep

# Logs
logs/
*.log

# Testing
.coverage
htmlcov/
.pytest_cache/
''',
        
        'README.md': '''# PlayStudy Backend - RAG-Powered Game Generation

A Django-based backend with RAG (Retrieval-Augmented Generation) for dynamically creating educational games using PixiJS.

## Features

- 🎮 **Dynamic Game Generation**: AI-powered game creation based on user prompts
- 🧠 **RAG System**: ChromaDB-powered retrieval for PixiJS game templates
- 🔐 **JWT Authentication**: Secure user authentication and authorization
- 📚 **Document Processing**: Support for PDF, DOCX, PPTX file uploads
- 🎯 **Game Types**: Plane, Fishing, Circuit, Quiz games
- 📊 **Progress Tracking**: User progress, XP, levels, and achievements
- ⚡ **Async Tasks**: Celery for background game generation

## Tech Stack

- **Framework**: Django 5.0 + Django REST Framework
- **AI/ML**: OpenAI GPT, LangChain, ChromaDB, Sentence Transformers
- **Database**: PostgreSQL (production), SQLite (development)
- **Cache/Queue**: Redis + Celery
- **Authentication**: JWT (Simple JWT)

## Installation

### Prerequisites

- Python 3.11+
- PostgreSQL (for production)
- Redis (for Celery tasks)
- Virtual environment

### Setup Steps

1. **Clone and Navigate**
   ```bash
   cd playstudy_backend
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

5. **Database Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Load PixiJS Game Templates**
   ```bash
   python manage.py load_game_templates
   ```

8. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

9. **Run Celery Worker** (in separate terminal)
   ```bash
   celery -A config worker --loglevel=info
   ```

## Project Structure

```
playstudy_backend/
├── config/                  # Django settings and configuration
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── celery.py
├── apps/
│   ├── users/              # User management
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── api/
│   ├── games/              # Game management
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── tasks.py
│   │   └── api/
│   └── ai_engine/          # RAG & AI generation
│       ├── rag/
│       │   ├── chroma_manager.py
│       │   └── retriever.py
│       ├── generators/
│       │   ├── base_generator.py
│       │   └── pixijs_generator.py
│       └── templates/
│           └── pixijs_templates/
├── data/
│   ├── chroma_db/          # ChromaDB storage
│   ├── uploads/            # User uploaded files
│   └── game_templates/     # PixiJS template library
├── scripts/                # Utility scripts
├── tests/                  # Test suites
├── manage.py
└── requirements.txt

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/token/` - Login (get tokens)
- `POST /api/auth/token/refresh/` - Refresh access token

### Games
- `POST /api/games/generate/` - Generate game from prompt
- `GET /api/games/` - List user games
- `GET /api/games/{id}/` - Get game details
- `GET /api/games/{id}/play/` - Get game code to play
- `PUT /api/games/{id}/progress/` - Update progress
- `POST /api/games/{id}/score/` - Submit score
- `DELETE /api/games/{id}/` - Delete game

### Users
- `GET /api/users/me/` - Get current user
- `GET /api/users/me/progress/` - Get user progress
- `PUT /api/users/me/` - Update profile

### Documents
- `POST /api/documents/upload/` - Upload study material
- `GET /api/documents/` - List documents
- `DELETE /api/documents/{id}/` - Delete document

## RAG System

The RAG system uses ChromaDB to store and retrieve PixiJS game templates:

1. **Template Storage**: PixiJS code templates are embedded and stored
2. **Semantic Search**: User prompts are matched to relevant templates
3. **Dynamic Generation**: Templates are combined and customized
4. **Game Types**: Plane, Fishing, Circuit, Quiz

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black .
flake8 .
```

### Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

## Deployment

### Using Gunicorn
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### Environment Variables (Production)
- Set `DEBUG=False`
- Use PostgreSQL for `DATABASE_URL`
- Configure proper `ALLOWED_HOSTS`
- Set strong `SECRET_KEY`
- Configure AWS S3 for media storage
- Set up Redis for Celery

## Contributing

1. Follow PEP 8 style guide
2. Write tests for new features
3. Update documentation
4. Create pull requests

## License

MIT License
''',
        
        'Dockerfile': '''FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    postgresql-client \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
''',
        
        'docker-compose.yml': '''version: '3.8'

services:
  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=playstudy_db
      - POSTGRES_USER=playstudy_user
      - POSTGRES_PASSWORD=playstudy_password
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  web:
    build: .
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db
      - redis

  celery:
    build: .
    command: celery -A config worker --loglevel=info
    volumes:
      - .:/app
    env_file:
      - .env
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
  static_volume:
  media_volume:
''',
    }
    
    print("\n📝 Creating file templates...\n")
    for file_path, content in files.items():
        full_path = Path(file_path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'w') as f:
            f.write(content)
        print(f"✓ Created: {full_path}")
    
    # Make manage.py executable
    os.chmod('manage.py', 0o755)
    
    print("\n✅ File templates created successfully!\n")


def create_app_files():
    """Create initial app files with basic structure"""
    
    app_files = {
        # Config files
        'config/__init__.py': '# Config package',
        'config/urls.py': '''from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.api.urls')),
    path('api/games/', include('apps.games.api.urls')),
    path('api/', include('apps.ai_engine.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
''',
        'config/wsgi.py': '''import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_wsgi_application()
''',
        'config/celery.py': '''import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('playstudy')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
''',
        
        # Users app
        'apps/users/models.py': '''# User models will be added here''',
        'apps/users/serializers.py': '''# User serializers will be added here''',
        'apps/users/views.py': '''# User views will be added here''',
        'apps/users/api/urls.py': '''# User API URLs will be added here''',
        'apps/users/api/views.py': '''# User API views will be added here''',
        
        # Games app
        'apps/games/models.py': '''# Game models will be added here''',
        'apps/games/serializers.py': '''# Game serializers will be added here''',
        'apps/games/views.py': '''# Game views will be added here''',
        'apps/games/tasks.py': '''# Celery tasks will be added here''',
        'apps/games/api/urls.py': '''# Game API URLs will be added here''',
        'apps/games/api/views.py': '''# Game API views will be added here''',
        'apps/games/utils.py': '''# Game utilities will be added here''',
        
        # AI Engine app
        'apps/ai_engine/models.py': '''# AI Engine models will be added here''',
        'apps/ai_engine/urls.py': '''# AI Engine URLs will be added here''',
        'apps/ai_engine/rag/chroma_manager.py': '''# ChromaDB manager will be added here''',
        'apps/ai_engine/rag/retriever.py': '''# RAG retriever will be added here''',
        'apps/ai_engine/generators/base_generator.py': '''# Base generator will be added here''',
        'apps/ai_engine/generators/pixijs_generator.py': '''# PixiJS generator will be added here''',
    }
    
    print("\n📝 Creating app files...\n")
    for file_path, content in app_files.items():
        full_path = Path(file_path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'w') as f:
            f.write(content)
        print(f"✓ Created: {full_path}")
    
    print("\n✅ App files created successfully!\n")


def create_gitkeep_files():
    """Create .gitkeep files for empty directories"""
    directories = [
        'data/chroma_db',
        'data/uploads',
        'data/game_templates',
        'logs',
        'media/documents',
        'media/games',
        'static',
        'staticfiles',
    ]
    
    print("\n📝 Creating .gitkeep files...\n")
    for directory in directories:
        gitkeep_path = Path(directory) / '.gitkeep'
        gitkeep_path.parent.mkdir(parents=True, exist_ok=True)
        gitkeep_path.touch()
        print(f"✓ Created: {gitkeep_path}")
    
    print("\n✅ .gitkeep files created successfully!\n")


def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "="*70)
    print("🎉 PROJECT STRUCTURE CREATED SUCCESSFULLY!")
    print("="*70)
    print("\n📋 NEXT STEPS:\n")
    print("1. Create and activate virtual environment:")
    print("   python -m venv venv")
    print("   source venv/bin/activate  # On Windows: venv\\Scripts\\activate\n")
    
    print("2. Install dependencies:")
    print("   pip install -r requirements.txt\n")
    
    print("3. Configure environment:")
    print("   cp .env.example .env")
    print("   # Edit .env with your actual configuration\n")
    
    print("4. Run migrations:")
    print("   python manage.py makemigrations")
    print("   python manage.py migrate\n")
    
    print("5. Create superuser:")
    print("   python manage.py createsuperuser\n")
    
    print("6. Start development server:")
    print("   python manage.py runserver\n")
    
    print("7. (Optional) Start Celery worker:")
    print("   celery -A config worker --loglevel=info\n")
    
    print("="*70)
    print("\n📚 Now you can add the model, view, and API code manually!")
    print("   Check the README.md for detailed documentation.\n")
    print("="*70 + "\n")


def main():
    """Main function to run the setup"""
    print("\n" + "="*70)
    print("🚀 PLAYSTUDY BACKEND PROJECT SETUP")
    print("="*70 + "\n")
    
    try:
        # Step 1: Create directory structure
        create_directory_structure()
        
        # Step 2: Create file templates
        create_file_templates()
        
        # Step 3: Create app files
        create_app_files()
        
        # Step 4: Create .gitkeep files
        create_gitkeep_files()
        
        # Step 5: Print next steps
        print_next_steps()
        
    except Exception as e:
        print(f"\n❌ Error occurred: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()