"""
トレーニングフォーム分析に必要な各種チェック関数
"""
import math
import numpy as np
from typing import Dict, Any, Optional, Tuple

def calculate_back_angle(landmarks: Dict[int, Dict[str, float]]) -> Optional[float]:
    """
    背中の角度を計算（垂直線に対する角度）
    
    Args:
        landmarks: ランドマークデータ
    
    Returns:
        背中の角度（度）、計算できない場合はNone
    """
    try:
        # 肩と腰のランドマークを取得
        if 11 in landmarks and 12 in landmarks and 23 in landmarks and 24 in landmarks:
            # 両肩の中心
            shoulder_x = (landmarks[11]['x'] + landmarks[12]['x']) / 2
            shoulder_y = (landmarks[11]['y'] + landmarks[12]['y']) / 2
            
            # 両腰の中心
            hip_x = (landmarks[23]['x'] + landmarks[24]['x']) / 2
            hip_y = (landmarks[23]['y'] + landmarks[24]['y']) / 2
            
            # 垂直線に対する角度を計算
            dx = shoulder_x - hip_x
            dy = shoulder_y - hip_y
            
            # 垂直線（下向きを正とする）との角度
            angle = math.degrees(math.atan2(dx, dy))
            
            # 絶対値を返す（左右の傾きを区別しない）
            return abs(angle)
        return None
    except Exception as e:
        print(f"背中の角度計算中にエラー: {e}")
        return None

def check_knee_alignment(landmarks: Dict[int, Dict[str, float]]) -> float:
    """
    膝と足首、股関節のアライメントをチェック（膝の内側・外側の度合い）
    
    Args:
        landmarks: ランドマークデータ
    
    Returns:
        膝の内側・外側の度合い（度）、値が正なら内側、負なら外側
    """
    try:
        # 左右の平均角度を計算
        total_angle = 0
        count = 0
        
        # 左足のチェック（股関節-膝-足首）
        if 23 in landmarks and 25 in landmarks and 27 in landmarks:
            hip = landmarks[23]
            knee = landmarks[25]
            ankle = landmarks[27]
            
            # 膝から股関節へのベクトル
            v1 = (hip['x'] - knee['x'], hip['y'] - knee['y'])
            
            # 膝から足首へのベクトル
            v2 = (ankle['x'] - knee['x'], ankle['y'] - knee['y'])
            
            # 2つのベクトル間の角度
            dot = v1[0] * v2[0] + v1[1] * v2[1]
            mag1 = math.sqrt(v1[0]**2 + v1[1]**2)
            mag2 = math.sqrt(v2[0]**2 + v2[1]**2)
            
            if mag1 > 0 and mag2 > 0:
                cos_angle = dot / (mag1 * mag2)
                # 値が範囲外にならないよう制限
                cos_angle = max(-1, min(1, cos_angle))
                angle = math.degrees(math.acos(cos_angle))
                
                # 内側か外側かを判定（外積のz成分の符号で判断）
                cross_z = v1[0] * v2[1] - v1[1] * v2[0]
                if cross_z > 0:  # 内側
                    angle = abs(angle)
                else:  # 外側
                    angle = -abs(angle)
                
                total_angle += angle
                count += 1
        
        # 右足のチェック（股関節-膝-足首）
        if 24 in landmarks and 26 in landmarks and 28 in landmarks:
            hip = landmarks[24]
            knee = landmarks[26]
            ankle = landmarks[28]
            
            # 膝から股関節へのベクトル
            v1 = (hip['x'] - knee['x'], hip['y'] - knee['y'])
            
            # 膝から足首へのベクトル
            v2 = (ankle['x'] - knee['x'], ankle['y'] - knee['y'])
            
            # 2つのベクトル間の角度
            dot = v1[0] * v2[0] + v1[1] * v2[1]
            mag1 = math.sqrt(v1[0]**2 + v1[1]**2)
            mag2 = math.sqrt(v2[0]**2 + v2[1]**2)
            
            if mag1 > 0 and mag2 > 0:
                cos_angle = dot / (mag1 * mag2)
                # 値が範囲外にならないよう制限
                cos_angle = max(-1, min(1, cos_angle))
                angle = math.degrees(math.acos(cos_angle))
                
                # 内側か外側かを判定（外積のz成分の符号で判断）
                cross_z = v1[0] * v2[1] - v1[1] * v2[0]
                if cross_z < 0:  # 右足は逆になる
                    angle = abs(angle)
                else:
                    angle = -abs(angle)
                
                total_angle += angle
                count += 1
        
        # 左右の平均を返す
        if count > 0:
            return total_angle / count
        return 0
    except Exception as e:
        print(f"膝のアライメントチェック中にエラー: {e}")
        return 0

