# core/metabolism_engine.py
"""
代謝計算エンジン
BMR、TDEE、カロリー目標の科学的計算を提供
"""

class MetabolismEngine:
    def __init__(self):
        self.activity_multipliers = {
            "sedentary": 1.2,      # 座りがち（ほとんど運動しない）
            "light": 1.375,        # 軽い活動（週1-3日の軽い運動）
            "moderate": 1.55,      # 中程度（週3-5日の運動）
            "active": 1.725,       # 活発（週6-7日の運動）
            "very_active": 1.9     # 非常に活発（1日2回の運動、肉体労働）
        }
        
        self.neat_factors = {
            "desk_job": 0.95,      # デスクワーク中心
            "light_job": 1.0,      # 軽い立ち仕事
            "active_job": 1.1,     # 活動的な仕事
            "physical_job": 1.2    # 肉体労働
        }
        
        self.goal_adjustments = {
            "aggressive_cut": -750,    # 急速減量（週0.75kg）
            "moderate_cut": -500,      # 中程度減量（週0.5kg）
            "mild_cut": -250,          # 緩やか減量（週0.25kg）
            "maintenance": 0,          # 維持
            "lean_bulk": 250,          # リーンバルク（週0.25kg）
            "moderate_bulk": 500,      # 中程度増量（週0.5kg）
            "aggressive_bulk": 750     # 急速増量（週0.75kg）
        }
    
    def calculate_bmr_mifflin(self, weight_kg, height_cm, age, gender):
        """Mifflin-St Jeor方程式（最も正確とされる）
        男性: BMR = 10 × 体重(kg) + 6.25 × 身長(cm) - 5 × 年齢 + 5
        女性: BMR = 10 × 体重(kg) + 6.25 × 身長(cm) - 5 × 年齢 - 161
        """
        if gender == 'male':
            return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        else:
            return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    
    def calculate_bmr_harris_benedict(self, weight_kg, height_cm, age, gender):
        """Revised Harris-Benedict方程式
        男性: BMR = 13.397 × 体重(kg) + 4.799 × 身長(cm) - 5.677 × 年齢 + 88.362
        女性: BMR = 9.247 × 体重(kg) + 3.098 × 身長(cm) - 4.330 × 年齢 + 447.593
        """
        if gender == 'male':
            return 13.397 * weight_kg + 4.799 * height_cm - 5.677 * age + 88.362
        else:
            return 9.247 * weight_kg + 3.098 * height_cm - 4.330 * age + 447.593
    
    def calculate_bmr_katch_mcardle(self, weight_kg, body_fat_percentage):
        """Katch-McArdle式（体脂肪率考慮）
        BMR = 370 + 21.6 × 除脂肪体重(kg)
        """
        lean_body_mass = weight_kg * (1 - body_fat_percentage / 100)
        return 370 + 21.6 * lean_body_mass
    
    def calculate_bmr_cunningham(self, weight_kg, body_fat_percentage):
        """Cunningham式（アスリート向け、より高い精度）
        BMR = 500 + 22 × 除脂肪体重(kg)
        """
        lean_body_mass = weight_kg * (1 - body_fat_percentage / 100)
        return 500 + 22 * lean_body_mass
    
    def calculate_all_bmr_methods(self, weight_kg, height_cm, age, gender, body_fat_percentage=None):
        """全ての方法でBMRを計算し比較"""
        results = {
            "mifflin": round(self.calculate_bmr_mifflin(weight_kg, height_cm, age, gender)),
            "harris_benedict": round(self.calculate_bmr_harris_benedict(weight_kg, height_cm, age, gender))
        }
        
        if body_fat_percentage is not None:
            results["katch_mcardle"] = round(self.calculate_bmr_katch_mcardle(weight_kg, body_fat_percentage))
            results["cunningham"] = round(self.calculate_bmr_cunningham(weight_kg, body_fat_percentage))
            
        # 平均値と推奨値
        results["average"] = round(sum(results.values()) / len(results))
        results["recommended"] = results["mifflin"]  # Mifflin-St Jeorが最も正確
        
        return results
    
    def calculate_tdee(self, bmr, activity_level, neat_factor=1.0, tef_percentage=10):
        """総消費カロリー計算（TDEE）
        TDEE = BMR × 活動レベル係数 × NEAT係数 × TEF
        TEF (Thermic Effect of Food) = 食事誘発性熱産生（通常10%）
        """
        base_tdee = bmr * self.activity_multipliers[activity_level]
        tdee_with_neat = base_tdee * neat_factor
        
        # TEF（食事誘発性熱産生）を追加
        tef = tdee_with_neat * (tef_percentage / 100)
        total_tdee = tdee_with_neat + tef
        
        return {
            "base_tdee": round(base_tdee),
            "neat_adjusted": round(tdee_with_neat),
            "tef": round(tef),
            "total_tdee": round(total_tdee)
        }
    
    def calculate_calorie_goals(self, tdee, goal, timeframe_weeks=12, current_weight=None):
        """目標別カロリー設定（安全性チェック付き）"""
        
        # 基本的な調整値を取得
        if goal in self.goal_adjustments:
            adjustment = self.goal_adjustments[goal]
        else:
            # カスタム目標の場合
            adjustment = 0
        
        target_calories = tdee + adjustment
        
        # 安全性チェック
        safety_limits = self._calculate_safety_limits(tdee, goal, current_weight)
        
        # カロリー制限の安全性チェック
        if goal.endswith("cut"):
            # 減量時：BMRを下回らない、TDEEの75%以上
            min_safe_calories = max(safety_limits["min_bmr_estimate"], tdee * 0.75)
            target_calories = max(target_calories, min_safe_calories)
            
        elif goal.endswith("bulk"):
            # 増量時：TDEEの120%以下
            max_safe_calories = tdee * 1.20
            target_calories = min(target_calories, max_safe_calories)
        
        # 週間・月間の体重変化予測
        weekly_change = (adjustment * 7) / 7700  # 1kg = 7700kcal
        total_change = weekly_change * timeframe_weeks
        
        return {
            "target_calories": round(target_calories),
            "adjustment": adjustment,
            "deficit_or_surplus_percentage": round((adjustment / tdee) * 100, 1),
            "description": self._get_goal_description(goal),
            "weekly_weight_change_kg": round(weekly_change, 2),
            "total_change_kg": round(total_change, 1),
            "timeframe_weeks": timeframe_weeks,
            "safety_checked": True,
            "warnings": self._generate_warnings(adjustment, tdee, goal)
        }
    
    def _calculate_safety_limits(self, tdee, goal, current_weight):
        """安全制限の計算"""
        # BMRの推定（TDEEの60-70%と仮定）
        estimated_bmr = tdee * 0.65
        
        # 体重に基づく最大減量ペース（週1%）
        if current_weight:
            max_weekly_loss = current_weight * 0.01 * 7700 / 7  # kcal/day
        else:
            max_weekly_loss = 750  # デフォルト
        
        return {
            "min_bmr_estimate": round(estimated_bmr),
            "max_daily_deficit": round(max_weekly_loss),
            "max_deficit_percentage": 25  # TDEEの最大25%カット
        }
    
    def _get_goal_description(self, goal):
        """目標の説明"""
        descriptions = {
            "aggressive_cut": "急速減量（週0.75kg減）- 短期集中型",
            "moderate_cut": "中程度減量（週0.5kg減）- バランス型",
            "mild_cut": "緩やか減量（週0.25kg減）- 筋肉維持重視",
            "maintenance": "体重維持 - 現状キープ",
            "lean_bulk": "リーンバルク（週0.25kg増）- 脂肪を抑えた増量",
            "moderate_bulk": "中程度増量（週0.5kg増）- 筋肉増量重視",
            "aggressive_bulk": "急速増量（週0.75kg増）- 最大筋肉増加"
        }
        return descriptions.get(goal, "カスタム目標")
    
    def _generate_warnings(self, adjustment, tdee, goal):
        """警告メッセージ生成"""
        warnings = []
        deficit_percentage = abs(adjustment / tdee * 100)
        
        if goal.endswith("cut") and deficit_percentage > 20:
            warnings.append({
                "type": "high_deficit",
                "message": "カロリー不足が大きすぎる可能性があります",
                "recommendation": "TDEEの20%以内の削減を推奨"
            })
        
        if goal == "aggressive_cut":
            warnings.append({
                "type": "muscle_loss_risk",
                "message": "急速な減量は筋肉量減少のリスクがあります",
                "recommendation": "十分なタンパク質摂取と筋トレを継続"
            })
        
        if goal == "aggressive_bulk":
            warnings.append({
                "type": "fat_gain_risk",
                "message": "急速な増量は体脂肪増加のリスクがあります",
                "recommendation": "トレーニング強度を高く保つことを推奨"
            })
        
        return warnings
    
    def calculate_macro_split(self, calories, goal_type):
        """目標に応じたマクロ栄養素の配分計算"""
        # これはNutritionEngineに移動予定
        pass
    
    def estimate_metabolic_adaptation(self, weeks_dieting, initial_tdee, current_deficit):
        """代謝適応の推定（長期ダイエット時）"""
        # 週ごとに約3-5%の代謝低下を想定
        adaptation_rate = 0.04  # 4%/週
        total_adaptation = min(adaptation_rate * weeks_dieting, 0.15)  # 最大15%
        
        adapted_tdee = initial_tdee * (1 - total_adaptation)
        
        return {
            "initial_tdee": round(initial_tdee),
            "adapted_tdee": round(adapted_tdee),
            "adaptation_percentage": round(total_adaptation * 100, 1),
            "recommendation": "リフィード日やダイエット休止を検討" if total_adaptation > 0.10 else "現状維持可能"
        }