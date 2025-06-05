#!/usr/bin/env python3
"""
前処理パイプライン実行スクリプト
コマンドライン引数でパラメータを指定して実行可能
"""

import argparse
import logging
import sys
import os
from datetime import datetime

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ml.scripts.preprocessing import TrainingDataPreprocessor
from ml.scripts.data_validation import DataQualityValidator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'ml/logs/pipeline_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)


def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(description='トレーニングデータ前処理パイプライン')
    
    parser.add_argument('--exercise', type=str, default=None,
                       help='特定のエクササイズのみ処理 (squat, deadlift, bench_press, etc.)')
    parser.add_argument('--limit', type=int, default=500,
                       help='処理するデータ数の上限 (デフォルト: 500)')
    parser.add_argument('--augment', type=int, default=2,
                       help='データ拡張倍率 (デフォルト: 2)')
    parser.add_argument('--output-dir', type=str, default='ml/data/processed',
                       help='出力ディレクトリ (デフォルト: ml/data/processed)')
    parser.add_argument('--validate', action='store_true',
                       help='処理後にデータ品質検証を実行')
    parser.add_argument('--skip-preprocessing', action='store_true',
                       help='前処理をスキップして検証のみ実行')
    
    args = parser.parse_args()
    
    logger.info("=== トレーニングデータ前処理パイプライン開始 ===")
    logger.info(f"パラメータ: exercise={args.exercise}, limit={args.limit}, "
                f"augment={args.augment}, output_dir={args.output_dir}")
    
    try:
        if not args.skip_preprocessing:
            # 前処理パイプラインの実行
            logger.info("前処理パイプライン開始...")
            
            preprocessor = TrainingDataPreprocessor()
            
            # 1. 生データ読み込み
            logger.info("ステップ1: 生データ読み込み")
            raw_data = preprocessor.load_raw_data(
                exercise_filter=args.exercise,
                limit=args.limit
            )
            
            if not raw_data:
                logger.error("処理対象のデータが見つかりません")
                return 1
            
            logger.info(f"生データ読み込み完了: {len(raw_data)}件")
            
            # 2. データクリーニング
            logger.info("ステップ2: データクリーニング")
            cleaned_data = preprocessor.clean_data(raw_data)
            logger.info(f"クリーニング完了: {len(cleaned_data)}件")
            
            # 3. 特徴量エンジニアリング
            logger.info("ステップ3: 特徴量エンジニアリング")
            featured_data = preprocessor.extract_features(cleaned_data)
            logger.info(f"特徴量抽出完了: {len(featured_data)}件")
            
            # 4. 正規化
            logger.info("ステップ4: 正規化")
            normalized_data = preprocessor.normalize_data(featured_data)
            logger.info(f"正規化完了: {len(normalized_data)}件")
            
            # 5. データ拡張
            logger.info("ステップ5: データ拡張")
            augmented_data = preprocessor.augment_data(
                normalized_data, 
                augmentation_factor=args.augment
            )
            logger.info(f"データ拡張完了: {len(augmented_data)}件")
            
            # 6. 保存
            logger.info("ステップ6: データ保存")
            preprocessor.save_processed_data(augmented_data, args.output_dir)
            logger.info("データ保存完了")
            
            # 統計情報の表示
            logger.info("=== 処理統計 ===")
            logger.info(f"生データ: {len(raw_data)}件")
            logger.info(f"クリーニング後: {len(cleaned_data)}件")
            logger.info(f"特徴量抽出後: {len(featured_data)}件")
            logger.info(f"正規化後: {len(normalized_data)}件")
            logger.info(f"最終データ: {len(augmented_data)}件")
            logger.info(f"出力ディレクトリ: {args.output_dir}")
        
        # データ品質検証
        if args.validate:
            logger.info("=== データ品質検証開始 ===")
            
            validator = DataQualityValidator()
            validation_report = validator.validate_processed_data(args.output_dir)
            
            # 検証結果の表示
            overall_quality = validation_report.get('overall_quality', {})
            
            logger.info("=== 検証結果 ===")
            logger.info(f"総合スコア: {overall_quality.get('overall_score', 0):.3f}")
            logger.info(f"グレード: {overall_quality.get('grade', 'F')}")
            logger.info(f"完全性: {overall_quality.get('data_completeness', 0):.3f}")
            logger.info(f"一貫性: {overall_quality.get('data_consistency', 0):.3f}")
            logger.info(f"バランス: {overall_quality.get('data_balance', 0):.3f}")
            
            logger.info("=== 推奨事項 ===")
            for i, recommendation in enumerate(validation_report.get('recommendations', []), 1):
                logger.info(f"{i}. {recommendation}")
        
        logger.info("=== パイプライン完了 ===")
        return 0
        
    except Exception as e:
        logger.error(f"パイプライン実行エラー: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    # ログディレクトリの作成
    os.makedirs('ml/logs', exist_ok=True)
    
    # 実行
    exit_code = main()
    sys.exit(exit_code)