def check_leg_symmetry(landmarks: Dict[int, Dict[str, float]]) -> float:
    """
    左右の脚のシンメトリをチェック
    
    Args:
        landmarks: ランドマークデータ
    
    Returns:
        左右の非対称性の度合い（％）、0が完全に対称
    """
    try:
        # 左右の膝の角度を取得
        left_knee_angle = None
        right_knee_angle = None
        
        # 左膝の角度（股関節-膝-足首）
        if 23 in landmarks and 25 in landmarks and 27 in landmarks:
            hip = landmarks[23]
            knee = landmarks[25]
            ankle = landmarks[27]
            
            # 膝から股関節へのベクトル
            v1 = (hip['x'] - knee['x'], hip['y'] - knee['y'])
            
            # 膝から足首へのベクトル
            v2 = (ankle['x'] - knee['x'], ankle['y'] - knee['y'])
            
            # 2つのベクトル間の角度
            dot = v1[0] * v2[0] + v1[1] * v2[1]
            mag1 = math.sqrt(v1[0]**2 + v1[1]**2)
            mag2 = math.sqrt(v2[0]**2 + v2[1]**2)
            
            if mag1 > 0 and mag2 > 0:
                cos_angle = dot / (mag1 * mag2)
                # 値が範囲外にならないよう制限
                cos_angle = max(-1, min(1, cos_angle))
                left_knee_angle = math.degrees(math.acos(cos_angle))
        
        # 右膝の角度（股関節-膝-足首）
        if 24 in landmarks and 26 in landmarks and 28 in landmarks:
            hip = landmarks[24]
            knee = landmarks[26]
            ankle = landmarks[28]
            
            # 膝から股関節へのベクトル
            v1 = (hip['x'] - knee['x'], hip['y'] - knee['y'])
            
            # 膝から足首へのベクトル
            v2 = (ankle['x'] - knee['x'], ankle['y'] - knee['y'])
            
            # 2つのベクトル間の角度
            dot = v1[0] * v2[0] + v1[1] * v2[1]
            mag1 = math.sqrt(v1[0]**2 + v1[1]**2)
            mag2 = math.sqrt(v2[0]**2 + v2[1]**2)
            
            if mag1 > 0 and mag2 > 0:
                cos_angle = dot / (mag1 * mag2)
                # 値が範囲外にならないよう制限
                cos_angle = max(-1, min(1, cos_angle))
                right_knee_angle = math.degrees(math.acos(cos_angle))
        
        # 左右の膝の角度の差を計算
        if left_knee_angle is not None and right_knee_angle is not None:
            difference = abs(left_knee_angle - right_knee_angle)
            # 差を0-100%のスケールに変換（20度の差を100%とする）
            asymmetry = min(100, difference * 5)
            return asymmetry
        
        return 0
    except Exception as e:
        print(f"脚の対称性チェック中にエラー: {e}")
        return 0

