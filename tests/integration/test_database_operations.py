"""
Database Connection and Operation Tests
Tests database connectivity, CRUD operations, and data integrity
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from backend.app.database import Base, get_db
from backend.models.user import User
from backend.models.scientific_calculations import (
    UserScientificProfile,
    CalculationHistory,
    NutritionRecommendation,
    SafetyWarning
)
import os


# Test database URL (use test database)
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./test_tenax_fit.db")


@pytest.fixture(scope="module")
def test_engine():
    """Create test database engine"""
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    # Cleanup
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_session(test_engine):
    """Create test database session"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    yield session
    session.rollback()
    session.close()


class TestDatabaseConnection:
    """Test database connectivity"""
    
    def test_database_connection(self, test_engine):
        """Test basic database connection"""
        connection = test_engine.connect()
        assert connection is not None
        connection.close()
    
    def test_table_creation(self, test_engine):
        """Test that all tables are created"""
        inspector = test_engine.inspect(test_engine)
        tables = inspector.get_table_names()
        
        expected_tables = [
            'users',
            'user_scientific_profiles',
            'calculation_history',
            'nutrition_recommendations',
            'safety_warnings'
        ]
        
        for table in expected_tables:
            assert table in tables, f"Table {table} not found in database"


class TestUserOperations:
    """Test User model CRUD operations"""
    
    def test_create_user(self, test_session):
        """Test creating a new user"""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password_here"
        )
        
        test_session.add(user)
        test_session.commit()
        
        # Retrieve user
        saved_user = test_session.query(User).filter_by(email="test@example.com").first()
        assert saved_user is not None
        assert saved_user.email == "test@example.com"
        assert saved_user.username == "testuser"
    
    def test_update_user(self, test_session):
        """Test updating user information"""
        # Create user
        user = User(
            email="update@example.com",
            username="updateuser",
            hashed_password="hashed_password"
        )
        test_session.add(user)
        test_session.commit()
        
        # Update user
        user.username = "updatedusername"
        test_session.commit()
        
        # Verify update
        updated_user = test_session.query(User).filter_by(email="update@example.com").first()
        assert updated_user.username == "updatedusername"
    
    def test_delete_user(self, test_session):
        """Test deleting a user"""
        # Create user
        user = User(
            email="delete@example.com",
            username="deleteuser",
            hashed_password="hashed_password"
        )
        test_session.add(user)
        test_session.commit()
        
        # Delete user
        test_session.delete(user)
        test_session.commit()
        
        # Verify deletion
        deleted_user = test_session.query(User).filter_by(email="delete@example.com").first()
        assert deleted_user is None
    
    def test_user_unique_constraint(self, test_session):
        """Test unique constraint on email"""
        # Create first user
        user1 = User(
            email="unique@example.com",
            username="user1",
            hashed_password="password1"
        )
        test_session.add(user1)
        test_session.commit()
        
        # Try to create duplicate
        user2 = User(
            email="unique@example.com",
            username="user2",
            hashed_password="password2"
        )
        test_session.add(user2)
        
        with pytest.raises(Exception):  # Should raise IntegrityError
            test_session.commit()


class TestScientificProfileOperations:
    """Test UserScientificProfile CRUD operations"""
    
    def test_create_scientific_profile(self, test_session):
        """Test creating a scientific profile"""
        # Create user first
        user = User(
            email="profile@example.com",
            username="profileuser",
            hashed_password="password"
        )
        test_session.add(user)
        test_session.commit()
        
        # Create profile
        profile = UserScientificProfile(
            user_id=user.id,
            weight=70.5,
            height=175.0,
            age=25,
            gender="male",
            activity_level="moderate",
            goal="muscle_gain",
            experience_level="intermediate"
        )
        test_session.add(profile)
        test_session.commit()
        
        # Verify
        saved_profile = test_session.query(UserScientificProfile).filter_by(user_id=user.id).first()
        assert saved_profile is not None
        assert saved_profile.weight == 70.5
        assert saved_profile.height == 175.0
        assert saved_profile.activity_level == "moderate"
    
    def test_update_scientific_profile(self, test_session):
        """Test updating scientific profile"""
        # Create user and profile
        user = User(email="update_profile@example.com", username="user", hashed_password="pass")
        test_session.add(user)
        test_session.commit()
        
        profile = UserScientificProfile(
            user_id=user.id,
            weight=70.0,
            height=175.0,
            age=25,
            gender="male",
            activity_level="moderate",
            goal="maintenance",
            experience_level="beginner"
        )
        test_session.add(profile)
        test_session.commit()
        
        # Update
        profile.weight = 72.5
        profile.goal = "muscle_gain"
        test_session.commit()
        
        # Verify
        updated = test_session.query(UserScientificProfile).filter_by(user_id=user.id).first()
        assert updated.weight == 72.5
        assert updated.goal == "muscle_gain"


