"""
Step 3: 骨盤中心・肩幅=1の正規化

- 骨盤中心を原点（0,0,0）として座標を正規化
- 肩幅を基準にスケーリング
- XY平面で肩ラインをX軸に回転させて視点ロバスト性を確保
"""
import numpy as np
import json
import yaml
import time
import copy
import math
from typing import Dict, Any, List, Tuple

def load_config():
    """設定ファイルの読み込み"""
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)

def get_pelvis_center(landmarks: Dict[str, Dict[str, float]]) -> Tuple[float, float, float]:
    """
    骨盤の中心座標を計算
    
    Args:
        landmarks: フレームのランドマークデータ
    
    Returns:
        (x, y, z): 骨盤中心の座標
    """
    # 左右の腰のランドマークがあるか確認
    if 'LEFT_HIP' not in landmarks or 'RIGHT_HIP' not in landmarks:
        # デフォルト値を返す
        return (0.0, 0.0, 0.0)
    
    left_hip = landmarks['LEFT_HIP']
    right_hip = landmarks['RIGHT_HIP']
    
    # 中点を計算
    pelvis_x = (left_hip['x'] + right_hip['x']) / 2.0
    pelvis_y = (left_hip['y'] + right_hip['y']) / 2.0
    pelvis_z = (left_hip['z'] + right_hip['z']) / 2.0
    
    return (pelvis_x, pelvis_y, pelvis_z)

def get_shoulder_width(landmarks: Dict[str, Dict[str, float]]) -> float:
    """
    肩幅を計算
    
    Args:
        landmarks: フレームのランドマークデータ
    
    Returns:
        肩幅の値
    """
    # 左右の肩のランドマークがあるか確認
    if 'LEFT_SHOULDER' not in landmarks or 'RIGHT_SHOULDER' not in landmarks:
        # デフォルト値を返す
        return 1.0
    
    left_shoulder = landmarks['LEFT_SHOULDER']
    right_shoulder = landmarks['RIGHT_SHOULDER']
    
    # 3次元ユークリッド距離を計算
    dx = left_shoulder['x'] - right_shoulder['x']
    dy = left_shoulder['y'] - right_shoulder['y']
    dz = left_shoulder['z'] - right_shoulder['z']
    
    shoulder_width = math.sqrt(dx*dx + dy*dy + dz*dz)
    
    # ゼロ除算を防ぐ
    return max(shoulder_width, 0.001)

def get_shoulder_angle(landmarks: Dict[str, Dict[str, float]]) -> float:
    """
    肩のラインとX軸のなす角度を計算 (XY平面上)
    
    Args:
        landmarks: フレームのランドマークデータ
    
    Returns:
        角度（ラジアン）
    """
    # 左右の肩のランドマークがあるか確認
    if 'LEFT_SHOULDER' not in landmarks or 'RIGHT_SHOULDER' not in landmarks:
        # デフォルト値を返す（回転なし）
        return 0.0
    
    left_shoulder = landmarks['LEFT_SHOULDER']
    right_shoulder = landmarks['RIGHT_SHOULDER']
    
    # XY平面上での角度を計算
    dx = right_shoulder['x'] - left_shoulder['x']
    dy = right_shoulder['y'] - left_shoulder['y']
    
    # X軸との角度を計算
    return math.atan2(dy, dx)

def rotate_point_xy(x: float, y: float, angle: float) -> Tuple[float, float]:
    """
    XY平面上で点を回転
    
    Args:
        x, y: 回転させる点の座標
        angle: 回転角度（ラジアン）
    
    Returns:
        (new_x, new_y): 回転後の座標
    """
    cos_angle = math.cos(angle)
    sin_angle = math.sin(angle)
    
    new_x = x * cos_angle - y * sin_angle
    new_y = x * sin_angle + y * cos_angle
    
    return (new_x, new_y)

def normalize_landmarks(landmarks: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, float]]:
    """
    ランドマークを正規化
    
    Args:
        landmarks: フレームのランドマークデータ
    
    Returns:
        正規化されたランドマークデータ
    """
    # 骨盤中心を計算
    pelvis_x, pelvis_y, pelvis_z = get_pelvis_center(landmarks)
    
    # 肩幅を計算
    shoulder_width = get_shoulder_width(landmarks)
    
    # 肩の角度を計算
    shoulder_angle = get_shoulder_angle(landmarks)
    
    # 正規化されたランドマークを格納する辞書
    normalized_landmarks = {}
    
    # 各ランドマークを正規化
    for landmark_id, landmark_data in landmarks.items():
        # 座標を取得
        x = landmark_data.get('x', 0.0)
        y = landmark_data.get('y', 0.0)
        z = landmark_data.get('z', 0.0)
        
        # 骨盤中心を原点に平行移動
        x -= pelvis_x
        y -= pelvis_y
        z -= pelvis_z
        
        # XY平面で肩を水平に回転
        x, y = rotate_point_xy(x, y, -shoulder_angle)
        
        # 肩幅で正規化
        x /= shoulder_width
        y /= shoulder_width
        z /= shoulder_width
        
        # 正規化された座標を格納
        normalized_landmarks[landmark_id] = {
            'x': x,
            'y': y,
            'z': z
        }
        
        # visibilityが存在する場合は保持
        if 'visibility' in landmark_data:
            normalized_landmarks[landmark_id]['visibility'] = landmark_data['visibility']
    
    return normalized_landmarks

