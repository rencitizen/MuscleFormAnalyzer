"""
高度な食品認識モデル
複数食品の同時認識と量推定機能を持つ
"""
import numpy as np
import cv2
from typing import List, Dict, Tuple, Optional
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class FoodDetection:
    """食品検出結果"""
    name: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    estimated_grams: float
    nutrition_per_100g: Dict[str, float]

class AdvancedFoodRecognizer:
    """高度な食品認識エンジン"""
    
    def __init__(self):
        # 食品カテゴリと典型的なサイズ（参照用）
        self.food_references = {
            'rice_bowl': {
                'typical_diameter_cm': 12,
                'typical_grams': 150,
                'density': 0.8  # g/cm³
            },
            'bread_slice': {
                'typical_area_cm2': 100,
                'typical_grams': 30,
                'thickness_cm': 1.2
            },
            'apple': {
                'typical_diameter_cm': 7,
                'typical_grams': 180
            },
            'chicken_breast': {
                'typical_area_cm2': 80,
                'typical_grams': 120,
                'thickness_cm': 2.5
            }
        }
        
        # セグメンテーションモデル（簡易版）
        self.color_ranges = {
            'rice': {
                'lower': np.array([0, 0, 200]),
                'upper': np.array([180, 30, 255]),
                'hsv': False
            },
            'vegetables': {
                'lower': np.array([35, 40, 40]),
                'upper': np.array([85, 255, 255]),
                'hsv': True
            },
            'meat': {
                'lower': np.array([0, 50, 50]),
                'upper': np.array([20, 255, 255]),
                'hsv': True
            },
            'bread': {
                'lower': np.array([15, 30, 100]),
                'upper': np.array([30, 100, 200]),
                'hsv': True
            }
        }
    
    def detect_plate(self, image: np.ndarray) -> Optional[Tuple[int, int]]:
        """
        皿を検出してサイズ参照を取得
        Returns: (diameter_pixels, center_point)
        """
        # 円形の皿を検出（Hough変換）
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        circles = cv2.HoughCircles(
            gray,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=100,
            param1=50,
            param2=30,
            minRadius=50,
            maxRadius=300
        )
        
        if circles is not None:
            circles = np.uint16(np.around(circles))
            # 最大の円を皿として選択
            largest_circle = max(circles[0], key=lambda c: c[2])
            return int(largest_circle[2] * 2), (int(largest_circle[0]), int(largest_circle[1]))
        
        # 皿が見つからない場合は画像幅の60%を仮定
        return int(image.shape[1] * 0.6), (image.shape[1] // 2, image.shape[0] // 2)
    
    def segment_food_regions(self, image: np.ndarray) -> List[Dict]:
        """
        食品領域をセグメント化
        """
        regions = []
        height, width = image.shape[:2]
        
        # HSV変換
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        for food_type, color_range in self.color_ranges.items():
            # マスク作成
            if color_range['hsv']:
                mask = cv2.inRange(hsv, color_range['lower'], color_range['upper'])
            else:
                mask = cv2.inRange(image, color_range['lower'], color_range['upper'])
            
            # ノイズ除去
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            
            # 輪郭検出
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 1000:  # 最小面積フィルタ
                    x, y, w, h = cv2.boundingRect(contour)
                    regions.append({
                        'type': food_type,
                        'bbox': (x, y, w, h),
                        'area': area,
                        'contour': contour
                    })
        
        return regions
    
    def estimate_volume(self, region: Dict, plate_diameter_px: int) -> float:
        """
        領域から体積を推定（cm³）
        """
        # 標準的な皿のサイズ（25cm）を基準に変換
        STANDARD_PLATE_CM = 25
        px_to_cm = STANDARD_PLATE_CM / plate_diameter_px
        
        area_cm2 = region['area'] * (px_to_cm ** 2)
        
        # 食品タイプに応じた高さ推定
        height_estimates = {
            'rice': 3.0,  # ご飯の盛り高さ
            'vegetables': 2.0,
            'meat': 2.5,
            'bread': 1.5
        }
        
        estimated_height = height_estimates.get(region['type'], 2.0)
        volume_cm3 = area_cm2 * estimated_height * 0.7  # 形状係数
        
        return volume_cm3
    
    def classify_food_detailed(self, image: np.ndarray, region: Dict) -> str:
        """
        領域内の食品を詳細分類
        """
        x, y, w, h = region['bbox']
        roi = image[y:y+h, x:x+w]
        
        # 色とテクスチャ特徴を分析
        mean_color = cv2.mean(roi)[:3]
        
        # 簡易的な分類ルール
        food_mapping = {
            'rice': ['white_rice', 'fried_rice', 'mixed_rice'],
            'vegetables': ['salad', 'broccoli', 'carrot', 'spinach'],
            'meat': ['chicken', 'beef', 'pork', 'fish'],
            'bread': ['white_bread', 'whole_wheat', 'toast']
        }
        
        # ここでは最初の候補を返す（実際はより高度な分類を実装）
        base_type = region['type']
        return food_mapping.get(base_type, [base_type])[0]
    
    def get_nutrition_data(self, food_name: str) -> Dict[str, float]:
        """
        食品の栄養データを取得
        """
        # 拡張栄養データベース
        nutrition_db = {
            'white_rice': {'calories': 168, 'protein': 2.5, 'carbs': 37.1, 'fat': 0.3},
            'chicken': {'calories': 165, 'protein': 31.0, 'carbs': 0, 'fat': 3.6},
            'salad': {'calories': 20, 'protein': 1.2, 'carbs': 3.8, 'fat': 0.2},
            'broccoli': {'calories': 34, 'protein': 2.8, 'carbs': 6.6, 'fat': 0.4},
            'white_bread': {'calories': 265, 'protein': 9.0, 'carbs': 49.0, 'fat': 3.2},
            'beef': {'calories': 250, 'protein': 26.1, 'carbs': 0, 'fat': 15.5},
            'fish': {'calories': 206, 'protein': 22.0, 'carbs': 0, 'fat': 12.0}
        }
        
        return nutrition_db.get(food_name, {
            'calories': 100, 'protein': 5, 'carbs': 15, 'fat': 3
        })
    
    def recognize_multiple_foods(self, image_path: str) -> List[FoodDetection]:
        """
        画像から複数の食品を認識
        """
        # 画像読み込み
        image = cv2.imread(image_path)
        if image is None:
            return []
        
        # 皿の検出（サイズ参照）
        plate_diameter, _ = self.detect_plate(image)
        
        # 食品領域のセグメント化
        regions = self.segment_food_regions(image)
        
        # 各領域を分析
        detections = []
        for region in regions:
            # 詳細分類
            food_name = self.classify_food_detailed(image, region)
            
            # 体積推定
            volume_cm3 = self.estimate_volume(region, plate_diameter)
            
            # 重量推定（食品密度を使用）
            density = 0.8  # デフォルト密度
            if 'rice' in food_name:
                density = 0.8
            elif 'meat' in food_name or 'chicken' in food_name:
                density = 1.0
            elif 'vegetable' in food_name or 'salad' in food_name:
                density = 0.3
            
            estimated_grams = volume_cm3 * density
            
            # 栄養データ取得
            nutrition = self.get_nutrition_data(food_name)
            
            detections.append(FoodDetection(
                name=food_name,
                confidence=0.75,  # 簡易版なので固定値
                bbox=region['bbox'],
                estimated_grams=round(estimated_grams, 1),
                nutrition_per_100g=nutrition
            ))
        
        return detections
    
    def estimate_total_calories(self, detections: List[FoodDetection]) -> Dict:
        """
        検出された食品の総カロリーと栄養を計算
        """
        total = {
            'calories': 0,
            'protein': 0,
            'carbs': 0,
            'fat': 0,
            'items': []
        }
        
        for detection in detections:
            multiplier = detection.estimated_grams / 100
            item_nutrition = {
                'name': detection.name,
                'grams': detection.estimated_grams,
                'calories': round(detection.nutrition_per_100g['calories'] * multiplier),
                'protein': round(detection.nutrition_per_100g['protein'] * multiplier, 1),
                'carbs': round(detection.nutrition_per_100g['carbs'] * multiplier, 1),
                'fat': round(detection.nutrition_per_100g['fat'] * multiplier, 1)
            }
            
            total['calories'] += item_nutrition['calories']
            total['protein'] += item_nutrition['protein']
            total['carbs'] += item_nutrition['carbs']
            total['fat'] += item_nutrition['fat']
            total['items'].append(item_nutrition)
        
        return total