"""
モデル学習スクリプト
実際のトレーニングデータからエクササイズ分類器を学習
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import argparse

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from ml.models.exercise_classifier import ExerciseClassifier
from ml.data.preprocessor import PoseDataPreprocessor, WorkoutDataCollector
from utils.workout_models import WorkoutDatabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelTrainer:
    """モデル学習管理クラス"""
    
    def __init__(self, data_dir: str = "ml/data"):
        self.data_dir = data_dir
        self.raw_data_dir = os.path.join(data_dir, "raw")
        self.processed_data_dir = os.path.join(data_dir, "processed")
        
        # ディレクトリ作成
        os.makedirs(self.raw_data_dir, exist_ok=True)
        os.makedirs(self.processed_data_dir, exist_ok=True)
        
        self.preprocessor = PoseDataPreprocessor()
        self.classifier = ExerciseClassifier()
        self.workout_db = WorkoutDatabase()
    
    def collect_training_data(self, days: int = 30) -> str:
        """
        トレーニングデータを収集
        
        Args:
            days: 収集する日数
            
        Returns:
            保存されたファイルパス
        """
        logger.info(f"過去{days}日のトレーニングデータを収集中...")
        
        # 実際のワークアウトデータを取得
        # これは既存のワークアウトデータベースから実データを収集
        try:
            # サンプルデータの生成（実際の運用では実データを使用）
            sample_data = self._generate_sample_training_data()
            
            # データを保存
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(self.raw_data_dir, f"training_data_{timestamp}.json")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(sample_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"トレーニングデータを保存: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"データ収集エラー: {e}")
            raise
    
    def _generate_sample_training_data(self) -> Dict:
        """
        サンプル学習データを生成
        実際の運用では実際のポーズデータを使用
        """
        import numpy as np
        
        sample_data = {}
        exercises = ['squat', 'push_up', 'plank', 'deadlift', 'bicep_curl']
        
        for i, exercise in enumerate(exercises):
            for frame in range(50):  # 各エクササイズ50フレーム
                frame_id = f"{exercise}_{frame:03d}"
                
                # ランダムなランドマークデータを生成
                landmarks = {}
                landmark_names = [
                    'NOSE', 'LEFT_SHOULDER', 'RIGHT_SHOULDER', 'LEFT_ELBOW', 'RIGHT_ELBOW',
                    'LEFT_WRIST', 'RIGHT_WRIST', 'LEFT_HIP', 'RIGHT_HIP', 'LEFT_KNEE',
                    'RIGHT_KNEE', 'LEFT_ANKLE', 'RIGHT_ANKLE'
                ]
                
                for landmark_name in landmark_names:
                    # エクササイズに応じた特徴的な座標を生成
                    base_x = 0.4 + 0.2 * np.random.random()
                    base_y = 0.3 + 0.4 * np.random.random()
                    base_z = 0.1 * np.random.random()
                    
                    # エクササイズ固有の調整
                    if exercise == 'squat' and 'KNEE' in landmark_name:
                        base_y += 0.1  # 膝を下げる
                    elif exercise == 'push_up' and 'WRIST' in landmark_name:
                        base_y += 0.2  # 手を床に近づける
                    elif exercise == 'plank':
                        base_y = 0.5  # 水平姿勢
                    
                    landmarks[landmark_name] = {
                        'x': base_x,
                        'y': base_y,
                        'z': base_z,
                        'visibility': 0.8 + 0.2 * np.random.random()
                    }
                
                sample_data[frame_id] = {
                    'landmarks': landmarks,
                    'exercise_type': exercise,
                    'timestamp': datetime.now().timestamp() + frame,
                    'rep_count': frame // 10,  # 10フレームで1回
                    'form_score': 70 + 30 * np.random.random()
                }
        
        return sample_data
    
    def preprocess_data(self, raw_data_path: str) -> str:
        """
        生データを前処理
        
        Args:
            raw_data_path: 生データファイルパス
            
        Returns:
            処理済みデータファイルパス
        """
        logger.info(f"データ前処理開始: {raw_data_path}")
        
        try:
            # 生データ読み込み
            with open(raw_data_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            # データフレームに変換
            df = self.preprocessor.process_workout_session(raw_data)
            
            # 処理済みデータを保存
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            processed_path = os.path.join(self.processed_data_dir, f"processed_data_{timestamp}.csv")
            
            self.preprocessor.save_processed_data(df, processed_path)
            
            logger.info(f"前処理完了: {processed_path}")
            logger.info(f"データ形状: {df.shape}")
            logger.info(f"エクササイズ分布: {df['exercise_type'].value_counts().to_dict()}")
            
            return processed_path
            
        except Exception as e:
            logger.error(f"前処理エラー: {e}")
            raise
    
    def train_model(self, processed_data_path: str, validation_split: float = 0.2) -> Dict:
        """
        モデルを学習
        
        Args:
            processed_data_path: 処理済みデータパス
            validation_split: 検証用データの割合
            
        Returns:
            学習結果
        """
        logger.info(f"モデル学習開始: {processed_data_path}")
        
        try:
            # データ読み込み
            df = self.preprocessor.load_processed_data(processed_data_path)
            
            if df.empty:
                raise ValueError("データが空です")
            
            # 学習データ準備
            X, y = self.classifier.prepare_training_data(df)
            
            # モデル学習
            self.classifier.train(X, y, validation_split)
            
            # モデル保存
            self.classifier.save_model()
            
            # 特徴量重要度を取得
            feature_importance = self.classifier.get_feature_importance()
            
            # 学習結果をまとめ
            training_result = {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'data_shape': list(X.shape),
                'unique_exercises': len(set(y)) if hasattr(y, '__len__') else 0,
                'model_saved': True,
                'feature_importance_top10': dict(list(sorted(feature_importance.items(), 
                                                            key=lambda x: x[1], 
                                                            reverse=True))[:10]) if feature_importance else {},
                'training_history': self.classifier.training_history[-1] if self.classifier.training_history else {}
            }
            
            logger.info("モデル学習完了")
            logger.info(f"学習結果: {json.dumps(training_result, indent=2, ensure_ascii=False)}")
            
            return training_result
            
        except Exception as e:
            logger.error(f"学習エラー: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def evaluate_model(self, test_data_path: Optional[str] = None) -> Dict:
        """
        モデルを評価
        
        Args:
            test_data_path: テストデータパス（Noneの場合は学習データの一部を使用）
            
        Returns:
            評価結果
        """
        logger.info("モデル評価開始")
        
        try:
            if test_data_path and os.path.exists(test_data_path):
                df_test = self.preprocessor.load_processed_data(test_data_path)
                X_test, y_test = self.classifier.prepare_training_data(df_test)
            else:
                logger.info("テストデータが指定されていません。学習データを使用します。")
                # 実際の運用では別途テストデータを用意
                return {'message': 'テストデータが必要です'}
            
            # 評価実行
            evaluation = self.classifier.evaluate_model(X_test, y_test)
            
            evaluation['timestamp'] = datetime.now().isoformat()
            evaluation['success'] = True
            
            logger.info(f"評価完了: {evaluation}")
            return evaluation
            
        except Exception as e:
            logger.error(f"評価エラー: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def full_training_pipeline(self, days: int = 30) -> Dict:
        """
        完全な学習パイプラインを実行
        
        Args:
            days: データ収集日数
            
        Returns:
            パイプライン実行結果
        """
        logger.info("完全な学習パイプラインを開始")
        
        pipeline_result = {
            'pipeline_start': datetime.now().isoformat(),
            'steps': {}
        }
        
        try:
            # ステップ1: データ収集
            logger.info("ステップ1: データ収集")
            raw_data_path = self.collect_training_data(days)
            pipeline_result['steps']['data_collection'] = {
                'success': True,
                'output_path': raw_data_path
            }
            
            # ステップ2: データ前処理
            logger.info("ステップ2: データ前処理")
            processed_data_path = self.preprocess_data(raw_data_path)
            pipeline_result['steps']['preprocessing'] = {
                'success': True,
                'output_path': processed_data_path
            }
            
            # ステップ3: モデル学習
            logger.info("ステップ3: モデル学習")
            training_result = self.train_model(processed_data_path)
            pipeline_result['steps']['training'] = training_result
            
            # パイプライン完了
            pipeline_result['pipeline_end'] = datetime.now().isoformat()
            pipeline_result['success'] = True
            
            logger.info("学習パイプライン完了")
            
        except Exception as e:
            logger.error(f"パイプラインエラー: {e}")
            pipeline_result['success'] = False
            pipeline_result['error'] = str(e)
            pipeline_result['pipeline_end'] = datetime.now().isoformat()
        
        return pipeline_result


def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(description='機械学習モデル学習スクリプト')
    parser.add_argument('--days', type=int, default=30, help='データ収集日数')
    parser.add_argument('--data-path', type=str, help='既存の処理済みデータパス')
    parser.add_argument('--eval-only', action='store_true', help='評価のみ実行')
    
    args = parser.parse_args()
    
    trainer = ModelTrainer()
    
    if args.eval_only:
        # 評価のみ実行
        result = trainer.evaluate_model()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.data_path:
        # 既存データで学習
        result = trainer.train_model(args.data_path)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        # 完全パイプライン実行
        result = trainer.full_training_pipeline(args.days)
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()