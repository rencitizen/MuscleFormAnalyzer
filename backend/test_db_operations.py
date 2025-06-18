#!/usr/bin/env python
"""
Database operations test runner
Comprehensive database testing and validation
"""
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings
from app.database import engine, SessionLocal, Base, check_database_connection
from sqlalchemy import text, inspect
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_connection():
    """Test basic database connectivity"""
    print("\n🔍 Testing Database Connection...")
    
    if check_database_connection():
        print("✅ Database connection successful")
        
        # Get database info
        with engine.connect() as conn:
            if settings.DATABASE_URL.startswith("postgresql"):
                result = conn.execute(text("SELECT version()"))
                version = result.scalar()
                print(f"   Database: PostgreSQL")
                print(f"   Version: {version}")
            else:
                print(f"   Database: SQLite")
                print(f"   File: {settings.DATABASE_URL}")
    else:
        print("❌ Database connection failed")
        return False
    
    return True

def test_table_structure():
    """Test database table structure"""
    print("\n🔍 Testing Table Structure...")
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    expected_tables = [
        'users', 'user_profiles', 'user_settings', 'user_sessions',
        'user_body_measurements', 'exercises', 'workout_sessions',
        'form_analyses', 'workout_records', 'personal_records',
        'training_programs', 'meal_entries', 'meal_food_items',
        'foods', 'nutrition_goals', 'goals', 'achievements',
        'streaks', 'progress_snapshots'
    ]
    
    print(f"   Found {len(tables)} tables")
    
    missing_tables = []
    for table in expected_tables:
        if table not in tables:
            missing_tables.append(table)
            print(f"   ❌ Missing table: {table}")
        else:
            # Get column count
            columns = inspector.get_columns(table)
            print(f"   ✅ {table} ({len(columns)} columns)")
    
    if missing_tables:
        print(f"\n   ⚠️  Missing {len(missing_tables)} tables")
        return False
    
    return True

