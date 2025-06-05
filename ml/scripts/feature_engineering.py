"""
高度な特徴量エンジニアリング
時系列特徴量、動作パターン解析、フォーム品質評価
"""

import numpy as np
import json
import logging
from typing import Dict, List, Tuple, Optional, Any
import math
from scipy.signal import savgol_filter
from scipy.spatial.distance import euclidean

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdvancedFeatureEngineer:
    """高度な特徴量エンジニアリングクラス"""
    
    def __init__(self):
        # MediaPipeランドマークインデックス
        self.landmarks = {
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
        
        # エクササイズ別の重要関節
        self.exercise_key_joints = {
            'squat': ['LEFT_HIP', 'RIGHT_HIP', 'LEFT_KNEE', 'RIGHT_KNEE', 'LEFT_ANKLE', 'RIGHT_ANKLE'],
            'deadlift': ['LEFT_HIP', 'RIGHT_HIP', 'LEFT_KNEE', 'RIGHT_KNEE', 'LEFT_SHOULDER', 'RIGHT_SHOULDER'],
            'bench_press': ['LEFT_SHOULDER', 'RIGHT_SHOULDER', 'LEFT_ELBOW', 'RIGHT_ELBOW', 'LEFT_WRIST', 'RIGHT_WRIST'],
            'overhead_press': ['LEFT_SHOULDER', 'RIGHT_SHOULDER', 'LEFT_ELBOW', 'RIGHT_ELBOW', 'LEFT_WRIST', 'RIGHT_WRIST'],
            'row': ['LEFT_SHOULDER', 'RIGHT_SHOULDER', 'LEFT_ELBOW', 'RIGHT_ELBOW', 'LEFT_HIP', 'RIGHT_HIP']
        }
    
    def extract_temporal_features(self, pose_sequence: List[List[List[float]]], exercise: str) -> Dict[str, float]:
        """時系列特徴量の抽出"""
        features = {}
        
        if len(pose_sequence) < 3:
            return features
        
        # 動作速度の計算
        velocity_features = self._calculate_velocity_features(pose_sequence, exercise)
        features.update(velocity_features)
        
        # 加速度の計算
        acceleration_features = self._calculate_acceleration_features(pose_sequence, exercise)
        features.update(acceleration_features)
        
        # 滑らかさの評価
        smoothness_features = self._calculate_smoothness_features(pose_sequence, exercise)
        features.update(smoothness_features)
        
        # リズムの一貫性
        rhythm_features = self._calculate_rhythm_features(pose_sequence, exercise)
        features.update(rhythm_features)
        
        return features
    
    def _calculate_velocity_features(self, pose_sequence: List[List[List[float]]], exercise: str) -> Dict[str, float]:
        """動作速度特徴量の計算"""
        features = {}
        key_joints = self.exercise_key_joints.get(exercise, list(self.landmarks.keys())[:10])
        
        for joint_name in key_joints:
            joint_idx = self.landmarks[joint_name]
            
            # 各フレーム間の速度を計算
            velocities = []
            for i in range(1, len(pose_sequence)):
                prev_pos = pose_sequence[i-1][joint_idx][:3]
                curr_pos = pose_sequence[i][joint_idx][:3]
                
                velocity = euclidean(curr_pos, prev_pos)
                velocities.append(velocity)
            
            if velocities:
                features[f'velocity_mean_{joint_name.lower()}'] = np.mean(velocities)
                features[f'velocity_std_{joint_name.lower()}'] = np.std(velocities)
                features[f'velocity_max_{joint_name.lower()}'] = np.max(velocities)
        
        return features
    
    def _calculate_acceleration_features(self, pose_sequence: List[List[List[float]]], exercise: str) -> Dict[str, float]:
        """加速度特徴量の計算"""
        features = {}
        key_joints = self.exercise_key_joints.get(exercise, list(self.landmarks.keys())[:10])
        
        for joint_name in key_joints:
            joint_idx = self.landmarks[joint_name]
            
            # 加速度の計算（2次差分）
            accelerations = []
            for i in range(2, len(pose_sequence)):
                pos_prev2 = pose_sequence[i-2][joint_idx][:3]
                pos_prev1 = pose_sequence[i-1][joint_idx][:3]
                pos_curr = pose_sequence[i][joint_idx][:3]
                
                # 2次差分による加速度近似
                acc_x = pos_curr[0] - 2*pos_prev1[0] + pos_prev2[0]
                acc_y = pos_curr[1] - 2*pos_prev1[1] + pos_prev2[1]
                acc_z = pos_curr[2] - 2*pos_prev1[2] + pos_prev2[2]
                
                acceleration = math.sqrt(acc_x**2 + acc_y**2 + acc_z**2)
                accelerations.append(acceleration)
            
            if accelerations:
                features[f'acceleration_mean_{joint_name.lower()}'] = np.mean(accelerations)
                features[f'acceleration_std_{joint_name.lower()}'] = np.std(accelerations)
        
        return features
    
    def _calculate_smoothness_features(self, pose_sequence: List[List[List[float]]], exercise: str) -> Dict[str, float]:
        """動作の滑らかさ評価"""
        features = {}
        key_joints = self.exercise_key_joints.get(exercise, list(self.landmarks.keys())[:5])
        
        for joint_name in key_joints:
            joint_idx = self.landmarks[joint_name]
            
            # 各軸の座標系列を取得
            x_coords = [pose[joint_idx][0] for pose in pose_sequence]
            y_coords = [pose[joint_idx][1] for pose in pose_sequence]
            z_coords = [pose[joint_idx][2] for pose in pose_sequence]
            
            # Savitzky-Golayフィルタで平滑化
            if len(x_coords) >= 5:
                try:
                    x_smooth = savgol_filter(x_coords, window_length=min(5, len(x_coords)), polyorder=2)
                    y_smooth = savgol_filter(y_coords, window_length=min(5, len(y_coords)), polyorder=2)
                    z_smooth = savgol_filter(z_coords, window_length=min(5, len(z_coords)), polyorder=2)
                    
                    # 元データと平滑化データの差（ジャーク指標）
                    x_jerk = np.mean(np.abs(np.array(x_coords) - x_smooth))
                    y_jerk = np.mean(np.abs(np.array(y_coords) - y_smooth))
                    z_jerk = np.mean(np.abs(np.array(z_coords) - z_smooth))
                    
                    features[f'jerk_{joint_name.lower()}'] = (x_jerk + y_jerk + z_jerk) / 3
                    
                except Exception as e:
                    logger.debug(f"平滑化計算エラー {joint_name}: {e}")
        
        return features
    
    def _calculate_rhythm_features(self, pose_sequence: List[List[List[float]]], exercise: str) -> Dict[str, float]:
        """リズムの一貫性評価"""
        features = {}
        
        # 主要関節の動きからリズムを検出
        if exercise in ['squat', 'deadlift']:
            # 下半身の動きを解析
            hip_trajectory = self._get_joint_trajectory(pose_sequence, 'LEFT_HIP')
            knee_trajectory = self._get_joint_trajectory(pose_sequence, 'LEFT_KNEE')
            
            # 動作の周期性を評価
            hip_periods = self._detect_movement_periods(hip_trajectory)
            knee_periods = self._detect_movement_periods(knee_trajectory)
            
            if hip_periods:
                features['hip_rhythm_consistency'] = np.std(hip_periods) / (np.mean(hip_periods) + 1e-6)
            if knee_periods:
                features['knee_rhythm_consistency'] = np.std(knee_periods) / (np.mean(knee_periods) + 1e-6)
        
        elif exercise in ['bench_press', 'overhead_press']:
            # 上半身の動きを解析
            shoulder_trajectory = self._get_joint_trajectory(pose_sequence, 'LEFT_SHOULDER')
            elbow_trajectory = self._get_joint_trajectory(pose_sequence, 'LEFT_ELBOW')
            
            shoulder_periods = self._detect_movement_periods(shoulder_trajectory)
            elbow_periods = self._detect_movement_periods(elbow_trajectory)
            
            if shoulder_periods:
                features['shoulder_rhythm_consistency'] = np.std(shoulder_periods) / (np.mean(shoulder_periods) + 1e-6)
            if elbow_periods:
                features['elbow_rhythm_consistency'] = np.std(elbow_periods) / (np.mean(elbow_periods) + 1e-6)
        
        return features
    
    def _get_joint_trajectory(self, pose_sequence: List[List[List[float]]], joint_name: str) -> List[float]:
        """関節の軌跡を取得"""
        joint_idx = self.landmarks[joint_name]
        trajectory = []
        
        for pose in pose_sequence:
            # Y座標（上下動）を主に使用
            trajectory.append(pose[joint_idx][1])
        
        return trajectory
    
    def _detect_movement_periods(self, trajectory: List[float]) -> List[int]:
        """動作の周期を検出"""
        if len(trajectory) < 10:
            return []
        
        # 移動平均で平滑化
        smoothed = np.convolve(trajectory, np.ones(3)/3, mode='valid')
        
        # ピーク検出
        peaks = []
        valleys = []
        
        for i in range(1, len(smoothed) - 1):
            if smoothed[i] > smoothed[i-1] and smoothed[i] > smoothed[i+1]:
                peaks.append(i)
            elif smoothed[i] < smoothed[i-1] and smoothed[i] < smoothed[i+1]:
                valleys.append(i)
        
        # 周期の計算（ピーク間の距離）
        periods = []
        for i in range(1, len(peaks)):
            periods.append(peaks[i] - peaks[i-1])
        
        return periods
    
    def extract_form_quality_features(self, pose_data: List[List[float]], exercise: str, metadata: Dict) -> Dict[str, float]:
        """フォーム品質特徴量の抽出"""
        features = {}
        
        # エクササイズ別のフォーム評価
        if exercise == 'squat':
            squat_features = self._evaluate_squat_form(pose_data, metadata)
            features.update(squat_features)
        elif exercise == 'deadlift':
            deadlift_features = self._evaluate_deadlift_form(pose_data, metadata)
            features.update(deadlift_features)
        elif exercise == 'bench_press':
            bench_features = self._evaluate_bench_press_form(pose_data, metadata)
            features.update(bench_features)
        
        # 一般的なフォーム特徴量
        general_features = self._evaluate_general_form(pose_data)
        features.update(general_features)
        
        return features
    
    def _evaluate_squat_form(self, pose_data: List[List[float]], metadata: Dict) -> Dict[str, float]:
        """スクワットフォーム評価"""
        features = {}
        
        try:
            # 主要関節の取得
            left_hip = pose_data[self.landmarks['LEFT_HIP']]
            right_hip = pose_data[self.landmarks['RIGHT_HIP']]
            left_knee = pose_data[self.landmarks['LEFT_KNEE']]
            right_knee = pose_data[self.landmarks['RIGHT_KNEE']]
            left_ankle = pose_data[self.landmarks['LEFT_ANKLE']]
            right_ankle = pose_data[self.landmarks['RIGHT_ANKLE']]
            
            # 膝の角度評価
            left_knee_angle = self._calculate_angle_3d(
                pose_data[self.landmarks['LEFT_HIP']],
                pose_data[self.landmarks['LEFT_KNEE']],
                pose_data[self.landmarks['LEFT_ANKLE']]
            )
            right_knee_angle = self._calculate_angle_3d(
                pose_data[self.landmarks['RIGHT_HIP']],
                pose_data[self.landmarks['RIGHT_KNEE']],
                pose_data[self.landmarks['RIGHT_ANKLE']]
            )
            
            features['squat_knee_angle_left'] = left_knee_angle
            features['squat_knee_angle_right'] = right_knee_angle
            features['squat_knee_symmetry'] = abs(left_knee_angle - right_knee_angle)
            
            # 膝の前方突出評価
            knee_forward_left = left_knee[0] - left_ankle[0]  # 膝が足首より前に出ているか
            knee_forward_right = right_knee[0] - right_ankle[0]
            
            features['squat_knee_forward_left'] = knee_forward_left
            features['squat_knee_forward_right'] = knee_forward_right
            
            # 腰の深さ評価
            hip_center_y = (left_hip[1] + right_hip[1]) / 2
            knee_center_y = (left_knee[1] + right_knee[1]) / 2
            hip_knee_depth = knee_center_y - hip_center_y  # 正値: 膝より腰が上
            
            features['squat_depth'] = hip_knee_depth
            
            # 体幹の前傾評価
            torso_lean = self._calculate_torso_lean(pose_data)
            features['squat_torso_lean'] = torso_lean
            
        except Exception as e:
            logger.debug(f"スクワットフォーム評価エラー: {e}")
        
        return features
    
    def _evaluate_deadlift_form(self, pose_data: List[List[float]], metadata: Dict) -> Dict[str, float]:
        """デッドリフトフォーム評価"""
        features = {}
        
        try:
            # バーベルの軌跡（手首の位置で代用）
            left_wrist = pose_data[self.landmarks['LEFT_WRIST']]
            right_wrist = pose_data[self.landmarks['RIGHT_WRIST']]
            bar_center = [(left_wrist[0] + right_wrist[0])/2, (left_wrist[1] + right_wrist[1])/2]
            
            # 腰の位置
            left_hip = pose_data[self.landmarks['LEFT_HIP']]
            right_hip = pose_data[self.landmarks['RIGHT_HIP']]
            hip_center = [(left_hip[0] + right_hip[0])/2, (left_hip[1] + right_hip[1])/2]
            
            # バーパスの評価（バーが体に近いか）
            bar_distance_from_body = abs(bar_center[0] - hip_center[0])
            features['deadlift_bar_path'] = bar_distance_from_body
            
            # 背中の丸まり評価
            back_curvature = self._calculate_back_curvature(pose_data)
            features['deadlift_back_curvature'] = back_curvature
            
            # 膝とつま先の方向性
            knee_toe_alignment = self._calculate_knee_toe_alignment(pose_data)
            features['deadlift_knee_toe_alignment'] = knee_toe_alignment
            
        except Exception as e:
            logger.debug(f"デッドリフトフォーム評価エラー: {e}")
        
        return features
    
    def _evaluate_bench_press_form(self, pose_data: List[List[float]], metadata: Dict) -> Dict[str, float]:
        """ベンチプレスフォーム評価"""
        features = {}
        
        try:
            # 肘の角度
            left_elbow_angle = self._calculate_angle_3d(
                pose_data[self.landmarks['LEFT_SHOULDER']],
                pose_data[self.landmarks['LEFT_ELBOW']],
                pose_data[self.landmarks['LEFT_WRIST']]
            )
            right_elbow_angle = self._calculate_angle_3d(
                pose_data[self.landmarks['RIGHT_SHOULDER']],
                pose_data[self.landmarks['RIGHT_ELBOW']],
                pose_data[self.landmarks['RIGHT_WRIST']]
            )
            
            features['bench_elbow_angle_left'] = left_elbow_angle
            features['bench_elbow_angle_right'] = right_elbow_angle
            features['bench_elbow_symmetry'] = abs(left_elbow_angle - right_elbow_angle)
            
            # 肩の安定性（肩甲骨の位置）
            shoulder_stability = self._calculate_shoulder_stability(pose_data)
            features['bench_shoulder_stability'] = shoulder_stability
            
            # 手首の位置（肘の真上にあるか）
            wrist_alignment = self._calculate_wrist_alignment(pose_data)
            features['bench_wrist_alignment'] = wrist_alignment
            
        except Exception as e:
            logger.debug(f"ベンチプレスフォーム評価エラー: {e}")
        
        return features
    
    def _evaluate_general_form(self, pose_data: List[List[float]]) -> Dict[str, float]:
        """一般的なフォーム特徴量"""
        features = {}
        
        try:
            # 左右対称性の評価
            symmetry_score = self._calculate_overall_symmetry(pose_data)
            features['overall_symmetry'] = symmetry_score
            
            # 安定性の評価
            stability_score = self._calculate_stability(pose_data)
            features['overall_stability'] = stability_score
            
            # 姿勢の評価
            posture_score = self._calculate_posture_quality(pose_data)
            features['overall_posture'] = posture_score
            
        except Exception as e:
            logger.debug(f"一般フォーム評価エラー: {e}")
        
        return features
    
    def _calculate_angle_3d(self, p1: List[float], p2: List[float], p3: List[float]) -> float:
        """3次元空間での角度計算"""
        try:
            v1 = np.array([p1[0] - p2[0], p1[1] - p2[1], p1[2] - p2[2]])
            v2 = np.array([p3[0] - p2[0], p3[1] - p2[1], p3[2] - p2[2]])
            
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
            cos_angle = np.clip(cos_angle, -1.0, 1.0)
            
            angle = np.arccos(cos_angle)
            return np.degrees(angle)
        except Exception:
            return 0.0
    
    def _calculate_torso_lean(self, pose_data: List[List[float]]) -> float:
        """体幹の前傾角度計算"""
        try:
            left_shoulder = pose_data[self.landmarks['LEFT_SHOULDER']]
            right_shoulder = pose_data[self.landmarks['RIGHT_SHOULDER']]
            left_hip = pose_data[self.landmarks['LEFT_HIP']]
            right_hip = pose_data[self.landmarks['RIGHT_HIP']]
            
            shoulder_center = [(left_shoulder[0] + right_shoulder[0])/2, (left_shoulder[1] + right_shoulder[1])/2]
            hip_center = [(left_hip[0] + right_hip[0])/2, (left_hip[1] + right_hip[1])/2]
            
            # 垂直線からの角度
            dx = shoulder_center[0] - hip_center[0]
            dy = hip_center[1] - shoulder_center[1]  # Y軸は下向きが正
            
            angle = math.degrees(math.atan2(dx, dy + 1e-6))
            return angle
        except Exception:
            return 0.0
    
    def _calculate_back_curvature(self, pose_data: List[List[float]]) -> float:
        """背中の丸まり評価"""
        try:
            # 首、肩、腰の3点から曲率を計算
            nose = pose_data[self.landmarks['NOSE']]
            left_shoulder = pose_data[self.landmarks['LEFT_SHOULDER']]
            right_shoulder = pose_data[self.landmarks['RIGHT_SHOULDER']]
            left_hip = pose_data[self.landmarks['LEFT_HIP']]
            right_hip = pose_data[self.landmarks['RIGHT_HIP']]
            
            shoulder_center = [(left_shoulder[0] + right_shoulder[0])/2, (left_shoulder[1] + right_shoulder[1])/2]
            hip_center = [(left_hip[0] + right_hip[0])/2, (left_hip[1] + right_hip[1])/2]
            
            # 3点による曲率の近似
            curvature = self._calculate_angle_3d(
                [nose[0], nose[1], 0],
                [shoulder_center[0], shoulder_center[1], 0],
                [hip_center[0], hip_center[1], 0]
            )
            
            # 180度から引いて曲率として表現
            return 180 - curvature
        except Exception:
            return 0.0
    
    def _calculate_knee_toe_alignment(self, pose_data: List[List[float]]) -> float:
        """膝とつま先の方向性評価"""
        try:
            left_knee = pose_data[self.landmarks['LEFT_KNEE']]
            right_knee = pose_data[self.landmarks['RIGHT_KNEE']]
            left_ankle = pose_data[self.landmarks['LEFT_ANKLE']]
            right_ankle = pose_data[self.landmarks['RIGHT_ANKLE']]
            
            # 膝と足首の水平距離
            left_alignment = abs(left_knee[0] - left_ankle[0])
            right_alignment = abs(right_knee[0] - right_ankle[0])
            
            return (left_alignment + right_alignment) / 2
        except Exception:
            return 0.0
    
    def _calculate_shoulder_stability(self, pose_data: List[List[float]]) -> float:
        """肩の安定性評価"""
        try:
            left_shoulder = pose_data[self.landmarks['LEFT_SHOULDER']]
            right_shoulder = pose_data[self.landmarks['RIGHT_SHOULDER']]
            
            # 肩のラインの水平性
            shoulder_level_diff = abs(left_shoulder[1] - right_shoulder[1])
            
            return shoulder_level_diff
        except Exception:
            return 0.0
    
    def _calculate_wrist_alignment(self, pose_data: List[List[float]]) -> float:
        """手首のアライメント評価"""
        try:
            left_elbow = pose_data[self.landmarks['LEFT_ELBOW']]
            right_elbow = pose_data[self.landmarks['RIGHT_ELBOW']]
            left_wrist = pose_data[self.landmarks['LEFT_WRIST']]
            right_wrist = pose_data[self.landmarks['RIGHT_WRIST']]
            
            # 肘と手首の垂直アライメント
            left_alignment = abs(left_elbow[0] - left_wrist[0])
            right_alignment = abs(right_elbow[0] - right_wrist[0])
            
            return (left_alignment + right_alignment) / 2
        except Exception:
            return 0.0
    
    def _calculate_overall_symmetry(self, pose_data: List[List[float]]) -> float:
        """全体的な左右対称性評価"""
        try:
            symmetry_pairs = [
                ('LEFT_SHOULDER', 'RIGHT_SHOULDER'),
                ('LEFT_ELBOW', 'RIGHT_ELBOW'),
                ('LEFT_WRIST', 'RIGHT_WRIST'),
                ('LEFT_HIP', 'RIGHT_HIP'),
                ('LEFT_KNEE', 'RIGHT_KNEE'),
                ('LEFT_ANKLE', 'RIGHT_ANKLE')
            ]
            
            asymmetries = []
            for left_joint, right_joint in symmetry_pairs:
                left_pos = pose_data[self.landmarks[left_joint]]
                right_pos = pose_data[self.landmarks[right_joint]]
                
                # Y座標とZ座標の対称性を評価（X座標は反転）
                y_diff = abs(left_pos[1] - right_pos[1])
                z_diff = abs(left_pos[2] - right_pos[2])
                
                asymmetries.append(y_diff + z_diff)
            
            return np.mean(asymmetries)
        except Exception:
            return 0.0
    
    def _calculate_stability(self, pose_data: List[List[float]]) -> float:
        """安定性評価（重心バランス）"""
        try:
            # 主要関節の重心を計算
            key_joints = ['LEFT_SHOULDER', 'RIGHT_SHOULDER', 'LEFT_HIP', 'RIGHT_HIP']
            center_x = np.mean([pose_data[self.landmarks[joint]][0] for joint in key_joints])
            center_y = np.mean([pose_data[self.landmarks[joint]][1] for joint in key_joints])
            
            # 足の中心点
            left_ankle = pose_data[self.landmarks['LEFT_ANKLE']]
            right_ankle = pose_data[self.landmarks['RIGHT_ANKLE']]
            foot_center_x = (left_ankle[0] + right_ankle[0]) / 2
            
            # 重心と足の中心のずれ
            stability_offset = abs(center_x - foot_center_x)
            
            return stability_offset
        except Exception:
            return 0.0
    
    def _calculate_posture_quality(self, pose_data: List[List[float]]) -> float:
        """姿勢品質の総合評価"""
        try:
            # 頭部の位置
            nose = pose_data[self.landmarks['NOSE']]
            
            # 肩の中心
            left_shoulder = pose_data[self.landmarks['LEFT_SHOULDER']]
            right_shoulder = pose_data[self.landmarks['RIGHT_SHOULDER']]
            shoulder_center_x = (left_shoulder[0] + right_shoulder[0]) / 2
            
            # 頭部の前方突出
            head_forward = abs(nose[0] - shoulder_center_x)
            
            # 体幹の直立性
            torso_lean = abs(self._calculate_torso_lean(pose_data))
            
            # 総合的な姿勢スコア（小さいほど良い）
            posture_score = head_forward + torso_lean / 90.0  # 角度を正規化
            
            return posture_score
        except Exception:
            return 0.0


def main():
    """特徴量エンジニアリングのテスト"""
    engineer = AdvancedFeatureEngineer()
    
    # サンプルデータで機能テスト
    sample_pose = []
    for i in range(33):
        sample_pose.append([
            0.5 + 0.1 * np.random.randn(),
            0.3 + 0.4 * i / 33 + 0.05 * np.random.randn(),
            0.1 * np.random.randn(),
            0.8 + 0.2 * np.random.rand()
        ])
    
    sample_metadata = {
        'height': 170,
        'weight': 70,
        'experience': 'intermediate'
    }
    
    # フォーム品質特徴量のテスト
    form_features = engineer.extract_form_quality_features(sample_pose, 'squat', sample_metadata)
    print("フォーム品質特徴量:")
    for key, value in form_features.items():
        print(f"  {key}: {value:.4f}")
    
    # 時系列特徴量のテスト（複数フレーム）
    pose_sequence = [sample_pose for _ in range(10)]
    temporal_features = engineer.extract_temporal_features(pose_sequence, 'squat')
    print("\n時系列特徴量:")
    for key, value in temporal_features.items():
        print(f"  {key}: {value:.4f}")


if __name__ == "__main__":
    main()