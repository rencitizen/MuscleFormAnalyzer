'use client'

import { createContext, useContext, useEffect, useState } from 'react'
import { 
  User,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  GoogleAuthProvider,
  signInWithPopup
} from 'firebase/auth'
import { auth } from '../../lib/firebase'
import { useRouter } from 'next/navigation'
import toast from 'react-hot-toast'

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

    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setUser(user)
      setLoading(false)
    })

    return unsubscribe
  }, [isDemoMode])

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
      console.log('Firebase app initialized:', !!auth?.app)
      
      const provider = new GoogleAuthProvider()
      console.log('GoogleAuthProvider created:', provider)
      
      // ポップアップの代わりにリダイレクトを試すオプション
      console.log('Attempting signInWithPopup...')
      const result = await signInWithPopup(auth, provider)
      
      console.log('Google sign-in successful:', result.user?.email)
      toast.success('Googleアカウントでログインしました')
      router.push('/')
    } catch (error: any) {
      console.error('❌ Google Sign-in Error:')
      console.error('Error code:', error.code)
      console.error('Error message:', error.message)
      console.error('Full error:', error)
      
      // より詳細なエラーメッセージ
      let errorMessage = 'Googleログインに失敗しました'
      
      if (error.code === 'auth/popup-blocked') {
        errorMessage = 'ポップアップがブロックされました。ブラウザの設定を確認してください'
      } else if (error.code === 'auth/popup-closed-by-user') {
        errorMessage = 'ログインがキャンセルされました'
      } else if (error.code === 'auth/unauthorized-domain') {
        errorMessage = 'このドメインは認証されていません。Firebase Consoleで設定してください'
      } else if (error.code === 'auth/operation-not-allowed') {
        errorMessage = 'Google認証が有効になっていません。Firebase Consoleで設定してください'
      } else if (error.code === 'auth/configuration-not-found') {
        errorMessage = 'Firebase設定が見つかりません。環境変数を確認してください'
      } else if (error.message?.includes('domain is not authorized')) {
        errorMessage = '認証ドメインエラー: Firebase ConsoleとGoogle Cloud Consoleで以下を設定してください:\n1. Firebase → Authentication → Settings → Authorized domains に muscle-form-analyzer.vercel.app を追加\n2. Google Cloud Console → APIs & Services → Credentials → OAuth 2.0 Client IDs で Authorized JavaScript origins と Authorized redirect URIs を設定'
      }
      
      toast.error(errorMessage)
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