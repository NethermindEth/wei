# Wei Agent API Server

A FastAPI server for the Wei Agent that provides proposal analysis and evaluation capabilities.

## Features

- Proposal analysis and evaluation
- Custom evaluation with user-defined criteria
- Argument generation for and against proposals
- Related proposal search
- Community analysis
- Roadmap generation
- Cache management
- Chat interface

## Prerequisites

- Python 3.9+
- PostgreSQL 12+
- API keys for language models (OpenRouter, Exa)

## Installation

1. Clone the repository

```bash
git clone https://github.com/NethermindEth/wei.git
cd wei/langgraph/api
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Set up environment variables

Create a `.env` file in the `langgraph/api` directory with the following variables:

```
# API SERVER CONFIGURATION
PORT=8000

# Database Configuration
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres
DATABASE_NAME=wei_agent
# Optional: provide full URL instead of individual components
# DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/wei_agent

# API Security
SECRET_KEY=your_secret_key_here
API_KEYS=key1,key2,key3

# CORS Configuration
BACKEND_CORS_ORIGINS=http://localhost:3000,*nethermind.io,*nethermind-org.vercel.app

# AI MODEL CONFIGURATION
# OpenRouter API Key (required for AI model access)
WEI_AGENT_OPEN_ROUTER_API_KEY=your_openrouter_api_key_here

# Model Configuration
WEI_AGENT_AI_MODEL_PROVIDER=openai
WEI_AGENT_AI_MODEL_NAME=gpt-4o-mini

# Optional: secondary model for roadmap/planning features
WEI_AGENT_ROADMAP_MODEL_NAME=perplexity/sonar-pro

# Optional: Web search provider key
WEI_AGENT_EXA_API_KEY=your_exa_api_key_here

# Model parameters
WEI_AGENT_ANALYZING_TEMPERATURE=0.2
WEI_AGENT_ANALYZING_MAX_TOKENS=2000
WEI_AGENT_MAX_TOKENS=400

# TRACING CONFIGURATION (optional)
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key_here
LANGFUSE_SECRET_KEY=your_langfuse_secret_key_here
LANGFUSE_HOST=https://cloud.langfuse.com
LANGFUSE_PROJECT=default

# Logging level (debug, info, warn, error)
LOG_LEVEL=info
```

4. Initialize the database

Make sure PostgreSQL is running, then you can initialize the database in one of two ways:

- **Automatic initialization**: The server will automatically create the database and run migrations on startup.

- **Manual initialization**: Run the initialization script:

```bash
python init_db.py
```

This is useful if you want to set up the database before starting the server.

## Usage

### Starting the server

```bash
python server.py
```

The server will be available at http://localhost:8000.

### API Documentation

Once the server is running, you can access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### API Authentication

Protected endpoints require an API key to be provided in the `X-API-Key` header. You can configure multiple valid API keys by setting the `API_KEYS` environment variable to a comma-separated list of keys:

```
API_KEYS=key1,key2,key3
```

This allows you to issue different API keys to different clients and revoke them individually if needed.

You can test API key authentication with the `/api/v1/test` endpoint:

```bash
# Test with a valid API key
curl -H "X-API-Key: your_api_key_here" http://localhost:8007/api/v1/test

# Response if valid
{"message":"API key is valid"}

# Response if invalid
{"detail":"Invalid API key"}
```

### API Endpoints

#### Proposal Analysis

- `POST /api/v1/pre-filter` - Analyze a proposal
- `POST /api/v1/pre-filter/arguments` - Generate arguments for a proposal
- `POST /api/v1/pre-filter/custom` - Evaluate a proposal with custom criteria
- `GET /api/v1/pre-filter/{id}` - Get analysis by ID
- `GET /api/v1/pre-filter/proposals/{id}` - Get analysis by proposal ID
- `GET /api/v1/pre-filter/proposal/{proposal_id}` - Get all analyses for a proposal

#### Related Proposals

- `GET /api/v1/related-proposals` - Search for related proposals

#### Community Analysis

- `GET /api/v1/community` - Get community analysis
- `POST /api/v1/community` - Analyze community

#### Roadmap

- `GET /api/v1/roadmap` - Get cached roadmap
- `POST /api/v1/roadmap` - Generate roadmap

#### Cache Management

- `GET /api/v1/cache` - List cached queries
- `GET /api/v1/cache/stats` - Get cache statistics
- `POST /api/v1/cache/invalidate` - Invalidate cache entries
- `POST /api/v1/cache/refresh` - Refresh cache entries
- `POST /api/v1/cache/cleanup` - Clean up cache

#### Chat

- `POST /api/v1/chat` - Chat with the Wei Agent

## Development

### Project Structure

```
api/
├── alembic.ini          # Alembic configuration
├── app/                 # Application package
│   ├── __init__.py
│   ├── api/             # API routes
│   │   ├── __init__.py
│   │   └── routes.py    # API endpoints
│   ├── auth.py          # Authentication middleware
│   ├── config.py        # Application configuration
│   ├── db/              # Database module
│   │   ├── __init__.py
│   │   ├── core.py      # Database connection
│   │   └── models.py    # Database models
│   ├── main.py          # FastAPI application
│   └── schemas.py       # Request/response models
├── migrations/          # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   ├── versions/
│   └── 001_initial_schema.sql
├── README.md            # This file
├── requirements.txt     # Dependencies
└── server.py           # Entry point
```

### Running with Hot Reload

The server is configured to run with hot reload by default, which means it will automatically restart when you make changes to the code.

### Database Migrations

The server uses Alembic for database migrations. To create a new migration:

```bash
alembic revision -m "description of changes"
```

To apply migrations manually:

```bash
alembic upgrade head
```

### Running Tests

The project includes unit tests for key functionality. To run the tests:

```bash
python run_tests.py
```

Or using pytest directly:

```bash
pytest -v
```

The tests cover:
- JSON parsing utilities with various formats
- API endpoint functionality
- Tracing integration

## License

This project is licensed under the MIT License - see the LICENSE file for details.