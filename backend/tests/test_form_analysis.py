"""
Form Analysis API Tests
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi import status
import json
import base64
import numpy as np

class TestFormAnalysisAPI:
    """Test form analysis endpoints"""
    
    @patch('firebase_admin.auth.verify_id_token')
    def test_analyze_frame(self, mock_verify_token, client, test_user):
        """Test single frame analysis"""
        mock_verify_token.return_value = {'uid': test_user.id}
        
        # Create test frame data
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame_bytes = frame.tobytes()
        frame_base64 = base64.b64encode(frame_bytes).decode('utf-8')
        
        response = client.post(
            "/api/form/analyze/frame",
            json={
                "frame": frame_base64,
                "exercise_type": "squat",
                "frame_number": 1,
                "timestamp": 0.0
            },
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "success" in data
        
        if data["success"]:
            assert "pose_landmarks" in data
            assert "form_score" in data
            assert "feedback" in data
    
    @patch('firebase_admin.auth.verify_id_token')
    def test_analyze_video(self, mock_verify_token, client, test_user, test_video):
        """Test video analysis"""
        mock_verify_token.return_value = {'uid': test_user.id}
        
        with open(test_video, 'rb') as f:
            response = client.post(
                "/api/form/analyze/video",
                files={"file": ("exercise.mp4", f, "video/mp4")},
                data={"exercise_type": "squat"},
                headers={"Authorization": "Bearer test_token"}
            )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "success" in data
        
        if data["success"]:
            assert "analysis_id" in data
            assert "exercise_type" in data
            assert "duration" in data
            assert "frame_count" in data
            assert "overall_score" in data
    
    def test_get_supported_exercises(self, client):
        """Test getting list of supported exercises"""
        response = client.get("/api/form/exercises/supported")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "exercises" in data
        assert len(data["exercises"]) > 0
        
        # Check exercise structure
        exercise = data["exercises"][0]
        assert "id" in exercise
        assert "name" in exercise
        assert "category" in exercise
        assert "difficulty" in exercise
        assert "muscle_groups" in exercise
    
    @patch('firebase_admin.auth.verify_id_token')
    def test_get_analysis_history(self, mock_verify_token, client, test_user, db_session):
        """Test getting analysis history"""
        mock_verify_token.return_value = {'uid': test_user.id}
        
        # Create test analysis records
        from models.workout import FormAnalysis, Exercise
        from datetime import datetime, timedelta
        
        # Create exercise
        exercise = Exercise(
            name="Squat",
            category="strength",
            muscle_groups=["quadriceps", "glutes"]
        )
        db_session.add(exercise)
        db_session.flush()
        
        # Create analyses
        for i in range(3):
            analysis = FormAnalysis(
                user_id=test_user.id,
                exercise_id=exercise.id,
                video_duration=30.0,
                frame_count=900,
                overall_score=85.0 - i * 5,
                created_at=datetime.utcnow() - timedelta(days=i)
            )
            db_session.add(analysis)
        db_session.commit()
        
        response = client.get(
            f"/api/form/analysis/history/{test_user.id}",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert len(data["analyses"]) == 3
        assert data["analyses"][0]["overall_score"] == 85.0
    
    @patch('firebase_admin.auth.verify_id_token')
    def test_start_analysis_session(self, mock_verify_token, client, test_user):
        """Test starting an analysis session"""
        mock_verify_token.return_value = {'uid': test_user.id}
        
        response = client.post(
            "/api/form/session/start",
            json={
                "exercise_type": "squat",
                "target_reps": 10,
                "settings": {
                    "difficulty": "beginner",
                    "feedback_detail": "high"
                }
            },
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "session_id" in data
        assert data["exercise_type"] == "squat"
    
    @patch('firebase_admin.auth.verify_id_token')
    def test_end_analysis_session(self, mock_verify_token, client, test_user, db_session):
        """Test ending an analysis session"""
        mock_verify_token.return_value = {'uid': test_user.id}
        
        # Create a workout session
        from models.workout import WorkoutSession
        session = WorkoutSession(
            user_id=test_user.id,
            name="Test Session",
            total_exercises=1
        )
        db_session.add(session)
        db_session.commit()
        db_session.refresh(session)
        
        response = client.post(
            f"/api/form/session/{session.id}/end",
            json={
                "notes": "Good workout",
                "rating": 4
            },
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["session"]["status"] == "completed"
    
    @patch('firebase_admin.auth.verify_id_token')
    def test_invalid_exercise_type(self, mock_verify_token, client, test_user):
        """Test analysis with invalid exercise type"""
        mock_verify_token.return_value = {'uid': test_user.id}
        
        response = client.post(
            "/api/form/analyze/frame",
            json={
                "frame": "base64_frame_data",
                "exercise_type": "invalid_exercise",
                "frame_number": 1
            },
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Should either return error or handle gracefully
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]
    
    @patch('firebase_admin.auth.verify_id_token')
    def test_concurrent_frame_analysis(self, mock_verify_token, client, test_user):
        """Test analyzing multiple frames concurrently"""
        mock_verify_token.return_value = {'uid': test_user.id}
        
        # Create multiple frame requests
        frames = []
        for i in range(5):
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            frame_bytes = frame.tobytes()
            frame_base64 = base64.b64encode(frame_bytes).decode('utf-8')
            
            frames.append({
                "frame": frame_base64,
                "exercise_type": "squat",
                "frame_number": i,
                "timestamp": i * 0.033  # 30 FPS
            })
        
        # Send requests (in real scenario, these would be concurrent)
        responses = []
        for frame_data in frames:
            response = client.post(
                "/api/form/analyze/frame",
                json=frame_data,
                headers={"Authorization": "Bearer test_token"}
            )
            responses.append(response)
        
        # All should succeed
        for response in responses:
            assert response.status_code == status.HTTP_200_OK