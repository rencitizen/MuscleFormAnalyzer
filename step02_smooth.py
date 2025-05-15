"""
Step 2: ランドマークの平滑化処理

Savitzky-Golayフィルタまたは移動平均フィルタを使用して
ランドマークの時系列データを平滑化します。
"""
import numpy as np
import json
import yaml
import time
import copy
from typing import Dict, Any, List
from scipy import signal

def load_config():
    """設定ファイルの読み込み"""
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)

def apply_savgol_filter(data: np.ndarray, window_size: int, polyorder: int) -> np.ndarray:
    """
    Savitzky-Golayフィルタを適用
    
    Args:
        data: 入力データ配列
        window_size: 窓サイズ
        polyorder: 多項式の次数
    
    Returns:
        フィルタリングされたデータ
    """
    # データが窓サイズより小さい場合は処理しない
    if len(data) < window_size:
        return data
    
    # 奇数の窓サイズが必要
    if window_size % 2 == 0:
        window_size += 1
    
    # 多項式の次数は窓サイズより小さい必要がある
    if polyorder >= window_size:
        polyorder = window_size - 1
    
    # フィルタ適用
    return signal.savgol_filter(data, window_size, polyorder)

def apply_moving_average(data: np.ndarray, window_size: int) -> np.ndarray:
    """
    移動平均フィルタを適用
    
    Args:
        data: 入力データ配列
        window_size: 窓サイズ
    
    Returns:
        フィルタリングされたデータ
    """
    # データが窓サイズより小さい場合は処理しない
    if len(data) < window_size:
        return data
    
    # 畳み込みカーネル
    kernel = np.ones(window_size) / window_size
    
    # 畳み込みによる移動平均
    return np.convolve(data, kernel, mode='same')

def apply(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    ステップ2: 平滑化処理を適用
    
    Args:
        input_data: 入力フレームデータ (フレームID: ランドマークデータ)
    
    Returns:
        処理済みデータ
    """
    start_time = time.time()
    config = load_config()['smooth']
    
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
    
    # すべてのランドマークのIDを取得（最初の有効なフレームから）
    landmark_ids = []
    for frame_id in frame_ids:
        frame_data = input_data[str(frame_id)]
        if frame_data and 'landmarks' in frame_data:
            landmark_ids = list(frame_data['landmarks'].keys())
            break
    
    if not landmark_ids:
        print("警告: 有効なランドマークが見つかりませんでした")
        return output_data
    
    # 各ランドマークに対して処理
    for landmark_id in landmark_ids:
        # 各軸のデータを収集
        x_data = []
        y_data = []
        z_data = []
        
        # フレームからランドマークデータを収集
        for frame_id in frame_ids:
            str_frame_id = str(frame_id)
            if (str_frame_id in input_data and 
                'landmarks' in input_data[str_frame_id] and 
                landmark_id in input_data[str_frame_id]['landmarks']):
                
                landmark_data = input_data[str_frame_id]['landmarks'][landmark_id]
                
                # 座標データを収集
                x_data.append(landmark_data.get('x', 0.0))
                y_data.append(landmark_data.get('y', 0.0))
                z_data.append(landmark_data.get('z', 0.0))
            else:
                # データがない場合は0で埋める
                x_data.append(0.0)
                y_data.append(0.0)
                z_data.append(0.0)
        
        # NumPy配列に変換
        x_array = np.array(x_data)
        y_array = np.array(y_data)
        z_array = np.array(z_data)
        
        # 選択されたフィルタを適用
        if config['method'] == 'savgol':
            # Savitzky-Golayフィルタ
            window_size = config['window_size']
            polyorder = config['polyorder']
            
            x_smoothed = apply_savgol_filter(x_array, window_size, polyorder)
            y_smoothed = apply_savgol_filter(y_array, window_size, polyorder)
            z_smoothed = apply_savgol_filter(z_array, window_size, polyorder)
        else:
            # 移動平均フィルタ（デフォルト）
            window_size = config['moving_avg_window']
            
            x_smoothed = apply_moving_average(x_array, window_size)
            y_smoothed = apply_moving_average(y_array, window_size)
            z_smoothed = apply_moving_average(z_array, window_size)
        
        # 平滑化されたデータを出力データに格納
        for i, frame_id in enumerate(frame_ids):
            str_frame_id = str(frame_id)
            if (str_frame_id in output_data and 
                'landmarks' in output_data[str_frame_id] and 
                landmark_id in output_data[str_frame_id]['landmarks']):
                
                # 平滑化された座標を更新
                output_data[str_frame_id]['landmarks'][landmark_id]['x'] = x_smoothed[i]
                output_data[str_frame_id]['landmarks'][landmark_id]['y'] = y_smoothed[i]
                output_data[str_frame_id]['landmarks'][landmark_id]['z'] = z_smoothed[i]
    
    # 処理時間を記録
    elapsed_time = time.time() - start_time
    metadata['step02_time'] = elapsed_time
    metadata['step02_applied'] = True
    output_data['_metadata'] = metadata
    
    return output_data

def main():
    """単体実行用のエントリーポイント"""
    # サンプル入力データ（ステップ1の出力または既存システムからの入力）
    try:
        # まずステップ1の出力を試す
        sample_input = 'step01_output.json'
        with open(sample_input, 'r') as f:
            input_data = json.load(f)
    except FileNotFoundError:
        try:
            # ステップ1の出力がなければ生データを試す
            sample_input = 'raw_landmarks_by_frame.json'
            with open(sample_input, 'r') as f:
                input_data = json.load(f)
        except FileNotFoundError:
            print("エラー: 入力ファイルが見つかりません。")
            return
    
    # 平滑化ステップを適用
    output_data = apply(input_data)
    
    # 結果を保存
    output_file = 'step02_output.json'
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"ステップ2完了: 結果を {output_file} に保存しました")
    if '_metadata' in output_data:
        print(f"処理時間: {output_data['_metadata']['step02_time']:.3f} 秒")

if __name__ == '__main__':
    main()