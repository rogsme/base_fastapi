# FastAPI Base Project Conventions

This document outlines the conventions used in the FastAPI base project template. Following these guidelines ensures consistency throughout the codebase and makes it easier for all contributors to understand and maintain the code.

## Project Structure

The project follows a modular structure with clear separation of concerns:

- `models/`: Database models using SQLAlchemy ORM
- `schemas/`: Pydantic schemas for request/response validation 
- `routes/`: FastAPI routes and endpoint definitions
- `services/`: Business logic and external service integrations
- `middlewares/`: FastAPI middleware components
- `tools/`: Utility scripts for development and administrative tasks
- `scheduler/`: Celery tasks and worker configurations for background processing
- `migrations/`: Alembic database migration files
- `tests/`: Test suite mirroring the main project structure

## Import Conventions

- **Always use absolute imports**, never relative imports
- Import order should be:
  1. Standard library imports
  2. Third-party library imports
  3. Local application imports
- Group imports by type with a blank line between groups
- Sort imports alphabetically within each group

Example:
```python
from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from services.auth import AuthService
```

## Type Annotations

- All function parameters and return values must have type annotations
- Use `Optional[Type]` for parameters that can be None
- Use `Type | None` syntax for Python 3.10+ Optional type annotation alternative
- Use appropriate collection type annotations (e.g., `List[str]`, `Dict[str, Any]`)
- Import type-related modules from `typing` package
- Use `TypeVar` for generic type hints when appropriate

Example:
```python
from typing import List, Optional, TypeVar

T = TypeVar("T", bound="UserResponse")

async def get_user_by_id(user_id: int) -> Optional[User]:
    """Get a user by ID."""
    ...
```

## Error Handling

- Use custom exception classes defined within service classes
- Catch specific exceptions rather than using bare `except` statements
- Document all raised exceptions in function docstrings
- In routes, convert service exceptions to appropriate HTTPExceptions with status codes
- Always include descriptive error messages in exceptions

Example:
```python
class UserService:
    class UserNotFoundError(ValueError):
        """Raised when the user is not found."""
        
    class InvalidCredentialsError(ValueError):
        """Raised when user credentials are invalid."""
        
    async def authenticate_user(email: str, password: str) -> User:
        """Authenticate user with email and password.
        
        Args:
            email: The user's email address
            password: The user's password
            
        Raises:
            UserNotFoundError: If the user is not found
            InvalidCredentialsError: If credentials are invalid
        """
        ...
```

## Naming Conventions

- **Class names**: PascalCase (e.g., `UserService`, `EmailNotifier`)
- **Function/method names**: snake_case (e.g., `get_user_by_id`, `send_notification`)
- **Variable names**: snake_case (e.g., `user_email`, `created_at`)
- **Constant names**: UPPER_SNAKE_CASE (e.g., `MAX_RETRY_ATTEMPTS`, `DEFAULT_TIMEOUT`)
- **Private methods/variables**: Prefix with underscore (e.g., `_validate_email`)
- **Database models**: Singular nouns (e.g., `User`, `Order`, not `Users`)
- **Route names**: Plural nouns (e.g., `/users`, `/orders`, not `/user`)

## Documentation

- All modules, classes, methods, and functions should have docstrings
- Use **Google style** docstrings with Args, Returns, and Raises sections
- Include examples in docstrings when helpful
- Document complex algorithms or business rules with inline comments
- When you update code, do not add inline comments explaining the "Updated" or "End updated" code
- API endpoints should have descriptions and response documentation

Example:
```python
async def process_user_registration(user_data: dict) -> User:
    """Process new user registration.
    
    Args:
        user_data: Dictionary containing user registration information
        
    Returns:
        The newly created user object
        
    Raises:
        ValidationError: If user data is invalid
        DuplicateEmailError: If email already exists
    """
    # Implementation...
```

## API Design

- Use appropriate HTTP methods (GET, POST, PUT, DELETE) for CRUD operations
- Include descriptive summaries and descriptions in route decorators
- Document all possible response status codes
- Return structured error responses with consistent format
- Use path parameters for resource identifiers (user IDs, order IDs)
- Use query parameters for filtering, pagination, and sorting
- Version the API using URL path versioning if needed

