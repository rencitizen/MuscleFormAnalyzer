'use client'

import { useState, useEffect } from 'react'
import { Button } from '../ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Input } from '../ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select'
import { Plus, Check, X, PlayCircle, StopCircle } from 'lucide-react'
import toast from 'react-hot-toast'

interface TrainingSet {
  id?: string
  exercise_name: string
  set_number: number
  weight: number
  reps: number
  completed: boolean
}

interface TrainingSession {
  id: string
  routine_id?: string
  date: string
  sets: TrainingSet[]
  start_time?: string
  end_time?: string
}

interface Routine {
  id: string
  name: string
  description: string
  exercises: Array<{
    exercise_name: string
    target_sets: number
    target_reps: string
    target_weight?: number
    rest_time?: number
  }>
}

const EXERCISE_LIST = [
  // 胸
  'ベンチプレス',
  'ダンベルプレス',
  'インクラインベンチプレス',
  'ダンベルフライ',
  'ケーブルクロスオーバー',
  'ディップス',
  // 背中
  'デッドリフト',
  'ラットプルダウン',
  'ベントオーバーロー',
  'シーテッドロー',
  'プルアップ',
  // 脚
  'スクワット',
  'レッグプレス',
  'ランジ',
  'レッグカール',
  'レッグエクステンション',
  'カーフレイズ',
  // 肩
  'ショルダープレス',
  'サイドレイズ',
  'フロントレイズ',
  'リアレイズ',
  'アップライトロー',
  // 腕
  'バーベルカール',
  'ダンベルカール',
  'ハンマーカール',
  'トライセプスエクステンション',
  'ケーブルプッシュダウン',
  // 体幹
  'プランク',
  'クランチ',
  'レッグレイズ',
  'ロシアンツイスト',
]