def check_squat_depth(landmarks: Dict[int, Dict[str, float]]) -> float:
    """
    スクワットの深さをチェック（膝の曲がり具合）
    
    Args:
        landmarks: ランドマークデータ
    
    Returns:
        膝の角度（度）、90度が理想的な深さ、180度が直立
    """
    try:
        # 左右の膝の角度を取得
        knee_angles = []
        
        # 左膝の角度（股関節-膝-足首）
        if 23 in landmarks and 25 in landmarks and 27 in landmarks:
            hip = landmarks[23]
            knee = landmarks[25]
            ankle = landmarks[27]
            
            # 膝から股関節へのベクトル
            v1 = (hip['x'] - knee['x'], hip['y'] - knee['y'])
            
            # 膝から足首へのベクトル
            v2 = (ankle['x'] - knee['x'], ankle['y'] - knee['y'])
            
            # 2つのベクトル間の角度
            dot = v1[0] * v2[0] + v1[1] * v2[1]
            mag1 = math.sqrt(v1[0]**2 + v1[1]**2)
            mag2 = math.sqrt(v2[0]**2 + v2[1]**2)
            
            if mag1 > 0 and mag2 > 0:
                cos_angle = dot / (mag1 * mag2)
                # 値が範囲外にならないよう制限
                cos_angle = max(-1, min(1, cos_angle))
                angle = math.degrees(math.acos(cos_angle))
                knee_angles.append(angle)
        
        # 右膝の角度（股関節-膝-足首）
        if 24 in landmarks and 26 in landmarks and 28 in landmarks:
            hip = landmarks[24]
            knee = landmarks[26]
            ankle = landmarks[28]
            
            # 膝から股関節へのベクトル
            v1 = (hip['x'] - knee['x'], hip['y'] - knee['y'])
            
            # 膝から足首へのベクトル
            v2 = (ankle['x'] - knee['x'], ankle['y'] - knee['y'])
            
            # 2つのベクトル間の角度
            dot = v1[0] * v2[0] + v1[1] * v2[1]
            mag1 = math.sqrt(v1[0]**2 + v1[1]**2)
            mag2 = math.sqrt(v2[0]**2 + v2[1]**2)
            
            if mag1 > 0 and mag2 > 0:
                cos_angle = dot / (mag1 * mag2)
                # 値が範囲外にならないよう制限
                cos_angle = max(-1, min(1, cos_angle))
                angle = math.degrees(math.acos(cos_angle))
                knee_angles.append(angle)
        
        # 左右の膝の角度の平均を返す
        if knee_angles:
            return sum(knee_angles) / len(knee_angles)
        
        return 180  # デフォルトは直立状態
    except Exception as e:
        print(f"スクワットの深さチェック中にエラー: {e}")
        return 180

def check_shoulder_retraction(landmarks: Dict[int, Dict[str, float]]) -> float:
    """
    肩甲骨の引き寄せ度合いをチェック
    
    Args:
        landmarks: ランドマークデータ
    
    Returns:
        肩甲骨の引き寄せ度合い（0-1）、1が最大
    """
    try:
        # 左右の肩幅と背中の幅の比率で評価
        if 11 in landmarks and 12 in landmarks and 23 in landmarks and 24 in landmarks:
            # 肩幅
            shoulder_width = math.sqrt(
                (landmarks[11]['x'] - landmarks[12]['x'])**2 +
                (landmarks[11]['y'] - landmarks[12]['y'])**2
            )
            
            # 腰幅
            hip_width = math.sqrt(
                (landmarks[23]['x'] - landmarks[24]['x'])**2 +
                (landmarks[23]['y'] - landmarks[24]['y'])**2
            )
            
            if hip_width > 0:
                # 肩幅と腰幅の比率（肩甲骨を引き寄せると肩幅が広がる）
                ratio = shoulder_width / hip_width
                
                # 比率を0-1のスケールに正規化（比率1.5を最大の引き寄せとする）
                retraction = min(1, max(0, (ratio - 1) / 0.5))
                return retraction
        
        return 0.5  # デフォルト値
    except Exception as e:
        print(f"肩甲骨の引き寄せチェック中にエラー: {e}")
        return 0.5

