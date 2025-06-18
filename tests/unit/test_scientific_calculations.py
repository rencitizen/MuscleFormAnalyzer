"""
Unit tests for Scientific Calculation Engine
Tests accuracy of BMR, TDEE, body fat estimation, and other calculations
"""
import pytest
from core.scientific_calculations import ScientificCalculationEngine


class TestBMRCalculation:
    """Test cases for BMR calculation using Mifflin-St Jeor equation"""
    
    def test_bmr_male_accuracy(self):
        """Test BMR calculation accuracy for males"""
        # Test case: 25-year-old male, 70kg, 170cm
        # Expected: (10 × 70) + (6.25 × 170) - (5 × 25) + 5 = 1642.5 kcal
        result = ScientificCalculationEngine.calculate_bmr(70, 170, 25, "male")
        assert result == 1642.5
        
        # Test case: 30-year-old male, 80kg, 180cm
        # Expected: (10 × 80) + (6.25 × 180) - (5 × 30) + 5 = 1780.0 kcal
        result = ScientificCalculationEngine.calculate_bmr(80, 180, 30, "male")
        assert result == 1780.0
    
    def test_bmr_female_accuracy(self):
        """Test BMR calculation accuracy for females"""
        # Test case: 25-year-old female, 55kg, 160cm
        # Expected: (10 × 55) + (6.25 × 160) - (5 × 25) - 161 = 1264 kcal
        result = ScientificCalculationEngine.calculate_bmr(55, 160, 25, "female")
        assert result == 1264.0
        
        # Test case: 35-year-old female, 65kg, 165cm
        # Expected: (10 × 65) + (6.25 × 165) - (5 × 35) - 161 = 1345.625 → 1345.6
        result = ScientificCalculationEngine.calculate_bmr(65, 165, 35, "female")
        assert result == 1345.6
    
    def test_bmr_edge_cases(self):
        """Test BMR calculation with edge cases"""
        # Very low weight
        result = ScientificCalculationEngine.calculate_bmr(40, 150, 20, "male")
        assert result > 0
        
        # Very high weight
        result = ScientificCalculationEngine.calculate_bmr(150, 190, 40, "male")
        assert result > 0
        
        # Elderly person
        result = ScientificCalculationEngine.calculate_bmr(60, 160, 80, "female")
        assert result > 0
    
    def test_bmr_invalid_inputs(self):
        """Test BMR calculation with invalid inputs"""
        # Negative weight
        with pytest.raises(ValueError):
            ScientificCalculationEngine.calculate_bmr(-70, 170, 25, "male")
        
        # Zero height
        with pytest.raises(ValueError):
            ScientificCalculationEngine.calculate_bmr(70, 0, 25, "male")
        
        # Invalid gender
        with pytest.raises(ValueError):
            ScientificCalculationEngine.calculate_bmr(70, 170, 25, "invalid")


class TestTDEECalculation:
    """Test cases for TDEE calculation"""
    
    def test_activity_coefficients(self):
        """Test TDEE calculation with all activity levels"""
        bmr = 1642.5
        expected_coefficients = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "active": 1.725,
            "very_active": 1.9
        }
        
        for level, coefficient in expected_coefficients.items():
            result = ScientificCalculationEngine.calculate_tdee(bmr, level)
            expected = round(bmr * coefficient, 1)
            assert result == expected, f"Failed for {level}: expected {expected}, got {result}"
    
    def test_tdee_specific_values(self):
        """Test TDEE with specific BMR values"""
        # Test with BMR = 1500
        assert ScientificCalculationEngine.calculate_tdee(1500, "sedentary") == 1800.0
        assert ScientificCalculationEngine.calculate_tdee(1500, "moderate") == 2325.0
        assert ScientificCalculationEngine.calculate_tdee(1500, "very_active") == 2850.0
    
    def test_tdee_invalid_inputs(self):
        """Test TDEE calculation with invalid inputs"""
        # Invalid activity level
        with pytest.raises(ValueError):
            ScientificCalculationEngine.calculate_tdee(1500, "invalid_level")
        
        # Negative BMR
        with pytest.raises(ValueError):
            ScientificCalculationEngine.calculate_tdee(-1500, "moderate")


