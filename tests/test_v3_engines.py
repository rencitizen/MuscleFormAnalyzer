# tests/test_v3_engines.py
"""
TENAX FIT v3.0 エンジンテスト
科学的計算の正確性を検証
"""

import unittest
from core.body_composition_engine import BodyCompositionEngine
from core.metabolism_engine import MetabolismEngine
from core.nutrition_engine import NutritionEngine
from core.training_engine import TrainingEngine
from core.safety_engine import SafetyEngine


class TestBodyCompositionEngine(unittest.TestCase):
    def setUp(self):
        self.engine = BodyCompositionEngine()
    
    def test_bmi_calculation(self):
        """BMI計算の正確性テスト"""
        # 標準的なケース: 170cm, 70kg
        bmi = self.engine.calculate_bmi(70, 170)
        self.assertAlmostEqual(bmi, 24.22, places=2)
        
        # カテゴリー判定
        category = self.engine.get_bmi_category(bmi)
        self.assertEqual(category, "normal")
    
    def test_body_fat_estimation(self):
        """体脂肪率推定のテスト"""
        # 30歳男性のケース
        bf = self.engine.estimate_body_fat_tanita(70, 170, 30, 'male')
        self.assertGreater(bf, 0)
        self.assertLess(bf, 50)
        
        # 30歳女性のケース
        bf_female = self.engine.estimate_body_fat_tanita(60, 160, 30, 'female')
        self.assertGreater(bf_female, bf)  # 女性の方が高いはず
    
    def test_health_warnings(self):
        """健康警告生成のテスト"""
        # 危険な体脂肪率目標
        warnings = self.engine.generate_health_warnings(
            target_bodyfat=10,
            current_bodyfat=20,
            gender='female'
        )
        self.assertGreater(len(warnings), 0)
        self.assertEqual(warnings[0]['level'], 'danger')


class TestMetabolismEngine(unittest.TestCase):
    def setUp(self):
        self.engine = MetabolismEngine()
    
    def test_bmr_calculations(self):
        """BMR計算の正確性テスト"""
        # 30歳、170cm、70kg、男性
        bmr = self.engine.calculate_bmr_mifflin(70, 170, 30, 'male')
        self.assertAlmostEqual(bmr, 1617.5, places=1)
        
        # 全方法での計算
        all_bmr = self.engine.calculate_all_bmr_methods(70, 170, 30, 'male', 20)
        self.assertIn('mifflin', all_bmr)
        self.assertIn('harris_benedict', all_bmr)
        self.assertIn('katch_mcardle', all_bmr)
    
    def test_tdee_calculation(self):
        """TDEE計算のテスト"""
        bmr = 1600
        tdee_data = self.engine.calculate_tdee(bmr, 'moderate')
        
        self.assertGreater(tdee_data['total_tdee'], bmr)
        self.assertAlmostEqual(tdee_data['base_tdee'], bmr * 1.55, places=1)
    
    def test_calorie_goals(self):
        """カロリー目標設定のテスト"""
        tdee = 2400
        
        # 減量目標
        cutting_goals = self.engine.calculate_calorie_goals(tdee, 'moderate_cut')
        self.assertEqual(cutting_goals['adjustment'], -500)
        self.assertEqual(cutting_goals['target_calories'], 1900)
        
        # 安全性チェック
        self.assertTrue(cutting_goals['safety_checked'])


class TestNutritionEngine(unittest.TestCase):
    def setUp(self):
        self.engine = NutritionEngine()
    
    def test_pfc_macro_calculation(self):
        """PFCマクロ計算のテスト"""
        calories = 2000
        macros = self.engine.calculate_pfc_macros(calories, 'general_training')
        
        # 総カロリーの検証
        total_cal = (macros['protein_g'] * 4 + 
                    macros['carbs_g'] * 4 + 
                    macros['fat_g'] * 9)
        self.assertAlmostEqual(total_cal, calories, delta=20)
        
        # 比率の合計が100%
        total_ratio = (macros['protein_ratio'] + 
                      macros['carbs_ratio'] + 
                      macros['fat_ratio'])
        self.assertAlmostEqual(total_ratio, 100, places=1)
    
    def test_protein_requirements(self):
        """タンパク質必要量計算のテスト"""
        needs = self.engine.calculate_protein_needs(
            weight_kg=70,
            goal='muscle_gain',
            activity_level='general_training'
        )
        
        self.assertGreater(needs['daily_total_g'], 100)
        self.assertLessEqual(needs['daily_total_g'], 250)
        self.assertIn('meal_distribution', needs)
    
    def test_meal_plan_generation(self):
        """食事プラン生成のテスト"""
        macros = {'protein_g': 150, 'carbs_g': 200, 'fat_g': 70}
        meal_plan = self.engine.generate_sample_meal_plan(2000, macros)
        
        self.assertGreater(len(meal_plan['meal_plan']), 0)
        self.assertEqual(meal_plan['total_meals'], len(meal_plan['meal_plan']))


