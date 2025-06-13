'use client';

import React, { useState } from 'react';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Label } from '../ui/label';
import { Input } from '../ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { RadioGroup, RadioGroupItem } from '../ui/radio-group';
import { Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';

interface ProfileFormData {
  gender: 'male' | 'female' | '';
  age: string;
  height: string;
  weight: string;
  activityLevel: 'sedentary' | 'light' | 'moderate' | 'active' | 'veryActive' | '';
  goal: 'cutting' | 'maintenance' | 'bulking' | '';
  experience: 'beginner' | 'intermediate' | 'advanced';
  trainingDaysPerWeek: string;
  targetBodyFat?: string;
}

interface ProfileFormProps {
  onSubmit: (results: any) => void;
}

export default function ProfileForm({ onSubmit }: ProfileFormProps) {
  const [formData, setFormData] = useState<ProfileFormData>({
    gender: '',
    age: '',
    height: '',
    weight: '',
    activityLevel: '',
    goal: '',
    experience: 'beginner',
    trainingDaysPerWeek: '3',
    targetBodyFat: ''
  });

  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.gender) newErrors.gender = '性別を選択してください';
    
    const age = parseInt(formData.age);
    if (!formData.age || age < 15 || age > 100) {
      newErrors.age = '年齢は15-100歳の範囲で入力してください';
    }

    const height = parseFloat(formData.height);
    if (!formData.height || height < 100 || height > 250) {
      newErrors.height = '身長は100-250cmの範囲で入力してください';
    }

    const weight = parseFloat(formData.weight);
    if (!formData.weight || weight < 30 || weight > 300) {
      newErrors.weight = '体重は30-300kgの範囲で入力してください';
    }

    if (!formData.activityLevel) newErrors.activityLevel = '活動レベルを選択してください';
    if (!formData.goal) newErrors.goal = '目標を選択してください';

    const trainingDays = parseInt(formData.trainingDaysPerWeek);
    if (trainingDays < 0 || trainingDays > 7) {
      newErrors.trainingDaysPerWeek = 'トレーニング日数は0-7日の範囲で入力してください';
    }

    if (formData.targetBodyFat) {
      const targetBF = parseFloat(formData.targetBodyFat);
      if (targetBF < 3 || targetBF > 50) {
        newErrors.targetBodyFat = '目標体脂肪率は3-50%の範囲で入力してください';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      toast.error('入力内容を確認してください');
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch('/api/v3/comprehensive-analysis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          age: parseInt(formData.age),
          height: parseFloat(formData.height),
          weight: parseFloat(formData.weight),
          trainingDaysPerWeek: parseInt(formData.trainingDaysPerWeek),
          targetBodyFat: formData.targetBodyFat ? parseFloat(formData.targetBodyFat) : undefined
        })
      });
      
      if (!response.ok) {
        throw new Error('分析に失敗しました');
      }

      const results = await response.json();
      toast.success('分析が完了しました');
      onSubmit(results);
    } catch (error) {
      console.error('Analysis failed:', error);
      toast.error('分析中にエラーが発生しました');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>プロフィール設定</CardTitle>
        <CardDescription>
          あなたの情報を入力して、包括的な分析を開始しましょう
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* 基本情報 */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">基本情報</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="gender">性別 *</Label>
                <RadioGroup
                  value={formData.gender}
                  onValueChange={(value) => setFormData({...formData, gender: value as 'male' | 'female'})}
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
                {errors.gender && <p className="text-sm text-red-500">{errors.gender}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="age">年齢 *</Label>
                <Input
                  id="age"
                  type="number"
                  value={formData.age}
                  onChange={(e) => setFormData({...formData, age: e.target.value})}
                  placeholder="歳"
                />
                {errors.age && <p className="text-sm text-red-500">{errors.age}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="height">身長 *</Label>
                <Input
                  id="height"
                  type="number"
                  step="0.1"
                  value={formData.height}
                  onChange={(e) => setFormData({...formData, height: e.target.value})}
                  placeholder="cm"
                />
                {errors.height && <p className="text-sm text-red-500">{errors.height}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="weight">体重 *</Label>
                <Input
                  id="weight"
                  type="number"
                  step="0.1"
                  value={formData.weight}
                  onChange={(e) => setFormData({...formData, weight: e.target.value})}
                  placeholder="kg"
                />
                {errors.weight && <p className="text-sm text-red-500">{errors.weight}</p>}
              </div>
            </div>
          </div>

          {/* 活動・目標設定 */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">活動・目標設定</h3>

            <div className="space-y-2">
              <Label htmlFor="activityLevel">活動レベル *</Label>
              <Select
                value={formData.activityLevel}
                onValueChange={(value) => setFormData({...formData, activityLevel: value as any})}
              >
                <SelectTrigger id="activityLevel">
                  <SelectValue placeholder="活動レベルを選択" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="sedentary">座りがち (デスクワーク中心、運動なし)</SelectItem>
                  <SelectItem value="light">軽い活動 (週1-3日の軽い運動)</SelectItem>
                  <SelectItem value="moderate">中程度の活動 (週3-5日の運動)</SelectItem>
                  <SelectItem value="active">活発な活動 (週6-7日の運動)</SelectItem>
                  <SelectItem value="veryActive">非常に活発 (激しい運動や肉体労働)</SelectItem>
                </SelectContent>
              </Select>
              {errors.activityLevel && <p className="text-sm text-red-500">{errors.activityLevel}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="goal">目標 *</Label>
              <Select
                value={formData.goal}
                onValueChange={(value) => setFormData({...formData, goal: value as any})}
              >
                <SelectTrigger id="goal">
                  <SelectValue placeholder="目標を選択" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="cutting">体脂肪減少 (減量)</SelectItem>
                  <SelectItem value="maintenance">現状維持</SelectItem>
                  <SelectItem value="bulking">筋肉増加 (増量)</SelectItem>
                </SelectContent>
              </Select>
              {errors.goal && <p className="text-sm text-red-500">{errors.goal}</p>}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="experience">トレーニング経験</Label>
                <Select
                  value={formData.experience}
                  onValueChange={(value) => setFormData({...formData, experience: value as any})}
                >
                  <SelectTrigger id="experience">
                    <SelectValue placeholder="経験レベル" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="beginner">初心者 (1年未満)</SelectItem>
                    <SelectItem value="intermediate">中級者 (1-3年)</SelectItem>
                    <SelectItem value="advanced">上級者 (3年以上)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="trainingDays">週のトレーニング日数</Label>
                <Input
                  id="trainingDays"
                  type="number"
                  min="0"
                  max="7"
                  value={formData.trainingDaysPerWeek}
                  onChange={(e) => setFormData({...formData, trainingDaysPerWeek: e.target.value})}
                  placeholder="日"
                />
                {errors.trainingDaysPerWeek && <p className="text-sm text-red-500">{errors.trainingDaysPerWeek}</p>}
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="targetBodyFat">目標体脂肪率（オプション）</Label>
              <Input
                id="targetBodyFat"
                type="number"
                step="0.1"
                value={formData.targetBodyFat}
                onChange={(e) => setFormData({...formData, targetBodyFat: e.target.value})}
                placeholder="%"
              />
              {errors.targetBodyFat && <p className="text-sm text-red-500">{errors.targetBodyFat}</p>}
              <p className="text-xs text-gray-500">
                設定しない場合は、目標に応じた推奨値が使用されます
              </p>
            </div>
          </div>

          <Button
            type="submit"
            className="w-full"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                分析中...
              </>
            ) : (
              '包括的分析を実行'
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}