export function TrainingRecord() {
  const [activeSession, setActiveSession] = useState<TrainingSession | null>(null)
  const [routines, setRoutines] = useState<Routine[]>([])
  const [currentExercise, setCurrentExercise] = useState('')
  const [currentSet, setCurrentSet] = useState({
    weight: '',
    reps: '',
  })
  const [sessionStartTime, setSessionStartTime] = useState<Date | null>(null)

  useEffect(() => {
    // ルーティン一覧を取得
    fetchRoutines()
    // アクティブセッションがあるか確認
    checkActiveSession()
  }, [])

  const fetchRoutines = async () => {
    try {
      const response = await fetch('/api/training/routines')
      if (response.ok) {
        const data = await response.json()
        setRoutines(data)
      }
    } catch (error) {
      console.error('ルーティン取得エラー:', error)
    }
  }

  const checkActiveSession = async () => {
    try {
      const response = await fetch('/api/training/sessions/active')
      if (response.ok) {
        const session = await response.json()
        if (session) {
          setActiveSession(session)
          setSessionStartTime(new Date(session.start_time))
        }
      }
    } catch (error) {
      console.error('セッション確認エラー:', error)
    }
  }

  const startSession = async (routineId?: string) => {
    try {
      const response = await fetch('/api/training/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ routine_id: routineId }),
      })
      
      if (response.ok) {
        const session = await response.json()
        setActiveSession(session)
        setSessionStartTime(new Date())
        toast.success('トレーニングを開始しました')
      }
    } catch (error) {
      console.error('セッション開始エラー:', error)
      toast.error('セッションの開始に失敗しました')
    }
  }

  const recordSet = async () => {
    if (!activeSession || !currentExercise || !currentSet.weight || !currentSet.reps) {
      toast.error('すべての項目を入力してください')
      return
    }

    const setNumber = activeSession.sets.filter(s => s.exercise_name === currentExercise).length + 1

    try {
      const response = await fetch('/api/training/sets', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: activeSession.id,
          exercise_name: currentExercise,
          weight: parseFloat(currentSet.weight),
          reps: parseInt(currentSet.reps),
          set_number: setNumber,
          completed: true,
        }),
      })

      if (response.ok) {
        const newSet = await response.json()
        setActiveSession(prev => prev ? {
          ...prev,
          sets: [...prev.sets, newSet],
        } : null)
        
        // フォームリセット
        setCurrentSet({ weight: '', reps: '' })
        toast.success(`${currentExercise} セット${setNumber}を記録しました`)
      }
    } catch (error) {
      console.error('セット記録エラー:', error)
      toast.error('セットの記録に失敗しました')
    }
  }

  const endSession = async () => {
    if (!activeSession) return

    try {
      await fetch(`/api/training/sessions/${activeSession.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'completed' }),
      })
      
      setActiveSession(null)
      setSessionStartTime(null)
      toast.success('トレーニングを終了しました')
    } catch (error) {
      console.error('セッション終了エラー:', error)
      toast.error('セッションの終了に失敗しました')
    }
  }

  const getElapsedTime = () => {
    if (!sessionStartTime) return '00:00'
    const elapsed = new Date().getTime() - sessionStartTime.getTime()
    const minutes = Math.floor(elapsed / 60000)
    const seconds = Math.floor((elapsed % 60000) / 1000)
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
  }

  // セッション開始前の画面
  if (!activeSession) {
    return (
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>トレーニング開始</CardTitle>
            <CardDescription>
              保存済みのルーティンを選択するか、フリートレーニングを開始してください
            </CardDescription>
          </CardHeader>
          <CardContent>
            {/* ルーティン選択 */}
            {routines.length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-3">保存済みルーティン</h3>
                <div className="grid gap-3">
                  {routines.map(routine => (
                    <Card
                      key={routine.id}
                      className="cursor-pointer hover:shadow-md transition-shadow"
                      onClick={() => startSession(routine.id)}
                    >
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                          <div>
                            <h4 className="font-semibold">{routine.name}</h4>
                            <p className="text-sm text-muted-foreground">{routine.description}</p>
                            <div className="mt-2">
                              {routine.exercises.slice(0, 3).map((ex, idx) => (
                                <span key={idx} className="inline-block text-xs bg-primary/10 text-primary px-2 py-1 rounded mr-1">
                                  {ex.exercise_name}
                                </span>
                              ))}
                              {routine.exercises.length > 3 && (
                                <span className="text-xs text-muted-foreground">
                                  +{routine.exercises.length - 3}
                                </span>
                              )}
                            </div>
                          </div>
                          <PlayCircle className="w-8 h-8 text-primary" />
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            )}

            {/* フリートレーニング */}
            <Button
              onClick={() => startSession()}
              size="lg"
              className="w-full"
              variant="outline"
            >
              <Dumbbell className="w-5 h-5 mr-2" />
              フリートレーニングを開始
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  // トレーニング記録画面
  return (
    <div className="space-y-6">
      {/* セッション情報 */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
              トレーニング中
            </CardTitle>
            <div className="text-2xl font-mono font-bold">{getElapsedTime()}</div>
          </div>
        </CardHeader>
      </Card>

      {/* セット入力 */}
      <Card>
        <CardHeader>
          <CardTitle>セット記録</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">エクササイズ</label>
            <Select value={currentExercise} onValueChange={setCurrentExercise}>
              <SelectTrigger>
                <SelectValue placeholder="エクササイズを選択" />
              </SelectTrigger>
              <SelectContent>
                {EXERCISE_LIST.map(exercise => (
                  <SelectItem key={exercise} value={exercise}>
                    {exercise}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">重量 (kg)</label>
              <Input
                type="number"
                step="0.5"
                value={currentSet.weight}
                onChange={(e) => setCurrentSet(prev => ({ ...prev, weight: e.target.value }))}
                placeholder="0"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">レップ数</label>
              <Input
                type="number"
                value={currentSet.reps}
                onChange={(e) => setCurrentSet(prev => ({ ...prev, reps: e.target.value }))}
                placeholder="0"
              />
            </div>
          </div>

          <Button
            onClick={recordSet}
            disabled={!currentExercise || !currentSet.weight || !currentSet.reps}
            className="w-full"
          >
            <Check className="w-4 h-4 mr-2" />
            セット完了
          </Button>
        </CardContent>
      </Card>

      {/* 記録済みセット */}
      {activeSession.sets.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>今日の記録</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {activeSession.sets.map((set, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-muted rounded-lg">
                  <div>
                    <span className="font-medium">{set.exercise_name}</span>
                    <span className="text-sm text-muted-foreground ml-2">
                      セット{set.set_number}
                    </span>
                  </div>
                  <div className="font-mono">
                    {set.weight}kg × {set.reps}回
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* セッション終了 */}
      <Button
        onClick={endSession}
        variant="destructive"
        size="lg"
        className="w-full"
      >
        <StopCircle className="w-5 h-5 mr-2" />
        トレーニング終了
      </Button>
    </div>
  )
}