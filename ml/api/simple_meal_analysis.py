import os
import json
import numpy as np
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import cv2
from typing import List, Dict
import logging

# Import calorie calculator
try:
    from ml.nutrition import CalorieCalculator
    NUTRITION_CALC_AVAILABLE = True
except ImportError:
    NUTRITION_CALC_AVAILABLE = False

meal_bp = Blueprint('meal', __name__)
logger = logging.getLogger(__name__)

# Configuration
UPLOAD_FOLDER = 'static/meal_images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class SimpleFoodRecognizer:
    def __init__(self):
        # Simplified food database with common Japanese and Western foods
        self.food_database = {
            # Rice and grain dishes
            'rice': {'ja': 'ご飯', 'en': 'Rice', 'calories_per_100g': 168},
            'sushi': {'ja': '寿司', 'en': 'Sushi', 'calories_per_100g': 150},
            'onigiri': {'ja': 'おにぎり', 'en': 'Rice Ball', 'calories_per_100g': 180},
            'ramen': {'ja': 'ラーメン', 'en': 'Ramen', 'calories_per_100g': 110},
            'udon': {'ja': 'うどん', 'en': 'Udon', 'calories_per_100g': 105},
            'soba': {'ja': 'そば', 'en': 'Soba', 'calories_per_100g': 114},
            'bread': {'ja': 'パン', 'en': 'Bread', 'calories_per_100g': 265},
            
            # Protein dishes
            'chicken': {'ja': '鶏肉', 'en': 'Chicken', 'calories_per_100g': 239},
            'beef': {'ja': '牛肉', 'en': 'Beef', 'calories_per_100g': 250},
            'pork': {'ja': '豚肉', 'en': 'Pork', 'calories_per_100g': 242},
            'fish': {'ja': '魚', 'en': 'Fish', 'calories_per_100g': 206},
            'salmon': {'ja': 'サーモン', 'en': 'Salmon', 'calories_per_100g': 208},
            'tuna': {'ja': 'マグロ', 'en': 'Tuna', 'calories_per_100g': 132},
            'egg': {'ja': '卵', 'en': 'Egg', 'calories_per_100g': 155},
            'tofu': {'ja': '豆腐', 'en': 'Tofu', 'calories_per_100g': 76},
            
            # Vegetables
            'salad': {'ja': 'サラダ', 'en': 'Salad', 'calories_per_100g': 20},
            'broccoli': {'ja': 'ブロッコリー', 'en': 'Broccoli', 'calories_per_100g': 34},
            'carrot': {'ja': 'にんじん', 'en': 'Carrot', 'calories_per_100g': 41},
            'tomato': {'ja': 'トマト', 'en': 'Tomato', 'calories_per_100g': 18},
            'cucumber': {'ja': 'きゅうり', 'en': 'Cucumber', 'calories_per_100g': 16},
            
            # Common dishes
            'curry': {'ja': 'カレー', 'en': 'Curry', 'calories_per_100g': 150},
            'tempura': {'ja': '天ぷら', 'en': 'Tempura', 'calories_per_100g': 250},
            'gyoza': {'ja': '餃子', 'en': 'Gyoza', 'calories_per_100g': 280},
            'pizza': {'ja': 'ピザ', 'en': 'Pizza', 'calories_per_100g': 285},
            'pasta': {'ja': 'パスタ', 'en': 'Pasta', 'calories_per_100g': 131},
            'hamburger': {'ja': 'ハンバーガー', 'en': 'Hamburger', 'calories_per_100g': 295},
            'sandwich': {'ja': 'サンドイッチ', 'en': 'Sandwich', 'calories_per_100g': 250},
            
            # Fruits
            'apple': {'ja': 'りんご', 'en': 'Apple', 'calories_per_100g': 52},
            'banana': {'ja': 'バナナ', 'en': 'Banana', 'calories_per_100g': 89},
            'orange': {'ja': 'オレンジ', 'en': 'Orange', 'calories_per_100g': 47},
            
            # Beverages
            'coffee': {'ja': 'コーヒー', 'en': 'Coffee', 'calories_per_100g': 2},
            'tea': {'ja': 'お茶', 'en': 'Tea', 'calories_per_100g': 1},
            'milk': {'ja': '牛乳', 'en': 'Milk', 'calories_per_100g': 61},
            
            # Snacks and desserts
            'cake': {'ja': 'ケーキ', 'en': 'Cake', 'calories_per_100g': 257},
            'ice_cream': {'ja': 'アイスクリーム', 'en': 'Ice Cream', 'calories_per_100g': 207},
            'donut': {'ja': 'ドーナツ', 'en': 'Donut', 'calories_per_100g': 452},
        }
        
        # Color-based food hints (simplified detection)
        self.color_hints = {
            'white': ['rice', 'bread', 'milk', 'tofu', 'egg', 'onigiri'],
            'brown': ['bread', 'beef', 'pork', 'curry', 'coffee'],
            'green': ['salad', 'broccoli', 'cucumber', 'tea'],
            'red': ['tomato', 'tuna', 'beef', 'apple'],
            'orange': ['carrot', 'orange', 'salmon', 'curry'],
            'yellow': ['egg', 'banana', 'curry', 'tempura'],
        }
        
    def analyze_image_colors(self, image_path: str) -> Dict[str, float]:
        """Analyze dominant colors in the image"""
        try:
            img = cv2.imread(image_path)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Resize for faster processing
            img_small = cv2.resize(img_rgb, (150, 150))
            
            # Calculate color histograms
            colors = {
                'red': np.mean(img_small[:, :, 0]),
                'green': np.mean(img_small[:, :, 1]),
                'blue': np.mean(img_small[:, :, 2])
            }
            
            # Determine dominant color category
            if colors['green'] > colors['red'] and colors['green'] > colors['blue']:
                dominant = 'green'
            elif colors['red'] > colors['green'] and colors['red'] > colors['blue']:
                if colors['red'] > 150:
                    dominant = 'red'
                else:
                    dominant = 'brown'
            elif colors['blue'] > colors['red'] and colors['blue'] > colors['green']:
                dominant = 'blue'
            elif colors['red'] > 200 and colors['green'] > 200 and colors['blue'] > 200:
                dominant = 'white'
            elif colors['red'] > 150 and colors['green'] > 100:
                dominant = 'orange'
            elif colors['red'] > 150 and colors['green'] > 150:
                dominant = 'yellow'
            else:
                dominant = 'brown'
                
            return {'dominant_color': dominant, 'colors': colors}
            
        except Exception as e:
            logger.error(f"Color analysis error: {e}")
            return {'dominant_color': 'unknown', 'colors': {}}
    
    def estimate_food_items(self, image_path: str) -> List[Dict]:
        """Estimate food items based on image analysis"""
        # Analyze colors
        color_analysis = self.analyze_image_colors(image_path)
        dominant_color = color_analysis.get('dominant_color', 'unknown')
        
        # Get potential foods based on color
        potential_foods = self.color_hints.get(dominant_color, [])
        
        # For demo purposes, return top 3 most likely foods
        # In production, use proper ML model
        food_items = []
        
        if not potential_foods:
            # Default to common foods
            potential_foods = ['rice', 'salad', 'chicken']
        
        # Create food items with estimated quantities
        for i, food_key in enumerate(potential_foods[:3]):
            if food_key in self.food_database:
                food_info = self.food_database[food_key]
                
                # Estimate quantity based on typical servings
                quantity_map = {
                    'rice': '150g',
                    'bread': '2 slices',
                    'salad': '100g',
                    'chicken': '120g',
                    'beef': '100g',
                    'fish': '100g',
                    'egg': '2 pieces',
                    'apple': '1 medium',
                    'banana': '1 medium',
                }
                
                quantity = quantity_map.get(food_key, '100g')
                
                # Calculate calories
                grams = 100  # Default
                if 'g' in quantity:
                    grams = int(quantity.replace('g', ''))
                elif food_key == 'egg':
                    grams = 100  # 2 eggs ≈ 100g
                elif food_key in ['apple', 'banana']:
                    grams = 150  # 1 medium fruit
                    
                calories = int((grams / 100) * food_info['calories_per_100g'])
                
                food_items.append({
                    'name': food_info['ja'] + ' / ' + food_info['en'],
                    'quantity': quantity,
                    'calories': calories,
                    'confidence': 0.8 - (i * 0.2)  # Decreasing confidence
                })
        
        # If no items detected, add a generic item
        if not food_items:
            food_items.append({
                'name': '不明な食品 / Unknown Food',
                'quantity': '1 serving',
                'calories': 200,
                'confidence': 0.3
            })
            
        return food_items

