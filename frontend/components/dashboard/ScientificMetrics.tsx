'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  Flame,
  Activity,
  TrendingUp,
  Scale,
  Heart,
  Info,
  Target,
  AlertCircle
} from 'lucide-react'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from './ChartWrapper'
import {
  BMRResult,
  TDEEResult,
  BodyFatResult,
  TargetCaloriesResult,
  PFCBalanceResult,
  CalorieSafetyResult
} from '@/services/v3Api'

interface ScientificMetricsProps {
  bmr?: BMRResult
  tdee?: TDEEResult
  bodyFat?: BodyFatResult
  targetCalories?: TargetCaloriesResult
  pfcBalance?: PFCBalanceResult
  calorieSafety?: CalorieSafetyResult
  isLoading?: boolean
}

export function ScientificMetrics({
  bmr,
  tdee,
  bodyFat,
  targetCalories,
  pfcBalance,
  calorieSafety,
  isLoading = false
}: ScientificMetricsProps) {
  const [selectedMetric, setSelectedMetric] = useState<string | null>(null)

  // PFCバランスのデータ準備
  const pfcData = pfcBalance ? [
    { name: 'タンパク質', value: pfcBalance.protein.percentage, color: '#3B82F6' },
    { name: '脂質', value: pfcBalance.fat.percentage, color: '#F59E0B' },
    { name: '炭水化物', value: pfcBalance.carbs.percentage, color: '#10B981' }
  ] : []

  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <Card key={i}>
            <CardHeader>
              <Skeleton className="h-4 w-32" />
              <Skeleton className="h-3 w-48 mt-2" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-8 w-24" />
              <Skeleton className="h-4 w-full mt-2" />
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* メインメトリクス */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {/* BMRカード */}
        {bmr && (
          <Card className="hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => setSelectedMetric('bmr')}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">基礎代謝率 (BMR)</CardTitle>
              <Heart className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{Math.round(bmr.bmr)} kcal/日</div>
              <p className="text-xs text-muted-foreground mt-1">
                {bmr.formula}式で計算
              </p>
              <Progress value={100} className="mt-2" />
            </CardContent>
          </Card>
        )}

        {/* TDEEカード */}
        {tdee && (
          <Card className="hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => setSelectedMetric('tdee')}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">総消費カロリー (TDEE)</CardTitle>
              <Flame className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{Math.round(tdee.tdee)} kcal/日</div>
              <p className="text-xs text-muted-foreground mt-1">
                活動レベル: {tdee.activity_level_description}
              </p>
              <Badge variant="secondary" className="mt-2">
                係数 ×{tdee.activity_multiplier}
              </Badge>
            </CardContent>
          </Card>
        )}

        {/* 体脂肪率カード */}
        {bodyFat && (
          <Card className="hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => setSelectedMetric('bodyFat')}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">推定体脂肪率</CardTitle>
              <Scale className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{bodyFat.body_fat_percentage.toFixed(1)}%</div>
              <div className="space-y-1 mt-2">
                <p className="text-xs text-muted-foreground">
                  除脂肪体重: {bodyFat.lean_body_mass.toFixed(1)}kg
                </p>
                <p className="text-xs text-muted-foreground">
                  体脂肪量: {bodyFat.fat_mass.toFixed(1)}kg
                </p>
              </div>
              <Badge variant="outline" className="mt-2 text-xs">
                {bodyFat.method}法
              </Badge>
            </CardContent>
          </Card>
        )}

        {/* 目標カロリーカード */}
        {targetCalories && (
          <Card className="hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => setSelectedMetric('targetCalories')}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">目標摂取カロリー</CardTitle>
              <Target className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{Math.round(targetCalories.daily_calories)} kcal/日</div>
              <p className="text-xs text-muted-foreground mt-1">
                {targetCalories.description}
              </p>
              <div className="flex items-center gap-2 mt-2">
                <TrendingUp className="h-3 w-3" />
                <span className="text-xs">
                  週間変化予測: {targetCalories.weekly_weight_change_estimate.toFixed(2)}kg
                </span>
              </div>
            </CardContent>
          </Card>
        )}

        {/* カロリー安全性カード */}
        {calorieSafety && (
          <Card className={`hover:shadow-lg transition-shadow cursor-pointer ${
            !calorieSafety.is_safe ? 'border-destructive' : ''
          }`} onClick={() => setSelectedMetric('safety')}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">安全性チェック</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                {calorieSafety.is_safe ? (
                  <>
                    <Badge variant="success">安全</Badge>
                    <span className="text-sm text-green-600">設定は適切です</span>
                  </>
                ) : (
                  <>
                    <Badge variant="destructive">警告</Badge>
                    <span className="text-sm text-destructive">見直しが必要</span>
                  </>
                )}
              </div>
              <p className="text-xs text-muted-foreground mt-2">
                最低推奨: {calorieSafety.minimum_safe_calories}kcal
              </p>
            </CardContent>
          </Card>
        )}
      </div>

      {/* PFCバランスチャート */}
      {pfcBalance && (
        <Card>
          <CardHeader>
            <CardTitle>PFCバランス</CardTitle>
            <CardDescription>
              推奨される主要栄養素の配分
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-6">
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={pfcData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, value }) => `${name}: ${value}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {pfcData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium flex items-center gap-2">
                      <div className="w-3 h-3 bg-blue-500 rounded-full" />
                      タンパク質
                    </span>
                    <span className="text-sm">{pfcBalance.protein.grams}g</span>
                  </div>
                  <Progress value={pfcBalance.protein.percentage} className="h-2" />
                  <p className="text-xs text-muted-foreground mt-1">
                    {pfcBalance.protein.calories}kcal ({pfcBalance.protein.percentage}%)
                  </p>
                </div>
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium flex items-center gap-2">
                      <div className="w-3 h-3 bg-amber-500 rounded-full" />
                      脂質
                    </span>
                    <span className="text-sm">{pfcBalance.fat.grams}g</span>
                  </div>
                  <Progress value={pfcBalance.fat.percentage} className="h-2" />
                  <p className="text-xs text-muted-foreground mt-1">
                    {pfcBalance.fat.calories}kcal ({pfcBalance.fat.percentage}%)
                  </p>
                </div>
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium flex items-center gap-2">
                      <div className="w-3 h-3 bg-green-500 rounded-full" />
                      炭水化物
                    </span>
                    <span className="text-sm">{pfcBalance.carbs.grams}g</span>
                  </div>
                  <Progress value={pfcBalance.carbs.percentage} className="h-2" />
                  <p className="text-xs text-muted-foreground mt-1">
                    {pfcBalance.carbs.calories}kcal ({pfcBalance.carbs.percentage}%)
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 詳細情報モーダル */}
      {selectedMetric && (
        <Alert>
          <Info className="h-4 w-4" />
          <AlertDescription>
            {selectedMetric === 'bmr' && 'BMR（基礎代謝率）は、完全に安静な状態で生命維持に必要な最小限のエネルギー量です。'}
            {selectedMetric === 'tdee' && 'TDEE（総消費カロリー）は、日常活動を含めた1日の総エネルギー消費量です。'}
            {selectedMetric === 'bodyFat' && '体脂肪率は身体測定値から推定された値です。正確な測定にはDEXAスキャンなどが必要です。'}
            {selectedMetric === 'targetCalories' && '目標カロリーは、あなたの目標と活動レベルに基づいて計算された推奨摂取量です。'}
            {selectedMetric === 'safety' && 'カロリー設定の安全性は、健康的な範囲内であるかを評価しています。'}
          </AlertDescription>
        </Alert>
      )}

      {/* 警告表示 */}
      {calorieSafety && !calorieSafety.is_safe && calorieSafety.warnings.length > 0 && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            <div className="space-y-2">
              <p className="font-semibold">安全性に関する警告:</p>
              <ul className="list-disc list-inside space-y-1">
                {calorieSafety.warnings.map((warning, index) => (
                  <li key={index} className="text-sm">{warning}</li>
                ))}
              </ul>
              <p className="text-sm mt-3">{calorieSafety.recommendation}</p>
            </div>
          </AlertDescription>
        </Alert>
      )}
    </div>
  )
}