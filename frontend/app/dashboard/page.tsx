'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { 
  Camera,
  Utensils,
  Calculator,
  Dumbbell,
  Database,
  TrendingUp,
  User,
  Shield,
  History,
  BarChart3,
  Brain
} from 'lucide-react'
import Link from 'next/link'
import { useSession } from 'next-auth/react'

export default function DashboardPage() {
  const { data: session } = useSession()
  const [recentActivity, setRecentActivity] = useState<any[]>([])

  useEffect(() => {
    // 最近のアクティビティを取得（API実装後に置き換え）
    setRecentActivity([
      { type: 'pose', date: new Date().toISOString(), description: '姿勢分析を実行' },
      { type: 'meal', date: new Date().toISOString(), description: '朝食を記録' },
      { type: 'training', date: new Date().toISOString(), description: 'トレーニングプログラムを生成' }
    ])
  }, [])

  const mainFeatures = [
    {
      title: '姿勢分析',
      description: 'カメラや動画から姿勢を分析',
      icon: Camera,
      link: '/pose-analysis',
      color: 'bg-blue-500'
    },
    {
      title: 'リアルタイム分析',
      description: '内カメラでリアルタイムフォーム分析',
      icon: Camera,
      link: '/workout/realtime',
      color: 'bg-red-500'
    },
    {
      title: '食事分析',
      description: '写真から食事内容を分析',
      icon: Utensils,
      link: '/meal-analysis',
      color: 'bg-green-500'
    },
    {
      title: '栄養計算',
      description: '必要カロリーとPFCバランスを計算',
      icon: Calculator,
      link: '/nutrition-calculator',
      color: 'bg-purple-500'
    },
    {
      title: 'トレーニング生成',
      description: 'パーソナライズされたプログラム作成',
      icon: Dumbbell,
      link: '/training-generator',
      color: 'bg-orange-500'
    }
  ]

  const additionalFeatures = [
    {
      title: '科学的計算',
      description: 'BMR・TDEE・PFCバランス',
      icon: Brain,
      link: '/dashboard/scientific'
    },
    {
      title: 'エクササイズDB',
      description: '600種類以上のエクササイズ',
      icon: Database,
      link: '/exercise-database'
    },
    {
      title: 'プログレス追跡',
      description: '成長を可視化',
      icon: TrendingUp,
      link: '/progress-tracking'
    },
    {
      title: 'プロファイル',
      description: 'ユーザー情報管理',
      icon: User,
      link: '/profile'
    },
    {
      title: '履歴',
      description: '過去のデータ確認',
      icon: History,
      link: '/history'
    }
  ]

  return (
    <div className="container mx-auto px-4 py-8 pb-24 md:pb-8">
      {/* ヘッダー */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">TENAX FIT ダッシュボード</h1>
        <p className="text-muted-foreground">
          {session?.user?.name ? `${session.user.name}さん、` : ''}今日も頑張りましょう！
        </p>
      </div>

      {/* メイン機能 */}
      <div className="mb-12">
        <h2 className="text-xl font-semibold mb-4">メイン機能</h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
          {mainFeatures.map((feature) => (
            <Link key={feature.title} href={feature.link}>
              <Card className="h-full hover:shadow-lg transition-shadow cursor-pointer">
                <CardHeader className="pb-4">
                  <div className={`w-12 h-12 rounded-lg ${feature.color} flex items-center justify-center mb-3`}>
                    <feature.icon className="w-6 h-6 text-white" />
                  </div>
                  <CardTitle className="text-lg">{feature.title}</CardTitle>
                  <CardDescription className="text-sm">
                    {feature.description}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Button className="w-full" variant="outline">
                    開始する
                  </Button>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </div>

      {/* その他の機能 */}
      <div className="mb-12">
        <h2 className="text-xl font-semibold mb-4">その他の機能</h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {additionalFeatures.map((feature) => (
            <Link key={feature.title} href={feature.link}>
              <Card className="hover:shadow-md transition-shadow cursor-pointer">
                <CardHeader className="flex flex-row items-center space-y-0 pb-2">
                  <feature.icon className="w-5 h-5 mr-2 text-muted-foreground" />
                  <div>
                    <CardTitle className="text-base">{feature.title}</CardTitle>
                    <CardDescription className="text-xs mt-1">
                      {feature.description}
                    </CardDescription>
                  </div>
                </CardHeader>
              </Card>
            </Link>
          ))}
        </div>
      </div>

      {/* 最近のアクティビティ */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5" />
            最近のアクティビティ
          </CardTitle>
        </CardHeader>
        <CardContent>
          {recentActivity.length > 0 ? (
            <div className="space-y-2">
              {recentActivity.map((activity, index) => (
                <div key={index} className="flex items-center justify-between py-2 border-b last:border-0">
                  <span className="text-sm">{activity.description}</span>
                  <span className="text-xs text-muted-foreground">
                    {new Date(activity.date).toLocaleString('ja-JP')}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">まだアクティビティがありません</p>
          )}
        </CardContent>
      </Card>

      {/* 管理者リンク（管理者のみ表示） */}
      {session?.user?.email === 'admin@tenaxfit.com' && (
        <div className="mt-8">
          <Link href="/admin">
            <Button variant="outline" className="w-full md:w-auto">
              <Shield className="w-4 h-4 mr-2" />
              管理者画面
            </Button>
          </Link>
        </div>
      )}
    </div>
  )
}