def check_elbow_angles(landmarks: Dict[int, Dict[str, float]]) -> float:
    """
    肘の角度をチェック
    
    Args:
        landmarks: ランドマークデータ
    
    Returns:
        肘の角度（度）、左右の平均
    """
    try:
        # 左右の肘の角度を取得
        elbow_angles = []
        
        # 左肘の角度（肩-肘-手首）
        if 11 in landmarks and 13 in landmarks and 15 in landmarks:
            shoulder = landmarks[11]
            elbow = landmarks[13]
            wrist = landmarks[15]
            
            # 肘から肩へのベクトル
            v1 = (shoulder['x'] - elbow['x'], shoulder['y'] - elbow['y'])
            
            # 肘から手首へのベクトル
            v2 = (wrist['x'] - elbow['x'], wrist['y'] - elbow['y'])
            
            # 2つのベクトル間の角度
            dot = v1[0] * v2[0] + v1[1] * v2[1]
            mag1 = math.sqrt(v1[0]**2 + v1[1]**2)
            mag2 = math.sqrt(v2[0]**2 + v2[1]**2)
            
            if mag1 > 0 and mag2 > 0:
                cos_angle = dot / (mag1 * mag2)
                # 値が範囲外にならないよう制限
                cos_angle = max(-1, min(1, cos_angle))
                angle = math.degrees(math.acos(cos_angle))
                elbow_angles.append(angle)
        
        # 右肘の角度（肩-肘-手首）
        if 12 in landmarks and 14 in landmarks and 16 in landmarks:
            shoulder = landmarks[12]
            elbow = landmarks[14]
            wrist = landmarks[16]
            
            # 肘から肩へのベクトル
            v1 = (shoulder['x'] - elbow['x'], shoulder['y'] - elbow['y'])
            
            # 肘から手首へのベクトル
            v2 = (wrist['x'] - elbow['x'], wrist['y'] - elbow['y'])
            
            # 2つのベクトル間の角度
            dot = v1[0] * v2[0] + v1[1] * v2[1]
            mag1 = math.sqrt(v1[0]**2 + v1[1]**2)
            mag2 = math.sqrt(v2[0]**2 + v2[1]**2)
            
            if mag1 > 0 and mag2 > 0:
                cos_angle = dot / (mag1 * mag2)
                # 値が範囲外にならないよう制限
                cos_angle = max(-1, min(1, cos_angle))
                angle = math.degrees(math.acos(cos_angle))
                elbow_angles.append(angle)
        
        # 左右の肘の角度の平均を返す
        if elbow_angles:
            return sum(elbow_angles) / len(elbow_angles)
        
        return 180  # デフォルトは直立状態
    except Exception as e:
        print(f"肘の角度チェック中にエラー: {e}")
        return 180

def check_back_arch(landmarks: Dict[int, Dict[str, float]]) -> float:
    """
    背中のアーチ（反り）の度合いをチェック
    
    Args:
        landmarks: ランドマークデータ
    
    Returns:
        背中のアーチの度合い（度）
    """
    try:
        # 肩、腰、膝のランドマークを使用
        if (11 in landmarks and 12 in landmarks and 
            23 in landmarks and 24 in landmarks and 
            25 in landmarks and 26 in landmarks):
            
            # 肩の中心点
            shoulder_x = (landmarks[11]['x'] + landmarks[12]['x']) / 2
            shoulder_y = (landmarks[11]['y'] + landmarks[12]['y']) / 2
            
            # 腰の中心点
            hip_x = (landmarks[23]['x'] + landmarks[24]['x']) / 2
            hip_y = (landmarks[23]['y'] + landmarks[24]['y']) / 2
            
            # 膝の中心点
            knee_x = (landmarks[25]['x'] + landmarks[26]['x']) / 2
            knee_y = (landmarks[25]['y'] + landmarks[26]['y']) / 2
            
            # 腰と肩を結ぶベクトル
            v1 = (shoulder_x - hip_x, shoulder_y - hip_y)
            
            # 腰と膝を結ぶベクトル
            v2 = (knee_x - hip_x, knee_y - hip_y)
            
            # 2つのベクトル間の角度
            dot = v1[0] * v2[0] + v1[1] * v2[1]
            mag1 = math.sqrt(v1[0]**2 + v1[1]**2)
            mag2 = math.sqrt(v2[0]**2 + v2[1]**2)
            
            if mag1 > 0 and mag2 > 0:
                cos_angle = dot / (mag1 * mag2)
                # 値が範囲外にならないよう制限
                cos_angle = max(-1, min(1, cos_angle))
                angle = math.degrees(math.acos(cos_angle))
                
                # 腰の反りの角度（180度から引く）
                arch_angle = 180 - angle
                return arch_angle
        
        return 0  # デフォルトは反りなし
    except Exception as e:
        print(f"背中のアーチチェック中にエラー: {e}")
        return 0

def check_shoulder_bar_alignment(landmarks: Dict[int, Dict[str, float]]) -> float:
    """
    肩とバー（またはベンチ）のアライメントをチェック
    
    Args:
        landmarks: ランドマークデータ
    
    Returns:
        肩とバーのずれ（ピクセル）
    """
    try:
        # デッドリフトでは肩がバーの真上にあるべき
        # ここでは簡易的に肩と手首の水平距離で代用
        if 11 in landmarks and 12 in landmarks and 15 in landmarks and 16 in landmarks:
            # 肩の中心点
            shoulder_x = (landmarks[11]['x'] + landmarks[12]['x']) / 2
            
            # 手首の中心点（バーの位置と仮定）
            wrist_x = (landmarks[15]['x'] + landmarks[16]['x']) / 2
            
            # 水平距離の差分
            alignment_diff = abs(shoulder_x - wrist_x)
            return alignment_diff
        
        return 0  # デフォルト値
    except Exception as e:
        print(f"肩とバーのアライメントチェック中にエラー: {e}")
        return 0

