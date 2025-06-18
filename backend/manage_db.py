#!/usr/bin/env python
"""
Database management script
Handles migrations, initialization, and maintenance
"""
import os
import sys
import argparse
import subprocess
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings
from app.database import engine, Base

def init_alembic():
    """Initialize Alembic if not already initialized"""
    if not os.path.exists("migrations"):
        print("Initializing Alembic...")
        subprocess.run(["alembic", "init", "migrations"], check=True)
        print("✅ Alembic initialized")
    else:
        print("ℹ️  Alembic already initialized")

def create_migration(message):
    """Create a new migration"""
    if not message:
        print("❌ Please provide a migration message")
        sys.exit(1)
    
    print(f"Creating migration: {message}")
    result = subprocess.run(
        ["alembic", "revision", "--autogenerate", "-m", message],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Migration created successfully")
        print(result.stdout)
    else:
        print("❌ Failed to create migration")
        print(result.stderr)
        sys.exit(1)

def run_migrations():
    """Run pending migrations"""
    print("Running migrations...")
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Migrations completed successfully")
        print(result.stdout)
    else:
        print("❌ Migration failed")
        print(result.stderr)
        sys.exit(1)

def downgrade_migration(revision=""):
    """Downgrade database to a previous revision"""
    target = revision if revision else "-1"
    print(f"Downgrading to revision: {target}")
    
    result = subprocess.run(
        ["alembic", "downgrade", target],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Downgrade completed successfully")
        print(result.stdout)
    else:
        print("❌ Downgrade failed")
        print(result.stderr)
        sys.exit(1)

def show_history():
    """Show migration history"""
    print("Migration history:")
    subprocess.run(["alembic", "history", "--verbose"])

def show_current():
    """Show current database revision"""
    print("Current database revision:")
    subprocess.run(["alembic", "current"])

def create_tables():
    """Create all tables without migrations (for development)"""
    print("Creating all tables...")
    
    # Import all models to ensure they're registered
    from models.user import User, UserProfile, UserSettings, UserSession, UserBodyMeasurement
    from models.workout import Exercise, WorkoutSession, FormAnalysis, WorkoutRecord, PersonalRecord, TrainingProgram
    from models.nutrition import MealEntry, MealFoodItem, Food, NutritionGoal
    from models.progress import ProgressSnapshot, Goal, Achievement, Streak
    
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created successfully")

def drop_tables():
    """Drop all tables (DANGEROUS!)"""
    response = input("⚠️  This will DELETE ALL DATA. Are you sure? (yes/no): ")
    if response.lower() != "yes":
        print("Operation cancelled")
        return
    
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("✅ All tables dropped")

def main():
    parser = argparse.ArgumentParser(description="Database management tool")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Init command
    subparsers.add_parser("init", help="Initialize Alembic")
    
    # Create migration command
    create_parser = subparsers.add_parser("create", help="Create a new migration")
    create_parser.add_argument("message", help="Migration message")
    
    # Migrate command
    subparsers.add_parser("migrate", help="Run pending migrations")
    
    # Downgrade command
    downgrade_parser = subparsers.add_parser("downgrade", help="Downgrade database")
    downgrade_parser.add_argument("revision", nargs="?", default="", help="Target revision")
    
    # History command
    subparsers.add_parser("history", help="Show migration history")
    
    # Current command
    subparsers.add_parser("current", help="Show current revision")
    
    # Create tables command
    subparsers.add_parser("create-tables", help="Create all tables (dev only)")
    
    # Drop tables command
    subparsers.add_parser("drop-tables", help="Drop all tables (DANGEROUS!)")
    
    args = parser.parse_args()
    
    # Set DATABASE_URL for Alembic
    if settings.DATABASE_URL:
        os.environ["DATABASE_URL"] = settings.DATABASE_URL
    
    if args.command == "init":
        init_alembic()
    elif args.command == "create":
        create_migration(args.message)
    elif args.command == "migrate":
        run_migrations()
    elif args.command == "downgrade":
        downgrade_migration(args.revision)
    elif args.command == "history":
        show_history()
    elif args.command == "current":
        show_current()
    elif args.command == "create-tables":
        create_tables()
    elif args.command == "drop-tables":
        drop_tables()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()