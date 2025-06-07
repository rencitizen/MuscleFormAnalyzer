"""
カロリー計算と栄養素分析モジュール
"""
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import re

@dataclass
class NutritionInfo:
    """栄養情報データクラス"""
    calories: float
    protein: float
    carbs: float
    fat: float
    fiber: float = 0.0
    sodium: float = 0.0

class CalorieCalculator:
    """カロリー計算と栄養素分析クラス"""
    
    def __init__(self):
        # 拡張された食品データベース（100gあたりの栄養素）
        self.food_database = {
            # 主食類
            'ご飯': {'cal_per_100g': 168, 'protein': 2.5, 'carbs': 37.1, 'fat': 0.3, 'fiber': 0.3},
            '白米': {'cal_per_100g': 168, 'protein': 2.5, 'carbs': 37.1, 'fat': 0.3, 'fiber': 0.3},
            '玄米': {'cal_per_100g': 165, 'protein': 2.8, 'carbs': 35.6, 'fat': 1.0, 'fiber': 1.4},
            'パン': {'cal_per_100g': 264, 'protein': 9.3, 'carbs': 46.7, 'fat': 4.4, 'fiber': 2.3},
            '食パン': {'cal_per_100g': 264, 'protein': 9.3, 'carbs': 46.7, 'fat': 4.4, 'fiber': 2.3},
            'うどん': {'cal_per_100g': 105, 'protein': 2.6, 'carbs': 21.6, 'fat': 0.4, 'fiber': 0.8},
            'そば': {'cal_per_100g': 114, 'protein': 4.8, 'carbs': 22.1, 'fat': 0.7, 'fiber': 2.0},
            'パスタ': {'cal_per_100g': 165, 'protein': 5.4, 'carbs': 32.2, 'fat': 0.9, 'fiber': 1.7},
            'ラーメン': {'cal_per_100g': 445, 'protein': 10.7, 'carbs': 55.7, 'fat': 19.1, 'fiber': 2.3},
            
            # タンパク質源
            '鶏肉': {'cal_per_100g': 165, 'protein': 31.0, 'carbs': 0.0, 'fat': 3.6, 'fiber': 0.0},
            '鶏胸肉': {'cal_per_100g': 165, 'protein': 31.0, 'carbs': 0.0, 'fat': 3.6, 'fiber': 0.0},
            '鶏もも肉': {'cal_per_100g': 204, 'protein': 16.2, 'carbs': 0.0, 'fat': 14.0, 'fiber': 0.0},
            '牛肉': {'cal_per_100g': 250, 'protein': 26.1, 'carbs': 0.0, 'fat': 15.5, 'fiber': 0.0},
            '豚肉': {'cal_per_100g': 242, 'protein': 14.2, 'carbs': 0.2, 'fat': 19.3, 'fiber': 0.0},
            '魚': {'cal_per_100g': 206, 'protein': 22.0, 'carbs': 0.0, 'fat': 12.0, 'fiber': 0.0},
            'サーモン': {'cal_per_100g': 208, 'protein': 20.4, 'carbs': 0.0, 'fat': 13.4, 'fiber': 0.0},
            'マグロ': {'cal_per_100g': 132, 'protein': 29.5, 'carbs': 0.1, 'fat': 0.5, 'fiber': 0.0},
            '卵': {'cal_per_100g': 155, 'protein': 12.6, 'carbs': 1.1, 'fat': 10.6, 'fiber': 0.0},
            '豆腐': {'cal_per_100g': 76, 'protein': 8.1, 'carbs': 1.9, 'fat': 4.8, 'fiber': 0.4},
            '納豆': {'cal_per_100g': 200, 'protein': 16.5, 'carbs': 12.1, 'fat': 10.0, 'fiber': 6.7},
            
            # 野菜類
            'ブロッコリー': {'cal_per_100g': 34, 'protein': 2.8, 'carbs': 6.6, 'fat': 0.4, 'fiber': 2.6},
            'ほうれん草': {'cal_per_100g': 23, 'protein': 2.9, 'carbs': 3.6, 'fat': 0.4, 'fiber': 2.2},
            'トマト': {'cal_per_100g': 18, 'protein': 0.9, 'carbs': 3.9, 'fat': 0.2, 'fiber': 1.2},
            'きゅうり': {'cal_per_100g': 16, 'protein': 0.7, 'carbs': 3.6, 'fat': 0.1, 'fiber': 0.5},
            'レタス': {'cal_per_100g': 15, 'protein': 0.9, 'carbs': 2.9, 'fat': 0.2, 'fiber': 1.3},
            'キャベツ': {'cal_per_100g': 25, 'protein': 1.3, 'carbs': 5.8, 'fat': 0.1, 'fiber': 2.5},
            'にんじん': {'cal_per_100g': 41, 'protein': 0.9, 'carbs': 9.6, 'fat': 0.2, 'fiber': 2.8},
            'たまねぎ': {'cal_per_100g': 40, 'protein': 1.1, 'carbs': 9.3, 'fat': 0.1, 'fiber': 1.7},
            'じゃがいも': {'cal_per_100g': 77, 'protein': 2.0, 'carbs': 17.5, 'fat': 0.1, 'fiber': 2.2},
            'さつまいも': {'cal_per_100g': 86, 'protein': 1.6, 'carbs': 20.1, 'fat': 0.1, 'fiber': 3.0},
            
            # 果物類
            'りんご': {'cal_per_100g': 52, 'protein': 0.3, 'carbs': 13.8, 'fat': 0.2, 'fiber': 2.4},
            'バナナ': {'cal_per_100g': 89, 'protein': 1.1, 'carbs': 22.8, 'fat': 0.3, 'fiber': 2.6},
            'オレンジ': {'cal_per_100g': 47, 'protein': 0.9, 'carbs': 11.8, 'fat': 0.1, 'fiber': 2.4},
            'いちご': {'cal_per_100g': 32, 'protein': 0.7, 'carbs': 7.7, 'fat': 0.3, 'fiber': 2.0},
            'ぶどう': {'cal_per_100g': 69, 'protein': 0.7, 'carbs': 18.1, 'fat': 0.2, 'fiber': 0.9},
            
            # 飲み物
            '牛乳': {'cal_per_100g': 61, 'protein': 3.4, 'carbs': 4.8, 'fat': 3.3, 'fiber': 0.0},
            '豆乳': {'cal_per_100g': 45, 'protein': 3.6, 'carbs': 3.1, 'fat': 2.0, 'fiber': 0.2},
            'コーヒー': {'cal_per_100g': 2, 'protein': 0.2, 'carbs': 0.3, 'fat': 0.0, 'fiber': 0.0},
            'お茶': {'cal_per_100g': 1, 'protein': 0.0, 'carbs': 0.2, 'fat': 0.0, 'fiber': 0.0},
            
            # その他
            'みそ汁': {'cal_per_100g': 40, 'protein': 2.2, 'carbs': 5.7, 'fat': 1.1, 'fiber': 0.5},
            'サラダ': {'cal_per_100g': 20, 'protein': 1.2, 'carbs': 3.8, 'fat': 0.2, 'fiber': 1.5},
            'カレー': {'cal_per_100g': 150, 'protein': 5.5, 'carbs': 17.0, 'fat': 7.0, 'fiber': 2.0},
            '天ぷら': {'cal_per_100g': 250, 'protein': 8.0, 'carbs': 15.0, 'fat': 17.0, 'fiber': 1.0},
            '寿司': {'cal_per_100g': 150, 'protein': 8.5, 'carbs': 22.0, 'fat': 3.0, 'fiber': 0.5},
        }
        
        # 量の単位変換マップ
        self.unit_conversions = {
            '個': {'卵': 50, 'りんご': 200, 'バナナ': 120, 'オレンジ': 150},
            '枚': {'パン': 60, '食パン': 60},
            '杯': {'ご飯': 150, '白米': 150, 'みそ汁': 180},
            '切れ': {'魚': 80, 'サーモン': 80, 'マグロ': 80},
            'slice': {'パン': 30, 'pizza': 100},
            'cup': {'牛乳': 240, 'コーヒー': 240},
        }
    
    def parse_quantity(self, quantity_str: str) -> float:
        """
        量の文字列をグラム数に変換
        例: "150g" -> 150, "2個" -> 100 (卵の場合)
        """
        # 数値と単位を抽出
        match = re.match(r'([\d.]+)\s*(.+)?', quantity_str)
        if not match:
            return 100.0  # デフォルト値
        
        amount = float(match.group(1))
        unit = match.group(2) if match.group(2) else 'g'
        
        # グラム単位の場合はそのまま返す
        if unit in ['g', 'グラム']:
            return amount
        
        # kg単位の場合
        if unit in ['kg', 'キロ']:
            return amount * 1000
        
        # その他の単位は100gとして扱う
        return amount * 100
    
    def calculate_nutrition(self, food_name: str, quantity: str) -> Optional[NutritionInfo]:
        """
        食品名と量から栄養情報を計算
        """
        # 食品名の正規化（英語/日本語の変換）
        normalized_name = self._normalize_food_name(food_name)
        
        # データベースで検索
        food_info = None
        for db_name, info in self.food_database.items():
            if normalized_name in db_name or db_name in normalized_name:
                food_info = info
                break
        
        if not food_info:
            # デフォルト値を返す
            return NutritionInfo(
                calories=100,
                protein=5.0,
                carbs=15.0,
                fat=3.0,
                fiber=1.0
            )
        
        # 量をグラムに変換
        grams = self.parse_quantity(quantity)
        multiplier = grams / 100.0
        
        # 栄養素を計算
        return NutritionInfo(
            calories=food_info['cal_per_100g'] * multiplier,
            protein=food_info.get('protein', 0) * multiplier,
            carbs=food_info.get('carbs', 0) * multiplier,
            fat=food_info.get('fat', 0) * multiplier,
            fiber=food_info.get('fiber', 0) * multiplier
        )
    
    def _normalize_food_name(self, name: str) -> str:
        """食品名の正規化（日本語/英語の統一）"""
        # 簡単な正規化マップ
        normalization_map = {
            'rice': 'ご飯',
            'chicken': '鶏肉',
            'beef': '牛肉',
            'pork': '豚肉',
            'fish': '魚',
            'egg': '卵',
            'tofu': '豆腐',
            'milk': '牛乳',
            'bread': 'パン',
            'apple': 'りんご',
            'banana': 'バナナ',
            'orange': 'オレンジ',
            'salad': 'サラダ',
            'curry': 'カレー',
            'sushi': '寿司',
        }
        
        # 小文字に変換
        lower_name = name.lower()
        
        # 英語から日本語への変換を試みる
        for eng, jpn in normalization_map.items():
            if eng in lower_name:
                return jpn
        
        # スペースと特殊文字を除去
        cleaned = re.sub(r'[^\w\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', '', name)
        
        return cleaned
    
    def calculate_meal_nutrition(self, foods: List[Dict]) -> Dict:
        """
        複数の食品から食事全体の栄養情報を計算
        """
        total = NutritionInfo(calories=0, protein=0, carbs=0, fat=0, fiber=0)
        
        foods_with_nutrition = []
        for food in foods:
            nutrition = self.calculate_nutrition(food['name'], food['quantity'])
            if nutrition:
                total.calories += nutrition.calories
                total.protein += nutrition.protein
                total.carbs += nutrition.carbs
                total.fat += nutrition.fat
                total.fiber += nutrition.fiber
                
                foods_with_nutrition.append({
                    **food,
                    'calories': round(nutrition.calories),
                    'protein': round(nutrition.protein, 1),
                    'carbs': round(nutrition.carbs, 1),
                    'fat': round(nutrition.fat, 1),
                    'fiber': round(nutrition.fiber, 1)
                })
        
        # PFCバランスを計算（％）
        total_cal_from_macros = (total.protein * 4) + (total.carbs * 4) + (total.fat * 9)
        pfc_balance = {
            'protein_ratio': round((total.protein * 4 / total_cal_from_macros * 100), 1) if total_cal_from_macros > 0 else 0,
            'carbs_ratio': round((total.carbs * 4 / total_cal_from_macros * 100), 1) if total_cal_from_macros > 0 else 0,
            'fat_ratio': round((total.fat * 9 / total_cal_from_macros * 100), 1) if total_cal_from_macros > 0 else 0,
        }
        
        return {
            'foods': foods_with_nutrition,
            'total': {
                'calories': round(total.calories),
                'protein': round(total.protein, 1),
                'carbs': round(total.carbs, 1),
                'fat': round(total.fat, 1),
                'fiber': round(total.fiber, 1)
            },
            'pfc_balance': pfc_balance
        }
    
    def get_food_suggestions(self, query: str = '') -> List[Dict]:
        """
        食品データベースから検索候補を取得
        """
        query_lower = query.lower()
        suggestions = []
        
        for food_name, info in self.food_database.items():
            if not query or query_lower in food_name.lower():
                suggestions.append({
                    'name': food_name,
                    'calories_per_100g': info['cal_per_100g'],
                    'protein': info.get('protein', 0),
                    'carbs': info.get('carbs', 0),
                    'fat': info.get('fat', 0)
                })
        
        # カロリーでソート
        suggestions.sort(key=lambda x: x['name'])
        return suggestions[:20]  # 最大20件
    
    def estimate_daily_needs(self, weight_kg: float, height_cm: float, age: int, 
                           gender: str = 'male', activity_level: str = 'moderate') -> Dict:
        """
        基礎代謝量と推奨摂取カロリーを計算
        """
        # Harris-Benedict式で基礎代謝量（BMR）を計算
        if gender.lower() == 'male':
            bmr = 88.362 + (13.397 * weight_kg) + (4.799 * height_cm) - (5.677 * age)
        else:
            bmr = 447.593 + (9.247 * weight_kg) + (3.098 * height_cm) - (4.330 * age)
        
        # 活動レベル係数
        activity_multipliers = {
            'sedentary': 1.2,      # 座りがち
            'light': 1.375,        # 軽い運動
            'moderate': 1.55,      # 適度な運動
            'active': 1.725,       # 活発
            'very_active': 1.9     # 非常に活発
        }
        
        multiplier = activity_multipliers.get(activity_level, 1.55)
        daily_calories = bmr * multiplier
        
        # 推奨PFCバランス（一般的な目安）
        recommended_pfc = {
            'protein_g': weight_kg * 1.2,  # 体重1kgあたり1.2g
            'carbs_g': daily_calories * 0.5 / 4,  # カロリーの50%を炭水化物から
            'fat_g': daily_calories * 0.25 / 9,    # カロリーの25%を脂質から
        }
        
        return {
            'bmr': round(bmr),
            'daily_calories': round(daily_calories),
            'recommended_pfc': {
                'protein': round(recommended_pfc['protein_g'], 1),
                'carbs': round(recommended_pfc['carbs_g'], 1),
                'fat': round(recommended_pfc['fat_g'], 1)
            }
        }