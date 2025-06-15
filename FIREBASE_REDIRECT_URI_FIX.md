# 🚨 redirect_uri_mismatch エラーの修正方法

## 問題の原因
Firebaseの認証フローでは、実際のリダイレクトURIとGoogle Cloud Consoleに登録されているURIが完全に一致する必要があります。

## 🔧 即座に修正する手順

### 1. エラーメッセージから正しいリダイレクトURIを確認

エラー画面に表示される情報を確認：
- エラーの詳細をクリック
- 「リクエストの詳細」セクションで `redirect_uri` パラメータの値を確認
- その値を正確にコピー

### 2. Google Cloud Console で設定を更新

1. [Google Cloud Console](https://console.cloud.google.com/apis/credentials?project=tenaxauth) を開く

2. OAuth 2.0 Client ID をクリックして編集

3. **承認済みのリダイレクト URI** に以下をすべて追加：

```
https://muscle-form-analyzer-git-main-ren-fujiokas-projects.vercel.app/__/auth/handler
https://tenaxauth.firebaseapp.com/__/auth/handler
http://localhost:3000/__/auth/handler
```

### 3. 重要: Firebaseのauthドメインも確認

FirebaseのGoogle認証では、`authDomain` の設定が重要です。

**環境変数を確認**:
```
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=tenaxauth.firebaseapp.com
```

この場合、リダイレクトURIは以下の形式になることがあります：
```
https://tenaxauth.firebaseapp.com/__/auth/handler
```

## 🎯 完全な設定リスト

### Google Cloud Console - 承認済みの JavaScript 生成元
```
http://localhost
http://localhost:3000
https://tenaxauth.firebaseapp.com
https://muscle-form-analyzer-git-main-ren-fujiokas-projects.vercel.app
```

### Google Cloud Console - 承認済みのリダイレクト URI
```
http://localhost:3000/__/auth/handler
https://tenaxauth.firebaseapp.com/__/auth/handler
https://muscle-form-analyzer-git-main-ren-fujiokas-projects.vercel.app/__/auth/handler
```

## 🔍 デバッグ方法

### ブラウザの開発者ツールで確認

1. ネットワークタブを開く
2. Googleログインボタンをクリック
3. `accounts.google.com` へのリクエストを探す
4. そのリクエストのパラメータで `redirect_uri` の値を確認

### 正確なリダイレクトURIを見つける方法

```javascript
// ブラウザコンソールで実行
console.log('Auth Domain:', 'tenaxauth.firebaseapp.com');
console.log('Expected redirect URI:', 'https://tenaxauth.firebaseapp.com/__/auth/handler');
console.log('Current Origin:', window.location.origin);
console.log('Possible redirect URI:', window.location.origin + '/__/auth/handler');
```

## ⚡ 緊急対応

もしまだエラーが続く場合、以下を試してください：

### オプション1: signInWithPopup のみを使用

`frontend/components/providers/AuthProvider.tsx` を編集：

```typescript
const signInWithGoogle = async () => {
  try {
    const provider = new GoogleAuthProvider();
    // リダイレクトURIを明示的に設定しない
    const result = await signInWithPopup(auth, provider);
    toast.success('Googleアカウントでログインしました');
    router.push('/');
  } catch (error: any) {
    console.error('Google sign-in error:', error);
    toast.error('Googleログインに失敗しました');
    throw error;
  }
}
```

### オプション2: Firebase Hostingを使用

もし継続的に問題がある場合、Firebase Hostingを使用することで、`tenaxauth.firebaseapp.com` ドメインでアプリをホストできます。

## 📋 チェックリスト

- [ ] エラーメッセージから正確なredirect_uriを確認した
- [ ] Google Cloud Consoleにすべての必要なURIを追加した
- [ ] Firebase auth domainが正しく設定されている
- [ ] 5-10分待った
- [ ] ブラウザのキャッシュをクリアした
- [ ] シークレットモードでテストした

## 🆘 それでも解決しない場合

1. Firebase Consoleで新しいWebアプリを作成
2. 新しい認証情報でGoogle Cloud Consoleを設定
3. Vercelの環境変数を更新

---

**重要**: `redirect_uri_mismatch` エラーは、登録されているURIと実際のリクエストのURIが1文字でも違うと発生します。スペースや末尾のスラッシュにも注意してください。