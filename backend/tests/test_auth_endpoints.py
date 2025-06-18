import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import jwt
from sqlalchemy.orm import Session

from app.main import app
from app.models.user import User
from app.core.security import create_access_token, get_password_hash
from app.db.database import get_db

client = TestClient(app)


class TestAuthEndpoints:
    """認証関連のAPIエンドポイントのテストクラス"""

    @pytest.fixture
    def mock_db(self):
        """モックデータベースセッションのフィクスチャ"""
        db = MagicMock(spec=Session)
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
            hashed_password=get_password_hash("testpassword"),
            is_active=True,
            is_superuser=False,
            created_at=datetime.utcnow()
        )

    def test_login_success(self, override_get_db, mock_db, test_user):
        """正常なログインのテスト"""
        # データベースからユーザーが見つかる場合をモック
        mock_db.query().filter().first.return_value = test_user

        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "testpassword"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        
        # トークンの検証
        payload = jwt.decode(
            data["access_token"],
            options={"verify_signature": False}
        )
        assert payload["sub"] == "test@example.com"

    def test_login_invalid_credentials(self, override_get_db, mock_db):
        """無効な認証情報でのログインテスト"""
        # ユーザーが見つからない場合をモック
        mock_db.query().filter().first.return_value = None

        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "invalid@example.com",
                "password": "wrongpassword"
            }
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect username or password"

    def test_login_inactive_user(self, override_get_db, mock_db, test_user):
        """非アクティブユーザーのログインテスト"""
        test_user.is_active = False
        mock_db.query().filter().first.return_value = test_user

        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "testpassword"
            }
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Inactive user"

    def test_register_success(self, override_get_db, mock_db):
        """正常なユーザー登録のテスト"""
        # 既存ユーザーが存在しない場合をモック
        mock_db.query().filter().first.return_value = None
        
        # 新規ユーザーの作成をモック
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()

        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "newpassword123"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert "id" in data
        
        # データベース操作が呼ばれたことを確認
        assert mock_db.add.called
        assert mock_db.commit.called

    def test_register_duplicate_email(self, override_get_db, mock_db, test_user):
        """重複するメールアドレスでの登録テスト"""
        # 既存ユーザーが存在する場合をモック
        mock_db.query().filter().first.return_value = test_user

        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "anotheruser",
                "password": "password123"
            }
        )

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    def test_get_current_user_success(self, override_get_db, mock_db, test_user):
        """現在のユーザー情報取得のテスト"""
        # 有効なトークンを作成
        token = create_access_token(data={"sub": test_user.email})
        
        # ユーザーが見つかる場合をモック
        mock_db.query().filter().first.return_value = test_user

        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username

    def test_get_current_user_invalid_token(self):
        """無効なトークンでのユーザー情報取得テスト"""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]

    def test_get_current_user_no_token(self):
        """トークンなしでのユーザー情報取得テスト"""
        response = client.get("/api/v1/auth/me")

        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

    @patch('app.api.v1.endpoints.auth.oauth_manager')
    def test_google_oauth_callback_success(self, mock_oauth_manager, override_get_db, mock_db):
        """Google OAuth コールバックの成功テスト"""
        # OAuthManagerのモック設定
        mock_oauth_manager.handle_callback.return_value = {
            "access_token": "google_access_token",
            "id_token": "google_id_token"
        }
        
        # Google APIレスポンスのモック
        with patch('requests.get') as mock_get:
            mock_get.return_value.json.return_value = {
                "id": "google123",
                "email": "googleuser@gmail.com",
                "name": "Google User",
                "picture": "https://example.com/picture.jpg"
            }
            
            # 既存ユーザーが存在しない場合をモック
            mock_db.query().filter().first.return_value = None
            mock_db.add = Mock()
            mock_db.commit = Mock()
            mock_db.refresh = Mock()

            response = client.get(
                "/api/v1/auth/google/callback",
                params={
                    "code": "test_auth_code",
                    "state": "test_state"
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"

    @patch('app.api.v1.endpoints.auth.oauth_manager')
    def test_google_oauth_callback_existing_user(self, mock_oauth_manager, override_get_db, mock_db, test_user):
        """既存ユーザーでのGoogle OAuth コールバックテスト"""
        # 既存のGoogleユーザーを設定
        test_user.google_id = "google123"
        
        # OAuthManagerのモック設定
        mock_oauth_manager.handle_callback.return_value = {
            "access_token": "google_access_token",
            "id_token": "google_id_token"
        }
        
        with patch('requests.get') as mock_get:
            mock_get.return_value.json.return_value = {
                "id": "google123",
                "email": "test@example.com",
                "name": "Test User",
                "picture": "https://example.com/picture.jpg"
            }
            
            # 既存ユーザーが見つかる場合をモック
            mock_db.query().filter().first.return_value = test_user
            mock_db.commit = Mock()

            response = client.get(
                "/api/v1/auth/google/callback",
                params={
                    "code": "test_auth_code",
                    "state": "test_state"
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data

    def test_refresh_token_success(self, override_get_db, mock_db, test_user):
        """トークンリフレッシュの成功テスト"""
        # 有効なリフレッシュトークンを作成
        refresh_token = create_access_token(
            data={"sub": test_user.email, "type": "refresh"},
            expires_delta=timedelta(days=7)
        )
        
        # ユーザーが見つかる場合をモック
        mock_db.query().filter().first.return_value = test_user

        response = client.post(
            "/api/v1/auth/refresh",
            headers={"Authorization": f"Bearer {refresh_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_logout_success(self, override_get_db, mock_db, test_user):
        """ログアウトの成功テスト"""
        # 有効なトークンを作成
        token = create_access_token(data={"sub": test_user.email})
        
        # ユーザーが見つかる場合をモック
        mock_db.query().filter().first.return_value = test_user

        response = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert response.json()["message"] == "Successfully logged out"


if __name__ == "__main__":
    pytest.main([__file__])