# TENAX FIT v3.0 - 包括的フィットネス分析プラットフォーム

## 概要

TENAX FIT v3.0は、既存のAI機能（姿勢推定、食事分析、運動位相検出）に科学的根拠に基づいた包括的なフィットネス分析機能を統合した、世界最先端のパーソナライズドフィットネスプラットフォームです。

## 新機能 (v3.0)

### 1. 科学的身体組成分析
- **BMI計算と分類**
- **体脂肪率推定** (タニタ式、Navy式)
- **除脂肪体重とFFMI計算**
- **理想体重範囲の提案**
- **健康リスク警告システム**

### 2. 代謝計算エンジン
- **複数のBMR計算式** (Mifflin-St Jeor、Harris-Benedict、Katch-McArdle、Cunningham)
- **TDEE計算** (活動レベル、NEAT、TEF考慮)
- **目標別カロリー設定** (減量、維持、増量)
- **代謝適応の推定**

### 3. 栄養計画システム
- **PFCバランス最適化**
- **目標別タンパク質必要量計算**
- **食事タイミング最適化**
- **ワークアウト前後の栄養ガイド**
- **高タンパク質食品データベース**

### 4. トレーニングプログラム生成
- **経験レベル別プログラム** (初心者、中級者、上級者)
- **目標別トレーニング** (筋力、筋肥大、持久力)
- **プログレッション計画**
- **METs基準の消費カロリー計算**
- **回復ガイドライン**

### 5. 包括的安全性チェック
- **リアルタイム健康リスク評価**
- **個別化された警告システム**
- **モニタリング計画**
- **緊急警告サイン**

## APIエンドポイント

### 包括的分析
```
POST /api/v3/comprehensive_analysis
```

**リクエストボディ:**
```json
{
  "weight": 70,
  "height": 170,
  "age": 30,
  "gender": "male",
  "activity_level": "moderate",
  "goal": "cutting",
  "experience": "intermediate",
  "available_days": 4,
  "equipment": "full_gym",
  "target_body_fat": 15,
  "waist_cm": 80,
  "neck_cm": 38
}
```

**レスポンス:**
```json
{
  "analysis_id": "TENAX-20240120143052",
  "body_composition": {
    "bmi": 24.2,
    "estimated_body_fat": 18.5,
    "lean_body_mass": {...},
    "ffmi": {...},
    "health_warnings": [...]
  },
  "metabolism": {
    "bmr_calculations": {...},
    "tdee": {...},
    "calorie_goals": {...}
  },
  "nutrition": {
    "daily_macros": {...},
    "protein_requirements": {...},
    "meal_plan": {...}
  },
  "training": {
    "workout_plan": {...},
    "recovery_needs": {...}
  },
  "safety_analysis": {
    "overall_safety": "low_risk",
    "warnings": [...],
    "recommendations": [...]
  }
}
```

### 目標更新
```
POST /api/v3/update_goals
```

### 進捗追跡
```
POST /api/v3/track_progress
```

### AI統合
```
POST /api/v3/integrate_ai_analysis
```

### レポート生成
```
GET /api/v3/generate_reports?user_id={id}&type={weekly|monthly|progress}
```

## フロントエンド統合

### 新コンポーネント

#### ComprehensiveAnalysisDashboard
包括的分析結果を表示する主要ダッシュボード

```tsx
import { ComprehensiveAnalysisDashboard } from '@/components/v3/ComprehensiveAnalysisDashboard'

function AnalysisPage() {
  return <ComprehensiveAnalysisDashboard />
}
```

#### API Service
```typescript
import { v3Api } from '@/services/v3Api'

// 分析実行
const result = await v3Api.performComprehensiveAnalysis(userProfile)

// 進捗追跡
await v3Api.trackProgress(userId, progressData)
```

## データベーススキーマ

### 新テーブル
- `scientific_calculations` - 科学的計算結果
- `nutrition_plans` - 栄養計画
- `training_programs` - トレーニングプログラム
- `safety_logs` - 安全性ログ
- `progress_tracking_v3` - 進捗追跡（拡張版）
- `analysis_history` - 分析履歴

