import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime
import json
import io
from PIL import Image
import numpy as np

from app.main import app
from app.models.user import User
from app.models.workout import Exercise, WorkoutSession, FormAnalysis
from app.core.security import create_access_token
from app.db.database import get_db

client = TestClient(app)


class TestFormAnalysisEndpoints:
    """フォーム分析関連のAPIエンドポイントのテストクラス"""

    @pytest.fixture
    def mock_db(self):
        """モックデータベースセッションのフィクスチャ"""
        db = MagicMock()
        yield db

    @pytest.fixture
    def override_get_db(self, mock_db):
        """get_db依存関数をオーバーライドするフィクスチャ"""
        def _override_get_db():
            yield mock_db
        
        app.dependency_overrides[get_db] = _override_get_db
        yield
        app.dependency_overrides.clear()

    @pytest.fixture
    def test_user(self):
        """テスト用ユーザーデータ"""
        return User(
            id=1,
            email="test@example.com",
            username="testuser",
            is_active=True
        )

    @pytest.fixture
    def auth_headers(self, test_user):
        """認証ヘッダーのフィクスチャ"""
        token = create_access_token(data={"sub": test_user.email})
        return {"Authorization": f"Bearer {token}"}

    @pytest.fixture
    def test_exercise(self):
        """テスト用エクササイズデータ"""
        return Exercise(
            id=1,
            name="Squat",
            category="lower_body",
            muscle_groups=["quadriceps", "glutes", "hamstrings"],
            equipment="barbell",
            difficulty="intermediate"
        )

    @pytest.fixture
    def test_video_file(self):
        """テスト用ビデオファイルのフィクスチャ"""
        # ダミービデオファイルを作成
        video_content = b"fake video content"
        return io.BytesIO(video_content)

    @pytest.fixture
    def test_image_file(self):
        """テスト用画像ファイルのフィクスチャ"""
        # ダミー画像を作成
        img = Image.new('RGB', (640, 480), color='red')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        return img_byte_arr

    @patch('app.services.form_analyzer_v3.FormAnalyzerV3')
    def test_analyze_video_success(self, mock_analyzer_class, override_get_db, mock_db, test_user, auth_headers, test_exercise, test_video_file):
        """ビデオ分析の成功テスト"""
        # ユーザーとエクササイズが見つかる場合をモック
        mock_db.query().filter().first.side_effect = [test_user, test_exercise]
        
        # FormAnalyzerのモック
        mock_analyzer = Mock()
        mock_analyzer_class.return_value = mock_analyzer
        mock_analyzer.analyze_video = AsyncMock(return_value={
            "overall_score": 85.5,
            "frame_analyses": [
                {
                    "frame_number": 0,
                    "timestamp": 0.0,
                    "pose_score": 90.0,
                    "keypoints": {},
                    "angles": {"knee": 90, "hip": 45},
                    "feedback": ["Good knee angle", "Maintain hip position"]
                }
            ],
            "summary": {
                "total_frames": 1,
                "average_score": 85.5,
                "key_improvements": ["Focus on depth", "Keep back straight"]
            }
        })
        
        # データベース操作のモック
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()

        response = client.post(
            "/api/v1/form-analysis/analyze-video",
            headers=auth_headers,
            files={"video": ("test_video.mp4", test_video_file, "video/mp4")},
            data={"exercise_id": "1"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "analysis_id" in data
        assert data["overall_score"] == 85.5
        assert "frame_analyses" in data
        assert "summary" in data
        
        # FormAnalysisモデルがデータベースに追加されたことを確認
        assert mock_db.add.called
        assert mock_db.commit.called

    def test_analyze_video_no_auth(self, test_video_file):
        """認証なしでのビデオ分析テスト"""
        response = client.post(
            "/api/v1/form-analysis/analyze-video",
            files={"video": ("test_video.mp4", test_video_file, "video/mp4")},
            data={"exercise_id": "1"}
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

    def test_analyze_video_invalid_exercise(self, override_get_db, mock_db, test_user, auth_headers, test_video_file):
        """無効なエクササイズIDでのビデオ分析テスト"""
        # ユーザーは見つかるがエクササイズが見つからない場合をモック
        mock_db.query().filter().first.side_effect = [test_user, None]

        response = client.post(
            "/api/v1/form-analysis/analyze-video",
            headers=auth_headers,
            files={"video": ("test_video.mp4", test_video_file, "video/mp4")},
            data={"exercise_id": "999"}
        )

        assert response.status_code == 404
        assert "Exercise not found" in response.json()["detail"]

    @patch('app.services.form_analyzer_v3.FormAnalyzerV3')
    def test_analyze_image_success(self, mock_analyzer_class, override_get_db, mock_db, test_user, auth_headers, test_exercise, test_image_file):
        """画像分析の成功テスト"""
        # ユーザーとエクササイズが見つかる場合をモック
        mock_db.query().filter().first.side_effect = [test_user, test_exercise]
        
        # FormAnalyzerのモック
        mock_analyzer = Mock()
        mock_analyzer_class.return_value = mock_analyzer
        mock_analyzer.analyze_image = AsyncMock(return_value={
            "pose_score": 88.0,
            "keypoints": {
                "nose": {"x": 0.5, "y": 0.3, "confidence": 0.95},
                "left_shoulder": {"x": 0.4, "y": 0.4, "confidence": 0.90}
            },
            "angles": {
                "knee_angle": 92.5,
                "hip_angle": 45.0,
                "elbow_angle": 180.0
            },
            "feedback": [
                "Good squat depth",
                "Keep knees aligned with toes",
                "Maintain neutral spine"
            ]
        })

        response = client.post(
            "/api/v1/form-analysis/analyze-image",
            headers=auth_headers,
            files={"image": ("test_image.jpg", test_image_file, "image/jpeg")},
            data={"exercise_id": "1"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["pose_score"] == 88.0
        assert "keypoints" in data
        assert "angles" in data
        assert len(data["feedback"]) == 3

    def test_get_analysis_history_success(self, override_get_db, mock_db, test_user, auth_headers):
        """分析履歴取得の成功テスト"""
        # ユーザーが見つかる場合をモック
        mock_db.query().filter().first.return_value = test_user
        
        # 分析履歴のモック
        mock_analyses = [
            FormAnalysis(
                id=1,
                user_id=test_user.id,
                exercise_id=1,
                overall_score=85.5,
                created_at=datetime.utcnow(),
                analysis_data=json.dumps({
                    "summary": {"average_score": 85.5}
                })
            ),
            FormAnalysis(
                id=2,
                user_id=test_user.id,
                exercise_id=1,
                overall_score=90.0,
                created_at=datetime.utcnow(),
                analysis_data=json.dumps({
                    "summary": {"average_score": 90.0}
                })
            )
        ]
        
        mock_query = Mock()
        mock_query.filter().order_by().limit().offset().all.return_value = mock_analyses
        mock_db.query.return_value = mock_query

        response = client.get(
            "/api/v1/form-analysis/history",
            headers=auth_headers,
            params={"limit": 10, "offset": 0}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["overall_score"] == 85.5
        assert data[1]["overall_score"] == 90.0

    def test_get_analysis_detail_success(self, override_get_db, mock_db, test_user, auth_headers):
        """分析詳細取得の成功テスト"""
        # ユーザーが見つかる場合をモック
        mock_db.query().filter().first.return_value = test_user
        
        # 分析データのモック
        mock_analysis = FormAnalysis(
            id=1,
            user_id=test_user.id,
            exercise_id=1,
            overall_score=85.5,
            created_at=datetime.utcnow(),
            analysis_data=json.dumps({
                "frame_analyses": [
                    {
                        "frame_number": 0,
                        "pose_score": 85.5,
                        "feedback": ["Good form"]
                    }
                ],
                "summary": {
                    "average_score": 85.5,
                    "key_improvements": ["Focus on depth"]
                }
            })
        )
        
        mock_query = Mock()
        mock_query.filter().first.return_value = mock_analysis
        mock_db.query.return_value = mock_query

        response = client.get(
            "/api/v1/form-analysis/1",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["overall_score"] == 85.5
        assert "analysis_data" in data

    def test_get_analysis_detail_not_found(self, override_get_db, mock_db, test_user, auth_headers):
        """存在しない分析詳細取得のテスト"""
        # ユーザーが見つかる場合をモック
        mock_db.query().filter().first.return_value = test_user
        
        # 分析が見つからない場合をモック
        mock_query = Mock()
        mock_query.filter().first.return_value = None
        mock_db.query.return_value = mock_query

        response = client.get(
            "/api/v1/form-analysis/999",
            headers=auth_headers
        )

        assert response.status_code == 404
        assert "Analysis not found" in response.json()["detail"]

    def test_delete_analysis_success(self, override_get_db, mock_db, test_user, auth_headers):
        """分析削除の成功テスト"""
        # ユーザーが見つかる場合をモック
        mock_db.query().filter().first.return_value = test_user
        
        # 分析データのモック
        mock_analysis = FormAnalysis(
            id=1,
            user_id=test_user.id,
            exercise_id=1,
            overall_score=85.5
        )
        
        mock_query = Mock()
        mock_query.filter().first.return_value = mock_analysis
        mock_db.query.return_value = mock_query
        mock_db.delete = Mock()
        mock_db.commit = Mock()

        response = client.delete(
            "/api/v1/form-analysis/1",
            headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["message"] == "Analysis deleted successfully"
        assert mock_db.delete.called
        assert mock_db.commit.called

    @patch('app.services.form_analyzer_v3.FormAnalyzerV3')
    def test_compare_analyses_success(self, mock_analyzer_class, override_get_db, mock_db, test_user, auth_headers):
        """分析比較の成功テスト"""
        # ユーザーが見つかる場合をモック
        mock_db.query().filter().first.return_value = test_user
        
        # 複数の分析データのモック
        mock_analyses = [
            FormAnalysis(
                id=1,
                user_id=test_user.id,
                exercise_id=1,
                overall_score=85.5,
                created_at=datetime.utcnow(),
                analysis_data=json.dumps({
                    "summary": {"average_score": 85.5}
                })
            ),
            FormAnalysis(
                id=2,
                user_id=test_user.id,
                exercise_id=1,
                overall_score=90.0,
                created_at=datetime.utcnow(),
                analysis_data=json.dumps({
                    "summary": {"average_score": 90.0}
                })
            )
        ]
        
        mock_query = Mock()
        mock_query.filter().all.return_value = mock_analyses
        mock_db.query.return_value = mock_query

        response = client.post(
            "/api/v1/form-analysis/compare",
            headers=auth_headers,
            json={"analysis_ids": [1, 2]}
        )

        assert response.status_code == 200
        data = response.json()
        assert "comparison" in data
        assert "improvement_percentage" in data
        assert data["improvement_percentage"] == pytest.approx(5.26, rel=0.01)


if __name__ == "__main__":
    pytest.main([__file__])