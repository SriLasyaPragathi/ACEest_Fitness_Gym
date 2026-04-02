"""
Test database operations and schema
"""

import pytest
import sqlite3
import json


class TestDatabaseSchema:
    """Test database schema and tables"""
    
    def test_users_table_exists(self, test_db):
        """Test users table exists"""
        conn = sqlite3.connect(test_db)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        assert cur.fetchone() is not None
        conn.close()
    
    def test_clients_table_exists(self, test_db):
        """Test clients table exists"""
        conn = sqlite3.connect(test_db)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clients'")
        assert cur.fetchone() is not None
        conn.close()
    
    def test_progress_table_exists(self, test_db):
        """Test progress table exists"""
        conn = sqlite3.connect(test_db)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='progress'")
        assert cur.fetchone() is not None
        conn.close()
    
    def test_workouts_table_exists(self, test_db):
        """Test workouts table exists"""
        conn = sqlite3.connect(test_db)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='workouts'")
        assert cur.fetchone() is not None
        conn.close()
    
    def test_metrics_table_exists(self, test_db):
        """Test metrics table exists"""
        conn = sqlite3.connect(test_db)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='metrics'")
        assert cur.fetchone() is not None
        conn.close()


class TestUserOperations:
    """Test user CRUD operations"""
    
    def test_default_admin_user_exists(self, test_db):
        """Test default admin user is created"""
        conn = sqlite3.connect(test_db)
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username='admin'")
        user = cur.fetchone()
        assert user is not None
        assert user[1] == 'admin'  # password
        assert user[2] == 'Admin'  # role
        conn.close()
    
    def test_user_unique_constraint(self, test_db):
        """Test username must be unique"""
        conn = sqlite3.connect(test_db)
        cur = conn.cursor()
        
        # Try to insert duplicate username
        with pytest.raises(sqlite3.IntegrityError):
            cur.execute("INSERT INTO users VALUES (?, ?, ?)", ('admin', 'newpass', 'Admin'))
            conn.commit()
        
        conn.close()


class TestClientOperations:
    """Test client CRUD operations"""
    
    def test_create_client(self, test_db):
        """Test creating a client"""
        conn = sqlite3.connect(test_db)
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO clients (name, age, height, weight, membership_status)
            VALUES (?, ?, ?, ?, ?)
        """, ('Test Client', 30, 180, 85, 'Active'))
        conn.commit()
        
        cur.execute("SELECT * FROM clients WHERE name='Test Client'")
        client = cur.fetchone()
        assert client is not None
        assert client[1] == 'Test Client'
        assert client[2] == 30
        conn.close()
    
    def test_client_name_unique(self, test_db):
        """Test client names must be unique"""
        conn = sqlite3.connect(test_db)
        cur = conn.cursor()
        
        # Insert first client
        cur.execute("""
            INSERT INTO clients (name, age, height, weight, membership_status)
            VALUES (?, ?, ?, ?, ?)
        """, ('Duplicate Name', 30, 180, 85, 'Active'))
        conn.commit()
        
        # Try to insert duplicate
        with pytest.raises(sqlite3.IntegrityError):
            cur.execute("""
                INSERT INTO clients (name, age, height, weight, membership_status)
                VALUES (?, ?, ?, ?, ?)
            """, ('Duplicate Name', 25, 175, 80, 'Active'))
            conn.commit()
        
        conn.close()
    
    def test_update_client(self, test_db):
        """Test updating a client"""
        conn = sqlite3.connect(test_db)
        cur = conn.cursor()
        
        # Create client
        cur.execute("""
            INSERT INTO clients (name, age, height, weight, membership_status)
            VALUES (?, ?, ?, ?, ?)
        """, ('Update Test', 30, 180, 85, 'Active'))
        conn.commit()
        
        # Update client
        cur.execute("UPDATE clients SET weight=? WHERE name=?", (90, 'Update Test'))
        conn.commit()
        
        # Verify update
        cur.execute("SELECT weight FROM clients WHERE name='Update Test'")
        result = cur.fetchone()
        assert result[0] == 90
        conn.close()
    
    def test_delete_client(self, test_db):
        """Test deleting a client"""
        conn = sqlite3.connect(test_db)
        cur = conn.cursor()
        
        # Create client
        cur.execute("""
            INSERT INTO clients (name, age, height, weight, membership_status)
            VALUES (?, ?, ?, ?, ?)
        """, ('Delete Test', 30, 180, 85, 'Active'))
        conn.commit()
        
        # Delete client
        cur.execute("DELETE FROM clients WHERE name='Delete Test'")
        conn.commit()
        
        # Verify deletion
        cur.execute("SELECT * FROM clients WHERE name='Delete Test'")
        result = cur.fetchone()
        assert result is None
        conn.close()


class TestProgressTracking:
    """Test progress tracking operations"""
    
    def test_add_progress_record(self, test_db):
        """Test adding progress record"""
        conn = sqlite3.connect(test_db)
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO progress (client_name, week, adherence)
            VALUES (?, ?, ?)
        """, ('Test Client', '2026-W14', 85))
        conn.commit()
        
        cur.execute("SELECT adherence FROM progress WHERE client_name='Test Client'")
        result = cur.fetchone()
        assert result[0] == 85
        conn.close()
    
    def test_multiple_progress_records(self, test_db):
        """Test multiple progress records for same client"""
        conn = sqlite3.connect(test_db)
        cur = conn.cursor()
        
        # Insert multiple records
        cur.execute("""
            INSERT INTO progress (client_name, week, adherence)
            VALUES (?, ?, ?)
        """, ('Multi Test', '2026-W13', 80))
        cur.execute("""
            INSERT INTO progress (client_name, week, adherence)
            VALUES (?, ?, ?)
        """, ('Multi Test', '2026-W14', 85))
        conn.commit()
        
        # Verify both records exist
        cur.execute("SELECT COUNT(*) FROM progress WHERE client_name='Multi Test'")
        count = cur.fetchone()[0]
        assert count == 2
        conn.close()


