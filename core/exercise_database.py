"""
トレーニング種目データベース
部位別種目分類とデータ管理
"""

# 部位別種目データベース
EXERCISE_DATABASE = {
    "legs": {
        "name": "脚部",
        "icon": "🦵",
        "subcategories": {
            "quadriceps": {
                "name": "大腿四頭筋",
                "exercises": [
                    {"id": "squat", "name": "スクワット", "type": "compound"},
                    {"id": "leg_press", "name": "レッグプレス", "type": "compound"},
                    {"id": "leg_extension", "name": "レッグエクステンション", "type": "isolation"},
                    {"id": "front_squat", "name": "フロントスクワット", "type": "compound"},
                    {"id": "goblet_squat", "name": "ゴブレットスクワット", "type": "compound"},
                    {"id": "split_squat", "name": "スプリットスクワット", "type": "compound"},
                    {"id": "lunge", "name": "ランジ", "type": "compound"},
                    {"id": "hack_squat", "name": "ハックスクワット", "type": "compound"},
                    {"id": "sissy_squat", "name": "シシースクワット", "type": "isolation"}
                ]
            },
            "hamstrings": {
                "name": "ハムストリングス",
                "exercises": [
                    {"id": "romanian_deadlift", "name": "ルーマニアンデッドリフト", "type": "compound"},
                    {"id": "rdl", "name": "RDL", "type": "compound"},
                    {"id": "leg_curl", "name": "レッグカール", "type": "isolation"},
                    {"id": "good_morning", "name": "グッドモーニング", "type": "compound"},
                    {"id": "stiff_leg_deadlift", "name": "スティッフレッグデッドリフト", "type": "compound"},
                    {"id": "back_extension", "name": "バックエクステンション", "type": "compound"}
                ]
            },
            "glutes": {
                "name": "お尻（臀筋）",
                "exercises": [
                    {"id": "hip_thrust", "name": "ヒップスラスト", "type": "compound"},
                    {"id": "bulgarian_squat", "name": "ブルガリアンスクワット", "type": "compound"},
                    {"id": "cable_kickback", "name": "ケーブルキックバック", "type": "isolation"},
                    {"id": "abduction", "name": "アブダクション", "type": "isolation"},
                    {"id": "adduction", "name": "アダクション", "type": "isolation"},
                    {"id": "glute_bridge", "name": "グルートブリッジ", "type": "compound"}
                ]
            },
            "calves": {
                "name": "ふくらはぎ",
                "exercises": [
                    {"id": "standing_calf_raise", "name": "スタンディングカーフレイズ", "type": "isolation"},
                    {"id": "seated_calf_raise", "name": "シーテッドカーフレイズ", "type": "isolation"},
                    {"id": "donkey_calf_raise", "name": "ドンキーカーフレイズ", "type": "isolation"}
                ]
            }
        }
    },
    "chest": {
        "name": "胸部",
        "icon": "💪",
        "subcategories": {
            "pectorals": {
                "name": "大胸筋",
                "exercises": [
                    {"id": "bench_press", "name": "ベンチプレス", "type": "compound"},
                    {"id": "dumbbell_press", "name": "ダンベルプレス", "type": "compound"},
                    {"id": "incline_bench_press", "name": "インクラインベンチプレス", "type": "compound"},
                    {"id": "incline_dumbbell_press", "name": "インクラインダンベルプレス", "type": "compound"},
                    {"id": "decline_bench_press", "name": "デクラインベンチプレス", "type": "compound"},
                    {"id": "decline_dumbbell_press", "name": "デクラインダンベルプレス", "type": "compound"},
                    {"id": "dips", "name": "ディップス", "type": "compound"},
                    {"id": "chest_fly", "name": "チェストフライ", "type": "isolation"},
                    {"id": "push_up", "name": "プッシュアップ", "type": "compound"},
                    {"id": "cable_fly", "name": "ケーブルフライ", "type": "isolation"},
                    {"id": "chest_press", "name": "チェストプレス", "type": "compound"},
                    {"id": "dumbbell_fly", "name": "ダンベルフライ", "type": "isolation"},
                    {"id": "incline_dumbbell_fly", "name": "インクラインダンベルフライ", "type": "isolation"},
                    {"id": "cable_crossover", "name": "ケーブルクロスオーバー", "type": "isolation"},
                    {"id": "dumbbell_pullover", "name": "ダンベルプルオーバー", "type": "compound"}
                ]
            }
        }
    },
    "back": {
        "name": "背中",
        "icon": "🔙",
        "subcategories": {
            "lats": {
                "name": "広背筋",
                "exercises": [
                    {"id": "lat_pulldown", "name": "ラットプルダウン", "type": "compound"},
                    {"id": "chin_up", "name": "チンニング", "type": "compound"},
                    {"id": "pull_up", "name": "懸垂", "type": "compound"},
                    {"id": "straight_arm_pulldown", "name": "ストレートアームプルダウン", "type": "isolation"},
                    {"id": "t_bar_row", "name": "Tバーロウ", "type": "compound"},
                    {"id": "bent_over_row", "name": "ベントオーバーロウ", "type": "compound"},
                    {"id": "one_hand_row", "name": "ワンハンドロウ", "type": "compound"}
                ]
            },
            "traps_erectors": {
                "name": "僧帽筋・脊柱起立筋",
                "exercises": [
                    {"id": "deadlift", "name": "デッドリフト", "type": "compound"},
                    {"id": "barbell_row", "name": "バーベルロウ", "type": "compound"},
                    {"id": "dumbbell_row", "name": "ダンベルロウ", "type": "compound"},
                    {"id": "seated_row", "name": "シーテッドロウ", "type": "compound"},
                    {"id": "hyperextension", "name": "ハイパーエクステンション", "type": "compound"},
                    {"id": "shrug", "name": "シュラッグ", "type": "isolation"},
                    {"id": "rack_pull", "name": "ラックプル", "type": "compound"}
                ]
            }
        }
    },
    "shoulders": {
        "name": "肩",
        "icon": "🤲",
        "subcategories": {
            "deltoids": {
                "name": "三角筋",
                "exercises": [
                    {"id": "shoulder_press", "name": "ショルダープレス", "type": "compound"},
                    {"id": "side_raise", "name": "サイドレイズ", "type": "isolation"},
                    {"id": "front_raise", "name": "フロントレイズ", "type": "isolation"},
                    {"id": "rear_delt_fly", "name": "リアデルトフライ", "type": "isolation"},
                    {"id": "upright_row", "name": "アップライトロウ", "type": "compound"},
                    {"id": "military_press", "name": "ミリタリープレス", "type": "compound"},
                    {"id": "arnold_press", "name": "アーノルドプレス", "type": "compound"},
                    {"id": "rear_raise", "name": "リアレイズ", "type": "isolation"},
                    {"id": "face_pull", "name": "フェイスプル", "type": "compound"}
                ]
            }
        }
    },
    "biceps": {
        "name": "上腕二頭筋",
        "icon": "💪",
        "subcategories": {
            "biceps_main": {
                "name": "上腕二頭筋",
                "exercises": [
                    {"id": "barbell_curl", "name": "バーベルカール", "type": "isolation"},
                    {"id": "dumbbell_curl", "name": "ダンベルカール", "type": "isolation"},
                    {"id": "preacher_curl", "name": "プリチャーカール", "type": "isolation"},
                    {"id": "hammer_curl", "name": "ハンマーカール", "type": "isolation"},
                    {"id": "cable_curl", "name": "ケーブルカール", "type": "isolation"},
                    {"id": "concentration_curl", "name": "コンセントレーションカール", "type": "isolation"},
                    {"id": "drag_curl", "name": "ドラッグカール", "type": "isolation"},
                    {"id": "reverse_grip_chinning", "name": "逆手懸垂", "type": "compound"}
                ]
            }
        }
    },
    "triceps": {
        "name": "上腕三頭筋",
        "icon": "🔥",
        "subcategories": {
            "triceps_main": {
                "name": "上腕三頭筋",
                "exercises": [
                    {"id": "triceps_extension", "name": "トライセップスエクステンション", "type": "isolation"},
                    {"id": "skull_crusher", "name": "スカルクラッシャー", "type": "isolation"},
                    {"id": "narrow_bench_press", "name": "ナローベンチプレス", "type": "compound"},
                    {"id": "push_down", "name": "プッシュダウン", "type": "isolation"},
                    {"id": "cable_extension", "name": "ケーブルエクステンション", "type": "isolation"},
                    {"id": "overhead_extension", "name": "オーバーヘッドエクステンション", "type": "isolation"},
                    {"id": "french_press", "name": "フレンチプレス", "type": "isolation"},
                    {"id": "press_down", "name": "プレスダウン", "type": "isolation"},
                    {"id": "kickback", "name": "キックバック", "type": "isolation"},
                    {"id": "reverse_push_up", "name": "リバースプッシュアップ", "type": "compound"},
                    {"id": "diamond_push_up", "name": "ダイヤモンドプッシュアップ", "type": "compound"}
                ]
            }
        }
    },
    "forearms": {
        "name": "前腕",
        "icon": "✊",
        "subcategories": {
            "forearms_main": {
                "name": "前腕筋群",
                "exercises": [
                    {"id": "wrist_curl", "name": "リストカール", "type": "isolation"},
                    {"id": "reverse_wrist_curl", "name": "リバースリストカール", "type": "isolation"},
                    {"id": "farmer_walk", "name": "ファーマーズウォーク", "type": "compound"}
                ]
            }
        }
    },
    "abs": {
        "name": "腹筋",
        "icon": "🔥",
        "subcategories": {
            "core": {
                "name": "腹直筋・腹斜筋",
                "exercises": [
                    {"id": "crunch", "name": "クランチ", "type": "isolation"},
                    {"id": "sit_up", "name": "シットアップ", "type": "isolation"},
                    {"id": "leg_raise", "name": "レッグレイズ", "type": "isolation"},
                    {"id": "plank", "name": "プランク", "type": "compound"},
                    {"id": "side_plank", "name": "サイドプランク", "type": "compound"},
                    {"id": "russian_twist", "name": "ロシアンツイスト", "type": "isolation"},
                    {"id": "ab_roller", "name": "アブローラー", "type": "compound"},
                    {"id": "bicycle_crunch", "name": "バイシクルクランチ", "type": "isolation"},
                    {"id": "mountain_climber", "name": "マウンテンクライマー", "type": "compound"},
                    {"id": "side_bend", "name": "サイドベント", "type": "isolation"},
                    {"id": "knee_to_chest", "name": "ニートゥチェスト", "type": "compound"}
                ]
            }
        }
    }
}