class TestBodyFatEstimation:
    """Test cases for body fat percentage estimation using Tanita formula"""
    
    def test_body_fat_male(self):
        """Test body fat estimation for males"""
        # Test case: 25-year-old male, 70kg, 170cm
        # BMI = 70 / (1.7)² = 24.22
        # BF% = 1.2 × 24.22 + 0.23 × 25 - 10.8 × 1 - 5.4 = 19.3
        result = ScientificCalculationEngine.estimate_body_fat(70, 170, 25, "male")
        assert result == 19.3
        
        # Test case: 40-year-old male, 85kg, 180cm
        # BMI = 85 / (1.8)² = 26.23
        # BF% = 1.2 × 26.23 + 0.23 × 40 - 10.8 × 1 - 5.4 = 24.5
        result = ScientificCalculationEngine.estimate_body_fat(85, 180, 40, "male")
        assert result == 24.5
    
    def test_body_fat_female(self):
        """Test body fat estimation for females"""
        # Test case: 25-year-old female, 55kg, 160cm
        # BMI = 55 / (1.6)² = 21.48
        # BF% = 1.2 × 21.48 + 0.23 × 25 - 10.8 × 0 - 5.4 = 26.1
        result = ScientificCalculationEngine.estimate_body_fat(55, 160, 25, "female")
        assert result == 26.1
    
    def test_body_fat_minimum_essential(self):
        """Test that body fat doesn't go below essential levels"""
        # Very fit young male - should not go below 3%
        result = ScientificCalculationEngine.estimate_body_fat(50, 180, 20, "male")
        assert result >= 3
        
        # Very fit young female - should not go below 10%
        result = ScientificCalculationEngine.estimate_body_fat(45, 170, 20, "female")
        assert result >= 10


class TestTargetCalories:
    """Test cases for target calorie calculation"""
    
    def test_goal_adjustments(self):
        """Test calorie adjustments for different goals"""
        tdee = 2000
        
        # Muscle gain: 15% surplus
        result = ScientificCalculationEngine.calculate_target_calories(tdee, "muscle_gain")
        assert result == 2300.0
        
        # Fat loss: 20% deficit
        result = ScientificCalculationEngine.calculate_target_calories(tdee, "fat_loss")
        assert result == 1600.0
        
        # Maintenance: no change
        result = ScientificCalculationEngine.calculate_target_calories(tdee, "maintenance")
        assert result == 2000.0
    
    def test_target_calories_invalid_inputs(self):
        """Test target calorie calculation with invalid inputs"""
        with pytest.raises(ValueError):
            ScientificCalculationEngine.calculate_target_calories(2000, "invalid_goal")


class TestPFCBalance:
    """Test cases for PFC (Protein, Fat, Carbs) balance calculation"""
    
    def test_pfc_muscle_gain(self):
        """Test PFC balance for muscle gain goal"""
        calories = 2500
        result = ScientificCalculationEngine.calculate_pfc_balance(calories, "muscle_gain")
        
        # Muscle gain: P30%, F25%, C45%
        assert result["protein"]["grams"] == 187.5  # 750 cal / 4
        assert result["protein"]["calories"] == 750.0
        assert result["protein"]["percentage"] == 30.0
        
        assert result["fat"]["grams"] == 69.4  # 625 cal / 9
        assert result["fat"]["calories"] == 625.0
        assert result["fat"]["percentage"] == 25.0
        
        assert result["carbs"]["grams"] == 281.3  # 1125 cal / 4
        assert result["carbs"]["calories"] == 1125.0
        assert result["carbs"]["percentage"] == 45.0
    
    def test_pfc_fat_loss(self):
        """Test PFC balance for fat loss goal"""
        calories = 1800
        result = ScientificCalculationEngine.calculate_pfc_balance(calories, "fat_loss")
        
        # Fat loss: P40%, F30%, C30%
        assert result["protein"]["grams"] == 180.0  # 720 cal / 4
        assert result["protein"]["calories"] == 720.0
        assert result["protein"]["percentage"] == 40.0
        
        assert result["fat"]["grams"] == 60.0  # 540 cal / 9
        assert result["fat"]["calories"] == 540.0
        assert result["fat"]["percentage"] == 30.0
        
        assert result["carbs"]["grams"] == 135.0  # 540 cal / 4
        assert result["carbs"]["calories"] == 540.0
        assert result["carbs"]["percentage"] == 30.0
    
    def test_pfc_maintenance(self):
        """Test PFC balance for maintenance goal"""
        calories = 2000
        result = ScientificCalculationEngine.calculate_pfc_balance(calories, "maintenance")
        
        # Maintenance: P25%, F30%, C45%
        assert result["protein"]["grams"] == 125.0  # 500 cal / 4
        assert result["fat"]["grams"] == 66.7  # 600 cal / 9
        assert result["carbs"]["grams"] == 225.0  # 900 cal / 4


