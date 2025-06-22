# Google認証セットアップガイド

## 概要
このアプリケーションはFirebase Authenticationを使用してGoogle認証を実装しています。
以下の手順に従って設定を行ってください。

## 必要な設定

### 1. Firebase Console での設定

1. [Firebase Console](https://console.firebase.google.com/) にアクセス
2. プロジェクト `tenaxauth` を選択
3. 左メニューから「Authentication」を選択
4. 「Sign-in method」タブをクリック
5. 「Google」プロバイダーを有効化
6. 以下の設定を行う：
   - プロジェクトの公開名: `TENAX FIT`
   - プロジェクトのサポートメール: あなたのメールアドレスを設定

### 2. 承認済みドメインの追加

Firebase Console > Authentication > Settings > Authorized domains で以下のドメインを追加：

**開発環境:**
- `localhost`

**本番環境:**
- `muscleformanalyzer.vercel.app`
- `*.vercel.app`
- あなたのカスタムドメイン（もしあれば）

### 3. Google Cloud Console での OAuth 設定

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. Firebase プロジェクトに対応するGCPプロジェクトを選択
3. 「APIとサービス」→「認証情報」へ移動
4. OAuth 2.0 クライアントIDを確認/作成

**承認済みのJavaScript生成元に追加:**
```
http://localhost:3000
https://muscleformanalyzer.vercel.app
https://tenaxauth.firebaseapp.com
```

**承認済みのリダイレクトURIに追加:**
```
http://localhost:3000/__/auth/handler
https://muscleformanalyzer.vercel.app/__/auth/handler
https://tenaxauth.firebaseapp.com/__/auth/handler
```

### 4. 環境変数の確認

現在の `.env.local` ファイルには以下の設定があります：

```env
# Firebase Configuration - tenaxauth project
NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSyAjfiJLZkNjx9kqdFdyew7Kno9NXUpGTXI
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=tenaxauth.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=tenaxauth
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=tenaxauth.firebasestorage.app
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=957012960073
NEXT_PUBLIC_FIREBASE_APP_ID=1:957012960073:web:edf5449d38e087ab69f098

# Backend API
NEXT_PUBLIC_API_URL=https://muscleformanalyzer-production.up.railway.app

# Enable Demo Mode
NEXT_PUBLIC_DEMO_MODE=false
```

これらの設定は既に正しく設定されています。

### 5. Vercel での環境変数設定

1. [Vercel Dashboard](https://vercel.com/) にアクセス
2. プロジェクトを選択
3. Settings → Environment Variables
4. 上記の環境変数をすべて追加

## トラブルシューティング

### よくあるエラーと解決方法

1. **「auth/unauthorized-domain」エラー**
   - Firebase Console で承認済みドメインにアクセス元のドメインを追加

2. **「auth/popup-blocked」エラー**
   - ブラウザのポップアップブロッカーを無効化
   - または自動的にリダイレクト方式に切り替わります

3. **「auth/operation-not-allowed」エラー**
   - Firebase Console でGoogleプロバイダーが有効になっているか確認

4. **CORS エラー**
   - Google Cloud Console でJavaScript生成元とリダイレクトURIを確認

## 動作確認

1. 開発環境: `npm run dev` でローカルサーバーを起動
2. http://localhost:3000/auth/login にアクセス
3. 「Googleでログイン」ボタンをクリック
4. Googleアカウントを選択してログイン

## 本番環境へのデプロイ

```bash
git add .
git commit -m "fix: Google認証の設定を更新"
git push
```

Vercelが自動的にデプロイを開始します。