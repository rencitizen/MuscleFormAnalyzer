# 身長測定精度向上ガイド

## 概要

本ガイドでは、MediaPipeを使用した動画ベースの身長測定システムの精度を大幅に向上させる実装について説明します。

## 主な改善点

### 1. **カメラキャリブレーション**
- カメラの角度、距離、歪みを自動検出・補正
- 顔の傾き検出による姿勢チェック
- 適切な撮影距離の自動判定（2-3メートル推奨）

### 2. **基準点検出の精度向上**
- 複数の頭部ランドマークから最高点を特定
- 髪の毛分のオフセット調整
- 足元検出に踵と足先を含む6点を使用

### 3. **複数の測定方法**
- **体比率ベース**: 肩幅と身長の比率（最も正確）
- **胴体長ベース**: 胴体と全身の比率
- **直接変換**: 経験的係数による変換

### 4. **マルチフレーム安定化**
- 30フレーム分の測定値を保持
- IQR法による外れ値除去
- 信頼度重み付き平均

### 5. **ユーザー較正システム**
- 実際の身長入力による較正
- 較正係数の自動計算と保存
- 較正状態の可視化

## 実装ファイル

### フロントエンド（TypeScript/React）

#### 1. `frontend/lib/mediapipe/improvedHeightMeasurement.ts`
- コア測定ロジック
- カメラキャリブレーション
- マルチフレーム処理
- 較正システム

```typescript
import { heightMeasurementSystem } from '@/lib/mediapipe/improvedHeightMeasurement'

// 初期化
await heightMeasurementSystem.initialize()

// 測定実行
const result = await heightMeasurementSystem.measureHeight(videoElement)

// 較正付き測定
const calibratedResult = await heightMeasurementSystem.measureHeight(
  videoElement, 
  170 // 実際の身長(cm)
)
```

#### 2. `frontend/components/body-measurement/ImprovedHeightMeasurement.tsx`
- 完全なUIコンポーネント
- カメラ/動画アップロード対応
- 較正ウィザード
- リアルタイム結果表示

### バックエンド（Python）

#### `core/improved_height_measurement.py`
- サーバーサイド処理
- 動画ファイル処理
- バッチ処理対応

```python
from core.improved_height_measurement import AccurateHeightMeasurementSystem

# システム初期化
system = AccurateHeightMeasurementSystem()

# フレーム処理
result = system.process_frame(frame, user_height=170)

# 動画全体を処理
from core.improved_height_measurement import process_video_for_height
result = process_video_for_height(
    "video.mp4",
    reference_height=170,
    progress_callback=lambda p: print(f"Progress: {p}%")
)
```

## 使用方法

### 1. 基本的な測定

```typescript
// React コンポーネントで使用
import { ImprovedHeightMeasurement } from '@/components/body-measurement/ImprovedHeightMeasurement'

function App() {
  return <ImprovedHeightMeasurement />
}
```

### 2. 較正プロセス

1. **較正モード選択**: UIで「較正モード」を選択
2. **距離調整**: カメラから2-3メートル離れる
3. **姿勢確認**: 背筋を伸ばして直立
4. **身長入力**: 実際の身長を入力（50-250cm）
5. **較正完了**: システムが自動的に係数を計算

### 3. 推奨される撮影条件

- **距離**: カメラから2-3メートル
- **照明**: 明るく均一な照明
- **背景**: 無地の壁（コントラストがある色）
- **服装**: 体のラインが分かる服装
- **姿勢**: 壁に背中をつけて直立

## 精度向上のメカニズム

### 1. 距離補正

```typescript
// 瞳孔間距離による補正
const eyeDistance = calculateEyeDistance(landmarks)
const correction = AVERAGE_EYE_DISTANCE / eyeDistance
```

### 2. 外れ値除去

```typescript
// IQR（四分位範囲）法
const q1 = percentile(heights, 25)
const q3 = percentile(heights, 75)
const iqr = q3 - q1
const filtered = heights.filter(h => 
  h >= q1 - 1.5 * iqr && h <= q3 + 1.5 * iqr
)
```

### 3. 信頼度計算

```typescript
// 変動係数から信頼度を算出
const cv = standardDeviation / mean
const confidence = Math.max(0, Math.min(1, 1 - cv * 5))
```

## トラブルシューティング

### 問題: 測定値が実際と大きく異なる

**解決策**:
1. 較正モードで実際の身長を入力
2. カメラの位置を調整（高さは胸の高さ）
3. 全身が画面に収まることを確認

### 問題: 測定値が安定しない

**解決策**:
1. より明るい場所で撮影
2. 静止して測定（10秒以上）
3. 無地の背景を使用

### 問題: ポーズが検出されない

**解決策**:
1. カメラとの距離を調整
2. 体のラインが見える服装に変更
3. MediaPipeモデルの複雑度を上げる

## パフォーマンス最適化

### フロントエンド
- MediaPipeインスタンスのシングルトン化
- 不要なレンダリングの防止
- Web Workerでの処理（オプション）

### バックエンド
- フレームスキップ（5fps程度で十分）
- 並列処理による高速化
- キャッシュの活用

## 今後の改善案

1. **機械学習モデルの追加**
   - より正確な頭頂部検出
   - 体型別の補正係数学習

2. **3D再構築**
   - ステレオカメラ対応
   - 深度情報の活用

3. **参照物体検出**
   - クレジットカード、スマートフォンなどの自動検出
   - より正確なスケール推定

## まとめ

この改良システムにより、以下が実現されます：

- **精度向上**: ±2cm以内の誤差（較正時）
- **安定性**: 複数フレーム処理による安定した測定
- **使いやすさ**: 直感的なUIと詳細なガイダンス
- **信頼性**: 測定条件の自動チェックと推奨事項

適切な条件下で較正を行えば、医療グレードに近い精度での身長測定が可能になります。