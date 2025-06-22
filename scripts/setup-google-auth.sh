#!/bin/bash
# Google認証セットアップスクリプト

echo "🔧 Google認証セットアップを開始します..."

# 色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 現在のドメインを取得
if [ -z "$VERCEL_URL" ]; then
    DOMAIN="localhost:3000"
    PROTOCOL="http"
else
    DOMAIN="$VERCEL_URL"
    PROTOCOL="https"
fi

echo -e "${YELLOW}📋 必要な設定項目${NC}"
echo "----------------------------------------"
echo "1. Firebase Console設定"
echo "   - URL: https://console.firebase.google.com"
echo "   - Authentication > Sign-in method > Google を有効化"
echo "   - Authentication > Settings > Authorized domains に以下を追加:"
echo "     * localhost"
echo "     * $DOMAIN"
echo ""
echo "2. Google Cloud Console設定"
echo "   - URL: https://console.cloud.google.com"
echo "   - APIs & Services > Credentials > OAuth 2.0 Client IDs"
echo "   - Authorized JavaScript origins:"
echo "     * $PROTOCOL://$DOMAIN"
echo "     * https://tenaxauth.firebaseapp.com"
echo "   - Authorized redirect URIs:"
echo "     * $PROTOCOL://$DOMAIN/__/auth/handler"
echo "     * https://tenaxauth.firebaseapp.com/__/auth/handler"
echo ""
echo "3. 環境変数設定（.env.local）"
echo "   - Firebase設定は既に完了済み"
echo ""
echo -e "${GREEN}✅ 設定が完了したら、以下のコマンドでテスト:${NC}"
echo "   npm run dev"
echo "   ブラウザで http://localhost:3000/test-auth にアクセス"
echo ""
echo -e "${YELLOW}⚠️  注意事項:${NC}"
echo "   - 設定変更後、5-10分待ってから試してください"
echo "   - ブラウザのキャッシュをクリアすることを推奨"
echo "   - シークレットモードでのテストを推奨"