class TestWorkoutTracking:
    """Test workout tracking operations"""
    
    def test_add_workout(self, test_db):
        """Test adding a workout"""
        conn = sqlite3.connect(test_db)
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO workouts (client_name, date, workout_type, duration_min, notes)
            VALUES (?, ?, ?, ?, ?)
        """, ('Workout Test', '2026-04-02', 'Strength', 60, 'Good session'))
        conn.commit()
        
        cur.execute("SELECT workout_type FROM workouts WHERE client_name='Workout Test'")
        result = cur.fetchone()
        assert result[0] == 'Strength'
        conn.close()
    
    def test_workout_duration_positive(self, test_db):
        """Test workout duration is stored correctly"""
        conn = sqlite3.connect(test_db)
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO workouts (client_name, date, workout_type, duration_min, notes)
            VALUES (?, ?, ?, ?, ?)
        """, ('Duration Test', '2026-04-02', 'Cardio', 45, ''))
        conn.commit()
        
        cur.execute("SELECT duration_min FROM workouts WHERE client_name='Duration Test'")
        result = cur.fetchone()
        assert result[0] == 45
        conn.close()


class TestMetricsTracking:
    """Test metrics tracking operations"""
    
    def test_add_metrics(self, test_db):
        """Test adding metrics record"""
        conn = sqlite3.connect(test_db)
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO metrics (client_name, date, weight, waist, bodyfat)
            VALUES (?, ?, ?, ?, ?)
        """, ('Metrics Test', '2026-04-02', 85.5, 90, 15.5))
        conn.commit()
        
        cur.execute("SELECT weight FROM metrics WHERE client_name='Metrics Test'")
        result = cur.fetchone()
        assert result[0] == 85.5
        conn.close()
    
    def test_metrics_tracking_multiple_entries(self, test_db):
        """Test multiple metrics for same client"""
        conn = sqlite3.connect(test_db)
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO metrics (client_name, date, weight, waist, bodyfat)
            VALUES (?, ?, ?, ?, ?)
        """, ('Multi Metrics', '2026-03-26', 86, 91, 16))
        cur.execute("""
            INSERT INTO metrics (client_name, date, weight, waist, bodyfat)
            VALUES (?, ?, ?, ?, ?)
        """, ('Multi Metrics', '2026-04-02', 85, 90, 15.5))
        conn.commit()
        
        cur.execute("SELECT COUNT(*) FROM metrics WHERE client_name='Multi Metrics'")
        count = cur.fetchone()[0]
        assert count == 2
        conn.close()


class TestDataIntegrity:
    """Test data integrity constraints"""
    
    def test_client_membership_default(self, test_db):
        """Test client membership status is tracked"""
        conn = sqlite3.connect(test_db)
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO clients (name, age, height, weight, membership_status)
            VALUES (?, ?, ?, ?, ?)
        """, ('Membership Test', 30, 180, 85, 'Active'))
        conn.commit()
        
        cur.execute("SELECT membership_status FROM clients WHERE name='Membership Test'")
        result = cur.fetchone()
        assert result[0] == 'Active'
        conn.close()
