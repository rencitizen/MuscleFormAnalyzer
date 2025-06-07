import os
import json
import numpy as np
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import cv2
import tensorflow as tf
import tensorflow_hub as hub
from typing import List, Dict, Tuple

meal_bp = Blueprint('meal', __name__)

# Configuration
UPLOAD_FOLDER = 'static/meal_images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class FoodRecognizer:
    def __init__(self):
        # Load a pre-trained model for food recognition
        # Using MobileNetV2 for feature extraction
        self.model = tf.keras.applications.MobileNetV2(
            weights='imagenet',
            include_top=True,
            input_shape=(224, 224, 3)
        )
        
        # Load ImageNet class names
        self.load_food_mapping()
        
    def load_food_mapping(self):
        # Map ImageNet classes to food items
        # This is a simplified mapping - in production, use a dedicated food model
        self.food_classes = {
            'pizza': ['pizza', 'pizza, pizza pie'],
            'hamburger': ['hamburger', 'cheeseburger'],
            'hot_dog': ['hotdog', 'hot dog', 'red hot'],
            'french_fries': ['french fries', 'fries'],
            'apple': ['Granny Smith', 'apple'],
            'banana': ['banana'],
            'orange': ['orange'],
            'broccoli': ['broccoli'],
            'carrot': ['carrot'],
            'sandwich': ['sandwich'],
            'coffee': ['espresso', 'coffee', 'cappuccino'],
            'ice_cream': ['ice cream', 'ice lolly'],
            'donut': ['doughnut', 'donut'],
            'cake': ['cake', 'layer cake'],
            'bread': ['bread', 'loaf of bread', 'French loaf'],
        }
        
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """Preprocess image for model input"""
        img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (224, 224))
        img = tf.keras.applications.mobilenet_v2.preprocess_input(img)
        return np.expand_dims(img, axis=0)
    
    def estimate_quantity(self, food_name: str, confidence: float) -> str:
        """Estimate quantity based on food type and confidence"""
        # Simple quantity estimation - in production, use object detection for size
        quantity_map = {
            'pizza': '1 slice',
            'hamburger': '1 burger',
            'hot_dog': '1 hot dog',
            'french_fries': '1 medium serving',
            'apple': '1 medium',
            'banana': '1 medium',
            'orange': '1 medium',
            'broccoli': '1 cup',
            'carrot': '1 medium',
            'sandwich': '1 sandwich',
            'coffee': '1 cup',
            'ice_cream': '1 scoop',
            'donut': '1 donut',
            'cake': '1 slice',
            'bread': '2 slices',
        }
        
        # Adjust quantity based on confidence
        base_quantity = quantity_map.get(food_name, '1 serving')
        if confidence < 0.5:
            return f"~{base_quantity}"
        return base_quantity
    
    def recognize_food(self, image_path: str) -> List[Dict[str, str]]:
        """Recognize food items in the image"""
        # Preprocess image
        processed_img = self.preprocess_image(image_path)
        
        # Get predictions
        predictions = self.model.predict(processed_img)
        decoded_predictions = tf.keras.applications.mobilenet_v2.decode_predictions(predictions, top=5)[0]
        
        # Extract food items
        food_items = []
        seen_foods = set()
        
        for _, label, confidence in decoded_predictions:
            # Check if this prediction matches any food category
            for food_name, keywords in self.food_classes.items():
                if any(keyword.lower() in label.lower() for keyword in keywords):
                    if food_name not in seen_foods and confidence > 0.1:
                        seen_foods.add(food_name)
                        quantity = self.estimate_quantity(food_name, confidence)
                        food_items.append({
                            'name': food_name.replace('_', ' ').title(),
                            'quantity': quantity,
                            'confidence': float(confidence)
                        })
                    break
        
        # If no food items detected, return a generic result
        if not food_items:
            food_items.append({
                'name': 'Unidentified food',
                'quantity': '1 serving',
                'confidence': 0.0
            })
        
        return food_items

# Initialize food recognizer
food_recognizer = FoodRecognizer()

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
            food_items = food_recognizer.recognize_food(filepath)
            
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
        return jsonify({'error': str(e)}), 500

@meal_bp.route('/api/meal/calculate-calories', methods=['POST'])
def calculate_calories():
    """Calculate calories for identified food items"""
    try:
        data = request.get_json()
        food_items = data.get('foods', [])
        
        # Simple calorie database (calories per standard serving)
        calorie_db = {
            'Pizza': 285,  # per slice
            'Hamburger': 540,  # per burger
            'Hot Dog': 150,  # per hot dog
            'French Fries': 365,  # medium serving
            'Apple': 95,  # medium
            'Banana': 105,  # medium
            'Orange': 62,  # medium
            'Broccoli': 55,  # per cup
            'Carrot': 25,  # medium
            'Sandwich': 350,  # average
            'Coffee': 2,  # per cup (black)
            'Ice Cream': 137,  # per scoop
            'Donut': 253,  # per donut
            'Cake': 257,  # per slice
            'Bread': 79,  # per slice (x2 = 158)
        }
        
        # Calculate calories for each item
        total_calories = 0
        items_with_calories = []
        
        for item in food_items:
            food_name = item['name']
            quantity = item['quantity']
            
            # Get base calories
            base_calories = calorie_db.get(food_name, 100)  # Default 100 if not found
            
            # Adjust for quantity (simple parsing)
            multiplier = 1.0
            if '2' in quantity:
                multiplier = 2.0
            elif '1/2' in quantity or 'half' in quantity:
                multiplier = 0.5
            
            item_calories = int(base_calories * multiplier)
            total_calories += item_calories
            
            items_with_calories.append({
                **item,
                'calories': item_calories
            })
        
        return jsonify({
            'success': True,
            'foods': items_with_calories,
            'total_calories': total_calories
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500