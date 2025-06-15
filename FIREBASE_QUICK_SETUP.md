# 🚀 Firebase OAuth クイック設定リファレンス

## 📌 コピー&ペースト用の設定値

### Firebase Console - 承認済みドメイン
```
muscle-form-analyzer-git-main-ren-fujiokas-projects.vercel.app
```

### Google Cloud Console - JavaScript 生成元
```
https://muscle-form-analyzer-git-main-ren-fujiokas-projects.vercel.app
```

### Google Cloud Console - リダイレクトURI（2つ）
```
https://muscle-form-analyzer-git-main-ren-fujiokas-projects.vercel.app/__/auth/handler
https://muscle-form-analyzer-git-main-ren-fujiokas-projects.vercel.app/auth/callback
```

## 🔗 直接アクセスリンク

1. **Firebase Console - 承認済みドメイン設定**
   ```
   https://console.firebase.google.com/project/tenaxauth/authentication/settings
   ```

2. **Google Cloud Console - OAuth設定**
   ```
   https://console.cloud.google.com/apis/credentials?project=tenaxauth
   ```

## ⚡ 最速設定手順

### 1️⃣ Firebase（1分）
1. [このリンク](https://console.firebase.google.com/project/tenaxauth/authentication/settings)を開く
2. 「Authorized domains」タブ
3. 「Add domain」→ 上記ドメインをペースト → 「Add」

### 2️⃣ Google Cloud（2分）
1. [このリンク](https://console.cloud.google.com/apis/credentials?project=tenaxauth)を開く
2. Web Client をクリック
3. JavaScript origins に HTTPS URL を追加
4. Redirect URIs に 2つの URL を追加
5. 「SAVE」

### 3️⃣ 待機&テスト（5-10分）
1. 5-10分待つ
2. シークレットモードで https://muscle-form-analyzer-git-main-ren-fujiokas-projects.vercel.app を開く
3. Googleログインをテスト

## 🎯 設定完了の確認方法

ブラウザコンソール（F12）で実行:
```javascript
// これが true なら設定OK
window.location.hostname === 'muscle-form-analyzer-git-main-ren-fujiokas-projects.vercel.app'
```

---
プロジェクト: **tenaxauth** | 更新日: 2024年1月