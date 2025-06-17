'use client'

import { useState, useMemo } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Search,
  Filter,
  Dumbbell,
  Video,
  BookOpen,
  Star,
  ChevronRight,
  X
} from 'lucide-react'
import { completeExerciseDatabase } from '@/lib/engines/training/completeExerciseDatabase'

interface ExerciseFilter {
  search: string
  category: string
  muscle: string
  equipment: string
  difficulty: string
}

export default function ExerciseDatabasePage() {
  const [filter, setFilter] = useState<ExerciseFilter>({
    search: '',
    category: 'all',
    muscle: 'all',
    equipment: 'all',
    difficulty: 'all'
  })
  const [selectedExercise, setSelectedExercise] = useState<any>(null)

  // カテゴリー別にエクササイズを整理
  const allExercises = Object.entries(completeExerciseDatabase).flatMap(([category, exercises]) =>
    Object.entries(exercises).map(([key, exercise]) => ({
      ...exercise,
      id: key,
      category
    }))
  )

  // フィルタリング
  const filteredExercises = useMemo(() => {
    return allExercises.filter(exercise => {
      if (filter.search && !exercise.name.toLowerCase().includes(filter.search.toLowerCase())) {
        return false
      }
      if (filter.category !== 'all' && exercise.category !== filter.category) {
        return false
      }
      if (filter.muscle !== 'all' && !exercise.primaryMuscles.includes(filter.muscle)) {
        return false
      }
      if (filter.equipment !== 'all' && exercise.equipment !== filter.equipment) {
        return false
      }
      if (filter.difficulty !== 'all' && exercise.difficulty !== filter.difficulty) {
        return false
      }
      return true
    })
  }, [filter, allExercises])

  // 統計情報
  const stats = {
    total: allExercises.length,
    byCategory: {
      compound: allExercises.filter(e => e.category === 'compound').length,
      isolation: allExercises.filter(e => e.category === 'isolation').length,
      olympic: allExercises.filter(e => e.category === 'olympic').length,
      plyometric: allExercises.filter(e => e.category === 'plyometric').length,
      cardio: allExercises.filter(e => e.category === 'cardio').length
    }
  }

  const categories = [
    { value: 'all', label: 'すべて' },
    { value: 'compound', label: 'コンパウンド' },
    { value: 'isolation', label: 'アイソレーション' },
    { value: 'olympic', label: 'オリンピックリフト' },
    { value: 'plyometric', label: 'プライオメトリック' },
    { value: 'cardio', label: '有酸素' }
  ]

  const muscles = [
    { value: 'all', label: 'すべて' },
    { value: 'chest', label: '胸' },
    { value: 'back', label: '背中' },
    { value: 'legs', label: '脚' },
    { value: 'shoulders', label: '肩' },
    { value: 'arms', label: '腕' },
    { value: 'core', label: '体幹' },
    { value: 'glutes', label: '臀部' }
  ]

  const equipmentOptions = [
    { value: 'all', label: 'すべて' },
    { value: 'barbell', label: 'バーベル' },
    { value: 'dumbbell', label: 'ダンベル' },
    { value: 'machine', label: 'マシン' },
    { value: 'cable', label: 'ケーブル' },
    { value: 'bodyweight', label: '自重' },
    { value: 'bands', label: 'バンド' },
    { value: 'kettlebell', label: 'ケトルベル' }
  ]

  const difficulties = [
    { value: 'all', label: 'すべて' },
    { value: 'beginner', label: '初級' },
    { value: 'intermediate', label: '中級' },
    { value: 'advanced', label: '上級' }
  ]

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'bg-green-500'
      case 'intermediate': return 'bg-yellow-500'
      case 'advanced': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }

  return (
    <div className="container mx-auto px-4 py-8 pb-24 md:pb-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">エクササイズデータベース</h1>
        <p className="text-muted-foreground">600種類以上のエクササイズから検索</p>
      </div>

      {/* 統計情報 */}
      <div className="grid gap-4 md:grid-cols-6 mb-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">総エクササイズ数</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{stats.total}</p>
          </CardContent>
        </Card>
        {Object.entries(stats.byCategory).map(([category, count]) => (
          <Card key={category}>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm capitalize">{category}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold">{count}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-4">
        {/* 左側：フィルター */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Filter className="w-5 h-5" />
                フィルター
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="search">検索</Label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    id="search"
                    type="text"
                    placeholder="エクササイズ名で検索"
                    value={filter.search}
                    onChange={(e) => setFilter({...filter, search: e.target.value})}
                    className="pl-10"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="category">カテゴリー</Label>
                <Select
                  value={filter.category}
                  onValueChange={(value) => setFilter({...filter, category: value})}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.map((cat) => (
                      <SelectItem key={cat.value} value={cat.value}>
                        {cat.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="muscle">筋肉群</Label>
                <Select
                  value={filter.muscle}
                  onValueChange={(value) => setFilter({...filter, muscle: value})}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {muscles.map((muscle) => (
                      <SelectItem key={muscle.value} value={muscle.value}>
                        {muscle.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="equipment">器具</Label>
                <Select
                  value={filter.equipment}
                  onValueChange={(value) => setFilter({...filter, equipment: value})}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {equipmentOptions.map((eq) => (
                      <SelectItem key={eq.value} value={eq.value}>
                        {eq.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="difficulty">難易度</Label>
                <Select
                  value={filter.difficulty}
                  onValueChange={(value) => setFilter({...filter, difficulty: value})}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {difficulties.map((diff) => (
                      <SelectItem key={diff.value} value={diff.value}>
                        {diff.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <Button
                variant="outline"
                className="w-full"
                onClick={() => setFilter({
                  search: '',
                  category: 'all',
                  muscle: 'all',
                  equipment: 'all',
                  difficulty: 'all'
                })}
              >
                <X className="w-4 h-4 mr-2" />
                フィルターをリセット
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* 右側：エクササイズリスト */}
        <div className="lg:col-span-3">
          <div className="mb-4">
            <p className="text-sm text-muted-foreground">
              {filteredExercises.length} 件のエクササイズが見つかりました
            </p>
          </div>

          <div className="grid gap-4">
            {filteredExercises.map((exercise) => (
              <Card 
                key={exercise.id} 
                className="cursor-pointer hover:shadow-md transition-shadow"
                onClick={() => setSelectedExercise(exercise)}
              >
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-lg">{exercise.name}</CardTitle>
                      <CardDescription className="capitalize">
                        {exercise.category} • {exercise.equipment}
                      </CardDescription>
                    </div>
                    <Badge className={`${getDifficultyColor(exercise.difficulty)} text-white`}>
                      {exercise.difficulty === 'beginner' ? '初級' :
                       exercise.difficulty === 'intermediate' ? '中級' : '上級'}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2 mb-3">
                    <div className="text-sm">
                      <span className="text-muted-foreground">主働筋:</span>
                      <span className="ml-1 font-medium">
                        {exercise.primaryMuscles.join(', ')}
                      </span>
                    </div>
                    {exercise.secondaryMuscles.length > 0 && (
                      <div className="text-sm">
                        <span className="text-muted-foreground">補助筋:</span>
                        <span className="ml-1">
                          {exercise.secondaryMuscles.join(', ')}
                        </span>
                      </div>
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground line-clamp-2">
                    {exercise.description}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>

          {filteredExercises.length === 0 && (
            <Card>
              <CardContent className="py-8">
                <div className="text-center">
                  <Dumbbell className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                  <p className="text-muted-foreground">
                    条件に一致するエクササイズが見つかりません
                  </p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* エクササイズ詳細モーダル */}
      {selectedExercise && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <Card className="max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle>{selectedExercise.name}</CardTitle>
                  <CardDescription className="capitalize">
                    {selectedExercise.category} • {selectedExercise.equipment}
                  </CardDescription>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setSelectedExercise(null)}
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="details" className="space-y-4">
                <TabsList>
                  <TabsTrigger value="details">
                    <BookOpen className="w-4 h-4 mr-2" />
                    詳細
                  </TabsTrigger>
                  <TabsTrigger value="execution">
                    <ChevronRight className="w-4 h-4 mr-2" />
                    実行方法
                  </TabsTrigger>
                  <TabsTrigger value="tips">
                    <Star className="w-4 h-4 mr-2" />
                    ポイント
                  </TabsTrigger>
                </Tabs>

                <TabsContent value="details" className="space-y-4">
                  <div>
                    <h4 className="font-semibold mb-2">説明</h4>
                    <p className="text-sm">{selectedExercise.description}</p>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-semibold mb-2">主働筋</h4>
                      <div className="flex flex-wrap gap-2">
                        {selectedExercise.primaryMuscles.map((muscle: string) => (
                          <Badge key={muscle} variant="default">
                            {muscle}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    <div>
                      <h4 className="font-semibold mb-2">補助筋</h4>
                      <div className="flex flex-wrap gap-2">
                        {selectedExercise.secondaryMuscles.map((muscle: string) => (
                          <Badge key={muscle} variant="secondary">
                            {muscle}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="execution" className="space-y-4">
                  <div>
                    <h4 className="font-semibold mb-2">準備</h4>
                    <p className="text-sm">{selectedExercise.preparation}</p>
                  </div>
                  <div>
                    <h4 className="font-semibold mb-2">実行</h4>
                    <p className="text-sm">{selectedExercise.execution}</p>
                  </div>
                </TabsContent>

                <TabsContent value="tips" className="space-y-4">
                  <div>
                    <h4 className="font-semibold mb-2">フォームのポイント</h4>
                    <ul className="list-disc list-inside space-y-1">
                      {selectedExercise.tips.map((tip: string, index: number) => (
                        <li key={index} className="text-sm">{tip}</li>
                      ))}
                    </ul>
                  </div>
                  {selectedExercise.commonMistakes && (
                    <div>
                      <h4 className="font-semibold mb-2">よくある間違い</h4>
                      <ul className="list-disc list-inside space-y-1">
                        {selectedExercise.commonMistakes.map((mistake: string, index: number) => (
                          <li key={index} className="text-sm">{mistake}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}