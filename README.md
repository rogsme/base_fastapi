# FastAPI Base Project

<p align="center">
  <img src="https://github.com/user-attachments/assets/a1c42b67-7f78-4918-ab98-4c986fb33daa" alt="base_fastapi"/>
</p>

A production-ready FastAPI template with PostgreSQL, Celery, Redis, and modern Python tooling. This template provides a solid foundation for building scalable web APIs with background task processing.

## 🚀 Features

- **FastAPI** - Modern, fast web framework with automatic API docs
- **PostgreSQL** - Robust relational database with async support
- **SQLAlchemy** - Powerful ORM with async capabilities
- **Celery + Redis** - Distributed task queue for background processing
- **Alembic** - Database migration management
- **Docker** - Containerized development and deployment
- **Modern Tooling** - UV, Ruff, MyPy, Pre-commit hooks
- **Health Checks** - Built-in monitoring endpoints
- **Type Safety** - Full type hints with MyPy validation

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.13+ (for local development)
- UV package manager (optional, for local development)

## 🏗️ Converting to Your Project

This is a template project with placeholder names. Follow these steps to convert it to your specific project:

### 1. Clone and Rename

```bash
# Clone the repository
git clone <repository-url> my-awesome-api
cd my-awesome-api

# Remove git history to start fresh
rm -rf .git
git init
```

### 2. Replace Project Names

Use these commands to replace all instances of the base project names with your project name:

```bash
# Replace "base-fastapi" with your project name (kebab-case)
find . -type f \( -name "*.py" -o -name "*.toml" -o -name "*.yml" -o -name "*.yaml" -o -name "*.md" -o -name "*.txt" \) -exec sed -i 's/base-fastapi/my-awesome-api/g' {} +

# Replace "base_fastapi" with your project name (snake_case)
find . -type f \( -name "*.py" -o -name "*.toml" -o -name "*.yml" -o -name "*.yaml" \) -exec sed -i 's/base_fastapi/my_awesome_api/g' {} +

# Replace "Base API" with your project title
find . -type f \( -name "*.py" -o -name "*.md" \) -exec sed -i 's/Base API/My Awesome API/g' {} +

# Replace "base-api" with your service name
find . -type f \( -name "*.py" -o -name "*.yml" -o -name "*.yaml" \) -exec sed -i 's/base-api/my-awesome-api/g' {} +

# Replace database names
find . -type f \( -name "*.yml" -o -name "*.yaml" \) -exec sed -i 's/POSTGRES_DB: base/POSTGRES_DB: my_awesome_api/g' {} +
find . -type f \( -name "*.yml" -o -name "*.yaml" \) -exec sed -i 's/POSTGRES_USER: base/POSTGRES_USER: my_awesome_api/g' {} +
```

### 3. Update Environment Variables

Create your `.env` file:

```bash
cp .env.example .env  # If you have an example file, or create manually
```

Update `.env` with your project-specific values:

```env
# Database
DATABASE_URL=postgresql+asyncpg://my_awesome_api:my_awesome_api123@postgres:5432/my_awesome_api
MIGRATE_DATABASE_URL=postgresql://my_awesome_api:my_awesome_api123@postgres:5432/my_awesome_api

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Environment
ENVIRONMENT=development
```

### 4. Update Docker Compose (if needed)

If you want custom database credentials, update `compose.yml`:

```yaml
postgres:
  environment:
    POSTGRES_DB: my_awesome_api
    POSTGRES_USER: my_awesome_api
    POSTGRES_PASSWORD: my_awesome_api123
```

### 5. Update pyproject.toml

```bash
# Update project metadata in pyproject.toml
sed -i 's/name = "base-fastapi"/name = "my-awesome-api"/' pyproject.toml
sed -i 's/description = "A base FastAPI project"/description = "My awesome API project"/' pyproject.toml
```

## 🚀 Getting Started

### Using Docker (Recommended)

1. **Start all services:**
   ```bash
   make dev-docker
   # or
   docker compose up
   ```

2. **Build containers:**
   ```bash
   make docker-build
   # or
   docker compose build
   ```

3. **Start only supporting services (for local API development):**
   ```bash
   make base-dev
   ```

### Local Development

1. **Install dependencies:**
   ```bash
   make install
   # or
   uv sync
   ```

2. **Start supporting services:**
   ```bash
   make base-dev
   ```

3. **Run the API locally:**
   ```bash
   make dev
   # or
   uv run src/main.py
   ```