def get_all_exercises():
    """全ての種目をフラットなリストで取得"""
    exercises = []
    for category_key, category in EXERCISE_DATABASE.items():
        for subcategory_key, subcategory in category["subcategories"].items():
            for exercise in subcategory["exercises"]:
                exercises.append({
                    **exercise,
                    "category": category_key,
                    "category_name": category["name"],
                    "subcategory": subcategory_key,
                    "subcategory_name": subcategory["name"]
                })
    return exercises

def search_exercises(query):
    """種目名で検索"""
    all_exercises = get_all_exercises()
    query_lower = query.lower()
    
    results = []
    for exercise in all_exercises:
        if (query_lower in exercise["name"].lower() or 
            query_lower in exercise["category_name"].lower() or
            query_lower in exercise["subcategory_name"].lower()):
            results.append(exercise)
    
    return results

def get_exercises_by_category(category):
    """部位別で種目を取得"""
    if category not in EXERCISE_DATABASE:
        return []
    
    exercises = []
    for subcategory_key, subcategory in EXERCISE_DATABASE[category]["subcategories"].items():
        for exercise in subcategory["exercises"]:
            exercises.append({
                **exercise,
                "subcategory": subcategory_key,
                "subcategory_name": subcategory["name"]
            })
    
    return exercises

