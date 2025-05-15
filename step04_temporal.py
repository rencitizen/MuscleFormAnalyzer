"""
Step 4: 時系列特徴量の計算

- 主要関節角度（股関節・膝・肘など）の計算
- 角度の一次微分（Δangle）と二次微分（Δ²angle）を計算
- 時系列特徴量をJSONに追記
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

def calculate_angle(p1: Dict[str, float], p2: Dict[str, float], p3: Dict[str, float]) -> float:
    """
    3点間の角度を計算（p2が頂点）
    
    Args:
        p1, p2, p3: 3点の座標
    
    Returns:
        角度（度）
    """
    # ベクトル計算
    v1 = (p1['x'] - p2['x'], p1['y'] - p2['y'], p1['z'] - p2['z'])
    v2 = (p3['x'] - p2['x'], p3['y'] - p2['y'], p3['z'] - p2['z'])
    
    # ベクトルの長さ
    len_v1 = math.sqrt(v1[0]**2 + v1[1]**2 + v1[2]**2)
    len_v2 = math.sqrt(v2[0]**2 + v2[1]**2 + v2[2]**2)
    
    # ゼロ除算を防ぐ
    if len_v1 < 0.0001 or len_v2 < 0.0001:
        return 0.0
    
    # 内積計算
    dot_product = v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]
    
    # コサイン値（角度）
    cos_angle = dot_product / (len_v1 * len_v2)
    
    # 数値誤差を防ぐ
    cos_angle = max(-1.0, min(1.0, cos_angle))
    
    # ラジアンから度に変換
    angle_deg = math.degrees(math.acos(cos_angle))
    
    return angle_deg

def calculate_joint_angles(landmarks: Dict[str, Dict[str, float]]) -> Dict[str, float]:
    """
    主要関節の角度を計算
    
    Args:
        landmarks: フレームのランドマークデータ
    
    Returns:
        関節角度の辞書
    """
    angles = {}
    
    # 左肘の角度（肩-肘-手首）
    if all(key in landmarks for key in ['LEFT_SHOULDER', 'LEFT_ELBOW', 'LEFT_WRIST']):
        angles['left_elbow'] = calculate_angle(
            landmarks['LEFT_SHOULDER'],
            landmarks['LEFT_ELBOW'],
            landmarks['LEFT_WRIST']
        )
    
    # 右肘の角度（肩-肘-手首）
    if all(key in landmarks for key in ['RIGHT_SHOULDER', 'RIGHT_ELBOW', 'RIGHT_WRIST']):
        angles['right_elbow'] = calculate_angle(
            landmarks['RIGHT_SHOULDER'],
            landmarks['RIGHT_ELBOW'],
            landmarks['RIGHT_WRIST']
        )
    
    # 左肩の角度（肘-肩-腰）
    if all(key in landmarks for key in ['LEFT_ELBOW', 'LEFT_SHOULDER', 'LEFT_HIP']):
        angles['left_shoulder'] = calculate_angle(
            landmarks['LEFT_ELBOW'],
            landmarks['LEFT_SHOULDER'],
            landmarks['LEFT_HIP']
        )
    
    # 右肩の角度（肘-肩-腰）
    if all(key in landmarks for key in ['RIGHT_ELBOW', 'RIGHT_SHOULDER', 'RIGHT_HIP']):
        angles['right_shoulder'] = calculate_angle(
            landmarks['RIGHT_ELBOW'],
            landmarks['RIGHT_SHOULDER'],
            landmarks['RIGHT_HIP']
        )
    
    # 左股関節の角度（肩-腰-膝）
    if all(key in landmarks for key in ['LEFT_SHOULDER', 'LEFT_HIP', 'LEFT_KNEE']):
        angles['left_hip'] = calculate_angle(
            landmarks['LEFT_SHOULDER'],
            landmarks['LEFT_HIP'],
            landmarks['LEFT_KNEE']
        )
    
    # 右股関節の角度（肩-腰-膝）
    if all(key in landmarks for key in ['RIGHT_SHOULDER', 'RIGHT_HIP', 'RIGHT_KNEE']):
        angles['right_hip'] = calculate_angle(
            landmarks['RIGHT_SHOULDER'],
            landmarks['RIGHT_HIP'],
            landmarks['RIGHT_KNEE']
        )
    
    # 左膝の角度（腰-膝-足首）
    if all(key in landmarks for key in ['LEFT_HIP', 'LEFT_KNEE', 'LEFT_ANKLE']):
        angles['left_knee'] = calculate_angle(
            landmarks['LEFT_HIP'],
            landmarks['LEFT_KNEE'],
            landmarks['LEFT_ANKLE']
        )
    
    # 右膝の角度（腰-膝-足首）
    if all(key in landmarks for key in ['RIGHT_HIP', 'RIGHT_KNEE', 'RIGHT_ANKLE']):
        angles['right_knee'] = calculate_angle(
            landmarks['RIGHT_HIP'],
            landmarks['RIGHT_KNEE'],
            landmarks['RIGHT_ANKLE']
        )
    
    # 体幹の角度（肩-腰の傾き）
    if all(key in landmarks for key in ['LEFT_SHOULDER', 'RIGHT_SHOULDER', 'LEFT_HIP', 'RIGHT_HIP']):
        # 肩の中点
        shoulder_mid = {
            'x': (landmarks['LEFT_SHOULDER']['x'] + landmarks['RIGHT_SHOULDER']['x']) / 2,
            'y': (landmarks['LEFT_SHOULDER']['y'] + landmarks['RIGHT_SHOULDER']['y']) / 2,
            'z': (landmarks['LEFT_SHOULDER']['z'] + landmarks['RIGHT_SHOULDER']['z']) / 2
        }
        
        # 腰の中点
        hip_mid = {
            'x': (landmarks['LEFT_HIP']['x'] + landmarks['RIGHT_HIP']['x']) / 2,
            'y': (landmarks['LEFT_HIP']['y'] + landmarks['RIGHT_HIP']['y']) / 2,
            'z': (landmarks['LEFT_HIP']['z'] + landmarks['RIGHT_HIP']['z']) / 2
        }
        
        # 体幹のZ軸（奥行き）に対する角度
        # 垂直方向の参照点
        vertical_ref = {
            'x': hip_mid['x'],
            'y': hip_mid['y'] - 1.0,  # Y軸下方向に1単位
            'z': hip_mid['z']
        }
        
        angles['torso'] = calculate_angle(
            shoulder_mid,
            hip_mid,
            vertical_ref
        )
    
    return angles

def calculate_derivatives(angle_series: List[float], window_size: int) -> Tuple[List[float], List[float]]:
    """
    角度系列の一次微分と二次微分を計算
    
    Args:
        angle_series: 角度の時系列データ
        window_size: 差分計算の窓サイズ
    
    Returns:
        (delta_angles, delta2_angles): 一次微分と二次微分のリスト
    """
    n = len(angle_series)
    delta_angles = [0.0] * n
    delta2_angles = [0.0] * n
    
    # 一次微分 (中心差分法)
    half_window = window_size // 2
    for i in range(n):
        if i < half_window:
            # 前方差分
            if i + 1 < n:
                delta_angles[i] = angle_series[i+1] - angle_series[i]
        elif i >= n - half_window:
            # 後方差分
            if i > 0:
                delta_angles[i] = angle_series[i] - angle_series[i-1]
        else:
            # 中心差分
            delta_angles[i] = (angle_series[i+half_window] - angle_series[i-half_window]) / window_size
    
    # 二次微分 (デルタ角度の一次微分)
    for i in range(n):
        if i < half_window:
            # 前方差分
            if i + 1 < n:
                delta2_angles[i] = delta_angles[i+1] - delta_angles[i]
        elif i >= n - half_window:
            # 後方差分
            if i > 0:
                delta2_angles[i] = delta_angles[i] - delta_angles[i-1]
        else:
            # 中心差分
            delta2_angles[i] = (delta_angles[i+half_window] - delta_angles[i-half_window]) / window_size
    
    return delta_angles, delta2_angles

def apply(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    ステップ4: 時系列特徴量計算処理を適用
    
    Args:
        input_data: 入力フレームデータ (フレームID: ランドマークデータ)
    
    Returns:
        処理済みデータ
    """
    start_time = time.time()
    config = load_config()['temporal']
    
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
    
    # 各関節角度の時系列データを収集
    angle_series = {
        'left_elbow': [],
        'right_elbow': [],
        'left_shoulder': [],
        'right_shoulder': [],
        'left_hip': [],
        'right_hip': [],
        'left_knee': [],
        'right_knee': [],
        'torso': []
    }
    
    # 各フレームの関節角度を計算・収集
    for frame_id in frame_ids:
        str_frame_id = str(frame_id)
        
        if str_frame_id in input_data and 'landmarks' in input_data[str_frame_id]:
            frame_landmarks = input_data[str_frame_id]['landmarks']
            
            # ランドマークの名前と値のマッピングを作成
            named_landmarks = {}
            for landmark_name, landmark_id in landmark_name_to_id.items():
                if landmark_id in frame_landmarks:
                    named_landmarks[landmark_name] = frame_landmarks[landmark_id]
            
            # 関節角度を計算
            if named_landmarks:
                joint_angles = calculate_joint_angles(named_landmarks)
                
                # 各関節角度を時系列データに追加
                for angle_name in angle_series.keys():
                    angle_series[angle_name].append(joint_angles.get(angle_name, 0.0))
                
                # 出力データに関節角度を追加
                if 'joint_angles' not in output_data[str_frame_id]:
                    output_data[str_frame_id]['joint_angles'] = {}
                
                output_data[str_frame_id]['joint_angles'] = joint_angles
    
    # 一次微分と二次微分の計算
    delta_window = config['delta_window']
    delta2_window = config['delta2_window']
    
    for angle_name, angles in angle_series.items():
        delta_angles, delta2_angles = calculate_derivatives(angles, delta_window)
        
        # 微分値を各フレームに追加
        for i, frame_id in enumerate(frame_ids):
            str_frame_id = str(frame_id)
            
            if str_frame_id in output_data and 'joint_angles' in output_data[str_frame_id]:
                # 一次微分
                if 'delta_angles' not in output_data[str_frame_id]:
                    output_data[str_frame_id]['delta_angles'] = {}
                
                output_data[str_frame_id]['delta_angles'][angle_name] = delta_angles[i]
                
                # 二次微分
                if 'delta2_angles' not in output_data[str_frame_id]:
                    output_data[str_frame_id]['delta2_angles'] = {}
                
                output_data[str_frame_id]['delta2_angles'][angle_name] = delta2_angles[i]
    
    # 処理時間を記録
    elapsed_time = time.time() - start_time
    metadata['step04_time'] = elapsed_time
    metadata['step04_applied'] = True
    output_data['_metadata'] = metadata
    
    return output_data

def main():
    """単体実行用のエントリーポイント"""
    # サンプル入力データ（ステップ3の出力またはそれ以前の出力）
    try:
        # まずステップ3の出力を試す
        sample_input = 'step03_output.json'
        with open(sample_input, 'r') as f:
            input_data = json.load(f)
    except FileNotFoundError:
        try:
            # ステップ3の出力がなければステップ2の出力を試す
            sample_input = 'step02_output.json'
            with open(sample_input, 'r') as f:
                input_data = json.load(f)
        except FileNotFoundError:
            try:
                # それもなければステップ1の出力を試す
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
    
    # 時系列特徴量計算ステップを適用
    output_data = apply(input_data)
    
    # 結果を保存
    output_file = 'step04_output.json'
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"ステップ4完了: 結果を {output_file} に保存しました")
    if '_metadata' in output_data:
        print(f"処理時間: {output_data['_metadata']['step04_time']:.3f} 秒")

if __name__ == '__main__':
    main()