def test_crud_operations():
    """Test basic CRUD operations"""
    print("\n🔍 Testing CRUD Operations...")
    
    from models.user import User
    from models.workout import Exercise
    from models.nutrition import Food
    
    db = SessionLocal()
    
    try:
        # Test CREATE
        print("   Testing CREATE...")
        test_user = User(
            id="crud_test_user",
            email="crud_test@example.com",
            display_name="CRUD Test User"
        )
        db.add(test_user)
        db.commit()
        print("   ✅ User created")
        
        # Test READ
        print("   Testing READ...")
        user = db.query(User).filter_by(id="crud_test_user").first()
        assert user is not None
        assert user.email == "crud_test@example.com"
        print("   ✅ User read")
        
        # Test UPDATE
        print("   Testing UPDATE...")
        user.display_name = "Updated CRUD User"
        db.commit()
        
        updated = db.query(User).filter_by(id="crud_test_user").first()
        assert updated.display_name == "Updated CRUD User"
        print("   ✅ User updated")
        
        # Test DELETE
        print("   Testing DELETE...")
        db.delete(user)
        db.commit()
        
        deleted = db.query(User).filter_by(id="crud_test_user").first()
        assert deleted is None
        print("   ✅ User deleted")
        
        return True
        
    except Exception as e:
        print(f"   ❌ CRUD test failed: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def test_relationships():
    """Test database relationships"""
    print("\n🔍 Testing Relationships...")
    
    from models.user import User, UserProfile
    from models.workout import Exercise, WorkoutSession, FormAnalysis
    
    db = SessionLocal()
    
    try:
        # Create user with profile
        user = User(
            id="rel_test_user",
            email="relationship@test.com",
            display_name="Relationship Test"
        )
        db.add(user)
        db.flush()
        
        profile = UserProfile(
            user_id=user.id,
            bio="Test bio",
            preferred_language="en"
        )
        db.add(profile)
        db.commit()
        
        # Test relationship loading
        loaded_user = db.query(User).filter_by(id="rel_test_user").first()
        assert loaded_user.profile is not None
        assert loaded_user.profile.bio == "Test bio"
        print("   ✅ One-to-One relationship (User -> Profile)")
        
        # Create exercise and workout session
        exercise = Exercise(
            name="Relationship Test Exercise",
            category="test",
            muscle_groups=["test"]
        )
        db.add(exercise)
        db.flush()
        
        session = WorkoutSession(
            user_id=user.id,
            name="Test Session",
            total_exercises=1
        )
        db.add(session)
        db.flush()
        
        analysis = FormAnalysis(
            user_id=user.id,
            exercise_id=exercise.id,
            workout_session_id=session.id,
            overall_score=90.0
        )
        db.add(analysis)
        db.commit()
        
        # Test many-to-one relationships
        loaded_analysis = db.query(FormAnalysis).filter_by(
            workout_session_id=session.id
        ).first()
        assert loaded_analysis.workout_session is not None
        assert loaded_analysis.exercise is not None
        print("   ✅ Many-to-One relationships (Analysis -> Session, Exercise)")
        
        # Cleanup
        db.query(FormAnalysis).filter_by(user_id=user.id).delete()
        db.query(WorkoutSession).filter_by(user_id=user.id).delete()
        db.query(UserProfile).filter_by(user_id=user.id).delete()
        db.query(User).filter_by(id=user.id).delete()
        db.query(Exercise).filter_by(name="Relationship Test Exercise").delete()
        db.commit()
        
        return True
        
    except Exception as e:
        print(f"   ❌ Relationship test failed: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def test_constraints():
    """Test database constraints"""
    print("\n🔍 Testing Constraints...")
    
    from models.user import User
    from sqlalchemy.exc import IntegrityError
    
    db = SessionLocal()
    
    try:
        # Test unique constraint
        user1 = User(
            id="constraint_test_1",
            email="unique@test.com",
            display_name="User 1"
        )
        db.add(user1)
        db.commit()
        
        # Try to create duplicate email
        user2 = User(
            id="constraint_test_2",
            email="unique@test.com",  # Same email
            display_name="User 2"
        )
        db.add(user2)
        
        try:
            db.commit()
            print("   ❌ Unique constraint not working")
            return False
        except IntegrityError:
            db.rollback()
            print("   ✅ Unique constraint on email working")
        
        # Cleanup
        db.query(User).filter_by(email="unique@test.com").delete()
        db.commit()
        
        return True
        
    except Exception as e:
        print(f"   ❌ Constraint test failed: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def test_performance():
    """Test database performance"""
    print("\n🔍 Testing Performance...")
    
    from models.user import User, UserBodyMeasurement
    from datetime import datetime, timedelta
    import time
    
    db = SessionLocal()
    
    try:
        # Create test user
        user = User(
            id="perf_test_user",
            email="performance@test.com",
            display_name="Performance Test"
        )
        db.add(user)
        db.commit()
        
        # Bulk insert test
        print("   Testing bulk insert...")
        start = time.time()
        
        measurements = []
        for i in range(1000):
            m = UserBodyMeasurement(
                user_id=user.id,
                height_cm=175.0 + (i % 10) * 0.1,
                measured_at=datetime.utcnow() - timedelta(days=i)
            )
            measurements.append(m)
        
        db.bulk_save_objects(measurements)
        db.commit()
        
        insert_time = time.time() - start
        print(f"   ✅ Inserted 1000 records in {insert_time:.2f}s")
        
        # Query performance test
        print("   Testing query performance...")
        start = time.time()
        
        results = db.query(UserBodyMeasurement).filter_by(
            user_id=user.id
        ).order_by(UserBodyMeasurement.measured_at.desc()).limit(100).all()
        
        query_time = time.time() - start
        print(f"   ✅ Queried 100 records in {query_time:.3f}s")
        
        # Cleanup
        db.query(UserBodyMeasurement).filter_by(user_id=user.id).delete()
        db.query(User).filter_by(id=user.id).delete()
        db.commit()
        
        return insert_time < 5.0 and query_time < 0.5
        
    except Exception as e:
        print(f"   ❌ Performance test failed: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def run_all_tests():
    """Run all database tests"""
    print("=" * 50)
    print("Running Database Tests")
    print("=" * 50)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Table Structure", test_table_structure),
        ("CRUD Operations", test_crud_operations),
        ("Relationships", test_relationships),
        ("Constraints", test_constraints),
        ("Performance", test_performance)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<30} {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return all(results.values())

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database operations test")
    parser.add_argument("--test", choices=[
        "connection", "structure", "crud", "relationships", 
        "constraints", "performance", "all"
    ], default="all", help="Specific test to run")
    
    args = parser.parse_args()
    
    if args.test == "all":
        success = run_all_tests()
    else:
        test_map = {
            "connection": test_database_connection,
            "structure": test_table_structure,
            "crud": test_crud_operations,
            "relationships": test_relationships,
            "constraints": test_constraints,
            "performance": test_performance
        }
        success = test_map[args.test]()
    
    sys.exit(0 if success else 1)