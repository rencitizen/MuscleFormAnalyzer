# Firebase Authentication & Google OAuth 設定ガイド

## 🚨 重要な情報
- **Firebase プロジェクト名**: `tenaxauth`
- **Vercel デプロイ URL**: `muscle-form-analyzer-git-main-ren-fujiokas-projects.vercel.app`
- **設定が必要な箇所**: Firebase Console と Google Cloud Console の両方

## 📋 設定手順

### 1. Firebase Console での設定

#### ステップ 1-1: Firebase Console にアクセス
1. [Firebase Console](https://console.firebase.google.com/) にログイン
2. プロジェクト「**tenaxauth**」を選択（⚠️ MuscleFormAnalyzerではありません）

#### ステップ 1-2: 承認済みドメインの追加
1. 左サイドバーから「**Authentication**」をクリック
2. 上部タブから「**Settings**」（設定）をクリック
3. 「**Authorized domains**」（承認済みドメイン）タブを選択
4. 「**Add domain**」（ドメインを追加）ボタンをクリック
5. 以下のドメインを追加:
   ```
   muscle-form-analyzer-git-main-ren-fujiokas-projects.vercel.app
   ```
6. 「**Add**」をクリックして保存

✅ **確認**: 以下のドメインがリストに含まれているか確認
- `localhost`
- `tenaxauth.firebaseapp.com`
- `muscle-form-analyzer-git-main-ren-fujiokas-projects.vercel.app`（新規追加）

### 2. Google Cloud Console での OAuth 設定

#### ステップ 2-1: Google Cloud Console にアクセス
1. [Google Cloud Console](https://console.cloud.google.com/) にログイン
2. プロジェクトセレクタで「**tenaxauth**」プロジェクトを選択

#### ステップ 2-2: OAuth 2.0 認証情報ページへ移動
1. 左サイドバーのメニューを開く（☰）
2. 「**APIs & Services**」（APIとサービス）→「**Credentials**」（認証情報）をクリック

#### ステップ 2-3: OAuth 2.0 クライアントIDの編集
1. 「**OAuth 2.0 Client IDs**」セクションで、Web クライアントの名前をクリック
2. 編集画面が開きます

#### ステップ 2-4: 承認済みの JavaScript 生成元を追加
「**Authorized JavaScript origins**」（承認済みの JavaScript 生成元）セクション:

1. 「**ADD URI**」をクリック
2. 以下のURIを追加:
   ```
   https://muscle-form-analyzer-git-main-ren-fujiokas-projects.vercel.app
   ```

✅ **完成後のリスト**:
```
http://localhost:3000
https://muscle-form-analyzer-git-main-ren-fujiokas-projects.vercel.app
```

#### ステップ 2-5: 承認済みのリダイレクト URI を追加
「**Authorized redirect URIs**」（承認済みのリダイレクト URI）セクション:

1. 「**ADD URI**」を2回クリック
2. 以下の2つのURIを追加:
   ```
   https://muscle-form-analyzer-git-main-ren-fujiokas-projects.vercel.app/__/auth/handler
   https://muscle-form-analyzer-git-main-ren-fujiokas-projects.vercel.app/auth/callback
   ```

✅ **完成後のリスト**:
```
http://localhost:3000/__/auth/handler
http://localhost:3000/auth/callback
https://muscle-form-analyzer-git-main-ren-fujiokas-projects.vercel.app/__/auth/handler
https://muscle-form-analyzer-git-main-ren-fujiokas-projects.vercel.app/auth/callback
```

#### ステップ 2-6: 設定を保存
1. ページ下部の「**SAVE**」ボタンをクリック
2. 「Changes saved」というメッセージが表示されることを確認

### 3. 設定反映の待機とテスト

#### ⏰ 重要: 待機時間
```
設定変更後、5-10分待ってください
（Google側でキャッシュが更新されるまで時間がかかります）
```

#### 🧹 ブラウザのクリーンアップ
1. **ハードリフレッシュ**: `Ctrl + Shift + R` (Windows) / `Cmd + Shift + R` (Mac)
2. **シークレット/プライベートモード**で新しいウィンドウを開く
3. **Cookieとキャッシュをクリア**（必要に応じて）

### 4. 動作確認

#### テスト手順
1. https://muscle-form-analyzer-git-main-ren-fujiokas-projects.vercel.app にアクセス
2. 「Googleでログイン」ボタンをクリック
3. Googleアカウント選択画面が表示されることを確認
4. ログイン後、正常にアプリに戻ることを確認

#### デバッグ用コンソールコマンド
ブラウザの開発者ツール（F12）で以下を実行:
```javascript
// 現在のドメインを確認
console.log('Current domain:', window.location.hostname);

// Firebase設定を確認
console.log('Auth domain:', 'tenaxauth.firebaseapp.com');
```

## 🔍 トラブルシューティング

### エラー: "Error 400: redirect_uri_mismatch"
**原因**: リダイレクトURIが設定されていない
**解決**: ステップ2-5を再確認し、正確なURIを追加

### エラー: "This app isn't verified"
**原因**: アプリが未検証（開発中は正常）
**解決**: 
- 開発中: 「Advanced」→「Go to [app name] (unsafe)」をクリック
- 本番: Google にアプリ検証を申請

### エラー: "auth/unauthorized-domain"
**原因**: Firebaseで承認されていないドメイン
**解決**: ステップ1-2を再確認

## ✅ チェックリスト

- [ ] Firebase Console で承認済みドメインを追加した
- [ ] Google Cloud Console で JavaScript 生成元を追加した
- [ ] Google Cloud Console でリダイレクトURIを追加した（2つ）
- [ ] 設定を保存した
- [ ] 5-10分待った
- [ ] ブラウザをリフレッシュした
- [ ] テストが成功した

## 📝 メモ

### Vercel カスタムドメインを使用する場合
カスタムドメイン（例: `tenaxfit.com`）を設定した場合は、そのドメインも同様に追加してください:

```
承認済みドメイン: tenaxfit.com
JavaScript生成元: https://tenaxfit.com
リダイレクトURI: 
- https://tenaxfit.com/__/auth/handler
- https://tenaxfit.com/auth/callback
```

### 複数の環境を管理する場合
開発、ステージング、本番環境がある場合は、それぞれのURLを追加してください。

## 🆘 サポート

設定後も問題が解決しない場合は、以下の情報を確認してください:
1. Firebase プロジェクトID が正しいか（`tenaxauth`）
2. Vercel の環境変数が正しく設定されているか
3. ブラウザのコンソールエラーの詳細

---

最終更新: 2024年1月
Firebase プロジェクト: tenaxauth