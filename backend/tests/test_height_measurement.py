"""
Height Measurement API Tests
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi import status
import io

class TestHeightMeasurementAPI:
    """Test height measurement endpoints"""
    
    @patch('firebase_admin.auth.verify_id_token')
    def test_manual_height_measurement(self, mock_verify_token, client, test_user):
        """Test manual height measurement recording"""
        mock_verify_token.return_value = {'uid': test_user.id}
        
        response = client.post(
            "/api/height/measure/manual",
            json={
                "height_cm": 175.5,
                "measurement_method": "manual",
                "notes": "Measured with tape measure"
            },
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["height_cm"] == 175.5
        assert data["confidence"] == 1.0
        assert data["method"] == "manual"
        assert "measurement_id" in data
    
    @patch('firebase_admin.auth.verify_id_token')
    def test_manual_height_invalid_range(self, mock_verify_token, client, test_user):
        """Test manual height measurement with invalid height"""
        mock_verify_token.return_value = {'uid': test_user.id}
        
        # Test too short
        response = client.post(
            "/api/height/measure/manual",
            json={"height_cm": 30.0},
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "between 50cm and 250cm" in response.json()["detail"]
        
        # Test too tall
        response = client.post(
            "/api/height/measure/manual",
            json={"height_cm": 300.0},
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    @patch('firebase_admin.auth.verify_id_token')
    def test_video_height_measurement(self, mock_verify_token, client, test_user, test_video):
        """Test video-based height measurement"""
        mock_verify_token.return_value = {'uid': test_user.id}
        
        with open(test_video, 'rb') as f:
            response = client.post(
                "/api/height/measure/video/upload",
                files={"file": ("test.mp4", f, "video/mp4")},
                data={
                    "reference_object": "credit_card",
                    "reference_height_mm": "85.6"
                },
                headers={"Authorization": "Bearer test_token"}
            )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # The test video won't produce valid measurements,
        # but we should get a proper error response
        if data["success"]:
            assert "height_cm" in data
            assert "confidence" in data
            assert data["method"] == "video"
        else:
            assert "error" in data
    
    @patch('firebase_admin.auth.verify_id_token')
    def test_video_height_invalid_file(self, mock_verify_token, client, test_user):
        """Test video height measurement with invalid file type"""
        mock_verify_token.return_value = {'uid': test_user.id}
        
        # Send an image instead of video
        fake_file = io.BytesIO(b"not a video")
        
        response = client.post(
            "/api/height/measure/video/upload",
            files={"file": ("test.txt", fake_file, "text/plain")},
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "must be a video" in response.json()["detail"]
    
    @patch('firebase_admin.auth.verify_id_token')
    def test_height_measurement_history(self, mock_verify_token, client, test_user, db_session):
        """Test getting height measurement history"""
        mock_verify_token.return_value = {'uid': test_user.id}
        
        # Add some measurements
        from models.user import UserBodyMeasurement
        from datetime import datetime, timedelta
        
        for i in range(3):
            measurement = UserBodyMeasurement(
                user_id=test_user.id,
                height_cm=175.0 + i * 0.5,
                measurement_method="manual",
                measured_at=datetime.utcnow() - timedelta(days=i)
            )
            db_session.add(measurement)
        db_session.commit()
        
        response = client.get(
            "/api/height/history",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert len(data["measurements"]) == 3
        assert data["measurements"][0]["height_cm"] == 176.0  # Most recent
    
    def test_get_measurement_methods(self, client):
        """Test getting available measurement methods"""
        response = client.get("/api/height/methods")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "methods" in data
        assert len(data["methods"]) >= 2
        
        # Check method structure
        manual_method = next(m for m in data["methods"] if m["id"] == "manual")
        assert manual_method["name"] == "手動測定"
        assert "description" in manual_method
        assert "pros" in manual_method
        assert "cons" in manual_method
    
    @patch('firebase_admin.auth.verify_id_token')
    def test_delete_measurement(self, mock_verify_token, client, test_user, db_session):
        """Test deleting a height measurement"""
        mock_verify_token.return_value = {'uid': test_user.id}
        
        # Create a measurement
        from models.user import UserBodyMeasurement
        measurement = UserBodyMeasurement(
            user_id=test_user.id,
            height_cm=175.0,
            measurement_method="manual"
        )
        db_session.add(measurement)
        db_session.commit()
        db_session.refresh(measurement)
        
        response = client.delete(
            f"/api/height/measurements/{measurement.id}",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        
        # Verify it's deleted
        assert db_session.query(UserBodyMeasurement).filter_by(id=measurement.id).first() is None
    
    @patch('firebase_admin.auth.verify_id_token')
    def test_delete_measurement_not_found(self, mock_verify_token, client, test_user):
        """Test deleting non-existent measurement"""
        mock_verify_token.return_value = {'uid': test_user.id}
        
        response = client.delete(
            "/api/height/measurements/99999",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND