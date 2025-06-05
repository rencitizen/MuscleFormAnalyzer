"""
トレーニングデータ前処理パイプライン
収集されたポーズデータのクリーニング、特徴量エンジニアリング、正規化、データ拡張
"""

import numpy as np
import json
import logging
import os
import csv
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import math
import psycopg2
from psycopg2.extras import RealDictCursor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrainingDataPreprocessor:
    """トレーニングデータ前処理クラス"""
    
    def __init__(self):
        self.db_url = os.environ.get('DATABASE_URL')
        
        # MediaPipeランドマークのインデックス定義
        self.landmark_indices = {
            'NOSE': 0, 'LEFT_EYE_INNER': 1, 'LEFT_EYE': 2, 'LEFT_EYE_OUTER': 3,
            'RIGHT_EYE_INNER': 4, 'RIGHT_EYE': 5, 'RIGHT_EYE_OUTER': 6,
            'LEFT_EAR': 7, 'RIGHT_EAR': 8, 'MOUTH_LEFT': 9, 'MOUTH_RIGHT': 10,
            'LEFT_SHOULDER': 11, 'RIGHT_SHOULDER': 12, 'LEFT_ELBOW': 13, 'RIGHT_ELBOW': 14,
            'LEFT_WRIST': 15, 'RIGHT_WRIST': 16, 'LEFT_PINKY': 17, 'RIGHT_PINKY': 18,
            'LEFT_INDEX': 19, 'RIGHT_INDEX': 20, 'LEFT_THUMB': 21, 'RIGHT_THUMB': 22,
            'LEFT_HIP': 23, 'RIGHT_HIP': 24, 'LEFT_KNEE': 25, 'RIGHT_KNEE': 26,
            'LEFT_ANKLE': 27, 'RIGHT_ANKLE': 28, 'LEFT_HEEL': 29, 'RIGHT_HEEL': 30,
            'LEFT_FOOT_INDEX': 31, 'RIGHT_FOOT_INDEX': 32
        }
        
        # 関節角度計算用の定義
        self.joint_angles = {
            'left_elbow': ['LEFT_SHOULDER', 'LEFT_ELBOW', 'LEFT_WRIST'],
            'right_elbow': ['RIGHT_SHOULDER', 'RIGHT_ELBOW', 'RIGHT_WRIST'],
            'left_knee': ['LEFT_HIP', 'LEFT_KNEE', 'LEFT_ANKLE'],
            'right_knee': ['RIGHT_HIP', 'RIGHT_KNEE', 'RIGHT_ANKLE'],
            'left_hip': ['LEFT_SHOULDER', 'LEFT_HIP', 'LEFT_KNEE'],
            'right_hip': ['RIGHT_SHOULDER', 'RIGHT_HIP', 'RIGHT_KNEE'],
            'torso_left': ['LEFT_SHOULDER', 'LEFT_HIP', 'LEFT_KNEE'],
            'torso_right': ['RIGHT_SHOULDER', 'RIGHT_HIP', 'RIGHT_KNEE']
        }
        
    def get_connection(self):
        """データベース接続を取得"""
        return psycopg2.connect(self.db_url)
    
    def load_raw_data(self, exercise_filter: Optional[str] = None, limit: int = 1000) -> List[Dict]:
        """生データをデータベースから読み込み"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    query = """
                        SELECT session_id, exercise, pose_data, metadata, performance, timestamp
                        FROM training_data_collection
                        WHERE consent_status = TRUE AND anonymized = TRUE
                    """
                    params = []
                    
                    if exercise_filter:
                        query += " AND exercise = %s"
                        params.append(exercise_filter)
                    
                    query += " ORDER BY timestamp DESC LIMIT %s"
                    params.append(limit)
                    
                    cur.execute(query, params)
                    raw_data = cur.fetchall()
                    
                    logger.info(f"生データを{len(raw_data)}件読み込みました")
                    return [dict(row) for row in raw_data]
                    
        except Exception as e:
            logger.error(f"データ読み込みエラー: {e}")
            return []
    
    def clean_data(self, raw_data: List[Dict]) -> List[Dict]:
        """データクリーニング処理"""
        cleaned_data = []
        
        for record in raw_data:
            try:
                pose_data = json.loads(record['pose_data']) if isinstance(record['pose_data'], str) else record['pose_data']
                
                # 基本的な検証
                if not self._validate_pose_structure(pose_data):
                    logger.warning(f"不正なポーズ構造をスキップ: {record['session_id']}")
                    continue
                
                # 欠損値の補完
                cleaned_pose = self._fill_missing_landmarks(pose_data)
                
                # 外れ値の除去
                if not self._detect_outliers(cleaned_pose):
                    logger.warning(f"外れ値として除外: {record['session_id']}")
                    continue
                
                # ノイズ除去
                smoothed_pose = self._smooth_landmarks(cleaned_pose)
                
                # クリーニング済みデータを格納
                cleaned_record = record.copy()
                cleaned_record['pose_data'] = smoothed_pose
                cleaned_data.append(cleaned_record)
                
            except Exception as e:
                logger.error(f"クリーニングエラー {record.get('session_id', 'unknown')}: {e}")
                continue
        
        logger.info(f"クリーニング完了: {len(cleaned_data)}/{len(raw_data)}件")
        return cleaned_data
    
    def _validate_pose_structure(self, pose_data: List[List[float]]) -> bool:
        """ポーズデータ構造の検証"""
        if len(pose_data) != 33:
            return False
        
        for point in pose_data:
            if len(point) != 4:  # x, y, z, visibility
                return False
            
            # 座標値の基本範囲チェック
            if not all(isinstance(coord, (int, float)) for coord in point):
                return False
        
        return True
    
    def _fill_missing_landmarks(self, pose_data: List[List[float]]) -> List[List[float]]:
        """欠損ランドマークの補完"""
        filled_pose = []
        
        for i, point in enumerate(pose_data):
            x, y, z, visibility = point
            
            # 可視性が低い場合の補間
            if visibility < 0.3:
                # 隣接する関節からの推定
                interpolated = self._interpolate_landmark(pose_data, i)
                if interpolated:
                    filled_pose.append(interpolated)
                else:
                    # デフォルト値を使用
                    filled_pose.append([0.5, 0.5, 0.0, 0.1])
            else:
                filled_pose.append(point)
        
        return filled_pose
    
    def _interpolate_landmark(self, pose_data: List[List[float]], missing_index: int) -> Optional[List[float]]:
        """隣接関節からのランドマーク補間"""
        # 身体の対称性を利用した補間
        symmetry_pairs = {
            11: 12, 12: 11,  # 肩
            13: 14, 14: 13,  # 肘
            15: 16, 16: 15,  # 手首
            23: 24, 24: 23,  # 腰
            25: 26, 26: 25,  # 膝
            27: 28, 28: 27   # 足首
        }
        
        if missing_index in symmetry_pairs:
            pair_index = symmetry_pairs[missing_index]
            pair_point = pose_data[pair_index]
            
            if pair_point[3] > 0.5:  # ペアの可視性が高い場合
                # 左右反転して推定
                x_flipped = 1.0 - pair_point[0]  # X座標を反転
                return [x_flipped, pair_point[1], pair_point[2], 0.5]
        
        return None
    
    def _detect_outliers(self, pose_data: List[List[float]]) -> bool:
        """外れ値検出"""
        # 基本的な範囲チェック
        for point in pose_data:
            x, y, z, visibility = point
            
            # 座標が異常な範囲にある場合
            if x < -0.5 or x > 1.5 or y < -0.5 or y > 1.5:
                return False
            
            # Z座標の異常値チェック
            if abs(z) > 1.0:
                return False
        
        # 身体比率の妥当性チェック
        if not self._check_body_proportions(pose_data):
            return False
        
        return True
    
    def _check_body_proportions(self, pose_data: List[List[float]]) -> bool:
        """身体比率の妥当性チェック"""
        try:
            # 主要関節の取得
            left_shoulder = pose_data[self.landmark_indices['LEFT_SHOULDER']]
            right_shoulder = pose_data[self.landmark_indices['RIGHT_SHOULDER']]
            left_hip = pose_data[self.landmark_indices['LEFT_HIP']]
            right_hip = pose_data[self.landmark_indices['RIGHT_HIP']]
            
            # 肩幅の計算
            shoulder_width = self._calculate_distance(left_shoulder, right_shoulder)
            
            # 腰幅の計算
            hip_width = self._calculate_distance(left_hip, right_hip)
            
            # 体幹の長さ
            torso_length = self._calculate_distance(
                [(left_shoulder[0] + right_shoulder[0])/2, (left_shoulder[1] + right_shoulder[1])/2, 0, 1],
                [(left_hip[0] + right_hip[0])/2, (left_hip[1] + right_hip[1])/2, 0, 1]
            )
            
            # 比率チェック
            if shoulder_width > 0 and hip_width > 0 and torso_length > 0:
                # 肩幅と腰幅の比率（通常0.8-1.5の範囲）
                shoulder_hip_ratio = shoulder_width / hip_width
                if not (0.8 <= shoulder_hip_ratio <= 1.5):
                    return False
                
                # 体幹の長さと肩幅の比率（通常1.0-3.0の範囲）
                torso_shoulder_ratio = torso_length / shoulder_width
                if not (1.0 <= torso_shoulder_ratio <= 3.0):
                    return False
            
            return True
            
        except Exception:
            return True  # エラーの場合は通す
    
    def _smooth_landmarks(self, pose_data: List[List[float]]) -> List[List[float]]:
        """ランドマークの平滑化"""
        # 単純な移動平均フィルタを適用（時系列データがある場合）
        smoothed_pose = []
        
        for point in pose_data:
            # 現在は単一フレームなので、そのまま返す
            # 実際の実装では時系列データに対して移動平均を適用
            smoothed_pose.append(point)
        
        return smoothed_pose
    
    def extract_features(self, cleaned_data: List[Dict]) -> List[Dict]:
        """特徴量エンジニアリング"""
        featured_data = []
        
        for record in cleaned_data:
            try:
                pose_data = record['pose_data']
                metadata = json.loads(record['metadata']) if isinstance(record['metadata'], str) else record['metadata']
                
                # 基本特徴量の抽出
                features = {}
                
                # 関節角度の計算
                joint_angles = self._calculate_joint_angles(pose_data)
                features.update(joint_angles)
                
                # 距離特徴量
                distance_features = self._calculate_distance_features(pose_data)
                features.update(distance_features)
                
                # 左右バランス指標
                balance_features = self._calculate_balance_features(pose_data)
                features.update(balance_features)
                
                # 身体姿勢特徴量
                posture_features = self._calculate_posture_features(pose_data)
                features.update(posture_features)
                
                # メタデータ特徴量
                meta_features = self._extract_metadata_features(metadata)
                features.update(meta_features)
                
                # 結果を保存
                featured_record = record.copy()
                featured_record['features'] = features
                featured_data.append(featured_record)
                
            except Exception as e:
                logger.error(f"特徴量抽出エラー {record.get('session_id', 'unknown')}: {e}")
                continue
        
        logger.info(f"特徴量抽出完了: {len(featured_data)}件")
        return featured_data
    
    def _calculate_joint_angles(self, pose_data: List[List[float]]) -> Dict[str, float]:
        """関節角度の計算"""
        angles = {}
        
        for joint_name, landmark_names in self.joint_angles.items():
            try:
                # 3点の座標を取得
                point1 = pose_data[self.landmark_indices[landmark_names[0]]]
                point2 = pose_data[self.landmark_indices[landmark_names[1]]]
                point3 = pose_data[self.landmark_indices[landmark_names[2]]]
                
                # 角度を計算
                angle = self._calculate_angle(point1, point2, point3)
                angles[f'angle_{joint_name}'] = angle
                
            except Exception as e:
                logger.debug(f"角度計算エラー {joint_name}: {e}")
                angles[f'angle_{joint_name}'] = 0.0
        
        return angles
    
    def _calculate_angle(self, p1: List[float], p2: List[float], p3: List[float]) -> float:
        """3点間の角度計算"""
        try:
            # ベクトルの計算
            v1 = [p1[0] - p2[0], p1[1] - p2[1], p1[2] - p2[2]]
            v2 = [p3[0] - p2[0], p3[1] - p2[1], p3[2] - p2[2]]
            
            # 内積の計算
            dot_product = sum(a * b for a, b in zip(v1, v2))
            
            # ベクトルの大きさ
            magnitude1 = math.sqrt(sum(a * a for a in v1))
            magnitude2 = math.sqrt(sum(a * a for a in v2))
            
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0
            
            # コサインの計算
            cos_angle = dot_product / (magnitude1 * magnitude2)
            cos_angle = max(-1.0, min(1.0, cos_angle))  # クランプ
            
            # 角度（度）に変換
            angle_rad = math.acos(cos_angle)
            angle_deg = math.degrees(angle_rad)
            
            return angle_deg
            
        except Exception:
            return 0.0
    
    def _calculate_distance_features(self, pose_data: List[List[float]]) -> Dict[str, float]:
        """距離特徴量の計算"""
        distances = {}
        
        try:
            # 主要な距離の計算
            distance_pairs = [
                ('shoulder_width', 'LEFT_SHOULDER', 'RIGHT_SHOULDER'),
                ('hip_width', 'LEFT_HIP', 'RIGHT_HIP'),
                ('torso_length', 'LEFT_SHOULDER', 'LEFT_HIP'),
                ('left_arm_length', 'LEFT_SHOULDER', 'LEFT_WRIST'),
                ('right_arm_length', 'RIGHT_SHOULDER', 'RIGHT_WRIST'),
                ('left_leg_length', 'LEFT_HIP', 'LEFT_ANKLE'),
                ('right_leg_length', 'RIGHT_HIP', 'RIGHT_ANKLE')
            ]
            
            for name, landmark1, landmark2 in distance_pairs:
                p1 = pose_data[self.landmark_indices[landmark1]]
                p2 = pose_data[self.landmark_indices[landmark2]]
                distance = self._calculate_distance(p1, p2)
                distances[f'distance_{name}'] = distance
                
        except Exception as e:
            logger.debug(f"距離計算エラー: {e}")
        
        return distances
    
    def _calculate_distance(self, p1: List[float], p2: List[float]) -> float:
        """2点間の距離計算"""
        try:
            dx = p1[0] - p2[0]
            dy = p1[1] - p2[1]
            dz = p1[2] - p2[2]
            return math.sqrt(dx*dx + dy*dy + dz*dz)
        except Exception:
            return 0.0
    
    def _calculate_balance_features(self, pose_data: List[List[float]]) -> Dict[str, float]:
        """左右バランス特徴量の計算"""
        balance = {}
        
        try:
            # 左右の肩の高さの差
            left_shoulder = pose_data[self.landmark_indices['LEFT_SHOULDER']]
            right_shoulder = pose_data[self.landmark_indices['RIGHT_SHOULDER']]
            shoulder_balance = abs(left_shoulder[1] - right_shoulder[1])
            balance['balance_shoulder_height'] = shoulder_balance
            
            # 左右の腰の高さの差
            left_hip = pose_data[self.landmark_indices['LEFT_HIP']]
            right_hip = pose_data[self.landmark_indices['RIGHT_HIP']]
            hip_balance = abs(left_hip[1] - right_hip[1])
            balance['balance_hip_height'] = hip_balance
            
            # 左右の膝の高さの差
            left_knee = pose_data[self.landmark_indices['LEFT_KNEE']]
            right_knee = pose_data[self.landmark_indices['RIGHT_KNEE']]
            knee_balance = abs(left_knee[1] - right_knee[1])
            balance['balance_knee_height'] = knee_balance
            
            # 重心の計算
            center_x = (left_shoulder[0] + right_shoulder[0] + left_hip[0] + right_hip[0]) / 4
            center_y = (left_shoulder[1] + right_shoulder[1] + left_hip[1] + right_hip[1]) / 4
            balance['center_of_mass_x'] = center_x
            balance['center_of_mass_y'] = center_y
            
        except Exception as e:
            logger.debug(f"バランス計算エラー: {e}")
        
        return balance
    
    def _calculate_posture_features(self, pose_data: List[List[float]]) -> Dict[str, float]:
        """身体姿勢特徴量の計算"""
        posture = {}
        
        try:
            # 体幹の傾き
            left_shoulder = pose_data[self.landmark_indices['LEFT_SHOULDER']]
            right_shoulder = pose_data[self.landmark_indices['RIGHT_SHOULDER']]
            left_hip = pose_data[self.landmark_indices['LEFT_HIP']]
            right_hip = pose_data[self.landmark_indices['RIGHT_HIP']]
            
            # 肩のライン傾き
            shoulder_slope = (right_shoulder[1] - left_shoulder[1]) / (right_shoulder[0] - left_shoulder[0] + 1e-6)
            posture['shoulder_slope'] = math.degrees(math.atan(shoulder_slope))
            
            # 腰のライン傾き
            hip_slope = (right_hip[1] - left_hip[1]) / (right_hip[0] - left_hip[0] + 1e-6)
            posture['hip_slope'] = math.degrees(math.atan(hip_slope))
            
            # 体幹の前後傾
            torso_center_shoulder = [(left_shoulder[0] + right_shoulder[0])/2, (left_shoulder[1] + right_shoulder[1])/2]
            torso_center_hip = [(left_hip[0] + right_hip[0])/2, (left_hip[1] + right_hip[1])/2]
            
            torso_angle = math.degrees(math.atan2(
                torso_center_shoulder[0] - torso_center_hip[0],
                torso_center_hip[1] - torso_center_shoulder[1] + 1e-6
            ))
            posture['torso_lean'] = torso_angle
            
        except Exception as e:
            logger.debug(f"姿勢計算エラー: {e}")
        
        return posture
    
    def _extract_metadata_features(self, metadata: Dict[str, Any]) -> Dict[str, float]:
        """メタデータから特徴量を抽出"""
        meta_features = {}
        
        try:
            # 身長・体重の正規化
            height = float(metadata.get('height', 170))
            weight = float(metadata.get('weight', 70))
            
            meta_features['height_normalized'] = (height - 170) / 30  # 平均170cm、標準偏差30cmで正規化
            meta_features['weight_normalized'] = (weight - 70) / 20   # 平均70kg、標準偏差20kgで正規化
            meta_features['bmi'] = weight / ((height / 100) ** 2)
            
            # 経験レベルのエンコーディング
            experience = metadata.get('experience', 'beginner')
            experience_encoding = {'beginner': 0.0, 'intermediate': 0.5, 'advanced': 1.0}
            meta_features['experience_level'] = experience_encoding.get(experience, 0.0)
            
        except Exception as e:
            logger.debug(f"メタデータ特徴量エラー: {e}")
            meta_features.update({
                'height_normalized': 0.0,
                'weight_normalized': 0.0,
                'bmi': 22.0,
                'experience_level': 0.0
            })
        
        return meta_features
    
    def normalize_data(self, featured_data: List[Dict]) -> List[Dict]:
        """データの正規化"""
        if not featured_data:
            return []
        
        # 特徴量の統計情報を計算
        feature_stats = self._calculate_feature_statistics(featured_data)
        
        normalized_data = []
        for record in featured_data:
            try:
                # 正規化された特徴量を計算
                normalized_features = {}
                features = record['features']
                
                for feature_name, value in features.items():
                    if feature_name in feature_stats:
                        mean = feature_stats[feature_name]['mean']
                        std = feature_stats[feature_name]['std']
                        
                        if std > 0:
                            normalized_value = (value - mean) / std
                        else:
                            normalized_value = 0.0
                        
                        normalized_features[f'{feature_name}_normalized'] = normalized_value
                    else:
                        normalized_features[feature_name] = value
                
                # 正規化されたレコードを作成
                normalized_record = record.copy()
                normalized_record['normalized_features'] = normalized_features
                normalized_data.append(normalized_record)
                
            except Exception as e:
                logger.error(f"正規化エラー {record.get('session_id', 'unknown')}: {e}")
                continue
        
        logger.info(f"正規化完了: {len(normalized_data)}件")
        return normalized_data
    
    def _calculate_feature_statistics(self, featured_data: List[Dict]) -> Dict[str, Dict[str, float]]:
        """特徴量の統計情報を計算"""
        feature_values = {}
        
        # 全ての特徴量値を収集
        for record in featured_data:
            features = record.get('features', {})
            for feature_name, value in features.items():
                if isinstance(value, (int, float)):
                    if feature_name not in feature_values:
                        feature_values[feature_name] = []
                    feature_values[feature_name].append(value)
        
        # 統計情報を計算
        feature_stats = {}
        for feature_name, values in feature_values.items():
            if values:
                mean = np.mean(values)
                std = np.std(values)
                feature_stats[feature_name] = {'mean': mean, 'std': std}
        
        return feature_stats
    
    def augment_data(self, normalized_data: List[Dict], augmentation_factor: int = 2) -> List[Dict]:
        """データ拡張"""
        augmented_data = list(normalized_data)  # 元データを保持
        
        for record in normalized_data:
            for aug_idx in range(augmentation_factor):
                try:
                    augmented_record = self._create_augmented_sample(record, aug_idx)
                    if augmented_record:
                        augmented_data.append(augmented_record)
                except Exception as e:
                    logger.debug(f"データ拡張エラー: {e}")
                    continue
        
        logger.info(f"データ拡張完了: {len(normalized_data)} -> {len(augmented_data)}件")
        return augmented_data
    
    def _create_augmented_sample(self, record: Dict, aug_idx: int) -> Optional[Dict]:
        """拡張サンプルを作成"""
        try:
            pose_data = record['pose_data'].copy()
            
            # 拡張方法を選択
            if aug_idx % 3 == 0:
                # 左右反転
                pose_data = self._flip_horizontally(pose_data)
            elif aug_idx % 3 == 1:
                # 微小ノイズ追加
                pose_data = self._add_noise(pose_data, noise_level=0.02)
            else:
                # スケール変更
                pose_data = self._scale_pose(pose_data, scale_factor=np.random.uniform(0.95, 1.05))
            
            # 拡張レコードを作成
            augmented_record = record.copy()
            augmented_record['pose_data'] = pose_data
            augmented_record['session_id'] = f"{record['session_id']}_aug_{aug_idx}"
            
            # 特徴量を再計算
            features = {}
            joint_angles = self._calculate_joint_angles(pose_data)
            features.update(joint_angles)
            distance_features = self._calculate_distance_features(pose_data)
            features.update(distance_features)
            balance_features = self._calculate_balance_features(pose_data)
            features.update(balance_features)
            posture_features = self._calculate_posture_features(pose_data)
            features.update(posture_features)
            
            # メタデータ特徴量は元のまま
            metadata = json.loads(record['metadata']) if isinstance(record['metadata'], str) else record['metadata']
            meta_features = self._extract_metadata_features(metadata)
            features.update(meta_features)
            
            augmented_record['features'] = features
            
            return augmented_record
            
        except Exception as e:
            logger.debug(f"拡張サンプル作成エラー: {e}")
            return None
    
    def _flip_horizontally(self, pose_data: List[List[float]]) -> List[List[float]]:
        """水平反転"""
        flipped_pose = []
        
        # 左右対称ペアの定義
        flip_pairs = {
            1: 4, 2: 5, 3: 6, 4: 1, 5: 2, 6: 3,  # 目
            7: 8, 8: 7,  # 耳
            9: 10, 10: 9,  # 口
            11: 12, 12: 11,  # 肩
            13: 14, 14: 13,  # 肘
            15: 16, 16: 15,  # 手首
            17: 18, 18: 17,  # 小指
            19: 20, 20: 19,  # 人差し指
            21: 22, 22: 21,  # 親指
            23: 24, 24: 23,  # 腰
            25: 26, 26: 25,  # 膝
            27: 28, 28: 27,  # 足首
            29: 30, 30: 29,  # かかと
            31: 32, 32: 31   # 足の人差し指
        }
        
        # 反転処理
        for i in range(33):
            original_point = pose_data[i].copy()
            
            # X座標を反転
            original_point[0] = 1.0 - original_point[0]
            
            # 左右ペアがある場合は入れ替え
            if i in flip_pairs:
                target_idx = flip_pairs[i]
                target_point = pose_data[target_idx].copy()
                target_point[0] = 1.0 - target_point[0]
                flipped_pose.append(target_point)
            else:
                flipped_pose.append(original_point)
        
        return flipped_pose
    
    def _add_noise(self, pose_data: List[List[float]], noise_level: float = 0.02) -> List[List[float]]:
        """ガウシアンノイズを追加"""
        noisy_pose = []
        
        for point in pose_data:
            noisy_point = point.copy()
            
            # X, Y, Z座標にノイズを追加
            for i in range(3):
                noise = np.random.normal(0, noise_level)
                noisy_point[i] += noise
                
                # 範囲制限
                if i < 2:  # X, Y座標
                    noisy_point[i] = max(0, min(1, noisy_point[i]))
            
            noisy_pose.append(noisy_point)
        
        return noisy_pose
    
    def _scale_pose(self, pose_data: List[List[float]], scale_factor: float) -> List[List[float]]:
        """ポーズのスケール変更"""
        # 重心を計算
        center_x = np.mean([point[0] for point in pose_data])
        center_y = np.mean([point[1] for point in pose_data])
        
        scaled_pose = []
        for point in pose_data:
            scaled_point = point.copy()
            
            # 重心からの距離をスケール
            scaled_point[0] = center_x + (point[0] - center_x) * scale_factor
            scaled_point[1] = center_y + (point[1] - center_y) * scale_factor
            
            # 範囲制限
            scaled_point[0] = max(0, min(1, scaled_point[0]))
            scaled_point[1] = max(0, min(1, scaled_point[1]))
            
            scaled_pose.append(scaled_point)
        
        return scaled_pose
    
    def save_processed_data(self, augmented_data: List[Dict], output_dir: str = 'ml/data/processed'):
        """処理済みデータを保存"""
        os.makedirs(output_dir, exist_ok=True)
        
        # データを訓練・検証・テストに分割
        np.random.shuffle(augmented_data)
        
        total_samples = len(augmented_data)
        train_split = int(total_samples * 0.7)
        val_split = int(total_samples * 0.85)
        
        train_data = augmented_data[:train_split]
        val_data = augmented_data[train_split:val_split]
        test_data = augmented_data[val_split:]
        
        # CSV形式で保存
        datasets = {
            'train': train_data,
            'val': val_data,
            'test': test_data
        }
        
        for dataset_name, data in datasets.items():
            if data:
                csv_path = os.path.join(output_dir, f'{dataset_name}.csv')
                self._save_to_csv(data, csv_path)
                logger.info(f"{dataset_name}データを保存: {csv_path} ({len(data)}件)")
        
        # 統計情報も保存
        stats_path = os.path.join(output_dir, 'preprocessing_stats.json')
        stats = {
            'total_samples': total_samples,
            'train_samples': len(train_data),
            'val_samples': len(val_data),
            'test_samples': len(test_data),
            'processing_date': datetime.now().isoformat()
        }
        
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        logger.info(f"前処理完了: {total_samples}件のデータを処理")
    
    def _save_to_csv(self, data: List[Dict], csv_path: str):
        """データをCSV形式で保存"""
        if not data:
            return
        
        # ヘッダーを準備
        fieldnames = ['session_id', 'exercise', 'timestamp']
        
        # 特徴量のヘッダーを追加
        sample_features = data[0].get('normalized_features', {})
        feature_names = sorted(sample_features.keys())
        fieldnames.extend(feature_names)
        
        # メタデータとパフォーマンスデータのヘッダーも追加
        fieldnames.extend(['height', 'weight', 'experience', 'performance_weight', 'performance_reps', 'performance_form_score'])
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for record in data:
                row = {
                    'session_id': record['session_id'],
                    'exercise': record['exercise'],
                    'timestamp': record['timestamp']
                }
                
                # 正規化された特徴量を追加
                normalized_features = record.get('normalized_features', {})
                for feature_name in feature_names:
                    row[feature_name] = normalized_features.get(feature_name, 0.0)
                
                # メタデータを追加
                metadata = json.loads(record['metadata']) if isinstance(record['metadata'], str) else record['metadata']
                row['height'] = metadata.get('height', 170)
                row['weight'] = metadata.get('weight', 70)
                row['experience'] = metadata.get('experience', 'beginner')
                
                # パフォーマンスデータを追加
                performance = json.loads(record['performance']) if isinstance(record['performance'], str) else record['performance']
                row['performance_weight'] = performance.get('weight', 0)
                row['performance_reps'] = performance.get('reps', 1)
                row['performance_form_score'] = performance.get('form_score', 0.5)
                
                writer.writerow(row)


def main():
    """前処理パイプラインのメイン実行"""
    preprocessor = TrainingDataPreprocessor()
    
    logger.info("トレーニングデータ前処理を開始")
    
    # 1. 生データの読み込み
    raw_data = preprocessor.load_raw_data(limit=500)
    if not raw_data:
        logger.error("生データが見つかりません")
        return
    
    # 2. データクリーニング
    cleaned_data = preprocessor.clean_data(raw_data)
    if not cleaned_data:
        logger.error("クリーニング後にデータが残りませんでした")
        return
    
    # 3. 特徴量エンジニアリング
    featured_data = preprocessor.extract_features(cleaned_data)
    if not featured_data:
        logger.error("特徴量抽出に失敗しました")
        return
    
    # 4. 正規化
    normalized_data = preprocessor.normalize_data(featured_data)
    if not normalized_data:
        logger.error("正規化に失敗しました")
        return
    
    # 5. データ拡張
    augmented_data = preprocessor.augment_data(normalized_data, augmentation_factor=2)
    
    # 6. 保存
    preprocessor.save_processed_data(augmented_data)
    
    logger.info("前処理パイプライン完了")


if __name__ == "__main__":
    main()