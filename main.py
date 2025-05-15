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
import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox

from config import save_height, load_height
from scale import ScaleCalculator
from analysis import BodyAnalyzer

# Flaskサーバーモード用にappをインポート
try:
    from main_server import app
except ImportError:
    app = None

# MediaPipe Poseの初期化
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

def input_height() -> float:
    """
    ユーザーから身長を入力してもらう（GUI）
    
    Returns:
        float: 入力された身長（cm）
    """
    # 保存済みの身長を確認
    saved_height = load_height()
    
    # GUIウィンドウを作成
    root = tk.Tk()
    root.withdraw()  # メインウィンドウを非表示
    
    if saved_height:
        # 保存済みの身長があれば確認
        use_saved = messagebox.askyesno(
            "保存された身長情報",
            f"前回保存された身長 {saved_height} cm を使用しますか？\n「いいえ」を選択すると新しく入力できます。"
        )
        if use_saved:
            return saved_height
    
    # 新しい身長を入力
    while True:
        height_str = simpledialog.askstring(
            "身長を入力", 
            "身長（cm）を入力してください:",
            initialvalue="170" if not saved_height else str(saved_height)
        )
        
        if height_str is None:
            # キャンセルした場合はデフォルト値
            print("入力がキャンセルされました。デフォルト値 170cm を使用します。")
            return 170.0
        
        try:
            height = float(height_str)
            if 100 <= height <= 250:
                save_height(height)  # 入力値を保存
                return height
            else:
                messagebox.showerror("エラー", "身長は100cm～250cmの範囲で入力してください")
        except ValueError:
            messagebox.showerror("エラー", "有効な数値を入力してください")

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

def select_video_file() -> Optional[str]:
    """
    分析する動画ファイルを選択する（GUI）
    
    Returns:
        Optional[str]: 選択された動画ファイルのパス、キャンセルされた場合はNone
    """
    root = tk.Tk()
    root.withdraw()  # メインウィンドウを非表示
    
    file_path = filedialog.askopenfilename(
        title="分析する動画ファイルを選択",
        filetypes=[
            ("動画ファイル", "*.mp4 *.avi *.mov *.mkv"),
            ("すべてのファイル", "*.*")
        ]
    )
    
    return file_path if file_path else None

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

def analyze_video(video_path: str, user_height_cm: float, use_gui: bool = True) -> Dict[str, Any]:
    """
    動画を分析して身体各部の寸法を計測する
    
    Args:
        video_path (str): 分析する動画ファイルのパス
        user_height_cm (float): ユーザーの身長（cm）
        use_gui (bool, optional): GUIを使用するかどうか. Defaults to True.
    
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
        
        # プログレスバーの初期化
        if use_gui:
            progress_window = tk.Toplevel()
            progress_window.title("分析の進行状況")
            progress_window.geometry("400x100")
            
            progress_label = tk.Label(progress_window, text="動画を分析中...")
            progress_label.pack(pady=10)
            
            progress_bar = tk.Canvas(progress_window, width=300, height=20, bg="white")
            progress_bar.pack()
            
            progress_rect = progress_bar.create_rectangle(0, 0, 0, 20, fill="blue")
            
            progress_window.update()
        
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                break
            
            frame_count += 1
            
            # 進行状況の表示
            if frame_count % 10 == 0 or frame_count == 1:
                progress_percentage = min(100, int((frame_count / total_frames) * 100))
                
                if use_gui:
                    # GUIプログレスバーを更新
                    progress_bar.coords(progress_rect, 0, 0, 3 * progress_percentage, 20)
                    progress_label.config(text=f"分析中... {progress_percentage}% ({frame_count}/{total_frames})")
                    progress_window.update()
                else:
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
        if use_gui:
            progress_window.destroy()
        else:
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
    
    try:
        # GUIが利用可能かチェック
        use_gui = True
        root = tk.Tk()
        root.withdraw()
    except:
        use_gui = False
        print("GUIが利用できないため、コマンドラインモードで実行します")
    
    # 身長の入力
    user_height_cm = input_height() if use_gui else input_height_cli()
    print(f"身長情報: {user_height_cm} cm")
    
    # 動画ファイルの選択
    video_path = select_video_file() if use_gui else select_video_file_cli()
    if not video_path:
        print("処理をキャンセルしました。")
        return
    
    print(f"選択された動画: {video_path}")
    
    # 動画分析
    results = analyze_video(video_path, user_height_cm, use_gui)
    
    if results:
        # 分析結果が得られた場合は成功
        if use_gui:
            messagebox.showinfo(
                "分析完了", 
                f"身体寸法の分析が完了しました!\n結果はresultsフォルダに保存されています。"
            )
    else:
        # 分析に失敗した場合
        if use_gui:
            messagebox.showerror(
                "分析エラー", 
                "動画からポーズの検出に失敗しました。別の動画で再試行してください。"
            )

if __name__ == "__main__":
    main()