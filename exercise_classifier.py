"""
Stepwise Exercise Classifier Booster - 統合パイプライン

この統合モジュールは、以下の6ステップを順番に適用して
動作分類の精度を向上させる：
1. ランドマークの欠損補間とvisibility重み付け
2. Savitzky-Golayフィルタによる平滑化
3. 骨盤中心・肩幅=1の正規化
4. 時系列特徴量の計算
5. 窓幅多数決とHMM後処理
6. ルールベース優先判定ゲート
"""
import os
import json
import yaml
import time
from typing import Dict, Any, List, Optional, Tuple
import cv2
import numpy as np
import mediapipe as mp
from pathlib import Path

# ステップモジュールをインポート
import step01_cleanup
import step02_smooth
import step03_normalize
import step04_temporal
import step05_voting
import step06_rulegate

class ExerciseClassifier:
    """
    トレーニング動作識別器
    """
    def __init__(self, config_path: str = 'config.yaml'):
        """
        Args:
            config_path (str): 設定ファイルのパス
        """
        self.config_path = config_path
        self.load_config()
        
        # MediaPipe Poseセットアップ
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=2,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # 結果格納用
        self.landmarks_by_frame = {}
        self.frame_dimensions = (0, 0)  # (width, height)
        self.processed_data = None
    
    def load_config(self) -> None:
        """設定ファイルの読み込み"""
        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)
    
    def process_video(self, video_path: str, 
                     output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        動画を処理して運動種類を分類
        
        Args:
            video_path (str): 入力動画のパス
            output_path (Optional[str]): 結果を保存するJSONファイルのパス
        
        Returns:
            Dict[str, Any]: 分類結果
        """
        start_time = time.time()
        
        # 動画を開く
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"動画を開けませんでした: {video_path}")
        
        self.frame_dimensions = (
            int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        )
        
        # ランドマークの抽出
        self.landmarks_by_frame = self._extract_landmarks(cap)
        cap.release()
        
        # 抽出が成功したか確認
        if not self.landmarks_by_frame:
            raise ValueError("ランドマークを抽出できませんでした")
        
        # 6ステップパイプラインの適用
        self.processed_data = self._apply_pipeline()
        
        # 処理時間を記録
        elapsed_time = time.time() - start_time
        if '_metadata' not in self.processed_data:
            self.processed_data['_metadata'] = {}
        self.processed_data['_metadata']['total_processing_time'] = elapsed_time
        
        # 結果を保存（指定された場合）
        if output_path:
            self._save_results(output_path)
        
        return self.processed_data
    
    def _extract_landmarks(self, cap: cv2.VideoCapture) -> Dict[str, Any]:
        """
        動画からMediaPipeランドマークを抽出
        
        Args:
            cap (cv2.VideoCapture): OpenCVのVideoCapture
        
        Returns:
            Dict[str, Any]: フレームIDをキーとするランドマークデータ
        """
        landmarks_by_frame = {}
        frame_id = 0
        
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                break
            
            # MediaPipe処理のためにBGR->RGB変換
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # MediaPipe Poseでランドマーク検出
            results = self.pose.process(image_rgb)
            
            if results.pose_landmarks:
                # このフレームのランドマークを格納
                landmarks_by_frame[str(frame_id)] = {
                    'landmarks': self._convert_landmarks_to_dict(
                        results.pose_landmarks, self.frame_dimensions
                    ),
                    'timestamp': frame_id / cap.get(cv2.CAP_PROP_FPS),
                }
            
            frame_id += 1
            
            # 進捗表示
            if frame_id % 100 == 0:
                print(f"処理中: {frame_id}フレーム")
        
        return landmarks_by_frame
    
    def _convert_landmarks_to_dict(self, 
                                 pose_landmarks: mp.solutions.pose.PoseLandmark, 
                                 frame_dim: Tuple[int, int]) -> Dict[str, Dict[str, float]]:
        """
        MediaPipeランドマークを辞書形式に変換
        
        Args:
            pose_landmarks: MediaPipeのPoseLandmarkデータ
            frame_dim (Tuple[int, int]): フレームの寸法（幅, 高さ）
        
        Returns:
            Dict[str, Dict[str, float]]: ランドマークID: 座標データ の辞書
        """
        landmarks_dict = {}
        
        # MediaPipeポーズランドマークの名前と対応するIDのマッピング
        landmark_name_to_id = {
            0: "NOSE",
            1: "LEFT_EYE_INNER",
            2: "LEFT_EYE",
            3: "LEFT_EYE_OUTER",
            4: "RIGHT_EYE_INNER",
            5: "RIGHT_EYE",
            6: "RIGHT_EYE_OUTER",
            7: "LEFT_EAR",
            8: "RIGHT_EAR",
            9: "MOUTH_LEFT",
            10: "MOUTH_RIGHT",
            11: "LEFT_SHOULDER",
            12: "RIGHT_SHOULDER",
            13: "LEFT_ELBOW",
            14: "RIGHT_ELBOW",
            15: "LEFT_WRIST",
            16: "RIGHT_WRIST",
            17: "LEFT_PINKY",
            18: "RIGHT_PINKY",
            19: "LEFT_INDEX",
            20: "RIGHT_INDEX",
            21: "LEFT_THUMB",
            22: "RIGHT_THUMB",
            23: "LEFT_HIP",
            24: "RIGHT_HIP",
            25: "LEFT_KNEE",
            26: "RIGHT_KNEE",
            27: "LEFT_ANKLE",
            28: "RIGHT_ANKLE",
            29: "LEFT_HEEL",
            30: "RIGHT_HEEL",
            31: "LEFT_FOOT_INDEX",
            32: "RIGHT_FOOT_INDEX",
        }
        
        for idx, landmark in enumerate(pose_landmarks.landmark):
            # ランドマークのIDを取得
            landmark_id = landmark_name_to_id.get(idx, f"UNKNOWN_{idx}")
            
            # 座標をピクセル値に変換
            landmarks_dict[landmark_id] = {
                'x': landmark.x,
                'y': landmark.y,
                'z': landmark.z,
                'visibility': landmark.visibility
            }
        
        return landmarks_dict
    
    def _apply_pipeline(self) -> Dict[str, Any]:
        """
        6ステップのパイプラインを適用
        
        Returns:
            Dict[str, Any]: 処理後のデータ
        """
        print("ステップ1: ランドマークの欠損補間とvisibility重み付け")
        data = step01_cleanup.apply(self.landmarks_by_frame)
        
        print("ステップ2: Savitzky-Golayフィルタによる平滑化")
        data = step02_smooth.apply(data)
        
        print("ステップ3: 骨盤中心・肩幅=1の正規化")
        data = step03_normalize.apply(data)
        
        print("ステップ4: 時系列特徴量の計算")
        data = step04_temporal.apply(data)
        
        print("ステップ5: 窓幅多数決とHMM後処理")
        data = step05_voting.apply(data)
        
        print("ステップ6: ルールベース優先判定ゲート")
        data = step06_rulegate.apply(data)
        
        return data
    
    def _save_results(self, output_path: str) -> None:
        """
        処理結果をJSONファイルに保存
        
        Args:
            output_path (str): 出力ファイルのパス
        """
        # 出力ディレクトリがなければ作成
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 結果を保存
        with open(output_path, 'w') as f:
            json.dump(self.processed_data, f, indent=2)
        
        print(f"結果を保存しました: {output_path}")
    
    def get_summary(self) -> Dict[str, Any]:
        """
        分類結果のサマリを生成
        
        Returns:
            Dict[str, Any]: 分類結果のサマリ
        """
        if not self.processed_data:
            return {"error": "データが処理されていません"}
        
        # フレームIDを整数として取得し、順序付け
        frame_ids = sorted([int(k) for k in self.processed_data.keys() if k != '_metadata'])
        
        if not frame_ids:
            return {"error": "有効なフレームが見つかりませんでした"}
        
        # 各運動クラスのフレーム数をカウント
        class_counts = {}
        for frame_id in frame_ids:
            str_frame_id = str(frame_id)
            
            # 最終ラベルを取得
            if 'final_label' in self.processed_data[str_frame_id]:
                label = self.processed_data[str_frame_id]['final_label']
                if label in class_counts:
                    class_counts[label] += 1
                else:
                    class_counts[label] = 1
        
        # 最も多いクラスを特定
        dominant_class = max(class_counts.items(), key=lambda x: x[1]) if class_counts else ("unknown", 0)
        
        # サマリを作成
        summary = {
            "dominant_exercise": dominant_class[0],
            "confidence": dominant_class[1] / len(frame_ids) if frame_ids else 0,
            "class_distribution": {k: v / len(frame_ids) for k, v in class_counts.items()} if frame_ids else {},
            "frame_count": len(frame_ids),
            "processing_time": self.processed_data.get('_metadata', {}).get('total_processing_time', 0)
        }
        
        return summary
    
    def get_exercise_segments(self) -> List[Dict[str, Any]]:
        """
        連続したフレームを運動セグメントに分割
        
        Returns:
            List[Dict[str, Any]]: 運動セグメントのリスト
        """
        if not self.processed_data:
            return []
        
        # フレームIDを整数として取得し、順序付け
        frame_ids = sorted([int(k) for k in self.processed_data.keys() if k != '_metadata'])
        
        if not frame_ids:
            return []
        
        segments = []
        current_segment = {"exercise": "", "start_frame": 0, "end_frame": 0, "frames": []}
        
        for frame_id in frame_ids:
            str_frame_id = str(frame_id)
            
            # 最終ラベルを取得
            if 'final_label' in self.processed_data[str_frame_id]:
                label = self.processed_data[str_frame_id]['final_label']
                
                # 新しいセグメントの開始
                if not current_segment["exercise"]:
                    current_segment["exercise"] = label
                    current_segment["start_frame"] = frame_id
                    current_segment["frames"] = [frame_id]
                
                # 同じ運動の継続
                elif current_segment["exercise"] == label:
                    current_segment["frames"].append(frame_id)
                
                # 異なる運動への切り替え
                else:
                    # 現在のセグメントを完了
                    current_segment["end_frame"] = frame_id - 1
                    segments.append(current_segment)
                    
                    # 新しいセグメントを開始
                    current_segment = {
                        "exercise": label,
                        "start_frame": frame_id,
                        "end_frame": 0,
                        "frames": [frame_id]
                    }
        
        # 最後のセグメントを追加
        if current_segment["exercise"]:
            current_segment["end_frame"] = frame_ids[-1]
            segments.append(current_segment)
        
        return segments
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        パフォーマンス指標を計算（関節角度の動きなど）
        
        Returns:
            Dict[str, Any]: パフォーマンス指標
        """
        if not self.processed_data:
            return {"error": "データが処理されていません"}
        
        # フレームIDを整数として取得し、順序付け
        frame_ids = sorted([int(k) for k in self.processed_data.keys() if k != '_metadata'])
        
        if not frame_ids:
            return {"error": "有効なフレームが見つかりませんでした"}
        
        # セグメント分割
        segments = self.get_exercise_segments()
        
        metrics = {}
        
        for segment in segments:
            exercise = segment["exercise"]
            
            if exercise not in metrics:
                metrics[exercise] = {}
            
            # 各関節の角度範囲を計算
            joint_range = {}
            
            for frame_id in segment["frames"]:
                str_frame_id = str(frame_id)
                
                if 'joint_angles' in self.processed_data[str_frame_id]:
                    joint_angles = self.processed_data[str_frame_id]['joint_angles']
                    
                    for joint_name, angle in joint_angles.items():
                        if joint_name not in joint_range:
                            joint_range[joint_name] = {"min": angle, "max": angle}
                        else:
                            joint_range[joint_name]["min"] = min(joint_range[joint_name]["min"], angle)
                            joint_range[joint_name]["max"] = max(joint_range[joint_name]["max"], angle)
            
            # 関節の動作範囲を計算
            rom = {}  # Range of Motion
            for joint_name, range_data in joint_range.items():
                rom[joint_name] = range_data["max"] - range_data["min"]
            
            metrics[exercise]["joint_rom"] = rom
            metrics[exercise]["rep_count"] = self._estimate_rep_count(segment, exercise)
        
        return metrics
    
    def _estimate_rep_count(self, segment: Dict[str, Any], exercise: str) -> int:
        """
        セグメント内の反復回数を推定
        
        Args:
            segment (Dict[str, Any]): 運動セグメント
            exercise (str): 運動タイプ
        
        Returns:
            int: 推定反復回数
        """
        frames = segment["frames"]
        
        # 関節角度の時系列データを取得
        knee_angles = []
        hip_angles = []
        elbow_angles = []
        shoulder_angles = []
        
        for frame_id in frames:
            str_frame_id = str(frame_id)
            
            if 'joint_angles' in self.processed_data[str_frame_id]:
                joint_angles = self.processed_data[str_frame_id]['joint_angles']
                
                # 膝の角度（左右の平均）
                left_knee = joint_angles.get('left_knee', 0)
                right_knee = joint_angles.get('right_knee', 0)
                knee_angles.append((left_knee + right_knee) / 2)
                
                # 股関節の角度（左右の平均）
                left_hip = joint_angles.get('left_hip', 0)
                right_hip = joint_angles.get('right_hip', 0)
                hip_angles.append((left_hip + right_hip) / 2)
                
                # 肘の角度（左右の平均）
                left_elbow = joint_angles.get('left_elbow', 0)
                right_elbow = joint_angles.get('right_elbow', 0)
                elbow_angles.append((left_elbow + right_elbow) / 2)
                
                # 肩の角度（左右の平均）
                left_shoulder = joint_angles.get('left_shoulder', 0)
                right_shoulder = joint_angles.get('right_shoulder', 0)
                shoulder_angles.append((left_shoulder + right_shoulder) / 2)
        
        # 運動タイプに応じた反復回数の推定
        if exercise == 'squat':
            return self._count_peaks_and_valleys(knee_angles)
        elif exercise == 'pushup':
            return self._count_peaks_and_valleys(elbow_angles)
        elif exercise == 'deadlift':
            return self._count_peaks_and_valleys(hip_angles)
        elif exercise == 'overhead_press' or exercise == 'bench_press':
            return self._count_peaks_and_valleys(shoulder_angles)
        else:
            return 0
    
    def _count_peaks_and_valleys(self, angle_series: List[float]) -> int:
        """
        角度の時系列データからピークと谷を数えて反復回数を推定
        
        Args:
            angle_series (List[float]): 角度の時系列データ
        
        Returns:
            int: 推定反復回数
        """
        if len(angle_series) < 10:
            return 0
        
        # 移動平均を適用してノイズを低減
        window_size = min(15, len(angle_series) // 5)
        smoothed = np.convolve(angle_series, np.ones(window_size)/window_size, mode='valid')
        
        # ピークと谷を検出
        from scipy.signal import find_peaks
        
        # ピークの検出
        peaks, _ = find_peaks(smoothed, distance=window_size)
        
        # 谷の検出（-1を掛けて反転）
        valleys, _ = find_peaks(-smoothed, distance=window_size)
        
        # ピークと谷の数の少ない方を反復回数として採用
        return min(len(peaks), len(valleys))

def main():
    """メインの実行関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Stepwise Exercise Classifier Booster')
    parser.add_argument('--video', required=True, help='入力動画ファイルのパス')
    parser.add_argument('--output', default='enhanced_predictions.json', help='出力JSONファイルのパス')
    parser.add_argument('--config', default='config.yaml', help='設定ファイルのパス')
    
    args = parser.parse_args()
    
    # 分類器を初期化
    classifier = ExerciseClassifier(config_path=args.config)
    
    # 動画を処理
    try:
        processed_data = classifier.process_video(args.video, args.output)
        
        # サマリを表示
        summary = classifier.get_summary()
        print("\n分類結果のサマリ:")
        print(f"主要運動種目: {summary['dominant_exercise']}")
        print(f"信頼度: {summary['confidence']:.2f}")
        print(f"フレーム数: {summary['frame_count']}")
        print(f"処理時間: {summary['processing_time']:.2f}秒")
        
        # 運動セグメントを表示
        segments = classifier.get_exercise_segments()
        print(f"\n検出された運動セグメント: {len(segments)}個")
        for i, segment in enumerate(segments):
            print(f"セグメント{i+1}: {segment['exercise']} "
                  f"(フレーム{segment['start_frame']}～{segment['end_frame']})")
        
        # パフォーマンス指標を表示
        metrics = classifier.get_performance_metrics()
        print("\nパフォーマンス指標:")
        for exercise, data in metrics.items():
            if 'rep_count' in data:
                print(f"{exercise}: 推定反復回数 {data['rep_count']}回")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == '__main__':
    main()