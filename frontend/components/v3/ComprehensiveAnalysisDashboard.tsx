'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Button } from '../ui/button'
import { Alert, AlertDescription } from '../ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs'
import { Progress } from '../ui/progress'
import { Badge } from '../ui/badge'
import { 
  Activity, 
  AlertCircle, 
  BarChart3, 
  Brain, 
  CheckCircle, 
  Dumbbell, 
  Heart, 
  Pizza, 
  TrendingUp,
  Warning,
  Zap
} from 'lucide-react'
import { useAuth } from '@/components/providers/AuthProvider'
import { useToast } from '@/hooks/use-toast'

interface AnalysisData {
  body_composition: {
    bmi: number
    bmi_category: string
    estimated_body_fat: number
    lean_body_mass: any
    ffmi: any
    ideal_weight_range: any
    health_warnings: any[]
  }
  metabolism: {
    bmr_calculations: any
    tdee: any
    calorie_goals: any
    metabolic_type: string
  }
  nutrition: {
    daily_macros: any
    protein_requirements: any
    meal_plan: any
    workout_nutrition: any
    high_protein_foods: any
    hydration: any
  }
  training: {
    workout_plan: any
    exercise_calories: any
    recovery_needs: any
    form_analysis_integration: any
  }
  safety_analysis: {
    overall_safety: string
    risk_score: number
    warnings: any[]
    recommendations: any[]
    monitoring_plan: any
    emergency_signs: any
  }
  ai_integration: {
    pose_analysis_ready: boolean
    meal_photo_analysis: boolean
    exercise_phase_detection: boolean
    progress_tracking: boolean
    ai_recommendations: any[]
  }
  next_steps: any
}

