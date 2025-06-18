"""
V3 Calculations API - Scientific calculation endpoints for TENAX FIT
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, validator
from typing import Literal, Dict
from sqlalchemy.orm import Session

from ...app.database import get_db
from core.scientific_calculations import ScientificCalculationEngine


router = APIRouter()


# Request/Response Models
class BMRInput(BaseModel):
    """Input model for BMR calculation"""
    weight: float = Field(..., gt=0, le=300, description="Weight in kilograms")
    height: float = Field(..., gt=0, le=300, description="Height in centimeters")
    age: int = Field(..., gt=0, le=120, description="Age in years")
    gender: Literal["male", "female"] = Field(..., description="Biological sex")
    
    class Config:
        schema_extra = {
            "example": {
                "weight": 70.0,
                "height": 170.0,
                "age": 25,
                "gender": "male"
            }
        }


class BMRResponse(BaseModel):
    """Response model for BMR calculation"""
    bmr: float = Field(..., description="Basal Metabolic Rate in kcal/day")
    formula: str = Field(default="Mifflin-St Jeor", description="Formula used")
    
    class Config:
        schema_extra = {
            "example": {
                "bmr": 1642.5,
                "formula": "Mifflin-St Jeor"
            }
        }


class TDEEInput(BaseModel):
    """Input model for TDEE calculation"""
    bmr: float = Field(..., gt=0, description="Basal Metabolic Rate")
    activity_level: Literal["sedentary", "light", "moderate", "active", "very_active"] = Field(
        ..., description="Activity level"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "bmr": 1642.5,
                "activity_level": "moderate"
            }
        }


class TDEEResponse(BaseModel):
    """Response model for TDEE calculation"""
    tdee: float = Field(..., description="Total Daily Energy Expenditure in kcal/day")
    activity_coefficient: float = Field(..., description="Activity level coefficient used")
    
    class Config:
        schema_extra = {
            "example": {
                "tdee": 2545.9,
                "activity_coefficient": 1.55
            }
        }


class BodyFatInput(BaseModel):
    """Input model for body fat estimation"""
    weight: float = Field(..., gt=0, le=300, description="Weight in kilograms")
    height: float = Field(..., gt=0, le=300, description="Height in centimeters")
    age: int = Field(..., gt=0, le=120, description="Age in years")
    gender: Literal["male", "female"] = Field(..., description="Biological sex")
    
    class Config:
        schema_extra = {
            "example": {
                "weight": 70.0,
                "height": 170.0,
                "age": 25,
                "gender": "male"
            }
        }


class BodyFatResponse(BaseModel):
    """Response model for body fat estimation"""
    body_fat_percentage: float = Field(..., description="Estimated body fat percentage")
    bmi: float = Field(..., description="Body Mass Index")
    formula: str = Field(default="Tanita", description="Formula used")
    
    class Config:
        schema_extra = {
            "example": {
                "body_fat_percentage": 19.5,
                "bmi": 24.2,
                "formula": "Tanita"
            }
        }


class TargetCaloriesInput(BaseModel):
    """Input model for target calories calculation"""
    tdee: float = Field(..., gt=0, description="Total Daily Energy Expenditure")
    goal: Literal["muscle_gain", "fat_loss", "maintenance"] = Field(
        ..., description="Fitness goal"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "tdee": 2545.9,
                "goal": "muscle_gain"
            }
        }


class TargetCaloriesResponse(BaseModel):
    """Response model for target calories"""
    target_calories: float = Field(..., description="Recommended daily calorie intake")
    adjustment_percentage: float = Field(..., description="Percentage adjustment from TDEE")
    goal: str = Field(..., description="Selected fitness goal")
    
    class Config:
        schema_extra = {
            "example": {
                "target_calories": 2927.8,
                "adjustment_percentage": 15.0,
                "goal": "muscle_gain"
            }
        }


# API Endpoints
@router.post("/bmr", response_model=BMRResponse, summary="Calculate Basal Metabolic Rate")
async def calculate_bmr(data: BMRInput):
    """
    Calculate BMR using the Mifflin-St Jeor equation.
    
    This equation is considered the most accurate for modern populations.
    """
    try:
        bmr = ScientificCalculationEngine.calculate_bmr(
            weight=data.weight,
            height=data.height,
            age=data.age,
            gender=data.gender
        )
        
        return BMRResponse(
            bmr=bmr,
            formula="Mifflin-St Jeor"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal calculation error")


@router.post("/tdee", response_model=TDEEResponse, summary="Calculate Total Daily Energy Expenditure")
async def calculate_tdee(data: TDEEInput):
    """
    Calculate TDEE from BMR and activity level.
    
    Activity levels:
    - sedentary: Little to no exercise
    - light: Exercise 1-3 days/week
    - moderate: Exercise 3-5 days/week
    - active: Exercise 6-7 days/week
    - very_active: Very hard exercise & physical job
    """
    try:
        tdee = ScientificCalculationEngine.calculate_tdee(
            bmr=data.bmr,
            activity_level=data.activity_level
        )
        
        coefficient = ScientificCalculationEngine.ACTIVITY_COEFFICIENTS[data.activity_level]
        
        return TDEEResponse(
            tdee=tdee,
            activity_coefficient=coefficient
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal calculation error")


@router.post("/body-fat", response_model=BodyFatResponse, summary="Estimate Body Fat Percentage")
async def estimate_body_fat(data: BodyFatInput):
    """
    Estimate body fat percentage using the Tanita formula.
    
    This provides estimates comparable to DEXA scans for general population.
    """
    try:
        body_fat = ScientificCalculationEngine.estimate_body_fat(
            weight=data.weight,
            height=data.height,
            age=data.age,
            gender=data.gender
        )
        
        # Calculate BMI
        height_m = data.height / 100
        bmi = round(data.weight / (height_m ** 2), 1)
        
        return BodyFatResponse(
            body_fat_percentage=body_fat,
            bmi=bmi,
            formula="Tanita"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal calculation error")


@router.post("/target-calories", response_model=TargetCaloriesResponse, 
            summary="Calculate Target Daily Calories")
async def calculate_target_calories(data: TargetCaloriesInput):
    """
    Calculate recommended daily calorie intake based on TDEE and fitness goal.
    
    Goals:
    - muscle_gain: 15% calorie surplus
    - fat_loss: 20% calorie deficit
    - maintenance: No adjustment
    """
    try:
        target_calories = ScientificCalculationEngine.calculate_target_calories(
            tdee=data.tdee,
            goal=data.goal
        )
        
        # Calculate adjustment percentage
        adjustment = ScientificCalculationEngine.GOAL_ADJUSTMENTS[data.goal]
        adjustment_percentage = (adjustment - 1.0) * 100
        
        return TargetCaloriesResponse(
            target_calories=target_calories,
            adjustment_percentage=adjustment_percentage,
            goal=data.goal
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal calculation error")