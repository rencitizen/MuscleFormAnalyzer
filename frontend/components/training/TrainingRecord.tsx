'use client'

import { useState, useEffect } from 'react'
import { Button } from '../ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Input } from '../ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select'
import { Plus, Check, X, PlayCircle, StopCircle, Dumbbell } from 'lucide-react'
import toast from 'react-hot-toast'

interface TrainingSet {
  id?: string
  exercise_name: string
  set_number: number
  weight: number
  reps: number
  completed: boolean
}

interface PlannedExercise {
  exercise_name: string
  target_sets: number
  target_reps: string
  target_weight?: number
  rest_time?: number
  order_index?: number
  completed_sets: number
  planned_sets: number
}

interface TrainingSession {
  id: string
  routine_id?: string
  date: string
  sets: TrainingSet[]
  start_time?: string
  end_time?: string
  plannedExercises?: PlannedExercise[]
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
          // 計画された種目がある場合、最初の種目を選択
          if (session.plannedExercises && session.plannedExercises.length > 0) {
            setCurrentExercise(session.plannedExercises[0].exercise_name)
          }
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
        // 計画された種目がある場合、最初の種目を選択
        if (session.plannedExercises && session.plannedExercises.length > 0) {
          setCurrentExercise(session.plannedExercises[0].exercise_name)
          // 目標重量がある場合は設定
          if (session.plannedExercises[0].target_weight) {
            setCurrentSet(prev => ({ ...prev, weight: session.plannedExercises[0].target_weight.toString() }))
          }
        }
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
        setActiveSession(prev => {
          if (!prev) return null
          
          const updatedSession = {
            ...prev,
            sets: [...prev.sets, newSet],
          }
          
          // ルーティンの進捗をチェックし、次の種目に移動
          if (prev.plannedExercises && prev.plannedExercises.length > 0) {
            const currentExerciseIndex = prev.plannedExercises.findIndex(
              e => e.exercise_name === currentExercise
            )
            if (currentExerciseIndex !== -1) {
              const currentPlannedExercise = prev.plannedExercises[currentExerciseIndex]
              const completedSetsForExercise = updatedSession.sets.filter(
                s => s.exercise_name === currentExercise
              ).length
              
              // 現在の種目が完了したら次の種目に移動
              if (completedSetsForExercise >= currentPlannedExercise.target_sets) {
                const nextIncompleteExercise = prev.plannedExercises.find((ex, idx) => {
                  if (idx <= currentExerciseIndex) return false
                  const setsCompleted = updatedSession.sets.filter(
                    s => s.exercise_name === ex.exercise_name
                  ).length
                  return setsCompleted < ex.target_sets
                })
                
                if (nextIncompleteExercise) {
                  setCurrentExercise(nextIncompleteExercise.exercise_name)
                  if (nextIncompleteExercise.target_weight) {
                    setCurrentSet({ weight: nextIncompleteExercise.target_weight.toString(), reps: '' })
                  } else {
                    setCurrentSet({ weight: '', reps: '' })
                  }
                  toast.success(`${currentExercise} セット${setNumber}を記録しました\n次: ${nextIncompleteExercise.exercise_name}`)
                } else {
                  // フォームリセット
                  setCurrentSet({ weight: '', reps: '' })
                  toast.success(`${currentExercise} セット${setNumber}を記録しました`)
                }
              } else {
                // フォームリセット（レップ数のみ）
                setCurrentSet(prev => ({ ...prev, reps: '' }))
                toast.success(`${currentExercise} セット${setNumber}を記録しました`)
              }
            } else {
              // フォームリセット
              setCurrentSet({ weight: '', reps: '' })
              toast.success(`${currentExercise} セット${setNumber}を記録しました`)
            }
          } else {
            // フォームリセット
            setCurrentSet({ weight: '', reps: '' })
            toast.success(`${currentExercise} セット${setNumber}を記録しました`)
          }
          
          return updatedSession
        })
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

