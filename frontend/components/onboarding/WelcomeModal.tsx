'use client'

import { useState, useEffect } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Slider } from '@/components/ui/slider'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { ChevronRight, ChevronLeft, Dumbbell, Target, Trophy } from 'lucide-react'
import { useAuth } from '@/components/providers/AuthProvider'

interface OnboardingData {
  height: number
  weight: number
  experience: 'beginner' | 'intermediate' | 'advanced'
  goals: string[]
}

export function WelcomeModal() {
  const { user } = useAuth()
  const [isOpen, setIsOpen] = useState(false)
  const [step, setStep] = useState(1)
  const [data, setData] = useState<OnboardingData>({
    height: 170,
    weight: 65,
    experience: 'beginner',
    goals: []
  })

  useEffect(() => {
    // 初回ユーザーかチェック
    const hasCompletedOnboarding = localStorage.getItem('onboarding_completed')
    if (user && !hasCompletedOnboarding) {
      setIsOpen(true)
    }
  }, [user])

  const handleComplete = () => {
    // データを保存
    localStorage.setItem('user_profile', JSON.stringify(data))
    localStorage.setItem('onboarding_completed', 'true')
    setIsOpen(false)
  }

  const goals = [
    { id: 'muscle', label: '筋力向上', icon: '💪' },
    { id: 'weight_loss', label: 'ダイエット', icon: '🏃' },
    { id: 'health', label: '健康維持', icon: '❤️' },
    { id: 'performance', label: '競技力向上', icon: '🏆' },
    { id: 'form', label: 'フォーム改善', icon: '📐' },
    { id: 'endurance', label: '持久力向上', icon: '⏱️' }
  ]

  const toggleGoal = (goalId: string) => {
    setData(prev => ({
      ...prev,
      goals: prev.goals.includes(goalId)
        ? prev.goals.filter(g => g !== goalId)
        : [...prev.goals, goalId]
    }))
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <div className="flex items-center gap-2 mb-2">
            <Dumbbell className="w-6 h-6 text-primary" />
            <DialogTitle className="text-xl">
              BodyScale Pose Analyzerへようこそ！
            </DialogTitle>
          </div>
          <DialogDescription>
            最適な分析のため、いくつか質問させてください（{step}/4）
          </DialogDescription>
        </DialogHeader>

        <div className="py-6">
          {/* Step 1: 身体情報 */}
          {step === 1 && (
            <div className="space-y-6">
              <div>
                <Label htmlFor="height" className="text-base font-medium mb-2 block">
                  身長を教えてください
                </Label>
                <div className="flex items-center gap-4">
                  <Slider
                    id="height"
                    min={140}
                    max={210}
                    step={1}
                    value={[data.height]}
                    onValueChange={([value]) => setData(prev => ({ ...prev, height: value }))}
                    className="flex-1"
                  />
                  <div className="w-20 text-right font-medium">
                    {data.height} cm
                  </div>
                </div>
              </div>

              <div>
                <Label htmlFor="weight" className="text-base font-medium mb-2 block">
                  体重を教えてください
                </Label>
                <div className="flex items-center gap-4">
                  <Slider
                    id="weight"
                    min={40}
                    max={120}
                    step={0.5}
                    value={[data.weight]}
                    onValueChange={([value]) => setData(prev => ({ ...prev, weight: value }))}
                    className="flex-1"
                  />
                  <div className="w-20 text-right font-medium">
                    {data.weight} kg
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Step 2: 経験レベル */}
          {step === 2 && (
            <div className="space-y-4">
              <Label className="text-base font-medium mb-2 block">
                トレーニング経験を教えてください
              </Label>
              <RadioGroup
                value={data.experience}
                onValueChange={(value) => setData(prev => ({ ...prev, experience: value as any }))}
              >
                <div className="space-y-3">
                  <label className="flex items-center space-x-3 p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
                    <RadioGroupItem value="beginner" />
                    <div className="flex-1">
                      <div className="font-medium">初心者</div>
                      <div className="text-sm text-muted-foreground">
                        トレーニング経験1年未満
                      </div>
                    </div>
                  </label>
                  <label className="flex items-center space-x-3 p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
                    <RadioGroupItem value="intermediate" />
                    <div className="flex-1">
                      <div className="font-medium">中級者</div>
                      <div className="text-sm text-muted-foreground">
                        トレーニング経験1〜3年
                      </div>
                    </div>
                  </label>
                  <label className="flex items-center space-x-3 p-4 border rounded-lg cursor-pointer hover:bg-gray-50">
                    <RadioGroupItem value="advanced" />
                    <div className="flex-1">
                      <div className="font-medium">上級者</div>
                      <div className="text-sm text-muted-foreground">
                        トレーニング経験3年以上
                      </div>
                    </div>
                  </label>
                </div>
              </RadioGroup>
            </div>
          )}

          {/* Step 3: 目標 */}
          {step === 3 && (
            <div className="space-y-4">
              <Label className="text-base font-medium mb-2 block">
                目標を選んでください（複数選択可）
              </Label>
              <div className="grid grid-cols-2 gap-3">
                {goals.map(goal => (
                  <button
                    key={goal.id}
                    onClick={() => toggleGoal(goal.id)}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      data.goals.includes(goal.id)
                        ? 'border-primary bg-primary/5'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="text-2xl mb-1">{goal.icon}</div>
                    <div className="text-sm font-medium">{goal.label}</div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Step 4: 完了 */}
          {step === 4 && (
            <div className="text-center space-y-6">
              <Trophy className="w-16 h-16 text-primary mx-auto" />
              <div>
                <h3 className="text-lg font-semibold mb-2">
                  設定が完了しました！
                </h3>
                <p className="text-muted-foreground">
                  あなたに最適化された分析を提供します
                </p>
              </div>
              <div className="bg-gray-50 rounded-lg p-4 text-left space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">身長</span>
                  <span className="font-medium">{data.height} cm</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">体重</span>
                  <span className="font-medium">{data.weight} kg</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">経験</span>
                  <span className="font-medium">
                    {data.experience === 'beginner' ? '初心者' : 
                     data.experience === 'intermediate' ? '中級者' : '上級者'}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="flex justify-between">
          <Button
            variant="outline"
            onClick={() => setStep(prev => Math.max(1, prev - 1))}
            disabled={step === 1}
          >
            <ChevronLeft className="w-4 h-4 mr-1" />
            戻る
          </Button>
          
          {step < 4 ? (
            <Button
              onClick={() => setStep(prev => prev + 1)}
              disabled={step === 3 && data.goals.length === 0}
            >
              次へ
              <ChevronRight className="w-4 h-4 ml-1" />
            </Button>
          ) : (
            <Button onClick={handleComplete}>
              始める
              <ChevronRight className="w-4 h-4 ml-1" />
            </Button>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}