# Google OAuth認証エラーの解決方法

## 🚨 エラー内容
```
The current domain is not authorized for OAuth operations. 
This will prevent signInWithPopup, signInWithRedirect, linkWithPopup, 
linkWithRedirect, reauthenticateWithPopup, and reauthenticateWithRedirect 
from working. Add your domain (muscle-form-analyzer.vercel.app) to the 
OAuth redirect domains list in the Firebase console -> Authentication -> Settings 
tab.
```

## ✅ 解決手順

### 1. Firebase Console設定

#### Step 1: Firebase Consoleにアクセス
1. [Firebase Console](https://console.firebase.google.com/)にログイン
2. **tenaxauth**プロジェクトを選択

#### Step 2: Google認証を有効化
1. **Authentication** → **Sign-in method**タブ
2. **Google**プロバイダーをクリック
3. **有効にする**をON
4. **プロジェクトのサポートメール**を設定
5. **保存**

#### Step 3: 認証済みドメインを追加
1. **Authentication** → **Settings**タブ
2. **Authorized domains**セクション
3. **Add domain**をクリック
4. 以下のドメインを追加：
   - `muscle-form-analyzer.vercel.app`
   - `localhost` (開発環境用)

### 2. Google Cloud Console設定

#### Step 1: OAuth 2.0クライアントIDの設定
1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. プロジェクトを選択
3. **APIs & Services** → **Credentials**

#### Step 2: OAuth 2.0クライアントIDを編集
1. 既存のOAuth 2.0クライアントIDをクリック
2. **Authorized JavaScript origins**に追加：
   ```
   https://muscle-form-analyzer.vercel.app
   http://localhost:3000
   ```
3. **Authorized redirect URIs**に追加：
   ```
   https://muscle-form-analyzer.vercel.app/__/auth/handler
   https://tenaxauth.firebaseapp.com/__/auth/handler
   http://localhost:3000/__/auth/handler
   ```
4. **保存**

### 3. 環境変数の確認

#### Vercelダッシュボード設定
1. [Vercel Dashboard](https://vercel.com/)にアクセス
2. プロジェクトを選択
3. **Settings** → **Environment Variables**
4. 以下の変数が正しく設定されているか確認：
   - `NEXT_PUBLIC_FIREBASE_API_KEY`
   - `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN`
   - `NEXT_PUBLIC_FIREBASE_PROJECT_ID`
   - `NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET`
   - `NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID`
   - `NEXT_PUBLIC_FIREBASE_APP_ID`

### 4. デプロイとテスト

#### Step 1: 再デプロイ
```bash
# 変更をコミット
git add .
git commit -m "Fix Google OAuth configuration"
git push origin main
```

#### Step 2: Vercelで再デプロイ
1. Vercelダッシュボード → **Deployments**
2. 最新のデプロイ → **...** → **Redeploy**
3. **Use existing Build Cache**のチェックを外す

#### Step 3: 動作確認
1. `https://muscle-form-analyzer.vercel.app`にアクセス
2. Googleログインボタンをクリック
3. ブラウザのコンソール（F12）でエラーを確認

## 🔍 デバッグ情報

### ブラウザコンソールで確認すべき情報
```javascript
// 以下のログが表示されます
🔍 Google Sign-in Debug:
Auth instance: [object]
Firebase app initialized: true
GoogleAuthProvider created: [object]
Attempting signInWithPopup...
```

### よくあるエラーと対処法

| エラーコード | 意味 | 対処法 |
|------------|-----|--------|
| `auth/unauthorized-domain` | ドメインが認証されていない | Firebase Consoleで認証済みドメインに追加 |
| `auth/operation-not-allowed` | Google認証が無効 | Firebase ConsoleでGoogle認証を有効化 |
| `auth/popup-blocked` | ポップアップがブロックされた | ブラウザのポップアップブロックを解除 |
| `auth/configuration-not-found` | Firebase設定エラー | 環境変数を確認 |

## 📋 チェックリスト

- [ ] Firebase ConsoleでGoogle認証が有効になっている
- [ ] Firebase Consoleで認証済みドメインに`muscle-form-analyzer.vercel.app`が追加されている
- [ ] Google Cloud ConsoleでOAuth設定が正しい
- [ ] Vercelの環境変数が正しく設定されている
- [ ] 再デプロイが完了している
- [ ] ブラウザのポップアップブロックが解除されている

## 🆘 それでも解決しない場合

1. **Firebase Consoleのプロジェクト設定を確認**
   - Project settings → General → Your apps
   - Web appの設定が正しいか確認

2. **新しいOAuth 2.0クライアントIDを作成**
   - Google Cloud Console → Create credentials → OAuth client ID
   - Application type: Web application
   - 上記の認証済みURLを設定

3. **ブラウザのキャッシュをクリア**
   - Ctrl + Shift + R（強制リロード）
   - シークレットウィンドウでテスト

## 📞 サポート

問題が解決しない場合は、以下の情報と共にissueを作成してください：
- ブラウザコンソールのエラーメッセージ
- ネットワークタブのエラー情報
- 実行した手順