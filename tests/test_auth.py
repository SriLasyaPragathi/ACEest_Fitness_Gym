"""
Test authentication logic
"""

import pytest
import json


class TestLoginFlow:
    """Test user authentication flow"""
    
    def test_valid_admin_login(self, client):
        """Test admin user login with valid credentials"""
        response = client.post('/api/login',
            json={'username': 'admin', 'password': 'admin'},
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['username'] == 'admin'
        assert data['role'] == 'Admin'
        assert data['token'] == 'admin:Admin'
    
    def test_valid_user_login(self, client):
        """Test regular user login with valid credentials"""
        response = client.post('/api/login',
            json={'username': 'user1', 'password': 'pass123'},
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['username'] == 'user1'
        assert data['role'] == 'User'
        assert data['token'] == 'user1:User'
    
    def test_wrong_password(self, client):
        """Test login with wrong password"""
        response = client.post('/api/login',
            json={'username': 'admin', 'password': 'wrongpass'},
            content_type='application/json'
        )
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_nonexistent_user(self, client):
        """Test login with non-existent user"""
        response = client.post('/api/login',
            json={'username': 'nonexistent', 'password': 'pass'},
            content_type='application/json'
        )
        assert response.status_code == 401
    
    def test_missing_username(self, client):
        """Test login without username"""
        response = client.post('/api/login',
            json={'password': 'admin'},
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_missing_password(self, client):
        """Test login without password"""
        response = client.post('/api/login',
            json={'username': 'admin'},
            content_type='application/json'
        )
        assert response.status_code == 400
    
    def test_missing_json_data(self, client):
        """Test login with missing JSON data"""
        response = client.post('/api/login',
            content_type='application/json'
        )
        assert response.status_code == 400


class TestTokenValidation:
    """Test token validation in endpoints"""
    
    def test_valid_token_format(self, client):
        """Test endpoint accepts valid token format"""
        headers = {'Authorization': 'Bearer admin:Admin'}
        response = client.get('/api/clients', headers=headers)
        # Should not return 401 (token format valid, though may return 200 or other)
        assert response.status_code != 401
    
    def test_missing_bearer_prefix(self, client):
        """Test token without Bearer prefix"""
        headers = {'Authorization': 'admin:Admin'}
        response = client.get('/api/clients', headers=headers)
        # Bearer prefix is required
        assert response.status_code == 401
    
    def test_malformed_token_missing_role(self, client):
        """Test malformed token without role"""
        headers = {'Authorization': 'Bearer admin'}
        response = client.get('/api/clients', headers=headers)
        assert response.status_code == 401
    
    def test_empty_token(self, client):
        """Test empty token"""
        headers = {'Authorization': 'Bearer '}
        response = client.get('/api/clients', headers=headers)
        assert response.status_code == 401
    
    def test_missing_authorization_header(self, client):
        """Test missing Authorization header"""
        response = client.get('/api/clients')
        assert response.status_code == 401
    
    def test_invalid_authorization_header_value(self, client):
        """Test invalid Authorization header value"""
        headers = {'Authorization': 'InvalidFormat'}
        response = client.get('/api/clients', headers=headers)
        assert response.status_code == 401
    
    def test_multiple_colons_in_token(self, client):
        """Test token with multiple colons"""
        headers = {'Authorization': 'Bearer admin:Admin:Extra'}
        response = client.get('/api/clients', headers=headers)
        # Token with extra colons should fail validation
        assert response.status_code == 401


class TestAuthenticationRequired:
    """Test that protected endpoints require authentication"""
    
    def test_clients_endpoint_requires_auth(self, client):
        """Test /api/clients requires authentication"""
        response = client.get('/api/clients')
        assert response.status_code == 401
    
    def test_programs_endpoint_requires_auth(self, client):
        """Test /api/programs requires authentication"""
        response = client.get('/api/programs')
        assert response.status_code == 401
    
    def test_progress_endpoint_requires_auth(self, client):
        """Test /api/progress requires authentication"""
        response = client.get('/api/progress/1')
        assert response.status_code == 401
    
    def test_workouts_endpoint_requires_auth(self, client):
        """Test /api/workouts requires authentication"""
        response = client.get('/api/workouts/1')
        assert response.status_code == 401
    
    def test_membership_endpoint_requires_auth(self, client):
        """Test /api/membership requires authentication"""
        response = client.get('/api/membership/1')
        assert response.status_code == 401
    
    def test_health_endpoint_no_auth_required(self, client):
        """Test /health doesn't require authentication"""
        response = client.get('/health')
        assert response.status_code == 200
    
    def test_login_endpoint_no_auth_required(self, client):
        """Test /api/login doesn't require authentication"""
        response = client.post('/api/login',
            json={'username': 'admin', 'password': 'admin'},
            content_type='application/json'
        )
        assert response.status_code == 200
