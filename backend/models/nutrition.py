"""
Nutrition and Food Database Models
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Food(Base):
    """Food database model"""
    __tablename__ = "foods"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    name_en = Column(String, nullable=True)
    name_ja = Column(String, nullable=True)
    
    # Food categorization
    category = Column(String, nullable=True)  # protein, carbs, fat, vegetable, etc.
    subcategory = Column(String, nullable=True)
    brand = Column(String, nullable=True)
    
    # Nutritional information (per 100g)
    calories_per_100g = Column(Float, nullable=False)
    protein_g = Column(Float, nullable=True)
    carbs_g = Column(Float, nullable=True)
    fat_g = Column(Float, nullable=True)
    fiber_g = Column(Float, nullable=True)
    sugar_g = Column(Float, nullable=True)
    sodium_mg = Column(Float, nullable=True)
    
    # Micronutrients
    micronutrients = Column(JSON, nullable=True)  # vitamins and minerals
    
    # Alternative serving sizes
    serving_sizes = Column(JSON, nullable=True)
    
    # Food recognition
    barcode = Column(String, nullable=True, index=True)
    image_recognition_tags = Column(JSON, nullable=True)
    
    # Metadata
    source = Column(String, nullable=True)  # USDA, manual, user
    verified = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MealEntry(Base):
    """User meal entry model"""
    __tablename__ = "meal_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    
    # Meal information
    meal_type = Column(String, nullable=False)  # breakfast, lunch, dinner, snack
    meal_name = Column(String, nullable=True)
    
    # Timing
    consumed_at = Column(DateTime, nullable=False)
    
    # Photo and recognition
    photo_url = Column(String, nullable=True)
    recognition_confidence = Column(Float, nullable=True)
    manual_entry = Column(Boolean, default=False)
    
    # Calculated totals
    total_calories = Column(Float, nullable=True)
    total_protein = Column(Float, nullable=True)
    total_carbs = Column(Float, nullable=True)
    total_fat = Column(Float, nullable=True)
    total_fiber = Column(Float, nullable=True)
    
    # Context
    notes = Column(Text, nullable=True)
    location = Column(String, nullable=True)
    mood_before = Column(String, nullable=True)
    mood_after = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to food items
    food_items = relationship("MealFoodItem", back_populates="meal")

class MealFoodItem(Base):
    """Individual food item in a meal"""
    __tablename__ = "meal_food_items"
    
    id = Column(Integer, primary_key=True, index=True)
    meal_id = Column(Integer, ForeignKey("meal_entries.id"), nullable=False)
    food_id = Column(Integer, ForeignKey("foods.id"), nullable=False)
    
    # Quantity information
    quantity = Column(Float, nullable=False)
    unit = Column(String, nullable=False)  # g, ml, piece, cup, etc.
    
    # Calculated nutrition for this portion
    calories = Column(Float, nullable=True)
    protein = Column(Float, nullable=True)
    carbs = Column(Float, nullable=True)
    fat = Column(Float, nullable=True)
    
    # Recognition details
    confidence = Column(Float, nullable=True)
    bounding_box = Column(JSON, nullable=True)  # if from image recognition
    
    # Relationships
    meal = relationship("MealEntry", back_populates="food_items")
    food = relationship("Food")

class NutritionGoal(Base):
    """User nutrition goals"""
    __tablename__ = "nutrition_goals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    
    # Goals
    goal_type = Column(String, nullable=False)  # daily, weekly, monthly
    target_calories = Column(Float, nullable=True)
    target_protein = Column(Float, nullable=True)
    target_carbs = Column(Float, nullable=True)
    target_fat = Column(Float, nullable=True)
    target_fiber = Column(Float, nullable=True)
    
    # Macronutrient ratios
    protein_percentage = Column(Float, nullable=True)
    carb_percentage = Column(Float, nullable=True)
    fat_percentage = Column(Float, nullable=True)
    
    # Weight goals
    target_weight_kg = Column(Float, nullable=True)
    weight_change_rate = Column(Float, nullable=True)  # kg per week
    
    # Activity level
    activity_level = Column(String, nullable=True)  # sedentary, light, moderate, very_active
    
    # Goal period
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class NutritionInsight(Base):
    """AI-generated nutrition insights"""
    __tablename__ = "nutrition_insights"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    
    # Insight information
    insight_type = Column(String, nullable=False)  # trend, recommendation, warning
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    
    # Data period
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Supporting data
    supporting_data = Column(JSON, nullable=True)
    confidence_score = Column(Float, nullable=True)
    
    # Status
    is_read = Column(Boolean, default=False)
    is_dismissed = Column(Boolean, default=False)
    priority = Column(String, default="medium")  # low, medium, high
    
    created_at = Column(DateTime, default=datetime.utcnow)

class Recipe(Base):
    """Recipe database model"""
    __tablename__ = "recipes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    creator_id = Column(String, nullable=True)  # user who created it
    
    # Recipe details
    servings = Column(Integer, nullable=False)
    prep_time_minutes = Column(Integer, nullable=True)
    cook_time_minutes = Column(Integer, nullable=True)
    difficulty = Column(String, nullable=True)  # easy, medium, hard
    
    # Instructions
    ingredients = Column(JSON, nullable=False)  # list of ingredients with quantities
    instructions = Column(JSON, nullable=False)  # list of steps
    
    # Nutrition (calculated from ingredients)
    calories_per_serving = Column(Float, nullable=True)
    protein_per_serving = Column(Float, nullable=True)
    carbs_per_serving = Column(Float, nullable=True)
    fat_per_serving = Column(Float, nullable=True)
    
    # Categorization
    cuisine_type = Column(String, nullable=True)
    meal_type = Column(JSON, nullable=True)  # breakfast, lunch, dinner
    dietary_tags = Column(JSON, nullable=True)  # vegetarian, vegan, keto, etc.
    
    # Media
    image_url = Column(String, nullable=True)
    video_url = Column(String, nullable=True)
    
    # Metadata
    is_public = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserFavoriteFood(Base):
    """User's favorite foods"""
    __tablename__ = "user_favorite_foods"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    food_id = Column(Integer, ForeignKey("foods.id"), nullable=False)
    
    # Customization
    custom_name = Column(String, nullable=True)
    custom_serving_size = Column(Float, nullable=True)
    custom_unit = Column(String, nullable=True)
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    last_used = Column(DateTime, nullable=True)
    
    added_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    food = relationship("Food")

class WaterIntake(Base):
    """Water intake tracking"""
    __tablename__ = "water_intake"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    
    # Intake data
    amount_ml = Column(Float, nullable=False)
    drink_type = Column(String, default="water")  # water, tea, coffee, etc.
    
    # Timing
    consumed_at = Column(DateTime, nullable=False)
    
    # Context
    activity_type = Column(String, nullable=True)  # workout, meal, general
    temperature = Column(String, nullable=True)  # cold, room, hot
    
    created_at = Column(DateTime, default=datetime.utcnow)