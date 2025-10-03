"""
Pytest configuration for end-to-end tests.
"""

import os
import pytest
import asyncio
import uuid
import httpx
from datetime import datetime
from typing import Generator, AsyncGenerator

from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from unittest.mock import patch, MagicMock, AsyncMock

# Set test environment variables
os.environ["DATABASE_NAME"] = "wei_agent_test"
os.environ["API_KEYS"] = "test_api_key"
os.environ["TESTING"] = "True"

from app.main import app
from app.db.core import Base, get_session
from app.config import settings
from app.db.models import Analysis, WebhookEvent

# Use a unique test database for each test session
import time
TEST_DATABASE_NAME = f"wei_agent_test_{int(time.time())}"

# Use the same database URL but with the unique test database name
TEST_DATABASE_URL = str(settings.DATABASE_URL).replace(str(settings.DATABASE_URL).split('/')[-1], TEST_DATABASE_NAME)

# Create test engine with pooling disabled to avoid concurrency issues
test_engine = create_async_engine(
    TEST_DATABASE_URL, 
    echo=False,  # Reduce log noise
    pool_size=1,  # Limit pool size
    max_overflow=0,  # Prevent overflow connections
    pool_pre_ping=True,  # Check connection health before use
    pool_recycle=3600  # Recycle connections after an hour
)

TestingSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)

# Test API key
TEST_API_KEY = "test_api_key"


async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
    """Override the get_session dependency for testing."""
    # Create a new session for each request
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def setup_database():
    """Set up the test database."""
    import asyncpg
    
    # Create the test database
    # Convert SQLAlchemy URL to asyncpg URL
    system_db_url = str(settings.DATABASE_URL).replace('postgresql+asyncpg://', 'postgresql://')
    system_db_url = system_db_url.rsplit('/', 1)[0] + '/postgres'
    conn = await asyncpg.connect(
        dsn=system_db_url,
        server_settings={'search_path': 'public'}
    )
    
    # Check if the test database exists and drop it if it does
    try:
        await conn.execute(f'DROP DATABASE IF EXISTS {TEST_DATABASE_NAME}')
    except Exception as e:
        print(f"Error dropping database: {e}")
    
    # Create the test database
    try:
        await conn.execute(f'CREATE DATABASE {TEST_DATABASE_NAME}')
        print(f"Created test database: {TEST_DATABASE_NAME}")
    except Exception as e:
        print(f"Error creating database: {e}")
    
    await conn.close()
    
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create extension for UUID generation
    async with test_engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto;"))
    
    yield
    
    # Close all connections
    await test_engine.dispose()
    
    # Drop the test database after tests
    system_db_url = str(settings.DATABASE_URL).replace('postgresql+asyncpg://', 'postgresql://')
    system_db_url = system_db_url.rsplit('/', 1)[0] + '/postgres'
    conn = await asyncpg.connect(
        dsn=system_db_url,
        server_settings={'search_path': 'public'}
    )
    
    # Terminate all connections to the test database
    await conn.execute(f"""
    SELECT pg_terminate_backend(pg_stat_activity.pid)
    FROM pg_stat_activity
    WHERE pg_stat_activity.datname = '{TEST_DATABASE_NAME}'
    AND pid <> pg_backend_pid();
    """)
    
    # Drop the test database
    await conn.execute(f'DROP DATABASE IF EXISTS {TEST_DATABASE_NAME}')
    print(f"Dropped test database: {TEST_DATABASE_NAME}")
    
    await conn.close()


# Create a mock database session for tests that don't need real DB access
class MockDBSession:
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    
    async def commit(self):
        pass
    
    async def close(self):
        pass
    
    async def add(self, obj):
        pass
    
    async def refresh(self, obj):
        pass
    
    async def get(self, model, id):
        # Create a mock object with the requested ID
        mock_obj = MagicMock()
        mock_obj.id = id
        mock_obj.proposal_id = f"test-proposal-{uuid.uuid4()}"
        mock_obj.result = "pass"
        mock_obj.confidence = 0.85
        mock_obj.details = "Test details"
        mock_obj.created_at = datetime.now()
        mock_obj.updated_at = datetime.now()
        return mock_obj


