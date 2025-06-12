'use client'

import { useEffect } from 'react'
import { getRedirectResult } from 'firebase/auth'
import { auth } from '@/lib/firebase'
import { useRouter } from 'next/navigation'
import toast from 'react-hot-toast'
import { Loader2 } from 'lucide-react'

export default function AuthCallbackPage() {
  const router = useRouter()

  useEffect(() => {
    const handleRedirectResult = async () => {
      try {
        console.log('Handling auth redirect result...')
        const result = await getRedirectResult(auth)
        
        if (result) {
          console.log('Redirect sign-in successful:', result.user?.email)
          toast.success('Googleアカウントでログインしました')
          router.push('/')
        } else {
          // リダイレクト結果がない場合はログインページへ
          console.log('No redirect result found')
          router.push('/auth/login')
        }
      } catch (error: any) {
        console.error('Redirect result error:', error)
        
        let errorMessage = 'ログインに失敗しました'
        if (error.code === 'auth/unauthorized-domain') {
          errorMessage = 'このドメインは認証されていません'
        } else if (error.code === 'auth/operation-not-allowed') {
          errorMessage = 'Google認証が無効になっています'
        }
        
        toast.error(errorMessage)
        router.push('/auth/login')
      }
    }

    handleRedirectResult()
  }, [router])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center space-y-4">
        <Loader2 className="w-12 h-12 animate-spin mx-auto text-blue-600" />
        <div>
          <h2 className="text-xl font-semibold mb-2">認証処理中...</h2>
          <p className="text-gray-600">しばらくお待ちください</p>
        </div>
      </div>
    </div>
  )
}