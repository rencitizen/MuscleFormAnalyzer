'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/components/providers/AuthProvider'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { 
  Camera, 
  Utensils,
  TrendingUp
} from 'lucide-react'
import Link from 'next/link'

export default function HomePage() {
  const { user, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading && !user) {
      router.push('/auth/login')
    }
  }, [user, loading, router])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Simple Header */}
      <header className="border-b">
        <div className="container mx-auto px-4 py-4">
          <h1 className="text-xl font-bold">TENAX FIT</h1>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {/* Simple Welcome */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold mb-2">
            こんにちは
          </h2>
        </div>

        {/* Main Features - Simplified */}
        <div className="mb-8">
          <div className="grid gap-4 md:grid-cols-3">
            <Link href="/analyze">
              <Card className="cursor-pointer hover:shadow-sm transition-shadow">
                <CardHeader>
                  <Camera className="w-8 h-8 mb-2" />
                  <CardTitle>フォーム分析</CardTitle>
                  <CardDescription>
                    トレーニングフォームを撮影して分析
                  </CardDescription>
                </CardHeader>
              </Card>
            </Link>

            <Link href="/nutrition">
              <Card className="cursor-pointer hover:shadow-sm transition-shadow">
                <CardHeader>
                  <Utensils className="w-8 h-8 mb-2" />
                  <CardTitle>栄養管理</CardTitle>
                  <CardDescription>
                    食事を記録してカロリー計算
                  </CardDescription>
                </CardHeader>
              </Card>
            </Link>

            <Link href="/progress">
              <Card className="cursor-pointer hover:shadow-sm transition-shadow">
                <CardHeader>
                  <TrendingUp className="w-8 h-8 mb-2" />
                  <CardTitle>進捗管理</CardTitle>
                  <CardDescription>
                    トレーニングの記録と成長を確認
                  </CardDescription>
                </CardHeader>
              </Card>
            </Link>
          </div>
        </div>


        {/* Quick Stats - Simplified */}
        <div className="mt-8">
          <h3 className="text-lg font-semibold mb-4">今日の記録</h3>
          <div className="grid gap-4 grid-cols-2 md:grid-cols-4">
            <div>
              <p className="text-sm text-muted-foreground">トレーニング</p>
              <p className="text-xl font-semibold">5回</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">カロリー</p>
              <p className="text-xl font-semibold">1,850</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">フォーム</p>
              <p className="text-xl font-semibold">88%</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">連続日数</p>
              <p className="text-xl font-semibold">12日</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}