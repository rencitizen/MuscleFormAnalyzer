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
                    # ユーザープロファイルテーブル
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
                            sets INTEGER NOT NULL,
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
                   reps: int, sets: int, notes: str = None, form_analysis_ref: str = None):
        """ワークアウト記録を追加"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO workouts (user_id, date, exercise, weight_kg, reps, sets, notes, form_analysis_ref)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (user_id, date, exercise, weight_kg, reps, sets, notes, form_analysis_ref))
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

# グローバルインスタンス
workout_db = WorkoutDatabase()