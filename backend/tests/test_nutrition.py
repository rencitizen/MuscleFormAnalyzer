"""
Nutrition API Tests
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi import status
import io
from datetime import datetime, date

class TestNutritionAPI:
    """Test nutrition management endpoints"""
    
    @patch('firebase_admin.auth.verify_id_token')
    def test_food_recognition_single_image(self, mock_verify_token, client, test_user, test_image):
        """Test food recognition from single image"""
        mock_verify_token.return_value = {'uid': test_user.id}
        
        with open(test_image, 'rb') as f:
            response = client.post(
                "/api/nutrition/recognize",
                files={"file": ("food.jpg", f, "image/jpeg")},
                headers={"Authorization": "Bearer test_token"}
            )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "success" in data
        assert "recognized_foods" in data
        assert "processing_time" in data
    
    @patch('firebase_admin.auth.verify_id_token')
    def test_food_recognition_with_auto_save(self, mock_verify_token, client, test_user, test_image):
        """Test food recognition with automatic meal saving"""
        mock_verify_token.return_value = {'uid': test_user.id}
        
        with open(test_image, 'rb') as f:
            response = client.post(
                "/api/nutrition/recognize?save_to_meal=true&meal_type=lunch",
                files={"file": ("food.jpg", f, "image/jpeg")},
                headers={"Authorization": "Bearer test_token"}
            )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "success" in data
    
    @patch('firebase_admin.auth.verify_id_token')
    def test_food_recognition_batch(self, mock_verify_token, client, test_user, test_image):
        """Test batch food recognition"""
        mock_verify_token.return_value = {'uid': test_user.id}
        
        files = []
        for i in range(3):
            with open(test_image, 'rb') as f:
                files.append(("files", (f"food{i}.jpg", f.read(), "image/jpeg")))
        
        response = client.post(
            "/api/nutrition/recognize/batch",
            files=files,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "foods" in data
        assert data["images_processed"] <= 3
        assert "processing_time" in data
    
    @patch('firebase_admin.auth.verify_id_token')
    def test_food_recognition_invalid_file(self, mock_verify_token, client, test_user):
        """Test food recognition with invalid file type"""
        mock_verify_token.return_value = {'uid': test_user.id}
        
        fake_file = io.BytesIO(b"not an image")
        
        response = client.post(
            "/api/nutrition/recognize",
            files={"file": ("test.txt", fake_file, "text/plain")},
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "must be an image" in response.json()["detail"]
    
    @patch('firebase_admin.auth.verify_id_token')
    @patch('httpx.AsyncClient.get')
    def test_food_recognition_from_url(self, mock_http_get, mock_verify_token, client, test_user):
        """Test food recognition from URL"""
        mock_verify_token.return_value = {'uid': test_user.id}
        
        # Mock HTTP response with image data
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100  # Minimal PNG header
        mock_http_get.return_value = mock_response
        
        response = client.post(
            "/api/nutrition/recognize/url",
            json={"image_url": "https://example.com/food.jpg"},
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "success" in data
    
    @patch('firebase_admin.auth.verify_id_token')
    def test_add_meal(self, mock_verify_token, client, test_user, db_session):
        """Test adding a meal"""
        mock_verify_token.return_value = {'uid': test_user.id}
        
        # Create test food items
        from models.nutrition import Food
        food1 = Food(
            name="白米",
            name_en="White Rice",
            calories_per_100g=156,
            protein_g=2.7,
            carbs_g=35.1,
            fat_g=0.3
        )
        food2 = Food(
            name="鶏胸肉",
            name_en="Chicken Breast",
            calories_per_100g=165,
            protein_g=31.0,
            carbs_g=0,
            fat_g=3.6
        )
        db_session.add_all([food1, food2])
        db_session.commit()
        db_session.refresh(food1)
        db_session.refresh(food2)
        
        response = client.post(
            "/api/nutrition/meals",
            json={
                "meal_type": "lunch",
                "food_items": [
                    {"food_id": food1.id, "quantity": 150, "unit": "g"},
                    {"food_id": food2.id, "quantity": 100, "unit": "g"}
                ],
                "notes": "Post-workout meal"
            },
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "meal_id" in data
        assert data["total_calories"] > 0
        assert data["total_protein"] > 0
    
    @patch('firebase_admin.auth.verify_id_token')
    def test_get_nutrition_summary(self, mock_verify_token, client, test_user, db_session):
        """Test getting nutrition summary"""
        mock_verify_token.return_value = {'uid': test_user.id}
        
        # Add a meal for today
        from models.nutrition import MealEntry, Food, MealFoodItem
        
        food = Food(
            name="Test Food",
            calories_per_100g=200,
            protein_g=20,
            carbs_g=30,
            fat_g=10
        )
        db_session.add(food)
        db_session.flush()
        
        meal = MealEntry(
            user_id=test_user.id,
            meal_type="breakfast",
            consumed_at=datetime.utcnow()
        )
        db_session.add(meal)
        db_session.flush()
        
        meal_item = MealFoodItem(
            meal_id=meal.id,
            food_id=food.id,
            quantity=100,
            unit="g"
        )
        db_session.add(meal_item)
        db_session.commit()
        
        today = date.today().isoformat()
        response = client.get(
            f"/api/nutrition/summary?date={today}",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["date"] == today
        assert data["total_calories"] == 200
        assert data["total_protein"] == 20
        assert len(data["meals"]) == 1
    
    @patch('firebase_admin.auth.verify_id_token')
    def test_search_foods(self, mock_verify_token, client, test_user, db_session):
        """Test food search"""
        mock_verify_token.return_value = {'uid': test_user.id}
        
        # Add test foods
        from models.nutrition import Food
        foods = [
            Food(name="バナナ", name_en="Banana", calories_per_100g=89),
            Food(name="りんご", name_en="Apple", calories_per_100g=52),
            Food(name="オレンジ", name_en="Orange", calories_per_100g=47)
        ]
        db_session.add_all(foods)
        db_session.commit()
        
        response = client.get(
            "/api/nutrition/foods/search?q=apple",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert len(data["foods"]) == 1
        assert data["foods"][0]["name_en"] == "Apple"
    
    @patch('firebase_admin.auth.verify_id_token')
    def test_nutrition_goals(self, mock_verify_token, client, test_user, db_session):
        """Test nutrition goals management"""
        mock_verify_token.return_value = {'uid': test_user.id}
        
        # Create a goal
        from models.nutrition import NutritionGoal
        goal = NutritionGoal(
            user_id=test_user.id,
            target_calories=2000,
            target_protein=150,
            target_carbs=250,
            target_fat=65,
            activity_level="moderate",
            is_active=True
        )
        db_session.add(goal)
        db_session.commit()
        
        response = client.get(
            "/api/nutrition/goals",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["goal"]["target_calories"] == 2000
        assert data["goal"]["activity_level"] == "moderate"