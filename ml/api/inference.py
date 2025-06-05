"""
機械学習推論APIエンドポイント
リアルタイムでエクササイズを分類・評価
"""

import numpy as np
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import os
import sys

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from ml.models.exercise_classifier import ExerciseClassifier
from ml.data.preprocessor import PoseDataPreprocessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MLInferenceEngine:
    """機械学習推論エンジン"""
    
    def __init__(self):
        self.classifier = ExerciseClassifier()
        self.preprocessor = PoseDataPreprocessor()
        self.is_initialized = False
        
        # モデルの初期化
        self._initialize_models()
    
    def _initialize_models(self):
        """モデルを初期化"""
        try:
            # 学習済みモデルを読み込み
            self.classifier.load_model()
            self.is_initialized = True
            logger.info("MLモデルが初期化されました")
        except Exception as e:
            logger.warning(f"学習済みモデルの読み込みに失敗: {e}")
            logger.info("ルールベース分類器を使用します")
            self.is_initialized = True
    
    def analyze_pose(self, landmarks_data: Dict) -> Dict:
        """
        ポーズデータを分析してエクササイズを予測
        
        Args:
            landmarks_data: MediaPipeランドマークデータ
            
        Returns:
            分析結果
        """
        if not self.is_initialized:
            return self._error_response("MLエンジンが初期化されていません")
        
        try:
            # 特徴量抽出
            features = self.preprocessor.extract_pose_features(landmarks_data)
            
            if len(features) == 0:
                return self._error_response("特徴量の抽出に失敗しました")
            
            # 予測実行
            features_array = features.reshape(1, -1)  # バッチ次元を追加
            predictions, confidences = self.classifier.predict(features_array)
            
            # 結果をフォーマット
            result = {
                'success': True,
                'exercise_type': predictions[0] if predictions else 'unknown',
                'confidence': float(confidences[0]) if confidences else 0.0,
                'timestamp': datetime.now().isoformat(),
                'feature_count': len(features),
                'analysis': self._generate_form_analysis(landmarks_data, predictions[0] if predictions else 'unknown')
            }
            
            # 信頼度に基づく品質評価
            if result['confidence'] > 0.8:
                result['quality'] = 'excellent'
            elif result['confidence'] > 0.6:
                result['quality'] = 'good'
            elif result['confidence'] > 0.4:
                result['quality'] = 'fair'
            else:
                result['quality'] = 'poor'
            
            return result
            
        except Exception as e:
            logger.error(f"ポーズ分析エラー: {e}")
            return self._error_response(f"分析中にエラーが発生: {str(e)}")
    
    def _generate_form_analysis(self, landmarks_data: Dict, exercise_type: str) -> Dict:
        """フォーム分析を生成"""
        analysis = {
            'form_score': 0,
            'feedback': [],
            'corrections': []
        }
        
        try:
            if exercise_type == 'squat':
                analysis = self._analyze_squat_form(landmarks_data)
            elif exercise_type == 'push_up':
                analysis = self._analyze_pushup_form(landmarks_data)
            elif exercise_type == 'deadlift':
                analysis = self._analyze_deadlift_form(landmarks_data)
            elif exercise_type == 'plank':
                analysis = self._analyze_plank_form(landmarks_data)
            else:
                analysis['form_score'] = 70  # デフォルトスコア
                analysis['feedback'].append("一般的なフォームチェックを実行中")
                
        except Exception as e:
            logger.warning(f"フォーム分析エラー: {e}")
            analysis['form_score'] = 50
            analysis['feedback'].append("フォーム分析で問題が発生しました")
        
        return analysis
    
    def _analyze_squat_form(self, landmarks: Dict) -> Dict:
        """スクワットフォーム分析"""
        analysis = {'form_score': 0, 'feedback': [], 'corrections': []}
        score = 100
        
        try:
            # 膝とつま先の方向チェック
            if 'LEFT_KNEE' in landmarks and 'LEFT_ANKLE' in landmarks:
                knee_x = landmarks['LEFT_KNEE'].get('x', 0)
                ankle_x = landmarks['LEFT_ANKLE'].get('x', 0)
                
                if abs(knee_x - ankle_x) > 0.1:  # 閾値は調整が必要
                    score -= 15
                    analysis['feedback'].append("膝がつま先の方向と一致していません")
                    analysis['corrections'].append("膝をつま先と同じ方向に向けてください")
            
            # 背中の角度チェック
            if all(key in landmarks for key in ['NOSE', 'LEFT_SHOULDER', 'LEFT_HIP']):
                # 簡単な姿勢チェック
                shoulder_y = landmarks['LEFT_SHOULDER'].get('y', 0)
                hip_y = landmarks['LEFT_HIP'].get('y', 0)
                
                if abs(shoulder_y - hip_y) < 0.1:  # 体が水平すぎる
                    score -= 10
                    analysis['feedback'].append("上体が前傾しすぎています")
                    analysis['corrections'].append("胸を張って背筋を伸ばしてください")
            
            # スクワットの深さチェック
            if 'LEFT_HIP' in landmarks and 'LEFT_KNEE' in landmarks:
                hip_y = landmarks['LEFT_HIP'].get('y', 0)
                knee_y = landmarks['LEFT_KNEE'].get('y', 0)
                
                if hip_y < knee_y:  # 十分な深さ
                    analysis['feedback'].append("良い深さまでしゃがめています")
                else:
                    score -= 20
                    analysis['feedback'].append("もう少し深くしゃがんでください")
                    analysis['corrections'].append("太ももが地面と平行になるまでしゃがんでください")
            
        except Exception as e:
            logger.warning(f"スクワット分析エラー: {e}")
            score = 50
        
        analysis['form_score'] = max(0, score)
        return analysis
    
    def _analyze_pushup_form(self, landmarks: Dict) -> Dict:
        """プッシュアップフォーム分析"""
        analysis = {'form_score': 0, 'feedback': [], 'corrections': []}
        score = 100
        
        try:
            # 体のライン（プランクポジション）チェック
            if all(key in landmarks for key in ['NOSE', 'LEFT_SHOULDER', 'LEFT_HIP', 'LEFT_ANKLE']):
                # 各部位のY座標を取得
                nose_y = landmarks['NOSE'].get('y', 0)
                shoulder_y = landmarks['LEFT_SHOULDER'].get('y', 0)
                hip_y = landmarks['LEFT_HIP'].get('y', 0)
                ankle_y = landmarks['LEFT_ANKLE'].get('y', 0)
                
                # 体のラインの直線性をチェック
                body_alignment = abs((shoulder_y + hip_y) / 2 - (nose_y + ankle_y) / 2)
                
                if body_alignment > 0.05:  # 閾値は調整が必要
                    score -= 15
                    analysis['feedback'].append("体のラインが真っ直ぐではありません")
                    analysis['corrections'].append("頭からかかとまで一直線を保ってください")
            
            # 腕の位置チェック
            if 'LEFT_WRIST' in landmarks and 'LEFT_SHOULDER' in landmarks:
                wrist_x = landmarks['LEFT_WRIST'].get('x', 0)
                shoulder_x = landmarks['LEFT_SHOULDER'].get('x', 0)
                
                if abs(wrist_x - shoulder_x) > 0.15:  # 手が肩幅より大きく外れている
                    score -= 10
                    analysis['feedback'].append("手の位置を調整してください")
                    analysis['corrections'].append("手は肩幅程度に開いて配置してください")
            
        except Exception as e:
            logger.warning(f"プッシュアップ分析エラー: {e}")
            score = 50
        
        analysis['form_score'] = max(0, score)
        return analysis
    
    def _analyze_deadlift_form(self, landmarks: Dict) -> Dict:
        """デッドリフトフォーム分析"""
        analysis = {'form_score': 0, 'feedback': [], 'corrections': []}
        score = 100
        
        try:
            # 背中の丸まりチェック
            if all(key in landmarks for key in ['NOSE', 'LEFT_SHOULDER', 'LEFT_HIP']):
                # 簡単な背中の角度チェック
                analysis['feedback'].append("背中の姿勢を確認中")
            
            # 膝とつま先の位置関係
            if 'LEFT_KNEE' in landmarks and 'LEFT_ANKLE' in landmarks:
                analysis['feedback'].append("膝とつま先の位置関係を確認中")
            
        except Exception as e:
            logger.warning(f"デッドリフト分析エラー: {e}")
            score = 50
        
        analysis['form_score'] = max(0, score)
        return analysis
    
    def _analyze_plank_form(self, landmarks: Dict) -> Dict:
        """プランクフォーム分析"""
        analysis = {'form_score': 0, 'feedback': [], 'corrections': []}
        score = 100
        
        try:
            # 体のライン（一直線）チェック
            if all(key in landmarks for key in ['NOSE', 'LEFT_SHOULDER', 'LEFT_HIP', 'LEFT_ANKLE']):
                analysis['feedback'].append("体の一直線ラインを確認中")
            
            # 腰の位置チェック
            if 'LEFT_HIP' in landmarks and 'LEFT_SHOULDER' in landmarks:
                hip_y = landmarks['LEFT_HIP'].get('y', 0)
                shoulder_y = landmarks['LEFT_SHOULDER'].get('y', 0)
                
                if hip_y > shoulder_y + 0.1:  # 腰が上がりすぎ
                    score -= 20
                    analysis['feedback'].append("腰が上がりすぎています")
                    analysis['corrections'].append("腰を下げて体を一直線に保ってください")
                elif hip_y < shoulder_y - 0.1:  # 腰が下がりすぎ
                    score -= 20
                    analysis['feedback'].append("腰が下がりすぎています")
                    analysis['corrections'].append("腰を上げて体を一直線に保ってください")
                else:
                    analysis['feedback'].append("良い姿勢を保てています")
            
        except Exception as e:
            logger.warning(f"プランク分析エラー: {e}")
            score = 50
        
        analysis['form_score'] = max(0, score)
        return analysis
    
    def batch_analyze(self, session_data: List[Dict]) -> Dict:
        """
        セッション全体のバッチ分析
        
        Args:
            session_data: フレームデータのリスト
            
        Returns:
            セッション分析結果
        """
        if not session_data:
            return self._error_response("分析するデータがありません")
        
        results = []
        exercise_counts = {}
        total_confidence = 0
        
        for frame_data in session_data:
            if 'landmarks' in frame_data:
                result = self.analyze_pose(frame_data['landmarks'])
                results.append(result)
                
                if result['success']:
                    exercise_type = result['exercise_type']
                    exercise_counts[exercise_type] = exercise_counts.get(exercise_type, 0) + 1
                    total_confidence += result['confidence']
        
        if not results:
            return self._error_response("有効なフレームデータがありません")
        
        # セッション統計
        avg_confidence = total_confidence / len(results) if results else 0
        dominant_exercise = max(exercise_counts.items(), key=lambda x: x[1])[0] if exercise_counts else 'unknown'
        
        session_analysis = {
            'success': True,
            'session_summary': {
                'total_frames': len(results),
                'dominant_exercise': dominant_exercise,
                'average_confidence': avg_confidence,
                'exercise_distribution': exercise_counts,
                'session_quality': 'excellent' if avg_confidence > 0.8 else 'good' if avg_confidence > 0.6 else 'fair'
            },
            'frame_results': results,
            'timestamp': datetime.now().isoformat()
        }
        
        return session_analysis
    
    def _error_response(self, message: str) -> Dict:
        """エラーレスポンスを生成"""
        return {
            'success': False,
            'error': message,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_model_info(self) -> Dict:
        """モデル情報を取得"""
        info = {
            'is_initialized': self.is_initialized,
            'model_type': 'machine_learning' if hasattr(self.classifier, 'model') and self.classifier.model else 'rule_based',
            'supported_exercises': self.classifier.exercise_labels,
            'timestamp': datetime.now().isoformat()
        }
        
        if hasattr(self.classifier, 'training_history') and self.classifier.training_history:
            info['last_training'] = self.classifier.training_history[-1]
        
        return info


# 使用例
if __name__ == "__main__":
    # 推論エンジンのテスト
    engine = MLInferenceEngine()
    
    # サンプルランドマークデータ
    sample_landmarks = {
        'LEFT_SHOULDER': {'x': 0.5, 'y': 0.3, 'z': 0.1, 'visibility': 0.9},
        'RIGHT_SHOULDER': {'x': 0.4, 'y': 0.3, 'z': 0.1, 'visibility': 0.9},
        'LEFT_HIP': {'x': 0.5, 'y': 0.6, 'z': 0.1, 'visibility': 0.9},
        'RIGHT_HIP': {'x': 0.4, 'y': 0.6, 'z': 0.1, 'visibility': 0.9},
        'LEFT_KNEE': {'x': 0.5, 'y': 0.8, 'z': 0.2, 'visibility': 0.8},
        'RIGHT_KNEE': {'x': 0.4, 'y': 0.8, 'z': 0.2, 'visibility': 0.8},
        'LEFT_ANKLE': {'x': 0.5, 'y': 1.0, 'z': 0.3, 'visibility': 0.7},
        'RIGHT_ANKLE': {'x': 0.4, 'y': 1.0, 'z': 0.3, 'visibility': 0.7}
    }
    
    # 分析実行
    result = engine.analyze_pose(sample_landmarks)
    print(f"分析結果: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    # モデル情報取得
    model_info = engine.get_model_info()
    print(f"モデル情報: {json.dumps(model_info, indent=2, ensure_ascii=False)}")