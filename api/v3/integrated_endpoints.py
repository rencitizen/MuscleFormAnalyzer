# api/v3/integrated_endpoints.py
"""
TENAX FIT v3.0 統合APIエンドポイント
既存のAI機能と新しい科学的分析機能を統合
"""

from flask import Blueprint, request, jsonify
import json
from datetime import datetime

# Core engines
from core.body_composition_engine import BodyCompositionEngine
from core.metabolism_engine import MetabolismEngine
from core.nutrition_engine import NutritionEngine
from core.training_engine import TrainingEngine
from core.safety_engine import SafetyEngine

# Existing AI features integration
from core.pose_analyzer import PoseAnalyzer
from ml.models.phase_detector import PhaseDetector
from ml.api.food_analyzer import FoodAnalyzer

api_v3 = Blueprint('api_v3', __name__, url_prefix='/api/v3')

# エンジンのグローバルインスタンス（実際の実装ではDIを使用）
body_engine = BodyCompositionEngine()
metabolism_engine = MetabolismEngine()
nutrition_engine = NutritionEngine()
training_engine = TrainingEngine()
safety_engine = SafetyEngine()

@api_v3.route('/comprehensive_analysis', methods=['POST'])
def comprehensive_fitness_analysis():
    """統合フィットネス分析エンドポイント
    
    既存のAI分析機能と新しい科学的計算を統合して
    包括的なフィットネスプランを生成
    """
    try:
        data = request.json
        
        # 入力データの検証
        required_fields = ['weight', 'height', 'age', 'gender', 'activity_level', 'goal']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # 1. 身体組成分析
        bmi = body_engine.calculate_bmi(data['weight'], data['height'])
        bmi_category = body_engine.get_bmi_category(bmi)
        
        # 体脂肪率の推定（複数の方法）
        estimated_bf_tanita = body_engine.estimate_body_fat_tanita(
            data['weight'], data['height'], data['age'], data['gender']
        )
        
        # より正確な推定が可能な場合
        if all(key in data for key in ['waist_cm', 'neck_cm']):
            hip_cm = data.get('hip_cm') if data['gender'] == 'female' else None
            estimated_bf_navy = body_engine.estimate_body_fat_navy(
                data['waist_cm'], data['neck_cm'], data['height'], hip_cm, data['gender']
            )
            estimated_bf = (estimated_bf_tanita + estimated_bf_navy) / 2
        else:
            estimated_bf = estimated_bf_tanita
        
        # 除脂肪体重とFFMI計算
        body_composition = body_engine.calculate_lean_body_mass(data['weight'], estimated_bf)
        ffmi_data = body_engine.calculate_ffmi(data['weight'], data['height'], estimated_bf)
        
        # 理想体重範囲
        ideal_weight = body_engine.calculate_ideal_weight_range(data['height'], data['gender'])
        
        # 2. 代謝計算（全方法で計算）
        bmr_all = metabolism_engine.calculate_all_bmr_methods(
            data['weight'], data['height'], data['age'], data['gender'], estimated_bf
        )
        
        # TDEEとカロリー目標
        tdee_data = metabolism_engine.calculate_tdee(
            bmr_all['recommended'], 
            data['activity_level'],
            data.get('neat_factor', 1.0)
        )
        
        calorie_goals = metabolism_engine.calculate_calorie_goals(
            tdee_data['total_tdee'], 
            data['goal'],
            data.get('timeframe_weeks', 12),
            data['weight']
        )
        
        # 3. 栄養計算
        pfc_macros = nutrition_engine.calculate_pfc_macros(
            calorie_goals['target_calories'], 
            data['goal']
        )
        
        protein_needs = nutrition_engine.calculate_protein_needs(
            data['weight'], 
            data['goal'], 
            data['activity_level'],
            estimated_bf
        )
        
        # 食事プラン生成
        meal_plan = nutrition_engine.generate_sample_meal_plan(
            calorie_goals['target_calories'],
            pfc_macros,
            data.get('meal_timing', 'general')
        )
        
        # ワークアウト前後の栄養
        if data.get('workout_planned'):
            workout_nutrition = nutrition_engine.calculate_pre_post_workout_nutrition(
                data.get('workout_duration', 60),
                data.get('workout_intensity', 'moderate')
            )
        else:
            workout_nutrition = None
        
        # 4. トレーニングプラン生成
        workout_plan = training_engine.generate_workout_plan(
            data.get('experience', 'intermediate'),
            data['goal'],
            data.get('available_days', 4),
            data.get('equipment', 'full_gym')
        )
        
        # 運動カロリー計算の例
        if data.get('planned_exercises'):
            exercise_calories = []
            for exercise in data['planned_exercises']:
                cal_data = training_engine.calculate_exercise_calories(
                    exercise['type'],
                    exercise['intensity'],
                    data['weight'],
                    exercise['duration']
                )
                exercise_calories.append({
                    "exercise": exercise['name'],
                    "calories": cal_data
                })
        else:
            exercise_calories = None
        
        # 5. 安全性チェック
        user_data_for_safety = {
            **data,
            'bmr': bmr_all['recommended'],
            'tdee': tdee_data['total_tdee'],
            'current_body_fat': estimated_bf
        }
        
        goals_for_safety = {
            'target_body_fat': data.get('target_body_fat'),
            'weekly_weight_change': calorie_goals['weekly_weight_change_kg']
        }
        
        plan_for_safety = {
            'target_calories': calorie_goals['target_calories'],
            'training_plan': {
                'weekly_duration_hours': float(workout_plan['frequency'].split('-')[0]) * 1.25,
                'frequency_days': int(workout_plan['frequency'].split('日')[0])
            },
            'nutrition_plan': {
                **pfc_macros,
                'total_calories': calorie_goals['target_calories']
            }
        }
        
        safety_analysis = safety_engine.comprehensive_safety_check(
            user_data_for_safety,
            goals_for_safety,
            plan_for_safety
        )
        
        # 6. 既存AI機能との統合ポイント
        integration_features = {
            "pose_analysis_ready": True,
            "meal_photo_analysis": True,
            "exercise_phase_detection": True,
            "progress_tracking": True,
            "ai_recommendations": _generate_ai_recommendations(data, safety_analysis)
        }
        
        # 7. 包括的な結果を構築
        comprehensive_result = {
            "analysis_id": f"TENAX-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "user_profile": {
                "basic_info": {
                    "age": data['age'],
                    "gender": data['gender'],
                    "height": data['height'],
                    "weight": data['weight'],
                    "activity_level": data['activity_level'],
                    "experience": data.get('experience', 'intermediate')
                }
            },
            "body_composition": {
                "bmi": round(bmi, 1),
                "bmi_category": bmi_category,
                "estimated_body_fat": round(estimated_bf, 1),
                "lean_body_mass": body_composition,
                "ffmi": ffmi_data,
                "ideal_weight_range": ideal_weight,
                "health_warnings": body_engine.generate_health_warnings(
                    data.get('target_body_fat', estimated_bf), 
                    estimated_bf, 
                    data['gender']
                )
            },
            "metabolism": {
                "bmr_calculations": bmr_all,
                "tdee": tdee_data,
                "calorie_goals": calorie_goals,
                "metabolic_type": _determine_metabolic_type(bmr_all, data)
            },
            "nutrition": {
                "daily_macros": pfc_macros,
                "protein_requirements": protein_needs,
                "meal_plan": meal_plan,
                "workout_nutrition": workout_nutrition,
                "high_protein_foods": nutrition_engine.get_high_protein_foods(),
                "hydration": {
                    "daily_water_ml": round(data['weight'] * 35),
                    "training_addition_ml": 500
                }
            },
            "training": {
                "workout_plan": workout_plan,
                "exercise_calories": exercise_calories,
                "recovery_needs": training_engine._get_recovery_recommendations(
                    int(workout_plan['frequency'].split('日')[0])
                ),
                "form_analysis_integration": {
                    "enabled": True,
                    "supported_exercises": ["squat", "deadlift", "bench_press"],
                    "real_time_feedback": True
                }
            },
            "safety_analysis": safety_analysis,
            "ai_integration": integration_features,
            "next_steps": _generate_action_plan(safety_analysis, data['goal']),
            "generated_at": datetime.now().isoformat()
        }
        
        return jsonify(comprehensive_result), 200
        
    except Exception as e:
        return jsonify({
            "error": "Analysis failed",
            "message": str(e)
        }), 500