def get_exercise_by_id(exercise_id):
    """IDから種目情報を取得"""
    all_exercises = get_all_exercises()
    for exercise in all_exercises:
        if exercise["id"] == exercise_id:
            return exercise
    return None

# よく使われる重量のリスト（kg単位）
COMMON_WEIGHTS = [
    2.5, 5, 7.5, 10, 12.5, 15, 17.5, 20, 22.5, 25, 27.5, 30, 32.5, 35, 37.5, 40,
    42.5, 45, 47.5, 50, 52.5, 55, 57.5, 60, 62.5, 65, 67.5, 70, 72.5, 75, 77.5, 80,
    82.5, 85, 87.5, 90, 92.5, 95, 97.5, 100, 105, 110, 115, 120, 125, 130, 135, 140,
    145, 150, 155, 160, 165, 170, 175, 180, 185, 190, 195, 200
]

def get_weight_suggestions(current_weight=None, count=10):
    """重量選択の候補を取得"""
    if current_weight:
        # 現在の重量の前後を中心に候補を生成
        base_weights = [w for w in COMMON_WEIGHTS if abs(w - current_weight) <= 20]
        if len(base_weights) < count:
            base_weights = COMMON_WEIGHTS[:count]
    else:
        # デフォルトは軽い重量から
        base_weights = COMMON_WEIGHTS[:count]
    
    return sorted(base_weights)