Example:
```python
@router.get(
    "/{user_id}/orders",
    response_model=List[OrderResponse],
    summary="Get User Orders",
    description="Retrieve all orders for a specific user.",
    responses={
        200: {"description": "Successfully retrieved user orders"},
        400: {"description": "Invalid user ID format"},
        404: {"description": "User not found"},
    },
)
async def get_user_orders(
    user_id: int = Path(..., description="The user ID")
) -> List[OrderResponse]:
    ...
```

## Models and Schemas

- **SQLAlchemy models**: Define database schema and behavior
  - Use descriptive table names
  - Define foreign key relationships explicitly
  - Include appropriate indexes for performance
  - Use constraints for data integrity

- **Pydantic schemas**: Define API request/response validation
  - Include example values for fields when possible
  - Define required vs optional fields explicitly
  - Use field validation for complex validation logic
  - Include descriptive field titles and descriptions

Example:
```python
# SQLAlchemy model
class User(Base):
    """User model for database storage."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    orders = relationship("Order", back_populates="user")

# Pydantic schema
class UserResponse(BaseModel):
    """Schema for user responses."""
    
    id: int = Field(
        ...,
        title="User ID",
        description="The unique identifier for the user",
        examples=[123],
    )
    email: str = Field(
        ...,
        title="Email Address",
        description="The user's email address",
        examples=["user@example.com"],
    )
    is_active: bool = Field(
        ...,
        title="Active Status",
        description="Whether the user account is active",
        examples=[True],
    )
    
    class Config:
        from_attributes = True
```

## Database Conventions

### Migration Handling
- Always generate migrations for model changes using Alembic
- Include descriptive messages for migrations
- Review migration files before applying them
- Test migrations on development data before production
- Use proper naming for indexes and constraints

### Query Patterns
- Use async sessions consistently
- Implement proper pagination for large datasets
- Use select() for queries instead of legacy Query API
- Include proper error handling for database operations
- Use transactions for operations that modify multiple records

Example:
```python
async def get_users_paginated(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> List[User]:
    """Get paginated list of users."""
    result = await db.execute(
        select(User)
        .where(User.is_active == True)
        .offset(skip)
        .limit(limit)
        .order_by(User.created_at.desc())
    )
    return result.scalars().all()
```

## Testing Conventions

### Test Organization

- Test files should mirror the structure of the source code (`tests/services/` for `services/`, etc.)
- Name test files with `test_` prefix (e.g., `test_user_service.py`)
- Name test functions with `test_` prefix (e.g., `test_create_user`)
- For complex test suites, organize related tests into classes with a descriptive name (e.g., `TestUserAuthentication`)
- Group tests by functionality or feature within a class

### Database Testing

- Use test database separate from development database
- Use database transactions that roll back after each test
- Create fixtures for common test data
- Test both success and failure scenarios
- Include edge cases and validation testing

### Test Fixtures

- Use pytest fixtures for common setup/teardown
- Define fixtures at the most appropriate scope (function, class, module, session)
- Create specialized fixtures with descriptive names (e.g., `mock_email_service`, `sample_user`)
- Use factory patterns for generating test data

Example:
```python
@pytest.fixture
async def sample_user(db_session: AsyncSession):
    """Create a sample user for testing."""
    user = User(
        email="test@example.com",
        hashed_password="hashed_password_here",
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user
```

## Service Layer Conventions

- Business logic should reside in service classes
- Service methods should be stateless when possible
- When services need to be instantiated, use dependency injection
- Define custom exceptions as inner classes of service classes
- Validate inputs at the service layer, not just in schemas
- Use async/await consistently for I/O operations

Example:
```python
class UserService:
    """Service for user-related operations."""
    
    class UserNotFoundError(ValueError):
        """Raised when a user is not found."""
    
    class DuplicateEmailError(ValueError):
        """Raised when email already exists."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_user(self, user_data: dict) -> User:
        """Create a new user."""
        # Implementation...
```

