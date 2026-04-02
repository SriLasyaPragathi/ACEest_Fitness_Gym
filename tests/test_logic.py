"""
Test business logic and calculations
"""

import pytest
import json


class TestCalorieCalculation:
    """Test calorie calculation logic"""
    
    def test_fat_loss_calorie_calculation(self, client, headers, sample_client_data):
        """Test Fat Loss program calorie calculation (factor: 22)"""
        # Create client with known weight
        create_response = client.post('/api/clients',
            json=sample_client_data,
            headers=headers
        )
        client_id = json.loads(create_response.data)['client_id']
        
        # Calculate calories for Fat Loss
        response = client.post(f'/api/calories/{client_id}/calculate',
            json={'program_type': 'Fat Loss'},
            headers=headers
        )
        data = json.loads(response.data)
        
        # Expected: 85 (weight) * 22 (factor) = 1870
        assert data['recommended_calories'] == 1870
        assert data['factor'] == 22
    
    def test_muscle_gain_calorie_calculation(self, client, headers, sample_client_data):
        """Test Muscle Gain program calorie calculation (factor: 35)"""
        # Create client
        create_response = client.post('/api/clients',
            json=sample_client_data,
            headers=headers
        )
        client_id = json.loads(create_response.data)['client_id']
        
        # Calculate calories for Muscle Gain
        response = client.post(f'/api/calories/{client_id}/calculate',
            json={'program_type': 'Muscle Gain'},
            headers=headers
        )
        data = json.loads(response.data)
        
        # Expected: 85 * 35 = 2975
        assert data['recommended_calories'] == 2975
        assert data['factor'] == 35
    
    def test_beginner_calorie_calculation(self, client, headers, sample_client_data):
        """Test Beginner program calorie calculation (factor: 26)"""
        # Create client
        create_response = client.post('/api/clients',
            json=sample_client_data,
            headers=headers
        )
        client_id = json.loads(create_response.data)['client_id']
        
        # Calculate calories for Beginner
        response = client.post(f'/api/calories/{client_id}/calculate',
            json={'program_type': 'Beginner'},
            headers=headers
        )
        data = json.loads(response.data)
        
        # Expected: 85 * 26 = 2210
        assert data['recommended_calories'] == 2210
        assert data['factor'] == 26
    
    def test_calorie_calculation_different_weights(self, client, headers):
        """Test calorie calculation varies with weight"""
        # Create clients with different weights
        client1_data = {'name': 'Light Client', 'age': 30, 'weight': 70, 'height': 170}
        client2_data = {'name': 'Heavy Client', 'age': 30, 'weight': 100, 'height': 180}
        
        c1_response = client.post('/api/clients', json=client1_data, headers=headers)
        c2_response = client.post('/api/clients', json=client2_data, headers=headers)
        
        c1_id = json.loads(c1_response.data)['client_id']
        c2_id = json.loads(c2_response.data)['client_id']
        
        # Calculate calories for both
        r1 = client.post(f'/api/calories/{c1_id}/calculate',
            json={'program_type': 'Fat Loss'},
            headers=headers
        )
        r2 = client.post(f'/api/calories/{c2_id}/calculate',
            json={'program_type': 'Fat Loss'},
            headers=headers
        )
        
        c1_cals = json.loads(r1.data)['recommended_calories']
        c2_cals = json.loads(r2.data)['recommended_calories']
        
        # Heavier client should have more calories
        assert c2_cals > c1_cals
        # Expected: 70*22=1540, 100*22=2200
        assert c1_cals == 1540
        assert c2_cals == 2200
    
    def test_calorie_calculation_all_programs(self, client, headers, sample_client_data):
        """Test all program types calculate correctly"""
        # Create client
        create_response = client.post('/api/clients',
            json=sample_client_data,
            headers=headers
        )
        client_id = json.loads(create_response.data)['client_id']
        
        programs = {
            'Fat Loss': 22,
            'Muscle Gain': 35,
            'Beginner': 26
        }
        
        for program, factor in programs.items():
            response = client.post(f'/api/calories/{client_id}/calculate',
                json={'program_type': program},
                headers=headers
            )
            data = json.loads(response.data)
            expected = 85 * factor
            assert data['recommended_calories'] == expected
    
    def test_calorie_calculation_invalid_program(self, client, headers, sample_client_data):
        """Test calorie calculation with invalid program type"""
        create_response = client.post('/api/clients',
            json=sample_client_data,
            headers=headers
        )
        client_id = json.loads(create_response.data)['client_id']
        
        response = client.post(f'/api/calories/{client_id}/calculate',
            json={'program_type': 'InvalidProgram'},
            headers=headers
        )
        assert response.status_code == 400


