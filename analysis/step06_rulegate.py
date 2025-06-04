"""
Step 6: ルールベース優先判定ゲート

- 特定の条件に基づくルールベース判定を定義
- 機械学習と判定が食い違う場合、ルールを優先
- 例: 「手が床より下＆体幹水平→Push-up」など
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

def is_hands_below_floor(landmarks: Dict[str, Dict[str, float]]) -> bool:
    """
    手が床より下にあるかチェック
    
    Args:
        landmarks: フレームのランドマークデータ
    
    Returns:
        Trueなら手が床より下
    """
    if 'LEFT_WRIST' not in landmarks or 'RIGHT_WRIST' not in landmarks or 'LEFT_ANKLE' not in landmarks or 'RIGHT_ANKLE' not in landmarks:
        return False
    
    # 両手首が両足首より下にあるか
    left_wrist_y = landmarks['LEFT_WRIST']['y']
    right_wrist_y = landmarks['RIGHT_WRIST']['y']
    left_ankle_y = landmarks['LEFT_ANKLE']['y']
    right_ankle_y = landmarks['RIGHT_ANKLE']['y']
    
    # 足首のY座標の平均（床レベル）
    floor_y = (left_ankle_y + right_ankle_y) / 2
    
    # 両手首がこの床レベルよりも大きいY座標を持つなら「下」に位置する
    # （画像座標系ではY軸は下向きが正）
    return left_wrist_y > floor_y and right_wrist_y > floor_y

def is_torso_horizontal(landmarks: Dict[str, Dict[str, float]], threshold_deg: float) -> bool:
    """
    体幹が水平に近いかチェック
    
    Args:
        landmarks: フレームのランドマークデータ
        threshold_deg: 水平とみなす閾値（度）
    
    Returns:
        Trueなら体幹が水平に近い
    """
    if 'LEFT_SHOULDER' not in landmarks or 'RIGHT_SHOULDER' not in landmarks or 'LEFT_HIP' not in landmarks or 'RIGHT_HIP' not in landmarks:
        return False
    
    # 肩の中点
    shoulder_mid_x = (landmarks['LEFT_SHOULDER']['x'] + landmarks['RIGHT_SHOULDER']['x']) / 2
    shoulder_mid_y = (landmarks['LEFT_SHOULDER']['y'] + landmarks['RIGHT_SHOULDER']['y']) / 2
    
    # 腰の中点
    hip_mid_x = (landmarks['LEFT_HIP']['x'] + landmarks['RIGHT_HIP']['x']) / 2
    hip_mid_y = (landmarks['LEFT_HIP']['y'] + landmarks['RIGHT_HIP']['y']) / 2
    
    # 体幹の傾きを計算
    dx = shoulder_mid_x - hip_mid_x
    dy = shoulder_mid_y - hip_mid_y
    
    # 水平線とのなす角度（度）
    angle_deg = abs(math.degrees(math.atan2(dy, dx)))
    
    # 角度が閾値以下なら水平に近い
    return angle_deg <= threshold_deg

def is_hip_flexion_above_threshold(landmarks: Dict[str, Dict[str, float]], joint_angles: Dict[str, float], threshold_deg: float) -> bool:
    """
    股関節の屈曲角度が閾値以上かチェック
    
    Args:
        landmarks: フレームのランドマークデータ
        joint_angles: 関節角度データ
        threshold_deg: 閾値（度）
    
    Returns:
        Trueなら股関節屈曲角度が閾値以上
    """
    # すでに計算された関節角度がある場合はそれを使う
    if 'left_hip' in joint_angles and 'right_hip' in joint_angles:
        left_hip_angle = joint_angles['left_hip']
        right_hip_angle = joint_angles['right_hip']
        
        # 左右の平均値
        avg_hip_angle = (left_hip_angle + right_hip_angle) / 2
        
        # 180度から引いて屈曲角度に変換（直立=0度）
        hip_flexion = 180 - avg_hip_angle
        
        return hip_flexion >= threshold_deg
    
    return False

def is_legs_extended(landmarks: Dict[str, Dict[str, float]], joint_angles: Dict[str, float]) -> bool:
    """
    脚が伸展しているかチェック
    
    Args:
        landmarks: フレームのランドマークデータ
        joint_angles: 関節角度データ
    
    Returns:
        Trueなら脚が伸展している
    """
    # すでに計算された関節角度がある場合はそれを使う
    if 'left_knee' in joint_angles and 'right_knee' in joint_angles:
        left_knee_angle = joint_angles['left_knee']
        right_knee_angle = joint_angles['right_knee']
        
        # 膝が伸びているとき、角度は160度以上
        return left_knee_angle >= 160 and right_knee_angle >= 160
    
    return False

def is_torso_forward_tilt(landmarks: Dict[str, Dict[str, float]], joint_angles: Dict[str, float], threshold_deg: float) -> bool:
    """
    体幹が前傾しているかチェック
    
    Args:
        landmarks: フレームのランドマークデータ
        joint_angles: 関節角度データ
        threshold_deg: 前傾とみなす閾値（度）
    
    Returns:
        Trueなら体幹が前傾している
    """
    # すでに計算された体幹角度がある場合はそれを使う
    if 'torso' in joint_angles:
        torso_angle = joint_angles['torso']
        
        # 90度が直立、それより小さいと前傾
        return torso_angle <= 90 - threshold_deg
    
    return False

def is_hands_above_head(landmarks: Dict[str, Dict[str, float]]) -> bool:
    """
    手が頭より上にあるかチェック
    
    Args:
        landmarks: フレームのランドマークデータ
    
    Returns:
        Trueなら手が頭より上
    """
    if 'LEFT_WRIST' not in landmarks or 'RIGHT_WRIST' not in landmarks or 'NOSE' not in landmarks:
        return False
    
    # 両手首が鼻より上にあるか（画像座標系ではY軸は下向きが正なので、小さいY値が「上」）
    left_wrist_y = landmarks['LEFT_WRIST']['y']
    right_wrist_y = landmarks['RIGHT_WRIST']['y']
    nose_y = landmarks['NOSE']['y']
    
    return left_wrist_y < nose_y and right_wrist_y < nose_y

def is_elbow_extension(landmarks: Dict[str, Dict[str, float]], joint_angles: Dict[str, float], threshold_deg: float) -> bool:
    """
    肘が伸展しているかチェック
    
    Args:
        landmarks: フレームのランドマークデータ
        joint_angles: 関節角度データ
        threshold_deg: 伸展とみなす閾値（度）
    
    Returns:
        Trueなら肘が伸展している
    """
    # すでに計算された関節角度がある場合はそれを使う
    if 'left_elbow' in joint_angles and 'right_elbow' in joint_angles:
        left_elbow_angle = joint_angles['left_elbow']
        right_elbow_angle = joint_angles['right_elbow']
        
        # 肘が伸びているとき、角度は閾値以上
        return left_elbow_angle >= threshold_deg and right_elbow_angle >= threshold_deg
    
    return False

def apply_rule_based_classification(frame_data: Dict[str, Any], config_rules: Dict[str, Any]) -> str:
    """
    ルールベースの分類を適用
    
    Args:
        frame_data: フレームデータ
        config_rules: ルール設定
    
    Returns:
        ルールベースで判定したラベル、または空文字列（ルール該当なし）
    """
    # ランドマークデータを取得
    if 'landmarks' not in frame_data:
        return ""
    
    landmarks = frame_data['landmarks']
    
    # 関節角度データを取得
    joint_angles = frame_data.get('joint_angles', {})
    
    # ルールベース判定
    # プッシュアップのルール
    if 'pushup' in config_rules:
        pushup_rules = config_rules['pushup']
        torso_angle_threshold = pushup_rules.get('torso_angle_threshold', 30)
        
        if (pushup_rules.get('hands_below_floor', False) and is_hands_below_floor(landmarks) and 
            pushup_rules.get('torso_horizontal', False) and is_torso_horizontal(landmarks, torso_angle_threshold)):
            return 'pushup'
    
    # スクワットのルール
    if 'squat' in config_rules:
        squat_rules = config_rules['squat']
        hip_flexion_threshold = squat_rules.get('hip_flexion_threshold', 90)
        
        if is_hip_flexion_above_threshold(landmarks, joint_angles, hip_flexion_threshold):
            return 'squat'
    
    # デッドリフトのルール
    if 'deadlift' in config_rules:
        deadlift_rules = config_rules['deadlift']
        torso_angle_threshold = deadlift_rules.get('torso_angle_threshold', 45)
        
        if (deadlift_rules.get('leg_extended', False) and is_legs_extended(landmarks, joint_angles) and 
            deadlift_rules.get('torso_forward_tilt', False) and is_torso_forward_tilt(landmarks, joint_angles, torso_angle_threshold)):
            return 'deadlift'
    
    # オーバーヘッドプレスのルール
    if 'overhead_press' in config_rules:
        ohp_rules = config_rules['overhead_press']
        elbow_angle_threshold = ohp_rules.get('elbow_angle_threshold', 160)
        
        if (ohp_rules.get('hands_above_head', False) and is_hands_above_head(landmarks) and 
            ohp_rules.get('elbow_extension', False) and is_elbow_extension(landmarks, joint_angles, elbow_angle_threshold)):
            return 'overhead_press'
    
    # ルールに該当しない場合は空文字列
    return ""

def apply(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    ステップ6: ルールベース優先判定ゲートを適用
    
    Args:
        input_data: 入力フレームデータ (フレームID: ランドマークデータ)
    
    Returns:
        処理済みデータ
    """
    start_time = time.time()
    config = load_config()['rulegate']
    
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
    
    # 各フレームに対してルールベース判定を適用
    for frame_id in frame_ids:
        str_frame_id = str(frame_id)
        
        if str_frame_id in input_data:
            frame_data = input_data[str_frame_id]
            
            # 現在のラベル（多数決やHMMで平滑化されたもの）
            current_label = ""
            if 'smoothed_label' in frame_data:
                current_label = frame_data['smoothed_label']
            elif 'label' in frame_data:
                current_label = frame_data['label']
            
            # ルールベース判定
            rule_based_label = apply_rule_based_classification(frame_data, config['rules'])
            
            # 出力データにルールベース判定結果を追加
            output_data[str_frame_id]['rule_based_label'] = rule_based_label
            
            # ルールが優先されるべきなら、最終ラベルを更新
            if config['rule_priority'] and rule_based_label and rule_based_label != current_label:
                output_data[str_frame_id]['final_label'] = rule_based_label
            else:
                # そうでなければ現在のラベルを維持
                output_data[str_frame_id]['final_label'] = current_label
    
    # 処理時間を記録
    elapsed_time = time.time() - start_time
    metadata['step06_time'] = elapsed_time
    metadata['step06_applied'] = True
    output_data['_metadata'] = metadata
    
    return output_data