  // ルーティンの進捗計算
  const getRoutineProgress = () => {
    if (!activeSession.plannedExercises || activeSession.plannedExercises.length === 0) {
      return null
    }
    
    const totalSets = activeSession.plannedExercises.reduce(
      (sum, ex) => sum + ex.target_sets, 0
    )
    const completedSets = activeSession.sets.length
    const progressPercentage = Math.round((completedSets / totalSets) * 100)
    
    return {
      completedSets,
      totalSets,
      progressPercentage,
    }
  }

  const routineProgress = getRoutineProgress()

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
          {routineProgress && (
            <div className="mt-4">
              <div className="flex items-center justify-between text-sm mb-2">
                <span className="text-muted-foreground">ルーティン進捗</span>
                <span className="font-semibold">
                  {routineProgress.completedSets} / {routineProgress.totalSets} セット
                </span>
              </div>
              <div className="w-full bg-secondary rounded-full h-2">
                <div
                  className="bg-primary h-2 rounded-full transition-all duration-300"
                  style={{ width: `${routineProgress.progressPercentage}%` }}
                />
              </div>
            </div>
          )}
        </CardHeader>
      </Card>

      {/* ルーティンから計画された種目 */}
      {activeSession.plannedExercises && activeSession.plannedExercises.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>本日のトレーニングメニュー</CardTitle>
            <CardDescription>
              ルーティンから読み込まれた種目一覧
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {activeSession.plannedExercises.map((exercise, index) => {
                const completedSets = activeSession.sets.filter(
                  s => s.exercise_name === exercise.exercise_name
                ).length
                const isCompleted = completedSets >= exercise.target_sets
                const isActive = currentExercise === exercise.exercise_name
                
                return (
                  <div
                    key={index}
                    className={`p-4 rounded-lg border transition-all cursor-pointer ${
                      isActive ? 'border-primary bg-primary/5' : 'border-border'
                    } ${isCompleted ? 'opacity-60' : ''}`}
                    onClick={() => {
                      setCurrentExercise(exercise.exercise_name)
                      if (exercise.target_weight) {
                        setCurrentSet(prev => ({ ...prev, weight: exercise.target_weight.toString() }))
                      }
                    }}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-semibold flex items-center gap-2">
                          {exercise.exercise_name}
                          {isCompleted && <Check className="w-4 h-4 text-green-600" />}
                        </h4>
                        <p className="text-sm text-muted-foreground">
                          {exercise.target_sets}セット × {exercise.target_reps}レップ
                          {exercise.target_weight && ` @ ${exercise.target_weight}kg`}
                        </p>
                      </div>
                      <div className="text-right">
                        <div className="text-lg font-semibold">
                          {completedSets} / {exercise.target_sets}
                        </div>
                        <div className="text-xs text-muted-foreground">完了セット</div>
                      </div>
                    </div>
                    {exercise.rest_time && (
                      <div className="mt-2 text-xs text-muted-foreground">
                        推奨休憩時間: {exercise.rest_time}秒
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>
      )}

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
                {/* ルーティンの種目を優先表示 */}
                {activeSession.plannedExercises && activeSession.plannedExercises.length > 0 && (
                  <>
                    <div className="px-2 py-1.5 text-xs font-semibold text-muted-foreground">ルーティンの種目</div>
                    {activeSession.plannedExercises.map((exercise, idx) => (
                      <SelectItem key={`planned-${idx}`} value={exercise.exercise_name}>
                        {exercise.exercise_name}
                      </SelectItem>
                    ))}
                    <div className="my-1 border-t" />
                    <div className="px-2 py-1.5 text-xs font-semibold text-muted-foreground">その他の種目</div>
                  </>
                )}
                {EXERCISE_LIST.filter(exercise => 
                  !activeSession.plannedExercises?.some(p => p.exercise_name === exercise)
                ).map(exercise => (
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