"""
Health Check and Integration Tests
"""
import pytest
from unittest.mock import patch
from fastapi import status

class TestHealthCheck:
    """Test health check endpoints"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "MuscleFormAnalyzer Backend API"
        assert data["version"] == "1.0.0"
        assert data["status"] == "healthy"
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "database" in data
        assert "timestamp" in data
        assert "version" in data
        assert "environment" in data
    
    def test_cors_headers(self, client):
        """Test CORS headers are properly set"""
        response = client.options("/api/auth/login")
        
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers

class TestErrorHandling:
    """Test error handling and responses"""
    
    def test_404_not_found(self, client):
        """Test 404 error handling"""
        response = client.get("/api/nonexistent")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "error" in data or "detail" in data
    
    def test_validation_error(self, client):
        """Test validation error handling"""
        response = client.post(
            "/api/auth/login",
            json={"invalid_field": "value"}  # Missing required fields
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data
    
    @patch('firebase_admin.auth.verify_id_token')
    def test_authentication_error(self, mock_verify_token, client):
        """Test authentication error handling"""
        mock_verify_token.side_effect = Exception("Invalid token")
        
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

class TestMiddleware:
    """Test custom middleware"""
    
    def test_request_id_header(self, client):
        """Test request ID is added to responses"""
        response = client.get("/")
        
        assert "x-request-id" in response.headers
    
    def test_response_time_header(self, client):
        """Test response time is added to headers"""
        response = client.get("/")
        
        assert "x-process-time" in response.headers
        process_time = float(response.headers["x-process-time"])
        assert process_time > 0
    
    def test_security_headers(self, client):
        """Test security headers are present"""
        response = client.get("/")
        
        assert response.headers.get("x-content-type-options") == "nosniff"
        assert response.headers.get("x-frame-options") == "DENY"
        assert response.headers.get("x-xss-protection") == "1; mode=block"

class TestIntegration:
    """End-to-end integration tests"""
    
    @patch('firebase_admin.auth.verify_id_token')
    @patch('firebase_admin.auth.get_user')
    def test_complete_user_flow(self, mock_get_user, mock_verify_token, client, db_session):
        """Test complete user registration and usage flow"""
        # Step 1: New user login
        mock_verify_token.return_value = {
            'uid': 'integration_test_user',
            'email': 'integration@test.com'
        }
        mock_get_user.return_value = MagicMock(
            uid='integration_test_user',
            email='integration@test.com',
            display_name='Integration Test',
            email_verified=True
        )
        
        login_response = client.post(
            "/api/auth/login",
            json={"id_token": "test_token"}
        )
        assert login_response.status_code == status.HTTP_200_OK
        
        # Step 2: Update profile
        profile_response = client.put(
            "/api/auth/me",
            json={
                "display_name": "Updated Integration Test",
                "height_cm": 175.0,
                "weight_kg": 70.0
            },
            headers={"Authorization": "Bearer test_token"}
        )
        assert profile_response.status_code == status.HTTP_200_OK
        
        # Step 3: Record height measurement
        height_response = client.post(
            "/api/height/measure/manual",
            json={"height_cm": 175.5},
            headers={"Authorization": "Bearer test_token"}
        )
        assert height_response.status_code == status.HTTP_200_OK
        
        # Step 4: Get measurement history
        history_response = client.get(
            "/api/height/history",
            headers={"Authorization": "Bearer test_token"}
        )
        assert history_response.status_code == status.HTTP_200_OK
        assert len(history_response.json()["measurements"]) >= 1
    
    @patch('firebase_admin.auth.verify_id_token')
    def test_concurrent_requests(self, mock_verify_token, client, test_user):
        """Test handling concurrent requests"""
        mock_verify_token.return_value = {'uid': test_user.id}
        
        # Simulate concurrent requests to different endpoints
        endpoints = [
            ("/api/auth/me", "GET", None),
            ("/api/height/methods", "GET", None),
            ("/api/form/exercises/supported", "GET", None),
        ]
        
        responses = []
        for endpoint, method, data in endpoints:
            if method == "GET":
                response = client.get(
                    endpoint,
                    headers={"Authorization": "Bearer test_token"}
                )
            else:
                response = client.post(
                    endpoint,
                    json=data,
                    headers={"Authorization": "Bearer test_token"}
                )
            responses.append(response)
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == status.HTTP_200_OK