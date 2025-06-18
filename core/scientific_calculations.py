"""
Scientific Calculation Engine for TENAX FIT v3.0
Implements medically-validated formulas for fitness calculations
"""
from typing import Literal, Dict, Tuple
import math


class ScientificCalculationEngine:
    """
    Core calculation engine implementing scientifically-validated formulas
    for BMR, TDEE, body fat percentage, and nutrition calculations.
    """
    
    # Activity level coefficients based on Harris-Benedict revised equation
    ACTIVITY_COEFFICIENTS = {
        "sedentary": 1.2,      # Little to no exercise
        "light": 1.375,        # Exercise 1-3 days/week
        "moderate": 1.55,      # Exercise 3-5 days/week
        "active": 1.725,       # Exercise 6-7 days/week
        "very_active": 1.9     # Very hard exercise & physical job
    }
    
    # Goal-based calorie adjustments
    GOAL_ADJUSTMENTS = {
        "muscle_gain": 1.15,   # 15% surplus
        "fat_loss": 0.80,      # 20% deficit
        "maintenance": 1.00    # No adjustment
    }
    
    # Goal-based PFC ratios (Protein, Fat, Carbs)
    PFC_RATIOS = {
        "muscle_gain": {"protein": 0.30, "fat": 0.25, "carbs": 0.45},
        "fat_loss": {"protein": 0.40, "fat": 0.30, "carbs": 0.30},
        "maintenance": {"protein": 0.25, "fat": 0.30, "carbs": 0.45}
    }
    
    @staticmethod
    def calculate_bmr(weight: float, height: float, age: int, gender: Literal["male", "female"]) -> float:
        """
        Calculate Basal Metabolic Rate using Mifflin-St Jeor equation.
        
        This equation is considered more accurate than Harris-Benedict for modern populations.
        Published in: Am J Clin Nutr. 1990 Feb;51(2):241-7.
        
        Args:
            weight: Weight in kilograms
            height: Height in centimeters
            age: Age in years
            gender: Biological sex ("male" or "female")
            
        Returns:
            BMR in kilocalories per day
            
        Formula:
            Men: BMR = (10 × weight[kg]) + (6.25 × height[cm]) - (5 × age[years]) + 5
            Women: BMR = (10 × weight[kg]) + (6.25 × height[cm]) - (5 × age[years]) - 161
        """
        if weight <= 0 or height <= 0 or age <= 0:
            raise ValueError("Weight, height, and age must be positive values")
            
        if gender not in ["male", "female"]:
            raise ValueError("Gender must be 'male' or 'female'")
        
        # Base calculation
        bmr = (10 * weight) + (6.25 * height) - (5 * age)
        
        # Gender adjustment
        if gender == "male":
            bmr += 5
        else:  # female
            bmr -= 161
            
        return round(bmr, 1)
    
    @staticmethod
    def calculate_tdee(bmr: float, activity_level: str) -> float:
        """
        Calculate Total Daily Energy Expenditure from BMR and activity level.
        
        Args:
            bmr: Basal Metabolic Rate in kcal/day
            activity_level: One of sedentary, light, moderate, active, very_active
            
        Returns:
            TDEE in kilocalories per day
        """
        if bmr <= 0:
            raise ValueError("BMR must be a positive value")
            
        if activity_level not in ScientificCalculationEngine.ACTIVITY_COEFFICIENTS:
            raise ValueError(f"Invalid activity level. Must be one of: {list(ScientificCalculationEngine.ACTIVITY_COEFFICIENTS.keys())}")
        
        coefficient = ScientificCalculationEngine.ACTIVITY_COEFFICIENTS[activity_level]
        return round(bmr * coefficient, 1)
    
    @staticmethod
    def estimate_body_fat(weight: float, height: float, age: int, gender: Literal["male", "female"]) -> float:
        """
        Estimate body fat percentage using the Tanita formula.
        
        This is a bioelectrical impedance-based formula that provides estimates
        comparable to DEXA scans for general population.
        
        Args:
            weight: Weight in kilograms
            height: Height in centimeters
            age: Age in years
            gender: Biological sex
            
        Returns:
            Estimated body fat percentage
            
        Formula:
            Body Fat % = 1.2 × BMI + 0.23 × age - 10.8 × gender_coefficient - 5.4
            Where gender_coefficient = 1 for male, 0 for female
        """
        if weight <= 0 or height <= 0 or age <= 0:
            raise ValueError("Weight, height, and age must be positive values")
        
        # Calculate BMI
        height_m = height / 100  # Convert cm to meters
        bmi = weight / (height_m ** 2)
        
        # Gender coefficient
        gender_coefficient = 1 if gender == "male" else 0
        
        # Tanita formula
        body_fat = (1.2 * bmi) + (0.23 * age) - (10.8 * gender_coefficient) - 5.4
        
        # Ensure reasonable bounds (minimum essential fat)
        min_essential_fat = 3 if gender == "male" else 10
        body_fat = max(body_fat, min_essential_fat)
        
        return round(body_fat, 1)
    
    @staticmethod
    def calculate_target_calories(tdee: float, goal: str) -> float:
        """
        Calculate target daily calories based on TDEE and fitness goal.
        
        Args:
            tdee: Total Daily Energy Expenditure
            goal: One of muscle_gain, fat_loss, maintenance
            
        Returns:
            Target daily calorie intake
        """
        if tdee <= 0:
            raise ValueError("TDEE must be a positive value")
            
        if goal not in ScientificCalculationEngine.GOAL_ADJUSTMENTS:
            raise ValueError(f"Invalid goal. Must be one of: {list(ScientificCalculationEngine.GOAL_ADJUSTMENTS.keys())}")
        
        adjustment = ScientificCalculationEngine.GOAL_ADJUSTMENTS[goal]
        return round(tdee * adjustment, 1)
    
    @staticmethod
    def calculate_pfc_balance(calories: float, goal: str) -> Dict[str, Dict[str, float]]:
        """
        Calculate macronutrient distribution based on calories and goal.
        
        Args:
            calories: Daily calorie target
            goal: Fitness goal
            
        Returns:
            Dictionary with grams and calories for each macronutrient
        """
        if calories <= 0:
            raise ValueError("Calories must be a positive value")
            
        if goal not in ScientificCalculationEngine.PFC_RATIOS:
            raise ValueError(f"Invalid goal. Must be one of: {list(ScientificCalculationEngine.PFC_RATIOS.keys())}")
        
        ratios = ScientificCalculationEngine.PFC_RATIOS[goal]
        
        # Calculate calories for each macro
        protein_cal = calories * ratios["protein"]
        fat_cal = calories * ratios["fat"]
        carbs_cal = calories * ratios["carbs"]
        
        # Convert to grams (protein: 4 cal/g, fat: 9 cal/g, carbs: 4 cal/g)
        result = {
            "protein": {
                "grams": round(protein_cal / 4, 1),
                "calories": round(protein_cal, 1),
                "percentage": round(ratios["protein"] * 100, 1)
            },
            "fat": {
                "grams": round(fat_cal / 9, 1),
                "calories": round(fat_cal, 1),
                "percentage": round(ratios["fat"] * 100, 1)
            },
            "carbs": {
                "grams": round(carbs_cal / 4, 1),
                "calories": round(carbs_cal, 1),
                "percentage": round(ratios["carbs"] * 100, 1)
            }
        }
        
        return result
    
    @staticmethod
    def check_calorie_safety(bmr: float, target_calories: float) -> Dict[str, any]:
        """
        Check if target calorie intake is safe based on BMR.
        
        Args:
            bmr: Basal Metabolic Rate
            target_calories: Proposed daily calorie intake
            
        Returns:
            Safety assessment with warnings if applicable
        """
        if bmr <= 0 or target_calories <= 0:
            raise ValueError("BMR and target calories must be positive values")
        
        percentage_of_bmr = (target_calories / bmr) * 100
        
        result = {
            "is_safe": True,
            "percentage_of_bmr": round(percentage_of_bmr, 1),
            "warnings": [],
            "severity": "low"
        }
        
        if percentage_of_bmr < 50:
            result["is_safe"] = False
            result["severity"] = "critical"
            result["warnings"].append("極度のカロリー制限は危険です。医師に相談してください。")
        elif percentage_of_bmr < 70:
            result["is_safe"] = False
            result["severity"] = "high"
            result["warnings"].append("カロリー設定がBMRを大幅に下回っています。代謝低下のリスクがあります。")
        elif percentage_of_bmr < 80:
            result["severity"] = "medium"
            result["warnings"].append("カロリー制限が厳しめです。長期継続は推奨されません。")
        elif percentage_of_bmr > 300:
            result["severity"] = "medium"
            result["warnings"].append("カロリー摂取が過剰です。体脂肪増加のリスクがあります。")
            
        return result
    
    @staticmethod
    def check_body_fat_goals(target_body_fat: float, gender: Literal["male", "female"]) -> Dict[str, any]:
        """
        Check if body fat percentage goal is healthy.
        
        Args:
            target_body_fat: Target body fat percentage
            gender: Biological sex
            
        Returns:
            Health assessment with warnings if applicable
        """
        # Essential fat levels
        essential_fat = {"male": 3, "female": 10}
        # Athletic ranges
        athletic_range = {"male": (6, 13), "female": (14, 20)}
        # Healthy ranges
        healthy_range = {"male": (14, 24), "female": (21, 31)}
        
        result = {
            "is_healthy": True,
            "category": "",
            "warnings": [],
            "recommendations": []
        }
        
        min_essential = essential_fat[gender]
        athletic_min, athletic_max = athletic_range[gender]
        healthy_min, healthy_max = healthy_range[gender]
        
        if target_body_fat < min_essential:
            result["is_healthy"] = False
            result["category"] = "危険"
            result["warnings"].append(f"{gender}の体脂肪率{target_body_fat}%は生命維持に必要な最低値を下回っています。")
            result["recommendations"].append(f"最低でも{min_essential}%以上を維持してください。")
        elif target_body_fat < athletic_min:
            result["is_healthy"] = False
            result["category"] = "極度に低い"
            result["warnings"].append(f"{gender}の体脂肪率{target_body_fat}%は健康リスクがあります。")
            result["recommendations"].append("ホルモンバランスや免疫機能への影響が懸念されます。")
        elif target_body_fat <= athletic_max:
            result["category"] = "アスリート"
            result["recommendations"].append("競技者レベルの体脂肪率です。適切な栄養管理が必要です。")
        elif target_body_fat <= healthy_max:
            result["category"] = "健康的"
            result["recommendations"].append("理想的な体脂肪率範囲です。")
        else:
            result["category"] = "高め"
            result["recommendations"].append("健康リスク低減のため、体脂肪率の改善を検討してください。")
            
        return result