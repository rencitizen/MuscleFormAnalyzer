'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { 
  TrendingUp, 
  Activity, 
  Weight,
  Utensils
} from 'lucide-react'
import Link from 'next/link'


export default function DashboardPage() {
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // シミュレートされたデータ読み込み
    setTimeout(() => setIsLoading(false), 1000)
  }, [])

  // サンプルデータ（実際の実装では、APIから取得）
  const statsData = [
    {
      title: 'トレーニング',
      value: 4,
      unit: '回',
      description: '今週',
      icon: <Activity className="w-5 h-5" />,
      link: '/training'
    },
    {
      title: '体重',
      value: 72.5,
      unit: 'kg',
      description: '現在',
      icon: <Weight className="w-5 h-5" />,
      link: '/progress'
    },
    {
      title: 'カロリー',
      value: 2150,
      unit: 'kcal',
      description: '今日',
      icon: <Utensils className="w-5 h-5" />,
      link: '/nutrition'
    },
    {
      title: '進捗',
      value: 78,
      unit: '%',
      description: '今月',
      icon: <TrendingUp className="w-5 h-5" />
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
      <div className="mb-6">
        <h1 className="text-2xl font-bold">ダッシュボード</h1>
      </div>


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
              {stat.link && (
                <Link href={stat.link} className="absolute inset-0" />
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-6 md:grid-cols-1">
        {/* 週間進捗 */}
        <Card>
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
            <div className="mt-4">
              <p className="text-sm text-muted-foreground">
                完了率: 4/7日
              </p>
            </div>
          </CardContent>
        </Card>

      </div>
    </div>
  )
}