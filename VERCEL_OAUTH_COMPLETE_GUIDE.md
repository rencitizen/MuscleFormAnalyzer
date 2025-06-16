# Vercel OAuth認証 完全設定ガイド

## 🎯 このガイドの目的
Vercelデプロイ後のGoogle OAuth認証エラー（Error 400、redirect_uri_mismatch等）を確実に解決する

## 📋 前提条件
- Firebaseプロジェクトが作成済み
- Google Cloud Consoleへのアクセス権限
- Vercelにデプロイ済み
- 環境変数が設定済み

## 🚀 クイックスタート

### 現在のドメイン情報
```
新ドメイン: muscle-form-analyzer-c5ukwtnbq-ren-fujiokas-projects.vercel.app
```

### 1分で確認すべきポイント
1. **Firebase Console** → Authentication → Settings → Authorized domains に上記ドメイン追加
2. **Google Cloud Console** → OAuth 2.0 設定に上記ドメイン追加
3. **5-10分待機**（設定反映のため）
4. **ブラウザキャッシュクリア** → シークレットモードでテスト

## 📝 詳細設定手順

### ステップ1: Firebase Console設定

#### 1-1. Authorized Domains追加
```
1. https://console.firebase.google.com にアクセス
2. プロジェクト選択
3. Authentication → Settings → Authorized domains
4. "Add domain" をクリック
5. 以下を正確に入力:
   muscle-form-analyzer-c5ukwtnbq-ren-fujiokas-projects.vercel.app
6. "Add" をクリック
```

**確認ポイント:**
- ✅ ドメイン名が完全一致
- ✅ HTTPSプロトコルは自動設定
- ✅ 余分なスペースなし
- ✅ localhostも残っている

### ステップ2: Google Cloud Console設定

#### 2-1. OAuth 2.0 Client ID設定
```
1. https://console.cloud.google.com にアクセス
2. Firebaseと同じプロジェクトを選択（重要！）
3. APIs & Services → Credentials
4. OAuth 2.0 Client IDs → Web client をクリック
```

#### 2-2. Authorized JavaScript origins
**追加する値（コピペ推奨）:**
```
https://muscle-form-analyzer-c5ukwtnbq-ren-fujiokas-projects.vercel.app
```

**注意事項:**
- ⚠️ `https://` を必ず含める
- ⚠️ 末尾にスラッシュ（/）は付けない
- ⚠️ 既存のlocalhostは削除しない

#### 2-3. Authorized redirect URIs
**追加する値（両方とも追加）:**
```
https://muscle-form-analyzer-c5ukwtnbq-ren-fujiokas-projects.vercel.app/__/auth/handler
https://muscle-form-analyzer-c5ukwtnbq-ren-fujiokas-projects.vercel.app/auth/callback
```

#### 2-4. 保存
「Save」ボタンをクリック（画面下部）

### ステップ3: 環境変数確認

#### 3-1. Vercel Dashboard確認
```
1. https://vercel.com/dashboard にアクセス
2. プロジェクト選択
3. Settings → Environment Variables
4. 以下の変数がすべて設定されているか確認:
```

**必須環境変数チェックリスト:**
- [ ] `NEXT_PUBLIC_FIREBASE_API_KEY`
- [ ] `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN`
- [ ] `NEXT_PUBLIC_FIREBASE_PROJECT_ID`
- [ ] `NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET`
- [ ] `NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID`
- [ ] `NEXT_PUBLIC_FIREBASE_APP_ID`

### ステップ4: デバッグと検証

#### 4-1. デバッグツール使用
```bash
# ローカルで検証スクリプトを実行
cd frontend
node scripts/verify-oauth-setup.js muscle-form-analyzer-c5ukwtnbq-ren-fujiokas-projects.vercel.app
```

#### 4-2. ブラウザでデバッグパネル確認
1. `https://muscle-form-analyzer-c5ukwtnbq-ren-fujiokas-projects.vercel.app/auth/login` にアクセス
2. 画面右下の「OAuth診断ツール」をクリック
3. すべての項目が緑色（成功）になっているか確認

