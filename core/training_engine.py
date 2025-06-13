# core/training_engine.py
"""
運動プログラム生成エンジン
個別化されたトレーニングプラン、METs計算、プログレッション管理を提供
"""

class TrainingEngine:
    def __init__(self):
        self.experience_levels = {
            "beginner": {
                "months": "0-6", 
                "frequency": "2-3", 
                "duration": "45-60",
                "volume": "低",
                "intensity": "低-中"
            },
            "intermediate": {
                "months": "6-24", 
                "frequency": "3-4", 
                "duration": "60-75",
                "volume": "中",
                "intensity": "中-高"
            },
            "advanced": {
                "months": "24+", 
                "frequency": "4-6", 
                "duration": "75-90",
                "volume": "高",
                "intensity": "高"
            }
        }
        
        self.training_parameters = {
            "strength": {
                "reps": "1-6", 
                "sets": "3-5", 
                "rest": "2-5分", 
                "intensity": "80-95% 1RM",
                "tempo": "2-0-2-0",
                "purpose": "最大筋力向上"
            },
            "hypertrophy": {
                "reps": "6-12", 
                "sets": "3-4", 
                "rest": "60-90秒", 
                "intensity": "67-85% 1RM",
                "tempo": "2-0-1-0",
                "purpose": "筋肥大"
            },
            "endurance": {
                "reps": "15-20+", 
                "sets": "2-3", 
                "rest": "30-60秒", 
                "intensity": "50-70% 1RM",
                "tempo": "1-0-1-0",
                "purpose": "筋持久力向上"
            }
        }
        
        self.mets_values = {
            # 筋力トレーニング
            "strength_light": 3.5,
            "strength_moderate": 5.0,
            "strength_intense": 7.0,
            "strength_circuit": 8.0,
            
            # 有酸素運動
            "walking_slow": 2.5,
            "walking_moderate": 3.5,
            "walking_fast": 4.5,
            "jogging_light": 7.0,
            "running_moderate": 10.0,
            "running_fast": 12.5,
            "cycling_light": 4.0,
            "cycling_moderate": 8.0,
            "cycling_intense": 12.0,
            "swimming_moderate": 6.0,
            "swimming_intense": 10.0,
            
            # その他
            "yoga": 2.5,
            "pilates": 3.0,
            "hiit": 12.0,
            "crossfit": 10.0
        }
        
        self.muscle_groups = {
            "push": ["胸", "肩", "三頭筋"],
            "pull": ["背中", "二頭筋"],
            "legs": ["大腿四頭筋", "ハムストリング", "臀筋", "ふくらはぎ"],
            "core": ["腹筋", "腹斜筋", "腰部"]
        }
    
    def generate_workout_plan(self, experience, goal, available_days, equipment="full_gym"):
        """個別化トレーニングプラン生成"""
        level_config = self.experience_levels[experience]
        
        # 週間頻度の決定
        if available_days < 3:
            frequency = min(available_days, 2)
            split_type = "full_body"
        elif available_days == 3:
            frequency = 3
            split_type = "full_body" if experience == "beginner" else "push_pull_legs"
        elif available_days == 4:
            frequency = 4
            split_type = "upper_lower" if experience != "advanced" else "push_pull_legs_upper"
        else:
            frequency = min(available_days, 5)
            split_type = "push_pull_legs" if experience != "advanced" else "body_part"
        
        # トレーニングプログラムの生成
        program = self._generate_program_structure(split_type, goal, experience, equipment)
        
        # プログレッション計画
        progression = self._generate_progression_plan(experience, goal)
        
        # 安全ガイドライン
        safety = self._get_safety_guidelines(experience)
        
        return {
            "experience_level": experience,
            "training_goal": goal,
            "frequency": f"{frequency}日/週",
            "duration": level_config["duration"] + "分/セッション",
            "split_type": split_type,
            "program": program,
            "progression_plan": progression,
            "safety_guidelines": safety,
            "recovery_recommendations": self._get_recovery_recommendations(frequency),
            "periodization": self._generate_periodization(goal, experience)
        }
    
    def _generate_program_structure(self, split_type, goal, experience, equipment):
        """プログラム構造の生成"""
        programs = {
            "full_body": self._create_full_body_program,
            "upper_lower": self._create_upper_lower_split,
            "push_pull_legs": self._create_ppl_split,
            "push_pull_legs_upper": self._create_ppl_upper_split,
            "body_part": self._create_body_part_split
        }
        
        program_func = programs.get(split_type, self._create_full_body_program)
        return program_func(goal, experience, equipment)
    
    def _create_full_body_program(self, goal, experience, equipment):
        """全身トレーニングプログラム"""
        if equipment == "bodyweight":
            return self._get_bodyweight_full_body()
        
        params = self.training_parameters[goal]
        
        workout_a = {
            "name": "全身トレーニングA",
            "exercises": [
                {
                    "name": "スクワット",
                    "target": "下半身全体",
                    "sets": 3,
                    "reps": params["reps"],
                    "rest": params["rest"],
                    "notes": "フルレンジで動作"
                },
                {
                    "name": "ベンチプレス",
                    "target": "胸・肩・三頭筋",
                    "sets": 3,
                    "reps": params["reps"],
                    "rest": params["rest"],
                    "notes": "肩甲骨を寄せて固定"
                },
                {
                    "name": "懸垂/ラットプルダウン",
                    "target": "背中・二頭筋",
                    "sets": 3,
                    "reps": params["reps"],
                    "rest": params["rest"],
                    "notes": "フルレンジで引く"
                },
                {
                    "name": "ショルダープレス",
                    "target": "肩",
                    "sets": 3,
                    "reps": params["reps"],
                    "rest": "60秒"
                },
                {
                    "name": "プランク",
                    "target": "体幹",
                    "sets": 3,
                    "duration": "30-60秒",
                    "rest": "30秒"
                }
            ]
        }
        
        workout_b = {
            "name": "全身トレーニングB",
            "exercises": [
                {
                    "name": "デッドリフト",
                    "target": "背中・下半身",
                    "sets": 3,
                    "reps": params["reps"],
                    "rest": params["rest"],
                    "notes": "背中をまっすぐに保つ"
                },
                {
                    "name": "インクラインダンベルプレス",
                    "target": "上部胸筋",
                    "sets": 3,
                    "reps": params["reps"],
                    "rest": params["rest"]
                },
                {
                    "name": "ベントオーバーロウ",
                    "target": "背中",
                    "sets": 3,
                    "reps": params["reps"],
                    "rest": params["rest"]
                },
                {
                    "name": "レッグプレス",
                    "target": "大腿四頭筋",
                    "sets": 3,
                    "reps": params["reps"],
                    "rest": "90秒"
                },
                {
                    "name": "アブローラー",
                    "target": "腹筋",
                    "sets": 3,
                    "reps": "8-12",
                    "rest": "60秒"
                }
            ]
        }
        
        return {
            "workouts": [workout_a, workout_b],
            "rotation": "A-休-B-休-A-休-休 or A-B-休-A-B-休-休",
            "warm_up": self._get_warmup_routine(),
            "cool_down": self._get_cooldown_routine()
        }
    
    def _get_bodyweight_full_body(self):
        """自重全身トレーニング"""
        return {
            "workouts": [{
                "name": "自重全身トレーニング",
                "exercises": [
                    {
                        "name": "スクワット/ジャンプスクワット",
                        "target": "下半身全体",
                        "sets": 3,
                        "reps": "10-15",
                        "progression": "通常→ジャンプ→片足"
                    },
                    {
                        "name": "プッシュアップ",
                        "target": "胸・肩・三頭筋",
                        "sets": 3,
                        "reps": "8-15",
                        "progression": "膝つき→通常→ダイヤモンド→片手"
                    },
                    {
                        "name": "懸垂/逆手懸垂",
                        "target": "背中・二頭筋",
                        "sets": 3,
                        "reps": "5-12",
                        "alternative": "斜め懸垂（低い鉄棒）"
                    },
                    {
                        "name": "パイクプッシュアップ",
                        "target": "肩",
                        "sets": 3,
                        "reps": "8-12",
                        "notes": "腰を高く上げて"
                    },
                    {
                        "name": "プランク→サイドプランク",
                        "target": "体幹",
                        "sets": 3,
                        "duration": "30-60秒",
                        "each_side": True
                    },
                    {
                        "name": "バーピー",
                        "target": "全身・心肺機能",
                        "sets": 3,
                        "reps": "5-10",
                        "notes": "最後の仕上げ"
                    }
                ]
            }],
            "frequency": "週3-4回（1日おき）",
            "progression": "回数→セット数→難易度の順で増やす"
        }
    
    def _create_ppl_split(self, goal, experience, equipment):
        """Push/Pull/Legsスプリット"""
        params = self.training_parameters[goal]
        
        push_day = {
            "name": "Push Day（胸・肩・三頭筋）",
            "exercises": [
                {"name": "ベンチプレス", "sets": 4, "reps": params["reps"]},
                {"name": "インクラインダンベルプレス", "sets": 3, "reps": params["reps"]},
                {"name": "ショルダープレス", "sets": 3, "reps": params["reps"]},
                {"name": "サイドレイズ", "sets": 3, "reps": "12-15"},
                {"name": "トライセプスディップス", "sets": 3, "reps": params["reps"]},
                {"name": "ケーブルフライ", "sets": 3, "reps": "12-15"}
            ]
        }
        
        pull_day = {
            "name": "Pull Day（背中・二頭筋）",
            "exercises": [
                {"name": "デッドリフト", "sets": 4, "reps": params["reps"]},
                {"name": "懸垂/ラットプルダウン", "sets": 3, "reps": params["reps"]},
                {"name": "ベントオーバーロウ", "sets": 3, "reps": params["reps"]},
                {"name": "ケーブルロウ", "sets": 3, "reps": "10-12"},
                {"name": "バーベルカール", "sets": 3, "reps": params["reps"]},
                {"name": "ハンマーカール", "sets": 3, "reps": "10-12"}
            ]
        }
        
        leg_day = {
            "name": "Leg Day（脚・臀筋）",
            "exercises": [
                {"name": "スクワット", "sets": 4, "reps": params["reps"]},
                {"name": "ルーマニアンデッドリフト", "sets": 3, "reps": params["reps"]},
                {"name": "レッグプレス", "sets": 3, "reps": "10-12"},
                {"name": "レッグカール", "sets": 3, "reps": "10-15"},
                {"name": "カーフレイズ", "sets": 4, "reps": "15-20"},
                {"name": "レッグエクステンション", "sets": 3, "reps": "12-15"}
            ]
        }
        
        return {
            "workouts": [push_day, pull_day, leg_day],
            "rotation": "Push-Pull-Legs-休-Push-Pull-Legs or 2オン1オフ",
            "volume_notes": f"{experience}レベルに適したボリューム"
        }
    
    def calculate_exercise_calories(self, exercise_type, intensity, weight_kg, duration_minutes):
        """運動消費カロリー計算（METs使用）"""
        # METsキーの構築
        mets_key = f"{exercise_type}_{intensity}"
        mets = self.mets_values.get(mets_key, 5.0)  # デフォルト5.0 METs
        
        # 基本カロリー計算: METs × 体重(kg) × 時間(h)
        calories = mets * weight_kg * (duration_minutes / 60)
        
        # EPOC効果（運動後過剰酸素消費）
        epoc_calories = 0
        if intensity == "intense" or exercise_type == "hiit":
            # 高強度運動の場合、15-20%のアフターバーン効果
            epoc_percentage = 0.15 if intensity == "intense" else 0.20
            epoc_calories = calories * epoc_percentage
        elif intensity == "moderate" and exercise_type.startswith("strength"):
            # 中強度筋トレの場合、10%のアフターバーン
            epoc_calories = calories * 0.10
        
        return {
            "exercise_calories": round(calories),
            "epoc_calories": round(epoc_calories),
            "total_calories": round(calories + epoc_calories),
            "mets_used": mets,
            "calories_per_minute": round((calories + epoc_calories) / duration_minutes, 1)
        }
    
    def _generate_progression_plan(self, experience, goal):
        """漸進性過負荷プログレッション計画"""
        if experience == "beginner":
            return {
                "week_1_2": {
                    "focus": "フォーム習得、神経系適応",
                    "intensity": "軽い負荷（40-50% 1RM）",
                    "volume": "低ボリューム",
                    "frequency": "週2-3回"
                },
                "week_3_4": {
                    "focus": "負荷増加開始",
                    "progression": "重量を5-10%増加",
                    "technique_check": "フォームを維持できる範囲で"
                },
                "week_5_8": {
                    "focus": "継続的な負荷増加",
                    "progression": "週ごとに2.5-5%増加",
                    "new_exercises": "バリエーション追加"
                },
                "month_3_6": {
                    "focus": "基礎筋力構築",
                    "periodization": "リニアピリオダイゼーション",
                    "deload": "4週ごとに軽い週を設定"
                },
                "principles": [
                    "フォーム重視",
                    "小さな改善の積み重ね",
                    "回復を十分に取る",
                    "記録をつける"
                ]
            }
        elif experience == "intermediate":
            return {
                "mesocycle_1": {
                    "weeks": "1-4",
                    "focus": "ボリューム増加",
                    "sets": "週ごとに1セット追加",
                    "intensity": "70-80% 1RM"
                },
                "mesocycle_2": {
                    "weeks": "5-8",
                    "focus": "強度増加",
                    "sets": "セット数維持",
                    "intensity": "80-90% 1RM"
                },
                "deload_week": {
                    "frequency": "4-6週ごと",
                    "volume": "50%に減少",
                    "focus": "回復と適応"
                },
                "variation_strategies": [
                    "エクササイズローテーション",
                    "テンポ操作",
                    "レンジオブモーション変更",
                    "アイソメトリックホールド追加"
                ]
            }
        else:  # advanced
            return {
                "periodization": "ブロックピリオダイゼーション",
                "accumulation_block": {
                    "duration": "3-4週",
                    "focus": "高ボリューム、中強度",
                    "volume": "週10-20セット/部位"
                },
                "intensification_block": {
                    "duration": "2-3週",
                    "focus": "高強度、低ボリューム",
                    "intensity": "85-95% 1RM"
                },
                "realization_block": {
                    "duration": "1-2週",
                    "focus": "ピーキング、テーパリング",
                    "testing": "1RMテストまたは競技"
                },
                "advanced_techniques": [
                    "クラスターセット",
                    "ドロップセット",
                    "レストポーズ",
                    "アクティベーション前の事前疲労"
                ]
            }
    
    def _get_safety_guidelines(self, experience=None):
        """安全ガイドライン"""
        general_safety = {
            "warm_up": {
                "duration": "5-10分",
                "components": [
                    "軽い有酸素運動（5分）",
                    "動的ストレッチ",
                    "特定動作の準備運動",
                    "軽い負荷でのセット"
                ]
            },
            "form_cues": {
                "spine": "脊柱をニュートラルに保つ",
                "breathing": "エキセントリックで吸気、コンセントリックで呼気",
                "core": "体幹を常に締める",
                "control": "コントロールされた動作速度"
            },
            "injury_prevention": [
                "痛みがある場合は中止",
                "適切な休息日の確保",
                "栄養と水分補給",
                "睡眠の重要性（7-9時間）"
            ],
            "overtraining_signs": [
                "慢性的な疲労感",
                "パフォーマンス低下",
                "気分の落ち込み",
                "食欲不振",
                "睡眠障害",
                "安静時心拍数の上昇（10拍/分以上）",
                "頻繁な風邪や感染症"
            ],
            "recovery_importance": "筋肉の成長と適応は休息中に起こる"
        }
        
        if experience == "beginner":
            general_safety["beginner_specific"] = [
                "最初の2週間は軽い負荷で",
                "週2-3回から開始",
                "複合動作を優先",
                "アイソレーション種目は後回し"
            ]
        
        return general_safety
    
    def _get_recovery_recommendations(self, training_frequency):
        """回復推奨事項"""
        return {
            "sleep": {
                "hours": "7-9時間/日",
                "quality_tips": [
                    "一定の就寝時間",
                    "寝室を涼しく暗く",
                    "就寝2時間前からスクリーンを避ける"
                ]
            },
            "nutrition": {
                "protein": "トレーニング後30分以内に20-40g",
                "carbs": "グリコーゲン回復のため十分な炭水化物",
                "hydration": "体重1kgあたり35-40ml/日"
            },
            "active_recovery": {
                "frequency": f"週{7-training_frequency}日",
                "activities": [
                    "軽いウォーキング（20-30分）",
                    "ヨガやストレッチ",
                    "水泳（低強度）",
                    "フォームローリング"
                ]
            },
            "rest_days": {
                "full_rest": "週1-2日は完全休養",
                "listen_to_body": "疲労感が強い時は追加休養"
            }
        }
    
    def _get_warmup_routine(self):
        """ウォームアップルーティン"""
        return {
            "general_warmup": {
                "duration": "5分",
                "activities": [
                    "ジョギングまたはバイク",
                    "アームサークル",
                    "レッグスイング",
                    "体幹回旋"
                ]
            },
            "dynamic_stretching": {
                "duration": "5分",
                "exercises": [
                    "ランジウォーク",
                    "ハイニー",
                    "バットキック",
                    "インチワーム"
                ]
            },
            "specific_warmup": "本番の動作を軽い負荷で2-3セット"
        }
    
    def _get_cooldown_routine(self):
        """クールダウンルーティン"""
        return {
            "light_cardio": {
                "duration": "5分",
                "intensity": "非常に軽い",
                "purpose": "心拍数を徐々に下げる"
            },
            "static_stretching": {
                "duration": "10-15分",
                "hold_time": "30秒/部位",
                "target_areas": "使用した筋群を中心に"
            },
            "foam_rolling": {
                "optional": True,
                "duration": "5-10分",
                "benefits": "筋膜リリース、回復促進"
            }
        }
    
    def _generate_periodization(self, goal, experience):
        """ピリオダイゼーション（期分け）計画"""
        if goal == "strength":
            return {
                "macrocycle": "12-16週",
                "phases": [
                    {"name": "解剖学的適応期", "weeks": 2, "focus": "基礎構築"},
                    {"name": "筋肥大期", "weeks": 4, "focus": "筋量増加"},
                    {"name": "最大筋力期", "weeks": 4, "focus": "神経系適応"},
                    {"name": "ピーキング期", "weeks": 2, "focus": "競技準備"}
                ]
            }
        elif goal == "hypertrophy":
            return {
                "macrocycle": "12週",
                "phases": [
                    {"name": "ボリューム蓄積期", "weeks": 4, "focus": "高ボリューム"},
                    {"name": "強度増加期", "weeks": 4, "focus": "中ボリューム・高強度"},
                    {"name": "オーバーリーチング期", "weeks": 3, "focus": "最大ボリューム"},
                    {"name": "テーパー期", "weeks": 1, "focus": "回復と成長"}
                ]
            }
        else:
            return {
                "macrocycle": "8-12週",
                "approach": "線形または波状",
                "flexibility": "目標に応じて調整"
            }
    
    def _create_upper_lower_split(self, goal, experience, equipment):
        """上半身/下半身スプリット"""
        params = self.training_parameters[goal]
        
        upper_day = {
            "name": "上半身の日",
            "exercises": [
                {"name": "ベンチプレス", "sets": 4, "reps": params["reps"]},
                {"name": "ベントオーバーロウ", "sets": 4, "reps": params["reps"]},
                {"name": "ショルダープレス", "sets": 3, "reps": params["reps"]},
                {"name": "懸垂", "sets": 3, "reps": params["reps"]},
                {"name": "バーベルカール", "sets": 3, "reps": "8-12"},
                {"name": "トライセプスエクステンション", "sets": 3, "reps": "8-12"}
            ]
        }
        
        lower_day = {
            "name": "下半身の日",
            "exercises": [
                {"name": "スクワット", "sets": 4, "reps": params["reps"]},
                {"name": "ルーマニアンデッドリフト", "sets": 4, "reps": params["reps"]},
                {"name": "レッグプレス", "sets": 3, "reps": "10-12"},
                {"name": "レッグカール", "sets": 3, "reps": "10-15"},
                {"name": "カーフレイズ", "sets": 4, "reps": "15-20"},
                {"name": "アブローラー", "sets": 3, "reps": "8-12"}
            ]
        }
        
        return {
            "workouts": [upper_day, lower_day],
            "rotation": "上-下-休-上-下-休-休",
            "notes": "各部位週2回の頻度"
        }