# Wei Agent API

This is a FastAPI-based service for analyzing governance proposals.

## Features

- **Repository Pattern**: Clean separation of data access logic
- **Service Layer**: Business logic encapsulation
- **Dependency Injection**: Improved testability and modularity
- **Enhanced Error Handling**: Consistent error responses
- **Pydantic Settings**: Type-safe configuration management
- **Request Logging**: Detailed logging of requests and performance
- **Rate Limiting**: Protection against excessive requests
- **OpenAPI Documentation**: Comprehensive API documentation
- **Test Utilities**: Tools for easier testing

## Architecture

The application follows a layered architecture:

1. **API Layer**: FastAPI routes and controllers
2. **Service Layer**: Business logic and orchestration
3. **Repository Layer**: Data access and persistence
4. **Domain Layer**: Core domain models and schemas

## Directory Structure

```
app/
├── api/
│   ├── dependencies.py  # Dependency injection
│   └── routes.py        # API routes
├── config.py            # Configuration with Pydantic
├── db/
│   ├── core.py                   # Database setup
│   └── models.py                 # SQLAlchemy models
├── errors.py                     # Error handling utilities
├── main.py              # Application entry point
├── middleware.py        # Custom middleware
├── repositories/
│   ├── analysis_repository.py  # Analysis repository
│   └── base.py                   # Base repository
├── schemas.py                    # Pydantic schemas
├── services/
│   ├── analysis_service.py  # Analysis service
│   ├── base_service.py           # Base service
│   └── langgraph/                # LangGraph integration
└── test_utils.py                 # Test utilities
```

## Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL
- Poetry (recommended for dependency management)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/NethermindEth/wei.git
   cd wei/langgraph/api
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

### Running the Application

Run the application:

```bash
python run.py
```

Or with custom settings:

```bash
python run.py --host 0.0.0.0 --port 8002 --workers 4 --log-level info
```

### Running Tests

Run the tests with pytest:

```bash
pytest tests/test_api.py -v
```

## API Documentation

Once the application is running, you can access the API documentation at:

- Swagger UI: http://localhost:8002/api/docs
- ReDoc: http://localhost:8002/api/redoc

## Key Improvements

### 1. Repository Pattern

The repository pattern abstracts data access logic from business logic:

```python
class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base repository class with default methods for CRUD operations."""
    
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db
    
    async def create(self, obj_in: Union[CreateSchemaType, Dict[str, Any]]) -> ModelType:
        """Create a new record."""
        # Implementation...
```

### 2. Service Layer

The service layer encapsulates business logic:

```python
class BaseService(Generic[RepoType, ModelType, ResponseSchemaType, CreateSchemaType, UpdateSchemaType]):
    """Base service class with default methods for business logic."""
    
    def __init__(self, repository: RepoType):
        self.repository = repository
    
    async def create(self, obj_in: CreateSchemaType) -> ResponseSchemaType:
        """Create a new record."""
        # Implementation...
```

### 3. Dependency Injection

Dependency injection is used for better testability:

```python
class ServiceDependency(Generic[S, R]):
    """Factory for service dependencies."""
    
    def __init__(self, service_class: Type[S], repository_dependency: Callable[..., AsyncGenerator[R, None]]):
        self.service_class = service_class
        self.repository_dependency = repository_dependency
    
    async def __call__(self, repository: R = Depends()) -> AsyncGenerator[S, None]:
        """Create and yield a service instance."""
        service = self.service_class(repository)
        yield service
```

### 4. Enhanced Error Handling

Consistent error handling with custom exception classes:

```python
class AppError(Exception):
    """Base exception class for application errors."""
    
    def __init__(
        self, 
        message: str, 
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)
```

### 5. Pydantic Settings

Type-safe configuration management:

```python
class Settings(BaseSettings):
    """Application settings with environment variable validation."""
    
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Wei Agent API"
    PORT: int = 8002
    
    # Database settings
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: str = "5432"
    # ...
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
