'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Calculator, Activity, Target, AlertCircle } from 'lucide-react'

export interface ScientificUserProfile {
  weight: number // kg
  height: number // cm
  age: number
  gender: 'male' | 'female'
  activityLevel: 'sedentary' | 'light' | 'moderate' | 'active' | 'very_active'
  goal: 'muscle_gain' | 'fat_loss' | 'maintenance'
  experienceLevel: 'beginner' | 'intermediate' | 'advanced'
}

interface ScientificProfileFormProps {
  initialData?: Partial<ScientificUserProfile>
  onSave: (data: ScientificUserProfile) => void
  isLoading?: boolean
}

export function ScientificProfileForm({ initialData, onSave, isLoading }: ScientificProfileFormProps) {
  const [profile, setProfile] = useState<ScientificUserProfile>({
    weight: initialData?.weight || 70,
    height: initialData?.height || 170,
    age: initialData?.age || 30,
    gender: initialData?.gender || 'male',
    activityLevel: initialData?.activityLevel || 'moderate',
    goal: initialData?.goal || 'maintenance',
    experienceLevel: initialData?.experienceLevel || 'intermediate'
  })

  const activityLevelOptions = [
    { value: 'sedentary', label: '座りがち', description: 'ほとんど運動しない' },
    { value: 'light', label: '軽い活動', description: '週1-2回の軽い運動' },
    { value: 'moderate', label: '中程度', description: '週3-5回の運動' },
    { value: 'active', label: '活発', description: '週6-7回の運動' },
    { value: 'very_active', label: '非常に活発', description: '激しい運動を毎日' }
  ]

  const goalOptions = [
    { value: 'muscle_gain', label: '筋肉増量', description: 'マッスルビルディング' },
    { value: 'fat_loss', label: '減量', description: '体脂肪を減らす' },
    { value: 'maintenance', label: '現状維持', description: '体重・体型を維持' }
  ]

  const experienceLevelOptions = [
    { value: 'beginner', label: '初心者', description: 'トレーニング歴1年未満' },
    { value: 'intermediate', label: '中級者', description: 'トレーニング歴1-3年' },
    { value: 'advanced', label: '上級者', description: 'トレーニング歴3年以上' }
  ]

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSave(profile)
  }

  const validateProfile = () => {
    if (profile.weight < 30 || profile.weight > 300) return false
    if (profile.height < 100 || profile.height > 250) return false
    if (profile.age < 15 || profile.age > 100) return false
    return true
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calculator className="w-5 h-5" />
            身体情報
          </CardTitle>
          <CardDescription>
            正確な計算のために、あなたの身体情報を入力してください
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <Label htmlFor="weight">体重 (kg)</Label>
              <Input
                id="weight"
                type="number"
                step="0.1"
                min="30"
                max="300"
                value={profile.weight}
                onChange={(e) => setProfile({...profile, weight: parseFloat(e.target.value) || 0})}
                required
              />
              <p className="text-xs text-muted-foreground mt-1">30-300kgの範囲で入力</p>
            </div>
            <div>
              <Label htmlFor="height">身長 (cm)</Label>
              <Input
                id="height"
                type="number"
                step="0.1"
                min="100"
                max="250"
                value={profile.height}
                onChange={(e) => setProfile({...profile, height: parseFloat(e.target.value) || 0})}
                required
              />
              <p className="text-xs text-muted-foreground mt-1">100-250cmの範囲で入力</p>
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <Label htmlFor="age">年齢</Label>
              <Input
                id="age"
                type="number"
                min="15"
                max="100"
                value={profile.age}
                onChange={(e) => setProfile({...profile, age: parseInt(e.target.value) || 0})}
                required
              />
              <p className="text-xs text-muted-foreground mt-1">15-100歳の範囲で入力</p>
            </div>
            <div>
              <Label>性別</Label>
              <RadioGroup
                value={profile.gender}
                onValueChange={(value) => setProfile({...profile, gender: value as 'male' | 'female'})}
              >
                <div className="flex space-x-4 mt-2">
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="male" id="male" />
                    <Label htmlFor="male">男性</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="female" id="female" />
                    <Label htmlFor="female">女性</Label>
                  </div>
                </div>
              </RadioGroup>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="w-5 h-5" />
            活動レベル
          </CardTitle>
          <CardDescription>
            日常の活動量を選択してください
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Select
            value={profile.activityLevel}
            onValueChange={(value) => setProfile({...profile, activityLevel: value as ScientificUserProfile['activityLevel']})}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {activityLevelOptions.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  <div>
                    <div className="font-medium">{option.label}</div>
                    <div className="text-xs text-muted-foreground">{option.description}</div>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="w-5 h-5" />
            目標設定
          </CardTitle>
          <CardDescription>
            あなたのフィットネス目標を選択してください
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label>目標</Label>
            <Select
              value={profile.goal}
              onValueChange={(value) => setProfile({...profile, goal: value as ScientificUserProfile['goal']})}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {goalOptions.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    <div>
                      <div className="font-medium">{option.label}</div>
                      <div className="text-xs text-muted-foreground">{option.description}</div>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label>経験レベル</Label>
            <Select
              value={profile.experienceLevel}
              onValueChange={(value) => setProfile({...profile, experienceLevel: value as ScientificUserProfile['experienceLevel']})}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {experienceLevelOptions.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    <div>
                      <div className="font-medium">{option.label}</div>
                      <div className="text-xs text-muted-foreground">{option.description}</div>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {!validateProfile() && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            入力値を確認してください。有効な範囲内で入力する必要があります。
          </AlertDescription>
        </Alert>
      )}

      <Button 
        type="submit" 
        className="w-full" 
        disabled={!validateProfile() || isLoading}
      >
        {isLoading ? '計算中...' : 'プロフィールを保存して計算を開始'}
      </Button>
    </form>
  )
}