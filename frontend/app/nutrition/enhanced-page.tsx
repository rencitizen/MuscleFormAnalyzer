'use client'

import { useState, useEffect } from 'react'
import { Button } from '../../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'
import { Input } from '../../components/ui/input'
import { Label } from '../../components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs'
import { Progress } from '../../components/ui/progress'
import { Camera, Upload, Loader2, Plus, Star, Search, TrendingUp, X } from 'lucide-react'
import Image from 'next/image'
import { useToast } from '@/hooks/use-toast'
import { MealStorage, type FoodItem, type MealRecord } from '../../lib/storage/mealStorage'
import { CameraCapture } from '../../components/camera/CameraCapture'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '../../components/ui/dialog'

interface NutritionTotal {
  calories: number
  protein: number
  carbs: number
  fat: number
  fiber?: number
}

interface PFCBalance {
  protein_ratio: number
  carbs_ratio: number
  fat_ratio: number
}

export default function EnhancedNutritionPage() {
  const [selectedImage, setSelectedImage] = useState<string | null>(null)
  const [imageFile, setImageFile] = useState<File | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [foodItems, setFoodItems] = useState<FoodItem[]>([])
  const [mealType, setMealType] = useState<MealRecord['mealType']>('lunch')
  const [nutritionTotal, setNutritionTotal] = useState<NutritionTotal>({
    calories: 0,
    protein: 0,
    carbs: 0,
    fat: 0,
    fiber: 0
  })
  const [pfcBalance, setPfcBalance] = useState<PFCBalance>({
    protein_ratio: 0,
    carbs_ratio: 0,
    fat_ratio: 0
  })
  const [searchQuery, setSearchQuery] = useState('')
  const [foodSuggestions, setFoodSuggestions] = useState<FoodItem[]>([])
  const [favoriteFoods, setFavoriteFoods] = useState<FoodItem[]>([])
  const [showAddFood, setShowAddFood] = useState(false)
  const [showCamera, setShowCamera] = useState(false)
  const { toast } = useToast()

  useEffect(() => {
    // Load favorite foods
    setFavoriteFoods(MealStorage.getFavoriteFoods())
  }, [])

  useEffect(() => {
    // Recalculate totals when food items change
    calculateNutritionTotals()
  }, [foodItems])

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setImageFile(file)
      const reader = new FileReader()
      reader.onloadend = () => {
        setSelectedImage(reader.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleCameraCapture = (imageData: string, file: File) => {
    setSelectedImage(imageData)
    setImageFile(file)
    setShowCamera(false)
    
    toast({
      title: '撮影完了',
      description: '写真を撮影しました。分析を開始してください。',
    })
  }

  const handleAnalyze = async () => {
    if (!imageFile) return

    setIsAnalyzing(true)
    const formData = new FormData()
    formData.append('image', imageFile)

    try {
      const response = await fetch('http://localhost:5000/api/analyze-meal-image', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Failed to analyze image')
      }

      const data = await response.json()
      
      // Calculate detailed nutrition
      if (data.foods && data.foods.length > 0) {
        const nutritionResponse = await fetch('http://localhost:5000/api/meal/calculate-calories', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ foods: data.foods })
        })
        
        if (nutritionResponse.ok) {
          const nutritionData = await nutritionResponse.json()
          setFoodItems(nutritionData.foods || data.foods)
          if (nutritionData.total) {
            setNutritionTotal(nutritionData.total)
          }
          if (nutritionData.pfc_balance) {
            setPfcBalance(nutritionData.pfc_balance)
          }
        } else {
          setFoodItems(data.foods)
        }
      }
      
      toast({
        title: '分析完了',
        description: `${data.foods?.length || 0}個の食品を識別しました`,
      })
    } catch (error) {
      toast({
        title: '分析失敗',
        description: '画像の分析に失敗しました。もう一度お試しください。',
        variant: 'destructive',
      })
    } finally {
      setIsAnalyzing(false)
    }
  }

  const calculateNutritionTotals = () => {
    const total = foodItems.reduce(
      (acc, item) => ({
        calories: acc.calories + (item.calories || 0),
        protein: acc.protein + (item.protein || 0),
        carbs: acc.carbs + (item.carbs || 0),
        fat: acc.fat + (item.fat || 0),
        fiber: acc.fiber + (item.fiber || 0)
      }),
      { calories: 0, protein: 0, carbs: 0, fat: 0, fiber: 0 }
    )
    
    setNutritionTotal(total)
    
    // Calculate PFC balance
    const totalCal = (total.protein * 4) + (total.carbs * 4) + (total.fat * 9)
    if (totalCal > 0) {
      setPfcBalance({
        protein_ratio: Math.round((total.protein * 4 / totalCal) * 100),
        carbs_ratio: Math.round((total.carbs * 4 / totalCal) * 100),
        fat_ratio: Math.round((total.fat * 9 / totalCal) * 100)
      })
    }
  }

  const handleQuantityChange = (index: number, newQuantity: string) => {
    const updatedItems = [...foodItems]
    updatedItems[index].quantity = newQuantity
    setFoodItems(updatedItems)
  }

  const handleNutritionChange = (index: number, field: keyof FoodItem, value: string) => {
    const updatedItems = [...foodItems]
    updatedItems[index] = {
      ...updatedItems[index],
      [field]: parseFloat(value) || 0
    }
    setFoodItems(updatedItems)
  }

  const handleRemoveItem = (index: number) => {
    setFoodItems(foodItems.filter((_, i) => i !== index))
  }

  const handleAddItem = (food?: FoodItem) => {
    const newItem: FoodItem = food || {
      name: '新しい食品',
      quantity: '100g',
      calories: 100,
      protein: 5,
      carbs: 15,
      fat: 3,
      fiber: 1
    }
    setFoodItems([...foodItems, newItem])
    setShowAddFood(false)
  }

  const searchFoods = async (query: string) => {
    if (!query) {
      setFoodSuggestions([])
      return
    }

    try {
      const response = await fetch(`http://localhost:5000/api/meal/food-suggestions?q=${query}`)
      if (response.ok) {
        const data = await response.json()
        setFoodSuggestions(data.suggestions || [])
      }
    } catch (error) {
      console.error('Failed to search foods:', error)
    }
  }

  const handleSaveMeal = async () => {
    if (foodItems.length === 0) return

    const meal = MealStorage.createMeal(
      mealType,
      foodItems,
      selectedImage || undefined
    )
    
    const success = MealStorage.saveMeal(meal)
    
    if (success) {
      toast({
        title: '保存完了',
        description: `${mealType}を記録しました（${nutritionTotal.calories}kcal）`,
      })
      
      // Reset form
      setSelectedImage(null)
      setImageFile(null)
      setFoodItems([])
      setNutritionTotal({ calories: 0, protein: 0, carbs: 0, fat: 0, fiber: 0 })
    } else {
      toast({
        title: '保存エラー',
        description: '食事記録の保存に失敗しました',
        variant: 'destructive',
      })
    }
  }

  const toggleFavorite = (food: FoodItem) => {
    const isFavorite = favoriteFoods.some(f => f.name === food.name)
    if (isFavorite) {
      MealStorage.removeFavoriteFood(food.name)
      setFavoriteFoods(favoriteFoods.filter(f => f.name !== food.name))
    } else {
      MealStorage.addFavoriteFood(food)
      setFavoriteFoods([...favoriteFoods, food])
    }
  }

  const clearImage = () => {
    setSelectedImage(null)
    setImageFile(null)
  }

  return (
    <div className="container mx-auto p-4 max-w-6xl">
      <h1 className="text-3xl font-bold mb-6">食事管理 / Meal Management</h1>
      
      <div className="grid gap-6 md:grid-cols-2">
        {/* Left Column - Image Upload and Analysis */}
        <Card>
          <CardHeader>
            <CardTitle>食事の撮影・分析</CardTitle>
            <CardDescription>
              写真から食品を識別してカロリーを計算します
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Meal Type Selection */}
            <div>
              <Label>食事タイプ</Label>
              <div className="grid grid-cols-4 gap-2 mt-2">
                {(['breakfast', 'lunch', 'dinner', 'snack'] as const).map((type) => (
                  <Button
                    key={type}
                    variant={mealType === type ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setMealType(type)}
                  >
                    {type === 'breakfast' && '朝食'}
                    {type === 'lunch' && '昼食'}
                    {type === 'dinner' && '夕食'}
                    {type === 'snack' && '間食'}
                  </Button>
                ))}
              </div>
            </div>

            {/* Image Upload */}
            <div className="space-y-4">
              {selectedImage ? (
                <div className="relative w-full h-64">
                  <Image
                    src={selectedImage}
                    alt="Selected meal"
                    fill
                    className="object-cover rounded-lg"
                  />
                  <Button
                    onClick={clearImage}
                    size="icon"
                    variant="secondary"
                    className="absolute top-2 right-2"
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              ) : (
                <div className="w-full h-64 border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center">
                  <div className="text-center">
                    <Upload className="mx-auto h-12 w-12 text-gray-400" />
                    <p className="mt-2 text-sm text-gray-600">
                      写真を撮影またはアップロード
                    </p>
                  </div>
                </div>
              )}
              
              <div className="flex gap-2">
                <Button
                  onClick={() => setShowCamera(true)}
                  className="flex-1"
                  variant="outline"
                >
                  <Camera className="w-4 h-4 mr-2" />
                  カメラで撮影
                </Button>
                
                <Input
                  type="file"
                  accept="image/*"
                  onChange={handleImageSelect}
                  className="hidden"
                  id="meal-upload"
                />
                <Label
                  htmlFor="meal-upload"
                  className="cursor-pointer inline-flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 flex-1"
                >
                  <Upload className="w-4 h-4 mr-2" />
                  ファイル選択
                </Label>
              </div>
              
              <Button
                onClick={handleAnalyze}
                disabled={!selectedImage || isAnalyzing}
                className="w-full"
              >
                {isAnalyzing ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    分析中...
                  </>
                ) : (
                  '分析開始'
                )}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Right Column - Nutrition Summary */}
        <Card>
          <CardHeader>
            <CardTitle>栄養サマリー</CardTitle>
            <CardDescription>
              現在の食事の栄養バランス
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Total Calories */}
            <div className="text-center p-4 bg-primary/10 rounded-lg">
              <div className="text-3xl font-bold text-primary">
                {nutritionTotal.calories} kcal
              </div>
              <div className="text-sm text-gray-600">総カロリー</div>
            </div>

            {/* Macros */}
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-xl font-semibold">{nutritionTotal.protein.toFixed(1)}g</div>
                <div className="text-sm text-gray-600">タンパク質</div>
                <Progress value={pfcBalance.protein_ratio} className="mt-2" />
                <div className="text-xs text-gray-500 mt-1">{pfcBalance.protein_ratio}%</div>
              </div>
              <div className="text-center">
                <div className="text-xl font-semibold">{nutritionTotal.carbs.toFixed(1)}g</div>
                <div className="text-sm text-gray-600">炭水化物</div>
                <Progress value={pfcBalance.carbs_ratio} className="mt-2" />
                <div className="text-xs text-gray-500 mt-1">{pfcBalance.carbs_ratio}%</div>
              </div>
              <div className="text-center">
                <div className="text-xl font-semibold">{nutritionTotal.fat.toFixed(1)}g</div>
                <div className="text-sm text-gray-600">脂質</div>
                <Progress value={pfcBalance.fat_ratio} className="mt-2" />
                <div className="text-xs text-gray-500 mt-1">{pfcBalance.fat_ratio}%</div>
              </div>
            </div>

            {/* Fiber */}
            {nutritionTotal.fiber > 0 && (
              <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
                <span className="text-sm">食物繊維</span>
                <span className="font-semibold">{nutritionTotal.fiber.toFixed(1)}g</span>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Food Items List */}
      {(foodItems.length > 0 || showAddFood) && (
        <Card className="mt-6">
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle>食品リスト</CardTitle>
              <Button onClick={() => setShowAddFood(true)} size="sm">
                <Plus className="w-4 h-4 mr-2" />
                食品を追加
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="list" className="w-full">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="list">リスト表示</TabsTrigger>
                <TabsTrigger value="search">食品検索</TabsTrigger>
                <TabsTrigger value="favorites">お気に入り</TabsTrigger>
              </TabsList>

              <TabsContent value="list" className="space-y-2">
                {foodItems.map((item, index) => (
                  <div key={index} className="p-4 border rounded-lg space-y-3">
                    <div className="grid grid-cols-1 md:grid-cols-6 gap-2 items-end">
                      <div className="md:col-span-2">
                        <Label>食品名</Label>
                        <Input
                          value={item.name}
                          onChange={(e) => handleNutritionChange(index, 'name', e.target.value)}
                        />
                      </div>
                      <div>
                        <Label>量</Label>
                        <Input
                          value={item.quantity}
                          onChange={(e) => handleQuantityChange(index, e.target.value)}
                        />
                      </div>
                      <div>
                        <Label>カロリー</Label>
                        <Input
                          type="number"
                          value={item.calories}
                          onChange={(e) => handleNutritionChange(index, 'calories', e.target.value)}
                        />
                      </div>
                      <div>
                        <Label>タンパク質(g)</Label>
                        <Input
                          type="number"
                          value={item.protein || 0}
                          onChange={(e) => handleNutritionChange(index, 'protein', e.target.value)}
                        />
                      </div>
                      <div className="flex gap-2">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => toggleFavorite(item)}
                        >
                          <Star className={`w-4 h-4 ${favoriteFoods.some(f => f.name === item.name) ? 'fill-yellow-400' : ''}`} />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleRemoveItem(index)}
                        >
                          削除
                        </Button>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                      <div>
                        <Label>炭水化物(g)</Label>
                        <Input
                          type="number"
                          value={item.carbs || 0}
                          onChange={(e) => handleNutritionChange(index, 'carbs', e.target.value)}
                        />
                      </div>
                      <div>
                        <Label>脂質(g)</Label>
                        <Input
                          type="number"
                          value={item.fat || 0}
                          onChange={(e) => handleNutritionChange(index, 'fat', e.target.value)}
                        />
                      </div>
                      <div>
                        <Label>食物繊維(g)</Label>
                        <Input
                          type="number"
                          value={item.fiber || 0}
                          onChange={(e) => handleNutritionChange(index, 'fiber', e.target.value)}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </TabsContent>

              <TabsContent value="search" className="space-y-4">
                <div className="flex gap-2">
                  <Input
                    placeholder="食品名で検索..."
                    value={searchQuery}
                    onChange={(e) => {
                      setSearchQuery(e.target.value)
                      searchFoods(e.target.value)
                    }}
                  />
                  <Button size="icon">
                    <Search className="w-4 h-4" />
                  </Button>
                </div>
                
                <div className="space-y-2">
                  {foodSuggestions.map((food, index) => (
                    <div
                      key={index}
                      className="p-3 border rounded-lg hover:bg-gray-50 cursor-pointer flex justify-between items-center"
                      onClick={() => handleAddItem({
                        name: food.name,
                        quantity: '100g',
                        calories: food.calories_per_100g,
                        protein: food.protein,
                        carbs: food.carbs,
                        fat: food.fat
                      })}
                    >
                      <div>
                        <div className="font-medium">{food.name}</div>
                        <div className="text-sm text-gray-500">
                          100gあたり: {food.calories_per_100g}kcal
                        </div>
                      </div>
                      <Plus className="w-4 h-4 text-gray-400" />
                    </div>
                  ))}
                </div>
              </TabsContent>

              <TabsContent value="favorites" className="space-y-2">
                {favoriteFoods.length === 0 ? (
                  <p className="text-center text-gray-500 py-4">
                    お気に入りの食品がありません
                  </p>
                ) : (
                  favoriteFoods.map((food, index) => (
                    <div
                      key={index}
                      className="p-3 border rounded-lg hover:bg-gray-50 cursor-pointer flex justify-between items-center"
                      onClick={() => handleAddItem(food)}
                    >
                      <div>
                        <div className="font-medium">{food.name}</div>
                        <div className="text-sm text-gray-500">
                          {food.quantity} - {food.calories}kcal
                        </div>
                      </div>
                      <Plus className="w-4 h-4 text-gray-400" />
                    </div>
                  ))
                )}
              </TabsContent>
            </Tabs>

            {/* Save Button */}
            <div className="mt-6 flex justify-end">
              <Button onClick={handleSaveMeal} size="lg" className="w-full md:w-auto">
                <TrendingUp className="w-4 h-4 mr-2" />
                食事を記録（{nutritionTotal.calories}kcal）
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Camera Dialog */}
      <Dialog open={showCamera} onOpenChange={setShowCamera}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle>食事を撮影</DialogTitle>
          </DialogHeader>
          <CameraCapture
            onCapture={handleCameraCapture}
            onClose={() => setShowCamera(false)}
            aspectRatio="4/3"
          />
        </DialogContent>
      </Dialog>
    </div>
  )
}