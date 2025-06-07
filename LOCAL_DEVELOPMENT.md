# BodyScale Pose Analyzer - ローカル開発環境セットアップガイド

このドキュメントでは、Cursor/VSCodeでBodyScale Pose Analyzerをローカル開発する手順を説明します。

## 🚀 クイックスタート

```bash
# 1. プロジェクトのクローン
git clone <repository-url>
cd MuscleFormAnalyzer

# 2. 環境設定ファイルの作成
cp .env.example .env.local

# 3. 依存関係のインストール（初回のみ）
npm run install:all

# 4. 開発サーバーの起動
npm run dev
```

アプリケーションは以下のURLでアクセスできます：
- Frontend: http://localhost:3000
- Backend: http://localhost:5000

## 📋 必要な環境

- Node.js 18以上
- Python 3.8以上
- npm 9以上
- Git

## 🛠️ セットアップ手順

### 1. Python仮想環境の作成

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. 環境変数の設定

`.env.local`ファイルを編集して、必要な設定を行います：

```env
# 最低限必要な設定
FLASK_ENV=development
FLASK_DEBUG=True
SESSION_SECRET=your-secret-key-here
```

### 3. VSCode/Cursor設定

1. VSCode/Cursorでプロジェクトを開く
2. 推奨拡張機能をインストール（`.vscode/extensions.json`参照）
3. Python interpreterを仮想環境のものに設定

## 🎯 開発コマンド

### 基本コマンド

```bash
# 開発サーバー起動（Frontend + Backend）
npm run dev

# 個別起動
npm run dev:frontend  # Frontend only
npm run dev:backend   # Backend only

# ビルド
npm run build

# テスト実行
npm test

# クリーンアップ
npm run clean
```

### Makefileコマンド（Unix系OS）

```bash
make setup      # 初期セットアップ
make dev        # 開発サーバー起動
make test       # テスト実行
make clean      # クリーンアップ
make docker-up  # Docker環境起動
```

## 🐳 Docker開発環境

Docker環境で開発する場合：

```bash
# Docker環境の起動
docker-compose up -d

# ログの確認
docker-compose logs -f

# 環境の停止
docker-compose down

# データベースも含めて削除
docker-compose down -v
```

## 🔥 ホットリロード

- **Backend**: Flask debug modeが有効で、ファイル変更時に自動リロード
- **Frontend**: Next.jsのFast Refreshが有効

## 🐛 デバッグ

### VSCode/Cursorでのデバッグ

1. サイドバーの「Run and Debug」を選択
2. 以下の設定から選択：
   - `Python: Flask Backend` - バックエンドのデバッグ
   - `Next.js: Frontend` - フロントエンドのデバッグ
   - `Full Stack` - 両方同時にデバッグ

### ブレークポイント

- Python: コード行の左側をクリック
- JavaScript/TypeScript: 同様にコード行の左側をクリック

## 📝 開発のヒント

### 1. 同時起動

`npm run dev`で両方のサーバーが起動しますが、個別のターミナルで起動する方が管理しやすい場合があります：

```bash
# Terminal 1
cd frontend && npm run dev

# Terminal 2
python app_local.py
```

### 2. APIテスト

VSCode拡張機能「Thunder Client」または「REST Client」を使用してAPIをテストできます。

### 3. データベース管理

- SQLite: DBブラウザーを使用
- PostgreSQL: pgAdminまたはDBeaver
- Docker環境: http://localhost:8080 でAdminer使用可能

### 4. ログ確認

```bash
# アプリケーションログ
tail -f logs/bodyscale_analyzer.log

# Dockerログ
docker-compose logs -f backend
```

## 🔧 トラブルシューティング

### ポートが使用中

```bash
# 使用中のポートを確認
# Windows
netstat -ano | findstr :5000
netstat -ano | findstr :3000

# Mac/Linux
lsof -i :5000
lsof -i :3000
```

### 依存関係のエラー

```bash
# クリーンインストール
npm run clean
npm run install:all
```

### Python仮想環境の問題

```bash
# 仮想環境を再作成
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### CORSエラー

`.env.local`のCORS設定を確認：

```env
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

## 📚 その他のリソース

- [README.md](README.md) - プロジェクト概要
- [QUICKSTART.md](QUICKSTART.md) - クイックスタートガイド
- [ml/README.md](ml/README.md) - 機械学習モジュールのドキュメント

## 🤝 貢献

1. Featureブランチを作成
2. 変更をコミット
3. プルリクエストを作成

## 📞 サポート

問題が解決しない場合は、GitHubのIssueを作成してください。