# Worker1（フロントエンド）Phase 1タスク割り当て

## 担当: フロントエンド開発者（Worker1）
## フェーズ: Phase 1 - 基盤機能実装

### 1. 既存システム分析タスク（優先度: 最高）
- [ ] frontend/componentsディレクトリの既存コンポーネント構造分析
- [ ] 既存のUI/UXパターンとデザインシステムの把握
- [ ] Radix UI + Tailwind CSSの実装パターン確認
- [ ] 既存のダッシュボード構造（frontend/app/dashboard）の分析

### 2. ユーザープロフィール設定UI（優先度: 高）
**実装場所**: `frontend/app/profile/page.tsx`の拡張
**新規コンポーネント**: `frontend/components/profile/ScientificProfileForm.tsx`

```typescript
// 必要なフィールド
interface UserProfile {
  // 既存フィールド + 新規追加
  weight: number; // kg
  height: number; // cm
  age: number;
  gender: 'male' | 'female';
  activityLevel: 'sedentary' | 'light' | 'moderate' | 'active' | 'very_active';
  goal: 'muscle_gain' | 'fat_loss' | 'maintenance';
  experienceLevel: 'beginner' | 'intermediate' | 'advanced';
}
```

### 3. 科学計算結果ダッシュボード（優先度: 高）
**実装場所**: `frontend/components/dashboard/ScientificMetrics.tsx`
**統合先**: 既存のComprehensiveDashboardに追加

必要なコンポーネント:
- BMR表示カード
- TDEE表示カード
- 目標カロリー表示
- 体脂肪率推定表示
- PFCバランス円グラフ（Chart.jsまたはRecharts使用）

### 4. 安全性警告システムUI（優先度: 高）
**実装場所**: `frontend/components/safety/HealthWarnings.tsx`

警告表示要件:
- カロリー設定が基礎代謝を下回る場合の警告
- 極端な体脂肪率目標への警告
- Radix UIのAlertDialogコンポーネント使用

### 5. API統合（優先度: 高）
**実装場所**: `frontend/services/v3Api.ts`の拡張

```typescript
// 新規エンドポイント
export const v3Api = {
  calculations: {
    calculateBMR: (data: BMRInput) => POST('/api/v3/calculations/bmr', data),
    calculateTDEE: (data: TDEEInput) => POST('/api/v3/calculations/tdee', data),
    estimateBodyFat: (data: BodyFatInput) => POST('/api/v3/calculations/body-fat', data),
    getTargetCalories: (data: TargetInput) => POST('/api/v3/calculations/target-calories', data),
  },
  nutrition: {
    getPFCBalance: (data: PFCInput) => POST('/api/v3/nutrition/pfc-balance', data),
  },
  safety: {
    checkCalorieSafety: (data: SafetyInput) => POST('/api/v3/safety/calorie-check', data),
  }
};
```

### 6. 既存UIとの統合（優先度: 中）
- 既存のナビゲーションメニューへの新機能追加
- ダッシュボードへの科学計算セクション統合
- レスポンシブデザインの確保

### 実装順序
1. ユーザープロフィール設定UIの実装
2. API統合レイヤーの構築
3. 科学計算結果ダッシュボードの実装
4. 安全性警告システムの実装
5. 既存UIへの統合とテスト

### 注意事項
- 既存のデザインシステムを踏襲すること
- TypeScriptの型定義を厳密に行うこと
- 既存のMediaPipe機能に影響を与えないこと
- パフォーマンス要件: 計算結果表示 <200ms

### 成果物
- 実装したコンポーネントのリスト
- APIとの統合確認
- レスポンシブデザインの確認
- 既存機能への影響評価レポート

開始前に既存コードベースの詳細分析を完了させてください。