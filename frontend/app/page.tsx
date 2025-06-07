'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/components/providers/AuthProvider'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { 
  Activity, 
  BarChart3, 
  Camera, 
  Dumbbell, 
  Target, 
  Trophy,
  Utensils,
  Calendar,
  TrendingUp,
  BookOpen,
  Settings,
  Users,
  FileText,
  Brain,
  Heart
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
      {/* Header */}
      <header className="border-b bg-white/95 backdrop-blur sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Dumbbell className="w-8 h-8 text-primary" />
              <h1 className="text-2xl font-bold">BodyScale Pose Analyzer</h1>
            </div>
            <nav className="hidden md:flex items-center gap-6">
              <Link href="/dashboard" className="text-sm hover:text-primary">
                ダッシュボード
              </Link>
              <Link href="/progress" className="text-sm hover:text-primary">
                進捗
              </Link>
              <Link href="/settings" className="text-sm hover:text-primary">
                設定
              </Link>
              <Button variant="outline" size="sm" onClick={() => router.push('/settings')}>
                <Settings className="w-4 h-4" />
              </Button>
            </nav>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {/* Welcome Section */}
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold mb-4">
            こんにちは、{user?.displayName || 'アスリート'}さん
          </h2>
          <p className="text-xl text-muted-foreground">
            今日はどの機能を使いますか？
          </p>
        </div>

        {/* Main Features Section */}
        <div className="mb-12">
          <h3 className="text-2xl font-semibold mb-6 flex items-center gap-2">
            <Target className="w-6 h-6 text-primary" />
            メイン機能
          </h3>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {/* Form Analysis */}
            <Link href="/analyze">
              <Card className="cursor-pointer hover:shadow-lg transition-all hover:scale-105 bg-gradient-to-br from-blue-50 to-blue-100/50">
                <CardHeader>
                  <CardTitle className="flex items-center gap-3">
                    <div className="p-3 bg-blue-500 rounded-lg">
                      <Camera className="w-6 h-6 text-white" />
                    </div>
                    フォーム分析
                  </CardTitle>
                  <CardDescription className="mt-2">
                    BIG3（スクワット、ベンチプレス、デッドリフト）のフォームをAIで分析
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• リアルタイム姿勢検出</li>
                    <li>• 角度測定と改善提案</li>
                    <li>• 動画保存と比較機能</li>
                  </ul>
                  <Button className="w-full mt-4">分析を開始</Button>
                </CardContent>
              </Card>
            </Link>

            {/* Nutrition Management */}
            <Link href="/nutrition">
              <Card className="cursor-pointer hover:shadow-lg transition-all hover:scale-105 bg-gradient-to-br from-green-50 to-green-100/50">
                <CardHeader>
                  <CardTitle className="flex items-center gap-3">
                    <div className="p-3 bg-green-500 rounded-lg">
                      <Utensils className="w-6 h-6 text-white" />
                    </div>
                    栄養管理
                  </CardTitle>
                  <CardDescription className="mt-2">
                    写真から食事を分析してカロリーと栄養素を自動計算
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• AI食品認識</li>
                    <li>• PFCバランス表示</li>
                    <li>• 食事履歴とグラフ</li>
                  </ul>
                  <Button className="w-full mt-4" variant="outline">食事を記録</Button>
                </CardContent>
              </Card>
            </Link>

            {/* Progress Tracking */}
            <Link href="/progress">
              <Card className="cursor-pointer hover:shadow-lg transition-all hover:scale-105 bg-gradient-to-br from-purple-50 to-purple-100/50">
                <CardHeader>
                  <CardTitle className="flex items-center gap-3">
                    <div className="p-3 bg-purple-500 rounded-lg">
                      <TrendingUp className="w-6 h-6 text-white" />
                    </div>
                    進捗管理
                  </CardTitle>
                  <CardDescription className="mt-2">
                    トレーニング記録と成長を可視化
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• ワークアウト記録</li>
                    <li>• 重量推移グラフ</li>
                    <li>• 目標達成率</li>
                  </ul>
                  <Button className="w-full mt-4" variant="outline">記録を見る</Button>
                </CardContent>
              </Card>
            </Link>
          </div>
        </div>

        {/* Analysis & Insights Section */}
        <div className="mb-12">
          <h3 className="text-2xl font-semibold mb-6 flex items-center gap-2">
            <Brain className="w-6 h-6 text-primary" />
            分析・インサイト
          </h3>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            {/* Dashboard */}
            <Link href="/dashboard">
              <Card className="cursor-pointer hover:shadow-lg transition-all hover:scale-105">
                <CardHeader className="pb-3">
                  <div className="flex items-center gap-3">
                    <BarChart3 className="w-5 h-5 text-orange-500" />
                    <CardTitle className="text-base">統計ダッシュボード</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    全体的な進捗と統計を一覧表示
                  </p>
                </CardContent>
              </Card>
            </Link>

            {/* Calendar View */}
            <Link href="/nutrition/tracking">
              <Card className="cursor-pointer hover:shadow-lg transition-all hover:scale-105">
                <CardHeader className="pb-3">
                  <div className="flex items-center gap-3">
                    <Calendar className="w-5 h-5 text-blue-500" />
                    <CardTitle className="text-base">カレンダービュー</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    食事とトレーニングを週間表示
                  </p>
                </CardContent>
              </Card>
            </Link>

            {/* Body Metrics */}
            <Link href="/analyze?type=body_metrics">
              <Card className="cursor-pointer hover:shadow-lg transition-all hover:scale-105">
                <CardHeader className="pb-3">
                  <div className="flex items-center gap-3">
                    <Heart className="w-5 h-5 text-red-500" />
                    <CardTitle className="text-base">身体測定</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    身体寸法の測定と記録
                  </p>
                </CardContent>
              </Card>
            </Link>

            {/* Exercise Database */}
            <Link href="/exercises">
              <Card className="cursor-pointer hover:shadow-lg transition-all hover:scale-105">
                <CardHeader className="pb-3">
                  <div className="flex items-center gap-3">
                    <BookOpen className="w-5 h-5 text-green-500" />
                    <CardTitle className="text-base">エクササイズDB</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    300種類以上の種目情報
                  </p>
                </CardContent>
              </Card>
            </Link>
          </div>
        </div>

        {/* Advanced Features Section */}
        <div className="mb-12">
          <h3 className="text-2xl font-semibold mb-6 flex items-center gap-2">
            <Trophy className="w-6 h-6 text-primary" />
            アドバンス機能
          </h3>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {/* AI Nutrition Advisor */}
            <Card className="border-2 border-dashed">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Brain className="w-5 h-5 text-purple-500" />
                  AI栄養アドバイザー
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  個人の目標に基づいた栄養アドバイスを提供
                </p>
                <Button 
                  className="w-full mt-4" 
                  variant="outline"
                  onClick={() => router.push('/nutrition/tracking')}
                >
                  アドバイスを見る
                </Button>
              </CardContent>
            </Card>

            {/* Training Data Collection */}
            <Card className="border-2 border-dashed">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <FileText className="w-5 h-5 text-blue-500" />
                  トレーニングデータ管理
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  AIモデル改善のためのデータ収集と管理
                </p>
                <Button 
                  className="w-full mt-4" 
                  variant="outline"
                  onClick={() => router.push('/training_data_management')}
                >
                  データ管理へ
                </Button>
              </CardContent>
            </Card>

            {/* Community */}
            <Card className="border-2 border-dashed opacity-50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Users className="w-5 h-5 text-green-500" />
                  コミュニティ（近日公開）
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  他のユーザーと知識を共有
                </p>
                <Button className="w-full mt-4" variant="outline" disabled>
                  準備中
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid gap-4 md:grid-cols-4 mb-8">
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>今週のトレーニング</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">5回</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>今日のカロリー</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">1,850 kcal</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>フォームスコア</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">88%</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>連続記録日数</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">12日</div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}