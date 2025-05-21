import os
import cv2
import numpy as np
import json
import logging
from typing import Dict, List, Any
import mediapipe as mp

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MediaPipe設定
mp_pose = mp.solutions.pose

IDEAL_FORMS_PATH = 'ideal_forms/'

class TrainingAnalyzer:
    def __init__(self, exercise_type: str = 'squat'):
        self.exercise_type = exercise_type
        self.ideal_keypoints = self._load_ideal_keypoints()

    def _load_ideal_keypoints(self) -> Dict[str, Any]:
        path = os.path.join(IDEAL_FORMS_PATH, f"{self.exercise_type}_ideal.json")
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        logger.warning(f"Ideal form file not found: {path}. Using defaults.")
        return self._default_keypoints()

    def _default_keypoints(self) -> Dict[str, Any]:
        return {
            'squat': {'knee_angle_bottom': 90.0, 'hip_angle_bottom': 80.0},
            'bench_press': {'elbow_angle_bottom': 90.0},
            'deadlift': {'hip_angle_start': 70.0},
            'overhead_press': {'elbow_angle_bottom': 90.0}
        }.get(self.exercise_type, {})

    def analyze_video(self, video_path: str) -> Dict[str, Any]:
        if not os.path.exists(video_path):
            return {"error": "Video not found."}
        try:
            return self._generate_sample_analysis()
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            return {"error": str(e)}

    def _generate_sample_analysis(self) -> Dict[str, Any]:
        metrics = self._load_body_metrics()
        
        # エクササイズタイプに応じて異なる分析結果を返す
        if self.exercise_type == 'squat':
            analysis = {
                'exercise_type': 'squat',
                'exercise_name': 'スクワット',
                'form_score': 82,
                'depth_score': 75,
                'tempo_score': 85,
                'issues': ['膝が内側に入る', '背中が丸まる'],
                'strengths': ['姿勢が安定している'],
                'rep_count': 8,
                'body_metrics': metrics,
                'advice': self._generate_advice(['膝が内側に入る', '背中が丸まる'], 85)
            }
        elif self.exercise_type == 'bench_press':
            analysis = {
                'exercise_type': 'bench_press',
                'exercise_name': 'ベンチプレス',
                'form_score': 78,
                'depth_score': 80,
                'tempo_score': 72,
                'issues': ['手首が曲がっている', 'バーの軌道が一定でない'],
                'strengths': ['肘の角度が適切'],
                'rep_count': 6,
                'body_metrics': metrics,
                'advice': ['手首をまっすぐに保ちましょう', 'バーの軌道を胸の上で一定に保ちましょう']
            }
        elif self.exercise_type == 'deadlift':
            analysis = {
                'exercise_type': 'deadlift',
                'exercise_name': 'デッドリフト',
                'form_score': 75,
                'depth_score': 88,
                'tempo_score': 79,
                'issues': ['背中が丸まる', '頭の位置が低い'],
                'strengths': ['重心が安定している'],
                'rep_count': 5,
                'body_metrics': metrics,
                'advice': ['背中をまっすぐに保ちましょう', '前方を見て頭を適切な位置に保ちましょう']
            }
        elif self.exercise_type == 'overhead_press':
            analysis = {
                'exercise_type': 'overhead_press',
                'exercise_name': 'オーバーヘッドプレス',
                'form_score': 85,
                'depth_score': 82,
                'tempo_score': 80,
                'issues': ['腰が反りすぎている', 'バーの軌道がぶれる'],
                'strengths': ['肩の可動域が良好'],
                'rep_count': 7,
                'body_metrics': metrics,
                'advice': ['腹筋に力を入れて腰の反りを抑えましょう', 'バーは顔の前でまっすぐ上に押し上げましょう']
            }
        else:
            # デフォルト（不明なエクササイズタイプの場合）
            analysis = {
                'exercise_type': self.exercise_type,
                'exercise_name': '不明なエクササイズ',
                'form_score': 70,
                'depth_score': 70,
                'tempo_score': 70,
                'issues': ['姿勢に問題あり'],
                'strengths': ['基本的な動作が安定している'],
                'rep_count': 6,
                'body_metrics': metrics,
                'advice': ['正しいフォームを学習しましょう']
            }
        
        return analysis

    def _load_body_metrics(self) -> Dict[str, Any]:
        try:
            with open('results/sample_metrics.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load metrics: {e}")
            return {
                'user_height_cm': 170,
                'left_leg_cm': 91,
                'right_leg_cm': 90
            }

    def _generate_advice(self, issues: List[str], tempo_score: int) -> List[str]:
        advice = []
        for issue in issues:
            if '膝が内側' in issue:
                advice.append('膝をつま先方向に向けましょう。')
            if '背中が丸' in issue:
                advice.append('背中をまっすぐに保ちましょう。')
        if tempo_score < 80:
            advice.append('テンポを一定に保ちましょう。')
        return advice

    def save_results(self, results: Dict[str, Any], filename: str = 'results.json') -> str:
        os.makedirs('results', exist_ok=True)
        path = os.path.join('results', filename)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            return path
        except Exception as e:
            logger.error(f"Save failed: {e}")
            return ""
