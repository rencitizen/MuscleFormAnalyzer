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
import { auth } from '@/lib/firebase'
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
      const provider = new GoogleAuthProvider()
      await signInWithPopup(auth, provider)
      toast.success('Googleアカウントでログインしました')
      router.push('/')
    } catch (error: any) {
      toast.error(error.message || 'Googleログインに失敗しました')
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