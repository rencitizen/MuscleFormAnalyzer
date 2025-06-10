"""
Workout and Form Analysis Database Models
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class WorkoutSession(Base):
    """Workout session model"""
    __tablename__ = "workout_sessions"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    exercise_type = Column(String, nullable=False)
    status = Column(String, default="active")  # active, completed, cancelled
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationship to form analyses
    form_analyses = relationship("FormAnalysis", back_populates="session")

class FormAnalysis(Base):
    """Form analysis results model"""
    __tablename__ = "form_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("workout_sessions.id"), nullable=False)
    user_id = Column(String, nullable=False, index=True)
    exercise_type = Column(String, nullable=False)
    
    # Analysis results
    score = Column(Float, nullable=False)
    angle_scores = Column(JSON, nullable=True)
    phase = Column(String, nullable=True)
    feedback = Column(JSON, nullable=True)
    confidence = Column(Float, nullable=False)
    biomechanics = Column(JSON, nullable=True)
    
    # Metadata
    analyzer_type = Column(String, default="mediapipe")
    processing_time = Column(Float, nullable=True)
    is_video_analysis = Column(Boolean, default=False)
    video_metadata = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to session
    session = relationship("WorkoutSession", back_populates="form_analyses")

class Exercise(Base):
    """Exercise database model"""
    __tablename__ = "exercises"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)  # strength, cardio, flexibility
    muscle_groups = Column(JSON, nullable=True)  # list of muscle groups
    equipment = Column(String, nullable=True)
    difficulty_level = Column(String, nullable=True)  # beginner, intermediate, advanced
    instructions = Column(Text, nullable=True)
    tips = Column(JSON, nullable=True)  # list of tips
    common_mistakes = Column(JSON, nullable=True)  # list of common mistakes
    
    # Analysis configuration
    supports_form_analysis = Column(Boolean, default=False)
    analysis_config = Column(JSON, nullable=True)  # MediaPipe configuration
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class WorkoutRecord(Base):
    """Individual workout record model"""
    __tablename__ = "workout_records"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("workout_sessions.id"), nullable=False)
    user_id = Column(String, nullable=False, index=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    
    # Set data
    sets = Column(Integer, nullable=False)
    reps = Column(JSON, nullable=True)  # list of reps per set
    weight = Column(JSON, nullable=True)  # list of weights per set
    rest_time = Column(JSON, nullable=True)  # list of rest times
    
    # Performance metrics
    total_volume = Column(Float, nullable=True)  # sets * reps * weight
    estimated_1rm = Column(Float, nullable=True)
    rpe = Column(JSON, nullable=True)  # rate of perceived exertion per set
    
    # Form analysis summary
    form_score = Column(Float, nullable=True)
    form_feedback = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("WorkoutSession")
    exercise = relationship("Exercise")

class PersonalRecord(Base):
    """Personal record tracking model"""
    __tablename__ = "personal_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    
    # Record data
    record_type = Column(String, nullable=False)  # 1rm, max_reps, max_volume, best_form
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=True)  # kg, lbs, reps, %
    
    # Context
    workout_record_id = Column(Integer, ForeignKey("workout_records.id"), nullable=True)
    notes = Column(Text, nullable=True)
    
    achieved_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    exercise = relationship("Exercise")
    workout_record = relationship("WorkoutRecord")

class TrainingProgram(Base):
    """Training program model"""
    __tablename__ = "training_programs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    creator_id = Column(String, nullable=True)  # user who created it
    
    # Program configuration
    duration_weeks = Column(Integer, nullable=True)
    difficulty_level = Column(String, nullable=True)
    goal = Column(String, nullable=True)  # strength, hypertrophy, endurance
    
    # Program structure
    program_structure = Column(JSON, nullable=False)  # detailed program layout
    exercises = Column(JSON, nullable=True)  # list of exercise IDs
    
    # Metadata
    is_public = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserTrainingProgram(Base):
    """User's assigned training program"""
    __tablename__ = "user_training_programs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    program_id = Column(Integer, ForeignKey("training_programs.id"), nullable=False)
    
    # Progress tracking
    current_week = Column(Integer, default=1)
    current_day = Column(Integer, default=1)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Customizations
    custom_modifications = Column(JSON, nullable=True)
    progress_notes = Column(Text, nullable=True)
    
    status = Column(String, default="active")  # active, paused, completed
    
    # Relationships
    program = relationship("TrainingProgram")