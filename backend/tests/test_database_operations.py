import pytest
import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError
import os
from datetime import datetime

from app.db.database import Base, get_db
from app.models.user import User
from app.models.workout import Exercise, WorkoutSession
from app.core.security import get_password_hash


class TestDatabaseOperations:
    """データベース操作のテストクラス"""

    @pytest.fixture(scope="module")
    def test_db_url(self):
        """テスト用データベースURLを生成"""
        # 環境変数からテストデータベースURLを取得
        return os.getenv(
            "TEST_DATABASE_URL",
            "postgresql://test_user:test_password@localhost:5432/test_tenax_fit"
        )

    @pytest.fixture(scope="module")
    def engine(self, test_db_url):
        """テスト用データベースエンジンを作成"""
        try:
            engine = create_engine(test_db_url)
            # データベース接続をテスト
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return engine
        except OperationalError as e:
            pytest.skip(f"Database not available: {e}")

    @pytest.fixture(scope="module")
    def TestSessionLocal(self, engine):
        """テスト用セッションファクトリを作成"""
        return sessionmaker(autocommit=False, autoflush=False, bind=engine)

    @pytest.fixture(scope="function")
    def db(self, TestSessionLocal, engine):
        """各テスト用のデータベースセッション"""
        # テーブルを作成
        Base.metadata.create_all(bind=engine)
        
        # セッションを作成
        session = TestSessionLocal()
        
        yield session
        
        # クリーンアップ
        session.close()
        # テーブルを削除
        Base.metadata.drop_all(bind=engine)

    def test_database_connection(self, db):
        """データベース接続の基本テスト"""
        # シンプルなクエリを実行
        result = db.execute(text("SELECT 1 as num"))
        assert result.scalar() == 1

    def test_create_user(self, db):
        """ユーザー作成のテスト"""
        # 新規ユーザーを作成
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("testpassword"),
            is_active=True,
            is_superuser=False
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # ユーザーが作成されたことを確認
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.created_at is not None

    def test_query_user(self, db):
        """ユーザークエリのテスト"""
        # ユーザーを作成
        user = User(
            email="query@example.com",
            username="queryuser",
            hashed_password=get_password_hash("password")
        )
        db.add(user)
        db.commit()
        
        # メールアドレスでユーザーを検索
        found_user = db.query(User).filter(User.email == "query@example.com").first()
        assert found_user is not None
        assert found_user.username == "queryuser"
        
        # ユーザー名でユーザーを検索
        found_user = db.query(User).filter(User.username == "queryuser").first()
        assert found_user is not None
        assert found_user.email == "query@example.com"

    def test_update_user(self, db):
        """ユーザー更新のテスト"""
        # ユーザーを作成
        user = User(
            email="update@example.com",
            username="updateuser",
            hashed_password=get_password_hash("password")
        )
        db.add(user)
        db.commit()
        
        # ユーザー情報を更新
        user.username = "updateduser"
        user.is_active = False
        db.commit()
        db.refresh(user)
        
        # 更新が反映されたことを確認
        assert user.username == "updateduser"
        assert user.is_active is False

    def test_delete_user(self, db):
        """ユーザー削除のテスト"""
        # ユーザーを作成
        user = User(
            email="delete@example.com",
            username="deleteuser",
            hashed_password=get_password_hash("password")
        )
        db.add(user)
        db.commit()
        user_id = user.id
        
        # ユーザーを削除
        db.delete(user)
        db.commit()
        
        # ユーザーが削除されたことを確認
        deleted_user = db.query(User).filter(User.id == user_id).first()
        assert deleted_user is None

    def test_create_exercise(self, db):
        """エクササイズ作成のテスト"""
        # エクササイズを作成
        exercise = Exercise(
            name="Test Squat",
            category="lower_body",
            muscle_groups=["quadriceps", "glutes"],
            equipment="barbell",
            difficulty="intermediate",
            instructions="Test instructions",
            tips=["tip1", "tip2"]
        )
        
        db.add(exercise)
        db.commit()
        db.refresh(exercise)
        
        # エクササイズが作成されたことを確認
        assert exercise.id is not None
        assert exercise.name == "Test Squat"
        assert len(exercise.muscle_groups) == 2
        assert exercise.muscle_groups[0] == "quadriceps"

    def test_create_workout_session(self, db):
        """ワークアウトセッション作成のテスト"""
        # ユーザーとエクササイズを作成
        user = User(
            email="workout@example.com",
            username="workoutuser",
            hashed_password=get_password_hash("password")
        )
        exercise = Exercise(
            name="Bench Press",
            category="upper_body",
            muscle_groups=["chest", "triceps"],
            equipment="barbell"
        )
        
        db.add(user)
        db.add(exercise)
        db.commit()
        
        # ワークアウトセッションを作成
        session = WorkoutSession(
            user_id=user.id,
            name="Test Workout",
            exercises=[
                {
                    "exercise_id": exercise.id,
                    "sets": 3,
                    "reps": [10, 10, 8],
                    "weight": [60, 65, 70]
                }
            ],
            duration=3600,  # 1時間
            calories_burned=300
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        # セッションが作成されたことを確認
        assert session.id is not None
        assert session.user_id == user.id
        assert len(session.exercises) == 1
        assert session.exercises[0]["exercise_id"] == exercise.id

    def test_transaction_rollback(self, db):
        """トランザクションロールバックのテスト"""
        # ユーザーを作成
        user = User(
            email="rollback@example.com",
            username="rollbackuser",
            hashed_password=get_password_hash("password")
        )
        db.add(user)
        
        # コミット前にロールバック
        db.rollback()
        
        # ユーザーが作成されていないことを確認
        found_user = db.query(User).filter(User.email == "rollback@example.com").first()
        assert found_user is None

    def test_bulk_insert(self, db):
        """バルクインサートのテスト"""
        # 複数のユーザーを一度に作成
        users = [
            User(
                email=f"bulk{i}@example.com",
                username=f"bulkuser{i}",
                hashed_password=get_password_hash("password")
            )
            for i in range(5)
        ]
        
        db.bulk_save_objects(users)
        db.commit()
        
        # すべてのユーザーが作成されたことを確認
        count = db.query(User).filter(User.email.like("bulk%@example.com")).count()
        assert count == 5

    def test_relationship_loading(self, db):
        """リレーションシップの読み込みテスト"""
        # ユーザーを作成
        user = User(
            email="relation@example.com",
            username="relationuser",
            hashed_password=get_password_hash("password")
        )
        db.add(user)
        db.commit()
        
        # 複数のワークアウトセッションを作成
        for i in range(3):
            session = WorkoutSession(
                user_id=user.id,
                name=f"Workout {i+1}",
                exercises=[],
                duration=1800
            )
            db.add(session)
        db.commit()
        
        # リレーションシップを通じてセッションを取得
        user_with_sessions = db.query(User).filter(
            User.email == "relation@example.com"
        ).first()
        
        sessions = db.query(WorkoutSession).filter(
            WorkoutSession.user_id == user_with_sessions.id
        ).all()
        
        assert len(sessions) == 3
        assert all(s.user_id == user_with_sessions.id for s in sessions)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])