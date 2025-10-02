# Wei Agent API End-to-End Tests

This directory contains end-to-end tests for the Wei Agent API. These tests validate the functionality of the API without mocking any dependencies, ensuring that the entire system works as expected in a real-world scenario.

## Test Categories

1. **Authentication Tests** (`test_auth.py`) - Verify API key validation
2. **Proposal Analysis Tests** (`test_proposal_analysis.py`) - Test proposal analysis endpoints
3. **Argument Generation Tests** (`test_arguments.py`) - Test argument generation for proposals
4. **Custom Evaluation Tests** (`test_custom_evaluation.py`, `test_custom_evaluation_detailed.py`) - Test custom evaluation of proposals
5. **Related Proposals Tests** (`test_related_proposals.py`) - Test searching for related proposals
6. **Cache Management Tests** (`test_cache.py`) - Test cache-related endpoints
7. **Chat Functionality Tests** (`test_chat.py`) - Test the chat endpoint
8. **Community and Roadmap Tests** (`test_community_roadmap.py`) - Test community and roadmap endpoints
9. **JSON Parsing Tests** (`test_json_parser.py`, `test_json_parsing.py`) - Test JSON parsing functionality
10. **Arguments Integration Tests** (`test_arguments_integration.py`) - Test integration between arguments and analysis
11. **Error Handling Tests** (`test_error_handling.py`) - Test error handling across all routes
12. **Concurrency Tests** (`test_concurrency.py`) - Test concurrent requests and performance
13. **Webhook Event Tests** (`test_webhook_events.py`) - Test webhook events functionality
14. **LangGraph Integration Tests** (`test_langgraph_integration.py`) - Test integration with LangGraph
15. **Tracing Tests** (`test_tracing.py`) - Test tracing and monitoring functionality
16. **API Documentation Tests** (`test_api_docs.py`) - Test API documentation generation

## Prerequisites

Before running the tests, make sure you have:

1. PostgreSQL installed and running
2. Environment variables set up (or use the defaults in the tests)
3. All dependencies installed

## Running the Tests

### Running All Tests

To run all tests that have been fixed and are passing:

```bash
cd /path/to/wei/langgraph/api
pytest tests/test_json_parser.py tests/test_json_parsing.py tests/test_api_docs.py tests/test_api_endpoints.py tests/test_auth.py tests/test_proposal_api.py tests/test_proposal_analysis.py tests/test_error_handling.py tests/test_langgraph_integration.py tests/test_webhook_events.py tests/test_arguments_integration.py tests/test_custom_evaluation.py -v
```

### Running Specific Test Files

To run specific test files:

```bash
cd /path/to/wei/langgraph/api

# Run JSON parsing tests
pytest tests/test_json_parser.py tests/test_json_parsing.py -v

# Run API documentation tests
pytest tests/test_api_docs.py -v

# Run API endpoint tests
pytest tests/test_api_endpoints.py -v

# Run authentication tests
pytest tests/test_auth.py -v

# Run proposal API tests
pytest tests/test_proposal_api.py -v

# Run proposal analysis tests
pytest tests/test_proposal_analysis.py -v

# Run error handling tests
pytest tests/test_error_handling.py -v

# Run LangGraph integration tests
pytest tests/test_langgraph_integration.py -v

# Run webhook events tests
pytest tests/test_webhook_events.py -v

# Run arguments integration tests
pytest tests/test_arguments_integration.py -v

# Run custom evaluation tests
pytest tests/test_custom_evaluation.py -v
```

### Running Tests by Category

To run tests with specific markers:

```bash
pytest -m "e2e"
pytest -m "auth"
pytest -m "slow"
```

## Test Approach

### Separation of Concerns

The tests follow a separation of concerns approach:

1. **Route Handlers**: Focus on HTTP request/response handling
2. **Database Operations**: Extracted into separate functions for better testability
3. **Business Logic**: Isolated from infrastructure concerns

### Mocking Strategy

The tests use mocking to isolate the components being tested:

1. **Database Mocking**: Mock database operations to avoid database access during tests
2. **AI Model Mocking**: Mock the LangGraph AI model to avoid making actual API calls
3. **Dependency Injection**: Use FastAPI's dependency injection to swap out real dependencies with mocks

### Test Database Setup

#### Automatic Test Database Creation

The test suite automatically creates a unique test database for each test session to avoid conflicts. The database name follows the pattern `wei_agent_test_<timestamp>`. This ensures that:

1. Tests don't interfere with your development database
2. Multiple test runs don't conflict with each other
3. Each test session has a clean database state

#### Database Connection Issues

If you encounter database connection issues during tests, check:

1. PostgreSQL is running and accessible
2. The PostgreSQL user has permissions to create databases
3. The connection URL in `app/config.py` is correct

#### Mocking Database Operations

For tests that don't need real database access, we use mocking to simulate database operations. This approach:

1. Makes tests faster and more reliable
2. Avoids database concurrency issues
3. Allows tests to run without a real database

#### Environment Variables

You can override database settings with environment variables:

```bash
DATABASE_URL="postgresql+asyncpg://user:password@localhost/custom_test_db" pytest tests/
```
