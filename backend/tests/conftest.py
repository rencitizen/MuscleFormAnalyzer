"""
Pytest configuration and fixtures
"""
import pytest
import os
import tempfile
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set test environment
os.environ["ENVIRONMENT"] = "test"
os.environ["FIREBASE_PROJECT_ID"] = "test-project"
os.environ["FIREBASE_CREDENTIALS"] = "{}"

from app.main import app
from app.database import Base, get_db
from models.user import User

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def setup_database():
    """Create test database tables"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    # Clean up test database file
    if os.path.exists("test.db"):
        os.remove("test.db")

@pytest.fixture
def db_session(setup_database):
    """Create a test database session"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    """Create a test client"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db_session) -> User:
    """Create a test user"""
    user = User(
        id="test_user_123",
        email="test@example.com",
        display_name="Test User",
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers for test user"""
    # In real tests, you would mock Firebase auth
    return {"Authorization": "Bearer test_token_123"}

@pytest.fixture
def test_image():
    """Create a test image file"""
    import numpy as np
    import cv2
    
    # Create a simple test image
    image = np.zeros((480, 640, 3), dtype=np.uint8)
    # Add some content (white rectangle)
    cv2.rectangle(image, (100, 100), (300, 300), (255, 255, 255), -1)
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
        cv2.imwrite(f.name, image)
        yield f.name
    
    # Cleanup
    os.unlink(f.name)

@pytest.fixture
def test_video():
    """Create a test video file"""
    import numpy as np
    import cv2
    
    # Create a simple test video
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
        out = cv2.VideoWriter(f.name, fourcc, 20.0, (640, 480))
        
        # Write 30 frames
        for i in range(30):
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            # Add moving rectangle
            x = 100 + i * 5
            cv2.rectangle(frame, (x, 200), (x + 100, 300), (255, 255, 255), -1)
            out.write(frame)
        
        out.release()
        yield f.name
    
    # Cleanup
    os.unlink(f.name)