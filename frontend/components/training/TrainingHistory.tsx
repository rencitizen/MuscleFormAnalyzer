'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Calendar, TrendingUp, Dumbbell, Clock } from 'lucide-react'
import { format, subDays, startOfWeek, endOfWeek } from 'date-fns'
import { ja } from 'date-fns/locale'

interface TrainingSession {
  id: string
  date: string
  duration: number
  routine_name?: string
  sets: Array<{
    exercise_name: string
    weight: number
    reps: number
    set_number: number
  }>
}

interface ExerciseStats {
  exercise_name: string
  total_volume: number
  max_weight: number
  total_sets: number
  last_performed: string
}

export function TrainingHistory() {
  const [sessions, setSessions] = useState<TrainingSession[]>([])
  const [stats, setStats] = useState<ExerciseStats[]>([])
  const [selectedPeriod, setSelectedPeriod] = useState<'week' | 'month' | 'all'>('week')

  useEffect(() => {
    fetchHistory()
    fetchStats()
  }, [selectedPeriod])

  const fetchHistory = async () => {
    try {
      const params = new URLSearchParams()
      
      if (selectedPeriod === 'week') {
        params.append('start_date', format(startOfWeek(new Date(), { weekStartsOn: 1 }), 'yyyy-MM-dd'))
        params.append('end_date', format(endOfWeek(new Date(), { weekStartsOn: 1 }), 'yyyy-MM-dd'))
      } else if (selectedPeriod === 'month') {
        params.append('start_date', format(subDays(new Date(), 30), 'yyyy-MM-dd'))
      }

      const response = await fetch(`/api/training/history?${params}`)
      if (response.ok) {
        const data = await response.json()
        setSessions(data)
      }
    } catch (error) {
      console.error('履歴取得エラー:', error)
    }
  }

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/training/stats')
      if (response.ok) {
        const data = await response.json()
        setStats(data)
      }
    } catch (error) {
      console.error('統計取得エラー:', error)
    }
  }

  const getTotalVolume = (session: TrainingSession) => {
    return session.sets.reduce((total, set) => total + (set.weight * set.reps), 0)
  }

  const getWeeklyVolume = () => {
    const weekStart = startOfWeek(new Date(), { weekStartsOn: 1 })
    const weekSessions = sessions.filter(s => new Date(s.date) >= weekStart)
    return weekSessions.reduce((total, session) => total + getTotalVolume(session), 0)
  }

  const getWeeklyWorkouts = () => {
    const weekStart = startOfWeek(new Date(), { weekStartsOn: 1 })
    return sessions.filter(s => new Date(s.date) >= weekStart).length
  }

  return (
    <div className="space-y-6">
      {/* 期間選択 */}
      <div className="flex gap-2">
        <button
          onClick={() => setSelectedPeriod('week')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            selectedPeriod === 'week'
              ? 'bg-primary text-primary-foreground'
              : 'bg-muted hover:bg-muted/80'
          }`}
        >
          今週
        </button>
        <button
          onClick={() => setSelectedPeriod('month')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            selectedPeriod === 'month'
              ? 'bg-primary text-primary-foreground'
              : 'bg-muted hover:bg-muted/80'
          }`}
        >
          過去30日
        </button>
        <button
          onClick={() => setSelectedPeriod('all')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            selectedPeriod === 'all'
              ? 'bg-primary text-primary-foreground'
              : 'bg-muted hover:bg-muted/80'
          }`}
        >
          全期間
        </button>
      </div>

      {/* 統計サマリー */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Dumbbell className="w-4 h-4" />
              今週のワークアウト
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{getWeeklyWorkouts()}回</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              今週の総ボリューム
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{(getWeeklyVolume() / 1000).toFixed(1)} ton</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Clock className="w-4 h-4" />
              平均トレーニング時間
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {sessions.length > 0 
                ? Math.round(sessions.reduce((sum, s) => sum + s.duration, 0) / sessions.length)
                : 0} 分
            </div>
          </CardContent>
        </Card>
      </div>

      {/* セッション履歴 */}
      <Card>
        <CardHeader>
          <CardTitle>トレーニング履歴</CardTitle>
        </CardHeader>
        <CardContent>
          {sessions.length === 0 ? (
            <div className="py-8 text-center text-muted-foreground">
              この期間のトレーニング記録はありません
            </div>
          ) : (
            <div className="space-y-4">
              {sessions.map(session => (
                <Card key={session.id}>
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <div className="flex items-center gap-2">
                          <Calendar className="w-4 h-4 text-muted-foreground" />
                          <span className="font-medium">
                            {format(new Date(session.date), 'M月d日(E)', { locale: ja })}
                          </span>
                          {session.routine_name && (
                            <span className="text-sm bg-primary/10 text-primary px-2 py-0.5 rounded">
                              {session.routine_name}
                            </span>
                          )}
                        </div>
                        <div className="flex items-center gap-4 mt-1 text-sm text-muted-foreground">
                          <span>⏱ {session.duration}分</span>
                          <span>💪 {session.sets.length}セット</span>
                          <span>📊 {(getTotalVolume(session) / 1000).toFixed(1)} ton</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="space-y-1">
                      {Object.entries(
                        session.sets.reduce((acc, set) => {
                          if (!acc[set.exercise_name]) {
                            acc[set.exercise_name] = []
                          }
                          acc[set.exercise_name].push(set)
                          return acc
                        }, {} as Record<string, typeof session.sets>)
                      ).map(([exercise, sets]) => (
                        <div key={exercise} className="flex items-center justify-between text-sm">
                          <span>{exercise}</span>
                          <span className="text-muted-foreground">
                            {sets.map(s => `${s.weight}kg×${s.reps}`).join(', ')}
                          </span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* エクササイズ別統計 */}
      <Card>
        <CardHeader>
          <CardTitle>エクササイズ別統計</CardTitle>
          <CardDescription>よく行うエクササイズとその進捗</CardDescription>
        </CardHeader>
        <CardContent>
          {stats.length === 0 ? (
            <div className="py-8 text-center text-muted-foreground">
              まだ統計データがありません
            </div>
          ) : (
            <div className="space-y-3">
              {stats.map(stat => (
                <div key={stat.exercise_name} className="flex items-center justify-between p-3 bg-muted rounded-lg">
                  <div>
                    <div className="font-medium">{stat.exercise_name}</div>
                    <div className="text-sm text-muted-foreground">
                      最終: {format(new Date(stat.last_performed), 'M/d', { locale: ja })}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-medium">最大 {stat.max_weight}kg</div>
                    <div className="text-sm text-muted-foreground">
                      合計 {stat.total_sets}セット
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}