@pytest.fixture
def mock_db_session():
    """Provide a mock database session."""
    return MockDBSession()


@pytest.fixture
def test_client(setup_database) -> TestClient:
    """Create a test client with the test database."""
    # Override the get_session dependency
    async def override_get_session():
        # Create a new session for each request
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            await session.close()
    
    # Mock the graph.ainvoke method
    async def mock_ainvoke(*args, **kwargs):
        return {
            "result": "pass",
            "confidence": 0.85,
            "details": "Test details"
        }
    
    # Mock the AnalysisService methods
    mock_service = MagicMock()
    mock_service.get_proposal_arguments = AsyncMock(return_value={
        "for_proposal": ["Test supporting argument."],
        "against": ["Test opposing argument."]
    })
    mock_service.analyze_proposal = AsyncMock(return_value={
        "id": uuid.uuid4(),
        "proposal_id": "test-proposal-id",
        "result": "pass",
        "confidence": 0.85,
        "details": "Test details",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "arguments": {
            "for_proposal": ["Test supporting argument."],
            "against": ["Test opposing argument."]
        }
    })
    
    # Apply patches
    with patch('app.api.routes.get_session', return_value=override_get_session()), \
         patch('app.api.dependencies.get_analysis_service', return_value=mock_service), \
         patch('app.api.routes.graph.ainvoke', side_effect=mock_ainvoke):
        
        # Create test client
        with TestClient(app) as client:
            yield client


