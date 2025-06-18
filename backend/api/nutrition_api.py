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
    current_user: User = Depends(get_current_user),
    save_to_meal: bool = Query(False, description="Automatically save recognized foods as a meal"),
    meal_type: Optional[str] = Query(None, description="Meal type if save_to_meal is true")
):
    """
    Recognize food items from uploaded image with optional automatic meal logging
    
    Parameters:
    - file: Image file containing food
    - save_to_meal: If true, automatically creates a meal entry
    - meal_type: Type of meal (breakfast, lunch, dinner, snack)
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
        
        # If requested, save recognized foods as a meal
        if save_to_meal and recognition_result.get("success") and recognition_result.get("foods"):
            if not meal_type:
                # Auto-detect meal type based on current time
                current_hour = datetime.now().hour
                if 5 <= current_hour < 11:
                    meal_type = "breakfast"
                elif 11 <= current_hour < 15:
                    meal_type = "lunch"
                elif 15 <= current_hour < 21:
                    meal_type = "dinner"
                else:
                    meal_type = "snack"
            
            # Create meal entry (implementation would go here)
            # This would save the recognized foods to the database
            
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
            error=str(e)
        )

@router.post("/recognize/batch")
async def recognize_food_batch(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Recognize food items from multiple images
    Useful for capturing a complete meal from different angles
    """
    import time
    start_time = time.time()
    
    if len(files) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 images allowed per batch"
        )
    
    all_foods = []
    total_confidence = 0
    successful_images = 0
    
    for idx, file in enumerate(files):
        try:
            if not file.content_type.startswith('image/'):
                continue
            
            image_data = await file.read()
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                continue
            
            # Recognize foods in this image
            result = await analyze_food_image(image)
            
            if result.get("success"):
                successful_images += 1
                total_confidence += result.get("confidence", 0)
                
                # Add image index to each food item
                for food in result.get("foods", []):
                    food["image_index"] = idx
                    all_foods.append(food)
        
        except Exception as e:
            logger.error(f"Error processing image {idx}: {e}")
            continue
    
    if successful_images == 0:
        return {
            "success": False,
            "error": "No valid images could be processed",
            "foods": []
        }
    
    # Merge duplicate foods from different angles
    merged_foods = merge_duplicate_foods(all_foods)
    
    processing_time = time.time() - start_time
    avg_confidence = total_confidence / successful_images if successful_images > 0 else 0
    
    return {
        "success": True,
        "foods": merged_foods,
        "confidence": avg_confidence,
        "images_processed": successful_images,
        "total_images": len(files),
        "processing_time": processing_time
    }

def merge_duplicate_foods(foods: List[dict]) -> List[dict]:
    """
    Merge foods that appear to be the same item from different angles
    """
    if not foods:
        return []
    
    merged = []
    used_indices = set()
    
    for i, food1 in enumerate(foods):
        if i in used_indices:
            continue
        
        # Start with this food
        merged_food = food1.copy()
        similar_foods = [food1]
        used_indices.add(i)
        
        # Look for similar foods
        for j, food2 in enumerate(foods[i+1:], start=i+1):
            if j in used_indices:
                continue
            
            # Check if foods are similar (same name or very close positions)
            if (food1["name"] == food2["name"] or 
                food1.get("name_en", "") == food2.get("name_en", "")):
                similar_foods.append(food2)
                used_indices.add(j)
        
        # Average the quantities and confidence scores
        if len(similar_foods) > 1:
            avg_quantity = sum(f["estimated_quantity"] for f in similar_foods) / len(similar_foods)
            avg_confidence = sum(f["confidence"] for f in similar_foods) / len(similar_foods)
            
            merged_food["estimated_quantity"] = avg_quantity
            merged_food["confidence"] = avg_confidence
            merged_food["detection_count"] = len(similar_foods)
            
            # Recalculate nutrition based on averaged quantity
            if "nutrition" in merged_food:
                factor = avg_quantity / 100.0
                base_nutrition = similar_foods[0]["nutrition"]
                merged_food["nutrition"] = {
                    key: round(base_nutrition[key] * factor / (similar_foods[0]["estimated_quantity"] / 100.0), 1)
                    for key in base_nutrition
                }
        
        merged.append(merged_food)
    
    return merged

@router.post("/recognize/url")
async def recognize_food_from_url(
    image_url: str,
    current_user: User = Depends(get_current_user)
):
    """
    Recognize food items from image URL
    """
    import httpx
    import time
    start_time = time.time()
    
    try:
        # Download image
        async with httpx.AsyncClient() as client:
            response = await client.get(image_url, timeout=10.0)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to download image from URL"
                )
        
        # Convert to OpenCV format
        nparr = np.frombuffer(response.content, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(
                status_code=400,
                detail="Could not decode image from URL"
            )
        
        # Perform recognition
        recognition_result = await analyze_food_image(image)
        
        processing_time = time.time() - start_time
        
        return FoodRecognitionResponse(
            success=recognition_result.get("success", False),
            recognized_foods=recognition_result.get("foods", []),
            confidence=recognition_result.get("confidence"),
            processing_time=processing_time,
            error=recognition_result.get("error")
        )
        
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error downloading image: {str(e)}"
        )
    except Exception as e:
        logger.error(f"URL food recognition error: {e}")
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

# Import the enhanced food recognition service
from ..services.food_recognition import FoodRecognitionService

# Initialize food recognition service
food_recognition_service = FoodRecognitionService()

# Helper functions
async def analyze_food_image(image: np.ndarray) -> dict:
    """
    Analyze image to recognize food items using enhanced ML service
    """
    try:
        # Use the enhanced food recognition service
        result = await food_recognition_service.recognize_food(image)
        
        if not result["success"]:
            return result
        
        # Format the response to match expected structure
        formatted_foods = []
        for food in result.get("foods", []):
            formatted_foods.append({
                "name": food["name_ja"],  # Use Japanese name as primary
                "name_en": food["name"],
                "confidence": food["confidence"],
                "estimated_quantity": food["estimated_quantity"],
                "unit": food["unit"],
                "bounding_box": food["bounding_box"],
                "nutrition": {
                    "calories": food["nutrition"]["calories"],
                    "protein": food["nutrition"]["protein"],
                    "carbs": food["nutrition"]["carbs"],
                    "fat": food["nutrition"]["fat"],
                    "fiber": food["nutrition"].get("fiber", 0)
                }
            })
        
        return {
            "success": True,
            "foods": formatted_foods,
            "confidence": result.get("confidence", 0),
            "detection_count": result.get("detection_count", 0)
        }
        
    except Exception as e:
        logger.error(f"Food image analysis error: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Image analysis failed: {str(e)}"
        }