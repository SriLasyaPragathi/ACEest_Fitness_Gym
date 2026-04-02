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
    
    # Override DATABASE_PATH for testing
    os.environ['DATABASE_PATH'] = db_path
    
    # Initialize schema
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Create tables
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        role TEXT
    )
    """)
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        age INTEGER,
        height REAL,
        weight REAL,
        program TEXT,
        calories INTEGER,
        target_weight REAL,
        target_adherence INTEGER,
        membership_status TEXT,
        membership_end TEXT
    )
    """)
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_name TEXT,
        week TEXT,
        adherence INTEGER
    )
    """)
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS workouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_name TEXT,
        date TEXT,
        workout_type TEXT,
        duration_min INTEGER,
        notes TEXT
    )
    """)
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS exercises (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        workout_id INTEGER,
        name TEXT,
        sets INTEGER,
        reps INTEGER,
        weight REAL
    )
    """)
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_name TEXT,
        date TEXT,
        weight REAL,
        waist REAL,
        bodyfat REAL
    )
    """)
    
    # Insert test users
    cur.execute("INSERT INTO users VALUES (?, ?, ?)", ('admin', 'admin', 'Admin'))
    cur.execute("INSERT INTO users VALUES (?, ?, ?)", ('user1', 'pass123', 'User'))
    
    conn.commit()
    conn.close()
    
    yield db_path
    
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(test_db):
    """Create a test Flask client"""
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client


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
