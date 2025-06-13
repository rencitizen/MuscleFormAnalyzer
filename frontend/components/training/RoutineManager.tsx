'use client'

import { useState, useEffect } from 'react'
import { Button } from '../ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Input } from '../ui/input'
import { Textarea } from '../ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '../ui/dialog'
import { Plus, Save, X, Edit, Trash2, Copy, AlertTriangle } from 'lucide-react'
import toast from 'react-hot-toast'

interface RoutineExercise {
  exercise_name: string
  target_sets: number
  target_reps: string
  target_weight?: number
  rest_time: number
  order_index: number
}

interface Routine {
  id?: string
  name: string
  description: string
  exercises: RoutineExercise[]
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

export function RoutineManager() {
  const [routines, setRoutines] = useState<Routine[]>([])
  const [isCreating, setIsCreating] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)
  const [newRoutine, setNewRoutine] = useState<Routine>({
    name: '',
    description: '',
    exercises: [],
  })

  useEffect(() => {
    fetchRoutines()
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
      toast.error('ルーティンの取得に失敗しました')
    }
  }

  const saveRoutine = async () => {
    if (!newRoutine.name) {
      toast.error('ルーティン名を入力してください')
      return
    }

    if (newRoutine.exercises.length === 0) {
      toast.error('エクササイズを追加してください')
      return
    }

    try {
      const method = editingId ? 'PUT' : 'POST'
      const url = editingId ? `/api/training/routines/${editingId}` : '/api/training/routines'
      
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newRoutine),
      })

      if (response.ok) {
        const savedRoutine = await response.json()
        
        if (editingId) {
          setRoutines(prev => prev.map(r => r.id === editingId ? savedRoutine : r))
          toast.success('ルーティンを更新しました')
        } else {
          setRoutines(prev => [...prev, savedRoutine])
          toast.success('ルーティンを保存しました')
        }
        
        resetForm()
      }
    } catch (error) {
      console.error('ルーティン保存エラー:', error)
      toast.error('ルーティンの保存に失敗しました')
    }
  }

  const handleDeleteClick = (id: string) => {
    setDeletingId(id)
  }

  const confirmDelete = async () => {
    if (!deletingId) return

    setIsDeleting(true)
    try {
      const response = await fetch(`/api/training/routines/${deletingId}`, {
        method: 'DELETE',
      })

      if (response.ok) {
        // 楽観的UI更新
        setRoutines(prev => prev.filter(r => r.id !== deletingId))
        toast.success('ルーティンを削除しました')
        setDeletingId(null)
      } else {
        const error = await response.json()
        toast.error(error.error || 'ルーティンの削除に失敗しました')
      }
    } catch (error) {
      console.error('ルーティン削除エラー:', error)
      toast.error('ルーティンの削除に失敗しました')
    } finally {
      setIsDeleting(false)
    }
  }

  const cancelDelete = () => {
    setDeletingId(null)
  }

  const addExercise = () => {
    setNewRoutine(prev => ({
      ...prev,
      exercises: [
        ...prev.exercises,
        {
          exercise_name: '',
          target_sets: 3,
          target_reps: '8-12',
          target_weight: undefined,
          rest_time: 60,
          order_index: prev.exercises.length,
        },
      ],
    }))
  }

  const updateExercise = (index: number, field: keyof RoutineExercise, value: any) => {
    const updatedExercises = [...newRoutine.exercises]
    updatedExercises[index] = {
      ...updatedExercises[index],
      [field]: value,
    }
    setNewRoutine(prev => ({ ...prev, exercises: updatedExercises }))
  }

  const removeExercise = (index: number) => {
    setNewRoutine(prev => ({
      ...prev,
      exercises: prev.exercises.filter((_, i) => i !== index),
    }))
  }

  const editRoutine = (routine: Routine) => {
    setNewRoutine(routine)
    setEditingId(routine.id || null)
    setIsCreating(true)
  }

  const duplicateRoutine = (routine: Routine) => {
    setNewRoutine({
      ...routine,
      name: `${routine.name} (コピー)`,
      id: undefined,
    })
    setEditingId(null)
    setIsCreating(true)
  }

  const resetForm = () => {
    setNewRoutine({ name: '', description: '', exercises: [] })
    setIsCreating(false)
    setEditingId(null)
  }

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">ルーティン管理</h2>
        {!isCreating && (
          <Button onClick={() => setIsCreating(true)}>
            <Plus className="w-4 h-4 mr-2" />
            新規ルーティン
          </Button>
        )}
      </div>

      {/* ルーティン作成/編集フォーム */}
      {isCreating && (
        <Card>
          <CardHeader>
            <CardTitle>{editingId ? 'ルーティン編集' : '新規ルーティン作成'}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">ルーティン名</label>
              <Input
                value={newRoutine.name}
                onChange={(e) => setNewRoutine(prev => ({ ...prev, name: e.target.value }))}
                placeholder="例: 胸・肩・上腕三頭筋"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">説明</label>
              <Textarea
                value={newRoutine.description}
                onChange={(e) => setNewRoutine(prev => ({ ...prev, description: e.target.value }))}
                placeholder="ルーティンの説明や注意点など"
                rows={3}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">エクササイズ</label>
              <div className="space-y-3">
                {newRoutine.exercises.map((exercise, index) => (
                  <Card key={index}>
                    <CardContent className="p-4">
                      <div className="grid gap-3">
                        <div className="flex items-center gap-2">
                          <Select
                            value={exercise.exercise_name}
                            onValueChange={(value) => updateExercise(index, 'exercise_name', value)}
                          >
                            <SelectTrigger className="flex-1">
                              <SelectValue placeholder="エクササイズを選択" />
                            </SelectTrigger>
                            <SelectContent>
                              {EXERCISE_LIST.map(ex => (
                                <SelectItem key={ex} value={ex}>
                                  {ex}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => removeExercise(index)}
                          >
                            <X className="w-4 h-4" />
                          </Button>
                        </div>

                        <div className="grid grid-cols-4 gap-2">
                          <div>
                            <label className="text-xs text-muted-foreground">セット数</label>
                            <Input
                              type="number"
                              value={exercise.target_sets}
                              onChange={(e) => updateExercise(index, 'target_sets', parseInt(e.target.value))}
                              min="1"
                            />
                          </div>
                          <div>
                            <label className="text-xs text-muted-foreground">レップ数</label>
                            <Input
                              value={exercise.target_reps}
                              onChange={(e) => updateExercise(index, 'target_reps', e.target.value)}
                              placeholder="8-12"
                            />
                          </div>
                          <div>
                            <label className="text-xs text-muted-foreground">重量(kg)</label>
                            <Input
                              type="number"
                              value={exercise.target_weight || ''}
                              onChange={(e) => updateExercise(index, 'target_weight', e.target.value ? parseFloat(e.target.value) : undefined)}
                              placeholder="任意"
                              step="0.5"
                            />
                          </div>
                          <div>
                            <label className="text-xs text-muted-foreground">休憩(秒)</label>
                            <Input
                              type="number"
                              value={exercise.rest_time}
                              onChange={(e) => updateExercise(index, 'rest_time', parseInt(e.target.value))}
                              min="0"
                              step="15"
                            />
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}

                <Button
                  variant="outline"
                  onClick={addExercise}
                  className="w-full"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  エクササイズを追加
                </Button>
              </div>
            </div>

            <div className="flex gap-2">
              <Button onClick={saveRoutine} className="flex-1">
                <Save className="w-4 h-4 mr-2" />
                保存
              </Button>
              <Button variant="outline" onClick={resetForm}>
                キャンセル
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* ルーティン一覧 */}
      {!isCreating && (
        <div className="space-y-4">
          {routines.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center text-muted-foreground">
                まだルーティンがありません
              </CardContent>
            </Card>
          ) : (
            routines.map(routine => (
              <Card key={routine.id}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle>{routine.name}</CardTitle>
                      <CardDescription>{routine.description}</CardDescription>
                    </div>
                    <div className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => editRoutine(routine)}
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => duplicateRoutine(routine)}
                      >
                        <Copy className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDeleteClick(routine.id!)}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {routine.exercises.map((exercise, index) => (
                      <div key={index} className="flex items-center justify-between text-sm">
                        <span className="font-medium">{exercise.exercise_name}</span>
                        <span className="text-muted-foreground">
                          {exercise.target_sets}セット × {exercise.target_reps}レップ
                          {exercise.target_weight && ` @ ${exercise.target_weight}kg`}
                        </span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      )}

      {/* 削除確認ダイアログ */}
      <Dialog open={!!deletingId} onOpenChange={(open) => !open && cancelDelete()}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-destructive" />
              ルーティンの削除確認
            </DialogTitle>
            <DialogDescription>
              {routines.find(r => r.id === deletingId)?.name} を削除しますか？
              この操作は取り消すことができません。
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={cancelDelete} disabled={isDeleting}>
              キャンセル
            </Button>
            <Button 
              variant="destructive" 
              onClick={confirmDelete}
              disabled={isDeleting}
            >
              {isDeleting ? '削除中...' : '削除する'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}