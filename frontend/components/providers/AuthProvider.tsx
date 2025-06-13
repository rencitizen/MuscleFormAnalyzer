'use client'

import { createContext, useContext, useEffect, useState } from 'react'
import { 
  User,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  GoogleAuthProvider,
  signInWithPopup,
  getRedirectResult
} from 'firebase/auth'
import { auth } from '../../lib/firebase'
import { useRouter } from 'next/navigation'
import toast from 'react-hot-toast'
import { diagnoseGoogleAuthError, configurePWAGoogleAuth } from '../../lib/auth/googleAuthConfig'

interface AuthContextType {
  user: User | null
  loading: boolean
  signIn: (email: string, password: string) => Promise<void>
  signUp: (email: string, password: string) => Promise<void>
  signInWithGoogle: () => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  signIn: async () => {},
  signUp: async () => {},
  signInWithGoogle: async () => {},
  logout: async () => {},
})

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()
  const isDemoMode = process.env.NEXT_PUBLIC_DEMO_MODE === 'true'

  useEffect(() => {
    // デモモードの場合はダミーユーザーを設定
    if (isDemoMode) {
      setUser({
        uid: 'demo-user',
        email: 'demo@example.com',
        displayName: 'デモユーザー',
      } as User)
      setLoading(false)
      return
    }

    // リダイレクト結果のチェック
    const checkRedirectResult = async () => {
      try {
        const result = await getRedirectResult(auth)
        if (result) {
          console.log('Found redirect result:', result.user?.email)
          toast.success('Googleアカウントでログインしました')
          // /auth/callbackからのリダイレクトを防ぐ
          if (window.location.pathname === '/auth/callback') {
            router.push('/')
          }
        }
      } catch (error) {
        console.error('Redirect result error:', error)
      }
    }

    checkRedirectResult()

    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setUser(user)
      setLoading(false)
    })

    return unsubscribe
  }, [isDemoMode, router])

  const signIn = async (email: string, password: string) => {
    // デモモードの場合
    if (isDemoMode) {
      if (email === 'demo@example.com' && password === 'demo123') {
        setUser({
          uid: 'demo-user',
          email: 'demo@example.com',
          displayName: 'デモユーザー',
        } as User)
        toast.success('デモモードでログインしました')
        router.push('/')
        return
      } else {
        toast.error('デモモードでは demo@example.com / demo123 でログインしてください')
        throw new Error('Invalid demo credentials')
      }
    }

    try {
      await signInWithEmailAndPassword(auth, email, password)
      toast.success('ログインしました')
      router.push('/')
    } catch (error: any) {
      toast.error(error.message || 'ログインに失敗しました')
      throw error
    }
  }

  const signUp = async (email: string, password: string) => {
    try {
      await createUserWithEmailAndPassword(auth, email, password)
      toast.success('アカウントを作成しました')
      router.push('/')
    } catch (error: any) {
      toast.error(error.message || 'アカウント作成に失敗しました')
      throw error
    }
  }

  const signInWithGoogle = async () => {
    try {
      console.log('🔍 Google Sign-in Debug:')
      console.log('Auth instance:', auth)
      console.log('Firebase app:', auth?.app?.name)
      console.log('Current domain:', window.location.hostname)
      console.log('Protocol:', window.location.protocol)
      console.log('Full URL:', window.location.href)
      console.log('Origin:', window.location.origin)
      console.log('Auth domain:', process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN)
      
      const provider = new GoogleAuthProvider()
      const pwaConfig = configurePWAGoogleAuth()
      provider.setCustomParameters(pwaConfig.customParameters)
      
      console.log('GoogleAuthProvider created with custom parameters:', pwaConfig)
      
      // モバイルデバイスの検出
      const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent)
      console.log('Is mobile device:', isMobile)
      
      try {
        console.log('Attempting signInWithPopup...')
        const result = await signInWithPopup(auth, provider)
        
        console.log('Google sign-in successful:', result.user?.email)
        toast.success('Googleアカウントでログインしました')
        router.push('/')
      } catch (popupError: any) {
        console.error('Popup error:', popupError)
        
        // ポップアップがブロックされた場合、リダイレクトを試行
        if (popupError.code === 'auth/popup-blocked' || 
            popupError.code === 'auth/popup-closed-by-user' ||
            isMobile) {
          console.log('Falling back to redirect method...')
          toast.info('リダイレクト方式でログインを試行します...')
          
          const { signInWithRedirect } = await import('firebase/auth')
          await signInWithRedirect(auth, provider)
        } else {
          throw popupError
        }
      }
    } catch (error: any) {
      console.error('❌ Google Sign-in Error:')
      console.error('Error code:', error.code)
      console.error('Error message:', error.message)
      console.error('Full error:', error)
      
      // エラーメッセージマッピング
      const errorMessages: Record<string, string> = {
        'auth/popup-blocked': 'ポップアップがブロックされました。リダイレクト方式を試します。',
        'auth/popup-closed-by-user': 'ログインがキャンセルされました',
        'auth/unauthorized-domain': `認証ドメインエラー: Firebase Consoleで ${window.location.hostname} を追加してください`,
        'auth/operation-not-allowed': 'Google認証が無効です。Firebase Consoleで有効化してください',
        'auth/configuration-not-found': 'Firebase設定エラー。環境変数を確認してください',
        'auth/invalid-api-key': 'APIキーが無効です。Firebase設定を確認してください',
        'auth/internal-error': 'Firebase内部エラー。設定を確認してください',
        'auth/cancelled-popup-request': '別のポップアップが開いています',
        'auth/network-request-failed': 'ネットワークエラー。接続を確認してください'
      }
      
      let errorMessage = errorMessages[error.code] || 'Googleログインに失敗しました'
      
      // Error 400やドメイン認証エラーの詳細診断
      const diagnosis = diagnoseGoogleAuthError(error)
      if (diagnosis) {
        errorMessage = `
🚨 ${diagnosis.title}

修正手順:
${diagnosis.steps.join('\n')}

デバッグ情報:
- 現在のドメイン: ${diagnosis.debugInfo.currentDomain}
- Vercel環境: ${diagnosis.debugInfo.isVercel ? 'はい' : 'いいえ'}
        `
      } else if (error.message?.includes('unauthorized') || 
          error.message?.includes('not authorized') ||
          error.code === 'auth/unauthorized-domain') {
        errorMessage = `
🚨 認証ドメインエラー

必要な設定:
1. Firebase Console → Authentication → Settings → Authorized domains
   追加: ${window.location.hostname}

2. Google Cloud Console → APIs & Services → Credentials
   OAuth 2.0 Client ID 設定:
   - Authorized JavaScript origins: ${window.location.origin}
   - Authorized redirect URIs: ${window.location.origin}/__/auth/handler

3. 環境変数の確認:
   - NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN が正しく設定されているか
        `
      }
      
      toast.error(errorMessage, {
        duration: 10000,
        style: {
          maxWidth: '500px',
          whiteSpace: 'pre-line'
        }
      })
      throw error
    }
  }

  const logout = async () => {
    try {
      await signOut(auth)
      toast.success('ログアウトしました')
      router.push('/auth/login')
    } catch (error: any) {
      toast.error('ログアウトに失敗しました')
      throw error
    }
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        signIn,
        signUp,
        signInWithGoogle,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}