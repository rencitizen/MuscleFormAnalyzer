"""
Step 5: 窓幅多数決とHMM後処理

- 30フレーム窓で多数決を取り、ノイズ低減
- HMM（Hidden Markov Model）で状態遷移を滑らかに
- 短時間の誤検出を抑制
"""
import numpy as np
import json
import yaml
import time
import copy
from typing import Dict, Any, List, Tuple
from collections import Counter

def load_config():
    """設定ファイルの読み込み"""
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)

def majority_vote(labels: List[str], window_size: int) -> List[str]:
    """
    窓幅多数決による平滑化
    
    Args:
        labels: 各フレームのラベル
        window_size: 多数決を取る窓サイズ
    
    Returns:
        平滑化されたラベル
    """
    n = len(labels)
    half_window = window_size // 2
    smoothed_labels = copy.deepcopy(labels)
    
    for i in range(n):
        # 窓の範囲を決定
        start = max(0, i - half_window)
        end = min(n, i + half_window + 1)
        
        # 窓内のラベルを収集
        window_labels = labels[start:end]
        
        # 多数決（最頻値）
        counter = Counter(window_labels)
        smoothed_labels[i] = counter.most_common(1)[0][0]
    
    return smoothed_labels

def hmm_smoothing(labels: List[str], transition_prob: float, min_state_duration: int) -> List[str]:
    """
    HMMによる状態遷移の平滑化
    
    Args:
        labels: 各フレームのラベル
        transition_prob: 状態遷移確率
        min_state_duration: 最小状態持続フレーム数
    
    Returns:
        平滑化されたラベル
    """
    n = len(labels)
    if n == 0:
        return []
    
    # ユニークなラベルを取得
    unique_labels = list(set(labels))
    
    # ラベルをインデックスに変換
    label_to_idx = {label: idx for idx, label in enumerate(unique_labels)}
    idx_to_label = {idx: label for idx, label in enumerate(unique_labels)}
    
    # ラベルをインデックスの配列に変換
    label_indices = [label_to_idx[label] for label in labels]
    
    # 初期状態はラベルの最初の値
    current_state = label_indices[0]
    current_duration = 1
    
    # 平滑化されたラベル
    smoothed_indices = [current_state]
    
    # 各フレームを処理
    for i in range(1, n):
        next_state = label_indices[i]
        
        # 状態が変わるかどうかを決定
        if next_state != current_state:
            # 現在の持続時間が最小閾値未満なら遷移確率を下げる
            if current_duration < min_state_duration:
                # ランダムに遷移を決定
                if np.random.random() > transition_prob:
                    # 遷移しない
                    next_state = current_state
                    current_duration += 1
                else:
                    # 遷移する
                    current_state = next_state
                    current_duration = 1
            else:
                # 最小持続時間を超えた場合は通常の遷移
                current_state = next_state
                current_duration = 1
        else:
            # 同じ状態が続く
            current_duration += 1
        
        smoothed_indices.append(current_state)
    
    # インデックスをラベルに戻す
    smoothed_labels = [idx_to_label[idx] for idx in smoothed_indices]
    
    return smoothed_labels

def apply(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    ステップ5: 多数決とHMM後処理を適用
    
    Args:
        input_data: 入力フレームデータ (フレームID: ランドマークデータ)
    
    Returns:
        処理済みデータ
    """
    start_time = time.time()
    config = load_config()['voting']
    
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
    
    # 各フレームのラベルを収集
    labels = []
    # ラベルがある場合はそれを使用、なければ'rest'をデフォルトとする
    for frame_id in frame_ids:
        str_frame_id = str(frame_id)
        
        # 予測ラベルのフィールド名は実装により異なる可能性がある
        if str_frame_id in input_data:
            frame_data = input_data[str_frame_id]
            
            # ラベルフィールドの候補
            label_fields = ['label', 'predicted_label', 'pose', 'exercise']
            
            # 最初に見つかったラベルフィールドを使用
            label = None
            for field in label_fields:
                if field in frame_data:
                    label = frame_data[field]
                    break
            
            if label is not None:
                labels.append(label)
            else:
                # デフォルトラベル
                labels.append('rest')
        else:
            # デフォルトラベル
            labels.append('rest')
    
    # 窓幅多数決による平滑化
    smoothed_labels = majority_vote(labels, config['window_size'])
    
    # HMM後処理（設定で有効な場合）
    if config['hmm']['enabled']:
        smoothed_labels = hmm_smoothing(
            smoothed_labels,
            config['hmm']['transition_prob'],
            config['hmm']['min_state_duration']
        )
    
    # 平滑化されたラベルを出力データに格納
    for i, frame_id in enumerate(frame_ids):
        str_frame_id = str(frame_id)
        
        if str_frame_id in output_data:
            # 平滑化されたラベルを追加
            output_data[str_frame_id]['smoothed_label'] = smoothed_labels[i]
    
    # 処理時間を記録
    elapsed_time = time.time() - start_time
    metadata['step05_time'] = elapsed_time
    metadata['step05_applied'] = True
    output_data['_metadata'] = metadata
    
    return output_data

def main():
    """単体実行用のエントリーポイント"""
    # サンプル入力データ（ステップ4の出力またはそれ以前の出力）
    try:
        # まずステップ4の出力を試す
        sample_input = 'step04_output.json'
        with open(sample_input, 'r') as f:
            input_data = json.load(f)
    except FileNotFoundError:
        try:
            # ステップ4の出力がなければステップ3の出力を試す
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
    
    # 多数決とHMM後処理ステップを適用
    output_data = apply(input_data)
    
    # 結果を保存
    output_file = 'step05_output.json'
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"ステップ5完了: 結果を {output_file} に保存しました")
    if '_metadata' in output_data:
        print(f"処理時間: {output_data['_metadata']['step05_time']:.3f} 秒")

if __name__ == '__main__':
    main()