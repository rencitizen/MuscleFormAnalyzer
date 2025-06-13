'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { Button } from '@/components/ui/button'
import { 
  TrendingUp, 
  Activity, 
  Target, 
  Calendar,
  Weight,
  Utensils,
  BarChart3,
  Trophy,
  ChevronRight,
  Info
} from 'lucide-react'
import Link from 'next/link'

interface StatCard {
  title: string
  value: string | number
  unit?: string
  description: string
  icon: React.ReactNode
  trend?: {
    value: number
    isPositive: boolean
  }
  link?: string
}

export default function DashboardPage() {
  const [selectedPeriod, setSelectedPeriod] = useState('week')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // シミュレートされたデータ読み込み
    setTimeout(() => setIsLoading(false), 1000)
  }, [])

  // サンプルデータ（実際の実装では、APIから取得）
  const statsData: StatCard[] = [
    {
      title: 'トレーニング頻度',
      value: 4,
      unit: '回/週',
      description: '今週のトレーニング回数',
      icon: <Activity className="w-5 h-5" />,
      trend: { value: 33, isPositive: true },
      link: '/training'
    },
    {
      title: '体重変化',
      value: -1.5,
      unit: 'kg',
      description: '先月比',
      icon: <Weight className="w-5 h-5" />,
      trend: { value: 2.1, isPositive: true },
      link: '/progress'
    },
    {
      title: 'カロリー摂取',
      value: 2150,
      unit: 'kcal',
      description: '今日の摂取カロリー',
      icon: <Utensils className="w-5 h-5" />,
      trend: { value: 5, isPositive: false },
      link: '/nutrition'
    },
    {
      title: '目標達成率',
      value: 78,
      unit: '%',
      description: '今月の目標達成状況',
      icon: <Target className="w-5 h-5" />,
      trend: { value: 12, isPositive: true }
    }
  ]

  const weeklyProgress = [
    { day: '月', completed: true, value: 100 },
    { day: '火', completed: false, value: 0 },
    { day: '水', completed: true, value: 100 },
    { day: '木', completed: true, value: 100 },
    { day: '金', completed: false, value: 0 },
    { day: '土', completed: true, value: 100 },
    { day: '日', completed: false, value: 0 }
  ]

  const recentAchievements = [
    { title: 'ベンチプレス新記録', value: '100kg達成', date: '2日前' },
    { title: '週4回トレーニング達成', value: '3週連続', date: '5日前' },
    { title: 'フォーム改善', value: 'スクワット評価A', date: '1週間前' }
  ]

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center h-[60vh]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
            <p className="mt-4 text-muted-foreground">データを読み込んでいます...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8 pb-24 md:pb-8">
      {/* ヘッダー */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">統計ダッシュボード</h1>
        <p className="text-muted-foreground">あなたのフィットネス進捗を一目で確認</p>
      </div>

      {/* 期間選択タブ */}
      <Tabs value={selectedPeriod} onValueChange={setSelectedPeriod} className="mb-8">
        <TabsList className="grid w-full max-w-md grid-cols-4">
          <TabsTrigger value="today">今日</TabsTrigger>
          <TabsTrigger value="week">今週</TabsTrigger>
          <TabsTrigger value="month">今月</TabsTrigger>
          <TabsTrigger value="year">今年</TabsTrigger>
        </TabsList>
      </Tabs>

      {/* 統計カード */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
        {statsData.map((stat, index) => (
          <Card key={index} className="relative overflow-hidden">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {stat.title}
              </CardTitle>
              <div className="text-muted-foreground">{stat.icon}</div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {stat.value}
                {stat.unit && <span className="text-sm font-normal text-muted-foreground ml-1">{stat.unit}</span>}
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                {stat.description}
              </p>
              {stat.trend && (
                <div className={`text-xs mt-2 flex items-center ${stat.trend.isPositive ? 'text-green-600' : 'text-red-600'}`}>
                  <TrendingUp className={`w-3 h-3 mr-1 ${!stat.trend.isPositive && 'rotate-180'}`} />
                  {stat.trend.value}%
                </div>
              )}
              {stat.link && (
                <Link href={stat.link} className="absolute inset-0" />
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* 週間進捗 */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>週間トレーニング進捗</CardTitle>
            <CardDescription>今週のトレーニング完了状況</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {weeklyProgress.map((day, index) => (
                <div key={index} className="flex items-center gap-3">
                  <div className="w-8 text-sm font-medium">{day.day}</div>
                  <div className="flex-1">
                    <Progress value={day.value} className="h-2" />
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {day.completed ? '完了' : '未完了'}
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-4 flex justify-between items-center">
              <div className="text-sm text-muted-foreground">
                完了率: 4/7日 (57%)
              </div>
              <Button variant="ghost" size="sm" asChild>
                <Link href="/training">
                  詳細を見る
                  <ChevronRight className="w-4 h-4 ml-1" />
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* 最近の達成 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Trophy className="w-5 h-5 text-yellow-500" />
              最近の達成
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentAchievements.map((achievement, index) => (
                <div key={index} className="space-y-1">
                  <p className="text-sm font-medium">{achievement.title}</p>
                  <p className="text-sm text-muted-foreground">{achievement.value}</p>
                  <p className="text-xs text-muted-foreground">{achievement.date}</p>
                </div>
              ))}
              <Button variant="ghost" size="sm" className="w-full" asChild>
                <Link href="/progress">
                  すべての記録を見る
                  <ChevronRight className="w-4 h-4 ml-1" />
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* クイックアクション */}
        <Card className="lg:col-span-3">
          <CardHeader>
            <CardTitle>クイックアクション</CardTitle>
            <CardDescription>よく使う機能にすばやくアクセス</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <Button variant="outline" asChild>
                <Link href="/training">
                  <Activity className="w-4 h-4 mr-2" />
                  トレーニング開始
                </Link>
              </Button>
              <Button variant="outline" asChild>
                <Link href="/analyze">
                  <BarChart3 className="w-4 h-4 mr-2" />
                  フォーム分析
                </Link>
              </Button>
              <Button variant="outline" asChild>
                <Link href="/nutrition/tracking">
                  <Utensils className="w-4 h-4 mr-2" />
                  食事記録
                </Link>
              </Button>
              <Button variant="outline" asChild>
                <Link href="/progress">
                  <TrendingUp className="w-4 h-4 mr-2" />
                  進捗確認
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* ヒント */}
        <Card className="lg:col-span-3 bg-blue-50 dark:bg-blue-950/20 border-blue-200 dark:border-blue-900">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-blue-700 dark:text-blue-400">
              <Info className="w-5 h-5" />
              今日のヒント
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-blue-700 dark:text-blue-400">
              トレーニング後30分以内にプロテインを摂取すると、筋肉の回復と成長が促進されます。
              今日のトレーニング後は忘れずに栄養補給を行いましょう！
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}