def apply(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    ステップ3: 正規化処理を適用
    
    Args:
        input_data: 入力フレームデータ (フレームID: ランドマークデータ)
    
    Returns:
        処理済みデータ
    """
    start_time = time.time()
    config = load_config()['normalize']
    
    # 入力データのディープコピーを作成
    output_data = copy.deepcopy(input_data)
    
    # メタデータが既に存在する場合は保持
    metadata = {}
    if '_metadata' in input_data:
        metadata = input_data['_metadata']
    
    # フレームIDを整数として取得し、順序付け
    frame_ids = sorted([int(k) for k in input_data.keys() if k != '_metadata'])
    
    if not frame_ids:
        print("警告: 有効なフレームが見つかりませんでした")
        return output_data
    
    # MediaPipeポーズランドマークの名前と対応するIDのマッピング
    # IDは各フレームデータのキーとして使用される
    landmark_name_to_id = {
        "NOSE": "NOSE",
        "LEFT_EYE_INNER": "LEFT_EYE_INNER",
        "LEFT_EYE": "LEFT_EYE",
        "LEFT_EYE_OUTER": "LEFT_EYE_OUTER",
        "RIGHT_EYE_INNER": "RIGHT_EYE_INNER",
        "RIGHT_EYE": "RIGHT_EYE",
        "RIGHT_EYE_OUTER": "RIGHT_EYE_OUTER",
        "LEFT_EAR": "LEFT_EAR",
        "RIGHT_EAR": "RIGHT_EAR",
        "MOUTH_LEFT": "MOUTH_LEFT",
        "MOUTH_RIGHT": "MOUTH_RIGHT",
        "LEFT_SHOULDER": "LEFT_SHOULDER",
        "RIGHT_SHOULDER": "RIGHT_SHOULDER",
        "LEFT_ELBOW": "LEFT_ELBOW",
        "RIGHT_ELBOW": "RIGHT_ELBOW",
        "LEFT_WRIST": "LEFT_WRIST",
        "RIGHT_WRIST": "RIGHT_WRIST",
        "LEFT_PINKY": "LEFT_PINKY",
        "RIGHT_PINKY": "RIGHT_PINKY",
        "LEFT_INDEX": "LEFT_INDEX",
        "RIGHT_INDEX": "RIGHT_INDEX",
        "LEFT_THUMB": "LEFT_THUMB",
        "RIGHT_THUMB": "RIGHT_THUMB",
        "LEFT_HIP": "LEFT_HIP",
        "RIGHT_HIP": "RIGHT_HIP",
        "LEFT_KNEE": "LEFT_KNEE",
        "RIGHT_KNEE": "RIGHT_KNEE",
        "LEFT_ANKLE": "LEFT_ANKLE",
        "RIGHT_ANKLE": "RIGHT_ANKLE",
        "LEFT_HEEL": "LEFT_HEEL",
        "RIGHT_HEEL": "RIGHT_HEEL",
        "LEFT_FOOT_INDEX": "LEFT_FOOT_INDEX",
        "RIGHT_FOOT_INDEX": "RIGHT_FOOT_INDEX",
    }
    
    # 各フレームに対して処理
    for frame_id in frame_ids:
        str_frame_id = str(frame_id)
        
        if str_frame_id in input_data and 'landmarks' in input_data[str_frame_id]:
            frame_landmarks = input_data[str_frame_id]['landmarks']
            
            # ランドマークの名前と値のマッピングを作成
            named_landmarks = {}
            for landmark_name, landmark_id in landmark_name_to_id.items():
                if landmark_id in frame_landmarks:
                    named_landmarks[landmark_name] = frame_landmarks[landmark_id]
            
            # 正規化を適用
            if named_landmarks:
                normalized_landmarks = normalize_landmarks(named_landmarks)
                
                # 正規化されたランドマークを出力データに格納
                for landmark_name, landmark_id in landmark_name_to_id.items():
                    if landmark_name in normalized_landmarks and landmark_id in frame_landmarks:
                        output_data[str_frame_id]['landmarks'][landmark_id] = normalized_landmarks[landmark_name]
    
    # 処理時間を記録
    elapsed_time = time.time() - start_time
    metadata['step03_time'] = elapsed_time
    metadata['step03_applied'] = True
    output_data['_metadata'] = metadata
    
    return output_data

def main():
    """単体実行用のエントリーポイント"""
    # サンプル入力データ（ステップ2の出力またはそれ以前の出力）
    try:
        # まずステップ2の出力を試す
        sample_input = 'step02_output.json'
        with open(sample_input, 'r') as f:
            input_data = json.load(f)
    except FileNotFoundError:
        try:
            # ステップ2の出力がなければステップ1の出力を試す
            sample_input = 'step01_output.json'
            with open(sample_input, 'r') as f:
                input_data = json.load(f)
        except FileNotFoundError:
            try:
                # それもなければ生データを試す
                sample_input = 'raw_landmarks_by_frame.json'
                with open(sample_input, 'r') as f:
                    input_data = json.load(f)
            except FileNotFoundError:
                print("エラー: 入力ファイルが見つかりません。")
                return
    
    # 正規化ステップを適用
    output_data = apply(input_data)
    
    # 結果を保存
    output_file = 'step03_output.json'
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"ステップ3完了: 結果を {output_file} に保存しました")
    if '_metadata' in output_data:
        print(f"処理時間: {output_data['_metadata']['step03_time']:.3f} 秒")

if __name__ == '__main__':
    main()