"""
V3 Safety API - Health and safety check endpoints for TENAX FIT
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Literal, List, Dict, Optional

from core.scientific_calculations import ScientificCalculationEngine


router = APIRouter()


# Request/Response Models
class CalorieSafetyInput(BaseModel):
    """Input model for calorie safety check"""
    bmr: float = Field(..., gt=0, description="Basal Metabolic Rate")
    target_calories: float = Field(..., gt=0, description="Proposed daily calorie intake")
    
    class Config:
        schema_extra = {
            "example": {
                "bmr": 1642.5,
                "target_calories": 1200
            }
        }


class SafetyResponse(BaseModel):
    """Response model for safety checks"""
    is_safe: bool = Field(..., description="Whether the parameters are safe")
    percentage_of_bmr: Optional[float] = Field(None, description="Calories as percentage of BMR")
    warnings: List[str] = Field(..., description="List of warnings")
    severity: Literal["low", "medium", "high", "critical"] = Field(
        ..., description="Severity level of concerns"
    )
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    
    class Config:
        schema_extra = {
            "example": {
                "is_safe": False,
                "percentage_of_bmr": 73.1,
                "warnings": ["カロリー設定がBMRを大幅に下回っています"],
                "severity": "high",
                "recommendations": ["最低でもBMRの80%以上のカロリー摂取を推奨します"]
            }
        }


class BodyFatGoalInput(BaseModel):
    """Input model for body fat goal check"""
    target_body_fat: float = Field(..., ge=0, le=50, description="Target body fat percentage")
    gender: Literal["male", "female"] = Field(..., description="Biological sex")
    
    class Config:
        schema_extra = {
            "example": {
                "target_body_fat": 8,
                "gender": "female"
            }
        }


class UserHealthData(BaseModel):
    """Comprehensive user health data for overall assessment"""
    weight: float = Field(..., gt=0, description="Weight in kg")
    height: float = Field(..., gt=0, description="Height in cm")
    age: int = Field(..., gt=0, description="Age in years")
    gender: Literal["male", "female"] = Field(..., description="Biological sex")
    target_calories: Optional[float] = Field(None, description="Target daily calories")
    target_body_fat: Optional[float] = Field(None, description="Target body fat percentage")
    activity_level: Optional[str] = Field(None, description="Activity level")
    goal: Optional[str] = Field(None, description="Fitness goal")
    medical_conditions: List[str] = Field(default_factory=list, description="Known conditions")
    
    class Config:
        schema_extra = {
            "example": {
                "weight": 70,
                "height": 170,
                "age": 25,
                "gender": "male",
                "target_calories": 1500,
                "target_body_fat": 10,
                "activity_level": "moderate",
                "goal": "fat_loss",
                "medical_conditions": []
            }
        }


class HealthWarningsResponse(BaseModel):
    """Response model for comprehensive health warnings"""
    overall_risk_level: Literal["low", "medium", "high", "critical"]
    categories_checked: List[str]
    warnings: Dict[str, List[str]]
    recommendations: Dict[str, List[str]]
    requires_medical_consultation: bool
    
    class Config:
        schema_extra = {
            "example": {
                "overall_risk_level": "medium",
                "categories_checked": ["calorie_intake", "body_fat_goal"],
                "warnings": {
                    "calorie_intake": ["カロリー制限が厳しめです"],
                    "body_fat_goal": ["目標体脂肪率が低すぎます"]
                },
                "recommendations": {
                    "calorie_intake": ["段階的にカロリーを減らすことを推奨"],
                    "body_fat_goal": ["より現実的な目標設定を検討してください"]
                },
                "requires_medical_consultation": False
            }
        }


# API Endpoints
@router.post("/calorie-check", response_model=SafetyResponse,
            summary="Check Calorie Intake Safety")
async def check_calorie_safety(data: CalorieSafetyInput):
    """
    Check if proposed calorie intake is safe based on BMR.
    
    Safety thresholds:
    - <50% of BMR: Critical (dangerous)
    - 50-70% of BMR: High risk
    - 70-80% of BMR: Medium risk
    - >300% of BMR: Medium risk (excessive)
    """
    try:
        result = ScientificCalculationEngine.check_calorie_safety(
            bmr=data.bmr,
            target_calories=data.target_calories
        )
        
        # Add recommendations based on severity
        recommendations = []
        if result["severity"] == "critical":
            recommendations.extend([
                "医師または栄養士に相談することを強く推奨します",
                "極端なカロリー制限は健康に深刻な影響を与える可能性があります"
            ])
        elif result["severity"] == "high":
            recommendations.extend([
                "最低でもBMRの80%以上のカロリー摂取を推奨します",
                "段階的にカロリーを調整することを検討してください"
            ])
        elif result["severity"] == "medium":
            recommendations.extend([
                "長期的な継続は慎重に行ってください",
                "定期的に体調をモニタリングすることが重要です"
            ])
        
        return SafetyResponse(
            is_safe=result["is_safe"],
            percentage_of_bmr=result["percentage_of_bmr"],
            warnings=result["warnings"],
            severity=result["severity"],
            recommendations=recommendations
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal calculation error")


@router.post("/body-fat-check", response_model=SafetyResponse,
            summary="Check Body Fat Goal Safety")
async def check_body_fat_goal(data: BodyFatGoalInput):
    """
    Check if target body fat percentage is healthy.
    
    Essential body fat levels:
    - Male: 3-5%
    - Female: 10-13%
    
    Below essential levels can cause serious health issues.
    """
    try:
        result = ScientificCalculationEngine.check_body_fat_goals(
            target_body_fat=data.target_body_fat,
            gender=data.gender
        )
        
        return SafetyResponse(
            is_safe=result["is_healthy"],
            warnings=result["warnings"],
            severity="critical" if result["category"] == "危険" else
                    "high" if result["category"] == "極度に低い" else
                    "low",
            recommendations=result["recommendations"]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal calculation error")


@router.post("/health-warnings", response_model=HealthWarningsResponse,
            summary="Generate Comprehensive Health Warnings")
async def generate_health_warnings(data: UserHealthData):
    """
    Generate comprehensive health warnings based on user data.
    
    Checks multiple health parameters and provides integrated recommendations.
    """
    warnings = {}
    recommendations = {}
    categories_checked = []
    risk_levels = []
    
    # Calculate BMR for calorie checks
    bmr = ScientificCalculationEngine.calculate_bmr(
        weight=data.weight,
        height=data.height,
        age=data.age,
        gender=data.gender
    )
    
    # Check calorie safety if target provided
    if data.target_calories:
        categories_checked.append("calorie_intake")
        calorie_result = ScientificCalculationEngine.check_calorie_safety(
            bmr=bmr,
            target_calories=data.target_calories
        )
        if calorie_result["warnings"]:
            warnings["calorie_intake"] = calorie_result["warnings"]
            recommendations["calorie_intake"] = [
                f"推奨カロリー範囲: {int(bmr * 0.8)} - {int(bmr * 1.2)} kcal/日"
            ]
            risk_levels.append(calorie_result["severity"])
    
    # Check body fat goal if provided
    if data.target_body_fat is not None:
        categories_checked.append("body_fat_goal")
        bf_result = ScientificCalculationEngine.check_body_fat_goals(
            target_body_fat=data.target_body_fat,
            gender=data.gender
        )
        if bf_result["warnings"]:
            warnings["body_fat_goal"] = bf_result["warnings"]
            recommendations["body_fat_goal"] = bf_result["recommendations"]
            if bf_result["category"] == "危険":
                risk_levels.append("critical")
            elif bf_result["category"] == "極度に低い":
                risk_levels.append("high")
    
    # Age-specific warnings
    categories_checked.append("age_factors")
    if data.age < 18:
        warnings["age_factors"] = ["18歳未満の方は成長期のため、特別な栄養配慮が必要です"]
        recommendations["age_factors"] = ["医師または栄養士の指導を受けることを推奨します"]
        risk_levels.append("medium")
    elif data.age > 65:
        warnings["age_factors"] = ["65歳以上の方は筋肉量維持に特別な注意が必要です"]
        recommendations["age_factors"] = ["十分なタンパク質摂取と適度な運動を心がけてください"]
    
    # Medical conditions check
    if data.medical_conditions:
        categories_checked.append("medical_conditions")
        warnings["medical_conditions"] = ["既往症がある場合は医師に相談してください"]
        recommendations["medical_conditions"] = ["個別の医療アドバイスを優先してください"]
        risk_levels.append("high")
    
    # Determine overall risk level
    if "critical" in risk_levels:
        overall_risk = "critical"
    elif "high" in risk_levels:
        overall_risk = "high"
    elif "medium" in risk_levels:
        overall_risk = "medium"
    else:
        overall_risk = "low"
    
    # Determine if medical consultation is needed
    requires_medical = overall_risk in ["critical", "high"] or bool(data.medical_conditions)
    
    return HealthWarningsResponse(
        overall_risk_level=overall_risk,
        categories_checked=categories_checked,
        warnings=warnings,
        recommendations=recommendations,
        requires_medical_consultation=requires_medical
    )