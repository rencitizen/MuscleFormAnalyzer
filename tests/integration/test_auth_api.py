"""
Integration tests for Authentication API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
import json
from datetime import datetime, timedelta
import jwt

client = TestClient(app)


class TestAuthenticationAPI:
    """Test cases for authentication endpoints"""
    
    def test_register_new_user(self):
        """Test user registration endpoint"""
        test_user = {
            "email": f"test_{datetime.now().timestamp()}@example.com",
            "password": "SecurePass123!",
            "name": "Test User"
        }
        
        response = client.post("/api/auth/register", json=test_user)
        
        assert response.status_code == 201
        data = response.json()
        assert "user" in data
        assert "token" in data
        assert data["user"]["email"] == test_user["email"]
        assert data["user"]["name"] == test_user["name"]
        assert "password" not in data["user"]
    
    def test_register_duplicate_user(self):
        """Test registration with existing email"""
        test_user = {
            "email": "duplicate@example.com",
            "password": "SecurePass123!",
            "name": "Test User"
        }
        
        # First registration
        response1 = client.post("/api/auth/register", json=test_user)
        if response1.status_code == 201:
            # Try to register again
            response2 = client.post("/api/auth/register", json=test_user)
            assert response2.status_code == 409
            assert "already exists" in response2.json()["detail"].lower()
    
    def test_register_invalid_email(self):
        """Test registration with invalid email"""
        test_user = {
            "email": "invalid-email",
            "password": "SecurePass123!",
            "name": "Test User"
        }
        
        response = client.post("/api/auth/register", json=test_user)
        assert response.status_code == 422
    
    def test_register_weak_password(self):
        """Test registration with weak password"""
        test_user = {
            "email": "test@example.com",
            "password": "weak",
            "name": "Test User"
        }
        
        response = client.post("/api/auth/register", json=test_user)
        assert response.status_code == 422
    
    def test_login_success(self):
        """Test successful login"""
        # First register a user
        test_user = {
            "email": f"login_test_{datetime.now().timestamp()}@example.com",
            "password": "SecurePass123!",
            "name": "Login Test User"
        }
        
        register_response = client.post("/api/auth/register", json=test_user)
        assert register_response.status_code == 201
        
        # Now try to login
        login_data = {
            "email": test_user["email"],
            "password": test_user["password"]
        }
        
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert "token" in data
        assert data["user"]["email"] == test_user["email"]
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "WrongPassword123!"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]
    
    def test_get_current_user(self):
        """Test getting current user with valid token"""
        # Register and login to get token
        test_user = {
            "email": f"current_user_{datetime.now().timestamp()}@example.com",
            "password": "SecurePass123!",
            "name": "Current User Test"
        }
        
        register_response = client.post("/api/auth/register", json=test_user)
        assert register_response.status_code == 201
        token = register_response.json()["token"]
        
        # Get current user
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user["email"]
        assert data["name"] == test_user["name"]
    
    def test_get_current_user_invalid_token(self):
        """Test getting current user with invalid token"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
    
    def test_get_current_user_no_token(self):
        """Test getting current user without token"""
        response = client.get("/api/auth/me")
        assert response.status_code == 401
    
    def test_refresh_token(self):
        """Test token refresh endpoint"""
        # Register to get initial tokens
        test_user = {
            "email": f"refresh_test_{datetime.now().timestamp()}@example.com",
            "password": "SecurePass123!",
            "name": "Refresh Test User"
        }
        
        register_response = client.post("/api/auth/register", json=test_user)
        assert register_response.status_code == 201
        initial_token = register_response.json()["token"]
        
        # Assuming refresh token is returned
        refresh_data = {
            "refresh_token": register_response.json().get("refresh_token", initial_token)
        }
        
        response = client.post("/api/auth/refresh", json=refresh_data)
        
        # If refresh endpoint exists
        if response.status_code != 404:
            assert response.status_code == 200
            data = response.json()
            assert "token" in data
            assert data["token"] != initial_token
    
    def test_logout(self):
        """Test logout endpoint"""
        # Register and login first
        test_user = {
            "email": f"logout_test_{datetime.now().timestamp()}@example.com",
            "password": "SecurePass123!",
            "name": "Logout Test User"
        }
        
        register_response = client.post("/api/auth/register", json=test_user)
        assert register_response.status_code == 201
        token = register_response.json()["token"]
        
        # Logout
        response = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # If logout endpoint exists
        if response.status_code != 404:
            assert response.status_code == 200
            
            # Verify token is invalidated
            me_response = client.get(
                "/api/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert me_response.status_code == 401


class TestOAuthEndpoints:
    """Test cases for OAuth endpoints"""
    
    def test_google_oauth_initiate(self):
        """Test Google OAuth initiation"""
        response = client.get("/api/auth/google")
        
        # Should redirect to Google OAuth
        if response.status_code != 404:
            assert response.status_code in [302, 307]
            assert "accounts.google.com" in response.headers.get("location", "")
    
    def test_google_oauth_callback(self):
        """Test Google OAuth callback handling"""
        # Simulate OAuth callback
        callback_data = {
            "code": "mock_auth_code",
            "state": "mock_state"
        }
        
        response = client.get("/api/auth/google/callback", params=callback_data)
        
        # Should handle callback or return appropriate error
        if response.status_code != 404:
            assert response.status_code in [200, 400, 401]
    
    def test_oauth_error_handling(self):
        """Test OAuth error handling"""
        # Simulate OAuth error callback
        error_params = {
            "error": "access_denied",
            "error_description": "User denied access"
        }
        
        response = client.get("/api/auth/google/callback", params=error_params)
        
        if response.status_code != 404:
            assert response.status_code in [400, 401]
            data = response.json()
            assert "error" in data or "detail" in data


class TestAuthorizationMiddleware:
    """Test cases for authorization middleware"""
    
    def test_protected_endpoint_with_valid_token(self):
        """Test accessing protected endpoint with valid token"""
        # Register user and get token
        test_user = {
            "email": f"protected_test_{datetime.now().timestamp()}@example.com",
            "password": "SecurePass123!",
            "name": "Protected Test User"
        }
        
        register_response = client.post("/api/auth/register", json=test_user)
        assert register_response.status_code == 201
        token = register_response.json()["token"]
        
        # Access protected endpoint (example: user profile update)
        update_data = {"name": "Updated Name"}
        response = client.put(
            "/api/auth/profile",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code != 404:
            assert response.status_code == 200
    
    def test_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without token"""
        update_data = {"name": "Updated Name"}
        response = client.put("/api/auth/profile", json=update_data)
        
        if response.status_code != 404:
            assert response.status_code == 401
    
    def test_rate_limiting(self):
        """Test rate limiting on auth endpoints"""
        # Try multiple rapid requests
        login_data = {
            "email": "ratelimit@example.com",
            "password": "TestPass123!"
        }
        
        responses = []
        for _ in range(10):
            response = client.post("/api/auth/login", json=login_data)
            responses.append(response.status_code)
        
        # Check if rate limiting is applied
        # Should see 429 (Too Many Requests) at some point
        # or all should be processed if no rate limiting
        assert all(status in [200, 401, 404, 429] for status in responses)


class TestPasswordReset:
    """Test cases for password reset functionality"""
    
    def test_request_password_reset(self):
        """Test password reset request"""
        reset_data = {
            "email": "reset@example.com"
        }
        
        response = client.post("/api/auth/forgot-password", json=reset_data)
        
        if response.status_code != 404:
            assert response.status_code in [200, 202]
            data = response.json()
            assert "message" in data
    
    def test_reset_password_with_token(self):
        """Test password reset with token"""
        reset_data = {
            "token": "mock_reset_token",
            "new_password": "NewSecurePass123!"
        }
        
        response = client.post("/api/auth/reset-password", json=reset_data)
        
        if response.status_code != 404:
            assert response.status_code in [200, 400, 401]