"""
Test configuration and common fixtures.
"""

import os
import tempfile
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.main import app
from app.models.database import Base, File, Question
from app.services.ai_factory import get_ai_service
from app.services.mock_ai_service import MockAIService


class TestSettings(Settings):
    """Test-specific settings that override default settings."""

    environment: str = "test"
    testing: bool = True
    database_url: str = "sqlite:///./test.db"
    upload_directory: str = "./test_uploads"

    # Use smaller limits for testing
    max_file_size: int = 1024 * 1024  # 1MB
    claude_max_tokens: int = 1000


@pytest.fixture(scope="session")
def test_settings() -> TestSettings:
    """Provide test settings."""
    return TestSettings()


@pytest.fixture(scope="session")
def test_engine(test_settings: TestSettings):
    """Create test database engine."""
    engine = create_engine(
        test_settings.database_url,
        connect_args={"check_same_thread": False},  # SQLite specific
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    yield engine

    # Cleanup
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_db_session(test_engine):
    """Create a test database session."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )

    # Create a transaction for this test
    connection = test_engine.connect()
    transaction = connection.begin()

    # Create a session bound to this transaction
    session = TestingSessionLocal(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def test_upload_dir(test_settings: TestSettings) -> Generator[Path, None, None]:
    """Create a temporary upload directory for testing."""
    upload_dir = Path(test_settings.upload_directory)
    upload_dir.mkdir(exist_ok=True)

    yield upload_dir

    # Cleanup uploaded test files
    if upload_dir.exists():
        for file in upload_dir.glob("*"):
            file.unlink()
        upload_dir.rmdir()


@pytest.fixture(scope="function")
def mock_ai_service() -> MockAIService:
    """Provide mock AI service."""
    return MockAIService()


@pytest.fixture(scope="function")
def clean_db(test_db_session):
    """Clean database before each test."""
    # Delete all data from test database
    test_db_session.query(File).delete()
    test_db_session.query(Question).delete()
    test_db_session.commit()


@pytest.fixture(scope="function")
def test_client(
    test_db_session,
    test_settings: TestSettings,
    mock_ai_service,
    test_upload_dir,
    clean_db,
):
    """Create test client with dependency overrides."""

    # Clear any existing overrides first
    app.dependency_overrides.clear()

    # Override dependencies
    app.dependency_overrides[get_db] = lambda: test_db_session
    app.dependency_overrides[get_settings] = lambda: test_settings
    app.dependency_overrides[get_ai_service] = lambda: mock_ai_service

    with TestClient(app) as client:
        yield client

    # Clear overrides
    app.dependency_overrides.clear()


@pytest.fixture
def sample_pdf_content() -> bytes:
    """Generate sample PDF content for testing."""
    # This creates a minimal PDF structure
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
72 720 Td
(Test PDF content) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000203 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
295
%%EOF"""
    return pdf_content


@pytest.fixture
def sample_questions() -> list[dict]:
    """Sample questions for testing."""
    return [
        {"text": "In welcher Form sind die Angebote einzureichen?", "type": "question"},
        {
            "text": "Wann ist die Frist für die Einreichung von Bieterfragen?",
            "type": "question",
        },
    ]


@pytest.fixture
def sample_conditions() -> list[dict]:
    """Sample conditions for testing."""
    return [
        {"text": "Ist die Abgabefrist vor dem 31.12.2025?", "type": "condition"},
        {"text": "Sind elektronische Angebote zugelassen?", "type": "condition"},
    ]


@pytest.fixture
def sample_checklist_request() -> dict:
    """Sample checklist request for testing."""
    return {
        "file_ids": [1, 2],
        "questions": ["In welcher Form sind die Angebote einzureichen?"],
        "conditions": ["Ist die Abgabefrist vor dem 31.12.2025?"],
    }


@pytest.fixture
def sample_chat_request() -> dict:
    """Sample chat request for testing."""
    return {
        "message": "What are the main requirements in these documents?",
        "file_ids": [1, 2],
    }