## 📊 Services

When running with Docker, the following services will be available:

| Service | URL | Description |
|---------|-----|-------------|
| API | http://localhost:8000 | FastAPI application |
| API Docs | http://localhost:8000/docs | Interactive API documentation |
| Adminer | http://localhost:9998 | Database administration |
| Flower | http://localhost:5555 | Celery task monitoring |
| Dozzle | http://localhost:9999 | Container log viewer |

## 🗄️ Database Management

### Migrations

```bash
# Generate a new migration
make db-generate message="Add user table"

# Apply migrations
make db-upgrade

# Check current migration
make db-current

# View migration history
make db-history

# Rollback to specific revision
make db-downgrade revision="abc123"

# Reset database (⚠️ DESTRUCTIVE)
make db-reset
```

### Database Shell

```bash
# Connect to PostgreSQL
make db-shell
```

## 🔧 Development Commands

### Code Quality

```bash
# Run all checks
make check

# Format and lint code
make lint-format

# Type checking
make type-check
```

### Utilities

```bash
# Install dependencies
make install

# Clean Python cache files
make clean

# Show all available commands
make help
```

## 📁 Project Structure

```
├── src/                          # Application source code
│   ├── main.py                   # FastAPI application entry point
│   ├── constants.py              # Configuration constants
│   ├── db.py                     # Database configuration
│   ├── routes/                   # API route definitions
│   │   ├── __init__.py
│   │   └── health.py            # Health check endpoints
│   ├── services/                 # Business logic services
│   │   ├── __init__.py
│   │   └── healthcheck.py       # Health check service
│   ├── models/                   # SQLAlchemy models
│   │   └── __init__.py
│   ├── migrations/               # Alembic database migrations
│   │   ├── env.py
│   │   └── versions/
│   ├── scheduler/                # Celery configuration
│   │   ├── __init__.py
│   │   └── worker.py            # Celery worker setup
│   └── start_celery.py          # Celery startup script
├── compose.yml                   # Docker Compose configuration
├── Dockerfile                    # Application container
├── entrypoint.sh                # Container entrypoint script
├── pyproject.toml               # Python project configuration
├── uv.lock                      # Dependency lock file
├── alembic.ini                  # Alembic configuration
├── Makefile                     # Development commands
└── README.md                    # This file
```

## 🔨 Adding Features

### Adding a New Model

1. Create your model in `src/models/`:
   ```python
   # src/models/user.py
   from sqlalchemy import Column, Integer, String
   from db import Base

   class User(Base):
       __tablename__ = "users"
       
       id = Column(Integer, primary_key=True)
       name = Column(String(100), nullable=False)
       email = Column(String(255), unique=True, nullable=False)
   ```

2. Import in `src/models/__init__.py`:
   ```python
   from .user import User  # noqa: F401
   ```

3. Generate migration:
   ```bash
   make db-generate message="Add user table"
   make db-upgrade
   ```

### Adding a New Route

1. Create route file in `src/routes/`:
   ```python
   # src/routes/users.py
   from fastapi import APIRouter, Depends
   from sqlalchemy.ext.asyncio import AsyncSession
   from db import get_db

   router = APIRouter(prefix="/users", tags=["users"])

   @router.get("/")
   async def get_users(db: AsyncSession = Depends(get_db)):
       # Your logic here
       return {"users": []}
   ```

2. Include in `src/routes/__init__.py`:
   ```python
   from routes.users import router as users_router
   router.include_router(users_router)
   ```

### Adding a Celery Task

1. Add task in `src/scheduler/worker.py`:
   ```python
   @app.task
   def send_email(email: str, subject: str, body: str):
       # Your task logic here
       return f"Email sent to {email}"
   ```

2. Use in your routes:
   ```python
   from scheduler.worker import send_email
   
   # Async task
   send_email.delay("user@example.com", "Hello", "Welcome!")
   ```

## 🐳 Production Deployment

### Environment Variables

Set these in your production environment:

```env
ENVIRONMENT=production
DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/dbname
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

### Docker

```bash
# Build production image
docker build -t my-awesome-api .

# Run with external database
docker run -p 8000:8000 \
  -e DATABASE_URL="your-db-url" \
  -e CELERY_BROKER_URL="your-redis-url" \
  my-awesome-api
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and quality checks: `make check`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Useful Links

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [UV Documentation](https://docs.astral.sh/uv/)
