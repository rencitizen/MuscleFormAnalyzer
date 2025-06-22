# Google認証を有効にする手順

## 現在の状況
- Firebase認証は既に実装済み
- 環境変数は設定済み
- Google認証を有効にするには、Firebase ConsoleとGoogle Cloud Consoleでの設定が必要

## 必要な設定手順

### 1. Firebase Consoleでの設定

1. https://console.firebase.google.com にアクセス
2. プロジェクト「tenaxauth」を選択
3. 左メニューから「Authentication」→「Sign-in method」を選択
4. 「Google」をクリックして有効化
5. プロジェクトの公開名: `TENAX FIT`
6. サポートメール: あなたのメールアドレスを入力
7. 「保存」をクリック

### 2. 承認済みドメインの追加

Firebase Console > Authentication > Settings > Authorized domains で以下を追加：

- `localhost` (開発用)
- `muscleformanalyzer.vercel.app` (本番用)
- あなたのVercelプレビューURL (例: `muscleformanalyzer-xxx.vercel.app`)

### 3. Google Cloud Consoleでの設定

1. https://console.cloud.google.com にアクセス
2. プロジェクトを「tenaxauth」に切り替え
3. 「APIとサービス」→「認証情報」へ移動
4. 「Web client (auto created by Google Service)」をクリック

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

5. 「保存」をクリック

## テスト方法

### ローカルでのテスト
```bash
cd frontend
npm run dev
```

1. http://localhost:3000/test-auth にアクセス
2. 「Google認証をテスト」ボタンをクリック
3. エラーが出た場合は、エラーメッセージに従って設定を修正

### 本番環境へのデプロイ
```bash
git add .
git commit -m "feat: Google認証テストページを追加"
git push
```

## よくあるエラーと対処法

### 1. auth/unauthorized-domain エラー
- Firebase Consoleで現在アクセスしているドメインを承認済みドメインに追加

### 2. auth/operation-not-allowed エラー
- Firebase ConsoleでGoogleプロバイダーが有効になっているか確認

### 3. Error 400: invalid_request
- Google Cloud ConsoleでJavaScript生成元とリダイレクトURIを確認

## 確認用URL
- テストページ: `/test-auth`
- ログインページ: `/auth/login`

設定が完了したら、通常のログインページ（/auth/login）でもGoogle認証が動作するようになります。