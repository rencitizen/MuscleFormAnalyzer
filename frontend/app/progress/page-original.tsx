'use client'

import { useState, useEffect } from 'react'
import { Button } from '../../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs'
import { Alert, AlertDescription } from '../../components/ui/alert'
import { ChevronLeft, TrendingUp, Calendar, Award, BarChart3, Loader2, AlertCircle } from 'lucide-react'
import Link from 'next/link'
import { LineChart, Line, BarChart, Bar, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from '../../components/dashboard/ChartWrapper'
import { format, subDays, startOfWeek, endOfWeek, subWeeks } from 'date-fns'
import { ja } from 'date-fns/locale'
import { useAuth } from '../../components/providers/AuthProvider'
import { ProgressService, ProgressData, ProgressSummary } from '../../lib/services/progressService'
import { useRouter } from 'next/navigation'
import toast from 'react-hot-toast'

interface WeeklyData {
  date: string;
  score: number;
  volume: number;
}

interface ExerciseBalance {
  exercise: string;
  value: number;
}

export default function ProgressPage() {
  const { user, loading: authLoading } = useAuth()
  const router = useRouter()
  const [selectedPeriod, setSelectedPeriod] = useState<'week' | 'month' | 'year'>('week')
  const [selectedExercise, setSelectedExercise] = useState<'all' | 'squat' | 'deadlift' | 'bench_press'>('all')
  
  // データ状態
  const [progressData, setProgressData] = useState<ProgressData[]>([])
  const [summary, setSummary] = useState<ProgressSummary | null>(null)
  const [weeklyData, setWeeklyData] = useState<WeeklyData[]>([])
  const [exerciseBalance, setExerciseBalance] = useState<ExerciseBalance[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // 認証チェック
  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/auth/login')
      toast.error('ログインが必要です')
    }
  }, [user, authLoading, router])

  // データ読み込み
  useEffect(() => {
    if (!user) return

    const loadData = async () => {
      try {
        setIsLoading(true)
        setError(null)

        // 期間設定
        const dateFrom = selectedPeriod === 'week' 
          ? subDays(new Date(), 7)
          : selectedPeriod === 'month'
          ? subDays(new Date(), 30)
          : subDays(new Date(), 365)

        // 進捗データ取得
        const data = await ProgressService.getUserProgress(
          selectedExercise === 'all' ? undefined : selectedExercise,
          dateFrom
        )
        setProgressData(data)

        // サマリー取得
        const summaryData = await ProgressService.getProgressSummary(dateFrom)
        setSummary(summaryData)

        // 週間データ生成
        generateWeeklyData(data)
        
        // エクササイズバランス計算
        calculateExerciseBalance(data)

      } catch (err) {
        console.error('データ読み込みエラー:', err)
        setError('データの読み込みに失敗しました')
        toast.error('データの読み込みに失敗しました')
      } finally {
        setIsLoading(false)
      }
    }

    loadData()
  }, [user, selectedPeriod, selectedExercise])

  // リアルタイムデータ監視
  useEffect(() => {
    if (!user) return

    const unsubscribe = ProgressService.subscribeToUserProgress(
      (data) => {
        setProgressData(data)
        generateWeeklyData(data)
        calculateExerciseBalance(data)
      },
      selectedExercise === 'all' ? undefined : selectedExercise
    )

    return () => unsubscribe()
  }, [user, selectedExercise])

  // 週間データ生成
  const generateWeeklyData = (data: ProgressData[]) => {
    const days = ['日', '月', '火', '水', '木', '金', '土']
    const weekData: WeeklyData[] = days.map(day => ({
      date: day,
      score: 0,
      volume: 0
    }))

    // 今週のデータのみ抽出
    const startOfThisWeek = startOfWeek(new Date(), { weekStartsOn: 0 })
    const endOfThisWeek = endOfWeek(new Date(), { weekStartsOn: 0 })

    data.forEach(item => {
      const itemDate = new Date(item.date)
      if (itemDate >= startOfThisWeek && itemDate <= endOfThisWeek) {
        const dayIndex = itemDate.getDay()
        weekData[dayIndex].score = Math.max(weekData[dayIndex].score, item.score || 0)
        weekData[dayIndex].volume += item.volume || 0
      }
    })

    setWeeklyData(weekData)
  }

  // エクササイズバランス計算
  const calculateExerciseBalance = (data: ProgressData[]) => {
    const exerciseMap = new Map<string, { totalScore: number; count: number }>()

    data.forEach(item => {
      const current = exerciseMap.get(item.exercise) || { totalScore: 0, count: 0 }
      exerciseMap.set(item.exercise, {
        totalScore: current.totalScore + (item.score || 0),
        count: current.count + 1
      })
    })

    const balance: ExerciseBalance[] = []
    exerciseMap.forEach((value, key) => {
      balance.push({
        exercise: key,
        value: Math.round(value.totalScore / value.count)
      })
    })

    // デフォルトエクササイズを追加（データがない場合）
    const defaultExercises = ['スクワット', 'デッドリフト', 'ベンチプレス', '体幹安定性', '柔軟性', 'テンポ']
    defaultExercises.forEach(exercise => {
      if (!balance.find(b => b.exercise === exercise)) {
        balance.push({ exercise, value: 0 })
      }
    })

    setExerciseBalance(balance.slice(0, 6)) // 最大6つまで表示
  }

  // ローディング中
  if (authLoading || isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    )
  }

  // エラー表示
  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <Alert className="max-w-md">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    )
  }

  // 進捗トレンドデータ生成
  const progressTrend = progressData
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
    .map(item => ({
      day: format(new Date(item.date), 'MM/dd'),
      score: item.score || 0,
      weight: item.weight || 0
    }))

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/">
              <Button variant="ghost" size="icon">
                <ChevronLeft className="w-5 h-5" />
              </Button>
            </Link>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <BarChart3 className="w-6 h-6" />
              進捗ダッシュボード
            </h1>
          </div>
          <div className="text-sm text-muted-foreground">
            {user?.email}
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {/* データがない場合の表示 */}
        {progressData.length === 0 && !isLoading && (
          <Alert className="mb-8">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              まだ進捗データがありません。トレーニングを記録してください。
            </AlertDescription>
          </Alert>
        )}

        {/* サマリーカード */}
        <div className="grid gap-4 md:grid-cols-4 mb-8">
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>総セッション数</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{summary?.totalSessions || 0}回</div>
              <p className="text-xs text-muted-foreground">
                {selectedPeriod === 'week' ? '今週' : selectedPeriod === 'month' ? '今月' : '今年'}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardDescription>平均フォームスコア</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {summary ? Math.round(summary.averageScore) : 0}%
              </div>
              <p className="text-xs text-muted-foreground">全エクササイズ</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardDescription>総ボリューム</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {summary ? summary.totalVolume.toLocaleString() : 0}kg
              </div>
              <p className="text-xs text-muted-foreground">重量×回数×セット</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardDescription>連続記録</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{summary?.currentStreak || 0}日</div>
              <p className="text-xs text-muted-foreground">
                {summary?.currentStreak ? '継続中' : '記録なし'}
              </p>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="overview" className="space-y-4">
          <TabsList>
            <TabsTrigger value="overview">概要</TabsTrigger>
            <TabsTrigger value="exercises">種目別</TabsTrigger>
            <TabsTrigger value="trends">トレンド</TabsTrigger>
            <TabsTrigger value="achievements">実績</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>週間アクティビティ</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={weeklyData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="score" fill="hsl(var(--primary))" name="スコア" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>バランス評価</CardTitle>
                </CardHeader>
                <CardContent>
                  {exerciseBalance.length > 0 ? (
                    <ResponsiveContainer width="100%" height={300}>
                      <RadarChart data={exerciseBalance}>
                        <PolarGrid />
                        <PolarAngleAxis dataKey="exercise" />
                        <PolarRadiusAxis angle={90} domain={[0, 100]} />
                        <Radar
                          name="スコア"
                          dataKey="value"
                          stroke="hsl(var(--primary))"
                          fill="hsl(var(--primary))"
                          fillOpacity={0.6}
                        />
                      </RadarChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                      データがありません
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="exercises" className="space-y-4">
            <div className="flex gap-2 mb-4">
              <Button
                variant={selectedExercise === 'all' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSelectedExercise('all')}
              >
                すべて
              </Button>
              <Button
                variant={selectedExercise === 'squat' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSelectedExercise('squat')}
              >
                スクワット
              </Button>
              <Button
                variant={selectedExercise === 'deadlift' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSelectedExercise('deadlift')}
              >
                デッドリフト
              </Button>
              <Button
                variant={selectedExercise === 'bench_press' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSelectedExercise('bench_press')}
              >
                ベンチプレス
              </Button>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>種目別進捗</CardTitle>
                <CardDescription>
                  フォームスコアと使用重量の推移
                </CardDescription>
              </CardHeader>
              <CardContent>
                {progressTrend.length > 0 ? (
                  <ResponsiveContainer width="100%" height={400}>
                    <LineChart data={progressTrend}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="day" />
                      <YAxis yAxisId="left" />
                      <YAxis yAxisId="right" orientation="right" />
                      <Tooltip />
                      <Legend />
                      <Line
                        yAxisId="left"
                        type="monotone"
                        dataKey="score"
                        stroke="hsl(var(--primary))"
                        name="フォームスコア"
                      />
                      <Line
                        yAxisId="right"
                        type="monotone"
                        dataKey="weight"
                        stroke="hsl(var(--destructive))"
                        name="重量(kg)"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-[400px] flex items-center justify-center text-muted-foreground">
                    データがありません
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="trends" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>成長予測</CardTitle>
                <CardDescription>
                  現在のペースでの3ヶ月後の予測
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between mb-2">
                      <span>フォームスコア</span>
                      <span className="font-semibold">
                        {summary && summary.averageScore > 0 
                          ? Math.min(100, Math.round(summary.averageScore * 1.15))
                          : 0}% (予測)
                      </span>
                    </div>
                    <div className="w-full bg-secondary rounded-full h-2">
                      <div
                        className="bg-primary h-2 rounded-full transition-all"
                        style={{ 
                          width: `${summary && summary.averageScore > 0 
                            ? Math.min(100, summary.averageScore * 1.15)
                            : 0}%` 
                        }}
                      />
                    </div>
                  </div>
                  
                  <div className="pt-4 border-t">
                    <h4 className="font-semibold mb-2">改善提案</h4>
                    <ul className="space-y-2 text-sm">
                      <li className="flex items-start gap-2">
                        <TrendingUp className="w-4 h-4 mt-0.5 text-green-600" />
                        <span>継続的なトレーニングで着実に成長しています</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <TrendingUp className="w-4 h-4 mt-0.5 text-yellow-600" />
                        <span>フォームの改善に注力することでさらなる向上が期待できます</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="achievements" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>獲得した実績</CardTitle>
                <CardDescription>
                  あなたの成長の軌跡
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {progressData.length > 0 ? (
                    <>
                      {summary && summary.totalSessions >= 1 && (
                        <AchievementItem
                          icon="🎯"
                          title="初めてのトレーニング記録"
                          date={summary.lastSessionDate}
                        />
                      )}
                      {summary && summary.averageScore >= 80 && (
                        <AchievementItem
                          icon="🏆"
                          title="フォームスコア80点以上"
                          date={new Date()}
                        />
                      )}
                      {summary && summary.currentStreak >= 7 && (
                        <AchievementItem
                          icon="🔥"
                          title="連続7日間トレーニング"
                          date={new Date()}
                        />
                      )}
                      {summary && summary.totalVolume >= 10000 && (
                        <AchievementItem
                          icon="💪"
                          title="総ボリューム10,000kg達成"
                          date={new Date()}
                        />
                      )}
                    </>
                  ) : (
                    <div className="text-center text-muted-foreground py-8">
                      トレーニングを記録して実績を獲得しましょう
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}

// 実績アイテムコンポーネント
function AchievementItem({ 
  icon, 
  title, 
  date 
}: { 
  icon: string; 
  title: string; 
  date?: Date;
}) {
  return (
    <div className="flex items-center gap-4 p-4 rounded-lg border">
      <div className="text-3xl">{icon}</div>
      <div className="flex-1">
        <h4 className="font-semibold">{title}</h4>
        <p className="text-sm text-muted-foreground">
          {date ? format(date, 'yyyy年MM月dd日', { locale: ja }) : ''}
        </p>
      </div>
      <Award className="w-5 h-5 text-yellow-600" />
    </div>
  )
}