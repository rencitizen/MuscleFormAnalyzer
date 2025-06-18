# Worker2（バックエンド）Phase 1タスク割り当て

## 担当: バックエンド開発者（Worker2）
## フェーズ: Phase 1 - 科学計算エンジンAPI実装

### 1. 既存バックエンドシステム分析（優先度: 最高）
- [ ] backend/ディレクトリ構造の分析
- [ ] 既存のAPIエンドポイント構造の把握
- [ ] FastAPIのルーティングパターン確認
- [ ] 既存の科学計算エンジン（lib/engines/）の分析

### 2. 科学計算APIエンドポイント実装（優先度: 高）
**実装場所**: `backend/routers/v3_calculations.py`

#### 必要なエンドポイント：

```python
# 1. BMR（基礎代謝率）計算
@router.post("/calculations/bmr")
async def calculate_bmr(data: BMRInput) -> BMRResult:
    """
    Mifflin-St Jeor式を使用してBMRを計算
    男性: (10 × weight) + (6.25 × height) - (5 × age) + 5
    女性: (10 × weight) + (6.25 × height) - (5 × age) - 161
    """

# 2. TDEE（総消費カロリー）計算
@router.post("/calculations/tdee")
async def calculate_tdee(data: TDEEInput) -> TDEEResult:
    """
    BMR × 活動係数でTDEEを計算
    - sedentary: 1.2
    - light: 1.375
    - moderate: 1.55
    - active: 1.725
    - very_active: 1.9
    """

# 3. 体脂肪率推定
@router.post("/calculations/body-fat")
async def estimate_body_fat(data: BodyFatInput) -> BodyFatResult:
    """
    Navy Method または BMI法で体脂肪率を推定
    測定値がある場合はNavy Method、ない場合はBMI法
    """

# 4. 目標カロリー計算
@router.post("/calculations/target-calories")
async def calculate_target_calories(data: TargetCaloriesInput) -> TargetCaloriesResult:
    """
    目標に応じたカロリー設定：
    - cutting: TDEE - 500 (初心者は-300)
    - maintenance: TDEE
    - bulking: TDEE + 300-500
    """

# 5. PFCバランス計算
@router.post("/nutrition/pfc-balance")
async def calculate_pfc_balance(data: PFCBalanceInput) -> PFCBalanceResult:
    """
    目標別PFCバランス：
    - タンパク質: 体重 × 1.6-2.2g
    - 脂質: 総カロリーの20-30%
    - 炭水化物: 残りのカロリー
    """

# 6. カロリー安全性チェック
@router.post("/safety/calorie-check")
async def check_calorie_safety(data: CalorieSafetyInput) -> CalorieSafetyResult:
    """
    安全性チェック：
    - BMRの1.2倍以上か
    - 極端な制限でないか
    - 年齢・性別に適切か
    """
```

### 3. 型定義（優先度: 高）
**実装場所**: `backend/models/v3_calculations.py`

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional

class BMRInput(BaseModel):
    weight: float = Field(..., gt=0, description="体重(kg)")
    height: float = Field(..., gt=0, description="身長(cm)")
    age: int = Field(..., gt=0, le=150, description="年齢")
    gender: Literal["male", "female"]

class BMRResult(BaseModel):
    bmr: float
    formula: str = "Mifflin-St Jeor"
    unit: str = "kcal/day"

class TDEEInput(BMRInput):
    activity_level: Literal["sedentary", "light", "moderate", "active", "very_active"]

class TDEEResult(BaseModel):
    tdee: float
    bmr: float
    activity_multiplier: float
    activity_level_description: str

# ... 他の型定義も同様に実装
```

### 4. 計算ロジック実装（優先度: 高）
**実装場所**: `backend/lib/calculators/scientific_calculator.py`

実装すべきメソッド：
- `calculate_bmr_mifflin(weight, height, age, gender)`
- `calculate_tdee(bmr, activity_level)`
- `estimate_body_fat_navy(waist, neck, hip, height, gender)`
- `estimate_body_fat_bmi(bmi, age, gender)`
- `calculate_lean_body_mass(weight, body_fat_percentage)`
- `calculate_target_calories(tdee, goal, experience_level)`
- `calculate_protein_requirement(weight, goal, experience_level)`
- `calculate_pfc_distribution(daily_calories, protein_grams)`
- `check_calorie_safety(calories, bmr, age, gender)`

### 5. 既存エンジンとの統合（優先度: 中）
- `lib/engines/scientific_calculations.py`との連携
- エラーハンドリングの統一
- ログ記録の実装

### 6. バリデーション実装（優先度: 高）
- 入力値の範囲チェック
- 科学的に妥当な値の検証
- エラーメッセージの日本語化

### 実装順序
1. 型定義（models）の作成
2. 計算ロジックの実装
3. APIエンドポイントの実装
4. 統合テストの作成
5. ドキュメント化

### 注意事項
- 既存のFastAPI構造に従うこと
- エラーレスポンスは既存のパターンに合わせる
- 計算の精度を保証（小数点以下の処理）
- パフォーマンス要件: 各計算 <100ms

### テスト要件
- 各計算メソッドの単体テスト
- APIエンドポイントの統合テスト
- エッジケースのテスト（極端な値）
- エラーケースのテスト

### 成果物
- 実装したAPIエンドポイント一覧
- 計算ロジックのドキュメント
- テストカバレッジレポート
- パフォーマンス測定結果

開始前に既存のバックエンドコードベースの詳細分析を完了させてください。