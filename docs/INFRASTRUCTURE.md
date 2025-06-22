# TENAX FIT インフラストラクチャ設計書

## 概要
TENAX FIT v3.0は完全無料のインフラストラクチャで構築され、月額コスト0円を実現しています。

## 使用サービス（すべて無料枠）

### フロントエンド
- **Vercel** (無料プラン)
  - 月間100GBの帯域幅
  - 無制限のデプロイ
  - 自動HTTPS
  - エッジネットワーク配信
  - 東京リージョン（hnd1）使用

### バックエンド
- **Railway** (無料クレジット)
  - FastAPIサーバーホスティング
  - 自動デプロイ
  - 環境変数管理
  - ログ監視

### データベース・認証
- **Supabase** (無料プラン)
  - PostgreSQL (500MB)
  - リアルタイムサブスクリプション
  - 認証サービス
  - ストレージ (1GB)

- **Firebase** (無料プラン)
  - Authentication
  - Firestore (1GB)
  - Cloud Storage (5GB)
  - Hosting

### CDN・セキュリティ
- **Cloudflare** (無料プラン)
  - CDN
  - DDoS保護
  - SSL/TLS
  - Web Analytics
  - Page Rules (3個)

### 監視・分析
- **Vercel Analytics** (無料)
- **Sentry** (無料プラン: 月5,000エラー)
- **Google Analytics** (無料)

## CI/CDパイプライン

### GitHub Actions
```yaml
- フロントエンドビルド・テスト
- バックエンドテスト
- セキュリティスキャン
- 依存関係チェック
- Lighthouseパフォーマンステスト
```

### 自動デプロイフロー
1. `main`ブランチへのプッシュ
2. GitHub Actions CI実行
3. Vercel自動デプロイ（フロントエンド）
4. Railway自動デプロイ（バックエンド）

## セキュリティ設定

### HTTPヘッダー（vercel.json）
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Strict-Transport-Security
- Permissions-Policy

### 環境変数管理
- Vercel環境変数（暗号化）
- GitHub Secrets
- Railway環境変数

## パフォーマンス最適化

### フロントエンド
- Next.js静的生成（SSG）
- 画像最適化（next/image）
- コード分割（動的インポート）
- Service Worker（PWA）
- エッジキャッシング

### バックエンド
- FastAPIレスポンスキャッシュ
- データベースクエリ最適化
- 非同期処理
- WebSocket接続プーリング

## 無料枠の使用状況監視

### 監視項目
1. **Vercel**
   - 帯域幅使用量（100GB/月）
   - ビルド時間（6,000分/月）
   - サーバーレス関数実行時間

2. **Supabase**
   - データベース容量（500MB）
   - ストレージ使用量（1GB）
   - 認証ユーザー数（50,000）

3. **Firebase**
   - Firestore読み取り（50,000/日）
   - Cloud Storage（5GB）
   - 認証リクエスト

### アラート設定
- 使用量80%でアラート
- 自動スケーリング無効化
- コスト予測レポート

## 災害復旧計画

### バックアップ
- Supabaseデイリーバックアップ
- GitHubコードバックアップ
- 環境変数のセキュアバックアップ

### フェイルオーバー
- Vercelマルチリージョン対応
- CloudflareキャッシュでのDR
- 静的サイトフォールバック

## 今後の拡張計画

### スケーリング戦略
1. **フェーズ1（現在）**
   - ユーザー数: ~1,000
   - 完全無料インフラ

2. **フェーズ2**
   - ユーザー数: 1,000-10,000
   - Cloudflare Workers活用
   - エッジコンピューティング

3. **フェーズ3**
   - ユーザー数: 10,000+
   - 有料プランへの段階的移行
   - セルフホスティングオプション

## 運用手順

### デプロイ手順
```bash
# フロントエンド
git push origin main
# Vercel自動デプロイ

# バックエンド
git push origin main
# Railway自動デプロイ
```

### 環境変数更新
1. Vercel Dashboard → Settings → Environment Variables
2. Railway Dashboard → Variables
3. GitHub Settings → Secrets

### 監視確認
- Vercel Analytics（日次）
- Sentry エラーログ（随時）
- Cloudflare Analytics（週次）

## コスト管理

### 月額コスト内訳
- Vercel: $0
- Supabase: $0
- Firebase: $0
- Cloudflare: $0
- Railway: $0（無料クレジット使用）
- **合計: $0/月**

### コスト最適化施策
1. 静的アセットのCDN配信
2. API呼び出しの最小化
3. クライアントサイド処理の活用
4. 画像・動画の最適化
5. キャッシュ戦略の最適化