class TestCalorieSafety:
    """Test cases for calorie safety checks"""
    
    def test_safe_calorie_range(self):
        """Test safe calorie ranges"""
        bmr = 1500
        
        # 85% of BMR - should be safe
        result = ScientificCalculationEngine.check_calorie_safety(bmr, 1275)
        assert result["is_safe"] == True
        assert result["severity"] == "low"
        assert len(result["warnings"]) == 0
    
    def test_moderate_restriction(self):
        """Test moderate calorie restriction warnings"""
        bmr = 1500
        
        # 75% of BMR - moderate warning
        result = ScientificCalculationEngine.check_calorie_safety(bmr, 1125)
        assert result["is_safe"] == True
        assert result["severity"] == "medium"
        assert len(result["warnings"]) > 0
    
    def test_dangerous_restriction(self):
        """Test dangerous calorie restriction"""
        bmr = 1500
        
        # 60% of BMR - high risk
        result = ScientificCalculationEngine.check_calorie_safety(bmr, 900)
        assert result["is_safe"] == False
        assert result["severity"] == "high"
        assert "大幅に下回っています" in result["warnings"][0]
    
    def test_extreme_restriction(self):
        """Test extreme calorie restriction"""
        bmr = 1500
        
        # 40% of BMR - critical
        result = ScientificCalculationEngine.check_calorie_safety(bmr, 600)
        assert result["is_safe"] == False
        assert result["severity"] == "critical"
        assert "極度" in result["warnings"][0]
    
    def test_excessive_calories(self):
        """Test excessive calorie intake warning"""
        bmr = 1500
        
        # 350% of BMR - excessive
        result = ScientificCalculationEngine.check_calorie_safety(bmr, 5250)
        assert result["severity"] == "medium"
        assert "過剰" in result["warnings"][0]


class TestBodyFatGoals:
    """Test cases for body fat goal safety checks"""
    
    def test_healthy_body_fat_goals(self):
        """Test healthy body fat percentage goals"""
        # Healthy male goal
        result = ScientificCalculationEngine.check_body_fat_goals(15, "male")
        assert result["is_healthy"] == True
        assert result["category"] == "健康的"
        
        # Healthy female goal
        result = ScientificCalculationEngine.check_body_fat_goals(25, "female")
        assert result["is_healthy"] == True
        assert result["category"] == "健康的"
    
    def test_athletic_body_fat_goals(self):
        """Test athletic body fat percentage goals"""
        # Athletic male
        result = ScientificCalculationEngine.check_body_fat_goals(8, "male")
        assert result["is_healthy"] == True
        assert result["category"] == "アスリート"
        
        # Athletic female
        result = ScientificCalculationEngine.check_body_fat_goals(16, "female")
        assert result["is_healthy"] == True
        assert result["category"] == "アスリート"
    
    def test_dangerous_body_fat_goals(self):
        """Test dangerous body fat percentage goals"""
        # Below essential fat for male
        result = ScientificCalculationEngine.check_body_fat_goals(2, "male")
        assert result["is_healthy"] == False
        assert result["category"] == "危険"
        
        # Below essential fat for female
        result = ScientificCalculationEngine.check_body_fat_goals(8, "female")
        assert result["is_healthy"] == False
        assert result["category"] == "極度に低い"