#### 4-3. コンソールログ確認
```javascript
// ブラウザのデベロッパーツール（F12）で確認
// 以下のようなログが表示されるはず:
🔍 Google Sign-in Debug:
Auth instance: [object]
Current domain: muscle-form-analyzer-c5ukwtnbq-ren-fujiokas-projects.vercel.app
Protocol: https:
```

## 🔧 トラブルシューティング

### エラー別対処法

#### Error 400: redirect_uri_mismatch
**原因:** Google OAuthの設定にドメインが追加されていない
**解決策:**
1. Google Cloud Console → OAuth 2.0 設定を再確認
2. Authorized JavaScript originsとRedirect URIsの両方を確認
3. 保存後、5-10分待機

#### auth/unauthorized-domain
**原因:** Firebase Authorized domainsに追加されていない
**解決策:**
1. Firebase Console → Authentication → Settings
2. Authorized domainsに正確なドメインを追加
3. 保存後、即座に反映されるはず

#### ポップアップブロック
**原因:** ブラウザがポップアップをブロック
**解決策:**
1. アドレスバーのポップアップブロックアイコンをクリック
2. 「常に許可」を選択
3. 自動的にリダイレクト方式にフォールバック

### 一般的な問題と解決策

| 問題 | 原因 | 解決策 |
|------|------|--------|
| 設定しても動かない | キャッシュ | ブラウザキャッシュをクリア、シークレットモードで試す |
| localhost は動くが本番が動かない | ドメイン設定漏れ | 本番ドメインをFirebaseとGoogleの両方に追加 |
| 突然動かなくなった | Vercel再デプロイでURL変更 | 新しいURLで再設定 |
| Error 400が消えない | 設定反映待ち | 10-15分待ってから再試行 |

## 🛠️ 開発者向けデバッグ情報

### コンポーネント構成
```
frontend/
├── components/
│   ├── auth/
│   │   └── OAuthDebugPanel.tsx    # OAuth診断ツール
│   └── providers/
│       └── AuthProvider.tsx        # 認証プロバイダー（エラーハンドリング強化）
├── lib/
│   ├── auth/
│   │   ├── googleAuthConfig.ts    # Google OAuth設定
│   │   └── authErrorHandler.ts    # エラーハンドラー（新規追加）
│   └── firebase.ts                 # Firebase初期化
└── scripts/
    └── verify-oauth-setup.js       # 設定検証スクリプト（新規追加）
```

### 追加された機能
1. **OAuthDebugPanel**: リアルタイムで設定状態を診断
2. **authErrorHandler**: Vercel特有のエラーに対する詳細な解決策を提供
3. **verify-oauth-setup.js**: コマンドラインから設定を検証

### エラーハンドリングの改善
```typescript
// 新しいエラーハンドラーが以下を提供:
- エラーコード別の詳細な解決手順
- 推定修正時間
- 現在のドメイン情報を含むデバッグ情報
- Vercel環境の自動検出
```

## 📅 メンテナンス

### 定期確認事項
- [ ] Vercel再デプロイ時のURL変更確認
- [ ] Firebase/Google Cloud設定の定期レビュー
- [ ] 環境変数の有効性確認

### URLが変更された場合
1. 新しいURLを確認
2. Firebase ConsoleとGoogle Cloud Consoleで旧URLを新URLに更新
3. 5-10分待機
4. テスト実施

## 🆘 サポート

### それでも解決しない場合
1. **OAuth診断ツール**のスクリーンショットを撮影
2. **ブラウザコンソール**のエラーメッセージをコピー
3. **ネットワークタブ**で失敗したリクエストの詳細を確認
4. 以下の情報と共にイシューを作成:
   - 使用ブラウザとバージョン
   - 実行した手順
   - エラーメッセージ全文
   - OAuth診断ツールの結果

## ✅ 最終チェックリスト

設定完了後、以下をすべて確認:

- [ ] Firebase Authorized domainsに追加完了
- [ ] Google OAuth JavaScript origins追加完了
- [ ] Google OAuth Redirect URIs追加完了（2つとも）
- [ ] Vercel環境変数確認完了
- [ ] 10分以上待機完了
- [ ] ブラウザキャッシュクリア完了
- [ ] シークレットモードでテスト成功
- [ ] OAuth診断ツールですべて緑色表示

すべてチェックできたら、Google OAuth認証が正常に動作するはずです！