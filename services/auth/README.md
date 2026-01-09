# Wei Auth Service

A FastAPI-based authentication service that provides JWT token verification and user management using Clerk as the identity provider. This service acts as an authentication gateway for the Wei platform, validating Clerk JWT tokens and retrieving user metadata.

## Features

- JWT token verification using Clerk's JWKS endpoint
- User metadata retrieval from Clerk
- Batch user queries
- Service-to-service authentication via API keys
- Interactive API documentation with Swagger UI
- CORS support for cross-origin requests
- Comprehensive error handling and logging
- Type-safe with Pydantic models

## Architecture

The service is built with:
- **FastAPI**: Modern, high-performance web framework
- **Clerk Backend API**: Official Clerk SDK for authentication and user management
- **Pydantic**: Data validation and settings management
- **HTTPX**: HTTP client for request handling

### Core Components

- `main.py`: FastAPI application and route definitions
- `auth.py`: Clerk authentication service using SDK's built-in token verification
- `config.py`: Configuration management using Pydantic Settings
- `models.py`: Data models for requests and responses
- `middleware.py`: Service-to-service authentication middleware

## API Endpoints

### Health

- `GET /health` - Health check endpoint (no authentication required)

### Authentication

- `POST /verify-token` - Verify a Clerk JWT token
  - Requires: Bearer token + service key
  - Returns: Token validation status, user ID, session ID, expiration

### User Management

- `GET /users/me` - Get current user metadata from JWT
  - Requires: Bearer token + service key
  - Returns: Complete user metadata

- `GET /users/{user_id}` - Get user metadata by Clerk user ID
  - Requires: Service key
  - Returns: User metadata for specified ID

- `POST /users/batch` - Get metadata for multiple users
  - Requires: Service key + JSON array of user IDs
  - Returns: Array of user metadata objects

## Setup

### Prerequisites

- Python 3.10 or higher
- Clerk account with API credentials
- Virtual environment (recommended)

### Installation

1. Navigate to the service directory:
```bash
cd services/auth
```

2. Run the setup script:
```bash
chmod +x setup.sh
./setup.sh
```

This script will:
- Create a Python virtual environment
- Install all dependencies
- Copy `env.example` to `.env`

3. Configure environment variables:
```bash
# Edit .env with your credentials
nano .env
```

### Manual Installation

If you prefer manual setup:

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp env.example .env
```

## Configuration

Edit the `.env` file with your configuration:

```bash
# Clerk Configuration (Required)
CLERK_SECRET_KEY=sk_test_your_clerk_secret_key
CLERK_PUBLISHABLE_KEY=pk_test_your_clerk_publishable_key

# Server Configuration
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=info

# Service Authorization (Required)
# Comma-separated list of allowed service API keys
ALLOWED_SERVICE_KEYS=your_secret_key_1,your_secret_key_2

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
```

### Configuration Details

- **CLERK_SECRET_KEY**: Your Clerk secret key (starts with `sk_`)
- **CLERK_PUBLISHABLE_KEY**: Your Clerk publishable key (starts with `pk_`)
- **ALLOWED_SERVICE_KEYS**: Comma-separated list of keys for service-to-service auth
- **ALLOWED_ORIGINS**: Comma-separated list of allowed CORS origins
- **PORT**: Port to run the service on (default: 8000)
- **HOST**: Host to bind to (default: 0.0.0.0)
- **LOG_LEVEL**: Logging level (debug, info, warning, error)

## Running the Service

### Development Mode

```bash
# Activate virtual environment
source .venv/bin/activate

# Run with auto-reload
python main.py
```

The service will start on `http://localhost:8000` by default.

### Production Mode

```bash
# Activate virtual environment
source .venv/bin/activate

# Run with Uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once the service is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

The Swagger UI provides an interactive interface where you can:
1. Click the "Authorize" button
2. Enter your Bearer token and Service key
3. Test endpoints directly from the browser

## Testing

The service includes comprehensive test coverage.

### Run All Tests

```bash
# Activate virtual environment
source .venv/bin/activate

