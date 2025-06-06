# BodyScale クイックスタートガイド

## 🚀 5分でBodyScaleを始める

### 1. 必要なソフトウェア
- Python 3.8以上
- Node.js 16以上
- Git

### 2. セットアップ（初回のみ）

```bash
# リポジトリのクローン（既にある場合はスキップ）
git clone <repository-url>
cd MuscleFormAnalyzer

# Windowsの場合
start_bodyscale.bat

# Mac/Linuxの場合
./start_bodyscale.sh
```

### 3. Firebase設定（オプション）
1. `frontend/.env.local.example` を `frontend/.env.local` にコピー
2. Firebaseプロジェクトを作成して認証情報を取得
3. `.env.local` に認証情報を設定

### 4. アプリケーションの使用

1. **ブラウザでアクセス**
   - http://localhost:3000 を開く

2. **アカウント作成**
   - 「新規登録」をクリック
   - メールアドレスとパスワードを入力
   - またはGoogleアカウントでログイン

3. **初期設定**
   - ホーム画面右上の「設定」をクリック
   - 身長・体重を入力

4. **フォーム分析開始**
   - ホーム画面の「フォーム分析を開始」をクリック
   - カメラの許可を与える
   - 種目を選択（スクワット/デッドリフト/ベンチプレス）
   - 「キャリブレーション」で個人設定
   - 全身が映る位置にカメラをセット
   - 「録画開始」をクリックして運動を実行
   - 「録画停止」で分析結果を確認

5. **進捗確認**
   - 「進捗を確認」から成長記録を確認

## 🎯 最適なカメラ位置

### スクワット・デッドリフト
- 横から撮影（真横がベスト）
- 2-3メートル離れる
- カメラは腰の高さ
- 全身が映るように

### ベンチプレス
- 斜め45度から撮影
- ベンチから2メートル離れる
- 上半身全体が映るように

## ❓ よくある質問

**Q: カメラが認識されない**
A: ブラウザのカメラ許可を確認してください。HTTPSまたはlocalhostでのみ動作します。

**Q: 分析精度が低い**
A: 明るい場所で、無地の背景で撮影してください。タイトな服装がおすすめです。

**Q: Firebase設定は必須？**
A: いいえ、ローカルストレージでも動作します。ただし、データの永続化にはFirebaseが推奨されます。

## 🆘 トラブルシューティング

### バックエンドが起動しない
```bash
# Python仮想環境を再作成
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
# 依存関係を再インストール
pip install -r requirements.txt
```

### フロントエンドが起動しない
```bash
cd frontend
# node_modulesを削除して再インストール
rm -rf node_modules package-lock.json
npm install
```

## 📞 サポート

問題が解決しない場合は、GitHubのIssueに報告してください。