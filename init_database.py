#!/usr/bin/env python3
"""
データベース初期化スクリプト
MuscleFormAnalyzerプロジェクト用のデータベーステーブルを作成・初期化
"""

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging
from datetime import datetime
import sys
from dotenv import load_dotenv

# .envファイルを読み込む
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseInitializer:
    """データベース初期化クラス"""
    
    def __init__(self):
        # 環境変数またはデフォルト値を使用
        self.connection_params = {
            'host': os.environ.get('PGHOST', 'localhost'),
            'port': os.environ.get('PGPORT', '5432'),
            'database': os.environ.get('PGDATABASE', 'muscleform_db'),
            'user': os.environ.get('PGUSER', 'postgres'),
            'password': os.environ.get('PGPASSWORD', 'password')
        }
        
        # SQLiteファイルベースのデータベースを使用する場合のパス
        self.sqlite_path = os.environ.get('SQLITE_DB_PATH', 'muscleform.db')
        self.use_sqlite = os.environ.get('USE_SQLITE', 'false').lower() == 'true'
    
    def get_connection(self):
        """データベース接続を取得"""
        if self.use_sqlite:
            import sqlite3
            return sqlite3.connect(self.sqlite_path)
        else:
            return psycopg2.connect(**self.connection_params)
    
    def create_database_if_not_exists(self):
        """データベースが存在しない場合は作成（PostgreSQLのみ）"""
        if self.use_sqlite:
            # SQLiteはファイルベースなので自動作成される
            return
            
        try:
            # デフォルトデータベースに接続
            conn_params = self.connection_params.copy()
            db_name = conn_params.pop('database')
            conn_params['database'] = 'postgres'
            
            conn = psycopg2.connect(**conn_params)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cur = conn.cursor()
            
            # データベースの存在確認
            cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
            exists = cur.fetchone()
            
            if not exists:
                cur.execute(f"CREATE DATABASE {db_name}")
                logger.info(f"データベース '{db_name}' を作成しました")
            else:
                logger.info(f"データベース '{db_name}' は既に存在します")
            
            cur.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"データベース作成エラー: {e}")
            raise
    
    def init_tables(self):
        """全てのテーブルを初期化"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # 1. ユーザー管理テーブル
                    self._create_user_tables(cur)
                    
                    # 2. トレーニング記録テーブル
                    self._create_workout_tables(cur)
                    
                    # 3. フォーム分析テーブル
                    self._create_analysis_tables(cur)
                    
                    # 4. 機械学習関連テーブル
                    self._create_ml_tables(cur)
                    
                    # 5. データ収集テーブル
                    self._create_data_collection_tables(cur)
                    
                    # 6. システム管理テーブル
                    self._create_system_tables(cur)
                    
                    conn.commit()
                    logger.info("全てのテーブルを初期化しました")
                    
        except Exception as e:
            logger.error(f"テーブル初期化エラー: {e}")
            raise
    
    def _create_user_tables(self, cur):
        """ユーザー管理関連のテーブルを作成"""
        # ユーザーアカウントテーブル
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_accounts (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(255) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                is_verified BOOLEAN DEFAULT FALSE,
                last_login TIMESTAMP
            )
        """)
        
        # ユーザープロファイルテーブル
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(255) UNIQUE NOT NULL,
                height_cm FLOAT,
                weight_kg FLOAT,
                age INTEGER,
                gender VARCHAR(20),
                experience_level VARCHAR(50),
                fitness_goals TEXT,
                calibration_data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # ユーザー設定テーブル
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(255) UNIQUE NOT NULL,
                language VARCHAR(10) DEFAULT 'ja',
                theme VARCHAR(20) DEFAULT 'light',
                notifications_enabled BOOLEAN DEFAULT TRUE,
                data_collection_consent BOOLEAN DEFAULT FALSE,
                privacy_settings JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        logger.info("ユーザー管理テーブルを作成しました")
    
    def _create_workout_tables(self, cur):
        """トレーニング記録関連のテーブルを作成"""
        # ワークアウト記録テーブル
        cur.execute("""
            CREATE TABLE IF NOT EXISTS workouts (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                date DATE NOT NULL,
                exercise VARCHAR(100) NOT NULL,
                exercise_name VARCHAR(255),
                category VARCHAR(100),
                weight_kg FLOAT NOT NULL,
                reps INTEGER NOT NULL,
                sets INTEGER DEFAULT 1,
                rest_seconds INTEGER,
                notes TEXT,
                form_analysis_ref VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # ワークアウトセッションテーブル
        cur.execute("""
            CREATE TABLE IF NOT EXISTS workout_sessions (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                session_date DATE NOT NULL,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                total_exercises INTEGER DEFAULT 0,
                total_sets INTEGER DEFAULT 0,
                total_volume FLOAT DEFAULT 0,
                session_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 個人記録テーブル
        cur.execute("""
            CREATE TABLE IF NOT EXISTS personal_records (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                exercise VARCHAR(100) NOT NULL,
                record_type VARCHAR(50) NOT NULL, -- '1RM', '5RM', 'max_reps', etc.
                value FLOAT NOT NULL,
                date_achieved DATE NOT NULL,
                previous_value FLOAT,
                improvement_percentage FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # インデックスを作成
        cur.execute("CREATE INDEX IF NOT EXISTS idx_workouts_user_date ON workouts(user_id, date DESC)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_workouts_exercise ON workouts(user_id, exercise, date DESC)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_workout_sessions_user ON workout_sessions(user_id, session_date DESC)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_personal_records_user ON personal_records(user_id, exercise, record_type)")
        
        logger.info("トレーニング記録テーブルを作成しました")
    
    def _create_analysis_tables(self, cur):
        """フォーム分析関連のテーブルを作成"""
        # フォーム分析結果テーブル
        cur.execute("""
            CREATE TABLE IF NOT EXISTS form_analysis_results (
                id SERIAL PRIMARY KEY,
                analysis_id VARCHAR(255) UNIQUE NOT NULL,
                user_id VARCHAR(255) NOT NULL,
                exercise_type VARCHAR(100) NOT NULL,
                video_path VARCHAR(500),
                analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                rep_count INTEGER,
                overall_score FLOAT,
                form_score FLOAT,
                depth_score FLOAT,
                tempo_score FLOAT,
                balance_score FLOAT,
                stability_score FLOAT,
                detailed_results JSONB,
                feedback JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # フレーム単位の分析データテーブル
        cur.execute("""
            CREATE TABLE IF NOT EXISTS frame_analysis_data (
                id SERIAL PRIMARY KEY,
                analysis_id VARCHAR(255) NOT NULL,
                frame_number INTEGER NOT NULL,
                timestamp_ms INTEGER,
                pose_landmarks JSONB,
                joint_angles JSONB,
                form_metrics JSONB,
                phase VARCHAR(50), -- 'start', 'middle', 'end'
                quality_score FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # インデックスを作成
        cur.execute("CREATE INDEX IF NOT EXISTS idx_form_analysis_user ON form_analysis_results(user_id, analysis_date DESC)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_frame_analysis ON frame_analysis_data(analysis_id, frame_number)")
        
        logger.info("フォーム分析テーブルを作成しました")
    
    def _create_ml_tables(self, cur):
        """機械学習関連のテーブルを作成"""
        # MLモデル管理テーブル
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ml_models (
                id SERIAL PRIMARY KEY,
                model_name VARCHAR(255) UNIQUE NOT NULL,
                model_type VARCHAR(100) NOT NULL,
                version VARCHAR(50) NOT NULL,
                file_path VARCHAR(500),
                accuracy FLOAT,
                training_date TIMESTAMP,
                training_samples INTEGER,
                feature_importance JSONB,
                hyperparameters JSONB,
                is_active BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # ML推論ログテーブル
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ml_inference_logs (
                id SERIAL PRIMARY KEY,
                model_id INTEGER,
                user_id VARCHAR(255),
                inference_type VARCHAR(100),
                input_data JSONB,
                predictions JSONB,
                confidence_scores JSONB,
                processing_time_ms INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        logger.info("機械学習テーブルを作成しました")
    
    def _create_data_collection_tables(self, cur):
        """データ収集関連のテーブルを作成"""
        # トレーニングデータ収集テーブル
        cur.execute("""
            CREATE TABLE IF NOT EXISTS training_data_collection (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255) UNIQUE NOT NULL,
                user_id VARCHAR(255) NOT NULL,
                exercise VARCHAR(100) NOT NULL,
                pose_data JSONB NOT NULL,
                metadata JSONB,
                performance JSONB,
                quality_score FLOAT,
                consent_status BOOLEAN DEFAULT FALSE,
                anonymized BOOLEAN DEFAULT FALSE,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # ユーザー同意管理テーブル
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_consent_records (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                consent_type VARCHAR(100) NOT NULL,
                consent_given BOOLEAN NOT NULL,
                consent_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address VARCHAR(45),
                user_agent TEXT,
                expires_at TIMESTAMP
            )
        """)
        
        # インデックスを作成
        cur.execute("CREATE INDEX IF NOT EXISTS idx_training_data_user ON training_data_collection(user_id, timestamp DESC)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_training_data_exercise ON training_data_collection(exercise, timestamp DESC)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_consent_records ON user_consent_records(user_id, consent_type, consent_date DESC)")
        
        logger.info("データ収集テーブルを作成しました")
    
    def _create_system_tables(self, cur):
        """システム管理関連のテーブルを作成"""
        # システムログテーブル
        cur.execute("""
            CREATE TABLE IF NOT EXISTS system_logs (
                id SERIAL PRIMARY KEY,
                log_level VARCHAR(20) NOT NULL,
                log_type VARCHAR(100) NOT NULL,
                message TEXT NOT NULL,
                details JSONB,
                user_id VARCHAR(255),
                ip_address VARCHAR(45),
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # APIアクセストークンテーブル
        cur.execute("""
            CREATE TABLE IF NOT EXISTS api_tokens (
                id SERIAL PRIMARY KEY,
                token_hash VARCHAR(255) UNIQUE NOT NULL,
                user_id VARCHAR(255) NOT NULL,
                name VARCHAR(255),
                permissions JSONB,
                last_used TIMESTAMP,
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        """)
        
        # セッション管理テーブル
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id SERIAL PRIMARY KEY,
                session_token VARCHAR(255) UNIQUE NOT NULL,
                user_id VARCHAR(255) NOT NULL,
                ip_address VARCHAR(45),
                user_agent TEXT,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # インデックスを作成
        cur.execute("CREATE INDEX IF NOT EXISTS idx_system_logs_date ON system_logs(created_at DESC)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_user_sessions_user ON user_sessions(user_id)")
        
        logger.info("システム管理テーブルを作成しました")
    
    def create_sample_data(self):
        """サンプルデータを作成（開発用）"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # サンプルユーザーを作成
                    cur.execute("""
                        INSERT INTO user_accounts (user_id, email, password_hash, is_verified)
                        VALUES ('demo_user', 'demo@example.com', 'hashed_password_here', TRUE)
                        ON CONFLICT (user_id) DO NOTHING
                    """)
                    
                    cur.execute("""
                        INSERT INTO user_profiles (user_id, height_cm, weight_kg, experience_level)
                        VALUES ('demo_user', 170, 70, 'intermediate')
                        ON CONFLICT (user_id) DO NOTHING
                    """)
                    
                    # サンプルワークアウトデータ
                    sample_workouts = [
                        ('2024-01-01', 'squat', 'スクワット', 'legs', 60, 10),
                        ('2024-01-01', 'bench_press', 'ベンチプレス', 'chest', 50, 8),
                        ('2024-01-03', 'deadlift', 'デッドリフト', 'back', 80, 5),
                        ('2024-01-05', 'squat', 'スクワット', 'legs', 65, 8),
                        ('2024-01-05', 'overhead_press', 'オーバーヘッドプレス', 'shoulders', 30, 10),
                    ]
                    
                    for date, exercise, name, category, weight, reps in sample_workouts:
                        cur.execute("""
                            INSERT INTO workouts (user_id, date, exercise, exercise_name, category, weight_kg, reps)
                            VALUES ('demo_user', %s, %s, %s, %s, %s, %s)
                        """, (date, exercise, name, category, weight, reps))
                    
                    conn.commit()
                    logger.info("サンプルデータを作成しました")
                    
        except Exception as e:
            logger.error(f"サンプルデータ作成エラー: {e}")


def main():
    """メイン実行関数"""
    logger.info("=== MuscleFormAnalyzer データベース初期化開始 ===")
    
    initializer = DatabaseInitializer()
    
    try:
        # PostgreSQLの場合はデータベースを作成
        if not initializer.use_sqlite:
            initializer.create_database_if_not_exists()
        
        # テーブルを初期化
        initializer.init_tables()
        
        # 開発環境の場合はサンプルデータを作成
        if os.environ.get('ENV', 'development') == 'development':
            response = input("サンプルデータを作成しますか？ (y/n): ")
            if response.lower() == 'y':
                initializer.create_sample_data()
        
        logger.info("=== データベース初期化完了 ===")
        
    except Exception as e:
        logger.error(f"初期化エラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()