## Background Task Conventions

### Celery Task Design
- Define tasks with clear, descriptive names
- Include proper error handling and retry logic
- Use appropriate task queues for different types of work
- Log task execution and failures
- Keep tasks idempotent when possible

### Task Organization
- Group related tasks in logical modules
- Use consistent naming patterns for tasks
- Document task parameters and expected behavior
- Implement proper task monitoring and alerting

Example:
```python
@app.task(bind=True, max_retries=3)
def send_welcome_email(self, user_id: int) -> str:
    """Send welcome email to new user.
    
    Args:
        user_id: The ID of the user to send email to
        
    Returns:
        Status message indicating success or failure
    """
    try:
        # Email sending logic
        return f"Welcome email sent to user {user_id}"
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

## Security Considerations

### API Security
- Implement rate limiting on all endpoints
- Use proper authentication and authorization
- Validate all user inputs to prevent injection attacks
- Sanitize data before database operations
- Log security-relevant events
- Use HTTPS in production

### Data Protection
- Hash passwords using secure algorithms (bcrypt, Argon2)
- Never log sensitive information (passwords, tokens)
- Implement proper session management
- Use environment variables for secrets
- Validate file uploads and limit file sizes

## Performance Considerations

### Database Optimization
- Index frequently queried fields
- Use appropriate pagination for large result sets
- Implement caching for frequently accessed data
- Use database connection pooling
- Monitor query performance and optimize slow queries

### API Performance
- Implement response caching where appropriate
- Use async operations for I/O bound tasks
- Optimize serialization for large responses
- Monitor API response times
- Implement proper logging for performance debugging

## Environment Configuration

### Required Environment Variables
```python
# Database configuration
DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/dbname"
MIGRATE_DATABASE_URL = "postgresql://user:password@localhost:5432/dbname"

# Celery configuration
CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"

# Application configuration
SECRET_KEY = "your-secret-key"
DEBUG = "false"
ENVIRONMENT = "production"

# External service configuration
EMAIL_SERVICE_API_KEY = "your-email-api-key"
```

## Coding Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications
- Line length: 88 characters (Black default)
- Use Ruff for linting and formatting
- Indentation: 4 spaces
- Use double quotes for strings
- Function arguments on one line when they fit, otherwise one per line
- Include trailing commas in multi-line collections
- Sort imports with isort
- Keep functions and methods concise and focused

## Dependencies and Libraries

### Preferred Libraries
- **HTTP requests**: `httpx` over `requests` for async support
- **Date/time**: `datetime` and `pytz` for timezone-aware timestamps
- **Validation**: `pydantic` for data validation and serialization
- **Async operations**: `asyncio` for concurrent operations
- **Testing**: `pytest` with `pytest-asyncio` for async testing
- **Environment**: `python-dotenv` for environment variable management

### Environment and Deployment
- Use Python 3.13+ features
- Manage dependencies with `uv`
- Define dependencies in `pyproject.toml`
- Store configuration in environment variables
- Use Docker for containerized deployment

## AI Assistance Guidelines

When working with this codebase via AI coding assistants, follow these guidelines:

### Code Generation Patterns
- Always include proper type hints and docstrings
- Follow the established project structure and conventions
- Implement proper error handling and validation
- Use async/await patterns consistently
- Include appropriate tests for new functionality

### Database Operations
- Use SQLAlchemy async patterns
- Include proper transaction handling
- Implement pagination for list endpoints
- Use appropriate indexes and constraints
- Handle database connection errors gracefully

### API Development
- Follow REST conventions for endpoint design
- Include proper request/response validation
- Implement appropriate status codes
- Add comprehensive documentation
- Consider rate limiting and security implications

### Testing Approach
- Write tests that cover both success and failure cases
- Use appropriate fixtures and mocking
- Test database operations with proper cleanup
- Include integration tests for critical flows
- Maintain good test coverage

When generating code, always consider the asynchronous nature of the application and the need for proper error handling, validation, and testing in a production environment.
