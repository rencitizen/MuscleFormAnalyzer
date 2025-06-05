"""
データ前処理モジュール
ポーズランドマークデータの正規化と特徴量抽出
"""

import numpy as np
# pandas import を条件付きに変更
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    # パンダス無しでも動作するようにダミークラスを定義
    class MockDataFrame:
        def __init__(self, data=None):
            self.data = data or []
            self.shape = (len(data) if data else 0, 0)
        
        def to_csv(self, filepath, index=False):
            import json
            with open(filepath.replace('.csv', '.json'), 'w') as f:
                json.dump(self.data, f, indent=2)
        
        @staticmethod
        def read_csv(filepath):
            import json
            try:
                with open(filepath.replace('.csv', '.json'), 'r') as f:
                    data = json.load(f)
                return MockDataFrame(data)
            except:
                return MockDataFrame()
    
    pd = type('MockPandas', (), {'DataFrame': MockDataFrame, 'read_csv': MockDataFrame.read_csv})()
from typing import Dict, List, Tuple, Optional
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PoseDataPreprocessor:
    """ポーズデータの前処理クラス"""
    
    def __init__(self):
        self.scaler = None
        self.feature_names = []
        
    def extract_pose_features(self, landmarks: Dict) -> np.ndarray:
        """
        ランドマークから特徴量を抽出
        
        Args:
            landmarks: MediaPipeから取得したランドマークデータ
            
        Returns:
            特徴量ベクトル
        """
        features = []
        
        # 基本座標特徴量
        for landmark_name, coords in landmarks.items():
            if isinstance(coords, dict):
                features.extend([
                    coords.get('x', 0.0),
                    coords.get('y', 0.0),
                    coords.get('z', 0.0),
                    coords.get('visibility', 1.0)
                ])
        
        # 関節角度特徴量
        angles = self._calculate_joint_angles(landmarks)
        features.extend(angles)
        
        # 距離特徴量
        distances = self._calculate_key_distances(landmarks)
        features.extend(distances)
        
        return np.array(features)
    
    def _calculate_joint_angles(self, landmarks: Dict) -> List[float]:
        """主要関節の角度を計算"""
        angles = []
        
        try:
            # 肩の角度 (左右)
            if all(key in landmarks for key in ['LEFT_SHOULDER', 'LEFT_ELBOW', 'LEFT_WRIST']):
                left_shoulder_angle = self._angle_between_points(
                    landmarks['LEFT_SHOULDER'],
                    landmarks['LEFT_ELBOW'], 
                    landmarks['LEFT_WRIST']
                )
                angles.append(left_shoulder_angle)
            else:
                angles.append(0.0)
                
            if all(key in landmarks for key in ['RIGHT_SHOULDER', 'RIGHT_ELBOW', 'RIGHT_WRIST']):
                right_shoulder_angle = self._angle_between_points(
                    landmarks['RIGHT_SHOULDER'],
                    landmarks['RIGHT_ELBOW'],
                    landmarks['RIGHT_WRIST']
                )
                angles.append(right_shoulder_angle)
            else:
                angles.append(0.0)
            
            # 股関節の角度 (左右)
            if all(key in landmarks for key in ['LEFT_HIP', 'LEFT_KNEE', 'LEFT_ANKLE']):
                left_hip_angle = self._angle_between_points(
                    landmarks['LEFT_HIP'],
                    landmarks['LEFT_KNEE'],
                    landmarks['LEFT_ANKLE']
                )
                angles.append(left_hip_angle)
            else:
                angles.append(0.0)
                
            if all(key in landmarks for key in ['RIGHT_HIP', 'RIGHT_KNEE', 'RIGHT_ANKLE']):
                right_hip_angle = self._angle_between_points(
                    landmarks['RIGHT_HIP'],
                    landmarks['RIGHT_KNEE'],
                    landmarks['RIGHT_ANKLE']
                )
                angles.append(right_hip_angle)
            else:
                angles.append(0.0)
                
        except Exception as e:
            logger.warning(f"角度計算エラー: {e}")
            angles = [0.0] * 4
            
        return angles
    
    def _calculate_key_distances(self, landmarks: Dict) -> List[float]:
        """重要な距離を計算"""
        distances = []
        
        try:
            # 肩幅
            if 'LEFT_SHOULDER' in landmarks and 'RIGHT_SHOULDER' in landmarks:
                shoulder_width = self._distance_between_points(
                    landmarks['LEFT_SHOULDER'],
                    landmarks['RIGHT_SHOULDER']
                )
                distances.append(shoulder_width)
            else:
                distances.append(0.0)
            
            # 腰幅
            if 'LEFT_HIP' in landmarks and 'RIGHT_HIP' in landmarks:
                hip_width = self._distance_between_points(
                    landmarks['LEFT_HIP'],
                    landmarks['RIGHT_HIP']
                )
                distances.append(hip_width)
            else:
                distances.append(0.0)
                
            # 体の高さ（頭頂から足首まで）
            if 'NOSE' in landmarks and 'LEFT_ANKLE' in landmarks:
                body_height = abs(landmarks['NOSE'].get('y', 0) - landmarks['LEFT_ANKLE'].get('y', 0))
                distances.append(body_height)
            else:
                distances.append(0.0)
                
        except Exception as e:
            logger.warning(f"距離計算エラー: {e}")
            distances = [0.0] * 3
            
        return distances
    
    def _angle_between_points(self, p1: Dict, p2: Dict, p3: Dict) -> float:
        """3点間の角度を計算"""
        try:
            # ベクトル計算
            v1 = np.array([p1.get('x', 0) - p2.get('x', 0), 
                          p1.get('y', 0) - p2.get('y', 0)])
            v2 = np.array([p3.get('x', 0) - p2.get('x', 0), 
                          p3.get('y', 0) - p2.get('y', 0)])
            
            # 角度計算
            cosine_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
            angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
            
            return np.degrees(angle)
        except:
            return 0.0
    
    def _distance_between_points(self, p1: Dict, p2: Dict) -> float:
        """2点間の距離を計算"""
        try:
            dx = p1.get('x', 0) - p2.get('x', 0)
            dy = p1.get('y', 0) - p2.get('y', 0)
            dz = p1.get('z', 0) - p2.get('z', 0)
            
            return np.sqrt(dx**2 + dy**2 + dz**2)
        except:
            return 0.0
    
    def process_workout_session(self, session_data: Dict) -> pd.DataFrame:
        """
        ワークアウトセッションデータを処理
        
        Args:
            session_data: セッションの時系列データ
            
        Returns:
            処理済みDataFrame
        """
        processed_data = []
        
        for frame_id, frame_data in session_data.items():
            if 'landmarks' in frame_data:
                features = self.extract_pose_features(frame_data['landmarks'])
                
                # メタデータも追加
                row = {
                    'frame_id': frame_id,
                    'exercise_type': frame_data.get('exercise_type', 'unknown'),
                    'timestamp': frame_data.get('timestamp', 0),
                    'rep_count': frame_data.get('rep_count', 0),
                    'form_score': frame_data.get('form_score', 0)
                }
                
                # 特徴量を追加
                for i, feature in enumerate(features):
                    row[f'feature_{i}'] = feature
                
                processed_data.append(row)
        
        return pd.DataFrame(processed_data)
    
    def save_processed_data(self, df: pd.DataFrame, filepath: str):
        """処理済みデータを保存"""
        try:
            df.to_csv(filepath, index=False)
            logger.info(f"データを保存しました: {filepath}")
        except Exception as e:
            logger.error(f"データ保存エラー: {e}")
    
    def load_processed_data(self, filepath: str) -> pd.DataFrame:
        """処理済みデータを読み込み"""
        try:
            df = pd.read_csv(filepath)
            logger.info(f"データを読み込みました: {filepath}")
            return df
        except Exception as e:
            logger.error(f"データ読み込みエラー: {e}")
            return pd.DataFrame()


