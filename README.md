# PlayStudy Backend - RAG-Powered Game Generation

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
   source venv/bin/activate  # On Windows: venv\Scripts\activate
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
# game-learn-backend