def check_hip_height(landmarks: Dict[int, Dict[str, float]]) -> float:
    """
    腰の高さをチェック（デッドリフトで重要）
    
    Args:
        landmarks: ランドマークデータ
    
    Returns:
        腰の高さの適切さ（0-1）、1が最適
    """
    try:
        # 腰、膝、足首のランドマークを使用
        if (23 in landmarks and 24 in landmarks and 
            25 in landmarks and 26 in landmarks and 
            27 in landmarks and 28 in landmarks):
            
            # 腰の中心点
            hip_y = (landmarks[23]['y'] + landmarks[24]['y']) / 2
            
            # 膝の中心点
            knee_y = (landmarks[25]['y'] + landmarks[26]['y']) / 2
            
            # 足首の中心点
            ankle_y = (landmarks[27]['y'] + landmarks[28]['y']) / 2
            
            # 膝と足首の間の距離
            knee_ankle_dist = knee_y - ankle_y
            
            # 理想的には腰は膝より少し高い位置にあるべき
            # 膝と足首の距離を基準にして、腰の位置を評価
            if knee_ankle_dist > 0:
                # 腰と膝の垂直距離
                hip_knee_dist = hip_y - knee_y
                
                # 腰の理想的な高さの比率（膝より少し高い位置）
                # 1.0に近いほど理想的
                ratio = (hip_knee_dist / knee_ankle_dist) + 0.5
                
                # 0.7-1.0の範囲が理想的
                return min(1, max(0, ratio))
        
        return 0.5  # デフォルト値
    except Exception as e:
        print(f"腰の高さチェック中にエラー: {e}")
        return 0.5

def check_pushup_form(landmarks: Dict[int, Dict[str, float]]) -> Dict[str, Any]:
    """
    腕立て伏せのフォームをチェック
    
    Args:
        landmarks: ランドマークデータ
    
    Returns:
        フォームチェック結果の辞書
    """
    results = {}
    
    try:
        # 肘の角度をチェック
        elbow_angle = check_elbow_angles(landmarks)
        results['elbow_angle'] = elbow_angle
        
        if elbow_angle < 70:
            results['elbow_too_bent'] = True
        elif elbow_angle > 160:
            results['elbow_too_straight'] = True
        else:
            results['elbow_good'] = True
        
        # 背中の角度をチェック
        back_angle = calculate_back_angle(landmarks)
        results['back_angle'] = back_angle
        
        if back_angle and back_angle > 20:
            results['back_not_straight'] = True
        else:
            results['back_good'] = True
        
        # 腰が落ちていないかチェック
        hip_alignment = check_hip_alignment_pushup(landmarks)
        results['hip_alignment'] = hip_alignment
        
        if hip_alignment > 15:
            results['hip_dropping'] = True
        else:
            results['hip_good'] = True
        
    except Exception as e:
        print(f"腕立て伏せのフォームチェック中にエラー: {e}")
    
    return results

def check_hip_alignment_pushup(landmarks: Dict[int, Dict[str, float]]) -> float:
    """
    腕立て伏せ時の腰のアライメントをチェック
    
    Args:
        landmarks: ランドマークデータ
    
    Returns:
        腰のズレ（度）
    """
    try:
        # 肩、腰、足首のランドマークを使用
        if (11 in landmarks and 12 in landmarks and 
            23 in landmarks and 24 in landmarks and 
            27 in landmarks and 28 in landmarks):
            
            # 肩の中心点
            shoulder_x = (landmarks[11]['x'] + landmarks[12]['x']) / 2
            shoulder_y = (landmarks[11]['y'] + landmarks[12]['y']) / 2
            
            # 腰の中心点
            hip_x = (landmarks[23]['x'] + landmarks[24]['x']) / 2
            hip_y = (landmarks[23]['y'] + landmarks[24]['y']) / 2
            
            # 足首の中心点
            ankle_x = (landmarks[27]['x'] + landmarks[28]['x']) / 2
            ankle_y = (landmarks[27]['y'] + landmarks[28]['y']) / 2
            
            # 肩と足首を結ぶ直線（理想的な体の線）
            if ankle_x != shoulder_x:  # ゼロ除算を避ける
                ideal_slope = (ankle_y - shoulder_y) / (ankle_x - shoulder_x)
                ideal_y_at_hip = shoulder_y + ideal_slope * (hip_x - shoulder_x)
                
                # 理想的な腰の位置との差
                hip_deviation = abs(hip_y - ideal_y_at_hip)
                
                # 肩と足首の距離で正規化
                shoulder_ankle_dist = math.sqrt((ankle_x - shoulder_x)**2 + (ankle_y - shoulder_y)**2)
                if shoulder_ankle_dist > 0:
                    normalized_deviation = (hip_deviation / shoulder_ankle_dist) * 100
                    return normalized_deviation
        
        return 0  # デフォルト値
    except Exception as e:
        print(f"腰のアライメントチェック中にエラー: {e}")
        return 0