# Run tests
pytest tests/
```

### Run Specific Test Files

```bash
pytest tests/test_api.py      # API endpoint tests
pytest tests/test_auth.py     # Authentication tests
```

### Run with Coverage

```bash
pytest tests/ --cov=. --cov-report=html
```

### Test Structure

- `test_api.py`: Tests for all API endpoints
- `test_auth.py`: Tests for authentication logic
- `conftest.py`: Shared test fixtures and configuration

## Security

### Authentication Flow

1. **Service Authentication**: All endpoints (except `/health`) require a valid service key via `X-Service-Key` header
2. **JWT Verification**: User-facing endpoints require a valid Clerk JWT token via `Authorization: Bearer <token>` header
3. **JWKS Validation**: JWTs are verified against Clerk's public keys using RS256 algorithm

### Security Best Practices

- Service keys should be kept secret and rotated regularly
- Use environment variables for all sensitive configuration
- Enable HTTPS in production
- Configure CORS to allow only trusted origins
- Review logs for suspicious authentication attempts
- Keep dependencies updated for security patches

### Token Verification Process

The service uses the Clerk SDK's built-in `authenticate_request` method, which handles:

1. JWKS fetching and caching from Clerk's well-known endpoint
2. Signature verification using RS256 algorithm
3. Token expiration and issued-at validation
4. Claims extraction (user ID, session ID, expiration)

This approach leverages the official SDK's optimized and maintained verification logic.

## Error Handling

The service returns standardized error responses:

```json
{
  "error": "Error type",
  "detail": "Detailed error message",
  "status_code": 401
}
```

Common status codes:
- `200`: Success
- `401`: Unauthorized (missing or invalid credentials)
- `403`: Forbidden (invalid service key)
- `404`: Not found (user doesn't exist)
- `503`: Service unavailable (cannot reach Clerk)

## Logging

The service logs all authentication attempts and errors:

```
2024-10-02 12:00:00 - main - INFO - Using JWKS URL: https://clerk.example.com/.well-known/jwks.json
2024-10-02 12:00:01 - main - WARNING - Token has expired
2024-10-02 12:00:02 - main - ERROR - Failed to fetch user metadata for user_123
```

## Dependencies

Core dependencies:
- `fastapi==0.115.0` - Web framework
- `uvicorn[standard]==0.31.0` - ASGI server
- `pydantic==2.11.2` - Data validation
- `pydantic-settings==2.6.1` - Settings management
- `clerk-backend-api==3.3.1` - Clerk SDK
- `httpx==0.28.1` - Async HTTP client
- `python-dotenv==1.0.1` - Environment variable loading

Development dependencies:
- `pytest==8.3.3` - Testing framework
- `pytest-asyncio==0.24.0` - Async test support

## Integration with Wei

This service is designed to be called by other Wei services (indexer, agent) to:
1. Verify user JWT tokens from frontend requests
2. Retrieve user metadata for authorization decisions
3. Validate service-to-service communication

Example integration:

```python
import httpx

async def verify_user_token(token: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://auth-service:8000/verify-token",
            headers={
                "Authorization": f"Bearer {token}",
                "X-Service-Key": "your_service_key"
            }
        )
        return response.json()
```

## Troubleshooting

### Cannot connect to Clerk

- Verify `CLERK_SECRET_KEY` is correct and starts with `sk_`
- Check internet connectivity
- Ensure firewall allows outbound HTTPS to Clerk's API

### Token verification fails

- Verify token is from the correct Clerk instance (matching the secret key)
- Check token hasn't expired
- Ensure the token is a valid Clerk session JWT (not an OAuth token)
- Verify the Clerk SDK can reach the JWKS endpoint

### Service key rejected

- Verify `X-Service-Key` header is included in the request
- Check key is in `ALLOWED_SERVICE_KEYS` list
- Ensure no extra whitespace in configuration

### SDK-related issues

- Ensure `clerk-backend-api` package is installed and up to date
- Check that the SDK version is compatible (v3.3.1+)
- Review Clerk SDK logs for detailed error messages

## Development

### Project Structure

```
services/auth/
├── main.py              # FastAPI application
├── auth.py              # Clerk authentication service
├── config.py            # Configuration management
├── models.py            # Pydantic models
├── middleware.py        # Authentication middleware
├── requirements.txt     # Python dependencies
├── setup.sh            # Setup script
├── env.example         # Environment template
├── pytest.ini          # Pytest configuration
└── tests/              # Test suite
    ├── test_api.py
    ├── test_auth.py
    └── conftest.py
```

### Adding New Endpoints

1. Define the route in `main.py`
2. Add request/response models in `models.py`
3. Implement business logic in `auth.py` or a new service file
4. Add tests in `tests/`
5. Update Swagger documentation with examples

### SDK Utilization

This service maximizes the use of the official [Clerk Python SDK](https://github.com/clerk/clerk-sdk-python) for:

- **Token Verification**: Uses `clerk.authenticate_request()` with built-in JWKS handling
- **User Management**: Uses `clerk.users.get()` for fetching user metadata
- **Error Handling**: Leverages SDK's structured error responses
- **Security**: Benefits from SDK's maintained security updates

Benefits of using the SDK:
- No manual JWKS fetching or caching needed
- Automatic token signature verification
- Built-in error handling for common auth scenarios
- Regular security updates from Clerk team
- Type-safe operations with Pydantic models

The SDK abstracts away the complexity of JWT verification, JWKS management, and API communication, allowing the service to focus on business logic.

## License

See the root LICENSE file in the Wei project.

## Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Review logs for error details
3. Consult [Clerk documentation](https://clerk.com/docs) for auth-related issues
4. Open an issue in the Wei repository


