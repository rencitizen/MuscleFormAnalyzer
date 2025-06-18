"""
Authentication API Tests
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi import status

class TestAuthAPI:
    """Test authentication endpoints"""
    
    @patch('firebase_admin.auth.verify_id_token')
    @patch('firebase_admin.auth.get_user')
    def test_login_success(self, mock_get_user, mock_verify_token, client, db_session):
        """Test successful login"""
        # Mock Firebase responses
        mock_verify_token.return_value = {
            'uid': 'test_firebase_uid',
            'email': 'new_user@example.com'
        }
        mock_get_user.return_value = MagicMock(
            uid='test_firebase_uid',
            email='new_user@example.com',
            display_name='New User',
            email_verified=True
        )
        
        response = client.post(
            "/api/auth/login",
            json={
                "id_token": "test_firebase_token",
                "device_info": {
                    "id": "test_device",
                    "platform": "web"
                }
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["user"]["email"] == "new_user@example.com"
        assert "session_id" in data
    
    @patch('firebase_admin.auth.verify_id_token')
    def test_login_invalid_token(self, mock_verify_token, client):
        """Test login with invalid token"""
        # Mock Firebase error
        mock_verify_token.side_effect = Exception("Invalid token")
        
        response = client.post(
            "/api/auth/login",
            json={
                "id_token": "invalid_token"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is False
        assert "error" in data
    
    @patch('firebase_admin.auth.verify_id_token')
    def test_get_current_user(self, mock_verify_token, client, test_user):
        """Test getting current user"""
        mock_verify_token.return_value = {
            'uid': test_user.id,
            'email': test_user.email
        }
        
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
    
    def test_get_current_user_no_auth(self, client):
        """Test getting current user without authentication"""
        response = client.get("/api/auth/me")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @patch('firebase_admin.auth.verify_id_token')
    def test_update_profile(self, mock_verify_token, client, test_user):
        """Test updating user profile"""
        mock_verify_token.return_value = {
            'uid': test_user.id,
            'email': test_user.email
        }
        
        response = client.put(
            "/api/auth/me",
            json={
                "display_name": "Updated Name",
                "birth_date": "1990-01-01",
                "height_cm": 175.5,
                "weight_kg": 70.0
            },
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["display_name"] == "Updated Name"
        assert data["profile"]["height_cm"] == 175.5
    
    @patch('firebase_admin.auth.verify_id_token')
    def test_logout(self, mock_verify_token, client, test_user, db_session):
        """Test logout"""
        mock_verify_token.return_value = {
            'uid': test_user.id,
            'email': test_user.email
        }
        
        # Create a session first
        from models.user import UserSession
        session = UserSession(
            user_id=test_user.id,
            is_active=True
        )
        db_session.add(session)
        db_session.commit()
        
        response = client.post(
            "/api/auth/logout",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        
        # Check session is deactivated
        db_session.refresh(session)
        assert session.is_active is False