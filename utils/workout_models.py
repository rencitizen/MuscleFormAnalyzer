"""
トレーニング記録データベースモデル
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import List, Dict, Any, Optional
import json

class WorkoutDatabase:
    def __init__(self):
        self.connection_params = {
            'host': os.environ.get('PGHOST'),
            'port': os.environ.get('PGPORT'),
            'database': os.environ.get('PGDATABASE'),
            'user': os.environ.get('PGUSER'),
            'password': os.environ.get('PGPASSWORD')
        }
        self.init_tables()
    
    def get_connection(self):
        """データベース接続を取得"""
        return psycopg2.connect(**self.connection_params)
    
    def init_tables(self):
        """テーブルを初期化"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # ユーザープロファイルテーブル（外部キー制約なし）
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS user_profiles (
                            id SERIAL PRIMARY KEY,
                            user_id VARCHAR(255) UNIQUE NOT NULL,
                            height_cm FLOAT,
                            calibration_data JSONB,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # ワークアウト記録テーブル
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS workouts (
                            id SERIAL PRIMARY KEY,
                            user_id VARCHAR(255) NOT NULL,
                            date DATE NOT NULL,
                            exercise VARCHAR(100) NOT NULL,
                            weight_kg FLOAT NOT NULL,
                            reps INTEGER NOT NULL,
                            notes TEXT,
                            form_analysis_ref VARCHAR(255),
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # インデックスを作成
                    cur.execute("""
                        CREATE INDEX IF NOT EXISTS idx_workouts_user_date 
                        ON workouts(user_id, date DESC)
                    """)
                    
                    cur.execute("""
                        CREATE INDEX IF NOT EXISTS idx_workouts_exercise 
                        ON workouts(user_id, exercise, date DESC)
                    """)
                    
                    conn.commit()
                    print("データベーステーブルを初期化しました")
                    
        except Exception as e:
            print(f"データベース初期化エラー: {e}")
    
    def user_exists(self, user_id: str) -> bool:
        """ユーザーアカウントが存在するかチェック"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1 FROM user_accounts WHERE user_id = %s", (user_id,))
                    return cur.fetchone() is not None
        except Exception as e:
            print(f"ユーザー存在チェックエラー: {e}")
            return False
    
    def create_user_account(self, user_id: str) -> bool:
        """ユーザーアカウントを作成"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # user_accounts テーブルに挿入
                    cur.execute("""
                        INSERT INTO user_accounts (user_id, created_at) 
                        VALUES (%s, CURRENT_TIMESTAMP)
                        ON CONFLICT (user_id) DO NOTHING
                    """, (user_id,))
                    
                    # user_profiles テーブルに基本プロファイルを作成
                    cur.execute("""
                        INSERT INTO user_profiles (user_id, display_name, created_at) 
                        VALUES (%s, %s, CURRENT_TIMESTAMP)
                        ON CONFLICT (user_id) DO NOTHING
                    """, (user_id, f"User {user_id.split('@')[0]}"))
                    
                    conn.commit()
                    return True
        except Exception as e:
            print(f"ユーザーアカウント作成エラー: {e}")
            return False

    def create_user_profile(self, user_id: str, height_cm: float = None, calibration_data: dict = None):
        """ユーザープロファイルを作成または更新"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO user_profiles (user_id, height_cm, calibration_data)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (user_id) 
                        DO UPDATE SET 
                            height_cm = EXCLUDED.height_cm,
                            calibration_data = EXCLUDED.calibration_data,
                            updated_at = CURRENT_TIMESTAMP
                    """, (user_id, height_cm, json.dumps(calibration_data) if calibration_data else None))
                    conn.commit()
                    return True
        except Exception as e:
            print(f"ユーザープロファイル作成エラー: {e}")
            return False
    
    def add_workout(self, user_id: str, date: str, exercise: str, weight_kg: float, 
                   reps: int, notes: str = None, form_analysis_ref: str = None, exercise_name: str = None):
        """ワークアウト記録を追加"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # exercise_nameカラムが存在するかチェックし、なければ追加
                    cur.execute("""
                        SELECT column_name FROM information_schema.columns 
                        WHERE table_name = 'workouts' AND column_name = 'exercise_name'
                    """)
                    has_exercise_name = cur.fetchone()
                    
                    if not has_exercise_name:
                        cur.execute("ALTER TABLE workouts ADD COLUMN exercise_name VARCHAR(255)")
                        conn.commit()
                    
                    cur.execute("""
                        INSERT INTO workouts (user_id, date, exercise, exercise_name, weight_kg, reps, notes, form_analysis_ref)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (user_id, date, exercise, exercise_name or exercise, weight_kg, reps, notes, form_analysis_ref))
                    workout_id = cur.fetchone()[0]
                    conn.commit()
                    return workout_id
        except Exception as e:
            print(f"ワークアウト追加エラー: {e}")
            return None
    
    def get_workouts_by_user(self, user_id: str, limit: int = 50) -> List[Dict]:
        """ユーザーのワークアウト記録を取得"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT * FROM workouts 
                        WHERE user_id = %s 
                        ORDER BY date DESC, created_at DESC 
                        LIMIT %s
                    """, (user_id, limit))
                    workouts = cur.fetchall()
                    return [dict(workout) for workout in workouts]
        except Exception as e:
            print(f"ワークアウト取得エラー: {e}")
            return []
    
    def get_workouts_summary_by_category(self, user_id: str) -> List[Dict]:
        """部位別にワークアウト記録を集計"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # 部位別の総重量を計算
                    cur.execute("""
                        SELECT 
                            CASE 
                                WHEN exercise IN ('bench_press', 'incline_bench_press', 'decline_bench_press', 'chest_press', 'push_up', 'dips', 'dumbbell_fly', 'incline_dumbbell_fly', 'cable_crossover', 'dumbbell_pullover') THEN 'chest'
                                WHEN exercise IN ('deadlift', 'lat_pulldown', 'bent_over_row', 'one_hand_row', 'chin_up', 't_bar_row', 'shrug', 'back_extension', 'seated_row') THEN 'back'
                                WHEN exercise IN ('shoulder_press', 'arnold_press', 'upright_row', 'front_raise', 'side_raise', 'rear_raise', 'face_pull') THEN 'shoulders'
                                WHEN exercise IN ('barbell_curl', 'dumbbell_curl', 'hammer_curl', 'concentration_curl', 'preacher_curl', 'cable_curl', 'drag_curl', 'reverse_chin_up') THEN 'biceps'
                                WHEN exercise IN ('triceps_extension', 'skull_crusher', 'narrow_bench_press', 'push_down', 'cable_extension', 'overhead_extension', 'french_press', 'press_down', 'kickback', 'reverse_push_up', 'diamond_push_up') THEN 'triceps'
                                WHEN exercise IN ('wrist_curl', 'reverse_wrist_curl', 'farmer_walk') THEN 'forearms'
                                WHEN exercise IN ('squat', 'leg_press', 'leg_extension', 'front_squat', 'goblet_squat', 'split_squat', 'lunge', 'hack_squat', 'sissy_squat') THEN 'quadriceps'
                                WHEN exercise IN ('romanian_deadlift', 'rdl', 'leg_curl', 'good_morning', 'stiff_leg_deadlift', 'back_extension') THEN 'hamstrings'
                                WHEN exercise IN ('hip_thrust', 'bulgarian_squat', 'cable_kickback', 'abduction', 'adduction', 'glute_bridge') THEN 'glutes'
                                WHEN exercise IN ('standing_calf_raise', 'seated_calf_raise') THEN 'calves'
                                WHEN exercise IN ('crunch', 'sit_up', 'leg_raise', 'plank', 'side_plank', 'russian_twist', 'ab_roller', 'bicycle_crunch', 'mountain_climber', 'side_bend', 'knee_to_chest') THEN 'abs'
                                ELSE 'other'
                            END as category,
                            CASE 
                                WHEN exercise IN ('bench_press', 'incline_bench_press', 'decline_bench_press', 'chest_press', 'push_up', 'dips', 'dumbbell_fly', 'incline_dumbbell_fly', 'cable_crossover', 'dumbbell_pullover') THEN '胸'
                                WHEN exercise IN ('deadlift', 'lat_pulldown', 'bent_over_row', 'one_hand_row', 'chin_up', 't_bar_row', 'shrug', 'back_extension', 'seated_row') THEN '背中'
                                WHEN exercise IN ('shoulder_press', 'arnold_press', 'upright_row', 'front_raise', 'side_raise', 'rear_raise', 'face_pull') THEN '肩'
                                WHEN exercise IN ('barbell_curl', 'dumbbell_curl', 'hammer_curl', 'concentration_curl', 'preacher_curl', 'cable_curl', 'drag_curl', 'reverse_chin_up') THEN '上腕二頭筋'
                                WHEN exercise IN ('triceps_extension', 'skull_crusher', 'narrow_bench_press', 'push_down', 'cable_extension', 'overhead_extension', 'french_press', 'press_down', 'kickback', 'reverse_push_up', 'diamond_push_up') THEN '上腕三頭筋'
                                WHEN exercise IN ('wrist_curl', 'reverse_wrist_curl', 'farmer_walk') THEN '前腕'
                                WHEN exercise IN ('squat', 'leg_press', 'leg_extension', 'front_squat', 'goblet_squat', 'split_squat', 'lunge', 'hack_squat', 'sissy_squat') THEN '大腿四頭筋'
                                WHEN exercise IN ('romanian_deadlift', 'rdl', 'leg_curl', 'good_morning', 'stiff_leg_deadlift', 'back_extension') THEN 'ハムストリングス'
                                WHEN exercise IN ('hip_thrust', 'bulgarian_squat', 'cable_kickback', 'abduction', 'adduction', 'glute_bridge') THEN 'お尻'
                                WHEN exercise IN ('standing_calf_raise', 'seated_calf_raise') THEN 'ふくらはぎ'
                                WHEN exercise IN ('crunch', 'sit_up', 'leg_raise', 'plank', 'side_plank', 'russian_twist', 'ab_roller', 'bicycle_crunch', 'mountain_climber', 'side_bend', 'knee_to_chest') THEN '腹筋'
                                ELSE 'その他'
                            END as category_name,
                            SUM(weight_kg * reps) as total_volume,
                            COUNT(*) as workout_count,
                            MAX(date) as latest_date
                        FROM workouts 
                        WHERE user_id = %s 
                        GROUP BY 1, 2
                        HAVING 1 != 'other'
                        ORDER BY total_volume DESC
                    """, (user_id,))
                    summary = cur.fetchall()
                    return [dict(item) for item in summary]
        except Exception as e:
            print(f"部位別集計エラー: {e}")
            return []
    
    def get_workouts_by_category(self, user_id: str, category: str) -> List[Dict]:
        """特定の部位のワークアウト記録を取得"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # カテゴリに応じた種目リストを定義
                    category_exercises = {
                        'chest': ['bench_press', 'incline_bench_press', 'decline_bench_press', 'chest_press', 'push_up', 'dips', 'dumbbell_fly', 'incline_dumbbell_fly', 'cable_crossover', 'dumbbell_pullover'],
                        'back': ['deadlift', 'lat_pulldown', 'bent_over_row', 'one_hand_row', 'chin_up', 't_bar_row', 'shrug', 'back_extension', 'seated_row'],
                        'shoulders': ['shoulder_press', 'arnold_press', 'upright_row', 'front_raise', 'side_raise', 'rear_raise', 'face_pull'],
                        'biceps': ['barbell_curl', 'dumbbell_curl', 'hammer_curl', 'concentration_curl', 'preacher_curl', 'cable_curl', 'drag_curl', 'reverse_chin_up'],
                        'triceps': ['triceps_extension', 'skull_crusher', 'narrow_bench_press', 'push_down', 'cable_extension', 'overhead_extension', 'french_press', 'press_down', 'kickback', 'reverse_push_up', 'diamond_push_up'],
                        'forearms': ['wrist_curl', 'reverse_wrist_curl', 'farmer_walk'],
                        'quadriceps': ['squat', 'leg_press', 'leg_extension', 'front_squat', 'goblet_squat', 'split_squat', 'lunge', 'hack_squat', 'sissy_squat'],
                        'hamstrings': ['romanian_deadlift', 'rdl', 'leg_curl', 'good_morning', 'stiff_leg_deadlift', 'back_extension'],
                        'glutes': ['hip_thrust', 'bulgarian_squat', 'cable_kickback', 'abduction', 'adduction', 'glute_bridge'],
                        'calves': ['standing_calf_raise', 'seated_calf_raise'],
                        'abs': ['crunch', 'sit_up', 'leg_raise', 'plank', 'side_plank', 'russian_twist', 'ab_roller', 'bicycle_crunch', 'mountain_climber', 'side_bend', 'knee_to_chest']
                    }
                    
                    exercises = category_exercises.get(category, [])
                    if not exercises:
                        return []
                    
                    placeholders = ','.join(['%s'] * len(exercises))
                    query = f"""
                        SELECT * FROM workouts 
                        WHERE user_id = %s AND exercise IN ({placeholders})
                        ORDER BY date DESC, created_at DESC
                    """
                    
                    cur.execute(query, [user_id] + exercises)
                    workouts = cur.fetchall()
                    return [dict(workout) for workout in workouts]
        except Exception as e:
            print(f"カテゴリ別ワークアウト取得エラー: {e}")
            return []
    
    def get_workouts_by_date_range(self, user_id: str, start_date: str, end_date: str) -> List[Dict]:
        """日付範囲でワークアウト記録を取得"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT * FROM workouts 
                        WHERE user_id = %s AND date BETWEEN %s AND %s
                        ORDER BY date DESC, created_at DESC
                    """, (user_id, start_date, end_date))
                    workouts = cur.fetchall()
                    return [dict(workout) for workout in workouts]
        except Exception as e:
            print(f"日付範囲ワークアウト取得エラー: {e}")
            return []
    
    def get_exercise_progress(self, user_id: str, exercise: str) -> List[Dict]:
        """特定種目の進捗データを取得"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT date, MAX(weight_kg) as max_weight, 
                               SUM(weight_kg * reps * sets) as total_volume
                        FROM workouts 
                        WHERE user_id = %s AND exercise = %s
                        GROUP BY date
                        ORDER BY date DESC
                        LIMIT 30
                    """, (user_id, exercise))
                    progress = cur.fetchall()
                    return [dict(record) for record in progress]
        except Exception as e:
            print(f"進捗データ取得エラー: {e}")
            return []
    
    def get_max_weights(self, user_id: str) -> Dict[str, float]:
        """各種目の最大重量を取得"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT exercise, MAX(weight_kg) as max_weight
                        FROM workouts 
                        WHERE user_id = %s
                        GROUP BY exercise
                    """, (user_id,))
                    results = cur.fetchall()
                    return {record['exercise']: record['max_weight'] for record in results}
        except Exception as e:
            print(f"最大重量取得エラー: {e}")
            return {}
    
    def delete_workout(self, workout_id: int, user_id: str) -> bool:
        """ワークアウト記録を削除"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        DELETE FROM workouts 
                        WHERE id = %s AND user_id = %s
                    """, (workout_id, user_id))
                    deleted_rows = cur.rowcount
                    conn.commit()
                    return deleted_rows > 0
        except Exception as e:
            print(f"ワークアウト削除エラー: {e}")
            return False

    def get_dashboard_stats(self, user_id: str) -> dict:
        """ダッシュボード用統計データを取得"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # 今月のトレーニング日数
                    cur.execute("""
                        SELECT COUNT(DISTINCT date) as training_days
                        FROM workouts 
                        WHERE user_id = %s 
                        AND date >= date_trunc('month', CURRENT_DATE)
                    """, (user_id,))
                    training_days = cur.fetchone()[0] or 0
                    
                    # 最も頻繁な種目TOP5
                    cur.execute("""
                        SELECT exercise, COUNT(*) as count
                        FROM workouts 
                        WHERE user_id = %s
                        GROUP BY exercise
                        ORDER BY count DESC
                        LIMIT 5
                    """, (user_id,))
                    top_exercises = cur.fetchall()
                    
                    # 今月の総ボリューム
                    cur.execute("""
                        SELECT COALESCE(SUM(weight_kg * reps * sets), 0) as total_volume
                        FROM workouts 
                        WHERE user_id = %s 
                        AND date >= date_trunc('month', CURRENT_DATE)
                    """, (user_id,))
                    total_volume = cur.fetchone()[0] or 0
                    
                    # 個人記録数
                    cur.execute("""
                        SELECT COUNT(DISTINCT exercise) as pr_count
                        FROM workouts 
                        WHERE user_id = %s
                    """, (user_id,))
                    pr_count = cur.fetchone()[0] or 0
                    
                    return {
                        'training_days': training_days,
                        'top_exercises': [{'exercise': ex[0], 'count': ex[1]} for ex in top_exercises],
                        'total_volume': float(total_volume),
                        'pr_count': pr_count
                    }
                    
        except Exception as e:
            print(f"ダッシュボード統計取得エラー: {e}")
            return {}

    def get_chart_progress_data(self, user_id: str, exercise: str) -> dict:
        """グラフ用の進捗データを取得"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT date, MAX(weight_kg) as max_weight
                        FROM workouts 
                        WHERE user_id = %s AND exercise = %s
                        GROUP BY date
                        ORDER BY date
                    """, (user_id, exercise))
                    
                    results = cur.fetchall()
                    
                    return {
                        'exercise': exercise,
                        'data': [
                            {
                                'date': row[0].strftime('%Y-%m-%d'),
                                'weight': float(row[1])
                            }
                            for row in results
                        ]
                    }
                    
        except Exception as e:
            print(f"グラフ進捗データ取得エラー: {e}")
            return {'exercise': exercise, 'data': []}

    def get_calendar_data(self, user_id: str, year: int, month: int) -> dict:
        """カレンダー用のトレーニングデータを取得"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT date, COUNT(*) as workout_count,
                               COUNT(DISTINCT exercise) as exercise_count
                        FROM workouts 
                        WHERE user_id = %s 
                        AND EXTRACT(YEAR FROM date) = %s 
                        AND EXTRACT(MONTH FROM date) = %s
                        GROUP BY date
                        ORDER BY date
                    """, (user_id, year, month))
                    
                    results = cur.fetchall()
                    
                    return {
                        'year': year,
                        'month': month,
                        'training_days': [
                            {
                                'date': row[0].strftime('%Y-%m-%d'),
                                'workout_count': row[1],
                                'exercise_count': row[2]
                            }
                            for row in results
                        ]
                    }
                    
        except Exception as e:
            print(f"カレンダーデータ取得エラー: {e}")
            return {'year': year, 'month': month, 'training_days': []}

    def get_user_settings(self, user_id: str) -> dict:
        """ユーザー設定を取得"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT height_cm, calibration_data
                        FROM user_profiles 
                        WHERE user_id = %s
                    """, (user_id,))
                    
                    result = cur.fetchone()
                    if result:
                        return {
                            'height': result[0],
                            'calibration_data': result[1]
                        }
                    return {}
                    
        except Exception as e:
            print(f"ユーザー設定取得エラー: {e}")
            return {}

    def save_user_settings(self, user_id: str, settings: dict) -> bool:
        """ユーザー設定を保存"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO user_profiles (user_id, height_cm, calibration_data)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (user_id) 
                        DO UPDATE SET 
                            height_cm = EXCLUDED.height_cm,
                            calibration_data = EXCLUDED.calibration_data,
                            updated_at = CURRENT_TIMESTAMP
                    """, (user_id, settings.get('height'), json.dumps(settings)))
                    conn.commit()
                    return True
        except Exception as e:
            print(f"ユーザー設定保存エラー: {e}")
            return False

    def export_user_data(self, user_id: str) -> dict:
        """ユーザーデータをエクスポート"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # ワークアウトデータ
                    cur.execute("""
                        SELECT * FROM workouts 
                        WHERE user_id = %s
                        ORDER BY date DESC
                    """, (user_id,))
                    workouts = cur.fetchall()
                    
                    # プロフィールデータ
                    cur.execute("""
                        SELECT * FROM user_profiles 
                        WHERE user_id = %s
                    """, (user_id,))
                    profile = cur.fetchone()
                    
                    return {
                        'user_id': user_id,
                        'export_date': datetime.now().isoformat(),
                        'workouts': [dict(zip([desc[0] for desc in cur.description], row)) for row in workouts],
                        'profile': dict(zip([desc[0] for desc in cur.description], profile)) if profile else None
                    }
                    
        except Exception as e:
            print(f"データエクスポートエラー: {e}")
            return {}

    def clear_user_data(self, user_id: str) -> bool:
        """ユーザーデータを削除"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM workouts WHERE user_id = %s", (user_id,))
                    cur.execute("DELETE FROM user_profiles WHERE user_id = %s", (user_id,))
                    conn.commit()
                    return True
        except Exception as e:
            print(f"データ削除エラー: {e}")
            return False

# グローバルインスタンス
workout_db = WorkoutDatabase()