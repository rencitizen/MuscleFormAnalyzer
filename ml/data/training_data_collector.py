"""
トレーニングデータ収集システム
MediaPipeポーズデータとメタデータの収集・匿名化・保存
"""

import json
import uuid
import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import csv
import io

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrainingDataCollector:
    """トレーニングデータ収集・管理クラス"""
    
    def __init__(self):
        self.db_url = os.environ.get('DATABASE_URL')
        self.init_database()
        
    def get_connection(self):
        """データベース接続を取得"""
        try:
            return psycopg2.connect(self.db_url)
        except Exception as e:
            logger.error(f"データベース接続エラー: {e}")
            raise
    
    def init_database(self):
        """データ収集用テーブルを初期化"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # トレーニングデータテーブル
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS training_data_collection (
                            id SERIAL PRIMARY KEY,
                            session_id VARCHAR(36) UNIQUE NOT NULL,
                            user_hash VARCHAR(64) NOT NULL,
                            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            exercise VARCHAR(50) NOT NULL,
                            pose_data JSONB NOT NULL,
                            metadata JSONB NOT NULL,
                            performance JSONB NOT NULL,
                            consent_status BOOLEAN DEFAULT FALSE,
                            anonymized BOOLEAN DEFAULT TRUE,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # データ同意記録テーブル
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS data_consent (
                            id SERIAL PRIMARY KEY,
                            user_hash VARCHAR(64) UNIQUE NOT NULL,
                            consent_given BOOLEAN NOT NULL,
                            consent_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            purpose_acknowledged BOOLEAN DEFAULT FALSE,
                            opt_out_date TIMESTAMP NULL,
                            consent_version VARCHAR(10) DEFAULT '1.0'
                        )
                    """)
                    
                    # インデックス作成
                    cur.execute("""
                        CREATE INDEX IF NOT EXISTS idx_training_data_exercise 
                        ON training_data_collection(exercise)
                    """)
                    cur.execute("""
                        CREATE INDEX IF NOT EXISTS idx_training_data_timestamp 
                        ON training_data_collection(timestamp)
                    """)
                    cur.execute("""
                        CREATE INDEX IF NOT EXISTS idx_training_data_user_hash 
                        ON training_data_collection(user_hash)
                    """)
                    
                    conn.commit()
                    logger.info("トレーニングデータ収集テーブルを初期化しました")
                    
        except Exception as e:
            logger.error(f"データベース初期化エラー: {e}")
            raise
    
    def anonymize_user_id(self, user_id: str, salt: str = "tenax_fit_ml") -> str:
        """ユーザーIDを匿名化（ハッシュ化）"""
        try:
            # ソルト付きハッシュでユーザーIDを匿名化
            combined = f"{user_id}_{salt}_{datetime.now().strftime('%Y-%m')}"
            return hashlib.sha256(combined.encode()).hexdigest()
        except Exception as e:
            logger.error(f"ユーザーID匿名化エラー: {e}")
            return hashlib.sha256(f"anonymous_{uuid.uuid4()}".encode()).hexdigest()
    
    def validate_pose_data(self, pose_data: List[List[float]]) -> bool:
        """ポーズデータの妥当性をチェック"""
        try:
            # MediaPipeは33個のランドマークポイント
            if len(pose_data) != 33:
                logger.warning(f"ポーズデータのポイント数が不正: {len(pose_data)}")
                return False
            
            # 各ポイントがx,y,z,visibilityの4次元であることを確認
            for i, point in enumerate(pose_data):
                if len(point) != 4:
                    logger.warning(f"ポイント{i}の次元数が不正: {len(point)}")
                    return False
                
                # 座標値が妥当な範囲内かチェック
                x, y, z, visibility = point
                if not (0 <= x <= 1 and 0 <= y <= 1 and 0 <= visibility <= 1):
                    logger.warning(f"ポイント{i}の値が範囲外: {point}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"ポーズデータ検証エラー: {e}")
            return False
    
    def validate_metadata(self, metadata: Dict[str, Any]) -> bool:
        """メタデータの妥当性をチェック"""
        required_fields = ['height', 'weight', 'experience']
        
        try:
            # 必須フィールドの存在確認
            for field in required_fields:
                if field not in metadata:
                    logger.warning(f"必須メタデータフィールドが不足: {field}")
                    return False
            
            # 値の範囲チェック
            height = metadata.get('height', 0)
            weight = metadata.get('weight', 0)
            experience = metadata.get('experience', '')
            
            if not (100 <= height <= 250):  # 身長: 100-250cm
                logger.warning(f"身長が範囲外: {height}")
                return False
            
            if not (30 <= weight <= 200):  # 体重: 30-200kg
                logger.warning(f"体重が範囲外: {weight}")
                return False
            
            if experience not in ['beginner', 'intermediate', 'advanced']:
                logger.warning(f"経験レベルが不正: {experience}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"メタデータ検証エラー: {e}")
            return False
    
    def validate_performance(self, performance: Dict[str, Any]) -> bool:
        """パフォーマンスデータの妥当性をチェック"""
        try:
            weight = performance.get('weight', 0)
            reps = performance.get('reps', 0)
            form_score = performance.get('form_score', 0)
            
            # 重量: 0-500kg
            if not (0 <= weight <= 500):
                logger.warning(f"重量が範囲外: {weight}")
                return False
            
            # レップ数: 1-100回
            if not (1 <= reps <= 100):
                logger.warning(f"レップ数が範囲外: {reps}")
                return False
            
            # フォームスコア: 0-1
            if not (0 <= form_score <= 1):
                logger.warning(f"フォームスコアが範囲外: {form_score}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"パフォーマンスデータ検証エラー: {e}")
            return False
    
    def check_user_consent(self, user_id: str) -> Dict[str, bool]:
        """ユーザーの同意状況を確認"""
        try:
            user_hash = self.anonymize_user_id(user_id)
            
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT consent_given, consent_date, opt_out_date, purpose_acknowledged
                        FROM data_consent 
                        WHERE user_hash = %s
                    """, (user_hash,))
                    
                    consent_record = cur.fetchone()
                    
                    if not consent_record:
                        return {
                            'has_consent': False,
                            'needs_consent': True,
                            'can_collect': False
                        }
                    
                    # オプトアウトしている場合
                    if consent_record['opt_out_date']:
                        return {
                            'has_consent': False,
                            'needs_consent': False,
                            'can_collect': False,
                            'opted_out': True
                        }
                    
                    return {
                        'has_consent': consent_record['consent_given'],
                        'needs_consent': not consent_record['consent_given'],
                        'can_collect': consent_record['consent_given'] and consent_record['purpose_acknowledged'],
                        'consent_date': consent_record['consent_date'].isoformat() if consent_record['consent_date'] else None
                    }
                    
        except Exception as e:
            logger.error(f"同意状況確認エラー: {e}")
            return {
                'has_consent': False,
                'needs_consent': True,
                'can_collect': False,
                'error': str(e)
            }
    
    def record_user_consent(self, user_id: str, consent_given: bool, purpose_acknowledged: bool = True) -> bool:
        """ユーザーの同意を記録"""
        try:
            user_hash = self.anonymize_user_id(user_id)
            
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # 既存の同意記録を更新または新規作成
                    cur.execute("""
                        INSERT INTO data_consent (user_hash, consent_given, purpose_acknowledged)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (user_hash) 
                        UPDATE SET 
                            consent_given = EXCLUDED.consent_given,
                            purpose_acknowledged = EXCLUDED.purpose_acknowledged,
                            consent_date = CURRENT_TIMESTAMP,
                            opt_out_date = NULL
                    """, (user_hash, consent_given, purpose_acknowledged))
                    
                    conn.commit()
                    logger.info(f"ユーザー同意を記録: {user_hash[:8]}... -> {consent_given}")
                    return True
                    
        except Exception as e:
            logger.error(f"同意記録エラー: {e}")
            return False
    
    def record_opt_out(self, user_id: str) -> bool:
        """ユーザーのオプトアウトを記録"""
        try:
            user_hash = self.anonymize_user_id(user_id)
            
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE data_consent 
                        SET opt_out_date = CURRENT_TIMESTAMP,
                            consent_given = FALSE
                        WHERE user_hash = %s
                    """, (user_hash,))
                    
                    conn.commit()
                    logger.info(f"オプトアウトを記録: {user_hash[:8]}...")
                    return True
                    
        except Exception as e:
            logger.error(f"オプトアウト記録エラー: {e}")
            return False
    
    def collect_training_data(
        self, 
        user_id: str,
        exercise: str,
        pose_data: List[List[float]],
        metadata: Dict[str, Any],
        performance: Dict[str, Any]
    ) -> Dict[str, Any]:
        """トレーニングデータを収集・保存"""
        
        try:
            # 同意確認
            consent_status = self.check_user_consent(user_id)
            if not consent_status.get('can_collect', False):
                return {
                    'success': False,
                    'error': 'データ収集の同意が得られていません',
                    'consent_status': consent_status
                }
            
            # データ検証
            if not self.validate_pose_data(pose_data):
                return {
                    'success': False,
                    'error': 'ポーズデータが無効です'
                }
            
            if not self.validate_metadata(metadata):
                return {
                    'success': False,
                    'error': 'メタデータが無効です'
                }
            
            if not self.validate_performance(performance):
                return {
                    'success': False,
                    'error': 'パフォーマンスデータが無効です'
                }
            
            # セッションIDとユーザーハッシュを生成
            session_id = str(uuid.uuid4())
            user_hash = self.anonymize_user_id(user_id)
            
            # データベースに保存
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO training_data_collection 
                        (session_id, user_hash, exercise, pose_data, metadata, performance, consent_status, anonymized)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (
                        session_id,
                        user_hash,
                        exercise,
                        json.dumps(pose_data),
                        json.dumps(metadata),
                        json.dumps(performance),
                        True,
                        True
                    ))
                    
                    record_id = cur.fetchone()[0]
                    conn.commit()
                    
                    logger.info(f"トレーニングデータを収集: {session_id}")
                    
                    return {
                        'success': True,
                        'session_id': session_id,
                        'record_id': record_id,
                        'anonymized': True,
                        'timestamp': datetime.now().isoformat()
                    }
                    
        except Exception as e:
            logger.error(f"データ収集エラー: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """データ収集統計を取得"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # 総収集数
                    cur.execute("""
                        SELECT COUNT(*) as total_records,
                               COUNT(DISTINCT user_hash) as unique_users,
                               COUNT(DISTINCT exercise) as unique_exercises
                        FROM training_data_collection
                    """)
                    stats = cur.fetchone()
                    
                    # エクササイズ別統計
                    cur.execute("""
                        SELECT exercise, COUNT(*) as count
                        FROM training_data_collection
                        GROUP BY exercise
                        ORDER BY count DESC
                    """)
                    exercise_stats = cur.fetchall()
                    
                    # 最近7日間の収集数
                    cur.execute("""
                        SELECT DATE(timestamp) as date, COUNT(*) as count
                        FROM training_data_collection
                        WHERE timestamp >= CURRENT_DATE - INTERVAL '7 days'
                        GROUP BY DATE(timestamp)
                        ORDER BY date DESC
                    """)
                    recent_stats = cur.fetchall()
                    
                    return {
                        'total_records': stats['total_records'],
                        'unique_users': stats['unique_users'],
                        'unique_exercises': stats['unique_exercises'],
                        'exercise_distribution': [dict(row) for row in exercise_stats],
                        'recent_activity': [dict(row) for row in recent_stats],
                        'timestamp': datetime.now().isoformat()
                    }
                    
        except Exception as e:
            logger.error(f"統計取得エラー: {e}")
            return {'error': str(e)}
    
    def export_training_data(
        self, 
        exercise_filter: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        format: str = 'csv'
    ) -> str:
        """トレーニングデータをエクスポート"""
        try:
            query = """
                SELECT session_id, timestamp, exercise, pose_data, metadata, performance
                FROM training_data_collection
                WHERE consent_status = TRUE
            """
            params = []
            
            # フィルター条件を追加
            if exercise_filter:
                query += " AND exercise = %s"
                params.append(exercise_filter)
            
            if date_from:
                query += " AND timestamp >= %s"
                params.append(date_from)
            
            if date_to:
                query += " AND timestamp <= %s"
                params.append(date_to)
            
            query += " ORDER BY timestamp DESC"
            
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query, params)
                    records = cur.fetchall()
                    
                    if format.lower() == 'csv':
                        return self._export_to_csv(records)
                    elif format.lower() == 'json':
                        return self._export_to_json(records)
                    else:
                        raise ValueError(f"サポートされていない形式: {format}")
                        
        except Exception as e:
            logger.error(f"データエクスポートエラー: {e}")
            raise
    
    def _export_to_csv(self, records: List[Dict]) -> str:
        """CSVフォーマットでエクスポート"""
        output = io.StringIO()
        
        if not records:
            return ""
        
        # ヘッダー行
        fieldnames = [
            'session_id', 'timestamp', 'exercise',
            'height', 'weight', 'experience',
            'performance_weight', 'performance_reps', 'performance_form_score'
        ]
        
        # ポーズデータのカラムを追加（33ポイント × 4次元）
        for i in range(33):
            for coord in ['x', 'y', 'z', 'visibility']:
                fieldnames.append(f'pose_{i}_{coord}')
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for record in records:
            row = {
                'session_id': record['session_id'],
                'timestamp': record['timestamp'].isoformat(),
                'exercise': record['exercise']
            }
            
            # メタデータ
            metadata = json.loads(record['metadata']) if isinstance(record['metadata'], str) else record['metadata']
            row['height'] = metadata.get('height')
            row['weight'] = metadata.get('weight')
            row['experience'] = metadata.get('experience')
            
            # パフォーマンスデータ
            performance = json.loads(record['performance']) if isinstance(record['performance'], str) else record['performance']
            row['performance_weight'] = performance.get('weight')
            row['performance_reps'] = performance.get('reps')
            row['performance_form_score'] = performance.get('form_score')
            
            # ポーズデータ
            pose_data = json.loads(record['pose_data']) if isinstance(record['pose_data'], str) else record['pose_data']
            for i, point in enumerate(pose_data):
                if len(point) >= 4:
                    row[f'pose_{i}_x'] = point[0]
                    row[f'pose_{i}_y'] = point[1]
                    row[f'pose_{i}_z'] = point[2]
                    row[f'pose_{i}_visibility'] = point[3]
            
            writer.writerow(row)
        
        return output.getvalue()
    
    def _export_to_json(self, records: List[Dict]) -> str:
        """JSONフォーマットでエクスポート"""
        export_data = []
        
        for record in records:
            # タイムスタンプを文字列に変換
            record_dict = dict(record)
            if record_dict.get('timestamp'):
                record_dict['timestamp'] = record_dict['timestamp'].isoformat()
            
            export_data.append(record_dict)
        
        return json.dumps(export_data, indent=2, ensure_ascii=False)
    
    def delete_user_data(self, user_id: str) -> bool:
        """ユーザーのデータを削除（GDPR対応）"""
        try:
            user_hash = self.anonymize_user_id(user_id)
            
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # トレーニングデータを削除
                    cur.execute("""
                        DELETE FROM training_data_collection 
                        WHERE user_hash = %s
                    """, (user_hash,))
                    deleted_training = cur.rowcount
                    
                    # 同意記録を削除
                    cur.execute("""
                        DELETE FROM data_consent 
                        WHERE user_hash = %s
                    """, (user_hash,))
                    deleted_consent = cur.rowcount
                    
                    conn.commit()
                    
                    logger.info(f"ユーザーデータを削除: {user_hash[:8]}... (トレーニング: {deleted_training}, 同意: {deleted_consent})")
                    return True
                    
        except Exception as e:
            logger.error(f"ユーザーデータ削除エラー: {e}")
            return False


# 使用例とテスト
if __name__ == "__main__":
    collector = TrainingDataCollector()
    
    # サンプルデータでテスト
    sample_pose_data = []
    for i in range(33):  # MediaPipeの33ポイント
        sample_pose_data.append([
            0.5 + 0.1 * (i % 5) / 5,  # x
            0.3 + 0.4 * i / 33,       # y
            0.1 * (i % 3) / 3,        # z
            0.8 + 0.2 * (i % 2)       # visibility
        ])
    
    sample_metadata = {
        'height': 170,
        'weight': 70,
        'experience': 'intermediate'
    }
    
    sample_performance = {
        'weight': 60,
        'reps': 10,
        'form_score': 0.85
    }
    
    # 同意記録（テスト用）
    test_user_id = "test_user_123"
    collector.record_user_consent(test_user_id, True, True)
    
    # データ収集テスト
    result = collector.collect_training_data(
        user_id=test_user_id,
        exercise='squat',
        pose_data=sample_pose_data,
        metadata=sample_metadata,
        performance=sample_performance
    )
    
    print(f"データ収集結果: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    # 統計取得
    stats = collector.get_collection_stats()
    print(f"収集統計: {json.dumps(stats, indent=2, ensure_ascii=False)}")