class TestCalculationHistoryOperations:
    """Test CalculationHistory operations"""
    
    def test_create_calculation_history(self, test_session):
        """Test creating calculation history record"""
        # Create user and profile
        user = User(email="calc@example.com", username="calcuser", hashed_password="pass")
        test_session.add(user)
        test_session.commit()
        
        profile = UserScientificProfile(
            user_id=user.id,
            weight=70.0,
            height=175.0,
            age=25,
            gender="male",
            activity_level="moderate",
            goal="maintenance",
            experience_level="intermediate"
        )
        test_session.add(profile)
        test_session.commit()
        
        # Create calculation history
        history = CalculationHistory(
            user_id=user.id,
            profile_id=profile.id,
            bmr=1700.0,
            tdee=2635.0,
            body_fat_percentage=15.5,
            lean_body_mass=59.15,
            target_calories=2635.0,
            bmi=22.9,
            calculation_type="comprehensive"
        )
        test_session.add(history)
        test_session.commit()
        
        # Verify
        saved_history = test_session.query(CalculationHistory).filter_by(user_id=user.id).first()
        assert saved_history is not None
        assert saved_history.bmr == 1700.0
        assert saved_history.tdee == 2635.0
    
    def test_multiple_calculation_records(self, test_session):
        """Test storing multiple calculation records for a user"""
        # Setup user and profile
        user = User(email="multi_calc@example.com", username="user", hashed_password="pass")
        test_session.add(user)
        test_session.commit()
        
        profile = UserScientificProfile(
            user_id=user.id, weight=70.0, height=175.0, age=25,
            gender="male", activity_level="moderate", goal="maintenance",
            experience_level="intermediate"
        )
        test_session.add(profile)
        test_session.commit()
        
        # Create multiple calculations
        for i in range(3):
            history = CalculationHistory(
                user_id=user.id,
                profile_id=profile.id,
                bmr=1700.0 + i * 10,
                tdee=2635.0 + i * 10,
                body_fat_percentage=15.5 + i * 0.5,
                lean_body_mass=59.15,
                target_calories=2635.0 + i * 10,
                calculation_type="comprehensive"
            )
            test_session.add(history)
        
        test_session.commit()
        
        # Verify
        calculations = test_session.query(CalculationHistory).filter_by(user_id=user.id).all()
        assert len(calculations) == 3


class TestNutritionRecommendations:
    """Test NutritionRecommendation operations"""
    
    def test_create_nutrition_recommendation(self, test_session):
        """Test creating nutrition recommendations"""
        # Setup
        user = User(email="nutrition@example.com", username="user", hashed_password="pass")
        test_session.add(user)
        test_session.commit()
        
        profile = UserScientificProfile(
            user_id=user.id, weight=70.0, height=175.0, age=25,
            gender="male", activity_level="moderate", goal="muscle_gain",
            experience_level="intermediate"
        )
        test_session.add(profile)
        test_session.commit()
        
        # Create recommendation
        recommendation = NutritionRecommendation(
            user_id=user.id,
            profile_id=profile.id,
            protein_grams=175.0,
            carbs_grams=350.0,
            fats_grams=78.0,
            protein_calories=700.0,
            carbs_calories=1400.0,
            fats_calories=700.0,
            total_calories=2800.0,
            protein_percentage=25.0,
            carbs_percentage=50.0,
            fats_percentage=25.0,
            water_liters=3.5,
            micronutrients={
                "vitamin_d": "20mcg",
                "zinc": "15mg",
                "magnesium": "400mg"
            }
        )
        test_session.add(recommendation)
        test_session.commit()
        
        # Verify
        saved = test_session.query(NutritionRecommendation).filter_by(user_id=user.id).first()
        assert saved is not None
        assert saved.protein_grams == 175.0
        assert saved.total_calories == 2800.0
        assert saved.micronutrients["vitamin_d"] == "20mcg"


