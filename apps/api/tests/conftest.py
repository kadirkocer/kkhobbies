import os
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.auth import hash_password
from app.db.fts import ensure_fts
from app.db.session import get_session
from app.main import app
from app.models import Hobby, HobbyType, User
from app.models.base import Base


@pytest.fixture(scope="session")
def test_db():
    """Create a test database"""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    database_url = f"sqlite:///{db_path}"

    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)

    # Setup FTS5 for testing
    session = TestingSessionLocal()
    try:
        ensure_fts(session)
    finally:
        session.close()

    yield TestingSessionLocal, engine

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def db_session(test_db):
    """Get a database session for testing"""
    TestingSessionLocal, engine = test_db
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture
def client(test_db):
    """Create a test client"""
    TestingSessionLocal, engine = test_db

    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_session] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    user = User(
        username="testuser",
        name="Test User",
        password_hash=hash_password("testpass123")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_hobby(db_session):
    """Create a test hobby"""
    hobby = Hobby(
        name="Test Hobby",
        color="#FF5733",
        icon="camera"
    )
    db_session.add(hobby)
    db_session.commit()
    db_session.refresh(hobby)
    return hobby


@pytest.fixture
def test_hobby_type(db_session):
    """Create a test hobby type"""
    hobby_type = HobbyType(
        key="test_type",
        title="Test Type",
        schema_json='{"type":"object","properties":{"test_prop":{"type":"string"}}}'
    )
    db_session.add(hobby_type)
    db_session.commit()
    db_session.refresh(hobby_type)
    return hobby_type
