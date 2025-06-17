'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { 
  Calculator,
  AlertTriangle,
  Target,
  Activity,
  Info,
  CheckCircle2
} from 'lucide-react'

interface UserData {
  weight: string
  height: string
  age: string
  gender: 'male' | 'female'
  activityLevel: string
  goal: string
}

interface CalculationResults {
  bmr: number
  tdee: number
  bodyFat: number
  targetCalories: number
  protein: number
  carbs: number
  fat: number
  proteinCal: number
  carbsCal: number
  fatCal: number
  micronutrients: {
    vitaminD: string
    omega3: string
    magnesium: string
    zinc: string
    vitaminB12: string
  }
  supplements: string[]
}

export default function NutritionCalculatorPage() {
  const [userData, setUserData] = useState<UserData>({
    weight: '',
    height: '',
    age: '',
    gender: 'male',
    activityLevel: 'moderate',
    goal: 'maintain'
  })

  const [results, setResults] = useState<CalculationResults | null>(null)
  const [warnings, setWarnings] = useState<string[]>([])

  const activityLevels = [
    { value: 'sedentary', label: '座りがち（運動なし）', multiplier: 1.2 },
    { value: 'light', label: '軽い運動（週1-3回）', multiplier: 1.375 },
    { value: 'moderate', label: '中程度（週3-5回）', multiplier: 1.55 },
    { value: 'active', label: '活発（週6-7回）', multiplier: 1.725 },
    { value: 'veryActive', label: '非常に活発（1日2回）', multiplier: 1.9 }
  ]

  const goals = [
    { value: 'cut', label: '減量（-20%）' },
    { value: 'slowCut', label: 'ゆっくり減量（-10%）' },
    { value: 'maintain', label: '維持' },
    { value: 'slowBulk', label: 'ゆっくり増量（+10%）' },
    { value: 'bulk', label: '増量（+20%）' }
  ]

  const calculate = () => {
    const weight = parseFloat(userData.weight)
    const height = parseFloat(userData.height)
    const age = parseFloat(userData.age)

    if (!weight || !height || !age) return

    // BMR計算（Mifflin-St Jeor式）
    let bmr: number
    if (userData.gender === 'male') {
      bmr = 10 * weight + 6.25 * height - 5 * age + 5
    } else {
      bmr = 10 * weight + 6.25 * height - 5 * age - 161
    }

    // TDEE計算
    const activityMultiplier = activityLevels.find(
      level => level.value === userData.activityLevel
    )?.multiplier || 1.55
    const tdee = bmr * activityMultiplier

    // 目標カロリー計算
    let targetCalories = tdee
    switch (userData.goal) {
      case 'cut':
        targetCalories = tdee * 0.8
        break
      case 'slowCut':
        targetCalories = tdee * 0.9
        break
      case 'slowBulk':
        targetCalories = tdee * 1.1
        break
      case 'bulk':
        targetCalories = tdee * 1.2
        break
    }

    // 体脂肪率推定（簡易版）
    const bmi = weight / ((height / 100) ** 2)
    let bodyFat: number
    if (userData.gender === 'male') {
      bodyFat = 1.20 * bmi + 0.23 * age - 16.2
    } else {
      bodyFat = 1.20 * bmi + 0.23 * age - 5.4
    }

    // PFCバランス計算
    const proteinPerKg = userData.goal.includes('bulk') ? 2.2 : 2.0
    const protein = weight * proteinPerKg
    const proteinCal = protein * 4

    const fatPercentage = 0.25
    const fatCal = targetCalories * fatPercentage
    const fat = fatCal / 9

    const carbsCal = targetCalories - proteinCal - fatCal
    const carbs = carbsCal / 4

    // 微量栄養素推奨値
    const micronutrients = {
      vitaminD: '2000-4000 IU',
      omega3: '2-3g',
      magnesium: userData.gender === 'male' ? '400mg' : '310mg',
      zinc: userData.gender === 'male' ? '11mg' : '8mg',
      vitaminB12: '2.4μg'
    }

    // サプリメント推奨
    const supplements = ['マルチビタミン', 'ビタミンD3']
    if (userData.goal.includes('bulk')) {
      supplements.push('クレアチン')
    }
    if (protein > 150) {
      supplements.push('消化酵素')
    }

    // 安全性チェック
    const newWarnings: string[] = []
    if (targetCalories < 1200) {
      newWarnings.push('目標カロリーが低すぎます。健康に悪影響を及ぼす可能性があります。')
    }
    if (bodyFat < 10 && userData.gender === 'male') {
      newWarnings.push('体脂肪率が低すぎる可能性があります。')
    }
    if (bodyFat < 18 && userData.gender === 'female') {
      newWarnings.push('体脂肪率が低すぎる可能性があります。女性の健康に影響する場合があります。')
    }
    if (bmi < 18.5) {
      newWarnings.push('BMIが低体重の範囲です。')
    }
    if (bmi > 30) {
      newWarnings.push('BMIが肥満の範囲です。医師への相談を推奨します。')
    }

    setWarnings(newWarnings)
    setResults({
      bmr: Math.round(bmr),
      tdee: Math.round(tdee),
      bodyFat: Math.round(bodyFat * 10) / 10,
      targetCalories: Math.round(targetCalories),
      protein: Math.round(protein),
      carbs: Math.round(carbs),
      fat: Math.round(fat),
      proteinCal: Math.round(proteinCal),
      carbsCal: Math.round(carbsCal),
      fatCal: Math.round(fatCal),
      micronutrients,
      supplements
    })
  }

  return (
    <div className="container mx-auto px-4 py-8 pb-24 md:pb-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">栄養計算</h1>
        <p className="text-muted-foreground">科学的根拠に基づいた栄養計算とアドバイス</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* 左側：入力フォーム */}
        <div>
          <Card>
            <CardHeader>
              <CardTitle>基本情報入力</CardTitle>
              <CardDescription>
                正確な計算のため、すべての項目を入力してください
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <Label htmlFor="weight">体重 (kg)</Label>
                  <Input
                    id="weight"
                    type="number"
                    value={userData.weight}
                    onChange={(e) => setUserData({...userData, weight: e.target.value})}
                    placeholder="70"
                  />
                </div>
                <div>
                  <Label htmlFor="height">身長 (cm)</Label>
                  <Input
                    id="height"
                    type="number"
                    value={userData.height}
                    onChange={(e) => setUserData({...userData, height: e.target.value})}
                    placeholder="170"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="age">年齢</Label>
                <Input
                  id="age"
                  type="number"
                  value={userData.age}
                  onChange={(e) => setUserData({...userData, age: e.target.value})}
                  placeholder="25"
                />
              </div>

              <div>
                <Label>性別</Label>
                <RadioGroup
                  value={userData.gender}
                  onValueChange={(value) => setUserData({...userData, gender: value as 'male' | 'female'})}
                >
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="male" id="male" />
                    <Label htmlFor="male">男性</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="female" id="female" />
                    <Label htmlFor="female">女性</Label>
                  </div>
                </RadioGroup>
              </div>

              <div>
                <Label htmlFor="activity">活動レベル</Label>
                <Select
                  value={userData.activityLevel}
                  onValueChange={(value) => setUserData({...userData, activityLevel: value})}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {activityLevels.map((level) => (
                      <SelectItem key={level.value} value={level.value}>
                        {level.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="goal">目標</Label>
                <Select
                  value={userData.goal}
                  onValueChange={(value) => setUserData({...userData, goal: value})}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {goals.map((goal) => (
                      <SelectItem key={goal.value} value={goal.value}>
                        {goal.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <Button onClick={calculate} className="w-full">
                <Calculator className="w-4 h-4 mr-2" />
                計算する
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* 右側：計算結果 */}
        <div className="space-y-4">
          {results && (
            <>
              {/* 基本指標 */}
              <Card>
                <CardHeader>
                  <CardTitle>基本指標</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-muted-foreground">基礎代謝率 (BMR)</p>
                      <p className="text-2xl font-bold">{results.bmr} kcal</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">総消費カロリー (TDEE)</p>
                      <p className="text-2xl font-bold">{results.tdee} kcal</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">推定体脂肪率</p>
                      <p className="text-2xl font-bold">{results.bodyFat}%</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">目標カロリー</p>
                      <p className="text-2xl font-bold text-primary">{results.targetCalories} kcal</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* PFCバランス */}
              <Card>
                <CardHeader>
                  <CardTitle>PFCバランス</CardTitle>
                  <CardDescription>推奨される三大栄養素の配分</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <div>
                        <p className="font-medium">タンパク質</p>
                        <p className="text-sm text-muted-foreground">{results.proteinCal} kcal</p>
                      </div>
                      <p className="text-xl font-bold">{results.protein}g</p>
                    </div>
                    <div className="flex justify-between items-center">
                      <div>
                        <p className="font-medium">炭水化物</p>
                        <p className="text-sm text-muted-foreground">{results.carbsCal} kcal</p>
                      </div>
                      <p className="text-xl font-bold">{results.carbs}g</p>
                    </div>
                    <div className="flex justify-between items-center">
                      <div>
                        <p className="font-medium">脂質</p>
                        <p className="text-sm text-muted-foreground">{results.fatCal} kcal</p>
                      </div>
                      <p className="text-xl font-bold">{results.fat}g</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* 微量栄養素 */}
              <Card>
                <CardHeader>
                  <CardTitle>微量栄養素推奨値</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div className="flex justify-between">
                      <span>ビタミンD:</span>
                      <span className="font-medium">{results.micronutrients.vitaminD}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>オメガ3:</span>
                      <span className="font-medium">{results.micronutrients.omega3}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>マグネシウム:</span>
                      <span className="font-medium">{results.micronutrients.magnesium}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>亜鉛:</span>
                      <span className="font-medium">{results.micronutrients.zinc}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* サプリメント推奨 */}
              <Card>
                <CardHeader>
                  <CardTitle>推奨サプリメント</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {results.supplements.map((supplement, index) => (
                      <div
                        key={index}
                        className="flex items-center gap-1 px-3 py-1 bg-primary/10 rounded-full text-sm"
                      >
                        <CheckCircle2 className="w-4 h-4 text-primary" />
                        {supplement}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </>
          )}

          {/* 警告 */}
          {warnings.length > 0 && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertTitle>注意事項</AlertTitle>
              <AlertDescription>
                <ul className="list-disc list-inside space-y-1">
                  {warnings.map((warning, index) => (
                    <li key={index}>{warning}</li>
                  ))}
                </ul>
              </AlertDescription>
            </Alert>
          )}
        </div>
      </div>
    </div>
  )
}