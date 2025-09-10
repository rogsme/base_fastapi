# Testing Documentation

This document provides comprehensive guidance on testing in the FastAPI Base Project. The testing setup is designed to be robust, fast, and easy to use while maintaining high code quality and coverage.

## 📚 Table of Contents

- [Overview](#-overview)
- [Quick Start](#-quick-start)
- [Test Architecture](#-test-architecture)
- [Running Tests](#-running-tests)
- [Test Database](#-test-database)
- [Fixtures](#-fixtures)
- [Writing Tests](#-writing-tests)
- [Testing Patterns](#-testing-patterns)
- [Mocking and Stubbing](#-mocking-and-stubbing)
- [Coverage Reports](#-coverage-reports)
- [Performance Testing](#-performance-testing)
- [Debugging Tests](#-debugging-tests)
- [Best Practices](#-best-practices)
- [Troubleshooting](#-troubleshooting)

## 🎯 Overview

The testing framework is built around these core principles:

- **Fast execution** - SQLite in-memory database for speed
- **Isolated tests** - Each test runs in isolation with clean state
- **Async support** - Full support for async/await patterns
- **Type safety** - Complete type hints in test code
- **Comprehensive coverage** - Tests for all layers (routes, services, models)
- **Easy debugging** - Clear error messages and debugging support

### Technology Stack

- **pytest** - Primary testing framework with rich plugin ecosystem
- **pytest-asyncio** - Async test support with automatic event loop management
- **httpx** - Modern async HTTP client for API testing
- **SQLite** - In-memory database for lightning-fast tests
- **pytest-cov** - Coverage reporting with multiple output formats
- **pytest-mock** - Mocking utilities built on top of unittest.mock
- **pytest-randomly** - Randomize test order to catch hidden dependencies
- **pytest-xdist** - Parallel test execution for faster runs

## 🚀 Quick Start

### Install Dependencies

```bash
# Install all dependencies including dev dependencies
make install
# or
uv sync
```

### Run Your First Test

```bash
# Run all tests
make test

# Run with verbose output to see what's happening
make test-verbose

# Run with coverage to see what code is tested
make test-coverage
```

### Basic Test Example

```python
import pytest
from httpx import AsyncClient
from fastapi import status

class TestMyFirstFeature:
    """Test cases for my first feature."""
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self, async_client: AsyncClient):
        """Test that the health endpoint works."""
        response = await async_client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
```

## 🏗️ Test Architecture

### Directory Structure

```
src/tests/
├── conftest.py             # Global pytest configuration and fixtures
├── test_db.py              # Test database configuration
├── __init__.py
├── routes/                 # API endpoint tests
│   ├── __init__.py
│   └── test_health.py      # Health endpoint tests
├── services/               # Business logic tests
│   ├── __init__.py
│   └── test_healthcheck.py # Health service tests
└── models/                 # Database model tests
    └── __init__.py
```

### Test Categories

1. **Unit Tests** (`services/`, `models/`) - Test individual components in isolation
2. **Integration Tests** - Test interactions between components
3. **API Tests** (`routes/`) - Test HTTP endpoints and request/response cycles
4. **Database Tests** - Test database operations and model behavior
5. **Task Tests** - Test background Celery tasks (when added)

### Naming Conventions

- **Test files**: `test_*.py` (e.g., `test_user_service.py`)
- **Test classes**: `TestClassName` (e.g., `TestUserService`)
- **Test methods**: `test_method_name` (e.g., `test_create_user_success`)
- **Descriptive names**: Use clear, descriptive names that explain what is being tested

## 🏃‍♂️ Running Tests

### Basic Commands

```bash
# Run all tests
make test

# Run tests in specific directory
uv run pytest src/tests/routes/
uv run pytest src/tests/services/

# Run specific test file
uv run pytest src/tests/routes/test_health.py

# Run specific test class
uv run pytest src/tests/routes/test_health.py::TestHealthEndpoint

# Run specific test method
uv run pytest src/tests/routes/test_health.py::TestHealthEndpoint::test_health_check_sync
```

### Advanced Options

```bash
# Run with verbose output (-v shows test names, -vv shows more details)
uv run pytest -v
uv run pytest -vv
make test-verbose

# Run with coverage
uv run pytest --cov=src --cov-report=html --cov-report=term-missing
make test-coverage

# Run in parallel (faster for large test suites)
uv run pytest -n auto

# Run only failed tests from last run
uv run pytest --lf

# Run tests and drop into debugger on failure
uv run pytest --pdb

# Stop after first failure
uv run pytest -x

# Show local variables in tracebacks
uv run pytest -l

# Run tests matching a pattern
uv run pytest -k "health"
uv run pytest -k "test_create and not slow"

# Run tests with specific markers
uv run pytest -m "slow"
uv run pytest -m "not integration"
```

### Makefile Commands

All the common test commands are available through the Makefile:

```bash
make test                    # Run all tests
make test-verbose           # Run with verbose output
make test-coverage          # Run with coverage report
make test-specific path="src/tests/routes/test_health.py"
```

### Environment Variables

Tests automatically use the `testing` environment:

```bash
# Explicitly set test environment (usually automatic)
ENVIRONMENT=testing pytest

# Run tests with different log levels
PYTEST_LOG_LEVEL=DEBUG pytest -s
```

## 🗄️ Test Database

### Configuration

The test database is configured in `test_db.py` using SQLite in-memory for maximum speed:

```python
# src/tests/test_db.py
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,  # Set to True for SQL query debugging
    poolclass=StaticPool,
    connect_args={"check_same_thread": False},
)
```

### Key Features

- **In-memory** - Extremely fast, no disk I/O, perfect for CI/CD
- **Isolated** - Each test gets a completely fresh database
- **Async support** - Full async/await compatibility with asyncpg patterns
- **Auto-cleanup** - Tables created and dropped automatically
- **No interference** - Tests never affect your development database

### Database Lifecycle

Each test follows this lifecycle:

```python
@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    # 1. Create all tables from models
    await create_test_tables()
    
    # 2. Provide clean session to test
    async with TestAsyncSessionLocal() as session:
        try:
            yield session  # Test runs here
        finally:
            await session.close()
    
    # 3. Clean up - drop all tables
    await drop_test_tables()
```

### Working with Test Database

```python
@pytest.mark.asyncio
async def test_database_operation(db_session: AsyncSession):
    """Example of testing database operations."""
    from models.user import User
    from sqlalchemy import select
    
    # Create test data
    user = User(name="Test User", email="test@example.com")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # Verify the data was created
    assert user.id is not None
    assert user.name == "Test User"
    
    # Query the data
    result = await db_session.execute(select(User))
    users = result.scalars().all()
    assert len(users) == 1
    assert users[0].email == "test@example.com"
```

### Database Debugging

To see SQL queries during test development:

```python
# In test_db.py, temporarily set echo=True
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=True,  # This will print all SQL queries
    poolclass=StaticPool,
    connect_args={"check_same_thread": False},
)
```

## 🔧 Fixtures

Fixtures provide reusable test setup and teardown. The project includes several powerful fixtures in `conftest.py`:

### Core Fixtures

```python
# Database session - fresh for each test
@pytest.mark.asyncio
async def test_with_database(db_session: AsyncSession):
    """Test that needs database access."""
    # Your test code here - db_session is clean and ready
    pass

# FastAPI app with overridden dependencies
@pytest.mark.asyncio
async def test_with_app(test_app: FastAPI):
    """Test that needs the FastAPI app."""
    # test_app has database dependency overridden to use test DB
    pass
```

### HTTP Client Fixtures

```python
# Synchronous client - good for simple tests
def test_simple_endpoint(sync_client: TestClient):
    """Test using synchronous client."""
    response = sync_client.get("/health")
    assert response.status_code == 200

# Asynchronous client - recommended for most tests
@pytest.mark.asyncio
async def test_async_endpoint(async_client: AsyncClient):
    """Test using async client - preferred approach."""
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
```

### Creating Custom Fixtures

Add your own fixtures to `conftest.py`:

```python
@pytest.fixture
def sample_user_data() -> dict:
    """Provide sample user data for testing."""
    return {
        "name": "John Doe",
        "email": "john@example.com",
        "is_active": True,
        "role": "user"
    }

@pytest.fixture
async def created_user(db_session: AsyncSession, sample_user_data: dict) -> User:
    """Create a user in the database for testing."""
    user = User(**sample_user_data)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture(scope="class")
def expensive_setup():
    """Expensive setup shared across test class."""
    # Expensive initialization (e.g., loading large dataset)
    setup_data = load_expensive_data()
    yield setup_data
    # Cleanup
    cleanup_expensive_data(setup_data)
```

### Fixture Scopes

Understanding fixture scopes helps optimize test performance:

- `function` (default) - New instance for each test function
- `class` - New instance for each test class (shared across methods)
- `module` - New instance for each test module
- `session` - One instance for entire test session

```python
@pytest.fixture(scope="session")
def app_config():
    """App configuration shared across all tests."""
    return {"debug": False, "testing": True}

@pytest.fixture(scope="class")
def shared_test_data():
    """Data shared across test class methods."""
    return {"shared_value": "test_data"}
```

## ✍️ Writing Tests

### Test Organization Strategy

Organize tests to mirror your application structure:

```python
class TestUserService:
    """Test cases for UserService.
    
    Groups related tests together and provides clear organization.
    Use descriptive docstrings to explain the test purpose.
    """
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, db_session: AsyncSession):
        """Test successful user creation with valid data."""
        # Implementation here
        pass
    
    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, db_session: AsyncSession):
        """Test that creating user with duplicate email raises appropriate error."""
        # Implementation here
        pass
    
    @pytest.mark.asyncio
    async def test_create_user_invalid_email(self, db_session: AsyncSession):
        """Test that creating user with invalid email format fails."""
        # Implementation here
        pass
```

### API Endpoint Testing

Test your FastAPI endpoints thoroughly:

```python
from fastapi import status
from httpx import AsyncClient

class TestUserRoutes:
    """Test cases for user API routes."""
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, async_client: AsyncClient):
        """Test successful user creation via API."""
        user_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "is_active": True
        }
        
        response = await async_client.post("/users", json=user_data)
        
        # Test response status
        assert response.status_code == status.HTTP_201_CREATED
        
        # Test response data
        data = response.json()
        assert data["name"] == user_data["name"]
        assert data["email"] == user_data["email"]
        assert data["is_active"] == user_data["is_active"]
        
        # Test auto-generated fields
        assert "id" in data
        assert "created_at" in data
        assert data["id"] > 0
    
    @pytest.mark.asyncio
    async def test_get_user_success(self, async_client: AsyncClient, created_user: User):
        """Test getting an existing user by ID."""
        response = await async_client.get(f"/users/{created_user.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == created_user.id
        assert data["name"] == created_user.name
        assert data["email"] == created_user.email
    
    @pytest.mark.asyncio
    async def test_get_user_not_found(self, async_client: AsyncClient):
        """Test getting non-existent user returns 404."""
        response = await async_client.get("/users/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_create_user_validation_errors(self, async_client: AsyncClient):
        """Test user creation with invalid data returns validation errors."""
        invalid_data = {
            "name": "",  # Empty name
            "email": "not-an-email",  # Invalid email format
        }
        
        response = await async_client.post("/users", json=invalid_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data
        
        # Check that validation errors are descriptive
        errors = data["detail"]
        assert len(errors) >= 2  # At least name and email errors
    
    @pytest.mark.asyncio
    async def test_list_users_pagination(self, async_client: AsyncClient):
        """Test user listing with pagination."""
        # Create multiple users first
        for i in range(5):
            user_data = {
                "name": f"User {i}",
                "email": f"user{i}@example.com"
            }
            await async_client.post("/users", json=user_data)
        
        # Test pagination
        response = await async_client.get("/users?skip=0&limit=3")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3
        
        # Test second page
        response = await async_client.get("/users?skip=3&limit=3")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2  # Remaining users
```

### Service Layer Testing

Test your business logic thoroughly:

```python
from services.user_service import UserService
from models.user import User

class TestUserService:
    """Test cases for UserService business logic."""
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, db_session: AsyncSession):
        """Test user creation through service layer."""
        service = UserService(db_session)
        user_data = {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "is_active": True
        }
        
        user = await service.create_user(user_data)
        
        # Test returned object
        assert isinstance(user, User)
        assert user.name == user_data["name"]
        assert user.email == user_data["email"]
        assert user.is_active == user_data["is_active"]
        
        # Test database persistence
        assert user.id is not None
        assert user.created_at is not None
    
    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, db_session: AsyncSession):
        """Test creating user with duplicate email raises custom error."""
        service = UserService(db_session)
        user_data = {"name": "Test", "email": "test@example.com"}
        
        # Create first user
        await service.create_user(user_data)
        
        # Attempt to create second user with same email
        with pytest.raises(UserService.DuplicateEmailError) as exc_info:
            await service.create_user(user_data)
        
        # Test error message is helpful
        assert "test@example.com" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_user_by_email(self, db_session: AsyncSession, created_user: User):
        """Test getting user by email address."""
        service = UserService(db_session)
        
        user = await service.get_user_by_email(created_user.email)
        
        assert user is not None
        assert user.id == created_user.id
        assert user.email == created_user.email
        assert user.name == created_user.name
    
    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, db_session: AsyncSession):
        """Test getting non-existent user by email returns None."""
        service = UserService(db_session)
        
        user = await service.get_user_by_email("nonexistent@example.com")
        
        assert user is None
    
    @pytest.mark.asyncio
    async def test_update_user_success(self, db_session: AsyncSession, created_user: User):
        """Test updating user information."""
        service = UserService(db_session)
        update_data = {
            "name": "Updated Name",
            "is_active": False
        }
        
        updated_user = await service.update_user(created_user.id, update_data)
        
        assert updated_user.name == update_data["name"]
        assert updated_user.is_active == update_data["is_active"]
        assert updated_user.email == created_user.email  # Unchanged
        
    @pytest.mark.asyncio
    async def test_delete_user_success(self, db_session: AsyncSession, created_user: User):
        """Test user deletion."""
        service = UserService(db_session)
        
        result = await service.delete_user(created_user.id)
        
        assert result is True
        
        # Verify user is actually deleted
        deleted_user = await service.get_user_by_id(created_user.id)
        assert deleted_user is None
```

### Database Model Testing

Test your SQLAlchemy models:

```python
from models.user import User
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

class TestUserModel:
    """Test cases for User database model."""
    
    @pytest.mark.asyncio
    async def test_create_user_basic(self, db_session: AsyncSession):
        """Test basic user model creation and persistence."""
        user = User(
            name="Test User",
            email="test@example.com",
            is_active=True
        )
        
        # Add to session and commit
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # Test auto-generated fields
        assert user.id is not None
        assert user.created_at is not None
        
        # Test stored values
        assert user.name == "Test User"
        assert user.email == "test@example.com"
        assert user.is_active is True
    
    @pytest.mark.asyncio
    async def test_user_unique_email_constraint(self, db_session: AsyncSession):
        """Test that email uniqueness is enforced at database level."""
        # Create first user
        user1 = User(name="User 1", email="same@example.com")
        db_session.add(user1)
        await db_session.commit()
        
        # Try to create second user with same email
        user2 = User(name="User 2", email="same@example.com")
        db_session.add(user2)
        
        with pytest.raises(IntegrityError):
            await db_session.commit()
    
    @pytest.mark.asyncio
    async def test_user_relationships(self, db_session: AsyncSession):
        """Test user model relationships."""
        from models.order import Order
        from sqlalchemy.orm import selectinload
        
        # Create user
        user = User(name="Test User", email="test@example.com")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # Create related orders
        order1 = Order(user_id=user.id, total_amount=100.0)
        order2 = Order(user_id=user.id, total_amount=200.0)
        db_session.add_all([order1, order2])
        await db_session.commit()
        
        # Test relationship loading
        result = await db_session.execute(
            select(User).options(selectinload(User.orders)).where(User.id == user.id)
        )
        user_with_orders = result.scalar_one()
        
        assert len(user_with_orders.orders) == 2
        assert sum(order.total_amount for order in user_with_orders.orders) == 300.0
    
    @pytest.mark.asyncio
    async def test_user_string_representation(self, db_session: AsyncSession):
        """Test user model string representation."""
        user = User(name="Test User", email="test@example.com")
        
        # Test __repr__ or __str__ methods if implemented
        assert "Test User" in str(user)
        assert "test@example.com" in str(user)
```

### Background Task Testing

When you add Celery tasks, test them like this:

```python
from scheduler.worker import send_welcome_email, run_func

class TestEmailTasks:
    """Test cases for email background tasks."""
    
    def test_send_welcome_email_sync(self):
        """Test synchronous welcome email task."""
        result = send_welcome_email("user@example.com", "John Doe")
        
        assert "Welcome email sent" in result
        assert "user@example.com" in result
        assert "John Doe" in result
    
    @pytest.mark.asyncio
    async def test_send_welcome_email_async(self):
        """Test async email task using run_func helper."""
        # For async tasks, use the run_func helper from worker.py
        result = run_func(send_welcome_email_async, "user@example.com", "John Doe")
        
        assert result["status"] == "sent"
        assert result["recipient"] == "user@example.com"
        assert result["name"] == "John Doe"
    
    @patch('scheduler.worker.EmailService')
    def test_send_email_with_mock(self, mock_email_service):
        """Test email task with mocked email service."""
        mock_email_service.send.return_value = {"success": True, "message_id": "123"}
        
        result = send_welcome_email("user@example.com", "John Doe")
        
        # Verify mock was called correctly
        mock_email_service.send.assert_called_once_with(
            to="user@example.com",
            subject="Welcome John Doe!",
            template="welcome",
            context={"name": "John Doe"}
        )
        
        assert "success" in result.lower()
```

## 🎭 Testing Patterns

### Arrange-Act-Assert (AAA) Pattern

Structure your tests clearly:

```python
@pytest.mark.asyncio
async def test_user_creation_follows_aaa_pattern(self, db_session: AsyncSession):
    """Example test following AAA pattern."""
    # Arrange - Set up test data and dependencies
    service = UserService(db_session)
    user_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "is_active": True
    }
    
    # Act - Perform the action being tested
    created_user = await service.create_user(user_data)
    
    # Assert - Verify the results
    assert created_user.name == user_data["name"]
    assert created_user.email == user_data["email"]
    assert created_user.is_active == user_data["is_active"]
    assert created_user.id is not None
```

### Given-When-Then Pattern

For behavior-driven development style:

```python
@pytest.mark.asyncio
async def test_user_login_with_invalid_credentials(self, async_client: AsyncClient):
    """Test user login behavior with invalid credentials."""
    # Given: A user exists in the system
    user_data = {"name": "John", "email": "john@example.com", "password": "secret123"}
    await async_client.post("/users", json=user_data)
    
    # When: User attempts to login with wrong password
    login_data = {"email": "john@example.com", "password": "wrongpassword"}
    response = await async_client.post("/auth/login", json=login_data)
    
    # Then: Login should fail with appropriate error
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert "invalid credentials" in data["detail"].lower()
```

### Parametrized Tests

Test multiple scenarios efficiently:

```python
@pytest.mark.parametrize("email,expected_valid", [
    ("valid@example.com", True),
    ("also.valid+tag@example.org", True),
    ("invalid.email", False),
    ("@example.com", False),
    ("user@", False),
    ("", False),
])
@pytest.mark.asyncio
async def test_email_validation(self, async_client: AsyncClient, email: str, expected_valid: bool):
    """Test email validation with various inputs."""
    user_data = {"name": "Test User", "email": email}
    response = await async_client.post("/users", json=user_data)
    
    if expected_valid:
        assert response.status_code == status.HTTP_201_CREATED
    else:
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.parametrize("user_data,expected_error", [
    ({"name": "", "email": "test@example.com"}, "name"),
    ({"name": "Test", "email": ""}, "email"),
    ({"name": "Test"}, "email"),  # Missing email
    ({"email": "test@example.com"}, "name"),  # Missing name
    ({}, "name"),  # Empty data
])
@pytest.mark.asyncio
async def test_user_creation_validation(self, async_client: AsyncClient, user_data: dict, expected_error: str):
    """Test user creation validation for various invalid inputs."""
    response = await async_client.post("/users", json=user_data)
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    error_detail = response.json()["detail"]
    
    # Check that the expected field is mentioned in error
    assert any(expected_error in str(error).lower() for error in error_detail)
```

### Error Testing

Test error conditions thoroughly:

```python
@pytest.mark.asyncio
async def test_service_error_handling(self, db_session: AsyncSession):
    """Test that service handles database errors gracefully."""
    service = UserService(db_session)
    
    # Test with invalid database session
    await db_session.close()  # Close the session to simulate error
    
    with pytest.raises(UserService.DatabaseError) as exc_info:
        await service.create_user({"name": "Test", "email": "test@example.com"})
    
    assert "database connection" in str(exc_info.value).lower()

@pytest.mark.asyncio
async def test_api_error_responses(self, async_client: AsyncClient):
    """Test that API returns proper error responses."""
    # Test 404 error
    response = await async_client.get("/users/999999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    
    error_data = response.json()
    assert "detail" in error_data
    assert "not found" in error_data["detail"].lower()
    
    # Test 422 validation error
    response = await async_client.post("/users", json={"invalid": "data"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    error_data = response.json()
    assert "detail" in error_data
    assert isinstance(error_data["detail"], list)
```

## 🎭 Mocking and Stubbing

### When to Use Mocks

Use mocks to:
- Isolate units under test
- Simulate external services (email, payment APIs)
- Control error conditions
- Speed up tests by avoiding slow operations

### Basic Mocking with pytest-mock

```python
from unittest.mock import AsyncMock, patch

class TestEmailService:
    """Test email functionality with mocks."""
    
    @patch('services.email_service.EmailProvider')
    @pytest.mark.asyncio
    async def test_send_email_success(self, mock_email_provider, db_session: AsyncSession):
        """Test successful email sending with mocked provider."""
        # Arrange
        mock_email_provider.send_async.return_value = {
            "success": True,
            "message_id": "msg_123456"
        }
        
        service = EmailService(db_session)
        
        # Act
        result = await service.send_welcome_email("user@example.com", "John Doe")
        
        # Assert
        assert result["success"] is True
        mock_email_provider.send_async.assert_called_once_with(
            to="user@example.com",
            subject="Welcome John Doe!",
            template="welcome",
            context={"name": "John Doe"}
        )
    
    @patch('services.email_service.EmailProvider')
    @pytest.mark.asyncio
    async def test_send_email_failure(self, mock_email_provider, db_session: AsyncSession):
        """Test email sending failure handling."""
        # Arrange
        mock_email_provider.send_async.side_effect = EmailProviderError("Service unavailable")
        
        service = EmailService(db_session)
        
        # Act & Assert
        with pytest.raises(EmailService.EmailSendError) as exc_info:
            await service.send_welcome_email("user@example.com", "John Doe")
        
        assert "Service unavailable" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_email_with_mock_fixture(self, mocker, db_session: AsyncSession):
        """Test using pytest-mock's mocker fixture."""
        # Create mock using mocker fixture (recommended approach)
        mock_send = mocker.patch('services.email_service.EmailProvider.send_async')
        mock_send.return_value = {"success": True, "message_id": "123"}
        
        service = EmailService(db_session)
        result = await service.send_welcome_email("test@example.com", "Test User")
        
        assert result["success"] is True
        mock_send.assert_called_once()

class TestExternalAPIIntegration:
    """Test external API integration with mocks."""
    
    @pytest.mark.asyncio
    async def test_payment_processing_mock(self, mocker, db_session: AsyncSession):
        """Test payment processing with mocked payment gateway."""
        # Mock the payment gateway
        mock_payment_gateway = mocker.patch('services.payment_service.PaymentGateway')
        mock_payment_gateway.charge.return_value = {
            "success": True,
            "transaction_id": "txn_123456",
            "amount": 100.00
        }
        
        service = PaymentService(db_session)
        
        result = await service.process_payment({
            "amount": 100.00,
            "currency": "USD",
            "card_token": "card_token_123"
        })
        
        assert result["success"] is True
        assert result["transaction_id"] == "txn_123456"
        mock_payment_gateway.charge.assert_called_once()
```

### Advanced Mocking Patterns

```python
class TestAdvancedMocking:
    """Advanced mocking patterns and techniques."""
    
    @pytest.mark.asyncio
    async def test_mock_with_side_effects(self, mocker, db_session: AsyncSession):
        """Test using side_effect for complex mock behavior."""
        mock_api_call = mocker.patch('services.external_service.api_call')
        
        # Mock different responses for multiple calls
        mock_api_call.side_effect = [
            {"status": "pending"},
            {"status": "processing"},
            {"status": "completed", "result": "success"}
        ]
        
        service = ExternalService(db_session)
        
        # First call
        result1 = await service.check_status("job_123")
        assert result1["status"] == "pending"
        
        # Second call
        result2 = await service.check_status("job_123")
        assert result2["status"] == "processing"
        
        # Third call
        result3 = await service.check_status("job_123")
        assert result3["status"] == "completed"
        
        assert mock_api_call.call_count == 3
    
    @pytest.mark.asyncio
    async def test_mock_async_context_manager(self, mocker):
        """Test mocking async context managers."""
        mock_session = AsyncMock()
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None
        mock_session.get.return_value = {"data": "test"}
        
        mocker.patch('aiohttp.ClientSession', return_value=mock_session)
        
        service = HTTPService()
        result = await service.fetch_data("http://example.com")
        
        assert result["data"] == "test"
        mock_session.__aenter__.assert_called_once()
        mock_session.__aexit__.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_partial_mocking(self, mocker, db_session: AsyncSession):
        """Test partial mocking - mock some methods but not others."""
        service = UserService(db_session)
        
        # Mock only the email validation method
        mocker.patch.object(service, '_validate_email', return_value=True)
        
        # Real method calls will work, but email validation is mocked
        user_data = {"name": "Test", "email": "invalid-email-format"}
        user = await service.create_user(user_data)  # Won't fail due to mocked validation
        
        assert user.email == "invalid-email-format"
    
    def test_mock_configuration(self, mocker):
        """Test configuring mocks with spec and autospec."""
        # Use spec to ensure mock has same interface as real object
        mock_service = mocker.Mock(spec=UserService)
        mock_service.create_user.return_value = User(id=1, name="Test")
        
        # This will work - method exists on UserService
        result = mock_service.create_user({"name": "Test"})
        assert result.name == "Test"
        
        # This would raise AttributeError - method doesn't exist on UserService
        # mock_service.nonexistent_method()  # Would fail with spec
```

### Mocking Best Practices

```python
class TestMockingBestPractices:
    """Examples of mocking best practices."""
    
    @pytest.mark.asyncio
    async def test_mock_at_boundary(self, mocker, db_session: AsyncSession):
        """Mock at the system boundary, not internal methods."""
        # Good: Mock external dependency
        mock_email_client = mocker.patch('services.email_service.SMTPClient')
        mock_email_client.send.return_value = True
        
        # Bad: Don't mock internal methods of the class you're testing
        # mocker.patch.object(EmailService, '_format_message')  # Avoid this
        
        service = EmailService(db_session)
        result = await service.send_email("test@example.com", "Subject", "Body")
        
        assert result is True
        mock_email_client.send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_verify_mock_interactions(self, mocker, db_session: AsyncSession):
        """Always verify how mocks were called."""
        mock_logger = mocker.patch('services.user_service.logger')
        
        service = UserService(db_session)
        user_data = {"name": "Test User", "email": "test@example.com"}
        
        await service.create_user(user_data)
        
        # Verify logging was called correctly
        mock_logger.info.assert_called_with("Creating user: test@example.com")
        
        # Verify specific call arguments
        call_args = mock_logger.info.call_args
        assert "test@example.com" in call_args[0][0]
    
    @pytest.fixture
    def mock_external_services(self, mocker):
        """Fixture for commonly mocked external services."""
        mocks = {
            'email': mocker.patch('services.email_service.EmailClient'),
            'payment': mocker.patch('services.payment_service.PaymentGateway'),
            'notification': mocker.patch('services.notification_service.NotificationClient')
        }
        
        # Configure common return values
        mocks['email'].send.return_value = {"success": True}
        mocks['payment'].charge.return_value = {"success": True, "id": "txn_123"}
        mocks['notification'].send.return_value = {"delivered": True}
        
        return mocks
    
    @pytest.mark.asyncio
    async def test_using_mock_fixture(self, mock_external_services, db_session: AsyncSession):
        """Test using centralized mock fixture."""
        service = OrderService(db_session)
        
        order_data = {
            "user_id": 1,
            "items": [{"id": 1, "quantity": 2}],
            "total": 100.00
        }
        
        result = await service.process_order(order_data)
        
        assert result["success"] is True
        
        # Verify all external services were called
        mock_external_services['payment'].charge.assert_called_once()
        mock_external_services['email'].send.assert_called_once()
        mock_external_services['notification'].send.assert_called_once()
```

## 📊 Coverage Reports

### Generating Coverage Reports

```bash
# Run tests with coverage
make test-coverage
# or
uv run pytest --cov=src --cov-report=html --cov-report=term-missing

# Generate only HTML report
uv run pytest --cov=src --cov-report=html

# Generate XML report (good for CI/CD)
uv run pytest --cov=src --cov-report=xml

# Show missing lines in terminal
uv run pytest --cov=src --cov-report=term-missing
```

### Understanding Coverage Reports

The coverage report shows:
- **Statements**: Total lines of code
- **Missing**: Lines not executed during tests
- **Excluded**: Lines marked to exclude from coverage
- **Coverage %**: Percentage of code covered by tests

### Coverage Configuration

Coverage settings are in `pyproject.toml`:

```toml
[tool.coverage.run]
omit = [
    "src/db.py",           # Database configuration
    "src/main.py",         # App startup
    "src/tests/*",         # Test files themselves
    "src/migrations/*"     # Database migrations
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]
```

### Improving Coverage

```python
class TestCoverageImprovement:
    """Examples of improving test coverage."""
    
    @pytest.mark.asyncio
    async def test_error_handling_paths(self, db_session: AsyncSession):
        """Test error handling code paths for better coverage."""
        service = UserService(db_session)
        
        # Test various error conditions
        with pytest.raises(UserService.ValidationError):
            await service.create_user({"name": "", "email": "invalid"})
        
        with pytest.raises(UserService.NotFoundError):
            await service.get_user_by_id(999999)
        
        with pytest.raises(UserService.DuplicateEmailError):
            await service.create_user({"name": "Test", "email": "existing@example.com"})
    
    @pytest.mark.asyncio
    async def test_edge_cases(self, db_session: AsyncSession):
        """Test edge cases to improve coverage."""
        service = UserService(db_session)
        
        # Test with maximum length strings
        long_name = "a" * 255
        user_data = {"name": long_name, "email": "test@example.com"}
        user = await service.create_user(user_data)
        assert user.name == long_name
        
        # Test with special characters
        special_name = "José María Azaña-Díaz"
        user_data = {"name": special_name, "email": "jose@example.com"}
        user = await service.create_user(user_data)
        assert user.name == special_name
    
    def test_string_representations(self):
        """Test __str__ and __repr__ methods for coverage."""
        user = User(id=1, name="Test User", email="test@example.com")
        
        # Test string representation
        str_repr = str(user)
        assert "Test User" in str_repr
        
        # Test repr representation
        repr_str = repr(user)
        assert "User" in repr_str
        assert "1" in repr_str
```

### Coverage Goals

- **Overall**: Aim for 80-90% coverage
- **Critical paths**: 95%+ coverage for core business logic
- **New code**: 100% coverage for new features
- **Don't chase 100%**: Some code doesn't need testing (simple getters, __repr__, etc.)

## ⚡ Performance Testing

### Basic Performance Tests

```python
import time
import pytest
from httpx import AsyncClient

class TestPerformance:
    """Performance and load testing examples."""
    
    @pytest.mark.asyncio
    async def test_api_response_time(self, async_client: AsyncClient):
        """Test that API responds within acceptable time."""
        start_time = time.time()
        
        response = await async_client.get("/users")
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 1.0  # Should respond within 1 second
    
    @pytest.mark.asyncio
    async def test_database_query_performance(self, db_session: AsyncSession):
        """Test database query performance."""
        from models.user import User
        from sqlalchemy import select
        
        # Create test data
        users = [
            User(name=f"User {i}", email=f"user{i}@example.com")
            for i in range(100)
        ]
        db_session.add_all(users)
        await db_session.commit()
        
        start_time = time.time()
        
        # Test query performance
        result = await db_session.execute(
            select(User).where(User.name.like("User 5%"))
        )
        users = result.scalars().all()
        
        end_time = time.time()
        query_time = end_time - start_time
        
        assert len(users) == 11  # User 5, User 50-59
        assert query_time < 0.1  # Should be fast with proper indexing
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("concurrent_requests", [5, 10, 20])
    async def test_concurrent_requests(self, async_client: AsyncClient, concurrent_requests: int):
        """Test handling concurrent requests."""
        import asyncio
        
        async def make_request():
            response = await async_client.get("/health")
            return response.status_code
        
        start_time = time.time()
        
        # Make concurrent requests
        tasks = [make_request() for _ in range(concurrent_requests)]
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # All requests should succeed
        assert all(status == 200 for status in results)
        
        # Should handle concurrent requests efficiently
        assert total_time < 2.0
        
        # Calculate requests per second
        rps = concurrent_requests / total_time
        assert rps > 10  # Should handle at least 10 requests per second

# Mark slow tests
@pytest.mark.slow
class TestSlowOperations:
    """Tests that take longer to run."""
    
    @pytest.mark.asyncio
    async def test_large_data_processing(self, db_session: AsyncSession):
        """Test processing large amounts of data."""
        # Create large dataset
        users = [
            User(name=f"User {i}", email=f"user{i}@example.com")
            for i in range(1000)
        ]
        
        start_time = time.time()
        
        # Bulk insert
        db_session.add_all(users)
        await db_session.commit()
        
        # Bulk query
        result = await db_session.execute(select(User))
        all_users = result.scalars().all()
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        assert len(all_users) == 1000
        assert processing_time < 5.0  # Should complete within 5 seconds
```

### Running Performance Tests

```bash
# Run only fast tests (default)
pytest

# Run slow tests
pytest -m slow

# Run without slow tests
pytest -m "not slow"

# Run with timing information
pytest --durations=10  # Show 10 slowest tests
```

## 🐛 Debugging Tests

### Debug Configuration

```python
# Enable SQL logging in test_db.py for debugging
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=True,  # Set to True to see all SQL queries
    poolclass=StaticPool,
    connect_args={"check_same_thread": False},
)
```

### Using pytest's Built-in Debugging

```bash
# Drop into debugger on failure
uv run pytest --pdb

# Drop into debugger on first failure
uv run pytest --pdb -x

# Show local variables in traceback
uv run pytest -l

# Capture output (don't capture, show prints)
uv run pytest -s

# Very verbose output
uv run pytest -vv

# Show reason for skip/xfail
uv run pytest -rs
```

### Custom Debug Helpers

```python
import logging
import pytest

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TestDebugging:
    """Examples of debugging techniques."""
    
    @pytest.mark.asyncio
    async def test_with_debugging(self, db_session: AsyncSession, caplog):
        """Test with debug output and log capture."""
        with caplog.at_level(logging.DEBUG):
            service = UserService(db_session)
            
            # Add debug logging to your service methods
            logger.debug("Starting user creation test")
            
            user_data = {"name": "Debug User", "email": "debug@example.com"}
            user = await service.create_user(user_data)
            
            logger.debug(f"Created user with ID: {user.id}")
            
            # Test logging
            assert "Starting user creation test" in caplog.text
            assert f"Created user with ID: {user.id}" in caplog.text
    
    @pytest.mark.asyncio
    async def test_database_state_debugging(self, db_session: AsyncSession):
        """Test with database state inspection."""
        from sqlalchemy import text
        
        # Create test data
        user = User(name="Test User", email="test@example.com")
        db_session.add(user)
        await db_session.commit()
        
        # Debug: Check database state
        result = await db_session.execute(text("SELECT COUNT(*) FROM users"))
        user_count = result.scalar()
        print(f"Debug: User count = {user_count}")
        
        # Debug: Check specific user
        result = await db_session.execute(text("SELECT * FROM users WHERE id = ?"), (user.id,))
        user_row = result.fetchone()
        print(f"Debug: User row = {user_row}")
        
        assert user_count == 1
    
    @pytest.mark.asyncio
    async def test_api_debugging(self, async_client: AsyncClient):
        """Test with API debugging."""
        # Create user first
        user_data = {"name": "API Test User", "email": "api@example.com"}
        create_response = await async_client.post("/users", json=user_data)
        
        print(f"Debug: Create response status = {create_response.status_code}")
        print(f"Debug: Create response data = {create_response.json()}")
        
        # Get user
        user_id = create_response.json()["id"]
        get_response = await async_client.get(f"/users/{user_id}")
        
        print(f"Debug: Get response status = {get_response.status_code}")
        print(f"Debug: Get response data = {get_response.json()}")
        
        assert create_response.status_code == 201
        assert get_response.status_code == 200
```

### Docker Testing

```dockerfile
# Dockerfile.test
FROM python:3.13-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency files
COPY uv.lock pyproject.toml ./

# Install dependencies
RUN uv sync

# Copy source code
COPY src/ ./src/

# Run tests
CMD ["uv", "run", "pytest", "--cov=src", "--cov-report=term-missing"]
```

## 📋 Best Practices

### Test Organization

1. **Mirror source structure** - Test files should mirror your source code structure
2. **Descriptive names** - Use clear, descriptive test names
3. **Group related tests** - Use test classes to group related functionality
4. **One concept per test** - Each test should verify one specific behavior

### Test Quality

```python
class TestBestPractices:
    """Examples of testing best practices."""
    
    @pytest.mark.asyncio
    async def test_single_responsibility(self, db_session: AsyncSession):
        """Test only one thing - user creation success."""
        service = UserService(db_session)
        user_data = {"name": "Test User", "email": "test@example.com"}
        
        user = await service.create_user(user_data)
        
        # Test only the core behavior - user was created successfully
        assert user.id is not None
        assert user.name == user_data["name"]
        assert user.email == user_data["email"]
    
    @pytest.mark.asyncio
    async def test_descriptive_assertions(self, async_client: AsyncClient):
        """Use descriptive assertions that explain what went wrong."""
        response = await async_client.post("/users", json={})
        
        # Bad: assert response.status_code == 422
        # Good: Descriptive assertion
        assert response.status_code == 422, (
            f"Expected validation error for empty user data, "
            f"got {response.status_code}: {response.text}"
        )
        
        data = response.json()
        assert "detail" in data, "Response should include validation error details"
        assert len(data["detail"]) > 0, "Should have at least one validation error"
    
    @pytest.mark.asyncio
    async def test_independent_tests(self, db_session: AsyncSession):
        """Tests should be independent and not rely on other tests."""
        # Don't rely on data from other tests
        # Create your own test data
        user = User(name="Independent Test", email="independent@example.com")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # Test only with this data
        assert user.name == "Independent Test"
    
    def test_meaningful_test_data(self):
        """Use meaningful test data that makes tests readable."""
        # Bad: Generic test data
        # user_data = {"name": "Test", "email": "test@test.com"}
        
        # Good: Meaningful test data
        user_data = {
            "name": "Alice Johnson",
            "email": "alice.johnson@company.com",
            "role": "developer",
            "department": "engineering"
        }
        
        # Test data tells a story and makes test intent clear
        assert user_data["role"] == "developer"
        assert user_data["department"] == "engineering"
```

### Performance Best Practices

1. **Use fixtures wisely** - Leverage fixture scopes appropriately
2. **Mock external dependencies** - Don't hit real APIs in tests
3. **Parallel execution** - Use pytest-xdist for faster test runs
4. **Test data cleanup** - Ensure tests clean up after themselves

### Maintenance Best Practices

1. **Regular test review** - Review and update tests regularly
2. **Remove obsolete tests** - Delete tests for removed features
3. **Update test data** - Keep test data current and realistic
4. **Documentation** - Document complex test scenarios

## 🔧 Troubleshooting

### Common Issues

#### Database Connection Errors

```python
# Problem: Tests fail with database connection errors
# Solution: Check test database configuration

# In test_db.py, ensure proper async session setup
async def get_test_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestAsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()  # Ensure proper cleanup
```

#### Async/Await Issues

```python
# Problem: RuntimeError: no running event loop
# Solution: Use proper async test setup

# Wrong:
def test_async_function():
    result = async_function()  # This won't work
    
# Right:
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()  # This works
```

#### Import Errors

```python
# Problem: ModuleNotFoundError in tests
# Solution: Check PYTHONPATH and imports

# Ensure proper project structure
# src/tests/conftest.py should be at the right level
# Use absolute imports in tests:
from models.user import User  # Good
from ..models.user import User  # Avoid relative imports
```

#### Fixture Dependency Issues

```python
# Problem: Fixture not found or circular dependency
# Solution: Check fixture scopes and dependencies

@pytest.fixture(scope="function")  # Explicit scope
async def test_user(db_session: AsyncSession):  # Proper dependency
    user = User(name="Test", email="test@example.com")
    db_session.add(user)
    await db_session.commit()
    return user
```

### Debug Commands

```bash
# See why tests are skipped
uv run pytest -rs

# See detailed failure information
uv run pytest -vv --tb=long

# Run specific failing test
uv run pytest src/tests/routes/test_health.py::TestHealthEndpoint::test_health_check_sync -vv

# Check fixture setup
uv run pytest --fixtures

# See test collection without running
uv run pytest --collect-only
```

### Getting Help

1. **Check logs** - Look at test output and logs carefully
2. **Isolate the problem** - Run individual tests to isolate issues
3. **Check dependencies** - Ensure all test dependencies are installed
4. **Review changes** - What changed since tests last passed?
5. **Community resources** - pytest documentation, Stack Overflow, project issues

## 📚 Additional Resources

### Documentation

- [pytest Documentation](https://docs.pytest.org/) - Comprehensive pytest guide
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/) - Async testing patterns
- [httpx Documentation](https://www.python-httpx.org/) - HTTP client for testing
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites) - Database testing patterns

### pytest Plugins

- `pytest-xdist` - Parallel test execution
- `pytest-cov` - Coverage reporting
- `pytest-mock` - Mocking utilities
- `pytest-randomly` - Randomize test order
- `pytest-sugar` - Better test output
- `pytest-clarity` - Better assertion introspection

### Testing Philosophy

- **Test behavior, not implementation** - Focus on what the code should do
- **Write tests first** - TDD can help design better APIs
- **Test edge cases** - Don't just test the happy path
- **Keep tests simple** - Tests should be easier to understand than the code they test
- **Fail fast** - Tests should fail quickly and clearly when something is wrong
