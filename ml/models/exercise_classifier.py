"""
エクササイズ分類器
ポーズデータからエクササイズの種類を予測
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import json
import logging
import os
from datetime import datetime

# 軽量な機械学習ライブラリを使用（Replitでの利用を考慮）
try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.metrics import classification_report, confusion_matrix
    import joblib
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logging.warning("scikit-learnが利用できません。基本的な分類器を使用します。")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExerciseClassifier:
    """エクササイズ分類器"""
    
    def __init__(self, model_path: str = "ml/models/exercise_classifier.pkl"):
        self.model_path = model_path
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.feature_importance = None
        self.training_history = []
        
        # エクササイズラベルの定義
        self.exercise_labels = [
            'squat', 'push_up', 'deadlift', 'bench_press', 'overhead_press',
            'bicep_curl', 'tricep_extension', 'plank', 'lunge', 'pull_up'
        ]
        
        if ML_AVAILABLE:
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            self.scaler = StandardScaler()
            self.label_encoder = LabelEncoder()
        
    def prepare_training_data(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        学習用データの準備
        
        Args:
            data: 前処理済みのデータフレーム
            
        Returns:
            特徴量とラベルのタプル
        """
        if data.empty:
            raise ValueError("データが空です")
        
        # 特徴量列を抽出
        feature_cols = [col for col in data.columns if col.startswith('feature_')]
        X = data[feature_cols].values
        
        # ラベルを抽出
        y = data['exercise_type'].values
        
        # 欠損値の処理
        X = np.nan_to_num(X, nan=0.0)
        
        # ラベルエンコーディング
        if ML_AVAILABLE and self.label_encoder is not None:
            y = self.label_encoder.fit_transform(y)
        
        logger.info(f"学習データ形状: X={X.shape}, y={y.shape}")
        return X, y
    
    def train(self, X: np.ndarray, y: np.ndarray, validation_split: float = 0.2):
        """
        モデルを学習
        
        Args:
            X: 特徴量
            y: ラベル
            validation_split: 検証用データの割合
        """
        if not ML_AVAILABLE:
            logger.warning("機械学習ライブラリが利用できません")
            return
        
        # データ分割
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=validation_split, random_state=42, stratify=y
        )
        
        # 特徴量の正規化
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        
        # モデル学習
        logger.info("モデル学習を開始...")
        self.model.fit(X_train_scaled, y_train)
        
        # 検証
        train_score = self.model.score(X_train_scaled, y_train)
        val_score = self.model.score(X_val_scaled, y_val)
        
        logger.info(f"学習スコア: {train_score:.4f}")
        logger.info(f"検証スコア: {val_score:.4f}")
        
        # クロスバリデーション
        cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=5)
        logger.info(f"CV平均スコア: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        
        # 特徴量重要度を保存
        self.feature_importance = self.model.feature_importances_
        
        # 学習履歴を記録
        self.training_history.append({
            'timestamp': datetime.now().isoformat(),
            'train_score': train_score,
            'val_score': val_score,
            'cv_score_mean': cv_scores.mean(),
            'cv_score_std': cv_scores.std(),
            'n_samples': len(X_train)
        })
        
        # 詳細な評価レポート
        y_pred = self.model.predict(X_val_scaled)
        report = classification_report(y_val, y_pred, target_names=self.label_encoder.classes_)
        logger.info(f"分類レポート:\n{report}")
    
    def predict(self, X: np.ndarray) -> Tuple[List[str], List[float]]:
        """
        予測を実行
        
        Args:
            X: 特徴量
            
        Returns:
            予測ラベルと確信度のタプル
        """
        if not ML_AVAILABLE or self.model is None:
            # フォールバック: ルールベース分類
            return self._rule_based_predict(X)
        
        try:
            # 特徴量の正規化
            X_scaled = self.scaler.transform(X)
            
            # 予測
            predictions = self.model.predict(X_scaled)
            probabilities = self.model.predict_proba(X_scaled)
            
            # ラベルをデコード
            predicted_labels = self.label_encoder.inverse_transform(predictions)
            confidence_scores = np.max(probabilities, axis=1)
            
            return predicted_labels.tolist(), confidence_scores.tolist()
            
        except Exception as e:
            logger.error(f"予測エラー: {e}")
            return self._rule_based_predict(X)
    
    def _rule_based_predict(self, X: np.ndarray) -> Tuple[List[str], List[float]]:
        """
        ルールベース予測（フォールバック）
        
        Args:
            X: 特徴量
            
        Returns:
            予測ラベルと確信度
        """
        predictions = []
        confidences = []
        
        for features in X:
            # 簡単なルールベース分類
            # 実際の実装では、より洗練されたルールを使用
            if len(features) > 10:
                # 上半身の動きが大きい場合
                if features[4] > 0.5:  # 例: 肩の角度
                    pred = 'push_up'
                    conf = 0.7
                # 下半身の動きが大きい場合
                elif features[8] > 0.5:  # 例: 股関節の角度
                    pred = 'squat'
                    conf = 0.6
                else:
                    pred = 'plank'
                    conf = 0.5
            else:
                pred = 'unknown'
                conf = 0.3
            
            predictions.append(pred)
            confidences.append(conf)
        
        return predictions, confidences
    
    def save_model(self, custom_path: Optional[str] = None):
        """モデルを保存"""
        if not ML_AVAILABLE:
            logger.warning("モデル保存機能が利用できません")
            return
        
        save_path = custom_path or self.model_path
        
        try:
            # ディレクトリ作成
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # モデルデータをまとめて保存
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'label_encoder': self.label_encoder,
                'feature_importance': self.feature_importance,
                'training_history': self.training_history,
                'exercise_labels': self.exercise_labels
            }
            
            joblib.dump(model_data, save_path)
            logger.info(f"モデルを保存しました: {save_path}")
            
        except Exception as e:
            logger.error(f"モデル保存エラー: {e}")
    
    def load_model(self, custom_path: Optional[str] = None):
        """モデルを読み込み"""
        if not ML_AVAILABLE:
            logger.warning("モデル読み込み機能が利用できません")
            return
        
        load_path = custom_path or self.model_path
        
        try:
            if os.path.exists(load_path):
                model_data = joblib.load(load_path)
                
                self.model = model_data['model']
                self.scaler = model_data['scaler']
                self.label_encoder = model_data['label_encoder']
                self.feature_importance = model_data.get('feature_importance')
                self.training_history = model_data.get('training_history', [])
                self.exercise_labels = model_data.get('exercise_labels', self.exercise_labels)
                
                logger.info(f"モデルを読み込みました: {load_path}")
            else:
                logger.warning(f"モデルファイルが見つかりません: {load_path}")
                
        except Exception as e:
            logger.error(f"モデル読み込みエラー: {e}")
    
    def get_feature_importance(self) -> Dict[str, float]:
        """特徴量重要度を取得"""
        if self.feature_importance is None:
            return {}
        
        importance_dict = {}
        for i, importance in enumerate(self.feature_importance):
            importance_dict[f'feature_{i}'] = importance
        
        return importance_dict
    
    def evaluate_model(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict:
        """モデルの評価"""
        if not ML_AVAILABLE or self.model is None:
            return {}
        
        try:
            X_test_scaled = self.scaler.transform(X_test)
            
            # 予測
            y_pred = self.model.predict(X_test_scaled)
            
            # 評価指標の計算
            accuracy = self.model.score(X_test_scaled, y_test)
            
            # 分類レポート
            report = classification_report(y_test, y_pred, output_dict=True)
            
            return {
                'accuracy': accuracy,
                'classification_report': report,
                'confusion_matrix': confusion_matrix(y_test, y_pred).tolist()
            }
            
        except Exception as e:
            logger.error(f"評価エラー: {e}")
            return {}


# 使用例とテスト
if __name__ == "__main__":
    # サンプルデータでテスト
    classifier = ExerciseClassifier()
    
    # ダミーデータ作成
    np.random.seed(42)
    n_samples = 1000
    n_features = 50
    
    X_dummy = np.random.randn(n_samples, n_features)
    y_dummy = np.random.choice(['squat', 'push_up', 'plank'], n_samples)
    
    # データフレーム作成
    data_dict = {'exercise_type': y_dummy}
    for i in range(n_features):
        data_dict[f'feature_{i}'] = X_dummy[:, i]
    
    df_dummy = pd.DataFrame(data_dict)
    
    if ML_AVAILABLE:
        try:
            # 学習データ準備
            X, y = classifier.prepare_training_data(df_dummy)
            
            # 学習
            classifier.train(X, y)
            
            # 予測テスト
            test_X = X[:5]  # 最初の5サンプル
            predictions, confidences = classifier.predict(test_X)
            
            print(f"予測結果: {predictions}")
            print(f"確信度: {confidences}")
            
            # モデル保存
            classifier.save_model()
            
        except Exception as e:
            logger.error(f"テスト実行エラー: {e}")
    else:
        print("機械学習ライブラリが利用できないため、ルールベース分類器を使用します。")