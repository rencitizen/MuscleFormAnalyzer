"""
Nutrition Management API Endpoints
Food recognition and nutrition tracking
"""
import logging
import tempfile
import os
from typing import Optional, List
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Query
from pydantic import BaseModel
from datetime import datetime, date
import cv2
import numpy as np

from ..database import get_db
from ..models.user import User
from ..models.nutrition import MealEntry, MealFoodItem, Food, NutritionGoal
from ..api.auth import get_current_user
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter()

# Request/Response Models
class FoodItem(BaseModel):
    food_id: int
    quantity: float
    unit: str

class MealRequest(BaseModel):
    meal_type: str  # breakfast, lunch, dinner, snack
    food_items: List[FoodItem]
    consumed_at: Optional[datetime] = None
    notes: Optional[str] = None

class FoodRecognitionResponse(BaseModel):
    success: bool
    recognized_foods: List[dict] = []
    confidence: Optional[float] = None
    processing_time: Optional[float] = None
    error: Optional[str] = None

class NutritionSummaryResponse(BaseModel):
    date: str
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    total_fiber: float
    meals: List[dict]
    goals: Optional[dict] = None

@router.post("/recognize", response_model=FoodRecognitionResponse)
async def recognize_food_from_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Recognize food items from uploaded image
    """
    import time
    start_time = time.time()
    
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="File must be an image"
            )
        
        # Read image data
        image_data = await file.read()
        
        # Convert to OpenCV format
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(
                status_code=400,
                detail="Could not decode image"
            )
        
        # Perform food recognition
        recognition_result = await analyze_food_image(image)
        
        processing_time = time.time() - start_time
        
        return FoodRecognitionResponse(
            success=recognition_result.get("success", False),
            recognized_foods=recognition_result.get("foods", []),
            confidence=recognition_result.get("confidence"),
            processing_time=processing_time,
            error=recognition_result.get("error")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Food recognition error: {e}")
        return FoodRecognitionResponse(
            success=False,
            error=str(e),
            processing_time=time.time() - start_time
        )

@router.post("/meals")
async def add_meal_entry(
    meal_data: MealRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a new meal entry
    """
    try:
        # Create meal entry
        meal = MealEntry(
            user_id=current_user.id,
            meal_type=meal_data.meal_type,
            consumed_at=meal_data.consumed_at or datetime.utcnow(),
            notes=meal_data.notes,
            manual_entry=True
        )
        
        db.add(meal)
        db.flush()  # Get the meal ID
        
        # Add food items
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        
        for item in meal_data.food_items:
            # Get food information
            food = db.query(Food).filter(Food.id == item.food_id).first()
            if not food:
                raise HTTPException(
                    status_code=404,
                    detail=f"Food with ID {item.food_id} not found"
                )
            
            # Calculate nutrition for this portion
            portion_factor = item.quantity / 100  # Assuming base nutrition is per 100g
            
            calories = food.calories_per_100g * portion_factor
            protein = (food.protein_g or 0) * portion_factor
            carbs = (food.carbs_g or 0) * portion_factor
            fat = (food.fat_g or 0) * portion_factor
            
            # Create meal food item
            meal_food_item = MealFoodItem(
                meal_id=meal.id,
                food_id=item.food_id,
                quantity=item.quantity,
                unit=item.unit,
                calories=calories,
                protein=protein,
                carbs=carbs,
                fat=fat
            )
            
            db.add(meal_food_item)
            
            # Add to meal totals
            total_calories += calories
            total_protein += protein
            total_carbs += carbs
            total_fat += fat
        
        # Update meal totals
        meal.total_calories = total_calories
        meal.total_protein = total_protein
        meal.total_carbs = total_carbs
        meal.total_fat = total_fat
        
        db.commit()
        db.refresh(meal)
        
        return {
            "success": True,
            "meal": {
                "id": meal.id,
                "meal_type": meal.meal_type,
                "consumed_at": meal.consumed_at.isoformat(),
                "total_calories": meal.total_calories,
                "total_protein": meal.total_protein,
                "total_carbs": meal.total_carbs,
                "total_fat": meal.total_fat,
                "food_items_count": len(meal_data.food_items)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add meal: {e}")
        raise HTTPException(status_code=500, detail="Failed to add meal")

@router.get("/summary", response_model=NutritionSummaryResponse)
async def get_nutrition_summary(
    target_date: date = Query(default_factory=date.today),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get nutrition summary for a specific date
    """
    try:
        # Get meals for the target date
        start_datetime = datetime.combine(target_date, datetime.min.time())
        end_datetime = datetime.combine(target_date, datetime.max.time())
        
        meals = db.query(MealEntry).filter(
            MealEntry.user_id == current_user.id,
            MealEntry.consumed_at >= start_datetime,
            MealEntry.consumed_at <= end_datetime
        ).order_by(MealEntry.consumed_at).all()
        
        # Calculate totals
        total_calories = sum(meal.total_calories or 0 for meal in meals)
        total_protein = sum(meal.total_protein or 0 for meal in meals)
        total_carbs = sum(meal.total_carbs or 0 for meal in meals)
        total_fat = sum(meal.total_fat or 0 for meal in meals)
        total_fiber = sum(meal.total_fiber or 0 for meal in meals)
        
        # Get nutrition goals
        goal = db.query(NutritionGoal).filter(
            NutritionGoal.user_id == current_user.id,
            NutritionGoal.is_active == True
        ).first()
        
        goals_data = None
        if goal:
            goals_data = {
                "target_calories": goal.target_calories,
                "target_protein": goal.target_protein,
                "target_carbs": goal.target_carbs,
                "target_fat": goal.target_fat,
                "calories_progress": (total_calories / goal.target_calories * 100) if goal.target_calories else 0,
                "protein_progress": (total_protein / goal.target_protein * 100) if goal.target_protein else 0,
                "carbs_progress": (total_carbs / goal.target_carbs * 100) if goal.target_carbs else 0,
                "fat_progress": (total_fat / goal.target_fat * 100) if goal.target_fat else 0
            }
        
        # Format meals data
        meals_data = []
        for meal in meals:
            meal_foods = db.query(MealFoodItem).filter(
                MealFoodItem.meal_id == meal.id
            ).all()
            
            meals_data.append({
                "id": meal.id,
                "meal_type": meal.meal_type,
                "consumed_at": meal.consumed_at.isoformat(),
                "calories": meal.total_calories,
                "protein": meal.total_protein,
                "carbs": meal.total_carbs,
                "fat": meal.total_fat,
                "food_items_count": len(meal_foods),
                "notes": meal.notes
            })
        
        return NutritionSummaryResponse(
            date=target_date.isoformat(),
            total_calories=total_calories,
            total_protein=total_protein,
            total_carbs=total_carbs,
            total_fat=total_fat,
            total_fiber=total_fiber,
            meals=meals_data,
            goals=goals_data
        )
        
    except Exception as e:
        logger.error(f"Failed to get nutrition summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get nutrition summary")

@router.get("/meals/{meal_id}")
async def get_meal_detail(
    meal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific meal
    """
    try:
        meal = db.query(MealEntry).filter(
            MealEntry.id == meal_id,
            MealEntry.user_id == current_user.id
        ).first()
        
        if not meal:
            raise HTTPException(status_code=404, detail="Meal not found")
        
        # Get food items
        food_items = db.query(MealFoodItem).filter(
            MealFoodItem.meal_id == meal_id
        ).all()
        
        food_items_data = []
        for item in food_items:
            food = db.query(Food).filter(Food.id == item.food_id).first()
            food_items_data.append({
                "id": item.id,
                "food": {
                    "id": food.id,
                    "name": food.name,
                    "category": food.category
                },
                "quantity": item.quantity,
                "unit": item.unit,
                "calories": item.calories,
                "protein": item.protein,
                "carbs": item.carbs,
                "fat": item.fat
            })
        
        return {
            "success": True,
            "meal": {
                "id": meal.id,
                "meal_type": meal.meal_type,
                "consumed_at": meal.consumed_at.isoformat(),
                "total_calories": meal.total_calories,
                "total_protein": meal.total_protein,
                "total_carbs": meal.total_carbs,
                "total_fat": meal.total_fat,
                "notes": meal.notes,
                "food_items": food_items_data
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get meal detail: {e}")
        raise HTTPException(status_code=500, detail="Failed to get meal detail")

@router.delete("/meals/{meal_id}")
async def delete_meal(
    meal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a meal entry
    """
    try:
        meal = db.query(MealEntry).filter(
            MealEntry.id == meal_id,
            MealEntry.user_id == current_user.id
        ).first()
        
        if not meal:
            raise HTTPException(status_code=404, detail="Meal not found")
        
        # Delete food items first
        db.query(MealFoodItem).filter(MealFoodItem.meal_id == meal_id).delete()
        
        # Delete meal
        db.delete(meal)
        db.commit()
        
        return {"success": True, "message": "Meal deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete meal: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete meal")

@router.get("/foods/search")
async def search_foods(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db)
):
    """
    Search foods in the database
    """
    try:
        foods = db.query(Food).filter(
            Food.name.ilike(f"%{q}%")
        ).limit(limit).all()
        
        return {
            "success": True,
            "foods": [
                {
                    "id": food.id,
                    "name": food.name,
                    "category": food.category,
                    "calories_per_100g": food.calories_per_100g,
                    "protein_g": food.protein_g,
                    "carbs_g": food.carbs_g,
                    "fat_g": food.fat_g
                }
                for food in foods
            ]
        }
        
    except Exception as e:
        logger.error(f"Food search failed: {e}")
        raise HTTPException(status_code=500, detail="Food search failed")

@router.get("/goals")
async def get_nutrition_goals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's nutrition goals
    """
    try:
        goal = db.query(NutritionGoal).filter(
            NutritionGoal.user_id == current_user.id,
            NutritionGoal.is_active == True
        ).first()
        
        if not goal:
            return {"success": True, "goal": None}
        
        return {
            "success": True,
            "goal": {
                "id": goal.id,
                "target_calories": goal.target_calories,
                "target_protein": goal.target_protein,
                "target_carbs": goal.target_carbs,
                "target_fat": goal.target_fat,
                "protein_percentage": goal.protein_percentage,
                "carb_percentage": goal.carb_percentage,
                "fat_percentage": goal.fat_percentage,
                "activity_level": goal.activity_level,
                "start_date": goal.start_date.isoformat(),
                "end_date": goal.end_date.isoformat() if goal.end_date else None
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get nutrition goals: {e}")
        raise HTTPException(status_code=500, detail="Failed to get nutrition goals")

# Helper functions
async def analyze_food_image(image: np.ndarray) -> dict:
    """
    Analyze image to recognize food items
    This is a simplified implementation - in production you'd use a trained food recognition model
    """
    try:
        # Simplified food recognition
        # In a real implementation, you would use a trained ML model
        # For now, returning mock data
        
        return {
            "success": True,
            "foods": [
                {
                    "name": "白米",
                    "confidence": 0.85,
                    "estimated_quantity": 150,
                    "unit": "g",
                    "bounding_box": [0.2, 0.3, 0.6, 0.7],
                    "nutrition": {
                        "calories": 234,
                        "protein": 3.5,
                        "carbs": 51.0,
                        "fat": 0.3
                    }
                }
            ],
            "confidence": 0.85
        }
        
    except Exception as e:
        logger.error(f"Food image analysis error: {e}")
        return {
            "success": False,
            "error": f"Image analysis failed: {str(e)}"
        }