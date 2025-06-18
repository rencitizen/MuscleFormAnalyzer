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
import { formatErrorMessage, shouldRetryWithRedirect } from '../../lib/auth/authErrorHandler'

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
      
      // Firebase設定の詳細ログ
      console.log('🔧 Firebase Configuration:')
      console.log('API Key exists:', !!process.env.NEXT_PUBLIC_FIREBASE_API_KEY)
      console.log('Auth Domain:', process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN)
      console.log('Project ID:', process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID)
      console.log('All env vars:', Object.keys(process.env).filter(key => key.startsWith('NEXT_PUBLIC_FIREBASE')))
      
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
        console.error('❌ Popup error:', popupError)
        console.error('Error details:', {
          code: popupError.code,
          message: popupError.message,
          customData: popupError.customData,
          name: popupError.name
        })
        
        // ポップアップがブロックされた場合、リダイレクトを試行
        if (shouldRetryWithRedirect(popupError) || isMobile) {
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
      
      // 新しいエラーハンドラーを使用
      const errorMessage = formatErrorMessage(error)
      
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