# Initialize recognizer and calculator
food_recognizer = SimpleFoodRecognizer()
calorie_calculator = CalorieCalculator() if NUTRITION_CALC_AVAILABLE else None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@meal_bp.route('/api/analyze-meal-image', methods=['POST'])
def analyze_meal_image():
    """Analyze uploaded meal image and identify food items"""
    try:
        # Check if image was uploaded
        if 'image' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image selected'}), 400
        
        if file and allowed_file(file.filename):
            # Save uploaded file
            filename = secure_filename(file.filename)
            timestamp = str(int(os.times().elapsed * 1000))
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            # Analyze image
            food_items = food_recognizer.estimate_food_items(filepath)
            
            # Clean up - remove uploaded file after analysis
            try:
                os.remove(filepath)
            except:
                pass
            
            return jsonify({
                'success': True,
                'foods': food_items
            })
        
        return jsonify({'error': 'Invalid file type'}), 400
        
    except Exception as e:
        logger.error(f"Meal image analysis error: {e}")
        return jsonify({'error': str(e)}), 500

@meal_bp.route('/api/meal/calculate-calories', methods=['POST'])
def calculate_calories():
    """Calculate detailed nutrition for food items"""
    try:
        data = request.get_json()
        food_items = data.get('foods', [])
        
        if NUTRITION_CALC_AVAILABLE and calorie_calculator:
            # Use advanced nutrition calculator
            result = calorie_calculator.calculate_meal_nutrition(food_items)
            return jsonify({
                'success': True,
                **result
            })
        else:
            # Fallback to simple calculation
            total_calories = 0
            for item in food_items:
                total_calories += item.get('calories', 0)
            
            return jsonify({
                'success': True,
                'foods': food_items,
                'total': {
                    'calories': total_calories,
                    'protein': 0,
                    'carbs': 0,
                    'fat': 0
                },
                'pfc_balance': {
                    'protein_ratio': 0,
                    'carbs_ratio': 0,
                    'fat_ratio': 0
                }
            })
        
    except Exception as e:
        logger.error(f"Calorie calculation error: {e}")
        return jsonify({'error': str(e)}), 500

