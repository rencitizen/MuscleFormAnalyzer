"""
Database Connection and Operation Tests
"""
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from app.database import Base, get_db
from models.user import User, UserProfile, UserSession, UserBodyMeasurement
from models.workout import Exercise, WorkoutSession, FormAnalysis
from models.nutrition import Food, MealEntry, MealFoodItem, NutritionGoal
from models.progress import Goal, Achievement, Streak, ProgressSnapshot

class TestDatabaseConnection:
    """Test database connection and basic operations"""
    
    def test_database_connection(self, db_session):
        """Test basic database connection"""
        # Execute a simple query
        result = db_session.execute(text("SELECT 1"))
        assert result.scalar() == 1
    
    def test_table_creation(self, setup_database):
        """Test that all tables are created"""
        # Get list of table names
        from sqlalchemy import inspect
        inspector = inspect(db_session.bind)
        tables = inspector.get_table_names()
        
        expected_tables = [
            'users', 'user_profiles', 'user_settings', 'user_sessions',
            'user_body_measurements', 'exercises', 'workout_sessions',
            'form_analyses', 'workout_records', 'personal_records',
            'training_programs', 'meal_entries', 'meal_food_items',
            'foods', 'nutrition_goals', 'goals', 'achievements',
            'streaks', 'progress_snapshots'
        ]
        
        for table in expected_tables:
            assert table in tables, f"Table {table} not found in database"

class TestUserOperations:
    """Test user-related database operations"""
    
    def test_create_user(self, db_session):
        """Test creating a new user"""
        user = User(
            id="test_create_user_123",
            email="create@example.com",
            display_name="Create Test User"
        )
        db_session.add(user)
        db_session.commit()
        
        # Verify user was created
        saved_user = db_session.query(User).filter_by(id="test_create_user_123").first()
        assert saved_user is not None
        assert saved_user.email == "create@example.com"
        assert saved_user.display_name == "Create Test User"
    
    def test_update_user(self, db_session, test_user):
        """Test updating user information"""
        test_user.display_name = "Updated Name"
        test_user.height_cm = 180.0
        db_session.commit()
        
        # Verify update
        updated_user = db_session.query(User).filter_by(id=test_user.id).first()
        assert updated_user.display_name == "Updated Name"
        assert updated_user.height_cm == 180.0
    
    def test_user_cascade_delete(self, db_session, test_user):
        """Test cascading delete for user"""
        # Create related records
        profile = UserProfile(user_id=test_user.id)
        session = UserSession(user_id=test_user.id)
        measurement = UserBodyMeasurement(
            user_id=test_user.id,
            height_cm=175.0
        )
        
        db_session.add_all([profile, session, measurement])
        db_session.commit()
        
        # Delete user
        db_session.delete(test_user)
        db_session.commit()
        
        # Verify cascade delete
        assert db_session.query(UserProfile).filter_by(user_id=test_user.id).first() is None
        assert db_session.query(UserSession).filter_by(user_id=test_user.id).first() is None
        assert db_session.query(UserBodyMeasurement).filter_by(user_id=test_user.id).first() is None
    
    def test_user_relationships(self, db_session, test_user):
        """Test user relationship loading"""
        # Create related records
        profile = UserProfile(
            user_id=test_user.id,
            bio="Test bio",
            preferred_language="ja"
        )
        db_session.add(profile)
        db_session.commit()
        
        # Load user with relationships
        user = db_session.query(User).filter_by(id=test_user.id).first()
        assert user.profile is not None
        assert user.profile.bio == "Test bio"

