"""
Progress Tracking and Analytics Models
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class ProgressSnapshot(Base):
    """Daily/weekly progress snapshots"""
    __tablename__ = "progress_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    
    # Snapshot type and period
    snapshot_type = Column(String, nullable=False)  # daily, weekly, monthly
    snapshot_date = Column(DateTime, nullable=False)
    
    # Physical measurements
    weight_kg = Column(Float, nullable=True)
    body_fat_percentage = Column(Float, nullable=True)
    muscle_mass_kg = Column(Float, nullable=True)
    
    # Performance metrics
    total_workouts = Column(Integer, default=0)
    total_workout_time = Column(Float, default=0.0)  # minutes
    average_form_score = Column(Float, nullable=True)
    
    # Strength metrics
    squat_1rm = Column(Float, nullable=True)
    bench_press_1rm = Column(Float, nullable=True)
    deadlift_1rm = Column(Float, nullable=True)
    total_powerlifting = Column(Float, nullable=True)
    
    # Volume metrics
    total_volume = Column(Float, nullable=True)  # kg lifted
    
    # Nutrition metrics
    average_calories = Column(Float, nullable=True)
    average_protein = Column(Float, nullable=True)
    nutrition_goal_adherence = Column(Float, nullable=True)  # percentage
    
    # Goals and achievements
    goals_achieved = Column(JSON, nullable=True)
    milestones_reached = Column(JSON, nullable=True)
    
    # Calculated fields
    calculated_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

class Goal(Base):
    """User goals and targets"""
    __tablename__ = "goals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    
    # Goal information
    goal_type = Column(String, nullable=False)  # weight_loss, strength, endurance, etc.
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Target values
    target_value = Column(Float, nullable=False)
    current_value = Column(Float, default=0.0)
    unit = Column(String, nullable=True)
    
    # Timeline
    start_date = Column(DateTime, nullable=False)
    target_date = Column(DateTime, nullable=False)
    completed_date = Column(DateTime, nullable=True)
    
    # Progress tracking
    progress_percentage = Column(Float, default=0.0)
    status = Column(String, default="active")  # active, paused, completed, cancelled
    
    # Priority and motivation
    priority = Column(String, default="medium")  # low, medium, high
    motivation_notes = Column(Text, nullable=True)
    
    # Tracking method
    tracking_method = Column(String, nullable=True)  # manual, automatic, hybrid
    tracking_frequency = Column(String, nullable=True)  # daily, weekly, monthly
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Achievement(Base):
    """User achievements and milestones"""
    __tablename__ = "achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    
    # Achievement information
    achievement_type = Column(String, nullable=False)  # milestone, streak, personal_record
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Achievement data
    value = Column(Float, nullable=True)
    unit = Column(String, nullable=True)
    category = Column(String, nullable=True)  # strength, endurance, consistency
    
    # Rarity and points
    rarity = Column(String, default="common")  # common, rare, epic, legendary
    points = Column(Integer, default=0)
    
    # Context
    workout_session_id = Column(String, nullable=True)
    exercise_id = Column(Integer, nullable=True)
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=True)
    
    # Timestamps
    achieved_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    goal = relationship("Goal")

class ProgressPhoto(Base):
    """Progress photos and body transformation tracking"""
    __tablename__ = "progress_photos"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    
    # Photo information
    photo_url = Column(String, nullable=False)
    photo_type = Column(String, nullable=False)  # front, side, back, specific_muscle
    
    # Measurements at time of photo
    weight_kg = Column(Float, nullable=True)
    body_fat_percentage = Column(Float, nullable=True)
    
    # Photo analysis (AI-generated)
    muscle_definition_score = Column(Float, nullable=True)
    posture_score = Column(Float, nullable=True)
    symmetry_score = Column(Float, nullable=True)
    
    # Context
    lighting_quality = Column(String, nullable=True)  # good, fair, poor
    photo_quality = Column(String, nullable=True)  # high, medium, low
    notes = Column(Text, nullable=True)
    
    # Privacy
    is_private = Column(Boolean, default=True)
    
    taken_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Streak(Base):
    """Activity streaks tracking"""
    __tablename__ = "streaks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    
    # Streak information
    streak_type = Column(String, nullable=False)  # workout, nutrition, water, sleep
    current_count = Column(Integer, default=0)
    best_count = Column(Integer, default=0)
    
    # Current streak period
    current_start_date = Column(DateTime, nullable=True)
    last_activity_date = Column(DateTime, nullable=True)
    
    # Best streak period
    best_start_date = Column(DateTime, nullable=True)
    best_end_date = Column(DateTime, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ProgressNote(Base):
    """User progress notes and reflections"""
    __tablename__ = "progress_notes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    
    # Note content
    title = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    note_type = Column(String, default="general")  # general, reflection, milestone
    
    # Associated data
    workout_session_id = Column(String, nullable=True)
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=True)
    
    # Mood and energy
    mood_rating = Column(Integer, nullable=True)  # 1-10 scale
    energy_level = Column(Integer, nullable=True)  # 1-10 scale
    motivation_level = Column(Integer, nullable=True)  # 1-10 scale
    
    # Tags for categorization
    tags = Column(JSON, nullable=True)
    
    # Privacy
    is_private = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    goal = relationship("Goal")

class AnalyticsEvent(Base):
    """User behavior analytics events"""
    __tablename__ = "analytics_events"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    
    # Event information
    event_type = Column(String, nullable=False)  # page_view, feature_use, goal_created
    event_name = Column(String, nullable=False)
    
    # Event properties
    properties = Column(JSON, nullable=True)
    
    # Session context
    session_id = Column(String, nullable=True)
    device_type = Column(String, nullable=True)
    
    # Timestamps
    event_timestamp = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ProgressReport(Base):
    """Generated progress reports"""
    __tablename__ = "progress_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    
    # Report information
    report_type = Column(String, nullable=False)  # weekly, monthly, quarterly
    report_period_start = Column(DateTime, nullable=False)
    report_period_end = Column(DateTime, nullable=False)
    
    # Report content
    summary = Column(Text, nullable=True)
    achievements = Column(JSON, nullable=True)
    improvements = Column(JSON, nullable=True)
    challenges = Column(JSON, nullable=True)
    recommendations = Column(JSON, nullable=True)
    
    # Metrics
    metrics = Column(JSON, nullable=False)
    
    # Report generation
    generated_by = Column(String, default="ai")  # ai, manual
    generation_version = Column(String, nullable=True)
    
    # Status
    is_read = Column(Boolean, default=False)
    
    generated_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)