export function ComprehensiveAnalysisDashboard() {
  const { user } = useAuth()
  const { toast } = useToast()
  const [loading, setLoading] = useState(false)
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null)
  const [activeTab, setActiveTab] = useState('overview')
  const [userProfile, setUserProfile] = useState({
    weight: 70,
    height: 170,
    age: 30,
    gender: 'male',
    activity_level: 'moderate',
    goal: 'maintenance',
    experience: 'intermediate',
    available_days: 4,
    equipment: 'full_gym'
  })

  const performAnalysis = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/v3/comprehensive_analysis', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userProfile),
      })

      if (!response.ok) {
        throw new Error('分析に失敗しました')
      }

      const data = await response.json()
      setAnalysisData(data)
      toast({
        title: '分析完了',
        description: '包括的なフィットネス分析が完了しました',
      })
    } catch (error) {
      toast({
        title: 'エラー',
        description: error.message,
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case 'high_risk':
        return 'text-red-600'
      case 'moderate_risk':
        return 'text-yellow-600'
      case 'low_risk':
        return 'text-blue-600'
      default:
        return 'text-green-600'
    }
  }

  const getWarningIcon = (level: string) => {
    switch (level) {
      case 'critical':
        return <AlertCircle className="w-5 h-5 text-red-600" />
      case 'danger':
        return <Warning className="w-5 h-5 text-orange-600" />
      case 'warning':
        return <AlertCircle className="w-5 h-5 text-yellow-600" />
      default:
        return <CheckCircle className="w-5 h-5 text-green-600" />
    }
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">TENAX FIT v3.0 - 包括的分析</h1>
          <p className="text-muted-foreground">
            科学的根拠に基づいたパーソナライズされたフィットネスプラン
          </p>
        </div>
        <Button 
          onClick={performAnalysis} 
          disabled={loading}
          size="lg"
        >
          {loading ? (
            <>
              <Activity className="mr-2 h-4 w-4 animate-spin" />
              分析中...
            </>
          ) : (
            <>
              <Brain className="mr-2 h-4 w-4" />
              包括的分析を開始
            </>
          )}
        </Button>
      </div>

      {/* ユーザープロファイル入力 */}
      {!analysisData && (
        <Card>
          <CardHeader>
            <CardTitle>プロファイル情報</CardTitle>
            <CardDescription>
              正確な分析のために基本情報を入力してください
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div>
                <label className="text-sm font-medium">体重 (kg)</label>
                <input
                  type="number"
                  className="w-full mt-1 p-2 border rounded"
                  value={userProfile.weight}
                  onChange={(e) => setUserProfile({
                    ...userProfile,
                    weight: parseFloat(e.target.value)
                  })}
                />
              </div>
              <div>
                <label className="text-sm font-medium">身長 (cm)</label>
                <input
                  type="number"
                  className="w-full mt-1 p-2 border rounded"
                  value={userProfile.height}
                  onChange={(e) => setUserProfile({
                    ...userProfile,
                    height: parseFloat(e.target.value)
                  })}
                />
              </div>
              <div>
                <label className="text-sm font-medium">年齢</label>
                <input
                  type="number"
                  className="w-full mt-1 p-2 border rounded"
                  value={userProfile.age}
                  onChange={(e) => setUserProfile({
                    ...userProfile,
                    age: parseInt(e.target.value)
                  })}
                />
              </div>
              <div>
                <label className="text-sm font-medium">性別</label>
                <select
                  className="w-full mt-1 p-2 border rounded"
                  value={userProfile.gender}
                  onChange={(e) => setUserProfile({
                    ...userProfile,
                    gender: e.target.value
                  })}
                >
                  <option value="male">男性</option>
                  <option value="female">女性</option>
                </select>
              </div>
              <div>
                <label className="text-sm font-medium">活動レベル</label>
                <select
                  className="w-full mt-1 p-2 border rounded"
                  value={userProfile.activity_level}
                  onChange={(e) => setUserProfile({
                    ...userProfile,
                    activity_level: e.target.value
                  })}
                >
                  <option value="sedentary">座りがち</option>
                  <option value="light">軽い活動</option>
                  <option value="moderate">中程度</option>
                  <option value="active">活発</option>
                  <option value="very_active">非常に活発</option>
                </select>
              </div>
              <div>
                <label className="text-sm font-medium">目標</label>
                <select
                  className="w-full mt-1 p-2 border rounded"
                  value={userProfile.goal}
                  onChange={(e) => setUserProfile({
                    ...userProfile,
                    goal: e.target.value
                  })}
                >
                  <option value="cutting">減量</option>
                  <option value="maintenance">維持</option>
                  <option value="bulking">増量</option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 分析結果 */}
      {analysisData && (
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="overview">概要</TabsTrigger>
            <TabsTrigger value="body">身体組成</TabsTrigger>
            <TabsTrigger value="nutrition">栄養</TabsTrigger>
            <TabsTrigger value="training">トレーニング</TabsTrigger>
            <TabsTrigger value="safety">安全性</TabsTrigger>
          </TabsList>

          {/* 概要タブ */}
          <TabsContent value="overview" className="space-y-4">
            {/* 安全性サマリー */}
            {analysisData.safety_analysis.warnings.length > 0 && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  {analysisData.safety_analysis.warnings.length}件の健康上の懸念事項があります。
                  安全性タブで詳細を確認してください。
                </AlertDescription>
              </Alert>
            )}

            {/* メトリクスグリッド */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">BMI</CardTitle>
                  <Heart className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {analysisData.body_composition.bmi}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {analysisData.body_composition.bmi_category}
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">体脂肪率</CardTitle>
                  <Activity className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {analysisData.body_composition.estimated_body_fat}%
                  </div>
                  <p className="text-xs text-muted-foreground">
                    推定値
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">目標カロリー</CardTitle>
                  <Pizza className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {analysisData.metabolism.calorie_goals.target_calories}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    kcal/日
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">週間トレーニング</CardTitle>
                  <Dumbbell className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {analysisData.training.workout_plan.frequency}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {analysisData.training.workout_plan.duration}
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* AI統合機能 */}
            <Card>
              <CardHeader>
                <CardTitle>AI統合機能</CardTitle>
                <CardDescription>
                  既存のTENAX FIT AI機能との連携状態
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="flex items-center space-x-4">
                    <CheckCircle className="h-5 w-5 text-green-600" />
                    <div>
                      <p className="text-sm font-medium">姿勢分析</p>
                      <p className="text-xs text-muted-foreground">
                        MediaPipeによるリアルタイム分析対応
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <CheckCircle className="h-5 w-5 text-green-600" />
                    <div>
                      <p className="text-sm font-medium">食事写真分析</p>
                      <p className="text-xs text-muted-foreground">
                        AIによる栄養素自動計算
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <CheckCircle className="h-5 w-5 text-green-600" />
                    <div>
                      <p className="text-sm font-medium">運動位相検出</p>
                      <p className="text-xs text-muted-foreground">
                        5段階の運動フェーズ自動検出
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <CheckCircle className="h-5 w-5 text-green-600" />
                    <div>
                      <p className="text-sm font-medium">進捗追跡</p>
                      <p className="text-xs text-muted-foreground">
                        自動データ収集と分析
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* 身体組成タブ */}
          <TabsContent value="body" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>身体組成分析</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <h4 className="font-medium">基本指標</h4>
                    <div className="space-y-1">
                      <div className="flex justify-between">
                        <span className="text-sm">BMI</span>
                        <span className="font-medium">
                          {analysisData.body_composition.bmi}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm">体脂肪率</span>
                        <span className="font-medium">
                          {analysisData.body_composition.estimated_body_fat}%
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm">除脂肪体重</span>
                        <span className="font-medium">
                          {analysisData.body_composition.lean_body_mass?.lean_mass_kg}kg
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm">FFMI</span>
                        <span className="font-medium">
                          {analysisData.body_composition.ffmi?.normalized_ffmi}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <h4 className="font-medium">理想体重範囲</h4>
                    <div className="space-y-1">
                      <div className="flex justify-between">
                        <span className="text-sm">BMI基準</span>
                        <span className="font-medium">
                          {analysisData.body_composition.ideal_weight_range?.bmi_range.min} - 
                          {analysisData.body_composition.ideal_weight_range?.bmi_range.max}kg
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm">推奨範囲</span>
                        <span className="font-medium">
                          {analysisData.body_composition.ideal_weight_range?.recommended_range.min} - 
                          {analysisData.body_composition.ideal_weight_range?.recommended_range.max}kg
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* 健康警告 */}
                {analysisData.body_composition.health_warnings.length > 0 && (
                  <div className="mt-4 space-y-2">
                    <h4 className="font-medium text-red-600">健康上の警告</h4>
                    {analysisData.body_composition.health_warnings.map((warning, index) => (
                      <Alert key={index} variant="destructive">
                        <AlertCircle className="h-4 w-4" />
                        <AlertDescription>
                          <p className="font-medium">{warning.message}</p>
                          <p className="text-sm mt-1">{warning.details}</p>
                        </AlertDescription>
                      </Alert>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* 栄養タブ */}
          <TabsContent value="nutrition" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>栄養計画</CardTitle>
                <CardDescription>
                  目標達成のための最適な栄養プラン
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* マクロ栄養素 */}
                <div>
                  <h4 className="font-medium mb-2">日次マクロ栄養素</h4>
                  <div className="grid gap-4 md:grid-cols-3">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">
                        {analysisData.nutrition.daily_macros.protein_g}g
                      </div>
                      <p className="text-sm text-muted-foreground">
                        タンパク質 ({analysisData.nutrition.daily_macros.protein_ratio}%)
                      </p>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">
                        {analysisData.nutrition.daily_macros.carbs_g}g
                      </div>
                      <p className="text-sm text-muted-foreground">
                        炭水化物 ({analysisData.nutrition.daily_macros.carbs_ratio}%)
                      </p>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-orange-600">
                        {analysisData.nutrition.daily_macros.fat_g}g
                      </div>
                      <p className="text-sm text-muted-foreground">
                        脂質 ({analysisData.nutrition.daily_macros.fat_ratio}%)
                      </p>
                    </div>
                  </div>
                </div>

                {/* タンパク質必要量 */}
                <div>
                  <h4 className="font-medium mb-2">タンパク質摂取ガイド</h4>
                  <div className="bg-muted p-4 rounded-lg">
                    <div className="grid gap-2">
                      <div className="flex justify-between">
                        <span>1日の必要量</span>
                        <span className="font-medium">
                          {analysisData.nutrition.protein_requirements.daily_total_g}g
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>体重1kgあたり</span>
                        <span className="font-medium">
                          {analysisData.nutrition.protein_requirements.per_kg_body_weight}g
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>推奨摂取回数</span>
                        <span className="font-medium">
                          {analysisData.nutrition.protein_requirements.meal_distribution.meals_per_day}回/日
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* 食事プラン */}
                {analysisData.nutrition.meal_plan && (
                  <div>
                    <h4 className="font-medium mb-2">1日の食事プラン例</h4>
                    <div className="space-y-2">
                      {analysisData.nutrition.meal_plan.meal_plan.map((meal, index) => (
                        <div key={index} className="border rounded-lg p-3">
                          <div className="flex justify-between items-center mb-2">
                            <span className="font-medium">{meal.timing}</span>
                            <Badge variant="secondary">{meal.calories}kcal</Badge>
                          </div>
                          <div className="text-sm text-muted-foreground">
                            P: {meal.protein_g}g | C: {meal.carbs_g}g | F: {meal.fat_g}g
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* トレーニングタブ */}
          <TabsContent value="training" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>トレーニングプログラム</CardTitle>
                <CardDescription>
                  {analysisData.training.workout_plan.experience_level}レベル向け
                  {analysisData.training.workout_plan.training_goal}プログラム
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid gap-2">
                    <div className="flex justify-between">
                      <span>頻度</span>
                      <span className="font-medium">
                        {analysisData.training.workout_plan.frequency}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>セッション時間</span>
                      <span className="font-medium">
                        {analysisData.training.workout_plan.duration}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>スプリットタイプ</span>
                      <span className="font-medium">
                        {analysisData.training.workout_plan.split_type}
                      </span>
                    </div>
                  </div>

                  {/* プログレッション計画 */}
                  <div>
                    <h4 className="font-medium mb-2">プログレッション計画</h4>
                    <div className="space-y-2">
                      {Object.entries(analysisData.training.workout_plan.progression_plan).map(([key, value]: [string, any]) => (
                        <div key={key} className="bg-muted p-3 rounded">
                          <p className="font-medium text-sm">{key}</p>
                          <p className="text-sm text-muted-foreground">
                            {typeof value === 'object' ? value.focus : value}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* 安全性タブ */}
          <TabsContent value="safety" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>安全性分析</CardTitle>
                <CardDescription>
                  健康リスクの評価と推奨事項
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* 総合評価 */}
                  <div className="text-center p-4 border rounded-lg">
                    <p className="text-sm text-muted-foreground mb-2">
                      総合安全性評価
                    </p>
                    <p className={`text-2xl font-bold ${getRiskLevelColor(analysisData.safety_analysis.overall_safety)}`}>
                      {analysisData.safety_analysis.overall_safety === 'safe' ? '安全' :
                       analysisData.safety_analysis.overall_safety === 'low_risk' ? '低リスク' :
                       analysisData.safety_analysis.overall_safety === 'moderate_risk' ? '中リスク' : '高リスク'}
                    </p>
                    <p className="text-sm text-muted-foreground mt-2">
                      リスクスコア: {analysisData.safety_analysis.risk_score}/100
                    </p>
                  </div>

                  {/* 警告リスト */}
                  {analysisData.safety_analysis.warnings.length > 0 && (
                    <div>
                      <h4 className="font-medium mb-2">健康上の懸念事項</h4>
                      <div className="space-y-2">
                        {analysisData.safety_analysis.warnings.map((warning, index) => (
                          <Alert key={index} variant={warning.level === 'critical' ? 'destructive' : 'default'}>
                            {getWarningIcon(warning.level)}
                            <div className="ml-2">
                              <AlertDescription>
                                <p className="font-medium">{warning.message}</p>
                                {warning.details && (
                                  <p className="text-sm mt-1">{warning.details}</p>
                                )}
                                {warning.recommendation && (
                                  <p className="text-sm mt-2 font-medium">
                                    推奨: {warning.recommendation}
                                  </p>
                                )}
                              </AlertDescription>
                            </div>
                          </Alert>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* 推奨事項 */}
                  {analysisData.safety_analysis.recommendations.length > 0 && (
                    <div>
                      <h4 className="font-medium mb-2">推奨アクション</h4>
                      <div className="space-y-2">
                        {analysisData.safety_analysis.recommendations.map((rec, index) => (
                          <div key={index} className="bg-muted p-3 rounded">
                            <Badge className="mb-2" variant={
                              rec.priority === 'immediate' ? 'destructive' :
                              rec.priority === 'high' ? 'default' : 'secondary'
                            }>
                              {rec.priority === 'immediate' ? '即座に対応' :
                               rec.priority === 'high' ? '優先度高' : '推奨'}
                            </Badge>
                            <p className="font-medium text-sm">{rec.action}</p>
                            {rec.specific_steps && (
                              <ul className="list-disc list-inside text-sm text-muted-foreground mt-2">
                                {rec.specific_steps.map((step, stepIndex) => (
                                  <li key={stepIndex}>{step}</li>
                                ))}
                              </ul>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* モニタリング計画 */}
                  <div>
                    <h4 className="font-medium mb-2">モニタリング計画</h4>
                    <div className="bg-muted p-4 rounded">
                      <div className="grid gap-2">
                        <div className="flex justify-between">
                          <span>頻度</span>
                          <span className="font-medium">
                            {analysisData.safety_analysis.monitoring_plan.frequency}
                          </span>
                        </div>
                        <div>
                          <span className="text-sm">追跡項目:</span>
                          <ul className="list-disc list-inside text-sm text-muted-foreground mt-1">
                            {analysisData.safety_analysis.monitoring_plan.metrics.map((metric, index) => (
                              <li key={index}>{metric}</li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}
    </div>
  )
}