class TestWorkoutOperations:
    """Test workout-related database operations"""
    
    def test_create_exercise(self, db_session):
        """Test creating exercises"""
        exercise = Exercise(
            name="Test Squat",
            name_ja="テストスクワット",
            category="strength",
            muscle_groups=["quadriceps", "glutes"],
            difficulty="beginner"
        )
        db_session.add(exercise)
        db_session.commit()
        
        saved = db_session.query(Exercise).filter_by(name="Test Squat").first()
        assert saved is not None
        assert saved.name_ja == "テストスクワット"
        assert "quadriceps" in saved.muscle_groups
    
    def test_workout_session_with_analysis(self, db_session, test_user):
        """Test creating workout session with form analysis"""
        # Create exercise
        exercise = Exercise(
            name="Push-up",
            category="strength",
            muscle_groups=["chest", "triceps"]
        )
        db_session.add(exercise)
        db_session.flush()
        
        # Create workout session
        session = WorkoutSession(
            user_id=test_user.id,
            name="Morning Workout",
            total_exercises=1
        )
        db_session.add(session)
        db_session.flush()
        
        # Create form analysis
        analysis = FormAnalysis(
            user_id=test_user.id,
            exercise_id=exercise.id,
            workout_session_id=session.id,
            video_duration=30.0,
            frame_count=900,
            overall_score=85.5
        )
        db_session.add(analysis)
        db_session.commit()
        
        # Verify relationships
        saved_session = db_session.query(WorkoutSession).filter_by(id=session.id).first()
        assert len(saved_session.form_analyses) == 1
        assert saved_session.form_analyses[0].overall_score == 85.5

class TestNutritionOperations:
    """Test nutrition-related database operations"""
    
    def test_food_crud(self, db_session):
        """Test food CRUD operations"""
        # Create
        food = Food(
            name="テスト食品",
            name_en="Test Food",
            calories_per_100g=250,
            protein_g=20,
            carbs_g=30,
            fat_g=10,
            fiber_g=5
        )
        db_session.add(food)
        db_session.commit()
        
        # Read
        saved = db_session.query(Food).filter_by(name="テスト食品").first()
        assert saved is not None
        assert saved.calories_per_100g == 250
        
        # Update
        saved.calories_per_100g = 260
        db_session.commit()
        
        updated = db_session.query(Food).filter_by(id=saved.id).first()
        assert updated.calories_per_100g == 260
        
        # Delete
        db_session.delete(updated)
        db_session.commit()
        
        deleted = db_session.query(Food).filter_by(id=saved.id).first()
        assert deleted is None
    
    def test_meal_with_food_items(self, db_session, test_user):
        """Test meal creation with food items"""
        # Create foods
        rice = Food(name="Rice", calories_per_100g=156, protein_g=2.7, carbs_g=35.1, fat_g=0.3)
        chicken = Food(name="Chicken", calories_per_100g=165, protein_g=31, carbs_g=0, fat_g=3.6)
        db_session.add_all([rice, chicken])
        db_session.flush()
        
        # Create meal
        meal = MealEntry(
            user_id=test_user.id,
            meal_type="lunch",
            consumed_at=datetime.utcnow()
        )
        db_session.add(meal)
        db_session.flush()
        
        # Add food items
        meal_items = [
            MealFoodItem(meal_id=meal.id, food_id=rice.id, quantity=150, unit="g"),
            MealFoodItem(meal_id=meal.id, food_id=chicken.id, quantity=100, unit="g")
        ]
        db_session.add_all(meal_items)
        db_session.commit()
        
        # Verify
        saved_meal = db_session.query(MealEntry).filter_by(id=meal.id).first()
        assert len(saved_meal.food_items) == 2
        
        # Calculate total nutrition
        total_calories = sum(
            item.food.calories_per_100g * item.quantity / 100
            for item in saved_meal.food_items
        )
        assert total_calories == (156 * 1.5 + 165 * 1.0)

