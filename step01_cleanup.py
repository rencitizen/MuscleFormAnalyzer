"""
Step 1: ランドマークの欠損補間とvisibility重み付け

- visibility値が低いランドマークを線形補間
- ランドマーク座標にvisibilityを掛けてノイズ緩和
"""
import numpy as np
import json
import yaml
import time
import copy
from typing import Dict, Any, List

def load_config():
    """設定ファイルの読み込み"""
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)

def apply(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    ステップ1: クリーンアップ処理を適用
    
    Args:
        input_data: 入力フレームデータ (フレームID: ランドマークデータ)
    
    Returns:
        処理済みデータ
    """
    start_time = time.time()
    config = load_config()['cleanup']
    
    # 入力データのディープコピーを作成
    output_data = copy.deepcopy(input_data)
    
    # フレームIDを整数として取得し、順序付け
    frame_ids = sorted([int(k) for k in input_data.keys()])
    
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
        # 各フレームのこのランドマークのvisibilityを収集
        visibility_values = {}
        coordinates = {}
        
        for frame_id in frame_ids:
            str_frame_id = str(frame_id)
            if (str_frame_id in input_data and 
                'landmarks' in input_data[str_frame_id] and 
                landmark_id in input_data[str_frame_id]['landmarks']):
                
                landmark_data = input_data[str_frame_id]['landmarks'][landmark_id]
                
                # visibilityがある場合は保存
                if 'visibility' in landmark_data:
                    visibility_values[frame_id] = landmark_data['visibility']
                else:
                    # visibilityがない場合は1.0と仮定
                    visibility_values[frame_id] = 1.0
                
                # 座標を保存
                if 'x' in landmark_data and 'y' in landmark_data and 'z' in landmark_data:
                    coordinates[frame_id] = {
                        'x': landmark_data['x'],
                        'y': landmark_data['y'],
                        'z': landmark_data['z']
                    }
        
        # visibility閾値以下のランドマークを特定
        low_visibility_frames = [
            frame_id for frame_id in visibility_values 
            if visibility_values[frame_id] < config['min_visibility']
        ]
        
        # 欠損補間: 低可視性のランドマークを線形補間
        for axis in ['x', 'y', 'z']:
            # 欠損していないフレームの座標を取得
            valid_frames = sorted([
                frame_id for frame_id in coordinates 
                if frame_id not in low_visibility_frames
            ])
            
            if not valid_frames:
                continue
            
            valid_coords = np.array([coordinates[frame_id][axis] for frame_id in valid_frames])
            
            # 低可視性フレームを線形補間
            for frame_id in low_visibility_frames:
                if frame_id in coordinates:
                    # 最も近い前後の有効なフレームを見つける
                    prev_idx = np.searchsorted(valid_frames, frame_id) - 1
                    next_idx = prev_idx + 1
                    
                    if prev_idx < 0:
                        # 最初のフレームより前の場合、最初の有効値を使用
                        output_data[str(frame_id)]['landmarks'][landmark_id][axis] = valid_coords[0]
                    elif next_idx >= len(valid_frames):
                        # 最後のフレームより後の場合、最後の有効値を使用
                        output_data[str(frame_id)]['landmarks'][landmark_id][axis] = valid_coords[-1]
                    else:
                        # 線形補間
                        prev_frame = valid_frames[prev_idx]
                        next_frame = valid_frames[next_idx]
                        prev_val = coordinates[prev_frame][axis]
                        next_val = coordinates[next_frame][axis]
                        
                        ratio = (frame_id - prev_frame) / (next_frame - prev_frame)
                        interpolated_val = prev_val + ratio * (next_val - prev_val)
                        
                        output_data[str(frame_id)]['landmarks'][landmark_id][axis] = interpolated_val
        
        # ランドマーク座標にvisibilityを掛ける (ノイズ緩和)
        for frame_id in frame_ids:
            str_frame_id = str(frame_id)
            if (str_frame_id in output_data and 
                'landmarks' in output_data[str_frame_id] and 
                landmark_id in output_data[str_frame_id]['landmarks']):
                
                landmark_data = output_data[str_frame_id]['landmarks'][landmark_id]
                visibility = visibility_values.get(frame_id, 0.0)
                
                # 座標をvisibilityで重み付け
                for axis in ['x', 'y', 'z']:
                    if axis in landmark_data:
                        landmark_data[axis] *= visibility
    
    # 処理時間を記録
    elapsed_time = time.time() - start_time
    output_data['_metadata'] = output_data.get('_metadata', {})
    output_data['_metadata']['step01_time'] = elapsed_time
    output_data['_metadata']['step01_applied'] = True
    
    return output_data

def main():
    """単体実行用のエントリーポイント"""
    # サンプル入力データ（実際には既存システムからJSONとして提供される）
    sample_input = 'raw_landmarks_by_frame.json'
    
    try:
        with open(sample_input, 'r') as f:
            input_data = json.load(f)
    except FileNotFoundError:
        print(f"エラー: 入力ファイル {sample_input} が見つかりません。")
        return
    
    # クリーンアップステップを適用
    output_data = apply(input_data)
    
    # 結果を保存
    output_file = 'step01_output.json'
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"ステップ1完了: 結果を {output_file} に保存しました")
    if '_metadata' in output_data:
        print(f"処理時間: {output_data['_metadata']['step01_time']:.3f} 秒")

if __name__ == '__main__':
    main()