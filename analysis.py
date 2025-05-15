"""
腕長・脚長・関節位置を計算し、JSON出力を行うモジュール
"""
import os
import json
import mediapipe as mp
import numpy as np
from typing import Dict, Tuple, List, Any, Optional

from scale import ScaleCalculator

# MediaPipe Poseのランドマーク列挙型
try:
    mp_pose = mp.solutions.pose
    PoseLandmark = mp_pose.PoseLandmark
except AttributeError:
    # MediaPipeのバージョンによって構造が異なる場合の対応
    import mediapipe.python as mp_python
    mp_pose = mp_python.solutions.pose
    PoseLandmark = mp_pose.PoseLandmark

class BodyAnalyzer:
    """
    身体の各部位の長さや関節位置を分析するクラス
    """
    def __init__(self, user_height_cm: float):
        """
        Args:
            user_height_cm (float): ユーザーの身長（cm）
        """
        self.user_height_cm = user_height_cm
        self.scale_calculator = ScaleCalculator(user_height_cm)
        self.results_dir = 'results'
        os.makedirs(self.results_dir, exist_ok=True)
    
    def analyze_landmarks(self, landmarks: Dict[int, Dict[str, float]], 
                         frame_dim: Tuple[int, int]) -> Dict[str, Any]:
        """
        ランドマークから身体の寸法を分析する

        Args:
            landmarks (Dict[int, Dict[str, float]]): MediaPipeのランドマーク
            frame_dim (Tuple[int, int]): フレームの寸法（幅, 高さ）

        Returns:
            Dict[str, Any]: 分析結果
        """
        # スケールを計算
        frame_width, frame_height = frame_dim
        self.scale_calculator.calculate_scale(landmarks, frame_height)
        
        # 腕の長さを計算
        left_arm_cm = self._calculate_arm_length('LEFT', landmarks, frame_dim)
        right_arm_cm = self._calculate_arm_length('RIGHT', landmarks, frame_dim)
        
        # 脚の長さを計算
        left_leg_cm = self._calculate_leg_length('LEFT', landmarks, frame_dim)
        right_leg_cm = self._calculate_leg_length('RIGHT', landmarks, frame_dim)
        
        # 関節の3D位置をcm単位で計算
        joints_cm = self.scale_calculator.convert_landmarks_to_cm(landmarks, frame_dim)
        
        # 結果を辞書にまとめる
        results = {
            'user_height_cm': self.user_height_cm,
            'left_arm_cm': round(left_arm_cm, 1) if left_arm_cm else None,
            'right_arm_cm': round(right_arm_cm, 1) if right_arm_cm else None,
            'left_leg_cm': round(left_leg_cm, 1) if left_leg_cm else None,
            'right_leg_cm': round(right_leg_cm, 1) if right_leg_cm else None,
            'joints_cm': joints_cm
        }
        
        return results
    
    def _calculate_arm_length(self, side: str, landmarks: Dict[int, Dict[str, float]], 
                            frame_dim: Tuple[int, int]) -> Optional[float]:
        """
        片腕の長さを計算する

        Args:
            side (str): 'LEFT'または'RIGHT'
            landmarks (Dict[int, Dict[str, float]]): MediaPipeのランドマーク
            frame_dim (Tuple[int, int]): フレームの寸法（幅, 高さ）

        Returns:
            Optional[float]: 腕の長さ（cm）。失敗した場合はNone
        """
        # ランドマークIDを取得
        shoulder_id = getattr(PoseLandmark, f'{side}_SHOULDER')
        elbow_id = getattr(PoseLandmark, f'{side}_ELBOW')
        wrist_id = getattr(PoseLandmark, f'{side}_WRIST')
        
        # 各関節のランドマーク
        shoulder = landmarks.get(shoulder_id)
        elbow = landmarks.get(elbow_id)
        wrist = landmarks.get(wrist_id)
        
        if shoulder and elbow and wrist:
            # 信頼度のチェック（必要に応じて）
            if (shoulder.get('visibility', 1) < 0.5 or 
                elbow.get('visibility', 1) < 0.5 or 
                wrist.get('visibility', 1) < 0.5):
                return None
            
            # 肩から肘までの距離（ピクセル）
            shoulder_to_elbow_px = self.scale_calculator.distance_px(shoulder, elbow, frame_dim)
            
            # 肘から手首までの距離（ピクセル）
            elbow_to_wrist_px = self.scale_calculator.distance_px(elbow, wrist, frame_dim)
            
            # ピクセルからcmに変換して合計
            return (self.scale_calculator.convert_to_cm(shoulder_to_elbow_px) + 
                    self.scale_calculator.convert_to_cm(elbow_to_wrist_px))
        
        return None
    
    def _calculate_leg_length(self, side: str, landmarks: Dict[int, Dict[str, float]], 
                            frame_dim: Tuple[int, int]) -> Optional[float]:
        """
        片脚の長さを計算する

        Args:
            side (str): 'LEFT'または'RIGHT'
            landmarks (Dict[int, Dict[str, float]]): MediaPipeのランドマーク
            frame_dim (Tuple[int, int]): フレームの寸法（幅, 高さ）

        Returns:
            Optional[float]: 脚の長さ（cm）。失敗した場合はNone
        """
        # ランドマークIDを取得
        hip_id = getattr(PoseLandmark, f'{side}_HIP')
        knee_id = getattr(PoseLandmark, f'{side}_KNEE')
        ankle_id = getattr(PoseLandmark, f'{side}_ANKLE')
        
        # 各関節のランドマーク
        hip = landmarks.get(hip_id)
        knee = landmarks.get(knee_id)
        ankle = landmarks.get(ankle_id)
        
        if hip and knee and ankle:
            # 信頼度のチェック（必要に応じて）
            if (hip.get('visibility', 1) < 0.5 or 
                knee.get('visibility', 1) < 0.5 or 
                ankle.get('visibility', 1) < 0.5):
                return None
            
            # 股関節から膝までの距離（ピクセル）
            hip_to_knee_px = self.scale_calculator.distance_px(hip, knee, frame_dim)
            
            # 膝から足首までの距離（ピクセル）
            knee_to_ankle_px = self.scale_calculator.distance_px(knee, ankle, frame_dim)
            
            # ピクセルからcmに変換して合計
            return (self.scale_calculator.convert_to_cm(hip_to_knee_px) + 
                    self.scale_calculator.convert_to_cm(knee_to_ankle_px))
        
        return None
    
    def save_results(self, results: Dict[str, Any], filename: str = 'body_metrics.json') -> str:
        """
        分析結果をJSONファイルに保存する

        Args:
            results (Dict[str, Any]): 分析結果
            filename (str, optional): 保存するファイル名. Defaults to 'body_metrics.json'.

        Returns:
            str: 保存したファイルの絶対パス
        """
        filepath = os.path.join(self.results_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        print(f"分析結果をファイルに保存しました: {filepath}")
        return filepath
    
    def print_summary(self, results: Dict[str, Any]) -> None:
        """
        分析結果の要約をコンソールに表示する

        Args:
            results (Dict[str, Any]): 分析結果
        """
        print("\n==== 身体測定結果の要約 ====")
        print(f"身長: {results['user_height_cm']} cm")
        if results['left_arm_cm']:
            print(f"左腕の長さ: {results['left_arm_cm']} cm")
        if results['right_arm_cm']:
            print(f"右腕の長さ: {results['right_arm_cm']} cm")
        if results['left_leg_cm']:
            print(f"左脚の長さ: {results['left_leg_cm']} cm")
        if results['right_leg_cm']:
            print(f"右脚の長さ: {results['right_leg_cm']} cm")
        print("============================")