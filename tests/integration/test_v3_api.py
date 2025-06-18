"""
Integration tests for V3 API endpoints
Tests the complete API flow including request/response validation
"""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app


client = TestClient(app)


class TestCalculationAPI:
    """Test cases for calculation endpoints"""
    
    def test_bmr_endpoint_success(self):
        """Test successful BMR calculation"""
        response = client.post("/api/v3/calculations/bmr", json={
            "weight": 70.0,
            "height": 170.0,
            "age": 25,
            "gender": "male"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["bmr"] == 1642.5
        assert data["formula"] == "Mifflin-St Jeor"
    
    def test_bmr_endpoint_female(self):
        """Test BMR calculation for female"""
        response = client.post("/api/v3/calculations/bmr", json={
            "weight": 55.0,
            "height": 160.0,
            "age": 25,
            "gender": "female"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["bmr"] == 1264.0
    
    def test_bmr_endpoint_validation(self):
        """Test BMR endpoint input validation"""
        # Invalid weight
        response = client.post("/api/v3/calculations/bmr", json={
            "weight": -70.0,
            "height": 170.0,
            "age": 25,
            "gender": "male"
        })
        assert response.status_code == 422
        
        # Invalid gender
        response = client.post("/api/v3/calculations/bmr", json={
            "weight": 70.0,
            "height": 170.0,
            "age": 25,
            "gender": "invalid"
        })
        assert response.status_code == 422
    
    def test_tdee_endpoint_success(self):
        """Test successful TDEE calculation"""
        response = client.post("/api/v3/calculations/tdee", json={
            "bmr": 1642.5,
            "activity_level": "moderate"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["tdee"] == 2545.9
        assert data["activity_coefficient"] == 1.55
    
    def test_tdee_all_activity_levels(self):
        """Test TDEE calculation for all activity levels"""
        bmr = 1500
        levels = {
            "sedentary": 1800.0,
            "light": 2062.5,
            "moderate": 2325.0,
            "active": 2587.5,
            "very_active": 2850.0
        }
        
        for level, expected_tdee in levels.items():
            response = client.post("/api/v3/calculations/tdee", json={
                "bmr": bmr,
                "activity_level": level
            })
            assert response.status_code == 200
            assert response.json()["tdee"] == expected_tdee
    
    def test_body_fat_endpoint_success(self):
        """Test successful body fat estimation"""
        response = client.post("/api/v3/calculations/body-fat", json={
            "weight": 70.0,
            "height": 170.0,
            "age": 25,
            "gender": "male"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["body_fat_percentage"] == 19.3
        assert data["bmi"] == 24.2
        assert data["formula"] == "Tanita"
    
    def test_target_calories_endpoint(self):
        """Test target calories calculation"""
        # Test muscle gain
        response = client.post("/api/v3/calculations/target-calories", json={
            "tdee": 2000.0,
            "goal": "muscle_gain"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["target_calories"] == 2300.0
        assert data["adjustment_percentage"] == 15.0
        
        # Test fat loss
        response = client.post("/api/v3/calculations/target-calories", json={
            "tdee": 2000.0,
            "goal": "fat_loss"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["target_calories"] == 1600.0
        assert data["adjustment_percentage"] == -20.0
    
    def test_calculation_chain(self):
        """Test complete calculation chain: BMR → TDEE → Target Calories"""
        # Step 1: Calculate BMR
        bmr_response = client.post("/api/v3/calculations/bmr", json={
            "weight": 75.0,
            "height": 175.0,
            "age": 30,
            "gender": "male"
        })
        assert bmr_response.status_code == 200
        bmr = bmr_response.json()["bmr"]
        
        # Step 2: Calculate TDEE
        tdee_response = client.post("/api/v3/calculations/tdee", json={
            "bmr": bmr,
            "activity_level": "moderate"
        })
        assert tdee_response.status_code == 200
        tdee = tdee_response.json()["tdee"]
        
        # Step 3: Calculate target calories
        target_response = client.post("/api/v3/calculations/target-calories", json={
            "tdee": tdee,
            "goal": "muscle_gain"
        })
        assert target_response.status_code == 200
        target_calories = target_response.json()["target_calories"]
        
        # Verify the chain
        assert target_calories > tdee  # Should be higher for muscle gain


class TestNutritionAPI:
    """Test cases for nutrition endpoints"""
    
    def test_pfc_balance_endpoint(self):
        """Test PFC balance calculation"""
        response = client.post("/api/v3/nutrition/pfc-balance", json={
            "calories": 2500,
            "goal": "muscle_gain"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Check protein (30% for muscle gain)
        assert data["protein"]["grams"] == 187.5
        assert data["protein"]["calories"] == 750.0
        assert data["protein"]["percentage"] == 30.0
        
        # Check fat (25% for muscle gain)
        assert data["fat"]["grams"] == 69.4
        assert data["fat"]["calories"] == 625.0
        assert data["fat"]["percentage"] == 25.0
        
        # Check carbs (45% for muscle gain)
        assert data["carbs"]["grams"] == 281.3
        assert data["carbs"]["calories"] == 1125.0
        assert data["carbs"]["percentage"] == 45.0
    
    def test_micronutrients_endpoint(self):
        """Test micronutrient recommendations endpoint"""
        response = client.get("/api/v3/nutrition/micronutrients")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "vitamins" in data
        assert "minerals" in data
        assert "notes" in data
        
        # Check that we have some vitamins
        assert len(data["vitamins"]) > 0
        vitamin_d = next((v for v in data["vitamins"] if v["name"] == "ビタミンD"), None)
        assert vitamin_d is not None
        assert vitamin_d["unit"] == "μg"
        
        # Check that we have some minerals
        assert len(data["minerals"]) > 0
        zinc = next((m for m in data["minerals"] if m["name"] == "亜鉛"), None)
        assert zinc is not None
    
    def test_high_protein_foods_endpoint(self):
        """Test high protein foods database endpoint"""
        # Test without category filter
        response = client.get("/api/v3/nutrition/high-protein-foods")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["foods"]) > 0
        assert len(data["categories"]) > 0
        
        # Test with category filter
        response = client.get("/api/v3/nutrition/high-protein-foods?category=animal")
        assert response.status_code == 200
        data = response.json()
        
        # All foods should be from animal category
        for food in data["foods"]:
            assert food["category"] == "animal"
        
        # Test with invalid category
        response = client.get("/api/v3/nutrition/high-protein-foods?category=invalid")
        assert response.status_code == 404


class TestSafetyAPI:
    """Test cases for safety check endpoints"""
    
    def test_calorie_safety_check_safe(self):
        """Test calorie safety check with safe values"""
        response = client.post("/api/v3/safety/calorie-check", json={
            "bmr": 1500,
            "target_calories": 1400
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_safe"] == True
        assert data["percentage_of_bmr"] == 93.3
        assert data["severity"] == "low"
    
    def test_calorie_safety_check_warning(self):
        """Test calorie safety check with warning level"""
        response = client.post("/api/v3/safety/calorie-check", json={
            "bmr": 1500,
            "target_calories": 1125  # 75% of BMR
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_safe"] == True
        assert data["severity"] == "medium"
        assert len(data["warnings"]) > 0
    
    def test_calorie_safety_check_dangerous(self):
        """Test calorie safety check with dangerous values"""
        response = client.post("/api/v3/safety/calorie-check", json={
            "bmr": 1500,
            "target_calories": 600  # 40% of BMR
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_safe"] == False
        assert data["severity"] == "critical"
        assert "極度" in data["warnings"][0]
    
    def test_body_fat_check_healthy(self):
        """Test body fat goal check with healthy values"""
        response = client.post("/api/v3/safety/body-fat-check", json={
            "target_body_fat": 15,
            "gender": "male"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_safe"] == True
        assert len(data["warnings"]) == 0
    
    def test_body_fat_check_dangerous(self):
        """Test body fat goal check with dangerous values"""
        response = client.post("/api/v3/safety/body-fat-check", json={
            "target_body_fat": 2,
            "gender": "male"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_safe"] == False
        assert data["severity"] == "critical"
        assert len(data["warnings"]) > 0
    
    def test_comprehensive_health_warnings(self):
        """Test comprehensive health warnings endpoint"""
        response = client.post("/api/v3/safety/health-warnings", json={
            "weight": 70,
            "height": 170,
            "age": 25,
            "gender": "male",
            "target_calories": 1200,  # Low calories
            "target_body_fat": 5,     # Low body fat
            "activity_level": "moderate",
            "goal": "fat_loss",
            "medical_conditions": []
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["overall_risk_level"] in ["high", "critical"]
        assert "calorie_intake" in data["categories_checked"]
        assert "body_fat_goal" in data["categories_checked"]
        assert len(data["warnings"]) > 0
        assert len(data["recommendations"]) > 0


class TestAPIErrors:
    """Test cases for API error handling"""
    
    def test_404_endpoint(self):
        """Test 404 for non-existent endpoint"""
        response = client.get("/api/v3/nonexistent")
        assert response.status_code == 404
    
    def test_invalid_json(self):
        """Test handling of invalid JSON"""
        response = client.post(
            "/api/v3/calculations/bmr",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [400, 422]
    
    def test_missing_required_fields(self):
        """Test missing required fields"""
        response = client.post("/api/v3/calculations/bmr", json={
            "weight": 70.0
            # Missing height, age, gender
        })
        assert response.status_code == 422