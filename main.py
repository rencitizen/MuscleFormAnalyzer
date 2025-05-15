"""
BodyScale Pose Analyzer - メイン実行モジュール
身長情報からピクセル→実寸法(cm)スケール変換を行い、身体各部の寸法を計測・表示
"""
import os
import sys
import time
import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, Any, Optional, Tuple, List, Union

from config import save_height, load_height
from scale import ScaleCalculator
from analysis import BodyAnalyzer

# Flaskサーバーモード用にappをインポート
try:
    from main_server import app
except ImportError:
    app = None

# MediaPipe Poseの初期化
try:
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
except AttributeError:
    # MediaPipeのバージョンによって構造が異なる場合の対応
    import mediapipe.python as mp_python
    mp_pose = mp_python.solutions.pose
    mp_drawing = mp_python.solutions.drawing_utils
    mp_drawing_styles = mp_python.solutions.drawing_styles

def input_height_cli() -> float:
    """
    ユーザーから身長を入力してもらう（CUI）
    
    Returns:
        float: 入力された身長（cm）
    """
    # 保存済みの身長を確認
    saved_height = load_height()
    
    if saved_height:
        # 保存済みの身長があれば確認
        while True:
            response = input(f"前回保存された身長 {saved_height} cm を使用しますか？ (y/n): ").lower()
            if response in ['y', 'yes']:
                return saved_height
            elif response in ['n', 'no']:
                break
            else:
                print("'y'または'n'で回答してください")
    
    # 新しい身長を入力
    while True:
        try:
            height_str = input("身長（cm）を入力してください: ")
            height = float(height_str)
            if 100 <= height <= 250:
                save_height(height)  # 入力値を保存
                return height
            else:
                print("身長は100cm～250cmの範囲で入力してください")
        except ValueError:
            print("有効な数値を入力してください")

def select_video_file_cli() -> Optional[str]:
    """
    分析する動画ファイルのパスを入力（CUI）
    
    Returns:
        Optional[str]: 入力された動画ファイルのパス、キャンセルされた場合はNone
    """
    while True:
        file_path = input("分析する動画ファイルのパスを入力してください（空欄で終了）: ")
        if not file_path:
            return None
        
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return file_path
        else:
            print(f"ファイル '{file_path}' が見つかりません。正しいパスを入力してください。")
            
            # サンプルファイルの提案
            sample_dir = "sample_videos"
            if os.path.exists(sample_dir) and os.path.isdir(sample_dir):
                samples = [f for f in os.listdir(sample_dir) if f.endswith(('.mp4', '.avi', '.mov'))]
                if samples:
                    print("\n利用可能なサンプル動画:")
                    for i, sample in enumerate(samples, 1):
                        print(f"  {i}. {sample}")
                    print(f"サンプルを使用する場合は、パス（例: {sample_dir}/{samples[0]}）を入力してください")

def analyze_video_cli(video_path: str, user_height_cm: float) -> Dict[str, Any]:
    """
    動画を分析して身体各部の寸法を計測する (CLI版)
    
    Args:
        video_path (str): 分析する動画ファイルのパス
        user_height_cm (float): ユーザーの身長（cm）
    
    Returns:
        Dict[str, Any]: 分析結果
    """
    # ビデオキャプチャを開始
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"エラー: 動画ファイル '{video_path}' を開けませんでした。")
        return {}
    
    # ビデオの情報を取得
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_dim = (frame_width, frame_height)
    
    print(f"\n動画情報:")
    print(f"解像度: {frame_width}x{frame_height}")
    print(f"総フレーム数: {total_frames}")
    print(f"フレームレート: {fps:.2f} fps")
    
    # 分析器を初期化
    body_analyzer = BodyAnalyzer(user_height_cm)
    
    # フレームごとのランドマークを保存
    frame_landmarks = []
    best_landmarks = None
    best_visibility = 0
    
    # MediaPipe Poseを初期化
    with mp_pose.Pose(
        static_image_mode=False,
        model_complexity=2,  # より高精度なモデル
        enable_segmentation=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as pose:
        
        print("\n動画を分析中...")
        frame_count = 0
        
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                break
            
            frame_count += 1
            
            # 進行状況の表示
            if frame_count % 10 == 0 or frame_count == 1:
                progress_percentage = min(100, int((frame_count / total_frames) * 100))
                # コンソールに進行状況を表示
                sys.stdout.write(f"\r分析中... {progress_percentage}% ({frame_count}/{total_frames})")
                sys.stdout.flush()
            
            # 画像の前処理
            # MediaPipeはRGB形式を期待するが、OpenCVはBGRで読み込む
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # ポーズ推定を実行
            results = pose.process(image_rgb)
            
            if results.pose_landmarks:
                # ランドマークを辞書に変換
                landmarks_dict = {}
                
                # 可視性の平均を計算
                total_visibility = 0
                visible_count = 0
                
                for i, landmark in enumerate(results.pose_landmarks.landmark):
                    landmarks_dict[i] = {
                        'x': landmark.x,
                        'y': landmark.y,
                        'z': landmark.z,
                        'visibility': landmark.visibility
                    }
                    
                    # 可視性の追跡（スケール計算に必要な主要なランドマークのみ）
                    if i in [0, 27, 28]:  # NOSE, LEFT_ANKLE, RIGHT_ANKLE
                        total_visibility += landmark.visibility
                        visible_count += 1
                
                # 平均可視性
                avg_visibility = total_visibility / visible_count if visible_count > 0 else 0
                
                frame_landmarks.append(landmarks_dict)
                
                # 可視性が良いフレームを保存
                if avg_visibility > best_visibility:
                    best_visibility = avg_visibility
                    best_landmarks = landmarks_dict
        
        # 終了処理
        print("\nポーズ分析完了!")
        cap.release()
    
    # 最も良いフレームの分析結果
    if best_landmarks:
        print("\n身体寸法の分析中...")
        results = body_analyzer.analyze_landmarks(best_landmarks, frame_dim)
        
        # 結果を保存
        result_path = body_analyzer.save_results(results)
        
        # 結果の要約を表示
        body_analyzer.print_summary(results)
        print(f"\n詳細結果は {result_path} に保存されました")
        
        return results
    else:
        print("警告: 有効なポーズが検出できませんでした。")
        return {}

def main():
    """
    メインエントリーポイント
    """
    print("====== BodyScale Pose Analyzer ======")
    print("動画から体のスケールを分析し、実寸法（cm）で計測します")
    
    # サンプル動画フォルダの確認・作成
    sample_dir = "sample_videos"
    if not os.path.exists(sample_dir):
        os.makedirs(sample_dir)
        print(f"サンプル動画用フォルダを作成しました: {sample_dir}/")
        print(f"このフォルダにテスト用の動画ファイルを入れると利用できます。")
    
    # 身長の入力
    user_height_cm = input_height_cli()
    print(f"身長情報: {user_height_cm} cm")
    
    # 動画ファイルの選択
    video_path = select_video_file_cli()
    if not video_path:
        print("処理をキャンセルしました。")
        return
    
    print(f"選択された動画: {video_path}")
    
    # 動画分析
    results = analyze_video_cli(video_path, user_height_cm)
    
    if results:
        print("\n分析が正常に完了しました！")
    else:
        print("\n分析に失敗しました。別の動画で再試行してください。")

if __name__ == "__main__":
    main()