class TestTrainingEngine(unittest.TestCase):
    def setUp(self):
        self.engine = TrainingEngine()
    
    def test_workout_plan_generation(self):
        """ワークアウトプラン生成のテスト"""
        plan = self.engine.generate_workout_plan(
            experience='intermediate',
            goal='hypertrophy',
            available_days=4,
            equipment='full_gym'
        )
        
        self.assertIn('program', plan)
        self.assertIn('progression_plan', plan)
        self.assertIn('safety_guidelines', plan)
        self.assertEqual(plan['experience_level'], 'intermediate')
    
    def test_exercise_calorie_calculation(self):
        """運動カロリー計算のテスト"""
        cal_data = self.engine.calculate_exercise_calories(
            exercise_type='strength',
            intensity='moderate',
            weight_kg=70,
            duration_minutes=60
        )
        
        self.assertGreater(cal_data['exercise_calories'], 200)
        self.assertLess(cal_data['exercise_calories'], 600)
        self.assertEqual(cal_data['mets_used'], 5.0)


class TestSafetyEngine(unittest.TestCase):
    def setUp(self):
        self.engine = SafetyEngine()
    
    def test_comprehensive_safety_check(self):
        """包括的安全性チェックのテスト"""
        user_data = {
            'gender': 'female',
            'bmr': 1400,
            'tdee': 2000,
            'weight': 60
        }
        
        goals = {
            'target_body_fat': 12,  # 危険な目標
            'weekly_weight_change': -1.5  # 急速すぎる減量
        }
        
        plan = {
            'target_calories': 1000,  # BMR以下
            'training_plan': {
                'weekly_duration_hours': 12,  # 過度
                'frequency_days': 7
            }
        }
        
        safety_result = self.engine.comprehensive_safety_check(
            user_data, goals, plan
        )
        
        self.assertIn(safety_result['overall_safety'], 
                     ['moderate_risk', 'high_risk'])
        self.assertGreater(len(safety_result['warnings']), 0)
        self.assertGreater(safety_result['risk_score'], 30)
    
    def test_calorie_safety(self):
        """カロリー安全性チェックのテスト"""
        user_data = {'bmr': 1500, 'tdee': 2100, 'gender': 'male'}
        
        warnings, risk = self.engine._check_calorie_safety(
            user_data, 
            target_calories=1200  # BMR以下
        )
        
        self.assertGreater(len(warnings), 0)
        self.assertEqual(warnings[0]['level'], 'critical')
        self.assertGreater(risk, 20)


class TestIntegration(unittest.TestCase):
    """統合テスト"""
    
    def test_full_analysis_flow(self):
        """完全な分析フローのテスト"""
        # エンジンの初期化
        body_engine = BodyCompositionEngine()
        metabolism_engine = MetabolismEngine()
        nutrition_engine = NutritionEngine()
        training_engine = TrainingEngine()
        safety_engine = SafetyEngine()
        
        # ユーザーデータ
        user_profile = {
            'weight': 75,
            'height': 175,
            'age': 28,
            'gender': 'male',
            'activity_level': 'moderate',
            'goal': 'cutting',
            'experience': 'intermediate'
        }
        
        # 1. 身体組成分析
        bmi = body_engine.calculate_bmi(
            user_profile['weight'], 
            user_profile['height']
        )
        self.assertGreater(bmi, 20)
        self.assertLess(bmi, 30)
        
        # 2. 代謝計算
        bmr = metabolism_engine.calculate_bmr_mifflin(
            user_profile['weight'],
            user_profile['height'],
            user_profile['age'],
            user_profile['gender']
        )
        tdee_data = metabolism_engine.calculate_tdee(
            bmr, 
            user_profile['activity_level']
        )
        
        # 3. カロリー目標
        calorie_goals = metabolism_engine.calculate_calorie_goals(
            tdee_data['total_tdee'],
            user_profile['goal']
        )
        
        # 4. 栄養計画
        macros = nutrition_engine.calculate_pfc_macros(
            calorie_goals['target_calories'],
            user_profile['goal']
        )
        
        # 5. トレーニング計画
        workout_plan = training_engine.generate_workout_plan(
            user_profile['experience'],
            'hypertrophy',  # 筋肥大目標
            4,  # 週4日
            'full_gym'
        )
        
        # 6. 安全性チェック
        safety_check = safety_engine.comprehensive_safety_check(
            {**user_profile, 'bmr': bmr, 'tdee': tdee_data['total_tdee']},
            {'weekly_weight_change': calorie_goals['weekly_weight_change_kg']},
            {
                'target_calories': calorie_goals['target_calories'],
                'nutrition_plan': macros,
                'training_plan': {'frequency_days': 4, 'weekly_duration_hours': 5}
            }
        )
        
        # 統合結果の検証
        self.assertIsNotNone(bmi)
        self.assertIsNotNone(bmr)
        self.assertIsNotNone(calorie_goals)
        self.assertIsNotNone(macros)
        self.assertIsNotNone(workout_plan)
        self.assertIn(safety_check['overall_safety'], 
                     ['safe', 'low_risk', 'moderate_risk', 'high_risk'])


if __name__ == '__main__':
    unittest.main()