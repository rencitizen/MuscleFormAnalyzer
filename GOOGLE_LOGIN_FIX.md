# Google Login Fix - Complete Implementation Guide

## 🚨 Phase 1: Emergency Fix (今すぐ修正)

### 1. Firebase Console設定
```
1. Firebase Console (https://console.firebase.google.com) にアクセス
2. プロジェクトを選択
3. Authentication → Settings → Authorized domains
4. 以下のドメインを追加:
   - muscle-form-analyzer.vercel.app
   - *.vercel.app (オプション)
   - localhost (開発用)
```

### 2. Google Cloud Console設定
```
1. Google Cloud Console (https://console.cloud.google.com) にアクセス
2. プロジェクトを選択（Firebaseと同じ）
3. APIs & Services → Credentials
4. OAuth 2.0 Client IDs → Web client を編集
5. 以下を設定:

Authorized JavaScript origins:
- https://muscle-form-analyzer.vercel.app
- https://*.vercel.app
- http://localhost:3000

Authorized redirect URIs:
- https://muscle-form-analyzer.vercel.app/__/auth/handler
- https://muscle-form-analyzer.vercel.app
- http://localhost:3000/__/auth/handler
```

### 3. Vercel環境変数確認
```
Vercel Dashboard → Settings → Environment Variables

必須変数:
- NEXT_PUBLIC_FIREBASE_API_KEY
- NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN
- NEXT_PUBLIC_FIREBASE_PROJECT_ID
- NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET
- NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID
- NEXT_PUBLIC_FIREBASE_APP_ID

注意: auth_domainは "[project-id].firebaseapp.com" 形式である必要があります
```

## 🔧 Phase 2: 安定化対策 (実装済み)

### 実装済みの改善点:

1. **PWAメタタグの追加** ✅
   - apple-mobile-web-app-capable
   - 各種アイコンサイズ対応
   - スプラッシュスクリーン設定

2. **manifest.json強化** ✅
   - scope, dir, lang追加
   - 複数アイコンサイズ対応
   - shortcuts定義

3. **OAuth エラーハンドリング強化** ✅
   - ポップアップブロック時の自動リダイレクトフォールバック
   - 詳細なエラーメッセージマッピング
   - モバイルデバイス検出

## 📱 Phase 3: 最適化対策

### 1. リダイレクト方式の実装（推奨）
```typescript
// AuthProvider.tsx に実装済み
// ポップアップがブロックされた場合、自動的にリダイレクト方式に切り替え
```

### 2. getRedirectResult処理
```typescript
// app/auth/callback/page.tsx を作成
'use client'

import { useEffect } from 'react'
import { getRedirectResult } from 'firebase/auth'
import { auth } from '@/lib/firebase'
import { useRouter } from 'next/navigation'
import toast from 'react-hot-toast'

export default function AuthCallbackPage() {
  const router = useRouter()

  useEffect(() => {
    const handleRedirectResult = async () => {
      try {
        const result = await getRedirectResult(auth)
        if (result) {
          console.log('Redirect sign-in successful:', result.user?.email)
          toast.success('ログインしました')
          router.push('/')
        }
      } catch (error: any) {
        console.error('Redirect result error:', error)
        toast.error('ログインに失敗しました')
        router.push('/auth/login')
      }
    }

    handleRedirectResult()
  }, [router])

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h2 className="text-xl font-semibold mb-2">認証処理中...</h2>
        <p className="text-gray-600">しばらくお待ちください</p>
      </div>
    </div>
  )
}
```

## 🎯 デバッグ手順

### 1. Console確認項目
```javascript
// ブラウザのConsoleで確認
console.log('Firebase Config:', {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID
})

// ドメイン確認
console.log('Current domain:', window.location.hostname)
console.log('Current origin:', window.location.origin)
```

### 2. ネットワーク確認
```
Chrome DevTools → Network タブ
1. Googleログインボタンクリック
2. identitytoolkit.googleapis.com へのリクエストを確認
3. エラーレスポンスの詳細を確認
```

## 🚀 即座に試すテスト手順

1. **ローカルテスト**
   ```bash
   cd frontend
   npm run dev
   # http://localhost:3000 でテスト
   ```

2. **本番テスト**
   ```bash
   git add .
   git commit -m "Fix Google login with enhanced OAuth handling and PWA support"
   git push origin main
   # Vercelの自動デプロイを待つ
   ```

3. **確認ポイント**
   - Googleログインボタンクリック
   - ポップアップまたはリダイレクト発生
   - エラーメッセージの内容確認
   - Console.logの出力確認

## 📝 よくあるエラーと対処法

### 1. "auth/unauthorized-domain"
**原因**: ドメインが承認されていない
**対処**: Firebase ConsoleとGoogle Cloud Consoleでドメイン追加

### 2. "auth/popup-blocked"
**原因**: ブラウザがポップアップをブロック
**対処**: 自動的にリダイレクト方式に切り替わる（実装済み）

### 3. "auth/operation-not-allowed"
**原因**: Google認証が無効
**対処**: Firebase Console → Authentication → Sign-in method → Google を有効化

### 4. "auth/invalid-api-key"
**原因**: APIキーが間違っている
**対処**: Vercel環境変数を再確認

## ✅ チェックリスト

- [ ] Firebase Console: Authorized domainsに本番ドメイン追加
- [ ] Google Cloud Console: OAuth設定完了
- [ ] Vercel: 環境変数6つすべて設定
- [ ] PWAメタタグ: layout.tsxに追加済み
- [ ] manifest.json: 更新済み
- [ ] AuthProvider: エラーハンドリング強化済み
- [ ] ローカルテスト: 成功
- [ ] 本番デプロイ: 完了

## 🆘 それでも解決しない場合

1. **Firebase設定リセット**
   - 新しいWebアプリを作成
   - 新しい設定値をVercelに設定

2. **OAuth同意画面確認**
   - Google Cloud Console → OAuth consent screen
   - アプリケーション名、サポートメール設定

3. **ドメイン検証**
   - Google Search Console でドメイン所有権確認
   - DNS設定確認

## 📧 サポート連絡先

問題が解決しない場合:
1. Firebaseサポート: https://firebase.google.com/support
2. Vercelサポート: https://vercel.com/support
3. プロジェクト管理者に連絡

---

最終更新: 2025-01-06
実装者: Claude Code Assistant