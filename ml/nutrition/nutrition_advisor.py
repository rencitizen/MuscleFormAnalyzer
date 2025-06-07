"""
栄養アドバイスシステム
個人の目標と摂取状況に基づいてアドバイスを提供
"""
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

@dataclass
class NutritionGoals:
    """栄養目標"""
    daily_calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float = 25.0
    water_ml: float = 2000.0

@dataclass
class NutritionAdvice:
    """栄養アドバイス"""
    category: str  # 'warning', 'suggestion', 'praise'
    priority: int  # 1-5 (5が最高)
    message: str
    action_items: List[str]
    food_suggestions: List[Dict[str, any]]

class NutritionAdvisor:
    """栄養アドバイザー"""
    
    def __init__(self):
        # アドバイステンプレート
        self.advice_templates = {
            'protein_low': {
                'message': 'タンパク質が不足しています。筋肉の維持・成長に重要です。',
                'actions': [
                    '各食事にタンパク質源を含める',
                    '間食にプロテインシェイクを追加',
                    '朝食に卵を追加'
                ],
                'foods': ['鶏胸肉', '卵', 'ギリシャヨーグルト', '豆腐', 'サーモン']
            },
            'protein_high': {
                'message': 'タンパク質が過剰です。バランスを考慮しましょう。',
                'actions': [
                    '野菜の量を増やす',
                    'タンパク質源の1回量を減らす'
                ],
                'foods': ['野菜サラダ', '玄米', 'さつまいも']
            },
            'carbs_low': {
                'message': '炭水化物が不足しています。エネルギー不足に注意。',
                'actions': [
                    'トレーニング前後に炭水化物を摂取',
                    '朝食に全粒穀物を追加'
                ],
                'foods': ['オートミール', 'バナナ', '玄米', '全粒粉パン']
            },
            'fiber_low': {
                'message': '食物繊維が不足しています。腸内環境の改善に重要です。',
                'actions': [
                    '各食事に野菜を追加',
                    '精製穀物を全粒穀物に置き換え'
                ],
                'foods': ['ブロッコリー', 'アボカド', 'りんご', 'オートミール']
            },
            'calories_surplus': {
                'message': 'カロリーが目標を大幅に超えています。',
                'actions': [
                    '食事の量を見直す',
                    '高カロリー食品を低カロリー食品に置き換え'
                ],
                'foods': ['野菜スープ', 'こんにゃく', 'キノコ類']
            },
            'balanced': {
                'message': '素晴らしい！栄養バランスが良好です。',
                'actions': [
                    'この調子を維持しましょう',
                    '水分補給を忘れずに'
                ],
                'foods': []
            }
        }
        
        # 時間帯別アドバイス
        self.timing_advice = {
            'morning': {
                'focus': 'エネルギー補給と代謝活性化',
                'nutrients': ['protein', 'complex_carbs', 'fiber'],
                'avoid': ['high_fat', 'simple_sugars']
            },
            'pre_workout': {
                'focus': 'エネルギー供給と消化の良さ',
                'nutrients': ['simple_carbs', 'moderate_protein'],
                'avoid': ['high_fiber', 'high_fat']
            },
            'post_workout': {
                'focus': '回復と筋肉合成',
                'nutrients': ['protein', 'simple_carbs'],
                'timing': '30分以内が理想的'
            },
            'evening': {
                'focus': '回復と翌日の準備',
                'nutrients': ['protein', 'vegetables'],
                'avoid': ['caffeine', 'high_carbs']
            }
        }
    
    def analyze_nutrition_status(self, 
                               current: Dict[str, float], 
                               goals: NutritionGoals,
                               meal_history: List[Dict] = None) -> List[NutritionAdvice]:
        """
        現在の栄養状態を分析してアドバイスを生成
        """
        advice_list = []
        
        # 各栄養素の達成率を計算
        protein_ratio = current.get('protein', 0) / goals.protein_g if goals.protein_g > 0 else 0
        carbs_ratio = current.get('carbs', 0) / goals.carbs_g if goals.carbs_g > 0 else 0
        fat_ratio = current.get('fat', 0) / goals.fat_g if goals.fat_g > 0 else 0
        calories_ratio = current.get('calories', 0) / goals.daily_calories if goals.daily_calories > 0 else 0
        fiber_ratio = current.get('fiber', 0) / goals.fiber_g if goals.fiber_g > 0 else 0
        
        # タンパク質のチェック
        if protein_ratio < 0.8:
            advice_list.append(self._create_advice('protein_low', 'warning', 4))
        elif protein_ratio > 1.5:
            advice_list.append(self._create_advice('protein_high', 'suggestion', 2))
        
        # 炭水化物のチェック
        if carbs_ratio < 0.7:
            advice_list.append(self._create_advice('carbs_low', 'warning', 3))
        
        # 食物繊維のチェック
        if fiber_ratio < 0.6:
            advice_list.append(self._create_advice('fiber_low', 'warning', 3))
        
        # カロリーのチェック
        if calories_ratio > 1.2:
            advice_list.append(self._create_advice('calories_surplus', 'warning', 4))
        
        # バランスが良い場合
        if 0.9 <= protein_ratio <= 1.1 and 0.9 <= carbs_ratio <= 1.1 and 0.9 <= calories_ratio <= 1.1:
            advice_list.append(self._create_advice('balanced', 'praise', 5))
        
        # 食事履歴に基づく追加アドバイス
        if meal_history:
            pattern_advice = self._analyze_eating_patterns(meal_history)
            advice_list.extend(pattern_advice)
        
        # 優先度でソート
        advice_list.sort(key=lambda x: x.priority, reverse=True)
        
        return advice_list[:5]  # 上位5件のアドバイス
    
    def _create_advice(self, template_key: str, category: str, priority: int) -> NutritionAdvice:
        """
        テンプレートからアドバイスを作成
        """
        template = self.advice_templates.get(template_key, {})
        
        return NutritionAdvice(
            category=category,
            priority=priority,
            message=template.get('message', ''),
            action_items=template.get('actions', []),
            food_suggestions=[
                {'name': food, 'reason': 'おすすめ食品'}
                for food in template.get('foods', [])
            ]
        )
    
    def _analyze_eating_patterns(self, meal_history: List[Dict]) -> List[NutritionAdvice]:
        """
        食事パターンを分析
        """
        pattern_advice = []
        
        # 食事回数の分析
        meal_counts = {}
        for meal in meal_history:
            date = meal.get('date', '').split('T')[0]
            meal_type = meal.get('meal_type', '')
            if date not in meal_counts:
                meal_counts[date] = set()
            meal_counts[date].add(meal_type)
        
        # 朝食スキップの検出
        breakfast_skip_days = sum(1 for meals in meal_counts.values() if 'breakfast' not in meals)
        if breakfast_skip_days > len(meal_counts) * 0.3:
            pattern_advice.append(NutritionAdvice(
                category='warning',
                priority=3,
                message='朝食を抜く日が多いようです。代謝と集中力に影響があります。',
                action_items=[
                    '簡単な朝食から始める（ヨーグルト、バナナなど）',
                    '前日に朝食を準備しておく'
                ],
                food_suggestions=[
                    {'name': 'オーバーナイトオーツ', 'reason': '前日準備可能'},
                    {'name': 'ゆで卵', 'reason': '作り置き可能'}
                ]
            ))
        
        # 夜遅い食事の検出
        late_dinner_count = sum(
            1 for meal in meal_history
            if meal.get('meal_type') == 'dinner' and 
            datetime.fromisoformat(meal.get('date', '')).hour >= 21
        )
        if late_dinner_count > len(meal_history) * 0.2:
            pattern_advice.append(NutritionAdvice(
                category='suggestion',
                priority=2,
                message='夜遅い食事が多いようです。睡眠の質に影響する可能性があります。',
                action_items=[
                    '夕食を早めに摂る',
                    '遅い場合は軽めの食事にする'
                ],
                food_suggestions=[
                    {'name': '野菜スープ', 'reason': '消化に良い'},
                    {'name': 'サラダチキン', 'reason': '高タンパク低脂質'}
                ]
            ))
        
        return pattern_advice
    
    def get_meal_suggestions(self, 
                           meal_type: str,
                           current_nutrition: Dict[str, float],
                           goals: NutritionGoals,
                           preferences: List[str] = None) -> List[Dict]:
        """
        次の食事の提案を生成
        """
        remaining = {
            'calories': goals.daily_calories - current_nutrition.get('calories', 0),
            'protein': goals.protein_g - current_nutrition.get('protein', 0),
            'carbs': goals.carbs_g - current_nutrition.get('carbs', 0),
            'fat': goals.fat_g - current_nutrition.get('fat', 0)
        }
        
        # 食事タイプに応じた配分
        meal_distribution = {
            'breakfast': 0.25,
            'lunch': 0.35,
            'dinner': 0.30,
            'snack': 0.10
        }
        
        target_calories = remaining['calories'] * meal_distribution.get(meal_type, 0.25)
        
        # 食事提案データベース
        meal_database = {
            'breakfast': [
                {
                    'name': 'オートミール＆ベリー',
                    'calories': 350,
                    'protein': 15,
                    'carbs': 55,
                    'fat': 8,
                    'prep_time': 5,
                    'ingredients': ['オートミール', 'ブルーベリー', 'アーモンド', 'はちみつ']
                },
                {
                    'name': 'スクランブルエッグ＆トースト',
                    'calories': 400,
                    'protein': 25,
                    'carbs': 35,
                    'fat': 18,
                    'prep_time': 10,
                    'ingredients': ['卵', '全粒粉パン', 'アボカド', 'トマト']
                }
            ],
            'lunch': [
                {
                    'name': '鶏胸肉のグリルサラダ',
                    'calories': 450,
                    'protein': 40,
                    'carbs': 30,
                    'fat': 15,
                    'prep_time': 15,
                    'ingredients': ['鶏胸肉', 'ミックスグリーン', 'キヌア', 'オリーブオイル']
                },
                {
                    'name': 'サーモン丼',
                    'calories': 500,
                    'protein': 35,
                    'carbs': 60,
                    'fat': 12,
                    'prep_time': 20,
                    'ingredients': ['サーモン', '玄米', 'アボカド', '海苔']
                }
            ],
            'dinner': [
                {
                    'name': '豆腐ステーキ野菜添え',
                    'calories': 350,
                    'protein': 20,
                    'carbs': 25,
                    'fat': 18,
                    'prep_time': 20,
                    'ingredients': ['木綿豆腐', 'ブロッコリー', 'にんじん', 'ごま油']
                }
            ],
            'snack': [
                {
                    'name': 'プロテインスムージー',
                    'calories': 200,
                    'protein': 20,
                    'carbs': 25,
                    'fat': 3,
                    'prep_time': 3,
                    'ingredients': ['プロテインパウダー', 'バナナ', 'アーモンドミルク']
                }
            ]
        }
        
        # 適切な食事を選択
        suitable_meals = []
        for meal in meal_database.get(meal_type, []):
            if abs(meal['calories'] - target_calories) < 100:
                suitable_meals.append(meal)
        
        return suitable_meals[:3]
    
    def generate_weekly_meal_plan(self, 
                                user_profile: Dict,
                                goals: NutritionGoals) -> Dict:
        """
        週間食事プランを生成
        """
        weekly_plan = {}
        days = ['月曜日', '火曜日', '水曜日', '木曜日', '金曜日', '土曜日', '日曜日']
        
        for day in days:
            daily_plan = {
                'breakfast': self.get_meal_suggestions('breakfast', {}, goals)[0] if self.get_meal_suggestions('breakfast', {}, goals) else None,
                'lunch': self.get_meal_suggestions('lunch', {}, goals)[0] if self.get_meal_suggestions('lunch', {}, goals) else None,
                'dinner': self.get_meal_suggestions('dinner', {}, goals)[0] if self.get_meal_suggestions('dinner', {}, goals) else None,
                'snacks': self.get_meal_suggestions('snack', {}, goals)[:2]
            }
            weekly_plan[day] = daily_plan
        
        return {
            'plan': weekly_plan,
            'shopping_list': self._generate_shopping_list(weekly_plan),
            'prep_schedule': self._generate_prep_schedule(weekly_plan)
        }
    
    def _generate_shopping_list(self, weekly_plan: Dict) -> List[str]:
        """
        買い物リストを生成
        """
        ingredients = set()
        for day_plan in weekly_plan.values():
            for meal_time, meal in day_plan.items():
                if isinstance(meal, dict) and 'ingredients' in meal:
                    ingredients.update(meal['ingredients'])
                elif isinstance(meal, list):
                    for m in meal:
                        if isinstance(m, dict) and 'ingredients' in m:
                            ingredients.update(m['ingredients'])
        
        return sorted(list(ingredients))
    
    def _generate_prep_schedule(self, weekly_plan: Dict) -> Dict:
        """
        下準備スケジュールを生成
        """
        return {
            '日曜日': [
                '野菜をカット・保存',
                '鶏胸肉を下味つけ',
                'ゆで卵を作る（5日分）'
            ],
            '水曜日': [
                '後半の野菜準備',
                'プロテインボールを作る'
            ]
        }