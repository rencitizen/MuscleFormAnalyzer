# Google OAuth Error 400 完全修復ガイド

## 問題の概要
MuscleFormAnalyzerでGoogle OAuth認証時にError 400 (アクセスブロック) が発生しています。
これはFirebase AuthenticationのGoogle Sign-inドメイン設定の問題です。

## 修正手順

### 1. Firebase Console設定
1. [Firebase Console](https://console.firebase.google.com/) にアクセス
2. プロジェクト "tenaxauth" を選択
3. Authentication → Settings → Authorized domains タブを開く
4. 以下のドメインを追加:
   - `localhost` (開発環境用)
   - `*.vercel.app` (Vercelプレビュー環境用)
   - あなたのVercelアプリURL (例: `muscleformanalyzer.vercel.app`)
   - カスタムドメイン (もしあれば)

### 2. Google Cloud Console設定
1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. プロジェクト "tenaxauth" を選択 (Firebase連携プロジェクト)
3. APIs & Services → Credentials を開く
4. OAuth 2.0 Client IDsから "Web client" を編集
5. **Authorized JavaScript origins** に追加:
   ```
   http://localhost:3000
   https://localhost:3000
   https://muscleformanalyzer.vercel.app
   https://muscleformanalyzer-*.vercel.app
   ```
6. **Authorized redirect URIs** に追加:
   ```
   http://localhost:3000/__/auth/handler
   https://localhost:3000/__/auth/handler
   https://muscleformanalyzer.vercel.app/__/auth/handler
   https://muscleformanalyzer-*.vercel.app/__/auth/handler
   ```
7. 「保存」をクリック

### 3. Vercel環境変数設定
1. [Vercel Dashboard](https://vercel.com/dashboard) にアクセス
2. MuscleFormAnalyzerプロジェクトを選択
3. Settings → Environment Variables を開く
4. 以下の環境変数を設定 (すべてProduction, Preview, Developmentで有効に):

```bash
NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSyAjfiJLZkNjx9kqdFdyew7Kno9NXUpGTXI
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=tenaxauth.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=tenaxauth
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=tenaxauth.firebasestorage.app
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=957012960073
NEXT_PUBLIC_FIREBASE_APP_ID=1:957012960073:web:edf5449d38e087ab69f098
```

### 4. デプロイと確認
```bash
# 最新の変更をコミット
git add .
git commit -m "Fix Google OAuth Error 400 - Add domain configuration and error handling"

# Vercelにデプロイ
git push origin main
```

### 5. 動作確認
1. デプロイ完了後、5-10分待つ (Google OAuth設定の反映待ち)
2. ブラウザのキャッシュをクリア
3. Google Sign-inを試行
4. ブラウザコンソールでデバッグ情報を確認

## デバッグ方法

### ブラウザコンソールで確認
```javascript
// 現在のドメイン情報を確認
console.log('Current domain:', window.location.hostname);
console.log('Current origin:', window.location.origin);
console.log('Auth domain:', process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN);
```

### 診断スクリプトの実行
```bash
cd frontend
node scripts/diagnose-google-auth.js
```

## よくあるエラーと対処法

### Error 400: redirect_uri_mismatch
- **原因**: Google Cloud ConsoleのAuthorized redirect URIsが不足
- **対処**: 上記の手順2-6を再確認

### Error 400: unauthorized client
- **原因**: Firebase ConsoleのAuthorized domainsが不足
- **対処**: 上記の手順1-4を再確認

### auth/unauthorized-domain
- **原因**: 現在のドメインが承認されていない
- **対処**: エラーメッセージに表示されるドメインを追加

## 追加の注意事項

1. **設定反映時間**: Google OAuth設定の変更は5-10分かかることがあります
2. **ワイルドカードドメイン**: Vercelプレビュー環境用に `*.vercel.app` を追加
3. **プロトコル**: httpsとhttpの両方を追加（開発環境用）
4. **末尾のスラッシュ**: redirect URIsには末尾スラッシュを付けない

## トラブルシューティング

問題が解決しない場合:
1. Firebase AuthenticationでGoogle Sign-inが有効化されているか確認
2. Google Cloud Consoleでプロジェクトが正しく選択されているか確認
3. ブラウザの開発者ツールでネットワークタブを確認
4. Firebase Consoleでエラーログを確認

## 実装されたエラーハンドリング

- 詳細なエラーメッセージ表示
- 環境別のドメイン自動検出
- PWA対応のリダイレクト処理
- デバッグ情報の自動出力