@meal_bp.route('/api/meal/food-database', methods=['GET'])
def get_food_database():
    """Get available food database"""
    try:
        foods = []
        for key, info in food_recognizer.food_database.items():
            foods.append({
                'id': key,
                'name_ja': info['ja'],
                'name_en': info['en'],
                'calories_per_100g': info['calories_per_100g']
            })
        
        return jsonify({
            'success': True,
            'foods': foods
        })
        
    except Exception as e:
        logger.error(f"Food database error: {e}")
        return jsonify({'error': str(e)}), 500

@meal_bp.route('/api/meal/food-suggestions', methods=['GET'])
def get_food_suggestions():
    """Get food suggestions based on query"""
    try:
        query = request.args.get('q', '')
        
        if NUTRITION_CALC_AVAILABLE and calorie_calculator:
            suggestions = calorie_calculator.get_food_suggestions(query)
            return jsonify({
                'success': True,
                'suggestions': suggestions
            })
        else:
            # Return simple list
            return jsonify({
                'success': True,
                'suggestions': []
            })
    except Exception as e:
        logger.error(f"Food suggestions error: {e}")
        return jsonify({'error': str(e)}), 500

@meal_bp.route('/api/meal/daily-needs', methods=['POST'])
def calculate_daily_needs():
    """Calculate daily nutritional needs"""
    try:
        data = request.get_json()
        
        if NUTRITION_CALC_AVAILABLE and calorie_calculator:
            needs = calorie_calculator.estimate_daily_needs(
                weight_kg=data.get('weight', 70),
                height_cm=data.get('height', 170),
                age=data.get('age', 30),
                gender=data.get('gender', 'male'),
                activity_level=data.get('activity_level', 'moderate')
            )
            return jsonify({
                'success': True,
                **needs
            })
        else:
            # Return default values
            return jsonify({
                'success': True,
                'bmr': 1700,
                'daily_calories': 2500,
                'recommended_pfc': {
                    'protein': 84,
                    'carbs': 312,
                    'fat': 69
                }
            })
    except Exception as e:
        logger.error(f"Daily needs calculation error: {e}")
        return jsonify({'error': str(e)}), 500