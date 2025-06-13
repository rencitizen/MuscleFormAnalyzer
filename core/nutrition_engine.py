# core/nutrition_engine.py
"""
栄養素計算エンジン
PFCバランス、タンパク質必要量、微量栄養素の科学的計算を提供
"""

class NutritionEngine:
    def __init__(self):
        self.pfc_ratios = {
            "general_training": {"protein": 0.25, "fat": 0.20, "carbs": 0.55},
            "bulking": {"protein": 0.30, "fat": 0.25, "carbs": 0.45},
            "cutting": {"protein": 0.30, "fat": 0.20, "carbs": 0.50},
            "ketogenic": {"protein": 0.25, "fat": 0.70, "carbs": 0.05},
            "low_carb": {"protein": 0.30, "fat": 0.45, "carbs": 0.25},
            "balanced": {"protein": 0.25, "fat": 0.25, "carbs": 0.50},
            "endurance": {"protein": 0.20, "fat": 0.20, "carbs": 0.60}
        }
        
        self.protein_recommendations = {
            "sedentary": 0.8,           # g/kg体重 - 座りがち
            "general_training": 2.0,     # 一般的なトレーニング
            "muscle_gain": 2.8,          # 筋肉増量期
            "cutting": 3.1,              # 減量期（筋肉維持）
            "endurance": 1.6,            # 持久系アスリート
            "strength_athlete": 2.5      # パワー系アスリート
        }
        
        self.micronutrients = {
            "vitamin_c": {
                "daily_min": 1000, 
                "daily_max": 5000, 
                "unit": "mg",
                "benefits": "免疫機能、回復促進、抗酸化作用"
            },
            "zinc": {
                "daily_min": 30, 
                "unit": "mg",
                "benefits": "テストステロン生成、免疫機能、タンパク質合成"
            },
            "magnesium": {
                "daily_min": 200, 
                "unit": "mg",
                "benefits": "筋肉機能、エネルギー代謝、睡眠の質"
            },
            "vitamin_d": {
                "daily_min": 2000,
                "unit": "IU",
                "benefits": "筋肉機能、骨密度、免疫機能"
            },
            "omega_3": {
                "daily_min": 3,
                "unit": "g",
                "benefits": "炎症抑制、回復促進、心血管健康"
            },
            "creatine": {
                "daily_min": 5,
                "unit": "g",
                "benefits": "筋力向上、筋肉量増加、回復促進"
            }
        }
        
        self.meal_timing_templates = {
            "general": {
                "meals": 4,
                "distribution": [0.25, 0.30, 0.25, 0.20],
                "timing": ["朝食", "昼食", "夕食", "間食/就寝前"]
            },
            "intermittent_fasting": {
                "meals": 2,
                "distribution": [0.40, 0.60],
                "timing": ["昼食(12:00)", "夕食(18:00)"],
                "fasting_window": 16
            },
            "bodybuilding": {
                "meals": 6,
                "distribution": [0.15, 0.20, 0.15, 0.20, 0.15, 0.15],
                "timing": ["朝食", "間食1", "昼食", "トレ前後", "夕食", "就寝前"]
            }
        }
    
    def calculate_pfc_macros(self, total_calories, goal, custom_ratios=None):
        """PFCバランス計算"""
        if custom_ratios:
            ratios = custom_ratios
        else:
            ratios = self.pfc_ratios.get(goal, self.pfc_ratios["balanced"])
        
        # カロリーから各栄養素のグラム数を計算
        protein_calories = total_calories * ratios["protein"]
        fat_calories = total_calories * ratios["fat"] 
        carb_calories = total_calories * ratios["carbs"]
        
        # グラム換算（タンパク質:4kcal/g、脂質:9kcal/g、炭水化物:4kcal/g）
        protein_g = protein_calories / 4
        fat_g = fat_calories / 9
        carbs_g = carb_calories / 4
        
        return {
            "protein_g": round(protein_g),
            "fat_g": round(fat_g),
            "carbs_g": round(carbs_g),
            "protein_calories": round(protein_calories),
            "fat_calories": round(fat_calories),
            "carbs_calories": round(carb_calories),
            "protein_ratio": round(ratios["protein"] * 100),
            "fat_ratio": round(ratios["fat"] * 100),
            "carbs_ratio": round(ratios["carbs"] * 100),
            "fiber_g": round(total_calories / 1000 * 14),  # 1000kcalあたり14g推奨
            "sugar_limit_g": round(total_calories * 0.10 / 4)  # 総カロリーの10%以下
        }
    
    def calculate_protein_needs(self, weight_kg, goal, activity_level, body_fat_percentage=None):
        """タンパク質必要量計算（最新の研究に基づく）"""
        
        # 除脂肪体重ベースの計算（より正確）
        if body_fat_percentage is not None:
            lean_mass = weight_kg * (1 - body_fat_percentage / 100)
            base_weight = lean_mass
        else:
            base_weight = weight_kg
        
        # 目標別の必要量
        if goal == "cutting":
            protein_per_kg = self.protein_recommendations["cutting"]
        elif goal in ["bulking", "muscle_gain"]:
            protein_per_kg = self.protein_recommendations["muscle_gain"]
        elif activity_level == "very_active":
            protein_per_kg = self.protein_recommendations["strength_athlete"]
        else:
            protein_per_kg = self.protein_recommendations["general_training"]
        
        total_protein = base_weight * protein_per_kg
        
        # 摂取タイミングの最適化
        meal_timing = self._optimize_protein_timing(total_protein)
        
        return {
            "daily_total_g": round(total_protein),
            "per_kg_body_weight": round(protein_per_kg, 1),
            "per_kg_lean_mass": round(total_protein / base_weight, 1) if body_fat_percentage else None,
            "minimum_g": round(base_weight * 1.6),  # 最低推奨量
            "maximum_g": round(base_weight * 3.5),  # 安全上限
            "meal_distribution": meal_timing,
            "leucine_threshold_per_meal": 3,  # 筋タンパク質合成の閾値
            "timing_recommendations": [
                "起床後1時間以内",
                "トレーニング前後2時間以内",
                "就寝前30分（カゼインプロテイン推奨）",
                "3-4時間ごとに分散摂取"
            ]
        }
    
    def _optimize_protein_timing(self, total_protein_g):
        """タンパク質摂取タイミングの最適化"""
        # 1回の摂取で効率的に利用できる量は20-40g
        optimal_per_meal = min(40, max(20, total_protein_g / 4))
        num_meals = round(total_protein_g / optimal_per_meal)
        
        distribution = []
        remaining = total_protein_g
        
        for i in range(num_meals):
            if i == num_meals - 1:
                amount = remaining
            else:
                amount = min(optimal_per_meal, remaining)
            distribution.append(round(amount))
            remaining -= amount
        
        return {
            "meals_per_day": num_meals,
            "per_meal_g": distribution,
            "optimal_spacing_hours": 3-4
        }
    
    def calculate_pre_post_workout_nutrition(self, workout_duration_minutes, workout_intensity):
        """トレーニング前後の栄養摂取計画"""
        
        # トレーニング前（1-2時間前）
        pre_workout = {
            "timing": "トレーニング1-2時間前",
            "carbs_g": 30 if workout_intensity == "high" else 20,
            "protein_g": 20,
            "fat_g": 5,  # 最小限に
            "hydration_ml": 500,
            "example_foods": [
                "バナナ1本 + プロテインシェイク",
                "オートミール50g + ギリシャヨーグルト",
                "全粒粉パン + 鶏胸肉"
            ]
        }
        
        # トレーニング中
        during_workout = {
            "needed": workout_duration_minutes > 60,
            "carbs_g": 30 if workout_duration_minutes > 90 else 15,
            "hydration_ml": 150 * (workout_duration_minutes / 15),
            "electrolytes": workout_duration_minutes > 60
        }
        
        # トレーニング後（30分以内）
        post_workout = {
            "timing": "トレーニング後30分以内（ゴールデンタイム）",
            "carbs_g": 50 if workout_intensity == "high" else 30,
            "protein_g": 30,
            "carb_protein_ratio": "2:1〜3:1",
            "example_meals": [
                "プロテインシェイク + バナナ2本",
                "チョコレートミルク500ml",
                "白米150g + 鶏胸肉100g"
            ]
        }
        
        return {
            "pre_workout": pre_workout,
            "during_workout": during_workout,
            "post_workout": post_workout,
            "total_workout_calories": self._estimate_workout_nutrition_calories(
                pre_workout, during_workout, post_workout
            )
        }
    
    def _estimate_workout_nutrition_calories(self, pre, during, post):
        """ワークアウト栄養の総カロリー計算"""
        pre_cal = (pre["carbs_g"] * 4) + (pre["protein_g"] * 4) + (pre["fat_g"] * 9)
        during_cal = during["carbs_g"] * 4 if during["needed"] else 0
        post_cal = (post["carbs_g"] * 4) + (post["protein_g"] * 4)
        
        return {
            "pre_workout_cal": round(pre_cal),
            "during_workout_cal": round(during_cal),
            "post_workout_cal": round(post_cal),
            "total_cal": round(pre_cal + during_cal + post_cal)
        }
    
    def get_high_protein_foods(self):
        """高タンパク質食品データベース（日本の食品を含む）"""
        return {
            "meat": [
                {"name": "鶏胸肉(皮なし)", "protein_per_100g": 23, "calories_per_100g": 108, 
                 "benefits": "低脂質、高BCAA、カルノシン含有"},
                {"name": "鶏ささみ", "protein_per_100g": 25, "calories_per_100g": 114,
                 "benefits": "最低脂質、消化が良い"},
                {"name": "赤身牛肉", "protein_per_100g": 22, "calories_per_100g": 182,
                 "benefits": "クレアチン、亜鉛、ビタミンB12豊富"},
                {"name": "豚ヒレ肉", "protein_per_100g": 22, "calories_per_100g": 115,
                 "benefits": "ビタミンB1豊富、低脂質"}
            ],
            "fish": [
                {"name": "サーモン", "protein_per_100g": 20, "calories_per_100g": 200,
                 "benefits": "オメガ3脂肪酸、ビタミンD豊富"},
                {"name": "サバ缶(水煮)", "protein_per_100g": 21, "calories_per_100g": 180,
                 "benefits": "手軽、オメガ3、保存性高い"},
                {"name": "マグロ(赤身)", "protein_per_100g": 24, "calories_per_100g": 106,
                 "benefits": "低脂質、ビタミンB6豊富"},
                {"name": "タラ", "protein_per_100g": 18, "calories_per_100g": 75,
                 "benefits": "超低脂質、消化に優しい"}
            ],
            "plant": [
                {"name": "納豆", "protein_per_100g": 17, "calories_per_100g": 200,
                 "benefits": "発酵食品、ビタミンK2、腸内環境改善"},
                {"name": "木綿豆腐", "protein_per_100g": 7, "calories_per_100g": 72,
                 "benefits": "植物性、低カロリー、イソフラボン"},
                {"name": "枝豆", "protein_per_100g": 12, "calories_per_100g": 135,
                 "benefits": "食物繊維、葉酸豊富"},
                {"name": "ブロッコリー", "protein_per_100g": 4, "calories_per_100g": 33,
                 "benefits": "ビタミンC、抗酸化物質豊富"}
            ],
            "dairy": [
                {"name": "ゆで卵", "protein_per_100g": 13, "calories_per_100g": 151,
                 "benefits": "完全栄養食、ビタミンD、コリン"},
                {"name": "ギリシャヨーグルト", "protein_per_100g": 10, "calories_per_100g": 90,
                 "benefits": "プロバイオティクス、カルシウム"},
                {"name": "カッテージチーズ", "protein_per_100g": 11, "calories_per_100g": 98,
                 "benefits": "カゼインプロテイン、低脂質"},
                {"name": "無脂肪乳", "protein_per_100g": 3.4, "calories_per_100g": 33,
                 "benefits": "低カロリー、カルシウム豊富"}
            ],
            "supplements": [
                {"name": "ホエイプロテイン", "protein_per_100g": 80, "calories_per_100g": 380,
                 "benefits": "高吸収率、BCAA豊富、便利"},
                {"name": "カゼインプロテイン", "protein_per_100g": 75, "calories_per_100g": 360,
                 "benefits": "徐放性、就寝前に最適"},
                {"name": "ソイプロテイン", "protein_per_100g": 85, "calories_per_100g": 380,
                 "benefits": "植物性、乳糖不耐症対応"}
            ]
        }
    
    def generate_sample_meal_plan(self, daily_calories, pfc_macros, meal_timing="general"):
        """サンプル食事プラン生成"""
        timing_template = self.meal_timing_templates[meal_timing]
        meals = []
        
        for i, (timing, distribution) in enumerate(zip(
            timing_template["timing"], 
            timing_template["distribution"]
        )):
            meal_calories = daily_calories * distribution
            meal_protein = pfc_macros["protein_g"] * distribution
            meal_carbs = pfc_macros["carbs_g"] * distribution
            meal_fat = pfc_macros["fat_g"] * distribution
            
            meals.append({
                "meal_number": i + 1,
                "timing": timing,
                "calories": round(meal_calories),
                "protein_g": round(meal_protein),
                "carbs_g": round(meal_carbs),
                "fat_g": round(meal_fat),
                "sample_foods": self._generate_meal_suggestions(
                    meal_protein, meal_carbs, meal_fat, timing
                )
            })
        
        return {
            "meal_plan": meals,
            "total_meals": len(meals),
            "meal_frequency": f"{len(meals)}食/日",
            "hydration_recommendation": "体重1kgあたり35-40ml（運動時は追加）"
        }
    
    def _generate_meal_suggestions(self, protein_g, carbs_g, fat_g, meal_timing):
        """食事の具体例を生成"""
        suggestions = []
        
        if "朝" in meal_timing:
            suggestions = [
                f"卵2個 + オートミール{round(carbs_g/0.6)}g + アボカド1/4個",
                f"プロテインスムージー + バナナ + アーモンド{round(fat_g/0.5)}g",
                f"ギリシャヨーグルト200g + グラノーラ + ベリー類"
            ]
        elif "昼" in meal_timing:
            suggestions = [
                f"鶏胸肉{round(protein_g/0.23)}g + 玄米{round(carbs_g/0.3)}g + サラダ",
                f"サーモン{round(protein_g/0.20)}g + さつまいも + ブロッコリー",
                f"豆腐ボウル + 雑穀米 + 野菜炒め"
            ]
        elif "夕" in meal_timing:
            suggestions = [
                f"赤身牛肉{round(protein_g/0.22)}g + 野菜スープ + サラダ",
                f"白身魚{round(protein_g/0.18)}g + 野菜たっぷり鍋",
                f"鶏もも肉（皮なし） + 温野菜 + 味噌汁"
            ]
        else:  # 間食・就寝前
            suggestions = [
                f"プロテインシェイク + ナッツ{round(fat_g/0.5)}g",
                f"ギリシャヨーグルト + アーモンド",
                f"カッテージチーズ + くるみ"
            ]
        
        return suggestions