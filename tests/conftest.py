"""
Pytest configuration and fixtures for ACEest Fitness API tests
"""

import sys
import os
import pytest
import sqlite3
import tempfile
from datetime import date
import gc

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Global test database path
TEST_DB_PATH = None


def pytest_configure(config):
    """Create test database before any tests run"""
    global TEST_DB_PATH
    db_fd, TEST_DB_PATH = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)
    
    # Set database path in app module
    import app as app_module
    app_module.DATABASE_PATH = TEST_DB_PATH
    
    # Initialize database schema
    app_module.init_db()
    
    # Insert test users (admin is already created by init_db)
    conn = app_module.get_db_connection()
    cur = conn.cursor()
    
    # Insert user1 (admin already exists from init_db)
    try:
        cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                   ('user1', 'pass123', 'User'))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # User might already exist
    finally:
        conn.close()


def pytest_unconfigure(config):
    """Clean up test database after all tests"""
    global TEST_DB_PATH
    if TEST_DB_PATH and os.path.exists(TEST_DB_PATH):
        try:
            os.unlink(TEST_DB_PATH)
        except:
            pass


@pytest.fixture(autouse=True)
def reset_database():
    """Reset database state before each test"""
    # Force garbage collection to close any dangling connections
    gc.collect()
    
    yield
    
    # Cleanup after each test
    try:
        import app as app_module
        conn = app_module.get_db_connection()
        cur = conn.cursor()
        
        # Delete all test data (keep users)
        cur.execute("DELETE FROM clients")
        cur.execute("DELETE FROM progress")
        cur.execute("DELETE FROM workouts")
        cur.execute("DELETE FROM exercises")
        cur.execute("DELETE FROM metrics")
        
        conn.commit()
        conn.close()
    except Exception as e:
        pass
    
    # Force cleanup of connections
    gc.collect()


@pytest.fixture
def client():
    """Create Flask test client for each test"""
    import app as app_module
    
    # Configure app for testing
    app.config['TESTING'] = True
    app.config['DATABASE_PATH'] = TEST_DB_PATH
    app_module.DATABASE_PATH = TEST_DB_PATH
    
    # Create test client
    test_client = app.test_client()
    
    yield test_client
    
    # Cleanup
    test_client = None
    gc.collect()


@pytest.fixture
def test_db():
    """Direct database access fixture for database tests"""
    return TEST_DB_PATH


@pytest.fixture
def auth_token():
    """Get authentication token for testing"""
    return "admin:Admin"


@pytest.fixture
def headers(auth_token):
    """Get request headers with authentication"""
    return {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }


@pytest.fixture
def sample_client_data():
    """Sample client data for testing"""
    return {
        "name": "John Doe",
        "age": 30,
        "height": 180,
        "weight": 85,
        "program": "Fat Loss"
    }


@pytest.fixture
def sample_progress_data():
    """Sample progress data for testing"""
    return {
        "week": "2026-W14",
        "adherence": 85
    }


@pytest.fixture
def sample_workout_data():
    """Sample workout data for testing"""
    return {
        "date": date.today().isoformat(),
        "workout_type": "Strength",
        "duration_min": 60,
        "notes": "Good session"
    }
