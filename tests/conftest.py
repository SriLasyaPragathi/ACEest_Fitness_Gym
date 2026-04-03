"""
Pytest configuration and fixtures for ACEest Fitness API tests
"""

import sys
import os
import pytest
import sqlite3
import tempfile
from datetime import date

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, get_db_connection, DATABASE_PATH


@pytest.fixture(scope='session')
def test_db():
    """Create a temporary test database"""
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    
    # Set environment variable for app to use test database
    os.environ['DATABASE_PATH'] = db_path
    
    # Patch app module database path
    import app as app_module
    app_module.DATABASE_PATH = db_path
    
    # Initialize database using app's init_db
    app_module.init_db()
    
    # Insert test users into database
    from app import get_db_connection
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                   ('admin', 'admin', 'Admin'))
        cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                   ('user1', 'pass123', 'User'))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Users might already exist
    finally:
        conn.close()
    
    yield db_path
    
    # Cleanup
    try:
        os.close(db_fd)
    except:
        pass
    try:
        os.unlink(db_path)
    except:
        pass


@pytest.fixture
def client(test_db):
    """Create a test Flask client with proper database configuration"""
    # Close any existing connections
    sqlite3.connect(test_db).close()
    
    # Configure Flask to use test database
    app.config['TESTING'] = True
    app.config['DATABASE_PATH'] = test_db
    
    # Patch the app module's DATABASE_PATH
    import app as app_module
    app_module.DATABASE_PATH = test_db
    
    # Create test client
    with app.test_client() as client:
        yield client
    
    # Clean up: close any open connections
    import gc
    gc.collect()  # Force garbage collection to close connections


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
