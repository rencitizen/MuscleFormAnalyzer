'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/components/providers/AuthProvider'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Activity, BarChart3, Camera, Dumbbell, Target, Trophy } from 'lucide-react'
import Link from 'next/link'

export default function HomePage() {
  const { user, loading } = useAuth()
  const router = useRouter()
  const [recentWorkouts, setRecentWorkouts] = useState(0)

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
      <header className="border-b">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Dumbbell className="w-6 h-6" />
            BodyScale
          </h1>
          <Button variant="outline" onClick={() => router.push('/settings')}>
            設定
          </Button>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold mb-2">
            こんにちは、{user?.displayName || 'トレーニー'}さん
          </h2>
          <p className="text-muted-foreground">
            今日もトレーニングを頑張りましょう！
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 mb-8">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="w-5 h-5" />
                今週のトレーニング
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{recentWorkouts}</div>
              <p className="text-sm text-muted-foreground">セッション</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="w-5 h-5" />
                平均フォームスコア
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">85%</div>
              <p className="text-sm text-muted-foreground">先週比 +3%</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Trophy className="w-5 h-5" />
                連続記録日数
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">7</div>
              <p className="text-sm text-muted-foreground">日</p>
            </CardContent>
          </Card>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <Link href="/analyze">
            <Card className="cursor-pointer hover:shadow-lg transition-shadow">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Camera className="w-5 h-5" />
                  フォーム分析を開始
                </CardTitle>
                <CardDescription>
                  カメラを使ってBIG3のフォームを分析します
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button className="w-full">分析を開始</Button>
              </CardContent>
            </Card>
          </Link>

          <Link href="/progress">
            <Card className="cursor-pointer hover:shadow-lg transition-shadow">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5" />
                  進捗を確認
                </CardTitle>
                <CardDescription>
                  過去のトレーニング記録と成長を確認します
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button variant="outline" className="w-full">
                  ダッシュボードへ
                </Button>
              </CardContent>
            </Card>
          </Link>
        </div>

        <div className="mt-8">
          <h3 className="text-lg font-semibold mb-4">最近の分析結果</h3>
          <Card>
            <CardContent className="p-6">
              <p className="text-muted-foreground text-center">
                まだ分析記録がありません。最初の分析を始めましょう！
              </p>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}