class WorkoutDataCollector:
    """ワークアウトデータ収集クラス"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        
    def collect_training_data(self, days: int = 30) -> pd.DataFrame:
        """
        過去のトレーニングデータを収集
        
        Args:
            days: 収集する日数
            
        Returns:
            収集されたデータ
        """
        # データベースから実際のワークアウトデータを取得
        # この部分は既存のワークアウトデータベースと統合
        pass
    
    def export_for_training(self, output_path: str):
        """機械学習用にデータをエクスポート"""
        pass


if __name__ == "__main__":
    # テスト用のサンプルデータ処理
    preprocessor = PoseDataPreprocessor()
    
    # サンプルランドマークデータ
    sample_landmarks = {
        'LEFT_SHOULDER': {'x': 0.5, 'y': 0.3, 'z': 0.1, 'visibility': 0.9},
        'RIGHT_SHOULDER': {'x': 0.4, 'y': 0.3, 'z': 0.1, 'visibility': 0.9},
        'LEFT_ELBOW': {'x': 0.6, 'y': 0.5, 'z': 0.2, 'visibility': 0.8},
        'RIGHT_ELBOW': {'x': 0.3, 'y': 0.5, 'z': 0.2, 'visibility': 0.8},
        'LEFT_WRIST': {'x': 0.7, 'y': 0.7, 'z': 0.3, 'visibility': 0.7},
        'RIGHT_WRIST': {'x': 0.2, 'y': 0.7, 'z': 0.3, 'visibility': 0.7}
    }
    
    features = preprocessor.extract_pose_features(sample_landmarks)
    print(f"抽出された特徴量数: {len(features)}")
    print(f"特徴量: {features[:10]}...")  # 最初の10個を表示