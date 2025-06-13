# core/body_composition_engine.py
"""
科学的身体組成分析エンジン
BMI計算、体脂肪率推定、健康リスク評価を提供
"""

class BodyCompositionEngine:
    def __init__(self):
        self.bmi_thresholds = {
            "underweight": 18.5,
            "normal": 24.0,
            "overweight": 25.0,
            "obese_1": 30.0,
            "obese_2": 35.0
        }
        
        self.female_bodyfat_ranges = {
            "athlete": {"min": 0, "max": 15, "health_risk": "high"},
            "fitness": {"min": 16, "max": 20, "health_risk": "low"},
            "healthy": {"min": 21, "max": 25, "health_risk": "none"},
            "curvy": {"min": 26, "max": 30, "health_risk": "low"},
            "overweight": {"min": 31, "max": 35, "health_risk": "medium"},
            "obese": {"min": 36, "max": 100, "health_risk": "high"}
        }
        
        self.male_bodyfat_ranges = {
            "athlete": {"min": 0, "max": 8, "health_risk": "high"},
            "fitness": {"min": 9, "max": 13, "health_risk": "low"},
            "healthy": {"min": 14, "max": 17, "health_risk": "none"},
            "average": {"min": 18, "max": 24, "health_risk": "low"},
            "overweight": {"min": 25, "max": 30, "health_risk": "medium"},
            "obese": {"min": 31, "max": 100, "health_risk": "high"}
        }
    
    def calculate_bmi(self, weight_kg, height_cm):
        """BMI計算 (kg/m²)"""
        height_m = height_cm / 100
        return weight_kg / (height_m ** 2)
    
    def get_bmi_category(self, bmi):
        """BMIカテゴリー判定"""
        if bmi < self.bmi_thresholds["underweight"]:
            return "underweight"
        elif bmi < self.bmi_thresholds["normal"]:
            return "normal"
        elif bmi < self.bmi_thresholds["overweight"]:
            return "overweight"
        elif bmi < self.bmi_thresholds["obese_1"]:
            return "obese_1"
        elif bmi < self.bmi_thresholds["obese_2"]:
            return "obese_2"
        else:
            return "obese_3"
    
    def estimate_body_fat_tanita(self, weight_kg, height_cm, age, gender):
        """タニタ式体脂肪率推定
        体脂肪率 = 1.2×BMI + 0.23×年齢 - 10.8×性別 - 5.4
        """
        bmi = self.calculate_bmi(weight_kg, height_cm)
        gender_value = 1 if gender == 'male' else 0
        body_fat = 1.2 * bmi + 0.23 * age - 10.8 * gender_value - 5.4
        return max(0, body_fat)  # 負の値を防ぐ
    
    def estimate_body_fat_navy(self, waist_cm, neck_cm, height_cm, hip_cm=None, gender='male'):
        """米海軍式体脂肪率推定（より正確）"""
        import math
        
        if gender == 'male':
            # 男性用: %BF = 495/(1.0324-0.19077*log10(waist-neck)+0.15456*log10(height))-450
            body_fat = 495 / (1.0324 - 0.19077 * math.log10(waist_cm - neck_cm) + 
                            0.15456 * math.log10(height_cm)) - 450
        else:
            # 女性用: %BF = 495/(1.29579-0.35004*log10(waist+hip-neck)+0.22100*log10(height))-450
            if hip_cm is None:
                raise ValueError("女性の体脂肪率計算にはヒップサイズが必要です")
            body_fat = 495 / (1.29579 - 0.35004 * math.log10(waist_cm + hip_cm - neck_cm) + 
                            0.22100 * math.log10(height_cm)) - 450
        
        return max(0, min(60, body_fat))  # 0-60%の範囲に制限
    
    def map_visual_to_bodyfat(self, visual_selection, gender):
        """視覚的体型選択から体脂肪率への変換"""
        if gender == 'female':
            return self.female_bodyfat_ranges.get(visual_selection, {"min": 25, "max": 30})
        else:
            return self.male_bodyfat_ranges.get(visual_selection, {"min": 18, "max": 24})
    
    def calculate_lean_body_mass(self, weight_kg, body_fat_percentage):
        """除脂肪体重の計算"""
        fat_mass = weight_kg * (body_fat_percentage / 100)
        lean_mass = weight_kg - fat_mass
        return {
            "lean_mass_kg": round(lean_mass, 1),
            "fat_mass_kg": round(fat_mass, 1),
            "lean_mass_percentage": round(100 - body_fat_percentage, 1)
        }
    
    def calculate_ffmi(self, weight_kg, height_cm, body_fat_percentage):
        """FFMI (Fat-Free Mass Index) 計算 - 筋肉量の指標"""
        lean_mass = weight_kg * (1 - body_fat_percentage / 100)
        height_m = height_cm / 100
        ffmi = lean_mass / (height_m ** 2)
        
        # 身長補正FFMI
        normalized_ffmi = ffmi + 6.1 * (1.8 - height_m)
        
        return {
            "ffmi": round(ffmi, 1),
            "normalized_ffmi": round(normalized_ffmi, 1),
            "interpretation": self._interpret_ffmi(normalized_ffmi)
        }
    
    def _interpret_ffmi(self, ffmi):
        """FFMI解釈"""
        if ffmi < 18:
            return "筋肉量が少ない"
        elif ffmi < 20:
            return "平均的な筋肉量"
        elif ffmi < 22:
            return "筋肉量が多い"
        elif ffmi < 25:
            return "非常に筋肉量が多い（自然な上限）"
        else:
            return "極めて高い筋肉量"
    
    def generate_health_warnings(self, target_bodyfat, current_bodyfat, gender):
        """健康リスク警告生成"""
        warnings = []
        
        # 女性の最低体脂肪率警告
        if gender == 'female' and target_bodyfat <= 15:
            warnings.append({
                "level": "danger",
                "message": "女性の体脂肪率15%以下は健康リスクを伴います",
                "details": "免疫力低下、月経不順、ホルモンバランスの乱れの可能性",
                "recommendations": [
                    "最低でも16-17%を維持することを推奨",
                    "医師や栄養士に相談することを検討",
                    "定期的な健康チェックを実施"
                ]
            })
        
        # 男性の最低体脂肪率警告
        if gender == 'male' and target_bodyfat <= 8:
            warnings.append({
                "level": "danger", 
                "message": "男性の体脂肪率8%以下は健康リスクを伴います",
                "details": "維持が非常に困難で、健康への悪影響の可能性",
                "recommendations": [
                    "9-10%を最低ラインとすることを推奨",
                    "競技者でない限り12-15%が健康的",
                    "極端な減量は避ける"
                ]
            })
        
        # 急激な体脂肪率変化の警告
        if abs(target_bodyfat - current_bodyfat) > 10:
            warnings.append({
                "level": "warning",
                "message": "目標と現在の体脂肪率の差が大きすぎます",
                "details": "急激な変化は健康リスクとリバウンドの原因になります",
                "recommendations": [
                    "3-6ヶ月で5-10%の変化を目標に",
                    "段階的な目標設定を推奨",
                    "持続可能なペースで進める"
                ]
            })
        
        return warnings
    
    def calculate_ideal_weight_range(self, height_cm, gender):
        """理想体重範囲の計算（複数の方法）"""
        height_m = height_cm / 100
        
        # BMI法（18.5-24.0）
        min_weight_bmi = 18.5 * (height_m ** 2)
        max_weight_bmi = 24.0 * (height_m ** 2)
        
        # Devine式
        if gender == 'male':
            ideal_weight_devine = 50 + 2.3 * ((height_cm / 2.54) - 60)
        else:
            ideal_weight_devine = 45.5 + 2.3 * ((height_cm / 2.54) - 60)
        
        # Robinson式
        if gender == 'male':
            ideal_weight_robinson = 52 + 1.9 * ((height_cm / 2.54) - 60)
        else:
            ideal_weight_robinson = 49 + 1.7 * ((height_cm / 2.54) - 60)
        
        return {
            "bmi_range": {
                "min": round(min_weight_bmi, 1),
                "max": round(max_weight_bmi, 1)
            },
            "devine_ideal": round(ideal_weight_devine, 1),
            "robinson_ideal": round(ideal_weight_robinson, 1),
            "recommended_range": {
                "min": round(min(ideal_weight_devine, ideal_weight_robinson) * 0.9, 1),
                "max": round(max(ideal_weight_devine, ideal_weight_robinson) * 1.1, 1)
            }
        }