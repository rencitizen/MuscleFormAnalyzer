# Vercel環境変数設定ガイド

Vercelのダッシュボードで以下の環境変数を設定してください：

## 必須の環境変数

### Node.js関連
```
NODE_VERSION=20.9.0
NODE_OPTIONS=--max-old-space-size=4096
NPM_CONFIG_LEGACY_PEER_DEPS=true
SKIP_BUILD_STATIC_GENERATION=true
```

### Firebase設定（必須）
```
NEXT_PUBLIC_FIREBASE_API_KEY=your-firebase-api-key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-firebase-auth-domain
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-firebase-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-firebase-storage-bucket
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your-firebase-messaging-sender-id
NEXT_PUBLIC_FIREBASE_APP_ID=your-firebase-app-id
```

### バックエンドAPI URL
```
NEXT_PUBLIC_API_URL=https://tenaxfit-production.up.railway.app
```

### Supabase設定（使用する場合）
```
NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
```

## ビルド設定の確認

Vercelのプロジェクト設定で以下を確認：

1. **Framework Preset**: Next.js
2. **Root Directory**: `frontend`
3. **Build Command**: `npm run build` (デフォルト)
4. **Output Directory**: `.next` (デフォルト)
5. **Install Command**: `npm install` (デフォルト)
6. **Development Command**: `npm run dev`

## トラブルシューティング

### undiciエラーが続く場合
環境変数に以下を追加：
```
SKIP_DEPENDENCY_INSTALL=false
VERCEL_FORCE_NO_BUILD_CACHE=1
```

### メモリ不足エラーの場合
```
NODE_OPTIONS=--max_old_space_size=4096
```

### ビルドタイムアウトの場合
Vercelのプロジェクト設定で「Build & Development Settings」→「Max Build Duration」を増やす（Pro/Enterpriseプランのみ）