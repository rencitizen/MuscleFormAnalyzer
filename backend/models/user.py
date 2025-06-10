"""
User and Authentication Models
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)  # Firebase UID
    email = Column(String, unique=True, index=True, nullable=False)
    display_name = Column(String, nullable=True)
    
    # Profile information
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    gender = Column(String, nullable=True)  # male, female, other
    
    # Physical measurements
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    height_measure_method = Column(String, default="manual")  # manual, video
    
    # Fitness profile
    fitness_level = Column(String, nullable=True)  # beginner, intermediate, advanced
    fitness_goals = Column(JSON, nullable=True)  # list of goals
    training_experience_years = Column(Float, nullable=True)
    
    # Preferences
    preferred_units = Column(String, default="metric")  # metric, imperial
    language = Column(String, default="ja")
    timezone = Column(String, default="Asia/Tokyo")
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

class UserProfile(Base):
    """Extended user profile information"""
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    
    # Detailed physical information
    body_fat_percentage = Column(Float, nullable=True)
    muscle_mass_kg = Column(Float, nullable=True)
    
    # Health information
    medical_conditions = Column(JSON, nullable=True)
    medications = Column(JSON, nullable=True)
    allergies = Column(JSON, nullable=True)
    injuries_history = Column(JSON, nullable=True)
    
    # Training preferences
    preferred_workout_duration = Column(Integer, nullable=True)  # minutes
    preferred_workout_frequency = Column(Integer, nullable=True)  # times per week
    available_equipment = Column(JSON, nullable=True)
    gym_membership = Column(Boolean, default=False)
    
    # Nutrition preferences
    dietary_restrictions = Column(JSON, nullable=True)
    nutrition_goals = Column(JSON, nullable=True)
    target_calories = Column(Integer, nullable=True)
    target_protein = Column(Float, nullable=True)
    target_carbs = Column(Float, nullable=True)
    target_fat = Column(Float, nullable=True)
    
    # Privacy settings
    profile_visibility = Column(String, default="private")  # public, friends, private
    data_sharing_consent = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserSettings(Base):
    """User application settings"""
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    
    # Notification preferences
    email_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)
    workout_reminders = Column(Boolean, default=True)
    progress_updates = Column(Boolean, default=True)
    
    # App preferences
    dark_mode = Column(Boolean, default=False)
    auto_sync = Column(Boolean, default=True)
    offline_mode = Column(Boolean, default=False)
    
    # Form analysis settings
    real_time_feedback = Column(Boolean, default=True)
    voice_feedback = Column(Boolean, default=False)
    form_analysis_sensitivity = Column(String, default="medium")  # low, medium, high
    
    # Data management
    data_retention_days = Column(Integer, default=365)
    auto_backup = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserSession(Base):
    """User session tracking"""
    __tablename__ = "user_sessions"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    
    # Session information
    device_type = Column(String, nullable=True)  # mobile, desktop, tablet
    device_id = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Session status
    is_active = Column(Boolean, default=True)
    login_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    logout_at = Column(DateTime, nullable=True)
    
    # Location (optional)
    country = Column(String, nullable=True)
    city = Column(String, nullable=True)

class UserBodyMeasurement(Base):
    """Body measurement tracking"""
    __tablename__ = "user_body_measurements"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    
    # Measurements
    weight_kg = Column(Float, nullable=True)
    height_cm = Column(Float, nullable=True)
    body_fat_percentage = Column(Float, nullable=True)
    muscle_mass_kg = Column(Float, nullable=True)
    
    # Circumference measurements
    chest_cm = Column(Float, nullable=True)
    waist_cm = Column(Float, nullable=True)
    hip_cm = Column(Float, nullable=True)
    thigh_cm = Column(Float, nullable=True)
    arm_cm = Column(Float, nullable=True)
    neck_cm = Column(Float, nullable=True)
    
    # Measurement context
    measurement_method = Column(String, nullable=True)  # manual, video, scale
    measurement_notes = Column(Text, nullable=True)
    measured_by = Column(String, nullable=True)  # self, trainer, ai
    
    # Timestamps
    measured_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)