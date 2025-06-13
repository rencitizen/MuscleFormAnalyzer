# core/safety_engine.py
"""
安全性チェックシステム
健康リスクの評価、警告生成、安全な目標設定をサポート
"""

class SafetyEngine:
    def __init__(self):
        self.danger_thresholds = {
            # 体脂肪率の危険閾値
            "female_min_bodyfat": 15,
            "female_essential_bodyfat": 10,  # 生命維持に必要な最低値
            "male_min_bodyfat": 8,
            "male_essential_bodyfat": 3,     # 生命維持に必要な最低値
            
            # カロリー制限の閾値
            "max_calorie_deficit_percent": 25,    # TDEEからの最大削減率
            "min_calories_female": 1200,           # 女性の最低摂取カロリー
            "min_calories_male": 1500,             # 男性の最低摂取カロリー
            
            # 体重変化の閾値
            "max_weight_loss_per_week_percent": 1,      # 週間体重の1%
            "max_weight_gain_per_week_percent": 0.5,    # 週間体重の0.5%
            
            # トレーニング量の閾値
            "max_training_hours_per_week": 10,          # 週10時間
            "max_consecutive_training_days": 6,          # 連続6日
            "min_rest_days_per_week": 1,                # 週1日の完全休養
            
            # 栄養素の閾値
            "min_protein_g_per_kg": 0.8,               # 最低タンパク質
            "max_protein_g_per_kg": 3.5,               # 最大タンパク質
            "min_fat_percent_of_calories": 15,          # 最低脂質割合
            "min_carbs_g_per_day": 100,                # 脳機能に必要な最低炭水化物
            
            # 心拍数の閾値
            "max_hr_percentage": 95,                   # 最大心拍数の95%
            "recovery_hr_increase": 10                 # 安静時心拍数の異常上昇
        }
        
        self.health_risk_factors = {
            "extreme_low_bodyfat": {
                "risks": [
                    "免疫機能低下",
                    "ホルモンバランス異常",
                    "骨密度低下",
                    "慢性疲労",
                    "精神的不安定"
                ],
                "female_specific": ["月経不順", "無月経", "不妊リスク"],
                "male_specific": ["テストステロン低下", "性機能障害"]
            },
            "severe_calorie_restriction": {
                "risks": [
                    "基礎代謝低下",
                    "筋肉量減少",
                    "栄養失調",
                    "摂食障害リスク",
                    "リバウンド"
                ]
            },
            "overtraining": {
                "symptoms": [
                    "パフォーマンス低下",
                    "慢性的な筋肉痛",
                    "睡眠障害",
                    "気分の変動",
                    "頻繁な怪我",
                    "免疫力低下"
                ]
            }
        }
    
    def comprehensive_safety_check(self, user_data, goals, plan):
        """包括的安全性チェック"""
        warnings = []
        risk_score = 0
        
        # 1. カロリー摂取の安全性チェック
        calorie_warnings, calorie_risk = self._check_calorie_safety(
            user_data, plan.get("target_calories", 0)
        )
        warnings.extend(calorie_warnings)
        risk_score += calorie_risk
        
        # 2. 体脂肪率目標の安全性チェック
        if goals.get("target_body_fat"):
            bf_warnings, bf_risk = self._check_body_fat_safety(
                goals["target_body_fat"], 
                user_data.get("current_body_fat", 20),
                user_data["gender"]
            )
            warnings.extend(bf_warnings)
            risk_score += bf_risk
        
        # 3. 減量/増量ペースの安全性チェック
        pace_warnings, pace_risk = self._check_weight_change_pace(
            user_data, goals
        )
        warnings.extend(pace_warnings)
        risk_score += pace_risk
        
        # 4. トレーニング量の安全性チェック
        if plan.get("training_plan"):
            training_warnings, training_risk = self._check_training_safety(
                plan["training_plan"], user_data
            )
            warnings.extend(training_warnings)
            risk_score += training_risk
        
        # 5. 栄養バランスの安全性チェック
        if plan.get("nutrition_plan"):
            nutrition_warnings, nutrition_risk = self._check_nutrition_safety(
                plan["nutrition_plan"], user_data
            )
            warnings.extend(nutrition_warnings)
            risk_score += nutrition_risk
        
        # 6. 総合評価とリスクレベル判定
        overall_risk_level = self._calculate_risk_level(risk_score)
        
        # 7. 個別化された推奨事項生成
        recommendations = self._generate_personalized_recommendations(
            warnings, user_data, goals
        )
        
        return {
            "overall_safety": overall_risk_level,
            "risk_score": risk_score,
            "warnings": warnings,
            "recommendations": recommendations,
            "monitoring_plan": self._create_monitoring_plan(overall_risk_level),
            "emergency_signs": self._get_emergency_warning_signs()
        }
    
    def _check_calorie_safety(self, user_data, target_calories):
        """カロリー摂取の安全性チェック"""
        warnings = []
        risk_score = 0
        
        bmr = user_data.get("bmr", 1500)
        tdee = user_data.get("tdee", 2000)
        gender = user_data["gender"]
        
        # BMR以下のチェック
        if target_calories < bmr:
            warnings.append({
                "level": "critical",
                "type": "calorie_below_bmr",
                "message": "目標カロリーが基礎代謝を下回っています",
                "details": f"基礎代謝: {bmr}kcal, 目標: {target_calories}kcal",
                "health_risks": [
                    "代謝の著しい低下",
                    "筋肉量の大幅な減少",
                    "臓器機能への影響",
                    "極度の疲労感"
                ],
                "recommendation": f"最低でも{bmr}kcal以上を摂取してください"
            })
            risk_score += 30
        
        # 最低カロリーチェック
        min_calories = self.danger_thresholds[f"min_calories_{gender}"]
        if target_calories < min_calories:
            warnings.append({
                "level": "danger",
                "type": "below_minimum_calories",
                "message": f"カロリーが推奨最低値（{min_calories}kcal）を下回っています",
                "health_risks": ["栄養不足", "健康障害のリスク"],
                "recommendation": f"{min_calories}kcal以上を維持してください"
            })
            risk_score += 20
        
        # カロリー不足率チェック
        deficit_percentage = ((tdee - target_calories) / tdee) * 100
        if deficit_percentage > self.danger_thresholds["max_calorie_deficit_percent"]:
            warnings.append({
                "level": "warning",
                "type": "high_calorie_deficit",
                "message": f"カロリー不足が{deficit_percentage:.1f}%と大きすぎます",
                "details": f"推奨上限: {self.danger_thresholds['max_calorie_deficit_percent']}%",
                "health_risks": ["持続困難", "リバウンドリスク", "代謝適応"],
                "recommendation": "TDEEの20%以内の削減に留めることを推奨"
            })
            risk_score += 15
        
        return warnings, risk_score
    
    def _check_body_fat_safety(self, target_bf, current_bf, gender):
        """体脂肪率目標の安全性チェック"""
        warnings = []
        risk_score = 0
        
        min_bf = self.danger_thresholds[f"{gender}_min_bodyfat"]
        essential_bf = self.danger_thresholds[f"{gender}_essential_bodyfat"]
        
        # 必須体脂肪率以下
        if target_bf <= essential_bf:
            warnings.append({
                "level": "critical",
                "type": "below_essential_bodyfat",
                "message": f"目標体脂肪率が生命維持に必要な水準（{essential_bf}%）を下回っています",
                "health_risks": self.health_risk_factors["extreme_low_bodyfat"]["risks"] + 
                              self.health_risk_factors["extreme_low_bodyfat"][f"{gender}_specific"],
                "recommendation": "医師の監督なしにこの目標を追求しないでください",
                "immediate_action": "目標の見直しを強く推奨"
            })
            risk_score += 40
        
        # 推奨最低値以下
        elif target_bf <= min_bf:
            warnings.append({
                "level": "danger",
                "type": "extreme_low_bodyfat",
                "message": f"{gender}の推奨最低体脂肪率（{min_bf}%）を下回っています",
                "health_risks": self.health_risk_factors["extreme_low_bodyfat"]["risks"],
                "specific_risks": self.health_risk_factors["extreme_low_bodyfat"][f"{gender}_specific"],
                "recommendation": f"健康維持のため{min_bf + 2}%以上を目標とすることを推奨",
                "monitoring": "定期的な健康チェックが必要"
            })
            risk_score += 25
        
        # 急激な変化
        bf_change = abs(current_bf - target_bf)
        if bf_change > 10:
            warnings.append({
                "level": "warning",
                "type": "rapid_bodyfat_change",
                "message": f"体脂肪率の変化幅（{bf_change:.1f}%）が大きすぎます",
                "health_risks": ["急激な変化による身体への負担", "リバウンドリスク"],
                "recommendation": "3-6ヶ月で5-10%の変化を目標に段階的に進めてください"
            })
            risk_score += 10
        
        return warnings, risk_score
    
    def _check_weight_change_pace(self, user_data, goals):
        """体重変化ペースの安全性チェック"""
        warnings = []
        risk_score = 0
        
        current_weight = user_data.get("weight", 70)
        weekly_change = goals.get("weekly_weight_change", 0)
        
        if weekly_change < 0:  # 減量
            max_loss_kg = current_weight * (self.danger_thresholds["max_weight_loss_per_week_percent"] / 100)
            if abs(weekly_change) > max_loss_kg:
                warnings.append({
                    "level": "warning",
                    "type": "rapid_weight_loss",
                    "message": f"週間減量ペース（{abs(weekly_change):.2f}kg）が速すぎます",
                    "safe_range": f"週{max_loss_kg:.2f}kg以下",
                    "health_risks": [
                        "筋肉量の減少",
                        "基礎代謝の低下",
                        "栄養不足",
                        "リバウンド"
                    ],
                    "recommendation": "週0.5-1.0kgの減量ペースを推奨"
                })
                risk_score += 15
        
        elif weekly_change > 0:  # 増量
            max_gain_kg = current_weight * (self.danger_thresholds["max_weight_gain_per_week_percent"] / 100)
            if weekly_change > max_gain_kg:
                warnings.append({
                    "level": "caution",
                    "type": "rapid_weight_gain",
                    "message": f"週間増量ペース（{weekly_change:.2f}kg）が速すぎます",
                    "safe_range": f"週{max_gain_kg:.2f}kg以下",
                    "health_risks": ["過度な体脂肪増加", "内臓脂肪の蓄積"],
                    "recommendation": "週0.25-0.5kgの増量ペースを推奨"
                })
                risk_score += 10
        
        return warnings, risk_score
    
    def _check_training_safety(self, training_plan, user_data):
        """トレーニング安全性チェック"""
        warnings = []
        risk_score = 0
        
        weekly_hours = training_plan.get("weekly_duration_hours", 0)
        training_days = training_plan.get("frequency_days", 0)
        consecutive_days = training_plan.get("max_consecutive_days", 0)
        
        # 週間トレーニング時間
        if weekly_hours > self.danger_thresholds["max_training_hours_per_week"]:
            warnings.append({
                "level": "warning",
                "type": "excessive_training_volume",
                "message": f"週間トレーニング時間（{weekly_hours}時間）が過度です",
                "safe_range": f"週{self.danger_thresholds['max_training_hours_per_week']}時間以下",
                "health_risks": self.health_risk_factors["overtraining"]["symptoms"],
                "recommendation": "トレーニング量を減らし、回復を重視してください"
            })
            risk_score += 20
        
        # 連続トレーニング日数
        if consecutive_days > self.danger_thresholds["max_consecutive_training_days"]:
            warnings.append({
                "level": "caution",
                "type": "insufficient_rest",
                "message": f"連続トレーニング日数（{consecutive_days}日）が多すぎます",
                "recommendation": "週1-2日の完全休養日を設けてください",
                "recovery_importance": "筋肉の成長と回復は休息中に起こります"
            })
            risk_score += 10
        
        # 初心者の過度なトレーニング
        if user_data.get("experience_level") == "beginner" and training_days > 4:
            warnings.append({
                "level": "caution",
                "type": "beginner_overtraining",
                "message": "初心者には週4日以上のトレーニングは推奨されません",
                "recommendation": "週2-3日から始めて徐々に増やしてください",
                "progression": "最初の3ヶ月は基礎を固めることに集中"
            })
            risk_score += 10
        
        return warnings, risk_score
    
    def _check_nutrition_safety(self, nutrition_plan, user_data):
        """栄養バランスの安全性チェック"""
        warnings = []
        risk_score = 0
        
        weight = user_data.get("weight", 70)
        protein_g = nutrition_plan.get("protein_g", 0)
        fat_calories = nutrition_plan.get("fat_calories", 0)
        total_calories = nutrition_plan.get("total_calories", 2000)
        carbs_g = nutrition_plan.get("carbs_g", 0)
        
        # タンパク質チェック
        protein_per_kg = protein_g / weight
        if protein_per_kg < self.danger_thresholds["min_protein_g_per_kg"]:
            warnings.append({
                "level": "warning",
                "type": "insufficient_protein",
                "message": f"タンパク質摂取量（{protein_per_kg:.1f}g/kg）が不足しています",
                "minimum": f"{self.danger_thresholds['min_protein_g_per_kg']}g/kg",
                "health_risks": ["筋肉量の減少", "回復の遅延", "免疫機能低下"],
                "recommendation": f"体重1kgあたり{1.6}-{2.2}gを目標に"
            })
            risk_score += 10
        elif protein_per_kg > self.danger_thresholds["max_protein_g_per_kg"]:
            warnings.append({
                "level": "caution",
                "type": "excessive_protein",
                "message": f"タンパク質摂取量（{protein_per_kg:.1f}g/kg）が過剰です",
                "maximum": f"{self.danger_thresholds['max_protein_g_per_kg']}g/kg",
                "considerations": ["腎臓への負担", "他の栄養素の不足"],
                "recommendation": "バランスの取れた栄養摂取を心がけてください"
            })
            risk_score += 5
        
        # 脂質チェック
        fat_percentage = (fat_calories / total_calories) * 100
        if fat_percentage < self.danger_thresholds["min_fat_percent_of_calories"]:
            warnings.append({
                "level": "warning",
                "type": "insufficient_fat",
                "message": f"脂質摂取割合（{fat_percentage:.1f}%）が低すぎます",
                "minimum": f"総カロリーの{self.danger_thresholds['min_fat_percent_of_calories']}%以上",
                "health_risks": [
                    "ホルモン生成の障害",
                    "脂溶性ビタミンの吸収不良",
                    "必須脂肪酸の不足"
                ],
                "recommendation": "健康的な脂質源（ナッツ、アボカド、魚）を増やしてください"
            })
            risk_score += 15
        
        # 炭水化物チェック
        if carbs_g < self.danger_thresholds["min_carbs_g_per_day"]:
            warnings.append({
                "level": "caution",
                "type": "low_carbohydrate",
                "message": f"炭水化物摂取量（{carbs_g}g）が少なすぎる可能性があります",
                "minimum": f"{self.danger_thresholds['min_carbs_g_per_day']}g/日",
                "considerations": [
                    "脳機能への影響",
                    "運動パフォーマンスの低下",
                    "ケトーシスのリスク"
                ],
                "recommendation": "特に高強度運動を行う場合は炭水化物を増やすことを検討"
            })
            risk_score += 5
        
        return warnings, risk_score
    
    def _calculate_risk_level(self, risk_score):
        """リスクレベルの判定"""
        if risk_score >= 50:
            return "high_risk"
        elif risk_score >= 30:
            return "moderate_risk"
        elif risk_score >= 15:
            return "low_risk"
        else:
            return "safe"
    
    def _generate_personalized_recommendations(self, warnings, user_data, goals):
        """個別化された推奨事項の生成"""
        recommendations = []
        
        # 警告レベル別の一般的な推奨事項
        critical_warnings = [w for w in warnings if w["level"] == "critical"]
        if critical_warnings:
            recommendations.append({
                "priority": "immediate",
                "action": "計画の全面的な見直し",
                "details": "現在の計画は健康に深刻な影響を与える可能性があります",
                "steps": [
                    "より現実的で安全な目標を設定",
                    "医療専門家への相談を検討",
                    "段階的なアプローチを採用"
                ]
            })
        
        # 特定の問題に対する推奨事項
        for warning in warnings:
            if warning["type"] == "calorie_below_bmr":
                recommendations.append({
                    "priority": "high",
                    "category": "nutrition",
                    "action": "カロリー摂取量の増加",
                    "specific_steps": [
                        f"最低でも基礎代謝量（{user_data.get('bmr', 1500)}kcal）以上を摂取",
                        "週0.5kgの減量ペースに調整",
                        "リフィード日を週1-2回設定"
                    ]
                })
            
            elif warning["type"] == "extreme_low_bodyfat":
                recommendations.append({
                    "priority": "high",
                    "category": "body_composition",
                    "action": "体脂肪率目標の再検討",
                    "specific_steps": [
                        "より健康的な体脂肪率範囲を目標に",
                        "段階的な目標設定（3ヶ月ごとに3-5%）",
                        "定期的な健康診断の実施"
                    ]
                })
            
            elif warning["type"] == "excessive_training_volume":
                recommendations.append({
                    "priority": "medium",
                    "category": "training",
                    "action": "トレーニング量の調整",
                    "specific_steps": [
                        "週4-5回、1回60-75分に制限",
                        "高強度日と低強度日を交互に",
                        "4週ごとにディロード週を設定"
                    ]
                })
        
        # ポジティブな推奨事項も追加
        if not critical_warnings:
            recommendations.append({
                "priority": "general",
                "category": "monitoring",
                "action": "進捗の定期的なモニタリング",
                "specific_steps": [
                    "週1回の体重・体脂肪率測定",
                    "トレーニング記録の継続",
                    "体調や気分の記録",
                    "月1回の計画見直し"
                ]
            })
        
        return recommendations
    
    def _create_monitoring_plan(self, risk_level):
        """リスクレベルに応じたモニタリング計画"""
        monitoring_plans = {
            "high_risk": {
                "frequency": "毎日",
                "metrics": [
                    "体調・エネルギーレベル",
                    "睡眠の質と時間",
                    "安静時心拍数",
                    "気分・モチベーション",
                    "筋肉痛・疲労度"
                ],
                "professional_support": "医師や栄養士への定期相談を推奨",
                "adjustment_frequency": "週1回の計画見直し"
            },
            "moderate_risk": {
                "frequency": "週3-4回",
                "metrics": [
                    "体重・体脂肪率",
                    "トレーニングパフォーマンス",
                    "回復状況",
                    "栄養摂取状況"
                ],
                "check_ins": "2週間ごとの自己評価",
                "adjustment_frequency": "2週間ごとの計画微調整"
            },
            "low_risk": {
                "frequency": "週1-2回",
                "metrics": [
                    "体重変化",
                    "主観的な体調",
                    "トレーニング進捗"
                ],
                "review": "月1回の総合評価"
            },
            "safe": {
                "frequency": "週1回",
                "metrics": ["基本的な健康指標", "目標達成度"],
                "focus": "継続性と長期的な進歩"
            }
        }
        
        return monitoring_plans.get(risk_level, monitoring_plans["safe"])
    
    def _get_emergency_warning_signs(self):
        """緊急警告サイン"""
        return {
            "immediate_medical_attention": [
                "胸痛や呼吸困難",
                "めまいや失神",
                "異常な心拍（不整脈）",
                "極度の脱水症状"
            ],
            "stop_and_reassess": [
                "持続的な疲労感（1週間以上）",
                "慢性的な不眠",
                "食欲の完全な喪失",
                "気分の激しい変動",
                "頻繁な怪我や病気"
            ],
            "modify_program": [
                "パフォーマンスの継続的低下",
                "回復の遅延",
                "モチベーションの著しい低下",
                "関節や筋肉の慢性的な痛み"
            ],
            "hormonal_warning_signs": {
                "female": [
                    "月経周期の乱れ",
                    "無月経（3ヶ月以上）",
                    "極度の冷え性",
                    "脱毛"
                ],
                "male": [
                    "性欲の著しい低下",
                    "朝の勃起の消失",
                    "筋力の急激な低下"
                ]
            }
        }
    
    def generate_safety_report(self, user_data, goals, plan, analysis_results):
        """包括的な安全性レポート生成"""
        safety_check = self.comprehensive_safety_check(user_data, goals, plan)
        
        report = {
            "report_date": "2024-01-20",  # 実際の実装では現在日付
            "user_profile": {
                "age": user_data.get("age"),
                "gender": user_data.get("gender"),
                "experience_level": user_data.get("experience_level"),
                "health_conditions": user_data.get("health_conditions", [])
            },
            "safety_assessment": safety_check,
            "risk_factors_identified": len(safety_check["warnings"]),
            "highest_priority_issues": [
                w for w in safety_check["warnings"] 
                if w["level"] in ["critical", "danger"]
            ],
            "action_plan": {
                "immediate_actions": [
                    r for r in safety_check["recommendations"] 
                    if r.get("priority") == "immediate"
                ],
                "short_term_modifications": [
                    r for r in safety_check["recommendations"] 
                    if r.get("priority") == "high"
                ],
                "monitoring_requirements": safety_check["monitoring_plan"]
            },
            "professional_consultation_recommended": 
                safety_check["overall_safety"] in ["high_risk", "moderate_risk"],
            "next_review_date": self._calculate_next_review_date(
                safety_check["overall_safety"]
            )
        }
        
        return report
    
    def _calculate_next_review_date(self, risk_level):
        """次回レビュー日の計算"""
        review_intervals = {
            "high_risk": "1週間後",
            "moderate_risk": "2週間後",
            "low_risk": "1ヶ月後",
            "safe": "3ヶ月後"
        }
        return review_intervals.get(risk_level, "1ヶ月後")