class TestProgramGeneration:
    """Test program generation logic"""
    
    def test_program_exists(self, client, headers):
        """Test requesting programs endpoint"""
        response = client.get('/api/programs', headers=headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'Fat Loss' in data
        assert 'Muscle Gain' in data
        assert 'Beginner' in data
    
    def test_program_has_required_fields(self, client, headers):
        """Test program structure"""
        response = client.get('/api/programs', headers=headers)
        data = json.loads(response.data)
        
        for program_name, program_data in data.items():
            assert 'factor' in program_data
            assert 'description' in program_data
            assert 'examples' in program_data
    
    def test_program_generation_returns_valid_program(self, client, headers, sample_client_data):
        """Test generated program is from valid list"""
        create_response = client.post('/api/clients',
            json=sample_client_data,
            headers=headers
        )
        client_id = json.loads(create_response.data)['client_id']
        
        response = client.post(f'/api/programs/generate/{client_id}',
            json={'program_type': 'Fat Loss'},
            headers=headers
        )
        data = json.loads(response.data)
        
        assert 'program' in data
        assert data['program'] in ["Full Body HIIT", "Circuit Training", "Cardio + Weights"]
    
    def test_program_generation_all_types(self, client, headers, sample_client_data):
        """Test program generation for all program types"""
        create_response = client.post('/api/clients',
            json=sample_client_data,
            headers=headers
        )
        client_id = json.loads(create_response.data)['client_id']
        
        program_types = ['Fat Loss', 'Muscle Gain', 'Beginner']
        
        for program_type in program_types:
            response = client.post(f'/api/programs/generate/{client_id}',
                json={'program_type': program_type},
                headers=headers
            )
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['program_type'] == program_type
            assert 'program' in data
    
    def test_program_generation_invalid_type(self, client, headers, sample_client_data):
        """Test program generation with invalid program type"""
        create_response = client.post('/api/clients',
            json=sample_client_data,
            headers=headers
        )
        client_id = json.loads(create_response.data)['client_id']
        
        response = client.post(f'/api/programs/generate/{client_id}',
            json={'program_type': 'InvalidType'},
            headers=headers
        )
        assert response.status_code == 400


class TestDataValidation:
    """Test data validation logic"""
    
    def test_client_age_validation(self, client, headers):
        """Test client age validation"""
        # Valid age
        response = client.post('/api/clients',
            json={'name': 'Age Test', 'age': 25, 'weight': 80, 'height': 175},
            headers=headers
        )
        assert response.status_code == 201
    
    def test_client_weight_validation(self, client, headers):
        """Test client weight is accepted"""
        response = client.post('/api/clients',
            json={'name': 'Weight Test', 'age': 30, 'weight': 85.5, 'height': 180},
            headers=headers
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'client_id' in data
    
    def test_duplicate_client_name_rejected(self, client, headers, sample_client_data):
        """Test duplicate client name is rejected"""
        # Create first client
        client.post('/api/clients', json=sample_client_data, headers=headers)
        
        # Try to create duplicate
        response = client.post('/api/clients',
            json=sample_client_data,
            headers=headers
        )
        assert response.status_code == 409


class TestAdherenceTracking:
    """Test adherence tracking logic"""
    
    def test_valid_adherence_value(self, client, headers, sample_client_data, sample_progress_data):
        """Test valid adherence value (0-100)"""
        create_response = client.post('/api/clients',
            json=sample_client_data,
            headers=headers
        )
        client_id = json.loads(create_response.data)['client_id']
        
        response = client.post(f'/api/progress/{client_id}',
            json=sample_progress_data,
            headers=headers
        )
        assert response.status_code == 201
    
    def test_progress_adherence_tracked(self, client, headers, sample_client_data):
        """Test adherence value is stored and retrievable"""
        create_response = client.post('/api/clients',
            json=sample_client_data,
            headers=headers
        )
        client_id = json.loads(create_response.data)['client_id']
        
        # Add progress
        client.post(f'/api/progress/{client_id}',
            json={'adherence': 92},
            headers=headers
        )
        
        # Get progress
        response = client.get(f'/api/progress/{client_id}', headers=headers)
        data = json.loads(response.data)
        
        assert len(data['progress']) > 0
        assert data['progress'][0]['adherence'] == 92