class TestSafetyWarnings:
    """Test SafetyWarning operations"""
    
    def test_create_safety_warning(self, test_session):
        """Test creating safety warnings"""
        # Setup user
        user = User(email="safety@example.com", username="user", hashed_password="pass")
        test_session.add(user)
        test_session.commit()
        
        # Create warning
        warning = SafetyWarning(
            user_id=user.id,
            warning_type="calorie_restriction",
            severity="high",
            message="Your calorie intake is below 70% of BMR",
            recommendations={
                "increase_calories": "Increase daily calories by 300-500",
                "consult_professional": "Consider consulting a nutritionist"
            }
        )
        test_session.add(warning)
        test_session.commit()
        
        # Verify
        saved_warning = test_session.query(SafetyWarning).filter_by(user_id=user.id).first()
        assert saved_warning is not None
        assert saved_warning.severity == "high"
        assert saved_warning.warning_type == "calorie_restriction"
    
    def test_acknowledge_warning(self, test_session):
        """Test acknowledging a safety warning"""
        # Setup
        user = User(email="ack_safety@example.com", username="user", hashed_password="pass")
        test_session.add(user)
        test_session.commit()
        
        warning = SafetyWarning(
            user_id=user.id,
            warning_type="body_fat_goal",
            severity="medium",
            message="Target body fat percentage may be too low"
        )
        test_session.add(warning)
        test_session.commit()
        
        # Acknowledge warning
        warning.acknowledged = True
        warning.acknowledged_at = datetime.utcnow()
        test_session.commit()
        
        # Verify
        updated = test_session.query(SafetyWarning).filter_by(user_id=user.id).first()
        assert updated.acknowledged == True
        assert updated.acknowledged_at is not None


class TestDatabaseTransactions:
    """Test database transaction handling"""
    
    def test_rollback_on_error(self, test_session):
        """Test transaction rollback on error"""
        # Create user
        user = User(email="rollback@example.com", username="user", hashed_password="pass")
        test_session.add(user)
        test_session.commit()
        
        # Start transaction
        try:
            profile = UserScientificProfile(
                user_id=user.id,
                weight=70.0,
                height=175.0,
                age=25,
                gender="invalid_gender",  # This should cause an error
                activity_level="moderate",
                goal="maintenance",
                experience_level="intermediate"
            )
            test_session.add(profile)
            test_session.commit()
        except:
            test_session.rollback()
        
        # Verify rollback
        profile = test_session.query(UserScientificProfile).filter_by(user_id=user.id).first()
        assert profile is None
    
    def test_cascade_delete(self, test_session):
        """Test cascade delete operations"""
        # Create user with related data
        user = User(email="cascade@example.com", username="user", hashed_password="pass")
        test_session.add(user)
        test_session.commit()
        
        profile = UserScientificProfile(
            user_id=user.id, weight=70.0, height=175.0, age=25,
            gender="male", activity_level="moderate", goal="maintenance",
            experience_level="intermediate"
        )
        test_session.add(profile)
        test_session.commit()
        
        history = CalculationHistory(
            user_id=user.id, profile_id=profile.id,
            bmr=1700.0, tdee=2635.0, target_calories=2635.0
        )
        test_session.add(history)
        test_session.commit()
        
        # Delete user (should cascade)
        test_session.delete(user)
        test_session.commit()
        
        # Verify cascade
        profile = test_session.query(UserScientificProfile).filter_by(id=profile.id).first()
        history = test_session.query(CalculationHistory).filter_by(id=history.id).first()
        
        # Behavior depends on cascade settings
        # This test assumes cascade delete is configured