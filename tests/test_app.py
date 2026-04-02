"""
Test suite for ACEest Fitness API endpoints
"""

import pytest
import json
from datetime import date


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check_success(self, client):
        """Test /health endpoint returns 200"""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'ok'
        assert data['service'] == 'ACEest Fitness API'
        assert 'timestamp' in data


class TestAuthenticationEndpoint:
    """Test authentication endpoints"""
    
    def test_login_success(self, client):
        """Test successful login"""
        response = client.post('/api/login', 
            json={'username': 'admin', 'password': 'admin'},
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['username'] == 'admin'
        assert data['role'] == 'Admin'
        assert 'token' in data
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        response = client.post('/api/login',
            json={'username': 'admin', 'password': 'wrong'},
            content_type='application/json'
        )
        assert response.status_code == 401
    
    def test_login_missing_credentials(self, client):
        """Test login with missing credentials"""
        response = client.post('/api/login',
            json={'username': 'admin'},
            content_type='application/json'
        )
        assert response.status_code == 400


class TestClientEndpoints:
    """Test client management endpoints"""
    
    def test_get_clients_requires_auth(self, client):
        """Test /api/clients requires authentication"""
        response = client.get('/api/clients')
        assert response.status_code == 401
    
    def test_get_clients_success(self, client, headers):
        """Test GET /api/clients with authentication"""
        response = client.get('/api/clients', headers=headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'clients' in data
        assert isinstance(data['clients'], list)
    
    def test_create_client_success(self, client, headers, sample_client_data):
        """Test POST /api/clients creates client"""
        response = client.post('/api/clients',
            json=sample_client_data,
            headers=headers
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'client_id' in data
    
    def test_create_client_missing_name(self, client, headers):
        """Test POST /api/clients without name"""
        response = client.post('/api/clients',
            json={'age': 30},
            headers=headers
        )
        assert response.status_code == 400
    
    def test_get_specific_client(self, client, headers, sample_client_data):
        """Test GET /api/clients/<id>"""
        # First create a client
        create_response = client.post('/api/clients',
            json=sample_client_data,
            headers=headers
        )
        client_id = json.loads(create_response.data)['client_id']
        
        # Then get it
        response = client.get(f'/api/clients/{client_id}', headers=headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['name'] == sample_client_data['name']
    
    def test_get_nonexistent_client(self, client, headers):
        """Test GET /api/clients/<id> for non-existent client"""
        response = client.get('/api/clients/9999', headers=headers)
        assert response.status_code == 404
    
    def test_update_client(self, client, headers, sample_client_data):
        """Test PUT /api/clients/<id>"""
        # Create client
        create_response = client.post('/api/clients',
            json=sample_client_data,
            headers=headers
        )
        client_id = json.loads(create_response.data)['client_id']
        
        # Update client
        update_data = {'age': 35, 'weight': 90}
        response = client.put(f'/api/clients/{client_id}',
            json=update_data,
            headers=headers
        )
        assert response.status_code == 200
    
    def test_delete_client(self, client, headers, sample_client_data):
        """Test DELETE /api/clients/<id>"""
        # Create client
        create_response = client.post('/api/clients',
            json=sample_client_data,
            headers=headers
        )
        client_id = json.loads(create_response.data)['client_id']
        
        # Delete client
        response = client.delete(f'/api/clients/{client_id}', headers=headers)
        assert response.status_code == 200
        
        # Verify deletion
        get_response = client.get(f'/api/clients/{client_id}', headers=headers)
        assert get_response.status_code == 404


class TestProgramEndpoints:
    """Test program management endpoints"""
    
    def test_get_programs(self, client, headers):
        """Test GET /api/programs"""
        response = client.get('/api/programs', headers=headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'Fat Loss' in data
        assert 'Muscle Gain' in data
        assert 'Beginner' in data
    
    def test_generate_program(self, client, headers, sample_client_data):
        """Test POST /api/programs/generate/<id>"""
        # Create client first
        create_response = client.post('/api/clients',
            json=sample_client_data,
            headers=headers
        )
        client_id = json.loads(create_response.data)['client_id']
        
        # Generate program
        response = client.post(f'/api/programs/generate/{client_id}',
            json={'program_type': 'Fat Loss'},
            headers=headers
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'program' in data


class TestCalorieEndpoints:
    """Test calorie calculation endpoints"""
    
    def test_calculate_calories(self, client, headers, sample_client_data):
        """Test POST /api/calories/<id>/calculate"""
        # Create client
        create_response = client.post('/api/clients',
            json=sample_client_data,
            headers=headers
        )
        client_id = json.loads(create_response.data)['client_id']
        
        # Calculate calories
        response = client.post(f'/api/calories/{client_id}/calculate',
            json={'program_type': 'Fat Loss'},
            headers=headers
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'recommended_calories' in data
        assert data['weight_kg'] == sample_client_data['weight']


class TestProgressEndpoints:
    """Test progress tracking endpoints"""
    
    def test_get_progress(self, client, headers, sample_client_data):
        """Test GET /api/progress/<id>"""
        # Create client
        create_response = client.post('/api/clients',
            json=sample_client_data,
            headers=headers
        )
        client_id = json.loads(create_response.data)['client_id']
        
        # Get progress
        response = client.get(f'/api/progress/{client_id}', headers=headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'progress' in data
    
    def test_add_progress(self, client, headers, sample_client_data, sample_progress_data):
        """Test POST /api/progress/<id>"""
        # Create client
        create_response = client.post('/api/clients',
            json=sample_client_data,
            headers=headers
        )
        client_id = json.loads(create_response.data)['client_id']
        
        # Add progress
        response = client.post(f'/api/progress/{client_id}',
            json=sample_progress_data,
            headers=headers
        )
        assert response.status_code == 201


class TestWorkoutEndpoints:
    """Test workout tracking endpoints"""
    
    def test_get_workouts(self, client, headers, sample_client_data):
        """Test GET /api/workouts/<id>"""
        # Create client
        create_response = client.post('/api/clients',
            json=sample_client_data,
            headers=headers
        )
        client_id = json.loads(create_response.data)['client_id']
        
        # Get workouts
        response = client.get(f'/api/workouts/{client_id}', headers=headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'workouts' in data
    
    def test_add_workout(self, client, headers, sample_client_data, sample_workout_data):
        """Test POST /api/workouts/<id>"""
        # Create client
        create_response = client.post('/api/clients',
            json=sample_client_data,
            headers=headers
        )
        client_id = json.loads(create_response.data)['client_id']
        
        # Add workout
        response = client.post(f'/api/workouts/{client_id}',
            json=sample_workout_data,
            headers=headers
        )
        assert response.status_code == 201


class TestMembershipEndpoints:
    """Test membership management endpoints"""
    
    def test_get_membership(self, client, headers, sample_client_data):
        """Test GET /api/membership/<id>"""
        # Create client
        create_response = client.post('/api/clients',
            json=sample_client_data,
            headers=headers
        )
        client_id = json.loads(create_response.data)['client_id']
        
        # Get membership
        response = client.get(f'/api/membership/{client_id}', headers=headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'membership_status' in data
    
    def test_update_membership(self, client, headers, sample_client_data):
        """Test PUT /api/membership/<id>"""
        # Create client
        create_response = client.post('/api/clients',
            json=sample_client_data,
            headers=headers
        )
        client_id = json.loads(create_response.data)['client_id']
        
        # Update membership
        response = client.put(f'/api/membership/{client_id}',
            json={'membership_status': 'Inactive', 'membership_end': '2026-12-31'},
            headers=headers
        )
        assert response.status_code == 200


class TestErrorHandling:
    """Test error handling"""
    
    def test_404_not_found(self, client):
        """Test 404 error"""
        response = client.get('/api/nonexistent', 
            headers={'Authorization': 'Bearer admin:Admin'}
        )
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_missing_auth_token(self, client):
        """Test missing authentication token"""
        response = client.get('/api/clients')
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_invalid_auth_token(self, client):
        """Test invalid authentication token"""
        response = client.get('/api/clients',
            headers={'Authorization': 'Bearer invalid'}
        )
        assert response.status_code == 401