def main():
    """単体実行用のエントリーポイント"""
    # サンプル入力データ（ステップ5の出力またはそれ以前の出力）
    try:
        # まずステップ5の出力を試す
        sample_input = 'step05_output.json'
        with open(sample_input, 'r') as f:
            input_data = json.load(f)
    except FileNotFoundError:
        try:
            # ステップ5の出力がなければステップ4の出力を試す
            sample_input = 'step04_output.json'
            with open(sample_input, 'r') as f:
                input_data = json.load(f)
        except FileNotFoundError:
            try:
                # それもなければステップ3の出力を試す
                sample_input = 'step03_output.json'
                with open(sample_input, 'r') as f:
                    input_data = json.load(f)
            except FileNotFoundError:
                try:
                    # それもなければステップ2の出力を試す
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
    
    # ルールベース優先判定ゲートステップを適用
    output_data = apply(input_data)
    
    # 結果を保存
    output_file = 'step06_output.json'
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"ステップ6完了: 結果を {output_file} に保存しました")
    if '_metadata' in output_data:
        print(f"処理時間: {output_data['_metadata']['step06_time']:.3f} 秒")
    
    # 最終出力ファイルとしてenhanced_predictions.jsonにも保存
    final_output_file = 'enhanced_predictions.json'
    with open(final_output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"すべてのステップ完了: 最終結果を {final_output_file} に保存しました")

if __name__ == '__main__':
    main()