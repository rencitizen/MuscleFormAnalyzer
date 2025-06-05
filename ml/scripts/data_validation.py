"""
データ品質検証とバリデーション
前処理パイプラインの結果を検証し、品質レポートを生成
"""

import numpy as np
import json
import logging
import os
import csv
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # GUI不要のバックエンドを使用
import matplotlib.pyplot as plt
import seaborn as sns

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataQualityValidator:
    """データ品質検証クラス"""
    
    def __init__(self):
        self.quality_metrics = {}
        self.validation_results = {}
        
    def validate_processed_data(self, data_dir: str = 'ml/data/processed') -> Dict[str, Any]:
        """処理済みデータの品質を検証"""
        validation_report = {
            'timestamp': datetime.now().isoformat(),
            'data_directory': data_dir,
            'datasets': {},
            'overall_quality': {},
            'recommendations': []
        }
        
        # 各データセットを検証
        datasets = ['train', 'val', 'test']
        
        for dataset_name in datasets:
            csv_path = os.path.join(data_dir, f'{dataset_name}.csv')
            
            if os.path.exists(csv_path):
                logger.info(f"{dataset_name}データセットを検証中...")
                dataset_validation = self._validate_dataset(csv_path, dataset_name)
                validation_report['datasets'][dataset_name] = dataset_validation
            else:
                logger.warning(f"{dataset_name}データセットが見つかりません: {csv_path}")
                validation_report['datasets'][dataset_name] = {'status': 'missing'}
        
        # 全体的な品質評価
        validation_report['overall_quality'] = self._calculate_overall_quality(validation_report['datasets'])
        
        # 推奨事項の生成
        validation_report['recommendations'] = self._generate_recommendations(validation_report)
        
        # レポートを保存
        report_path = os.path.join(data_dir, 'validation_report.json')
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(validation_report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"検証レポートを保存: {report_path}")
        
        # 可視化レポートを生成
        self._generate_visual_report(validation_report, data_dir)
        
        return validation_report
    
    def _validate_dataset(self, csv_path: str, dataset_name: str) -> Dict[str, Any]:
        """個別データセットの検証"""
        validation_result = {
            'status': 'unknown',
            'sample_count': 0,
            'feature_count': 0,
            'missing_values': {},
            'data_quality': {},
            'distribution_analysis': {},
            'outlier_analysis': {},
            'class_balance': {}
        }
        
        try:
            # CSVファイルを読み込み
            data = self._load_csv_data(csv_path)
            
            if not data:
                validation_result['status'] = 'empty'
                return validation_result
            
            validation_result['status'] = 'processed'
            validation_result['sample_count'] = len(data)
            
            # 特徴量列を識別
            feature_columns = [col for col in data[0].keys() if col.endswith('_normalized') or col.startswith('angle_') or col.startswith('distance_')]
            validation_result['feature_count'] = len(feature_columns)
            
            # 欠損値の検証
            missing_analysis = self._analyze_missing_values(data, feature_columns)
            validation_result['missing_values'] = missing_analysis
            
            # データ品質の検証
            quality_analysis = self._analyze_data_quality(data, feature_columns)
            validation_result['data_quality'] = quality_analysis
            
            # 分布の分析
            distribution_analysis = self._analyze_distributions(data, feature_columns)
            validation_result['distribution_analysis'] = distribution_analysis
            
            # 外れ値の検出
            outlier_analysis = self._detect_outliers(data, feature_columns)
            validation_result['outlier_analysis'] = outlier_analysis
            
            # クラスバランスの分析
            class_balance = self._analyze_class_balance(data)
            validation_result['class_balance'] = class_balance
            
        except Exception as e:
            logger.error(f"データセット検証エラー {dataset_name}: {e}")
            validation_result['status'] = 'error'
            validation_result['error_message'] = str(e)
        
        return validation_result
    
    def _load_csv_data(self, csv_path: str) -> List[Dict[str, Any]]:
        """CSVデータを読み込み"""
        data = []
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    # 数値列を適切な型に変換
                    converted_row = {}
                    for key, value in row.items():
                        try:
                            # 数値として解釈可能な場合は変換
                            if value and value != '':
                                converted_row[key] = float(value)
                            else:
                                converted_row[key] = value
                        except ValueError:
                            converted_row[key] = value
                    
                    data.append(converted_row)
                    
        except Exception as e:
            logger.error(f"CSV読み込みエラー {csv_path}: {e}")
            return []
        
        return data
    
    def _analyze_missing_values(self, data: List[Dict], feature_columns: List[str]) -> Dict[str, Any]:
        """欠損値の分析"""
        missing_analysis = {
            'total_features': len(feature_columns),
            'features_with_missing': 0,
            'missing_percentages': {},
            'worst_features': []
        }
        
        for feature in feature_columns:
            missing_count = 0
            total_count = len(data)
            
            for row in data:
                value = row.get(feature, None)
                if value is None or value == '' or (isinstance(value, float) and np.isnan(value)):
                    missing_count += 1
            
            missing_percentage = (missing_count / total_count) * 100 if total_count > 0 else 0
            missing_analysis['missing_percentages'][feature] = missing_percentage
            
            if missing_percentage > 0:
                missing_analysis['features_with_missing'] += 1
        
        # 欠損値が多い特徴量をリストアップ
        sorted_missing = sorted(missing_analysis['missing_percentages'].items(), 
                               key=lambda x: x[1], reverse=True)
        missing_analysis['worst_features'] = sorted_missing[:10]
        
        return missing_analysis
    
    def _analyze_data_quality(self, data: List[Dict], feature_columns: List[str]) -> Dict[str, Any]:
        """データ品質の分析"""
        quality_analysis = {
            'constant_features': [],
            'near_constant_features': [],
            'high_correlation_pairs': [],
            'extreme_value_features': []
        }
        
        # 定数特徴量の検出
        for feature in feature_columns:
            values = []
            for row in data:
                value = row.get(feature, None)
                if isinstance(value, (int, float)) and not np.isnan(value):
                    values.append(value)
            
            if values:
                unique_values = len(set(values))
                std_dev = np.std(values)
                
                if unique_values == 1:
                    quality_analysis['constant_features'].append(feature)
                elif std_dev < 1e-6:
                    quality_analysis['near_constant_features'].append(feature)
                
                # 極値の検出
                if len(values) > 1:
                    mean_val = np.mean(values)
                    std_val = np.std(values)
                    extreme_count = sum(1 for v in values if abs(v - mean_val) > 3 * std_val)
                    
                    if extreme_count > len(values) * 0.05:  # 5%以上が極値
                        quality_analysis['extreme_value_features'].append({
                            'feature': feature,
                            'extreme_percentage': (extreme_count / len(values)) * 100
                        })
        
        return quality_analysis
    
    def _analyze_distributions(self, data: List[Dict], feature_columns: List[str]) -> Dict[str, Any]:
        """分布の分析"""
        distribution_analysis = {
            'skewed_features': [],
            'bimodal_features': [],
            'normal_features': [],
            'statistics': {}
        }
        
        for feature in feature_columns[:20]:  # 最初の20特徴量のみ分析
            values = []
            for row in data:
                value = row.get(feature, None)
                if isinstance(value, (int, float)) and not np.isnan(value):
                    values.append(value)
            
            if len(values) > 10:
                # 基本統計量
                stats = {
                    'mean': np.mean(values),
                    'std': np.std(values),
                    'min': np.min(values),
                    'max': np.max(values),
                    'median': np.median(values),
                    'skewness': self._calculate_skewness(values),
                    'kurtosis': self._calculate_kurtosis(values)
                }
                
                distribution_analysis['statistics'][feature] = stats
                
                # 分布の特性を判定
                if abs(stats['skewness']) > 1.0:
                    distribution_analysis['skewed_features'].append({
                        'feature': feature,
                        'skewness': stats['skewness']
                    })
                elif abs(stats['skewness']) < 0.5 and abs(stats['kurtosis']) < 1.0:
                    distribution_analysis['normal_features'].append(feature)
        
        return distribution_analysis
    
    def _calculate_skewness(self, values: List[float]) -> float:
        """歪度の計算"""
        try:
            values = np.array(values)
            mean = np.mean(values)
            std = np.std(values)
            
            if std == 0:
                return 0.0
            
            skewness = np.mean(((values - mean) / std) ** 3)
            return float(skewness)
        except:
            return 0.0
    
    def _calculate_kurtosis(self, values: List[float]) -> float:
        """尖度の計算"""
        try:
            values = np.array(values)
            mean = np.mean(values)
            std = np.std(values)
            
            if std == 0:
                return 0.0
            
            kurtosis = np.mean(((values - mean) / std) ** 4) - 3
            return float(kurtosis)
        except:
            return 0.0
    
    def _detect_outliers(self, data: List[Dict], feature_columns: List[str]) -> Dict[str, Any]:
        """外れ値の検出"""
        outlier_analysis = {
            'method': 'IQR',
            'outlier_percentages': {},
            'high_outlier_features': []
        }
        
        for feature in feature_columns[:15]:  # 最初の15特徴量を分析
            values = []
            for row in data:
                value = row.get(feature, None)
                if isinstance(value, (int, float)) and not np.isnan(value):
                    values.append(value)
            
            if len(values) > 4:
                # IQR法で外れ値を検出
                q1 = np.percentile(values, 25)
                q3 = np.percentile(values, 75)
                iqr = q3 - q1
                
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                outlier_count = sum(1 for v in values if v < lower_bound or v > upper_bound)
                outlier_percentage = (outlier_count / len(values)) * 100
                
                outlier_analysis['outlier_percentages'][feature] = outlier_percentage
                
                if outlier_percentage > 5.0:  # 5%以上が外れ値
                    outlier_analysis['high_outlier_features'].append({
                        'feature': feature,
                        'outlier_percentage': outlier_percentage
                    })
        
        return outlier_analysis
    
    def _analyze_class_balance(self, data: List[Dict]) -> Dict[str, Any]:
        """クラスバランスの分析"""
        class_balance = {
            'exercise_distribution': {},
            'experience_distribution': {},
            'balance_score': 0.0
        }
        
        # エクササイズ別の分布
        exercise_counts = {}
        experience_counts = {}
        
        for row in data:
            exercise = row.get('exercise', 'unknown')
            experience = row.get('experience', 'unknown')
            
            exercise_counts[exercise] = exercise_counts.get(exercise, 0) + 1
            experience_counts[experience] = experience_counts.get(experience, 0) + 1
        
        # パーセンテージに変換
        total_samples = len(data)
        if total_samples > 0:
            for exercise, count in exercise_counts.items():
                class_balance['exercise_distribution'][exercise] = (count / total_samples) * 100
            
            for experience, count in experience_counts.items():
                class_balance['experience_distribution'][experience] = (count / total_samples) * 100
        
        # バランススコアの計算（エントロピーベース）
        if exercise_counts:
            exercise_probs = [count / total_samples for count in exercise_counts.values()]
            entropy = -sum(p * np.log2(p + 1e-6) for p in exercise_probs)
            max_entropy = np.log2(len(exercise_counts))
            class_balance['balance_score'] = entropy / max_entropy if max_entropy > 0 else 0.0
        
        return class_balance
    
    def _calculate_overall_quality(self, datasets: Dict[str, Any]) -> Dict[str, Any]:
        """全体的な品質スコアの計算"""
        overall_quality = {
            'data_completeness': 0.0,
            'data_consistency': 0.0,
            'data_balance': 0.0,
            'overall_score': 0.0,
            'grade': 'F'
        }
        
        valid_datasets = [d for d in datasets.values() if d.get('status') == 'processed']
        
        if not valid_datasets:
            return overall_quality
        
        # データ完全性（欠損値の少なさ）
        completeness_scores = []
        for dataset in valid_datasets:
            missing_info = dataset.get('missing_values', {})
            if 'missing_percentages' in missing_info:
                avg_missing = np.mean(list(missing_info['missing_percentages'].values()))
                completeness = max(0, 100 - avg_missing) / 100
                completeness_scores.append(completeness)
        
        if completeness_scores:
            overall_quality['data_completeness'] = np.mean(completeness_scores)
        
        # データ一貫性（品質問題の少なさ）
        consistency_scores = []
        for dataset in valid_datasets:
            quality_info = dataset.get('data_quality', {})
            
            total_features = dataset.get('feature_count', 1)
            problem_features = (
                len(quality_info.get('constant_features', [])) +
                len(quality_info.get('near_constant_features', [])) +
                len(quality_info.get('extreme_value_features', []))
            )
            
            consistency = max(0, total_features - problem_features) / total_features
            consistency_scores.append(consistency)
        
        if consistency_scores:
            overall_quality['data_consistency'] = np.mean(consistency_scores)
        
        # データバランス
        balance_scores = []
        for dataset in valid_datasets:
            class_balance = dataset.get('class_balance', {})
            balance_score = class_balance.get('balance_score', 0.0)
            balance_scores.append(balance_score)
        
        if balance_scores:
            overall_quality['data_balance'] = np.mean(balance_scores)
        
        # 総合スコア
        overall_quality['overall_score'] = (
            overall_quality['data_completeness'] * 0.4 +
            overall_quality['data_consistency'] * 0.4 +
            overall_quality['data_balance'] * 0.2
        )
        
        # グレード付け
        score = overall_quality['overall_score']
        if score >= 0.9:
            overall_quality['grade'] = 'A'
        elif score >= 0.8:
            overall_quality['grade'] = 'B'
        elif score >= 0.7:
            overall_quality['grade'] = 'C'
        elif score >= 0.6:
            overall_quality['grade'] = 'D'
        else:
            overall_quality['grade'] = 'F'
        
        return overall_quality
    
    def _generate_recommendations(self, validation_report: Dict[str, Any]) -> List[str]:
        """改善推奨事項の生成"""
        recommendations = []
        
        overall_quality = validation_report.get('overall_quality', {})
        datasets = validation_report.get('datasets', {})
        
        # 完全性に関する推奨
        if overall_quality.get('data_completeness', 0) < 0.8:
            recommendations.append("欠損値が多く検出されました。データ収集プロセスの見直しやより堅牢な前処理が必要です。")
        
        # 一貫性に関する推奨
        if overall_quality.get('data_consistency', 0) < 0.8:
            recommendations.append("データ品質に問題があります。定数特徴量や極値の除去を検討してください。")
        
        # バランスに関する推奨
        if overall_quality.get('data_balance', 0) < 0.6:
            recommendations.append("クラスバランスが悪い可能性があります。データ拡張やサンプリング手法を検討してください。")
        
        # データセット別の推奨
        for dataset_name, dataset_info in datasets.items():
            if dataset_info.get('status') == 'missing':
                recommendations.append(f"{dataset_name}データセットが見つかりません。前処理パイプラインを実行してください。")
            
            if dataset_info.get('sample_count', 0) < 100:
                recommendations.append(f"{dataset_name}データセットのサンプル数が少なすぎます（{dataset_info.get('sample_count', 0)}件）。")
        
        # 一般的な推奨
        if overall_quality.get('overall_score', 0) < 0.7:
            recommendations.append("データ品質が基準を下回っています。機械学習の性能に影響する可能性があります。")
        
        if not recommendations:
            recommendations.append("データ品質は良好です。機械学習の学習に進むことができます。")
        
        return recommendations
    
    def _generate_visual_report(self, validation_report: Dict[str, Any], output_dir: str):
        """可視化レポートの生成"""
        try:
            # 出力ディレクトリの作成
            plots_dir = os.path.join(output_dir, 'validation_plots')
            os.makedirs(plots_dir, exist_ok=True)
            
            # 品質スコアの可視化
            self._plot_quality_scores(validation_report, plots_dir)
            
            # データセット比較の可視化
            self._plot_dataset_comparison(validation_report, plots_dir)
            
            # 特徴量品質の可視化
            self._plot_feature_quality(validation_report, plots_dir)
            
            logger.info(f"可視化レポートを生成: {plots_dir}")
            
        except Exception as e:
            logger.error(f"可視化レポート生成エラー: {e}")
    
    def _plot_quality_scores(self, validation_report: Dict[str, Any], output_dir: str):
        """品質スコアの可視化"""
        try:
            overall_quality = validation_report.get('overall_quality', {})
            
            scores = {
                'Completeness': overall_quality.get('data_completeness', 0),
                'Consistency': overall_quality.get('data_consistency', 0),
                'Balance': overall_quality.get('data_balance', 0),
                'Overall': overall_quality.get('overall_score', 0)
            }
            
            plt.figure(figsize=(10, 6))
            bars = plt.bar(scores.keys(), scores.values(), 
                          color=['#2369FF', '#2296FF', '#FF6B6B', '#4ECDC4'])
            
            plt.title('Data Quality Scores', fontsize=16, fontweight='bold')
            plt.ylabel('Score', fontsize=12)
            plt.ylim(0, 1)
            
            # 値をバーの上に表示
            for bar, score in zip(bars, scores.values()):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                        f'{score:.3f}', ha='center', fontweight='bold')
            
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'quality_scores.png'), dpi=300, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            logger.error(f"品質スコア可視化エラー: {e}")
    
    def _plot_dataset_comparison(self, validation_report: Dict[str, Any], output_dir: str):
        """データセット比較の可視化"""
        try:
            datasets = validation_report.get('datasets', {})
            
            dataset_names = []
            sample_counts = []
            feature_counts = []
            
            for name, info in datasets.items():
                if info.get('status') == 'processed':
                    dataset_names.append(name.title())
                    sample_counts.append(info.get('sample_count', 0))
                    feature_counts.append(info.get('feature_count', 0))
            
            if dataset_names:
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
                
                # サンプル数の比較
                ax1.bar(dataset_names, sample_counts, color=['#2369FF', '#2296FF', '#FF6B6B'])
                ax1.set_title('Sample Count by Dataset', fontweight='bold')
                ax1.set_ylabel('Sample Count')
                
                # 特徴量数の比較
                ax2.bar(dataset_names, feature_counts, color=['#2369FF', '#2296FF', '#FF6B6B'])
                ax2.set_title('Feature Count by Dataset', fontweight='bold')
                ax2.set_ylabel('Feature Count')
                
                plt.tight_layout()
                plt.savefig(os.path.join(output_dir, 'dataset_comparison.png'), dpi=300, bbox_inches='tight')
                plt.close()
                
        except Exception as e:
            logger.error(f"データセット比較可視化エラー: {e}")
    
    def _plot_feature_quality(self, validation_report: Dict[str, Any], output_dir: str):
        """特徴量品質の可視化"""
        try:
            # 訓練データの情報を使用
            train_data = validation_report.get('datasets', {}).get('train', {})
            
            if train_data.get('status') != 'processed':
                return
            
            # 欠損値の可視化
            missing_info = train_data.get('missing_values', {})
            missing_percentages = missing_info.get('missing_percentages', {})
            
            if missing_percentages:
                # 欠損値が多い上位10特徴量
                sorted_missing = sorted(missing_percentages.items(), key=lambda x: x[1], reverse=True)
                top_missing = sorted_missing[:10]
                
                if any(mp[1] > 0 for mp in top_missing):
                    plt.figure(figsize=(12, 8))
                    features, percentages = zip(*top_missing)
                    
                    # 特徴量名を短縮
                    short_features = [f[:20] + '...' if len(f) > 20 else f for f in features]
                    
                    plt.barh(range(len(short_features)), percentages, color='#FF6B6B')
                    plt.yticks(range(len(short_features)), short_features)
                    plt.xlabel('Missing Percentage (%)')
                    plt.title('Top 10 Features with Missing Values', fontweight='bold')
                    plt.gca().invert_yaxis()
                    
                    plt.tight_layout()
                    plt.savefig(os.path.join(output_dir, 'missing_values.png'), dpi=300, bbox_inches='tight')
                    plt.close()
            
        except Exception as e:
            logger.error(f"特徴量品質可視化エラー: {e}")


def main():
    """データ品質検証のメイン実行"""
    validator = DataQualityValidator()
    
    logger.info("データ品質検証を開始")
    
    # 処理済みデータの検証
    validation_report = validator.validate_processed_data()
    
    # 結果のサマリーを表示
    overall_quality = validation_report.get('overall_quality', {})
    
    print("\n=== データ品質検証結果 ===")
    print(f"総合スコア: {overall_quality.get('overall_score', 0):.3f}")
    print(f"グレード: {overall_quality.get('grade', 'F')}")
    print(f"完全性: {overall_quality.get('data_completeness', 0):.3f}")
    print(f"一貫性: {overall_quality.get('data_consistency', 0):.3f}")
    print(f"バランス: {overall_quality.get('data_balance', 0):.3f}")
    
    print("\n=== 推奨事項 ===")
    for i, recommendation in enumerate(validation_report.get('recommendations', []), 1):
        print(f"{i}. {recommendation}")
    
    logger.info("データ品質検証完了")


if __name__ == "__main__":
    main()