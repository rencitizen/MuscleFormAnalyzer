'use client'

import { useState, useRef } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Progress } from '@/components/ui/progress'
import { 
  Camera,
  Upload,
  Plus,
  Trash2,
  Save,
  PieChart,
  Info
} from 'lucide-react'
import Image from 'next/image'

interface FoodItem {
  id: string
  name: string
  calories: number
  protein: number
  carbs: number
  fat: number
  quantity: number
  unit: string
}

interface MealAnalysis {
  totalCalories: number
  totalProtein: number
  totalCarbs: number
  totalFat: number
  foods: FoodItem[]
}

export default function MealAnalysisPage() {
  const [imageUrl, setImageUrl] = useState<string>('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysis, setAnalysis] = useState<MealAnalysis | null>(null)
  const [manualFood, setManualFood] = useState({
    name: '',
    calories: '',
    protein: '',
    carbs: '',
    fat: '',
    quantity: '100',
    unit: 'g'
  })
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleImageUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    const url = URL.createObjectURL(file)
    setImageUrl(url)

    // 画像分析を開始
    await analyzeImage(file)
  }

  const analyzeImage = async (file: File) => {
    setIsAnalyzing(true)
    
    // ここでAPIを呼び出す（仮実装）
    setTimeout(() => {
      setAnalysis({
        totalCalories: 650,
        totalProtein: 45,
        totalCarbs: 60,
        totalFat: 20,
        foods: [
          {
            id: '1',
            name: '鶏胸肉のグリル',
            calories: 250,
            protein: 35,
            carbs: 0,
            fat: 11,
            quantity: 150,
            unit: 'g'
          },
          {
            id: '2',
            name: 'ブロッコリー',
            calories: 50,
            protein: 4,
            carbs: 10,
            fat: 0.5,
            quantity: 150,
            unit: 'g'
          },
          {
            id: '3',
            name: '玄米',
            calories: 350,
            protein: 6,
            carbs: 50,
            fat: 8.5,
            quantity: 200,
            unit: 'g'
          }
        ]
      })
      setIsAnalyzing(false)
    }, 2000)
  }

  const addManualFood = () => {
    if (!manualFood.name || !manualFood.calories) return

    const newFood: FoodItem = {
      id: Date.now().toString(),
      name: manualFood.name,
      calories: Number(manualFood.calories),
      protein: Number(manualFood.protein) || 0,
      carbs: Number(manualFood.carbs) || 0,
      fat: Number(manualFood.fat) || 0,
      quantity: Number(manualFood.quantity),
      unit: manualFood.unit
    }

    if (analysis) {
      setAnalysis({
        ...analysis,
        totalCalories: analysis.totalCalories + newFood.calories,
        totalProtein: analysis.totalProtein + newFood.protein,
        totalCarbs: analysis.totalCarbs + newFood.carbs,
        totalFat: analysis.totalFat + newFood.fat,
        foods: [...analysis.foods, newFood]
      })
    } else {
      setAnalysis({
        totalCalories: newFood.calories,
        totalProtein: newFood.protein,
        totalCarbs: newFood.carbs,
        totalFat: newFood.fat,
        foods: [newFood]
      })
    }

    // フォームをリセット
    setManualFood({
      name: '',
      calories: '',
      protein: '',
      carbs: '',
      fat: '',
      quantity: '100',
      unit: 'g'
    })
  }

  const removeFood = (id: string) => {
    if (!analysis) return

    const foodToRemove = analysis.foods.find(f => f.id === id)
    if (!foodToRemove) return

    setAnalysis({
      ...analysis,
      totalCalories: analysis.totalCalories - foodToRemove.calories,
      totalProtein: analysis.totalProtein - foodToRemove.protein,
      totalCarbs: analysis.totalCarbs - foodToRemove.carbs,
      totalFat: analysis.totalFat - foodToRemove.fat,
      foods: analysis.foods.filter(f => f.id !== id)
    })
  }

  const saveMeal = async () => {
    // API呼び出し実装予定
    console.log('Saving meal:', analysis)
  }

  const getDailyTotals = () => {
    // 1日の累計を計算（仮実装）
    return {
      calories: (analysis?.totalCalories || 0) + 1200,
      protein: (analysis?.totalProtein || 0) + 80,
      carbs: (analysis?.totalCarbs || 0) + 150,
      fat: (analysis?.totalFat || 0) + 40
    }
  }

  const dailyTotals = getDailyTotals()

  return (
    <div className="container mx-auto px-4 py-8 pb-24 md:pb-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">食事分析</h1>
        <p className="text-muted-foreground">写真から食事内容を分析し、栄養価を計算します</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* 左側：画像アップロード */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>食事写真</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {imageUrl ? (
                  <div className="relative aspect-square rounded-lg overflow-hidden bg-gray-100">
                    <Image
                      src={imageUrl}
                      alt="Uploaded meal"
                      fill
                      className="object-cover"
                    />
                  </div>
                ) : (
                  <div className="aspect-square rounded-lg bg-gray-100 flex items-center justify-center">
                    <div className="text-center">
                      <Camera className="w-12 h-12 mx-auto mb-2 text-gray-400" />
                      <p className="text-sm text-gray-500">写真をアップロード</p>
                    </div>
                  </div>
                )}

                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleImageUpload}
                  className="hidden"
                />
                <Button
                  onClick={() => fileInputRef.current?.click()}
                  className="w-full"
                  disabled={isAnalyzing}
                >
                  {isAnalyzing ? (
                    <>分析中...</>
                  ) : (
                    <>
                      <Upload className="w-4 h-4 mr-2" />
                      写真を選択
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* PFCバランス */}
          {analysis && (
            <Card className="mt-4">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <PieChart className="w-5 h-5" />
                  PFCバランス
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>タンパク質</span>
                      <span>{analysis.totalProtein}g</span>
                    </div>
                    <Progress 
                      value={(analysis.totalProtein * 4 / analysis.totalCalories) * 100} 
                      className="h-2"
                    />
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>炭水化物</span>
                      <span>{analysis.totalCarbs}g</span>
                    </div>
                    <Progress 
                      value={(analysis.totalCarbs * 4 / analysis.totalCalories) * 100} 
                      className="h-2"
                    />
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>脂質</span>
                      <span>{analysis.totalFat}g</span>
                    </div>
                    <Progress 
                      value={(analysis.totalFat * 9 / analysis.totalCalories) * 100} 
                      className="h-2"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* 中央：検出された食品 */}
        <div className="lg:col-span-2 space-y-4">
          {/* 検出された食品リスト */}
          <Card>
            <CardHeader>
              <CardTitle>検出された食品</CardTitle>
              <CardDescription>
                写真から識別された食品と栄養成分
              </CardDescription>
            </CardHeader>
            <CardContent>
              {analysis && analysis.foods.length > 0 ? (
                <div className="space-y-3">
                  {analysis.foods.map((food) => (
                    <div key={food.id} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h4 className="font-semibold">{food.name}</h4>
                          <p className="text-sm text-muted-foreground">
                            {food.quantity}{food.unit}
                          </p>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeFood(food.id)}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                      <div className="grid grid-cols-4 gap-2 text-sm">
                        <div>
                          <span className="text-muted-foreground">カロリー:</span>
                          <p className="font-medium">{food.calories}kcal</p>
                        </div>
                        <div>
                          <span className="text-muted-foreground">P:</span>
                          <p className="font-medium">{food.protein}g</p>
                        </div>
                        <div>
                          <span className="text-muted-foreground">C:</span>
                          <p className="font-medium">{food.carbs}g</p>
                        </div>
                        <div>
                          <span className="text-muted-foreground">F:</span>
                          <p className="font-medium">{food.fat}g</p>
                        </div>
                      </div>
                    </div>
                  ))}
                  <div className="pt-4 border-t">
                    <div className="flex justify-between items-center">
                      <span className="font-semibold">合計</span>
                      <div className="text-right">
                        <p className="font-bold text-lg">{analysis.totalCalories} kcal</p>
                        <p className="text-sm text-muted-foreground">
                          P: {analysis.totalProtein}g / C: {analysis.totalCarbs}g / F: {analysis.totalFat}g
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <p className="text-center text-muted-foreground py-8">
                  写真をアップロードして分析を開始してください
                </p>
              )}
            </CardContent>
          </Card>

          {/* 手動追加 */}
          <Card>
            <CardHeader>
              <CardTitle>食品を手動で追加</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="md:col-span-2">
                  <Label htmlFor="food-name">食品名</Label>
                  <Input
                    id="food-name"
                    value={manualFood.name}
                    onChange={(e) => setManualFood({...manualFood, name: e.target.value})}
                    placeholder="例: 鶏胸肉"
                  />
                </div>
                <div>
                  <Label htmlFor="quantity">分量</Label>
                  <div className="flex gap-2">
                    <Input
                      id="quantity"
                      type="number"
                      value={manualFood.quantity}
                      onChange={(e) => setManualFood({...manualFood, quantity: e.target.value})}
                    />
                    <Input
                      value={manualFood.unit}
                      onChange={(e) => setManualFood({...manualFood, unit: e.target.value})}
                      className="w-20"
                    />
                  </div>
                </div>
                <div>
                  <Label htmlFor="calories">カロリー (kcal)</Label>
                  <Input
                    id="calories"
                    type="number"
                    value={manualFood.calories}
                    onChange={(e) => setManualFood({...manualFood, calories: e.target.value})}
                  />
                </div>
                <div>
                  <Label htmlFor="protein">タンパク質 (g)</Label>
                  <Input
                    id="protein"
                    type="number"
                    value={manualFood.protein}
                    onChange={(e) => setManualFood({...manualFood, protein: e.target.value})}
                  />
                </div>
                <div>
                  <Label htmlFor="carbs">炭水化物 (g)</Label>
                  <Input
                    id="carbs"
                    type="number"
                    value={manualFood.carbs}
                    onChange={(e) => setManualFood({...manualFood, carbs: e.target.value})}
                  />
                </div>
                <div>
                  <Label htmlFor="fat">脂質 (g)</Label>
                  <Input
                    id="fat"
                    type="number"
                    value={manualFood.fat}
                    onChange={(e) => setManualFood({...manualFood, fat: e.target.value})}
                  />
                </div>
              </div>
              <Button onClick={addManualFood} className="mt-4">
                <Plus className="w-4 h-4 mr-2" />
                追加
              </Button>
            </CardContent>
          </Card>

          {/* 1日の累計 */}
          <Card>
            <CardHeader>
              <CardTitle>今日の累計</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <p className="text-2xl font-bold">{dailyTotals.calories}</p>
                  <p className="text-sm text-muted-foreground">カロリー</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold">{dailyTotals.protein}</p>
                  <p className="text-sm text-muted-foreground">タンパク質(g)</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold">{dailyTotals.carbs}</p>
                  <p className="text-sm text-muted-foreground">炭水化物(g)</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold">{dailyTotals.fat}</p>
                  <p className="text-sm text-muted-foreground">脂質(g)</p>
                </div>
              </div>
              {analysis && (
                <Button onClick={saveMeal} className="w-full mt-4">
                  <Save className="w-4 h-4 mr-2" />
                  食事を保存
                </Button>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}