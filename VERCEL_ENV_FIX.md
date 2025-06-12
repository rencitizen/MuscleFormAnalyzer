# Vercel環境変数の根本的な解決方法

## 1. Vercelダッシュボードでの設定

### Step 1: 環境変数ページへアクセス
1. [Vercel Dashboard](https://vercel.com/dashboard)にログイン
2. プロジェクトを選択
3. **Settings** → **Environment Variables**

### Step 2: 環境変数を正しく設定
各変数を以下の形式で設定：

| 変数名 | 値 | Environment |
|--------|-----|------------|
| NEXT_PUBLIC_FIREBASE_API_KEY | AIzaSyAjfiJLZkNjx9kqdFdyew7Kno9NXUpGTXI | Production, Preview, Development |
| NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN | tenaxauth.firebaseapp.com | Production, Preview, Development |
| NEXT_PUBLIC_FIREBASE_PROJECT_ID | tenaxauth | Production, Preview, Development |
| NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET | tenaxauth.firebasestorage.app | Production, Preview, Development |
| NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID | 957012960073 | Production, Preview, Development |
| NEXT_PUBLIC_FIREBASE_APP_ID | 1:957012960073:web:edf5449d38e087ab69f098 | Production, Preview, Development |

### Step 3: 重要な注意点
- **引用符を入れない**（値の欄に`"AIzaSy..."`ではなく`AIzaSy...`を入力）
- **前後の空白を入れない**
- **改行を入れない**
- **すべての環境（Production, Preview, Development）にチェック**

### Step 4: 再デプロイ
1. 環境変数を保存後、**必ず再デプロイが必要**
2. Deployments → 最新のデプロイの「...」メニュー → **Redeploy**
3. 「Use existing Build Cache」のチェックを**外す**

## 2. ローカル開発環境の設定

```bash
# frontend/.env.localを作成
cd frontend
cp .env.local.example .env.local
```

## 3. 確認方法

### ビルド時の確認
Vercelのビルドログで以下を確認：
```
=== Environment Variables Check ===
✅ NEXT_PUBLIC_FIREBASE_API_KEY: AIzaSyAjfi...
✅ NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN: tenaxauth....
...
```

### ブラウザでの確認
1. デプロイ後のサイトにアクセス
2. ブラウザの開発者ツールを開く（F12）
3. Consoleタブで以下を確認：
```
🌐 Firebase Config Debug (Client side):
API Key: AIzaSyAjfiJLZkNjx9kqdFdyew7Kno9NXUpGTXI
✅ All required environment variables are present
```

## 4. トラブルシューティング

### 環境変数が`undefined`の場合
1. Vercelダッシュボードで値を再確認
2. 環境（Production/Preview/Development）の選択を確認
3. キャッシュなしで再デプロイ

### API Keyエラーが続く場合
1. Firebaseコンソールでプロジェクト設定を確認
2. Web APIキーが有効になっているか確認
3. ドメイン制限が設定されていないか確認

## 5. セキュリティのベストプラクティス

1. **Firebaseセキュリティルール**を設定
   - Firestore、Storage、Realtime Databaseのルールを適切に設定

2. **認証済みドメインを設定**
   - Firebase Console → Authentication → Settings → Authorized domains
   - Vercelのドメインを追加

3. **APIキーの制限**（オプション）
   - Google Cloud Console → APIs & Services → Credentials
   - APIキーに対してHTTPリファラー制限を設定

## 6. 最終確認

すべての設定後、以下を確認：
- [ ] 環境変数がVercelに正しく設定されている
- [ ] すべての環境にチェックが入っている
- [ ] キャッシュなしで再デプロイした
- [ ] ブラウザコンソールでエラーがない
- [ ] Firebase認証が正常に動作する