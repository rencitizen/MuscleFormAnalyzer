'use client'

import { useState, useEffect } from 'react'
import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { ScientificProfileForm, type ScientificUserProfile } from '@/components/profile/ScientificProfileForm'
import { ScientificMetrics } from '@/components/dashboard/ScientificMetrics'
import { HealthWarnings } from '@/components/safety/HealthWarnings'
import { useV3Api } from '@/services/v3Api'
import { Calculator, ChartBar, AlertCircle, ArrowLeft, RefreshCw } from 'lucide-react'
import { useAnalytics } from '@/hooks/useAnalytics'

export default function ScientificDashboardPage() {
  const { data: session } = useSession()
  const router = useRouter()
  const { track } = useAnalytics()
  const v3Api = useV3Api()
  
  const [activeTab, setActiveTab] = useState('profile')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // 計算結果の状態
  const [bmrResult, setBmrResult] = useState<any>(null)
  const [tdeeResult, setTdeeResult] = useState<any>(null)
  const [bodyFatResult, setBodyFatResult] = useState<any>(null)
  const [targetCaloriesResult, setTargetCaloriesResult] = useState<any>(null)
  const [pfcBalanceResult, setPfcBalanceResult] = useState<any>(null)
  const [calorieSafetyResult, setCalorieSafetyResult] = useState<any>(null)
  const [warnings, setWarnings] = useState<any[]>([])
  
  // プロフィールデータ
  const [profileData, setProfileData] = useState<ScientificUserProfile | null>(null)

  useEffect(() => {
    // ローカルストレージから保存されたプロフィールを読み込み
    const savedProfile = v3Api.getSavedProfile()
    if (savedProfile) {
      const scientificProfile: ScientificUserProfile = {
        weight: savedProfile.weight,
        height: savedProfile.height,
        age: savedProfile.age,
        gender: savedProfile.gender,
        activityLevel: savedProfile.activity_level as any,
        goal: savedProfile.goal === 'cutting' ? 'fat_loss' : 
              savedProfile.goal === 'bulking' ? 'muscle_gain' : 'maintenance',
        experienceLevel: savedProfile.experience || 'intermediate'
      }
      setProfileData(scientificProfile)
    }
  }, [])

  const handleProfileSave = async (profile: ScientificUserProfile) => {
    setIsLoading(true)
    setError(null)
    setProfileData(profile)
    
    try {
      track('scientific_calculation_started', { goal: profile.goal })
      
      // BMR計算
      const bmr = await v3Api.calculateBMR({
        weight: profile.weight,
        height: profile.height,
        age: profile.age,
        gender: profile.gender
      })
      setBmrResult(bmr)
      
      // TDEE計算
      const tdee = await v3Api.calculateTDEE({
        weight: profile.weight,
        height: profile.height,
        age: profile.age,
        gender: profile.gender,
        activity_level: profile.activityLevel
      })
      setTdeeResult(tdee)
      
      // 体脂肪率推定（オプション）
      const bodyFat = await v3Api.estimateBodyFat({
        gender: profile.gender,
        weight: profile.weight,
        height: profile.height
      })
      setBodyFatResult(bodyFat)
      
      // 目標カロリー計算
      const targetCalories = await v3Api.getTargetCalories({
        tdee: tdee.tdee,
        goal: profile.goal === 'fat_loss' ? 'cutting' : 
              profile.goal === 'muscle_gain' ? 'bulking' : 'maintenance',
        experience_level: profile.experienceLevel
      })
      setTargetCaloriesResult(targetCalories)
      
      // PFCバランス計算
      const pfcBalance = await v3Api.getPFCBalance({
        daily_calories: targetCalories.daily_calories,
        goal: profile.goal === 'fat_loss' ? 'cutting' : 
              profile.goal === 'muscle_gain' ? 'bulking' : 'maintenance',
        weight: profile.weight,
        experience_level: profile.experienceLevel
      })
      setPfcBalanceResult(pfcBalance)
      
      // カロリー安全性チェック
      const safety = await v3Api.checkCalorieSafety({
        daily_calories: targetCalories.daily_calories,
        bmr: bmr.bmr,
        gender: profile.gender,
        age: profile.age,
        goal: profile.goal === 'fat_loss' ? 'cutting' : 
              profile.goal === 'muscle_gain' ? 'bulking' : 'maintenance'
      })
      setCalorieSafetyResult(safety)
      
      // 警告の生成
      const generatedWarnings = []
      if (!safety.is_safe) {
        generatedWarnings.push({
          id: 'calorie-safety',
          severity: 'high',
          category: 'calorie',
          title: 'カロリー設定の安全性',
          description: safety.warnings.join(' '),
          recommendation: safety.recommendation,
          metrics: {
            current: targetCalories.daily_calories,
            safe_min: safety.minimum_safe_calories,
            unit: 'kcal'
          }
        })
      }
      
      setWarnings(generatedWarnings)
      setActiveTab('results')
      
      track('scientific_calculation_completed', {
        goal: profile.goal,
        bmr: bmr.bmr,
        tdee: tdee.tdee,
        targetCalories: targetCalories.daily_calories
      })
      
    } catch (err) {
      console.error('計算エラー:', err)
      setError('計算中にエラーが発生しました。もう一度お試しください。')
      track('scientific_calculation_error', { error: err })
    } finally {
      setIsLoading(false)
    }
  }

  const handleRecalculate = () => {
    setActiveTab('profile')
    track('scientific_calculation_recalculate')
  }

  const handleWarningDismiss = (warningId: string) => {
    setWarnings(prev => prev.filter(w => w.id !== warningId))
    track('warning_dismissed', { warningId })
  }

  const handleAcceptRecommendation = (warningId: string) => {
    track('recommendation_accepted', { warningId })
    // 推奨事項を適用する処理をここに実装
  }

  return (
    <div className="container mx-auto px-4 py-8 pb-24 md:pb-8">
      <div className="mb-6">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push('/dashboard')}
          className="mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          ダッシュボードに戻る
        </Button>
        
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">科学的フィットネス計算</h1>
            <p className="text-muted-foreground">
              あなたの身体データに基づいた詳細な分析と推奨値
            </p>
          </div>
          {profileData && activeTab === 'results' && (
            <Button onClick={handleRecalculate} variant="outline">
              <RefreshCw className="h-4 w-4 mr-2" />
              再計算
            </Button>
          )}
        </div>
      </div>

      {error && (
        <Alert variant="destructive" className="mb-4">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="profile">
            <Calculator className="h-4 w-4 mr-2" />
            プロフィール設定
          </TabsTrigger>
          <TabsTrigger value="results" disabled={!bmrResult}>
            <ChartBar className="h-4 w-4 mr-2" />
            計算結果
          </TabsTrigger>
          <TabsTrigger value="warnings" disabled={warnings.length === 0}>
            <AlertCircle className="h-4 w-4 mr-2" />
            健康警告 {warnings.length > 0 && `(${warnings.length})`}
          </TabsTrigger>
        </TabsList>

        <TabsContent value="profile" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>身体情報と目標設定</CardTitle>
              <CardDescription>
                正確な計算のために、詳細な情報を入力してください
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ScientificProfileForm
                initialData={profileData || undefined}
                onSave={handleProfileSave}
                isLoading={isLoading}
              />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="results" className="mt-6">
          <ScientificMetrics
            bmr={bmrResult}
            tdee={tdeeResult}
            bodyFat={bodyFatResult}
            targetCalories={targetCaloriesResult}
            pfcBalance={pfcBalanceResult}
            calorieSafety={calorieSafetyResult}
            isLoading={isLoading}
          />
        </TabsContent>

        <TabsContent value="warnings" className="mt-6">
          <HealthWarnings
            warnings={warnings}
            onDismiss={handleWarningDismiss}
            onAcceptRecommendation={handleAcceptRecommendation}
          />
        </TabsContent>
      </Tabs>
    </div>
  )
}