# 🚨 Googleログイン緊急チェックリスト

## 1. **5分以内にできる確認作業**

### A. ブラウザでの即時確認
```javascript
// 1. https://muscle-form-analyzer.vercel.app にアクセス
// 2. F12キーで開発者ツールを開く
// 3. Consoleタブで以下を確認:

// 以下のようなデバッグログが表示されているか確認
🔍 Google Sign-in Debug:
Auth instance: [object]
Firebase app: [app-name]
Current domain: muscle-form-analyzer.vercel.app
Protocol: https:

// エラーメッセージを確認
❌ Google Sign-in Error:
Error code: auth/unauthorized-domain
```

### B. Vercel環境変数の確認
1. https://vercel.com/dashboard にログイン
2. プロジェクト → Settings → Environment Variables
3. 以下の変数が**すべて**設定されているか確認:
   - `NEXT_PUBLIC_FIREBASE_API_KEY`
   - `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN`
   - `NEXT_PUBLIC_FIREBASE_PROJECT_ID`
   - `NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET`
   - `NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID`
   - `NEXT_PUBLIC_FIREBASE_APP_ID`

### C. Firebase Console の確認
1. https://console.firebase.google.com にアクセス
2. Authentication → Sign-in method → Google が**有効**か確認
3. Authentication → Settings → Authorized domains に以下があるか:
   - `muscle-form-analyzer.vercel.app`
   - `localhost`

## 2. **エラー別の即座の対処法**

### エラー: `auth/unauthorized-domain`
**原因**: ドメインが承認されていない
**対処**:
1. Firebase Console → Authentication → Settings → Authorized domains
2. 「Add domain」をクリック
3. `muscle-form-analyzer.vercel.app` を追加
4. 保存

### エラー: `auth/configuration-not-found`
**原因**: Firebase設定が見つからない
**対処**:
1. Vercel Dashboard で環境変数を再確認
2. 各変数の値にスペースや改行がないか確認
3. 「Redeploy」で再デプロイ（Use cache のチェックを外す）

### エラー: `auth/operation-not-allowed`
**原因**: Google認証が無効
**対処**:
1. Firebase Console → Authentication → Sign-in method
2. Google をクリックして「有効にする」
3. プロジェクトのサポートメールを設定
4. 保存

## 3. **テストコマンド実行**

```bash
# ローカルでテスト
cd frontend
npm run dev

# ブラウザで http://localhost:3000/auth/login にアクセス
# Googleログインボタンをクリック
# コンソールのエラーメッセージを確認
```

## 4. **Google Cloud Console 設定（重要）**

1. https://console.cloud.google.com にアクセス
2. Firebaseプロジェクトと同じプロジェクトを選択
3. APIs & Services → Credentials
4. OAuth 2.0 Client IDs → Web client (auto created by Firebase)を編集

**Authorized JavaScript origins に追加:**
```
https://muscle-form-analyzer.vercel.app
https://tenaxauth.firebaseapp.com
http://localhost:3000
```

**Authorized redirect URIs に追加:**
```
https://muscle-form-analyzer.vercel.app/__/auth/handler
https://tenaxauth.firebaseapp.com/__/auth/handler
http://localhost:3000/__/auth/handler
```

## 5. **確認用スクリプト実行**

```bash
# 環境変数とPWA設定の確認
cd frontend
node scripts/test-google-auth.js
```

## 6. **最終確認チェックリスト**

- [ ] Firebase ConsoleでGoogle認証が有効
- [ ] 承認済みドメインに本番URLが追加済み
- [ ] Vercelに6つの環境変数すべて設定済み
- [ ] Google Cloud ConsoleでOAuth設定完了
- [ ] ブラウザキャッシュをクリア
- [ ] プライベートモードでテスト

## 7. **それでも動かない場合**

### A. Firebase設定のリセット
1. Firebase Console → Project settings → General
2. 「Add app」→ Web を選択
3. 新しい設定値を取得
4. Vercelの環境変数を更新

### B. デバッグ情報の収集
```javascript
// ブラウザコンソールで実行
console.log('Firebase Config:', {
  apiKey: window.__NEXT_DATA__?.props?.pageProps?.firebaseConfig?.apiKey || 'NOT FOUND',
  authDomain: window.__NEXT_DATA__?.props?.pageProps?.firebaseConfig?.authDomain || 'NOT FOUND',
  currentDomain: window.location.hostname
});
```

### C. 代替認証方法
1. メールアドレス認証を一時的に使用
2. `/auth/register` でアカウント作成
3. メール/パスワードでログイン

---

**緊急連絡先**:
- Firebaseサポート: https://firebase.google.com/support
- Vercelサポート: https://vercel.com/support

**推定解決時間**: 15-30分（設定確認と修正）