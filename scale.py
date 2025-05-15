"""
ピクセル座標からcm単位の実寸法への変換ロジックを提供するモジュール
"""
import mediapipe as mp
import numpy as np
from typing import Tuple, Dict, Any, List, Optional

# MediaPipe Poseのランドマーク列挙型
try:
    mp_pose = mp.solutions.pose
    PoseLandmark = mp_pose.PoseLandmark
except AttributeError:
    # MediaPipeのバージョンによって構造が異なる場合の対応
    import mediapipe.python as mp_python
    mp_pose = mp_python.solutions.pose
    PoseLandmark = mp_pose.PoseLandmark

class ScaleCalculator:
    """
    ピクセル→cm変換のスケール計算機
    """
    def __init__(self, user_height_cm: float):
        """
        Args:
            user_height_cm (float): ユーザーの身長（cm）
        """
        self.user_height_cm = user_height_cm
        self.scale_px_per_cm = None  # 1cmあたりのピクセル数
    
    def calculate_scale(self, landmarks: Dict[int, Dict[str, float]], frame_height: int) -> Optional[float]:
        """
        ランドマークから1cmあたりのピクセル数を計算

        Args:
            landmarks (Dict[int, Dict[str, float]]): MediaPipeのランドマーク
            frame_height (int): フレームの高さ（ピクセル）

        Returns:
            Optional[float]: 1cmあたりのピクセル数。計算できない場合はNone
        """
        # 鼻の位置を取得 (頭頂部の代わりに使用)
        nose = landmarks.get(PoseLandmark.NOSE)
        
        # 左右の足首の位置を取得して平均をとる
        left_ankle = landmarks.get(PoseLandmark.LEFT_ANKLE)
        right_ankle = landmarks.get(PoseLandmark.RIGHT_ANKLE)
        
        # 足首のY座標の平均を計算
        ankle_y = (left_ankle['y'] + right_ankle['y']) / 2 if left_ankle and right_ankle else None
        
        if nose and ankle_y is not None:
            # 頭から足首までのピクセル距離を計算
            # 注意: MediaPipeの座標は0-1の正規化された値なので、実際のピクセル値に変換
            pixel_height = abs(nose['y'] - ankle_y) * frame_height
            
            # 1cmあたりのピクセル数を計算
            self.scale_px_per_cm = pixel_height / self.user_height_cm
            return self.scale_px_per_cm
        
        return None
    
    def convert_to_cm(self, pixels: float) -> float:
        """
        ピクセル距離をcm単位に変換

        Args:
            pixels (float): ピクセル距離

        Returns:
            float: cm単位の距離
        """
        if self.scale_px_per_cm and self.scale_px_per_cm > 0:
            return pixels / self.scale_px_per_cm
        
        raise ValueError("スケールが計算されていません。calculate_scale()を先に呼び出してください。")
    
    def distance_px(self, p1: Dict[str, float], p2: Dict[str, float], frame_dim: Tuple[int, int]) -> float:
        """
        2点間のピクセル距離を計算

        Args:
            p1 (Dict[str, float]): 1つ目の点の座標 (x, y, z)
            p2 (Dict[str, float]): 2つ目の点の座標 (x, y, z)
            frame_dim (Tuple[int, int]): フレームの寸法（幅, 高さ）

        Returns:
            float: 2点間のピクセル距離
        """
        frame_width, frame_height = frame_dim
        
        # 正規化された座標からピクセル座標に変換
        p1_px = np.array([p1['x'] * frame_width, p1['y'] * frame_height, p1.get('z', 0)])
        p2_px = np.array([p2['x'] * frame_width, p2['y'] * frame_height, p2.get('z', 0)])
        
        # ユークリッド距離を計算
        return float(np.linalg.norm(p1_px - p2_px))
    
    def convert_landmarks_to_cm(self, landmarks: Dict[int, Dict[str, float]], 
                               frame_dim: Tuple[int, int]) -> Dict[str, Dict[str, float]]:
        """
        全てのランドマークをcm単位の3D座標に変換

        Args:
            landmarks (Dict[int, Dict[str, float]]): MediaPipeのランドマーク
            frame_dim (Tuple[int, int]): フレームの寸法（幅, 高さ）

        Returns:
            Dict[str, Dict[str, float]]: cm単位のランドマーク位置
        """
        if not self.scale_px_per_cm:
            raise ValueError("スケールが計算されていません。calculate_scale()を先に呼び出してください。")
        
        frame_width, frame_height = frame_dim
        center_x, center_y = frame_width / 2, frame_height / 2
        
        # cm単位の座標を格納する辞書
        joints_cm = {}
        
        for landmark_id, landmark in landmarks.items():
            # ランドマークの名前を取得
            landmark_name = self._get_landmark_name(landmark_id)
            
            # 中央を原点とした座標系に変換
            x_px = (landmark['x'] * frame_width - center_x)
            y_px = (center_y - landmark['y'] * frame_height)  # Y軸は上が正
            z_px = landmark.get('z', 0) * frame_width  # Z値はX値と同様のスケール
            
            # ピクセルからcmに変換
            x_cm = self.convert_to_cm(x_px)
            y_cm = self.convert_to_cm(y_px)
            z_cm = self.convert_to_cm(z_px)
            
            joints_cm[landmark_name] = {
                'x': round(x_cm, 1),
                'y': round(y_cm, 1),
                'z': round(z_cm, 1)
            }
        
        return joints_cm
    
    def _get_landmark_name(self, landmark_id: int) -> str:
        """
        ランドマークIDから名前を取得

        Args:
            landmark_id (int): ランドマークのID

        Returns:
            str: ランドマークの名前
        """
        for name, value in vars(PoseLandmark).items():
            if not name.startswith('_') and value == landmark_id:
                return name
        return f"UNKNOWN_{landmark_id}"