@pytest.fixture
async def async_client() -> AsyncClient:
    """Create an async test client with the test database."""
    # Create a mock session
    mock_session = MagicMock()
    mock_session.add = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    mock_session.get = AsyncMock()
    mock_session.execute = AsyncMock()
    mock_session.close = AsyncMock()
    
    # Override the get_session dependency
    async def override_get_session():
        yield mock_session
    
    # Mock the extracted database functions
    async def mock_create_analysis(*args, **kwargs):
        mock_analysis = MagicMock()
        mock_analysis.id = uuid.uuid4()
        mock_analysis.proposal_id = kwargs.get('proposal_id', str(uuid.uuid4()))
        mock_analysis.result = kwargs.get('result', 'pass')
        mock_analysis.confidence = kwargs.get('confidence', 0.85)
        mock_analysis.details = kwargs.get('details', 'Test details')
        mock_analysis.created_at = datetime.now()
        mock_analysis.updated_at = datetime.now()
        return mock_analysis
    
    async def mock_get_analysis_by_id(*args, **kwargs):
        mock_analysis = MagicMock()
        mock_analysis.id = args[1] if len(args) > 1 else uuid.uuid4()
        mock_analysis.proposal_id = f"test-proposal-{uuid.uuid4()}"
        mock_analysis.result = "pass"
        mock_analysis.confidence = 0.85
        mock_analysis.details = "Test details"
        mock_analysis.created_at = datetime.now()
        mock_analysis.updated_at = datetime.now()
        return mock_analysis
    
    async def mock_find_analysis_by_proposal_id(*args, **kwargs):
        mock_analysis = MagicMock()
        mock_analysis.id = uuid.uuid4()
        mock_analysis.proposal_id = args[1] if len(args) > 1 else f"test-proposal-{uuid.uuid4()}"
        mock_analysis.result = "pass"
        mock_analysis.confidence = 0.85
        mock_analysis.details = "Test details"
        mock_analysis.created_at = datetime.now()
        mock_analysis.updated_at = datetime.now()
        return mock_analysis
    
    async def mock_find_analyses_by_proposal_id(*args, **kwargs):
        mock_analysis = MagicMock()
        mock_analysis.id = uuid.uuid4()
        mock_analysis.proposal_id = args[1] if len(args) > 1 else f"test-proposal-{uuid.uuid4()}"
        mock_analysis.result = "pass"
        mock_analysis.confidence = 0.85
        mock_analysis.details = "Test details"
        mock_analysis.created_at = datetime.now()
        mock_analysis.updated_at = datetime.now()
        return [mock_analysis]
    
    # Mock the graph.ainvoke method
    async def mock_ainvoke(*args, **kwargs):
        return {
            "analysis_result": {
                "result": "pass",
                "confidence": 0.85,
                "details": "Test details"
            }
        }
    
    # Mock the AnalysisService methods
    mock_service = MagicMock()
    mock_service.get_proposal_arguments = AsyncMock(return_value={
        "for_proposal": ["Test supporting argument."],
        "against": ["Test opposing argument."]
    })
    mock_service.analyze_proposal = AsyncMock(return_value={
        "id": uuid.uuid4(),
        "proposal_id": "test-proposal-id",
        "result": "pass",
        "confidence": 0.85,
        "details": "Test details",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "arguments": {
            "for_proposal": ["Test supporting argument."],
            "against": ["Test opposing argument."]
        }
    })
    mock_service.get_analysis_by_id = AsyncMock(return_value={
        "id": uuid.uuid4(),
        "proposal_id": "test-proposal-id",
        "result": "pass",
        "confidence": 0.85,
        "details": "Test details",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    })
    mock_service.get_analysis_by_proposal_id = AsyncMock(return_value={
        "id": uuid.uuid4(),
        "proposal_id": "test-proposal-id",
        "result": "pass",
        "confidence": 0.85,
        "details": "Test details",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    })
    mock_service.get_analyses_by_proposal_id = AsyncMock(return_value=[{
        "id": uuid.uuid4(),
        "proposal_id": "test-proposal-id",
        "result": "pass",
        "confidence": 0.85,
        "details": "Test details",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }])
    mock_service.custom_evaluate_proposal = AsyncMock(return_value={
        "summary": "Test summary",
        "response_map": {
            "test_criterion": {
                "status": "pass",
                "justification": "Test justification",
                "suggestions": ["Test suggestion"]
            }
        }
    })
    mock_service.chat = AsyncMock(return_value="Test response")
    mock_service.search_related_proposals = AsyncMock(return_value=[
        {"id": "1", "title": "Test Proposal 1", "score": 0.95},
        {"id": "2", "title": "Test Proposal 2", "score": 0.85}
    ])
    
    # Apply patches
    with patch('app.api.routes.get_session', return_value=override_get_session()), \
         patch('app.api.dependencies.get_analysis_service', return_value=mock_service), \
         patch('app.api.routes.graph.ainvoke', side_effect=mock_ainvoke):
        
        # Create async test client
        async with AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            yield client


def pytest_configure(config):
    """Configure pytest."""
    # Register markers
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "e2e: mark test as end-to-end test")
    config.addinivalue_line("markers", "auth: mark test as authentication test")
    config.addinivalue_line("markers", "analysis: mark test as proposal analysis test")
    config.addinivalue_line("markers", "arguments: mark test as argument generation test")
    config.addinivalue_line("markers", "custom: mark test as custom evaluation test")
    config.addinivalue_line("markers", "cache: mark test as cache management test")
    config.addinivalue_line("markers", "chat: mark test as chat functionality test")
    config.addinivalue_line("markers", "community: mark test as community and roadmap test")
    config.addinivalue_line("markers", "json: mark test as JSON parsing test")
    config.addinivalue_line("markers", "error: mark test as error handling test")
    config.addinivalue_line("markers", "concurrency: mark test as concurrency test")
    config.addinivalue_line("markers", "webhook: mark test as webhook event test")
    config.addinivalue_line("markers", "langgraph: mark test as LangGraph integration test")
    config.addinivalue_line("markers", "tracing: mark test as tracing functionality test")
    config.addinivalue_line("markers", "docs: mark test as API documentation test")


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up the test environment."""
    # Set up environment variables for testing
    os.environ["TESTING"] = "True"
    
    yield
    
    # Clean up
    os.environ.pop("TESTING", None)