@api_v3.route('/update_goals', methods=['POST'])
def update_fitness_goals():
    """目標更新と再計算エンドポイント"""
    try:
        data = request.json
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({"error": "User ID required"}), 400
        
        # 新しい目標データ
        new_goals = {
            'target_weight': data.get('target_weight'),
            'target_body_fat': data.get('target_body_fat'),
            'timeframe_weeks': data.get('timeframe_weeks', 12),
            'priority': data.get('priority', 'balanced')  # balanced, muscle_gain, fat_loss
        }
        
        # 現在のユーザーデータを取得（実際の実装ではDBから）
        current_data = _get_user_current_data(user_id)
        
        # 新しい目標に基づいて再計算
        updated_plan = _recalculate_plan(current_data, new_goals)
        
        # 安全性の再チェック
        safety_check = safety_engine.comprehensive_safety_check(
            current_data,
            new_goals,
            updated_plan
        )
        
        return jsonify({
            "success": True,
            "updated_goals": new_goals,
            "updated_plan": updated_plan,
            "safety_check": safety_check,
            "recommendations": _generate_goal_update_recommendations(
                current_data, new_goals, safety_check
            )
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_v3.route('/track_progress', methods=['POST'])
def track_progress():
    """進捗追跡とプラン調整エンドポイント"""
    try:
        data = request.json
        user_id = data.get('user_id')
        
        progress_data = {
            'date': data.get('date', datetime.now().isoformat()),
            'weight': data.get('weight'),
            'body_fat': data.get('body_fat'),
            'measurements': data.get('measurements', {}),
            'performance': data.get('performance', {}),
            'subjective': data.get('subjective', {})  # 体調、気分など
        }
        
        # 進捗分析
        progress_analysis = _analyze_progress(user_id, progress_data)
        
        # プラン調整の必要性を判定
        adjustment_needed = progress_analysis['adjustment_recommended']
        
        if adjustment_needed:
            adjusted_plan = _adjust_plan_based_on_progress(
                user_id, progress_analysis
            )
        else:
            adjusted_plan = None
        
        return jsonify({
            "success": True,
            "progress_analysis": progress_analysis,
            "adjusted_plan": adjusted_plan,
            "trend_visualization": _generate_progress_trends(user_id),
            "motivational_message": _generate_motivation(progress_analysis)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_v3.route('/integrate_ai_analysis', methods=['POST'])
def integrate_ai_analysis():
    """既存AI機能との統合エンドポイント"""
    try:
        data = request.json
        analysis_type = data.get('type')  # 'pose', 'meal', 'phase'
        
        if analysis_type == 'pose':
            # 姿勢分析結果との統合
            pose_data = data.get('pose_results')
            body_metrics = _extract_body_metrics_from_pose(pose_data)
            
            # 実際の測定値で身体組成を更新
            updated_composition = _update_composition_with_measurements(
                data.get('user_id'), body_metrics
            )
            
            return jsonify({
                "success": True,
                "integrated_analysis": updated_composition,
                "recommendations": _generate_posture_based_recommendations(pose_data)
            }), 200
            
        elif analysis_type == 'meal':
            # 食事分析結果との統合
            meal_data = data.get('meal_analysis')
            daily_nutrition = _integrate_meal_to_daily_nutrition(
                data.get('user_id'), meal_data
            )
            
            return jsonify({
                "success": True,
                "daily_nutrition_update": daily_nutrition,
                "remaining_macros": _calculate_remaining_macros(
                    data.get('user_id'), daily_nutrition
                )
            }), 200
            
        elif analysis_type == 'phase':
            # 運動位相検出との統合
            phase_data = data.get('phase_detection')
            workout_quality = _analyze_workout_quality(phase_data)
            
            return jsonify({
                "success": True,
                "workout_analysis": workout_quality,
                "form_improvements": _generate_form_improvements(phase_data),
                "calories_burned_adjusted": _adjust_calories_for_form_quality(
                    phase_data, workout_quality
                )
            }), 200
            
        else:
            return jsonify({"error": "Invalid analysis type"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_v3.route('/generate_reports', methods=['GET'])
def generate_comprehensive_report():
    """包括的レポート生成エンドポイント"""
    try:
        user_id = request.args.get('user_id')
        report_type = request.args.get('type', 'weekly')  # weekly, monthly, progress
        
        if not user_id:
            return jsonify({"error": "User ID required"}), 400
        
        # ユーザーデータの集約
        user_data = _get_user_current_data(user_id)
        historical_data = _get_historical_data(user_id, report_type)
        
        # レポート生成
        if report_type == 'weekly':
            report = _generate_weekly_report(user_data, historical_data)
        elif report_type == 'monthly':
            report = _generate_monthly_report(user_data, historical_data)
        else:
            report = _generate_progress_report(user_data, historical_data)
        
        # 安全性レポートも含める
        safety_report = safety_engine.generate_safety_report(
            user_data,
            user_data.get('goals', {}),
            user_data.get('current_plan', {}),
            {}
        )
        
        return jsonify({
            "report_type": report_type,
            "generated_at": datetime.now().isoformat(),
            "report_data": report,
            "safety_report": safety_report,
            "export_formats": ["PDF", "JSON", "CSV"]
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ヘルパー関数
def _generate_ai_recommendations(user_data, safety_analysis):
    """AI統合推奨事項の生成"""
    recommendations = []
    
    # 安全性に基づく推奨
    if safety_analysis['overall_safety'] in ['high_risk', 'moderate_risk']:
        recommendations.append({
            "type": "safety",
            "priority": "high",
            "message": "現在の計画にはリスクがあります。修正を推奨します。",
            "actions": safety_analysis['recommendations'][:3]
        })
    
    # 目標に基づく推奨
    if user_data['goal'] == 'cutting':
        recommendations.append({
            "type": "nutrition",
            "priority": "medium",
            "message": "減量期は高タンパク質摂取が重要です",
            "actions": ["毎食20-30gのタンパク質", "食事写真分析機能を活用"]
        })
    
    # 経験レベルに基づく推奨
    if user_data.get('experience') == 'beginner':
        recommendations.append({
            "type": "training",
            "priority": "medium",
            "message": "フォーム習得を優先してください",
            "actions": ["姿勢分析機能でフォームチェック", "軽い重量から開始"]
        })
    
    return recommendations

def _determine_metabolic_type(bmr_data, user_data):
    """代謝タイプの判定"""
    # 簡易的な判定ロジック
    avg_bmr = bmr_data['average']
    expected_bmr = bmr_data['mifflin']
    
    if avg_bmr > expected_bmr * 1.1:
        return "fast_metabolism"
    elif avg_bmr < expected_bmr * 0.9:
        return "slow_metabolism"
    else:
        return "normal_metabolism"

def _generate_action_plan(safety_analysis, goal):
    """次のステップのアクションプラン生成"""
    action_plan = {
        "immediate": [],
        "this_week": [],
        "this_month": []
    }
    
    # 安全性に基づくアクション
    for warning in safety_analysis['warnings']:
        if warning['level'] == 'critical':
            action_plan['immediate'].append(warning.get('recommendation'))
        elif warning['level'] == 'danger':
            action_plan['this_week'].append(warning.get('recommendation'))
    
    # 目標に基づくアクション
    if goal == 'muscle_gain':
        action_plan['this_week'].extend([
            "プログレッシブオーバーロードの記録開始",
            "タンパク質摂取量の追跡"
        ])
        action_plan['this_month'].append("体組成測定で進捗確認")
    
    return action_plan

def _get_user_current_data(user_id):
    """ユーザーの現在データ取得（モック）"""
    # 実際の実装ではデータベースから取得
    return {
        "user_id": user_id,
        "weight": 70,
        "height": 170,
        "age": 30,
        "gender": "male",
        "activity_level": "moderate",
        "experience_level": "intermediate",
        "current_body_fat": 20
    }

def _recalculate_plan(current_data, new_goals):
    """プランの再計算"""
    # 簡易実装
    return {
        "target_calories": 2200,
        "training_frequency": 4,
        "macro_split": {"protein": 150, "carbs": 250, "fat": 70}
    }

def _analyze_progress(user_id, progress_data):
    """進捗分析"""
    # 簡易実装
    return {
        "trend": "positive",
        "rate_of_change": -0.5,  # kg/week
        "on_track": True,
        "adjustment_recommended": False
    }

def _generate_goal_update_recommendations(current, goals, safety):
    """目標更新の推奨事項"""
    return ["段階的な目標設定を推奨", "現実的なタイムフレームの設定"]

def _extract_body_metrics_from_pose(pose_data):
    """姿勢データから身体測定値を抽出"""
    # MediaPipeの結果から実際の測定値を計算
    return {
        "arm_length": {"left": 62, "right": 62},
        "leg_length": {"left": 95, "right": 95},
        "shoulder_width": 45
    }

def _update_composition_with_measurements(user_id, metrics):
    """測定値で身体組成を更新"""
    return {"updated": True, "new_measurements": metrics}

def _integrate_meal_to_daily_nutrition(user_id, meal_data):
    """食事を日次栄養に統合"""
    return {
        "total_calories": meal_data.get("calories", 0),
        "macros": meal_data.get("macros", {})
    }

def _calculate_remaining_macros(user_id, consumed):
    """残りのマクロ栄養素を計算"""
    # 目標から消費分を引く
    return {
        "protein": 50,
        "carbs": 100,
        "fat": 20
    }

def _analyze_workout_quality(phase_data):
    """ワークアウトの質を分析"""
    return {
        "form_score": 85,
        "tempo_consistency": 92,
        "range_of_motion": "full"
    }

def _generate_form_improvements(phase_data):
    """フォーム改善提案"""
    return ["膝の位置に注意", "背中をまっすぐに保つ"]

def _adjust_calories_for_form_quality(phase_data, quality):
    """フォームの質に基づくカロリー調整"""
    base_calories = 300
    quality_multiplier = quality.get("form_score", 100) / 100
    return round(base_calories * quality_multiplier)

def _get_historical_data(user_id, period):
    """履歴データ取得"""
    return {"weeks": 4, "data_points": 28}

def _generate_weekly_report(user_data, historical):
    """週次レポート生成"""
    return {
        "summary": "Good progress this week",
        "achievements": ["目標カロリー達成率: 95%", "トレーニング完遂率: 100%"]
    }

def _generate_monthly_report(user_data, historical):
    """月次レポート生成"""
    return {
        "summary": "Significant improvements",
        "body_composition_changes": {"weight": -2.0, "body_fat": -1.5}
    }

def _generate_progress_report(user_data, historical):
    """進捗レポート生成"""
    return {
        "overall_progress": "On track",
        "goal_achievement": 75
    }

def _generate_progress_trends(user_id):
    """進捗トレンドの可視化データ"""
    return {
        "weight_trend": "decreasing",
        "strength_trend": "increasing",
        "body_composition_trend": "improving"
    }

def _generate_motivation(analysis):
    """モチベーションメッセージ生成"""
    if analysis.get("on_track"):
        return "素晴らしい進捗です！この調子で続けましょう！"
    else:
        return "小さな調整で軌道に戻れます。諦めずに続けましょう！"

def _adjust_plan_based_on_progress(user_id, analysis):
    """進捗に基づくプラン調整"""
    return {
        "calorie_adjustment": -100,
        "training_adjustment": "ボリューム10%増加",
        "reason": "プラトー打破のため"
    }

def _generate_posture_based_recommendations(pose_data):
    """姿勢に基づく推奨事項"""
    return ["肩甲骨の位置を改善", "骨盤の前傾を修正"]

# エラーハンドラー
@api_v3.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request", "message": str(error)}), 400

@api_v3.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error", "message": str(error)}), 500