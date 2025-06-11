'use client'

import { useState, useEffect } from 'react'
import { Button } from '../../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs'
import { ChevronLeft, TrendingUp, Calendar, Award, BarChart3 } from 'lucide-react'
import Link from 'next/link'
import { LineChart, Line, BarChart, Bar, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { format, subDays, startOfWeek, endOfWeek } from 'date-fns'
import { ja } from 'date-fns/locale'

// ダミーデータ
const weeklyData = [
  { date: '月', score: 78, volume: 1200 },
  { date: '火', score: 0, volume: 0 },
  { date: '水', score: 82, volume: 1350 },
  { date: '木', score: 0, volume: 0 },
  { date: '金', score: 85, volume: 1400 },
  { date: '土', score: 88, volume: 1450 },
  { date: '日', score: 0, volume: 0 },
]

const exerciseBalance = [
  { exercise: 'スクワット', value: 85 },
  { exercise: 'デッドリフト', value: 78 },
  { exercise: 'ベンチプレス', value: 92 },
  { exercise: '体幹安定性', value: 70 },
  { exercise: '柔軟性', value: 65 },
  { exercise: 'テンポ', value: 88 },
]

const progressTrend = Array.from({ length: 30 }, (_, i) => ({
  day: format(subDays(new Date(), 29 - i), 'MM/dd'),
  score: 70 + Math.random() * 20 + (i / 30) * 10,
  weight: 60 + (i / 30) * 5 + Math.random() * 3,
}))

const achievements = [
  { id: 1, title: '初めてのスクワット', date: '2024-01-15', icon: '🎯' },
  { id: 2, title: 'フォームスコア90点達成', date: '2024-01-18', icon: '🏆' },
  { id: 3, title: '連続7日間トレーニング', date: '2024-01-20', icon: '🔥' },
  { id: 4, title: 'スクワット100kg達成', date: '2024-01-22', icon: '💪' },
]

export default function ProgressPage() {
  const [selectedPeriod, setSelectedPeriod] = useState<'week' | 'month' | 'year'>('week')
  const [selectedExercise, setSelectedExercise] = useState<'all' | 'squat' | 'deadlift' | 'bench_press'>('all')

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
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {/* サマリーカード */}
        <div className="grid gap-4 md:grid-cols-4 mb-8">
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>今週のセッション</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">4回</div>
              <p className="text-xs text-muted-foreground">先週比 +1</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardDescription>平均フォームスコア</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">83.3%</div>
              <p className="text-xs text-green-600">+5.2%</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardDescription>総ボリューム</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">5,400kg</div>
              <p className="text-xs text-green-600">+12%</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardDescription>連続記録</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">7日</div>
              <p className="text-xs text-muted-foreground">継続中</p>
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
                  過去30日間のフォームスコアと使用重量
                </CardDescription>
              </CardHeader>
              <CardContent>
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
                      <span className="font-semibold">92% (予測)</span>
                    </div>
                    <div className="w-full bg-secondary rounded-full h-2">
                      <div
                        className="bg-primary h-2 rounded-full transition-all"
                        style={{ width: '92%' }}
                      />
                    </div>
                  </div>
                  
                  <div>
                    <div className="flex justify-between mb-2">
                      <span>スクワット最大重量</span>
                      <span className="font-semibold">120kg (予測)</span>
                    </div>
                    <div className="w-full bg-secondary rounded-full h-2">
                      <div
                        className="bg-primary h-2 rounded-full transition-all"
                        style={{ width: '80%' }}
                      />
                    </div>
                  </div>

                  <div className="pt-4 border-t">
                    <h4 className="font-semibold mb-2">改善提案</h4>
                    <ul className="space-y-2 text-sm">
                      <li className="flex items-start gap-2">
                        <TrendingUp className="w-4 h-4 mt-0.5 text-green-600" />
                        <span>現在の成長率を維持すれば、3ヶ月後にはフォームスコア90%超えが期待できます</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <TrendingUp className="w-4 h-4 mt-0.5 text-yellow-600" />
                        <span>体幹の安定性を改善することで、さらなる重量アップが可能です</span>
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
                  {achievements.map((achievement) => (
                    <div
                      key={achievement.id}
                      className="flex items-center gap-4 p-4 rounded-lg border"
                    >
                      <div className="text-3xl">{achievement.icon}</div>
                      <div className="flex-1">
                        <h4 className="font-semibold">{achievement.title}</h4>
                        <p className="text-sm text-muted-foreground">
                          {format(new Date(achievement.date), 'yyyy年MM月dd日', { locale: ja })}
                        </p>
                      </div>
                      <Award className="w-5 h-5 text-yellow-600" />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}