class TestProgressTracking:
    """Test progress tracking operations"""
    
    def test_goal_creation_and_progress(self, db_session, test_user):
        """Test goal creation and progress tracking"""
        # Create goal
        goal = Goal(
            user_id=test_user.id,
            goal_type="weight_loss",
            title="Lose 5kg",
            target_value=5.0,
            current_value=0.0,
            target_date=datetime.utcnow() + timedelta(days=90)
        )
        db_session.add(goal)
        db_session.commit()
        
        # Update progress
        goal.current_value = 2.5
        db_session.commit()
        
        # Verify
        saved = db_session.query(Goal).filter_by(id=goal.id).first()
        assert saved.current_value == 2.5
        assert saved.progress_percentage == 50.0
    
    def test_streak_tracking(self, db_session, test_user):
        """Test streak tracking"""
        streak = Streak(
            user_id=test_user.id,
            streak_type="workout",
            current_count=5,
            longest_count=10,
            last_activity_date=datetime.utcnow().date()
        )
        db_session.add(streak)
        db_session.commit()
        
        # Update streak
        streak.current_count += 1
        streak.last_activity_date = datetime.utcnow().date()
        db_session.commit()
        
        saved = db_session.query(Streak).filter_by(id=streak.id).first()
        assert saved.current_count == 6

class TestDatabaseTransactions:
    """Test database transaction handling"""
    
    def test_transaction_rollback(self, db_session):
        """Test transaction rollback on error"""
        user = User(
            id="rollback_test",
            email="rollback@test.com",
            display_name="Rollback Test"
        )
        db_session.add(user)
        
        try:
            # This should cause an error (duplicate email)
            duplicate = User(
                id="rollback_test_2",
                email="rollback@test.com",  # Same email
                display_name="Duplicate"
            )
            db_session.add(duplicate)
            db_session.commit()
        except Exception:
            db_session.rollback()
        
        # Verify no users were created
        count = db_session.query(User).filter(
            User.email == "rollback@test.com"
        ).count()
        assert count == 0
    
    def test_bulk_operations(self, db_session):
        """Test bulk insert and update operations"""
        # Bulk insert
        foods = [
            Food(name=f"Food {i}", calories_per_100g=100+i*10, protein_g=10+i, carbs_g=20+i, fat_g=5+i)
            for i in range(10)
        ]
        db_session.bulk_save_objects(foods)
        db_session.commit()
        
        # Verify
        count = db_session.query(Food).filter(Food.name.like("Food %")).count()
        assert count == 10
        
        # Bulk update
        db_session.query(Food).filter(Food.name.like("Food %")).update(
            {"fiber_g": 2.5},
            synchronize_session=False
        )
        db_session.commit()
        
        # Verify update
        updated = db_session.query(Food).filter(Food.name == "Food 0").first()
        assert updated.fiber_g == 2.5

class TestDatabasePerformance:
    """Test database performance and optimization"""
    
    def test_query_performance(self, db_session, test_user):
        """Test query performance with proper indexing"""
        import time
        
        # Create test data
        for i in range(100):
            measurement = UserBodyMeasurement(
                user_id=test_user.id,
                height_cm=175.0 + i * 0.1,
                measured_at=datetime.utcnow() - timedelta(days=i)
            )
            db_session.add(measurement)
        db_session.commit()
        
        # Test indexed query (user_id is indexed)
        start = time.time()
        results = db_session.query(UserBodyMeasurement).filter_by(
            user_id=test_user.id
        ).order_by(UserBodyMeasurement.measured_at.desc()).limit(10).all()
        query_time = time.time() - start
        
        assert len(results) == 10
        assert query_time < 0.1  # Should be fast with index
    
    def test_eager_loading(self, db_session, test_user):
        """Test eager loading to avoid N+1 queries"""
        from sqlalchemy.orm import joinedload
        
        # Create test data
        for i in range(5):
            session = WorkoutSession(
                user_id=test_user.id,
                name=f"Session {i}",
                total_exercises=1
            )
            db_session.add(session)
        db_session.commit()
        
        # Query with eager loading
        sessions = db_session.query(WorkoutSession).options(
            joinedload(WorkoutSession.user)
        ).filter_by(user_id=test_user.id).all()
        
        # Access related data without additional queries
        for session in sessions:
            assert session.user.email == test_user.email