def check_plank_form(landmarks: Dict[int, Dict[str, float]]) -> Dict[str, Any]:
    """
    プランクのフォームをチェック
    
    Args:
        landmarks: ランドマークデータ
    
    Returns:
        フォームチェック結果の辞書
    """
    results = {}
    
    try:
        # 背中の角度をチェック
        back_angle = calculate_back_angle(landmarks)
        results['back_angle'] = back_angle
        
        if back_angle and back_angle > 15:
            results['back_not_straight'] = True
        else:
            results['back_good'] = True
        
        # 腰が落ちていないかチェック
        hip_alignment = check_hip_alignment_pushup(landmarks)  # 同じ関数が使える
        results['hip_alignment'] = hip_alignment
        
        if hip_alignment > 10:
            results['hip_dropping'] = True
        else:
            results['hip_good'] = True
        
        # 頭の位置をチェック（頭が下がりすぎていないか）
        head_position = check_head_position(landmarks)
        results['head_position'] = head_position
        
        if head_position > 15:
            results['head_dropping'] = True
        else:
            results['head_good'] = True
        
    except Exception as e:
        print(f"プランクのフォームチェック中にエラー: {e}")
    
    return results

def check_head_position(landmarks: Dict[int, Dict[str, float]]) -> float:
    """
    頭の位置をチェック（正しい姿勢からの逸脱度）
    
    Args:
        landmarks: ランドマークデータ
    
    Returns:
        頭の位置の逸脱度（度）
    """
    try:
        # 頭、肩、腰のランドマークを使用
        if (0 in landmarks and  # 頭（鼻）
            11 in landmarks and 12 in landmarks and  # 肩
            23 in landmarks and 24 in landmarks):  # 腰
            
            # 頭の位置
            head_x = landmarks[0]['x']
            head_y = landmarks[0]['y']
            
            # 肩の中心点
            shoulder_x = (landmarks[11]['x'] + landmarks[12]['x']) / 2
            shoulder_y = (landmarks[11]['y'] + landmarks[12]['y']) / 2
            
            # 腰の中心点
            hip_x = (landmarks[23]['x'] + landmarks[24]['x']) / 2
            hip_y = (landmarks[23]['y'] + landmarks[24]['y']) / 2
            
            # 肩と腰を結ぶベクトル（背中の線）
            v_back = (hip_x - shoulder_x, hip_y - shoulder_y)
            
            # 肩と頭を結ぶベクトル
            v_head = (head_x - shoulder_x, head_y - shoulder_y)
            
            # 2つのベクトル間の角度
            dot = v_back[0] * v_head[0] + v_back[1] * v_head[1]
            mag_back = math.sqrt(v_back[0]**2 + v_back[1]**2)
            mag_head = math.sqrt(v_head[0]**2 + v_head[1]**2)
            
            if mag_back > 0 and mag_head > 0:
                cos_angle = dot / (mag_back * mag_head)
                # 値が範囲外にならないよう制限
                cos_angle = max(-1, min(1, cos_angle))
                angle = math.degrees(math.acos(cos_angle))
                
                # 正しい姿勢では頭と背中が一直線（180度）
                # 180度からの差分を返す
                return abs(180 - angle)
        
        return 0  # デフォルト値
    except Exception as e:
        print(f"頭の位置チェック中にエラー: {e}")
        return 0