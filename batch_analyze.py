#!/usr/bin/env python3
"""
BodyScale Pose Analyzer - バッチモード
コマンドライン引数で身長と動画ファイルを指定して実行可能
"""
import os
import sys
import json
from typing import Dict, Any, Optional

from config import save_height
from main import analyze_video_cli

def print_usage():
    """使用方法の表示"""
    print("使用方法:")
    print("  python batch_analyze.py <身長cm> <動画ファイルパス>")
    print("例:")
    print("  python batch_analyze.py 170 sample_videos/example.mp4")
    print("\nまたは引数なしで実行:")
    print("  python batch_analyze.py")
    print("  → サンプルデータを表示します。")

def display_sample_data():
    """サンプルデータを表示"""
    sample_path = 'results/sample_metrics.json'
    
    if not os.path.exists(sample_path):
        print(f"エラー: サンプルデータファイル {sample_path} が見つかりません。")
        return
    
    try:
        with open(sample_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("\n===== サンプルデータ =====")
        print(f"身長: {data['user_height_cm']} cm")
        print(f"左腕の長さ: {data['left_arm_cm']} cm")
        print(f"右腕の長さ: {data['right_arm_cm']} cm")
        print(f"左脚の長さ: {data['left_leg_cm']} cm")
        print(f"右脚の長さ: {data['right_leg_cm']} cm")
        
        print("\n関節位置 (先頭6件のみ表示):")
        for i, (joint, pos) in enumerate(data['joints_cm'].items()):
            if i >= 6:
                break
            print(f"  {joint}: x={pos['x']:.1f}, y={pos['y']:.1f}, z={pos['z']:.1f}")
        
        print(f"\n詳細データは {sample_path} を参照してください。")
    except Exception as e:
        print(f"エラー: サンプルデータの読み込みに失敗しました: {e}")

def main():
    """メイン関数"""
    print("====== BodyScale Pose Analyzer (バッチモード) ======")
    
    # コマンドライン引数の確認
    if len(sys.argv) == 1:
        print("引数がありません。サンプルデータを表示します。")
        display_sample_data()
        print_usage()
        return
    
    if len(sys.argv) != 3:
        print("エラー: 引数の数が正しくありません。")
        print_usage()
        return
    
    # 身長の処理
    try:
        height_cm = float(sys.argv[1])
        if height_cm < 100 or height_cm > 250:
            print("エラー: 身長は100cm～250cmの範囲で入力してください。")
            return
    except ValueError:
        print("エラー: 身長の値が無効です。数値を入力してください。")
        return
    
    # 動画ファイルの確認
    video_path = sys.argv[2]
    if not os.path.exists(video_path) or not os.path.isfile(video_path):
        print(f"エラー: 動画ファイル '{video_path}' が見つかりません。")
        return
    
    # 身長情報を保存
    save_height(height_cm)
    
    print(f"身長: {height_cm} cm")
    print(f"動画ファイル: {video_path}")
    
    # 分析実行
    results = analyze_video_cli(video_path, height_cm)
    
    if results:
        print("\n分析が正常に完了しました！")
    else:
        print("\n分析に失敗しました。別の動画で再試行してください。")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nプログラムが中断されました。")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nエラーが発生しました: {e}")
        sys.exit(1)