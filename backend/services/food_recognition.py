"""
Food Recognition Service
AI-powered food recognition and nutrition estimation
"""
import logging
from typing import Optional, List, Dict, Tuple
import cv2
import numpy as np
from dataclasses import dataclass
import json
import os
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class FoodDetection:
    """Represents a detected food item"""
    name: str
    name_ja: str
    confidence: float
    bounding_box: Tuple[float, float, float, float]  # x1, y1, x2, y2 (normalized)
    estimated_weight_g: float
    nutrition_per_100g: Dict[str, float]

class FoodRecognitionService:
    def __init__(self):
        self.model = None
        self.food_database = self._load_food_database()
        self.portion_estimator = PortionEstimator()
        
    def _load_food_database(self) -> Dict:
        """Load Japanese food nutrition database"""
        # In production, this would load from a comprehensive database
        # For now, using common Japanese foods
        return {
            "rice": {
                "name": "Rice",
                "name_ja": "白米",
                "category": "grains",
                "nutrition_per_100g": {
                    "calories": 156,
                    "protein": 2.7,
                    "carbs": 35.1,
                    "fat": 0.3,
                    "fiber": 0.3
                },
                "typical_portion_g": 150
            },
            "miso_soup": {
                "name": "Miso Soup",
                "name_ja": "味噌汁",
                "category": "soup",
                "nutrition_per_100g": {
                    "calories": 40,
                    "protein": 3.4,
                    "carbs": 5.8,
                    "fat": 1.2,
                    "fiber": 0.9
                },
                "typical_portion_g": 200
            },
            "salmon": {
                "name": "Grilled Salmon",
                "name_ja": "焼き鮭",
                "category": "protein",
                "nutrition_per_100g": {
                    "calories": 208,
                    "protein": 22.5,
                    "carbs": 0,
                    "fat": 12.5,
                    "fiber": 0
                },
                "typical_portion_g": 100
            },
            "tofu": {
                "name": "Tofu",
                "name_ja": "豆腐",
                "category": "protein",
                "nutrition_per_100g": {
                    "calories": 76,
                    "protein": 8.1,
                    "carbs": 1.9,
                    "fat": 4.8,
                    "fiber": 0.4
                },
                "typical_portion_g": 150
            },
            "soba": {
                "name": "Soba Noodles",
                "name_ja": "そば",
                "category": "grains",
                "nutrition_per_100g": {
                    "calories": 114,
                    "protein": 4.8,
                    "carbs": 24.4,
                    "fat": 0.7,
                    "fiber": 2.0
                },
                "typical_portion_g": 200
            },
            "chicken_teriyaki": {
                "name": "Chicken Teriyaki",
                "name_ja": "照り焼きチキン",
                "category": "protein",
                "nutrition_per_100g": {
                    "calories": 165,
                    "protein": 21.0,
                    "carbs": 8.0,
                    "fat": 6.0,
                    "fiber": 0.2
                },
                "typical_portion_g": 120
            },
            "edamame": {
                "name": "Edamame",
                "name_ja": "枝豆",
                "category": "vegetable",
                "nutrition_per_100g": {
                    "calories": 121,
                    "protein": 11.9,
                    "carbs": 8.9,
                    "fat": 5.2,
                    "fiber": 5.2
                },
                "typical_portion_g": 100
            },
            "sushi_roll": {
                "name": "Sushi Roll",
                "name_ja": "巻き寿司",
                "category": "mixed",
                "nutrition_per_100g": {
                    "calories": 150,
                    "protein": 5.5,
                    "carbs": 28.0,
                    "fat": 2.0,
                    "fiber": 1.0
                },
                "typical_portion_g": 180
            }
        }
    
    async def recognize_food(self, image: np.ndarray) -> Dict:
        """
        Recognize food items in image
        
        Args:
            image: OpenCV image array
            
        Returns:
            Dictionary with recognition results
        """
        try:
            # Preprocess image
            processed_image = self._preprocess_image(image)
            
            # Detect food items using object detection
            detections = await self._detect_food_items(processed_image)
            
            if not detections:
                return {
                    "success": True,
                    "foods": [],
                    "confidence": 0.0,
                    "message": "No food items detected in image"
                }
            
            # Estimate portions for each detection
            food_results = []
            for detection in detections:
                # Estimate portion size
                portion_g = self.portion_estimator.estimate_portion(
                    detection, 
                    image.shape[:2]
                )
                
                # Calculate nutrition
                nutrition = self._calculate_nutrition(
                    detection.nutrition_per_100g, 
                    portion_g
                )
                
                food_results.append({
                    "name": detection.name,
                    "name_ja": detection.name_ja,
                    "confidence": float(detection.confidence),
                    "estimated_quantity": float(portion_g),
                    "unit": "g",
                    "bounding_box": list(detection.bounding_box),
                    "nutrition": nutrition
                })
            
            # Calculate overall confidence
            avg_confidence = sum(d.confidence for d in detections) / len(detections)
            
            return {
                "success": True,
                "foods": food_results,
                "confidence": float(avg_confidence),
                "detection_count": len(detections)
            }
            
        except Exception as e:
            logger.error(f"Food recognition error: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "foods": []
            }
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for food detection"""
        # Resize if too large
        max_size = 1024
        height, width = image.shape[:2]
        
        if max(height, width) > max_size:
            scale = max_size / max(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            image = cv2.resize(image, (new_width, new_height))
        
        # Enhance image quality
        # Apply CLAHE for better contrast
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        
        return enhanced
    
    async def _detect_food_items(self, image: np.ndarray) -> List[FoodDetection]:
        """
        Detect food items in image
        In production, this would use a trained YOLO/R-CNN model
        """
        # Simulate ML model detection with basic image processing
        detections = []
        
        # Convert to HSV for color-based detection
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Detect different food types based on color and shape
        # This is a simplified approach - real implementation would use ML
        
        # Detect rice (white/light colored regions)
        rice_mask = self._detect_rice(hsv)
        if np.sum(rice_mask) > 1000:
            bbox = self._get_bbox_from_mask(rice_mask, image.shape)
            if bbox:
                food_info = self.food_database["rice"]
                detections.append(FoodDetection(
                    name=food_info["name"],
                    name_ja=food_info["name_ja"],
                    confidence=0.85,
                    bounding_box=bbox,
                    estimated_weight_g=food_info["typical_portion_g"],
                    nutrition_per_100g=food_info["nutrition_per_100g"]
                ))
        
        # Detect protein sources (darker regions with specific textures)
        protein_mask = self._detect_protein(hsv, image)
        if np.sum(protein_mask) > 1000:
            bbox = self._get_bbox_from_mask(protein_mask, image.shape)
            if bbox:
                # Determine specific protein type based on color/texture
                protein_type = self._classify_protein(image, bbox)
                if protein_type in self.food_database:
                    food_info = self.food_database[protein_type]
                    detections.append(FoodDetection(
                        name=food_info["name"],
                        name_ja=food_info["name_ja"],
                        confidence=0.75,
                        bounding_box=bbox,
                        estimated_weight_g=food_info["typical_portion_g"],
                        nutrition_per_100g=food_info["nutrition_per_100g"]
                    ))
        
        return detections
    
    def _detect_rice(self, hsv: np.ndarray) -> np.ndarray:
        """Detect rice regions in HSV image"""
        # Rice typically appears as white/light gray
        lower_white = np.array([0, 0, 150])
        upper_white = np.array([180, 30, 255])
        
        mask = cv2.inRange(hsv, lower_white, upper_white)
        
        # Morphological operations to clean up
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        return mask
    
    def _detect_protein(self, hsv: np.ndarray, bgr: np.ndarray) -> np.ndarray:
        """Detect protein sources (meat, fish, tofu)"""
        # Brown/orange colors for cooked meat/fish
        lower_brown = np.array([10, 50, 50])
        upper_brown = np.array([25, 255, 255])
        
        mask = cv2.inRange(hsv, lower_brown, upper_brown)
        
        # Also detect lighter proteins (tofu, chicken)
        lower_light = np.array([0, 0, 100])
        upper_light = np.array([180, 50, 200])
        mask_light = cv2.inRange(hsv, lower_light, upper_light)
        
        # Combine masks
        mask = cv2.bitwise_or(mask, mask_light)
        
        # Apply texture filter to distinguish from other foods
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        mask = cv2.bitwise_and(mask, edges)
        
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        return mask
    
    def _get_bbox_from_mask(self, mask: np.ndarray, image_shape: Tuple) -> Optional[Tuple[float, float, float, float]]:
        """Get normalized bounding box from mask"""
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None
        
        # Get largest contour
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        
        # Normalize coordinates
        height, width = image_shape[:2]
        x1 = x / width
        y1 = y / height
        x2 = (x + w) / width
        y2 = (y + h) / height
        
        return (x1, y1, x2, y2)
    
    def _classify_protein(self, image: np.ndarray, bbox: Tuple[float, float, float, float]) -> str:
        """Classify type of protein based on color and texture"""
        h, w = image.shape[:2]
        x1, y1, x2, y2 = bbox
        
        # Extract ROI
        roi = image[int(y1*h):int(y2*h), int(x1*w):int(x2*w)]
        
        if roi.size == 0:
            return "chicken_teriyaki"  # Default
        
        # Analyze color
        hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        avg_hue = np.mean(hsv_roi[:, :, 0])
        avg_saturation = np.mean(hsv_roi[:, :, 1])
        avg_value = np.mean(hsv_roi[:, :, 2])
        
        # Simple classification based on color
        if avg_value > 200 and avg_saturation < 50:
            return "tofu"  # Light colored, low saturation
        elif 10 < avg_hue < 25 and avg_saturation > 100:
            return "salmon"  # Orange-ish color
        else:
            return "chicken_teriyaki"  # Default for brown proteins
    
    def _calculate_nutrition(self, nutrition_per_100g: Dict[str, float], portion_g: float) -> Dict[str, float]:
        """Calculate nutrition for given portion size"""
        factor = portion_g / 100.0
        return {
            key: round(value * factor, 1)
            for key, value in nutrition_per_100g.items()
        }

class PortionEstimator:
    """Estimates food portion sizes from images"""
    
    def __init__(self):
        # Reference sizes for common objects (in pixels at standard distance)
        self.reference_sizes = {
            "plate": 250,  # Standard dinner plate ~25cm
            "bowl": 150,   # Standard rice bowl ~15cm
            "chopsticks": 230,  # Standard chopsticks ~23cm
        }
    
    def estimate_portion(self, detection: FoodDetection, image_shape: Tuple[int, int]) -> float:
        """
        Estimate portion size in grams
        
        Args:
            detection: Food detection object
            image_shape: (height, width) of image
            
        Returns:
            Estimated weight in grams
        """
        # Get bounding box area
        x1, y1, x2, y2 = detection.bounding_box
        bbox_width = (x2 - x1) * image_shape[1]
        bbox_height = (y2 - y1) * image_shape[0]
        bbox_area = bbox_width * bbox_height
        
        # Estimate based on typical serving sizes and visual area
        # This is simplified - real implementation would use depth estimation
        # or reference objects for scale
        
        # Base estimation on category and visual size
        if "rice" in detection.name.lower():
            # Rice bowl typically 150-200g
            portion_factor = min(bbox_area / (image_shape[0] * image_shape[1] * 0.1), 1.5)
            return 150 * portion_factor
        
        elif any(protein in detection.name.lower() for protein in ["chicken", "salmon", "fish"]):
            # Protein portions typically 100-150g
            portion_factor = min(bbox_area / (image_shape[0] * image_shape[1] * 0.08), 1.5)
            return 120 * portion_factor
        
        elif "tofu" in detection.name.lower():
            # Tofu portions typically 100-200g
            portion_factor = min(bbox_area / (image_shape[0] * image_shape[1] * 0.1), 2.0)
            return 150 * portion_factor
        
        else:
            # Default estimation
            typical_portion = detection.estimated_weight_g
            portion_factor = min(bbox_area / (image_shape[0] * image_shape[1] * 0.1), 1.5)
            return typical_portion * portion_factor