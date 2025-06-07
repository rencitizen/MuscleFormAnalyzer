"""
トレーニングと栄養の統合システム
運動量に基づく栄養最適化
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import numpy as np

@dataclass
class TrainingSession:
    """トレーニングセッション"""
    date: datetime
    exercise_type: str
    duration_minutes: int
    intensity: str  # 'low', 'moderate', 'high'
    volume: Dict[str, float]  # sets, reps, weight
    calories_burned: float

@dataclass
class NutritionPlan:
    """栄養プラン"""
    date: datetime
    base_calories: float
    training_calories: float
    total_calories: float
    macro_targets: Dict[str, float]
    meal_timing: List[Dict]
    supplements: List[Dict]

class TrainingNutritionIntegrator:
    """トレーニングと栄養の統合クラス"""
    
    def __init__(self):
        # 運動種目別のカロリー消費（METs値）
        self.exercise_mets = {
            'squat': 6.0,
            'bench_press': 5.0,
            'deadlift': 6.0,
            'overhead_press': 4.5,
            'cardio_low': 4.0,
            'cardio_moderate': 7.0,
            'cardio_high': 10.0,
            'yoga': 2.5,
            'stretching': 2.0
        }
        
        # トレーニング強度による係数
        self.intensity_multipliers = {
            'low': 0.8,
            'moderate': 1.0,
            'high': 1.3,
            'max': 1.5
        }
        
        # 筋トレ後の代謝向上（EPOC）
        self.epoc_factors = {
            'strength_training': 0.15,  # 15%追加消費
            'hiit': 0.20,
            'cardio': 0.05
        }
    
    def calculate_training_calories(self, 
                                  session: TrainingSession,
                                  user_weight_kg: float) -> float:
        """
        トレーニングによるカロリー消費を計算
        """
        # 基本METs値を取得
        base_mets = self.exercise_mets.get(session.exercise_type, 5.0)
        
        # 強度による調整
        intensity_mult = self.intensity_multipliers.get(session.intensity, 1.0)
        adjusted_mets = base_mets * intensity_mult
        
        # カロリー計算（METs × 体重 × 時間）
        calories = adjusted_mets * user_weight_kg * (session.duration_minutes / 60)
        
        # EPOC効果を追加
        if 'strength' in session.exercise_type or session.exercise_type in ['squat', 'bench_press', 'deadlift']:
            epoc_calories = calories * self.epoc_factors['strength_training']
            calories += epoc_calories
        
        return round(calories)
    
    def calculate_recovery_needs(self, 
                               session: TrainingSession,
                               muscle_groups: List[str]) -> Dict[str, float]:
        """
        回復に必要な栄養素を計算
        """
        recovery_needs = {
            'protein_g': 0,
            'carbs_g': 0,
            'water_ml': 0,
            'sodium_mg': 0,
            'potassium_mg': 0
        }
        
        # トレーニングボリュームに基づく計算
        if session.volume:
            total_volume = session.volume.get('sets', 0) * session.volume.get('reps', 0) * session.volume.get('weight', 0)
            
            # タンパク質需要（筋肉修復）
            recovery_needs['protein_g'] = min(40, total_volume * 0.0001)
            
            # 炭水化物需要（グリコーゲン補充）
            recovery_needs['carbs_g'] = session.duration_minutes * 0.5
        
        # 強度による調整
        if session.intensity == 'high':
            recovery_needs['protein_g'] *= 1.2
            recovery_needs['carbs_g'] *= 1.3
        
        # 水分と電解質
        recovery_needs['water_ml'] = session.duration_minutes * 15  # 15ml/分
        recovery_needs['sodium_mg'] = session.duration_minutes * 10
        recovery_needs['potassium_mg'] = session.duration_minutes * 8
        
        return recovery_needs
    
    def optimize_meal_timing(self, 
                           training_time: datetime,
                           training_type: str) -> List[Dict]:
        """
        トレーニングに合わせた食事タイミングを最適化
        """
        meal_schedule = []
        
        # プレワークアウト（トレーニング1-2時間前）
        pre_workout_time = training_time - timedelta(hours=1.5)
        meal_schedule.append({
            'time': pre_workout_time,
            'type': 'pre_workout',
            'macros': {
                'carbs': 30,  # g
                'protein': 20,
                'fat': 5
            },
            'foods': ['バナナ', 'オートミール', 'プロテインシェイク'],
            'notes': '消化の良い炭水化物中心'
        })
        
        # ポストワークアウト（トレーニング後30分以内）
        post_workout_time = training_time + timedelta(minutes=30)
        meal_schedule.append({
            'time': post_workout_time,
            'type': 'post_workout',
            'macros': {
                'carbs': 40,
                'protein': 30,
                'fat': 10
            },
            'foods': ['白米', '鶏胸肉', 'ブロッコリー'],
            'notes': 'タンパク質と炭水化物の黄金比率'
        })
        
        # トレーニング種別による調整
        if training_type in ['squat', 'deadlift']:
            # 下半身トレーニングは消費カロリーが多い
            meal_schedule[1]['macros']['carbs'] += 20
            meal_schedule[1]['macros']['protein'] += 10
        
        return meal_schedule
    
    def create_training_day_nutrition_plan(self,
                                         user_profile: Dict,
                                         training_session: TrainingSession,
                                         base_nutrition_goals: Dict) -> NutritionPlan:
        """
        トレーニング日の栄養プランを作成
        """
        # トレーニングによる追加カロリー計算
        training_calories = self.calculate_training_calories(
            training_session,
            user_profile.get('weight_kg', 70)
        )
        
        # 回復に必要な栄養素
        recovery_needs = self.calculate_recovery_needs(
            training_session,
            ['chest', 'triceps']  # TODO: 実際の筋群を判定
        )
        
        # 基礎目標に追加
        total_calories = base_nutrition_goals['calories'] + training_calories
        
        # マクロ栄養素の調整
        macro_targets = {
            'protein': base_nutrition_goals['protein'] + recovery_needs['protein_g'],
            'carbs': base_nutrition_goals['carbs'] + recovery_needs['carbs_g'],
            'fat': base_nutrition_goals['fat'],
            'fiber': base_nutrition_goals.get('fiber', 25),
            'water': base_nutrition_goals.get('water', 2000) + recovery_needs['water_ml']
        }
        
        # 食事タイミングの最適化
        meal_timing = self.optimize_meal_timing(
            training_session.date,
            training_session.exercise_type
        )
        
        # サプリメント提案
        supplements = self.suggest_supplements(training_session, recovery_needs)
        
        return NutritionPlan(
            date=training_session.date,
            base_calories=base_nutrition_goals['calories'],
            training_calories=training_calories,
            total_calories=total_calories,
            macro_targets=macro_targets,
            meal_timing=meal_timing,
            supplements=supplements
        )
    
    def suggest_supplements(self, 
                          session: TrainingSession,
                          recovery_needs: Dict) -> List[Dict]:
        """
        トレーニングに基づくサプリメント提案
        """
        supplements = []
        
        # 基本的なサプリメント
        if session.intensity in ['high', 'max']:
            supplements.append({
                'name': 'BCAA',
                'timing': 'during_workout',
                'dosage': '10g',
                'purpose': '筋肉の分解を防ぐ'
            })
        
        # 回復系サプリメント
        if recovery_needs['protein_g'] > 30:
            supplements.append({
                'name': 'ホエイプロテイン',
                'timing': 'post_workout',
                'dosage': '30g',
                'purpose': '筋肉の修復と成長'
            })
        
        # クレアチン（筋力向上）
        if session.exercise_type in ['squat', 'bench_press', 'deadlift']:
            supplements.append({
                'name': 'クレアチンモノハイドレート',
                'timing': 'anytime',
                'dosage': '5g',
                'purpose': '筋力とパワーの向上'
            })
        
        return supplements
    
    def analyze_training_nutrition_correlation(self,
                                            training_history: List[TrainingSession],
                                            nutrition_history: List[Dict]) -> Dict:
        """
        トレーニングと栄養の相関を分析
        """
        analysis = {
            'performance_trends': [],
            'recovery_quality': [],
            'recommendations': []
        }
        
        # パフォーマンストレンドの分析
        for i, session in enumerate(training_history):
            # 対応する日の栄養データを検索
            session_date = session.date.date()
            daily_nutrition = next(
                (n for n in nutrition_history if n['date'].date() == session_date),
                None
            )
            
            if daily_nutrition:
                # カロリー充足率とパフォーマンスの相関
                calorie_adequacy = daily_nutrition['calories'] / daily_nutrition.get('goal_calories', 2000)
                performance_score = self._calculate_performance_score(session)
                
                analysis['performance_trends'].append({
                    'date': session_date,
                    'calorie_adequacy': calorie_adequacy,
                    'performance_score': performance_score,
                    'correlation': 'positive' if calorie_adequacy > 0.9 and performance_score > 80 else 'needs_improvement'
                })
        
        # 推奨事項の生成
        if len(analysis['performance_trends']) > 0:
            avg_adequacy = np.mean([t['calorie_adequacy'] for t in analysis['performance_trends']])
            
            if avg_adequacy < 0.9:
                analysis['recommendations'].append({
                    'type': 'nutrition',
                    'message': 'トレーニング日のカロリー摂取が不足しています。パフォーマンス向上のため増やしましょう。',
                    'action': 'トレーニング日は基礎代謝の1.5倍のカロリーを目標に'
                })
        
        return analysis
    
    def _calculate_performance_score(self, session: TrainingSession) -> float:
        """
        トレーニングセッションのパフォーマンススコアを計算
        """
        # 簡易的なスコア計算（実際はより複雑な指標を使用）
        base_score = 70
        
        # ボリュームによる加点
        if session.volume:
            volume_score = min(20, session.volume.get('sets', 0) * session.volume.get('reps', 0) * 0.1)
            base_score += volume_score
        
        # 強度による加点
        intensity_scores = {'low': 5, 'moderate': 10, 'high': 15, 'max': 20}
        base_score += intensity_scores.get(session.intensity, 10)
        
        return min(100, base_score)
    
    def generate_periodized_nutrition_plan(self,
                                         training_program: Dict,
                                         user_profile: Dict) -> Dict:
        """
        トレーニング周期に合わせた栄養プランを生成
        """
        periodized_plan = {}
        
        # トレーニング周期の定義
        phases = {
            'hypertrophy': {  # 筋肥大期
                'duration_weeks': 8,
                'calorie_surplus': 300,
                'protein_multiplier': 2.2,  # g/kg体重
                'carb_ratio': 0.5,
                'fat_ratio': 0.25
            },
            'strength': {  # 筋力向上期
                'duration_weeks': 4,
                'calorie_surplus': 200,
                'protein_multiplier': 2.0,
                'carb_ratio': 0.45,
                'fat_ratio': 0.3
            },
            'cutting': {  # 減量期
                'duration_weeks': 6,
                'calorie_deficit': -300,
                'protein_multiplier': 2.5,  # 筋肉維持のため高め
                'carb_ratio': 0.35,
                'fat_ratio': 0.25
            }
        }
        
        current_phase = training_program.get('current_phase', 'hypertrophy')
        phase_config = phases[current_phase]
        
        # 基礎代謝の計算
        bmr = self._calculate_bmr(user_profile)
        
        # フェーズごとの栄養目標
        periodized_plan[current_phase] = {
            'daily_calories': bmr * 1.5 + phase_config.get('calorie_surplus', 0) + phase_config.get('calorie_deficit', 0),
            'protein_g': user_profile['weight_kg'] * phase_config['protein_multiplier'],
            'carbs_g': (bmr * 1.5 * phase_config['carb_ratio']) / 4,
            'fat_g': (bmr * 1.5 * phase_config['fat_ratio']) / 9,
            'meal_frequency': 5 if current_phase == 'hypertrophy' else 4,
            'hydration_ml': user_profile['weight_kg'] * 40,
            'key_foods': self._get_phase_specific_foods(current_phase)
        }
        
        return periodized_plan
    
    def _calculate_bmr(self, user_profile: Dict) -> float:
        """
        基礎代謝率を計算（Harris-Benedict式）
        """
        weight = user_profile.get('weight_kg', 70)
        height = user_profile.get('height_cm', 170)
        age = user_profile.get('age', 30)
        gender = user_profile.get('gender', 'male')
        
        if gender == 'male':
            bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
        else:
            bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
        
        return bmr
    
    def _get_phase_specific_foods(self, phase: str) -> List[str]:
        """
        トレーニングフェーズに適した食品リスト
        """
        phase_foods = {
            'hypertrophy': [
                '玄米', '鶏胸肉', '全卵', 'サーモン', 'さつまいも',
                'アボカド', 'ナッツ類', 'オートミール'
            ],
            'strength': [
                '赤身肉', 'キヌア', 'ブロッコリー', 'ほうれん草',
                'ギリシャヨーグルト', 'ベリー類'
            ],
            'cutting': [
                'ささみ', '白身魚', '野菜全般', 'こんにゃく',
                '海藻類', 'きのこ類', 'プロテインパウダー'
            ]
        }
        
        return phase_foods.get(phase, [])