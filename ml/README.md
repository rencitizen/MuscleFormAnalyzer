# Tenax Fit ML Pipeline

Tenax Fitの機械学習パイプライン - トレーニングデータの収集、前処理、特徴量エンジニアリング、モデル学習を提供

## 📁 ディレクトリ構造

```
ml/
├── api/                    # API・推論エンジン
│   ├── inference.py       # リアルタイム推論エンジン
│   └── __init__.py
├── data/                  # データ関連
│   ├── preprocessor.py    # データ前処理 (旧版)
│   ├── training_data_collector.py  # データ収集システム
│   └── processed/         # 前処理済みデータ (自動生成)
├── models/                # 機械学習モデル
│   ├── exercise_classifier.py  # エクササイズ分類器
│   └── __init__.py
├── scripts/               # バッチ処理スクリプト
│   ├── preprocessing.py   # 前処理パイプライン
│   ├── feature_engineering.py  # 高度な特徴量エンジニアリング
│   ├── data_validation.py # データ品質検証
│   ├── run_pipeline.py    # パイプライン実行スクリプト
│   └── train_model.py     # モデル学習スクリプト (予定)
├── logs/                  # ログファイル (自動生成)
└── README.md             # このファイル
```

## 🚀 機能概要

### 1. データ収集システム (`data/training_data_collector.py`)
- MediaPipeポーズデータの匿名化収集
- ユーザー同意管理 (GDPR対応)
- メタデータ・パフォーマンスデータの統合
- CSV/JSONエクスポート機能

### 2. 前処理パイプライン (`scripts/preprocessing.py`)
- **データクリーニング**: 欠損値補完、外れ値除去、ノイズ除去
- **特徴量エンジニアリング**: 関節角度、距離、バランス指標の計算
- **正規化**: 身長ベース正規化、統計的標準化
- **データ拡張**: 左右反転、ノイズ追加、スケール変更

### 3. 高度特徴量エンジニアリング (`scripts/feature_engineering.py`)
- **時系列特徴量**: 動作速度、加速度、滑らかさ、リズム一貫性
- **フォーム品質特徴量**: エクササイズ別フォーム評価
- **一般的特徴量**: 左右対称性、安定性、姿勢品質

### 4. データ品質検証 (`scripts/data_validation.py`)
- **完全性評価**: 欠損値分析
- **一貫性評価**: データ品質問題検出
- **バランス評価**: クラス分布分析
- **可視化レポート**: 品質スコア、分布グラフ

## 🔧 使用方法

### Webインターface経由

1. **データ同意**: `/data_consent` - データ利用同意の取得
2. **データ管理**: `/training_data_management` - 収集データの管理
3. **前処理**: `/data_preprocessing` - 前処理パイプラインの実行

### コマンドライン経由

```bash
# 基本的な前処理パイプライン実行
python ml/scripts/run_pipeline.py

# 特定エクササイズのみ処理
python ml/scripts/run_pipeline.py --exercise squat --limit 200

# データ拡張を含む完全パイプライン
python ml/scripts/run_pipeline.py --augment 3 --validate

# 検証のみ実行
python ml/scripts/run_pipeline.py --skip-preprocessing --validate
```

### API経由

```python
# 前処理パイプライン実行
POST /api/preprocessing/run
{
    "exercise_filter": "squat",
    "limit": 500,
    "augmentation_factor": 2
}

# データ品質検証
POST /api/preprocessing/validate
{
    "data_dir": "ml/data/processed"
}

# 特徴量エンジニアリング
POST /api/preprocessing/feature_engineering
{
    "pose_data": [[x,y,z,v], ...],
    "exercise": "squat",
    "metadata": {"height": 170, "weight": 70, "experience": "intermediate"}
}
```

## 📊 データスキーマ

### 収集データ形式
```json
{
    "session_id": "uuid",
    "timestamp": "2024-01-01T12:00:00Z",
    "exercise": "squat",
    "pose_data": [
        [x, y, z, visibility], // 33ポイント × 4次元
        ...
    ],
    "metadata": {
        "height": 170,
        "weight": 70,
        "experience": "intermediate"
    },
    "performance": {
        "weight": 60,
        "reps": 10,
        "form_score": 0.85
    }
}
```

### 処理済みデータ形式 (CSV)
```csv
session_id,exercise,timestamp,angle_left_knee_normalized,distance_shoulder_width_normalized,...
uuid1,squat,2024-01-01T12:00:00Z,0.234,-0.567,...
```

## 🏃‍♂️ クイックスタート

1. **データ収集開始**
   ```python
   # Webアプリでトレーニング記録中に自動収集
   # または
   from ml.data.training_data_collector import TrainingDataCollector
   collector = TrainingDataCollector()
   collector.record_user_consent("user_id", True)
   ```

2. **前処理実行**
   ```bash
   python ml/scripts/run_pipeline.py --validate
   ```

3. **結果確認**
   ```
   ml/data/processed/
   ├── train.csv          # 訓練データ (70%)
   ├── val.csv            # 検証データ (15%)
   ├── test.csv           # テストデータ (15%)
   ├── validation_report.json
   └── validation_plots/  # 品質可視化
   ```

## ⚙️ 設定

### 環境変数
- `DATABASE_URL`: PostgreSQLデータベースURL (必須)

### 依存関係
- `numpy`: 数値計算
- `scipy`: 信号処理 (Savitzky-Golayフィルタ)
- `matplotlib`: 可視化 (検証レポート用)
- `psycopg2-binary`: PostgreSQL接続

## 🔒 プライバシー・セキュリティ

- **完全匿名化**: ユーザーIDはハッシュ化
- **同意管理**: GDPR準拠の同意取得・撤回
- **データ削除**: 要求に応じた完全削除
- **暗号化保存**: データベースレベルでの暗号化

## 📈 パフォーマンス

- **処理速度**: 500サンプル/分 (標準設定)
- **メモリ使用量**: 最大2GB (大規模データセット)
- **出力サイズ**: 元データの約3-5倍 (拡張後)

## 🔧 トラブルシューティング

### よくある問題

1. **ModuleNotFoundError: pandas/sklearn**
   - 軽量版環境では一部機能が制限されます
   - 基本的な前処理は numpy のみで動作

2. **データが見つからない**
   - データ収集が必要: `/data_consent` で同意取得
   - ワークアウト記録でポーズデータを収集

3. **メモリ不足**
   - `--limit` パラメータでデータ数を制限
   - `--augment` で拡張倍率を下げる

### ログ確認
```bash
# 最新のログファイルを確認
ls -la ml/logs/
tail -f ml/logs/pipeline_*.log
```

## 🚀 今後の拡張予定

- [ ] リアルタイム特徴量計算の最適化
- [ ] 追加エクササイズタイプのサポート
- [ ] 分散処理対応 (大規模データセット)
- [ ] モデル学習パイプラインの統合
- [ ] A/Bテスト機能

## 📞 サポート

問題やご質問は Issue でお気軽にお問い合わせください。