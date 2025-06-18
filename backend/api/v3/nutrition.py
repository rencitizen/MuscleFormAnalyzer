"""
V3 Nutrition API - Nutrition management endpoints for TENAX FIT
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Literal, Dict, List

from core.scientific_calculations import ScientificCalculationEngine


router = APIRouter()


# Request/Response Models
class PFCBalanceInput(BaseModel):
    """Input model for PFC balance calculation"""
    calories: float = Field(..., gt=0, le=10000, description="Daily calorie target")
    goal: Literal["muscle_gain", "fat_loss", "maintenance"] = Field(
        ..., description="Fitness goal"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "calories": 2500,
                "goal": "muscle_gain"
            }
        }


class MacronutrientInfo(BaseModel):
    """Information for a single macronutrient"""
    grams: float = Field(..., description="Amount in grams")
    calories: float = Field(..., description="Calories from this macronutrient")
    percentage: float = Field(..., description="Percentage of total calories")


class PFCBalanceResponse(BaseModel):
    """Response model for PFC balance"""
    protein: MacronutrientInfo
    fat: MacronutrientInfo
    carbs: MacronutrientInfo
    total_calories: float = Field(..., description="Total calories (verification)")
    goal: str = Field(..., description="Selected fitness goal")
    
    class Config:
        schema_extra = {
            "example": {
                "protein": {
                    "grams": 187.5,
                    "calories": 750.0,
                    "percentage": 30.0
                },
                "fat": {
                    "grams": 69.4,
                    "calories": 625.0,
                    "percentage": 25.0
                },
                "carbs": {
                    "grams": 281.3,
                    "calories": 1125.0,
                    "percentage": 45.0
                },
                "total_calories": 2500.0,
                "goal": "muscle_gain"
            }
        }


class MicronutrientInfo(BaseModel):
    """Information for a micronutrient"""
    name: str = Field(..., description="Micronutrient name")
    recommended_amount: str = Field(..., description="Recommended daily amount")
    unit: str = Field(..., description="Unit of measurement")
    importance: str = Field(..., description="Why this nutrient is important")
    sources: List[str] = Field(..., description="Food sources")


class MicronutrientsResponse(BaseModel):
    """Response model for micronutrient recommendations"""
    vitamins: List[MicronutrientInfo]
    minerals: List[MicronutrientInfo]
    notes: List[str] = Field(..., description="Additional recommendations")


class ProteinFood(BaseModel):
    """High protein food item"""
    name: str = Field(..., description="Food name")
    protein_per_100g: float = Field(..., description="Protein content per 100g")
    calories_per_100g: float = Field(..., description="Calories per 100g")
    category: str = Field(..., description="Food category")
    complete_protein: bool = Field(..., description="Contains all essential amino acids")


class HighProteinFoodsResponse(BaseModel):
    """Response model for high protein foods"""
    foods: List[ProteinFood]
    categories: List[str] = Field(..., description="Available food categories")


# API Endpoints
@router.post("/pfc-balance", response_model=PFCBalanceResponse, 
            summary="Calculate PFC Balance")
async def calculate_pfc_balance(data: PFCBalanceInput):
    """
    Calculate optimal protein, fat, and carbohydrate distribution based on fitness goal.
    
    Goal-based ratios:
    - muscle_gain: P30%, F25%, C45%
    - fat_loss: P40%, F30%, C30%
    - maintenance: P25%, F30%, C45%
    """
    try:
        pfc_data = ScientificCalculationEngine.calculate_pfc_balance(
            calories=data.calories,
            goal=data.goal
        )
        
        return PFCBalanceResponse(
            protein=MacronutrientInfo(**pfc_data["protein"]),
            fat=MacronutrientInfo(**pfc_data["fat"]),
            carbs=MacronutrientInfo(**pfc_data["carbs"]),
            total_calories=data.calories,
            goal=data.goal
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal calculation error")


@router.get("/micronutrients", response_model=MicronutrientsResponse,
           summary="Get Micronutrient Recommendations")
async def get_micronutrient_recommendations():
    """
    Get recommended daily micronutrient intake for optimal fitness.
    
    Based on international dietary guidelines for active adults.
    """
    vitamins = [
        MicronutrientInfo(
            name="ビタミンD",
            recommended_amount="15-20",
            unit="μg",
            importance="筋肉機能、骨健康、免疫力向上",
            sources=["サケ", "サバ", "卵黄", "強化乳製品", "日光浴"]
        ),
        MicronutrientInfo(
            name="ビタミンB12",
            recommended_amount="2.4",
            unit="μg",
            importance="エネルギー代謝、赤血球生成",
            sources=["肉類", "魚介類", "卵", "乳製品"]
        ),
        MicronutrientInfo(
            name="ビタミンC",
            recommended_amount="90-100",
            unit="mg",
            importance="抗酸化作用、コラーゲン生成、免疫機能",
            sources=["柑橘類", "イチゴ", "ピーマン", "ブロッコリー"]
        ),
        MicronutrientInfo(
            name="ビタミンE",
            recommended_amount="15",
            unit="mg",
            importance="抗酸化作用、筋肉回復",
            sources=["ナッツ類", "種子類", "植物油", "アボカド"]
        )
    ]
    
    minerals = [
        MicronutrientInfo(
            name="亜鉛",
            recommended_amount="11-15",
            unit="mg",
            importance="免疫機能、タンパク質合成、テストステロン生成",
            sources=["牡蠣", "牛肉", "かぼちゃの種", "レンズ豆"]
        ),
        MicronutrientInfo(
            name="マグネシウム",
            recommended_amount="400-420",
            unit="mg",
            importance="筋肉機能、エネルギー生成、睡眠改善",
            sources=["アーモンド", "ほうれん草", "黒豆", "全粒穀物"]
        ),
        MicronutrientInfo(
            name="鉄",
            recommended_amount="8-18",
            unit="mg",
            importance="酸素運搬、エネルギー生成",
            sources=["赤身肉", "レバー", "ほうれん草", "豆類"]
        ),
        MicronutrientInfo(
            name="カルシウム",
            recommended_amount="1000-1200",
            unit="mg",
            importance="骨健康、筋肉収縮",
            sources=["乳製品", "小魚", "豆腐", "緑黄色野菜"]
        )
    ]
    
    notes = [
        "運動量が多い場合は、発汗により失われるミネラルの補給が重要です",
        "ビタミンDは日光浴でも生成されますが、サプリメント摂取も検討してください",
        "植物性食品からの鉄分摂取時は、ビタミンCと一緒に摂ると吸収率が向上します"
    ]
    
    return MicronutrientsResponse(
        vitamins=vitamins,
        minerals=minerals,
        notes=notes
    )


@router.get("/high-protein-foods", response_model=HighProteinFoodsResponse,
           summary="Get High Protein Food Database")
async def get_high_protein_foods(category: str = None):
    """
    Get a list of high protein foods with nutritional information.
    
    Categories: animal, plant, dairy, seafood
    """
    all_foods = [
        # Animal proteins
        ProteinFood(
            name="鶏胸肉（皮なし）",
            protein_per_100g=31.0,
            calories_per_100g=165,
            category="animal",
            complete_protein=True
        ),
        ProteinFood(
            name="牛赤身肉",
            protein_per_100g=26.0,
            calories_per_100g=250,
            category="animal",
            complete_protein=True
        ),
        ProteinFood(
            name="豚ヒレ肉",
            protein_per_100g=22.8,
            calories_per_100g=115,
            category="animal",
            complete_protein=True
        ),
        # Seafood
        ProteinFood(
            name="マグロ（赤身）",
            protein_per_100g=26.4,
            calories_per_100g=125,
            category="seafood",
            complete_protein=True
        ),
        ProteinFood(
            name="サケ",
            protein_per_100g=22.3,
            calories_per_100g=200,
            category="seafood",
            complete_protein=True
        ),
        ProteinFood(
            name="エビ",
            protein_per_100g=20.0,
            calories_per_100g=99,
            category="seafood",
            complete_protein=True
        ),
        # Dairy
        ProteinFood(
            name="ギリシャヨーグルト（無脂肪）",
            protein_per_100g=10.0,
            calories_per_100g=59,
            category="dairy",
            complete_protein=True
        ),
        ProteinFood(
            name="カッテージチーズ",
            protein_per_100g=11.0,
            calories_per_100g=98,
            category="dairy",
            complete_protein=True
        ),
        # Plant proteins
        ProteinFood(
            name="大豆",
            protein_per_100g=36.0,
            calories_per_100g=446,
            category="plant",
            complete_protein=True
        ),
        ProteinFood(
            name="レンズ豆",
            protein_per_100g=9.0,
            calories_per_100g=116,
            category="plant",
            complete_protein=False
        ),
        ProteinFood(
            name="キヌア",
            protein_per_100g=4.4,
            calories_per_100g=120,
            category="plant",
            complete_protein=True
        ),
        ProteinFood(
            name="アーモンド",
            protein_per_100g=21.0,
            calories_per_100g=579,
            category="plant",
            complete_protein=False
        )
    ]
    
    # Filter by category if provided
    if category:
        foods = [f for f in all_foods if f.category == category]
        if not foods:
            raise HTTPException(status_code=404, detail=f"Category '{category}' not found")
    else:
        foods = all_foods
    
    # Get unique categories
    categories = list(set(f.category for f in all_foods))
    
    return HighProteinFoodsResponse(
        foods=foods,
        categories=sorted(categories)
    )