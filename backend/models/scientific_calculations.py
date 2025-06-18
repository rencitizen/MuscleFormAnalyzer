"""
Scientific Calculations Database Models for TENAX FIT v3.0
"""
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, JSON, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class UserScientificProfile(Base):
    """User's scientific profile for calculations"""
    __tablename__ = "user_scientific_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Basic measurements
    weight = Column(Float, nullable=False)  # kg
    height = Column(Float, nullable=False)  # cm
    age = Column(Integer, nullable=False)
    gender = Column(String(10), nullable=False)  # male/female
    
    # Activity and goals
    activity_level = Column(String(20), nullable=False)  # sedentary/light/moderate/active/very_active
    goal = Column(String(20), nullable=False)  # muscle_gain/fat_loss/maintenance
    experience_level = Column(String(20), default="intermediate")  # beginner/intermediate/advanced
    
    # Optional measurements
    target_body_fat = Column(Float, nullable=True)
    waist_cm = Column(Float, nullable=True)
    neck_cm = Column(Float, nullable=True)
    hip_cm = Column(Float, nullable=True)  # For females
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="scientific_profile")
    calculation_history = relationship("CalculationHistory", back_populates="profile", cascade="all, delete-orphan")
    nutrition_recommendations = relationship("NutritionRecommendation", back_populates="profile", cascade="all, delete-orphan")


class CalculationHistory(Base):
    """History of all calculations performed for a user"""
    __tablename__ = "calculation_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    profile_id = Column(Integer, ForeignKey("user_scientific_profiles.id"), nullable=False)
    
    # Calculation results
    bmr = Column(Float, nullable=False)  # Basal Metabolic Rate
    tdee = Column(Float, nullable=False)  # Total Daily Energy Expenditure
    body_fat_percentage = Column(Float, nullable=True)
    lean_body_mass = Column(Float, nullable=True)
    target_calories = Column(Float, nullable=False)
    
    # Additional metrics
    bmi = Column(Float, nullable=True)
    ffmi = Column(Float, nullable=True)  # Fat-Free Mass Index
    
    # Context
    calculation_type = Column(String(50), default="comprehensive")
    notes = Column(Text, nullable=True)
    
    # Timestamp
    calculated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    profile = relationship("UserScientificProfile", back_populates="calculation_history")
    user = relationship("User", back_populates="calculation_history")


class NutritionRecommendation(Base):
    """Nutrition recommendations based on calculations"""
    __tablename__ = "nutrition_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    profile_id = Column(Integer, ForeignKey("user_scientific_profiles.id"), nullable=False)
    
    # Macronutrients (grams)
    protein_grams = Column(Float, nullable=False)
    carbs_grams = Column(Float, nullable=False)
    fats_grams = Column(Float, nullable=False)
    
    # Calories
    protein_calories = Column(Float, nullable=False)
    carbs_calories = Column(Float, nullable=False)
    fats_calories = Column(Float, nullable=False)
    total_calories = Column(Float, nullable=False)
    
    # Percentages
    protein_percentage = Column(Float, nullable=False)
    carbs_percentage = Column(Float, nullable=False)
    fats_percentage = Column(Float, nullable=False)
    
    # Micronutrients (JSON format)
    micronutrients = Column(JSON, nullable=True)
    
    # Hydration
    water_liters = Column(Float, default=3.0)
    
    # Meal timing suggestions
    meal_timing = Column(JSON, nullable=True)
    
    # Valid until
    valid_from = Column(DateTime, default=datetime.utcnow)
    valid_until = Column(DateTime, nullable=True)
    
    # Relationships
    profile = relationship("UserScientificProfile", back_populates="nutrition_recommendations")
    user = relationship("User", back_populates="nutrition_recommendations")


class SafetyWarning(Base):
    """Safety warnings and health checks"""
    __tablename__ = "safety_warnings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Warning details
    warning_type = Column(String(50), nullable=False)  # calorie_restriction/body_fat_goal/overtraining
    severity = Column(String(20), nullable=False)  # low/medium/high/critical
    message = Column(Text, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime, nullable=True)
    
    # Recommendations
    recommendations = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="safety_warnings")


class TrainingProgramRecommendation(Base):
    """AI-generated training program recommendations"""
    __tablename__ = "training_program_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Program details
    program_name = Column(String(100), nullable=False)
    program_type = Column(String(50), nullable=False)  # strength/hypertrophy/endurance/mixed
    duration_weeks = Column(Integer, nullable=False)
    frequency_per_week = Column(Integer, nullable=False)
    
    # Program structure (JSON)
    weekly_schedule = Column(JSON, nullable=False)
    exercises = Column(JSON, nullable=False)
    progression_scheme = Column(JSON, nullable=True)
    
    # Customization
    equipment_required = Column(JSON, nullable=True)
    difficulty_level = Column(String(20), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    starts_at = Column(DateTime, nullable=True)
    ends_at = Column(DateTime, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=False)
    completion_percentage = Column(Float, default=0.0)
    
    # Relationships
    user = relationship("User", back_populates="training_programs")


class SupplementRecommendation(Base):
    """Supplement recommendations based on goals and calculations"""
    __tablename__ = "supplement_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Supplement details
    supplement_name = Column(String(100), nullable=False)
    supplement_type = Column(String(50), nullable=False)  # protein/creatine/vitamins/minerals
    
    # Dosage
    recommended_dose = Column(String(100), nullable=False)
    timing = Column(String(200), nullable=False)  # When to take
    frequency = Column(String(50), nullable=False)  # Daily/weekly
    
    # Reasoning
    reason = Column(Text, nullable=False)
    scientific_backing = Column(Text, nullable=True)
    
    # Priority
    priority = Column(String(20), default="medium")  # low/medium/high
    
    # Status
    is_active = Column(Boolean, default=True)
    user_accepted = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    valid_until = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="supplement_recommendations")