### 主要ビュー
- `user_latest_analysis` - ユーザーの最新分析サマリー

## 使用方法

### 1. 初回セットアップ
```bash
# 依存関係のインストール
pip install -r requirements.txt
npm install

# データベースマイグレーション
psql -U username -d database_name -f database/v3_schema.sql

# サーバー起動
python app.py
```

### 2. 基本的な使用フロー

1. **プロファイル入力**
   - 基本情報（身長、体重、年齢、性別）
   - 活動レベルと目標設定
   - 経験レベルと利用可能日数

2. **包括的分析実行**
   - 身体組成分析
   - 代謝計算
   - 栄養計画生成
   - トレーニングプログラム作成
   - 安全性評価

3. **既存AI機能との統合**
   - 姿勢分析で実測値を取得
   - 食事写真で栄養摂取を追跡
   - 運動フォームの質を評価

4. **進捗モニタリング**
   - 定期的な測定値入力
   - 自動プラン調整
   - レポート生成

## 安全性ガイドライン

### 危険閾値

#### 体脂肪率
- **女性**: 最低15%（推奨17%以上）
- **男性**: 最低8%（推奨10%以上）

#### カロリー制限
- **最大削減率**: TDEEの25%
- **最低摂取量**: 
  - 女性: 1200kcal
  - 男性: 1500kcal

#### 体重変化
- **最大減量**: 週1%
- **最大増量**: 週0.5%

#### トレーニング
- **最大時間**: 週10時間
- **必須休養**: 週1日以上

## 科学的根拠

### BMR計算式

**Mifflin-St Jeor式** (最も正確)
```
男性: BMR = 10 × 体重(kg) + 6.25 × 身長(cm) - 5 × 年齢 + 5
女性: BMR = 10 × 体重(kg) + 6.25 × 身長(cm) - 5 × 年齢 - 161
```

**Katch-McArdle式** (体脂肪率考慮)
```
BMR = 370 + 21.6 × 除脂肪体重(kg)
```

### TDEE計算
```
TDEE = BMR × 活動係数 × NEAT係数 × (1 + TEF%)
```

活動係数:
- 座りがち: 1.2
- 軽い活動: 1.375
- 中程度: 1.55
- 活発: 1.725
- 非常に活発: 1.9

### タンパク質推奨量
- **一般トレーニング**: 2.0g/kg
- **筋肉増量期**: 2.8g/kg
- **減量期**: 3.1g/kg

## トラブルシューティング

### よくある問題

1. **分析が失敗する**
   - 必須フィールドが入力されているか確認
   - 数値が妥当な範囲内か確認

2. **警告が多すぎる**
   - より現実的な目標設定を検討
   - 段階的なアプローチを採用

3. **API接続エラー**
   - CORS設定を確認
   - APIサーバーが起動しているか確認

## 今後の拡張予定

### Phase 1 (実装済み)
- ✅ 科学的計算エンジン
- ✅ 安全性チェックシステム
- ✅ API統合
- ✅ 基本UI

### Phase 2 (計画中)
- [ ] 機械学習による個別化
- [ ] 長期トレンド分析
- [ ] ソーシャル機能
- [ ] モバイルアプリ

### Phase 3 (将来)
- [ ] ウェアラブルデバイス連携
- [ ] リアルタイムコーチング
- [ ] VR/ARトレーニング
- [ ] 医療機関連携

## サポート

質問や問題がある場合は、以下の方法でサポートを受けられます:

1. **GitHub Issues**: https://github.com/tenaxfit/issues
2. **ドキュメント**: https://docs.tenaxfit.com
3. **コミュニティフォーラム**: https://community.tenaxfit.com

## ライセンス

TENAX FIT v3.0は商用ライセンスで提供されています。
詳細はLICENSEファイルを参照してください。

---

**TENAX FIT v3.0** - Your Scientific Fitness Partner 💪🔬