# BodyScale Pose Analyzer - 完全実装版

ジム通いの筋トレ中級者向けBIG3フォーム分析アプリケーション

## 🚀 実装完了機能

### フェーズ1: 基盤構築 ✅
- ✅ Next.js + TypeScript + Tailwind CSSセットアップ
- ✅ MediaPipe統合（33点関節検出）
- ✅ リアルタイムカメラアクセス
- ✅ Firebase認証システム
- ✅ 基本的なUI/UXデザイン

### フェーズ2: BIG3基本分析 ✅
- ✅ 種目自動識別（スクワット、デッドリフト、ベンチプレス）
- ✅ 各種目の重要角度計算
  - スクワット：膝角度、股関節角度、背中の傾き
  - デッドリフト：腰椎曲がり、バーの軌道
  - ベンチプレス：肘の角度、アーチ維持
- ✅ フェーズ検出（セットアップ→下降→ボトム→上昇→トップ）
- ✅ リアルタイムフィードバック生成

### フェーズ3: 個人最適化（レベル4） ✅
- ✅ キャリブレーション機能
  - 身長・体重入力
  - 足首柔軟性測定
  - 自動身体寸法測定（実装済み）
- ✅ PersonalizedAnalyzer実装
  - 大腿骨比率に基づくスタンス幅調整
  - 足首柔軟性による推奨深度調整
  - 個別化されたフィードバック

### フェーズ4: 進捗管理システム ✅
- ✅ セッション記録機能
- ✅ 進捗の可視化
  - フォームスコアの推移（折れ線グラフ）
  - 種目バランス（レーダーチャート）
  - 週間アクティビティ（棒グラフ）
- ✅ トレンド分析と成長予測
- ✅ アチーブメントシステム

### フェーズ5: 簡易栄養管理 🔄
- 基本設計完了（UIは未実装）

### フェーズ6: リリース準備 ✅
- ✅ エラーハンドリング
- ✅ レスポンシブデザイン
- ✅ ダークモード対応

## 📁 プロジェクト構造

```
MuscleFormAnalyzer/
├── frontend/                    # Next.jsフロントエンド
│   ├── app/                    # App Router
│   │   ├── analyze/           # フォーム分析ページ
│   │   ├── auth/              # 認証ページ
│   │   ├── progress/          # 進捗ダッシュボード
│   │   └── page.tsx           # ホームページ
│   ├── components/            # Reactコンポーネント
│   │   ├── pose-analysis/     # ポーズ分析関連
│   │   ├── providers/         # Context Providers
│   │   └── ui/                # UIコンポーネント
│   ├── lib/                   # ユーティリティとロジック
│   │   ├── analysis/          # 分析アルゴリズム
│   │   ├── calibration/       # 個人最適化
│   │   └── mediapipe/         # MediaPipe統合
│   └── package.json           # 依存関係
│
├── app.py                      # Flask APIサーバー
├── analysis/                   # バックエンド分析モジュール
├── ml/                        # 機械学習モジュール
└── static/                    # 静的ファイル
```

## 🛠️ セットアップ手順

### 1. バックエンド（Flask）

```bash
# 依存関係のインストール
pip install -r requirements.txt

# データベースの初期化
python init_database.py

# サーバーの起動
python app.py
```

### 2. フロントエンド（Next.js）

```bash
# フロントエンドディレクトリに移動
cd frontend

# 依存関係のインストール
npm install

# 環境変数の設定
cp .env.local.example .env.local
# .env.localを編集してFirebase認証情報を設定

# 開発サーバーの起動
npm run dev
```

### 3. アクセス
- フロントエンド: http://localhost:3000
- バックエンドAPI: http://localhost:5000

## 🔑 主要技術

### フロントエンド
- **Next.js 14**: App Router使用
- **TypeScript**: 型安全性
- **Tailwind CSS**: スタイリング
- **MediaPipe**: ポーズ検出
- **Recharts**: データ可視化
- **Firebase Auth**: 認証
- **Radix UI**: UIコンポーネント

### バックエンド
- **Flask**: APIサーバー
- **MediaPipe**: サーバーサイド分析
- **PostgreSQL/SQLite**: データベース
- **NumPy/SciPy**: 数値計算

## 📊 データフロー

1. **カメラ入力** → MediaPipe → 33点ランドマーク検出
2. **ランドマーク** → ExerciseAnalyzer → 種目判定・角度計算
3. **分析結果** → PersonalizedAnalyzer → 個人最適化
4. **最適化結果** → UI表示 → ユーザーフィードバック

## 🎯 使用方法

1. **初回セットアップ**
   - アカウント作成
   - 身長・体重入力
   - キャリブレーション実行

2. **フォーム分析**
   - 種目選択（スクワット/デッドリフト/ベンチプレス）
   - カメラセットアップ
   - 録画開始
   - 分析結果確認

3. **進捗確認**
   - ダッシュボードで統計確認
   - 成長トレンド分析
   - 改善提案の確認

## 🔧 カスタマイズ

### 新しい種目の追加
1. `lib/analysis/exerciseAnalyzer.ts`に分析関数追加
2. `lib/mediapipe/types.ts`に種目タイプ追加
3. UIコンポーネントの更新

### 分析アルゴリズムの調整
- `lib/analysis/`内の各種スコア計算関数を編集
- 閾値や重み付けの調整

## 📝 今後の拡張予定

- [ ] 栄養管理機能の完全実装
- [ ] 動画の保存・再生機能
- [ ] ソーシャル機能（進捗シェア）
- [ ] AI による詳細なコーチング
- [ ] Apple Watch 連携

## 🤝 貢献方法

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 🙏 謝辞

- MediaPipe チーム
- Next.js チーム
- すべてのオープンソース貢献者