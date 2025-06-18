'use client'

import { useState } from 'react'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import {
  AlertTriangle,
  Info,
  ShieldAlert,
  Heart,
  Activity,
  Zap,
  TrendingDown,
  CheckCircle2,
  XCircle
} from 'lucide-react'

interface HealthWarning {
  id: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  category: 'calorie' | 'body_fat' | 'activity' | 'nutrition' | 'general'
  title: string
  description: string
  recommendation: string
  metrics?: {
    current: number
    safe_min?: number
    safe_max?: number
    unit: string
  }
}

interface HealthWarningsProps {
  warnings: HealthWarning[]
  onDismiss?: (warningId: string) => void
  onAcceptRecommendation?: (warningId: string) => void
}

export function HealthWarnings({ warnings, onDismiss, onAcceptRecommendation }: HealthWarningsProps) {
  const [dismissedWarnings, setDismissedWarnings] = useState<Set<string>>(new Set())
  const [expandedWarning, setExpandedWarning] = useState<string | null>(null)

  const activeWarnings = warnings.filter(w => !dismissedWarnings.has(w.id))

  const getSeverityIcon = (severity: HealthWarning['severity']) => {
    switch (severity) {
      case 'critical':
        return <ShieldAlert className="h-5 w-5 text-red-600" />
      case 'high':
        return <AlertTriangle className="h-5 w-5 text-orange-600" />
      case 'medium':
        return <Info className="h-5 w-5 text-yellow-600" />
      case 'low':
        return <Info className="h-5 w-5 text-blue-600" />
    }
  }

  const getSeverityColor = (severity: HealthWarning['severity']) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-50 border-red-200 text-red-900'
      case 'high':
        return 'bg-orange-50 border-orange-200 text-orange-900'
      case 'medium':
        return 'bg-yellow-50 border-yellow-200 text-yellow-900'
      case 'low':
        return 'bg-blue-50 border-blue-200 text-blue-900'
    }
  }

  const getCategoryIcon = (category: HealthWarning['category']) => {
    switch (category) {
      case 'calorie':
        return <Zap className="h-4 w-4" />
      case 'body_fat':
        return <TrendingDown className="h-4 w-4" />
      case 'activity':
        return <Activity className="h-4 w-4" />
      case 'nutrition':
        return <Heart className="h-4 w-4" />
      case 'general':
        return <Info className="h-4 w-4" />
    }
  }

  const handleDismiss = (warningId: string) => {
    setDismissedWarnings(prev => new Set(prev).add(warningId))
    onDismiss?.(warningId)
  }

  const criticalWarnings = activeWarnings.filter(w => w.severity === 'critical')
  const otherWarnings = activeWarnings.filter(w => w.severity !== 'critical')

  if (activeWarnings.length === 0) {
    return (
      <Card className="border-green-200 bg-green-50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-green-800">
            <CheckCircle2 className="h-5 w-5" />
            健康状態は良好です
          </CardTitle>
          <CardDescription className="text-green-700">
            現在、健康に関する警告はありません
          </CardDescription>
        </CardHeader>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      {/* 重大な警告 */}
      {criticalWarnings.map((warning) => (
        <AlertDialog key={warning.id}>
          <AlertDialogTrigger asChild>
            <Alert
              variant="destructive"
              className="cursor-pointer hover:shadow-lg transition-shadow"
            >
              <div className="flex items-start gap-2">
                {getSeverityIcon(warning.severity)}
                <div className="flex-1">
                  <AlertTitle className="mb-1">{warning.title}</AlertTitle>
                  <AlertDescription>{warning.description}</AlertDescription>
                  {warning.metrics && (
                    <div className="mt-3 space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <span>現在値: {warning.metrics.current} {warning.metrics.unit}</span>
                        {warning.metrics.safe_min && (
                          <span className="text-muted-foreground">
                            安全範囲: {warning.metrics.safe_min}-{warning.metrics.safe_max} {warning.metrics.unit}
                          </span>
                        )}
                      </div>
                      {warning.metrics.safe_min && warning.metrics.safe_max && (
                        <Progress
                          value={
                            ((warning.metrics.current - warning.metrics.safe_min) /
                              (warning.metrics.safe_max - warning.metrics.safe_min)) * 100
                          }
                          className="h-2"
                        />
                      )}
                    </div>
                  )}
                </div>
              </div>
            </Alert>
          </AlertDialogTrigger>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle className="flex items-center gap-2">
                {getSeverityIcon(warning.severity)}
                {warning.title}
              </AlertDialogTitle>
              <AlertDialogDescription asChild>
                <div className="space-y-4">
                  <p>{warning.description}</p>
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <h4 className="font-semibold text-blue-900 mb-2">推奨事項</h4>
                    <p className="text-blue-800">{warning.recommendation}</p>
                  </div>
                  {warning.metrics && (
                    <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                      <h4 className="font-semibold text-gray-900 mb-2">詳細データ</h4>
                      <dl className="space-y-1 text-sm">
                        <div className="flex justify-between">
                          <dt className="text-gray-600">現在値:</dt>
                          <dd className="font-medium">{warning.metrics.current} {warning.metrics.unit}</dd>
                        </div>
                        {warning.metrics.safe_min && (
                          <div className="flex justify-between">
                            <dt className="text-gray-600">推奨範囲:</dt>
                            <dd className="font-medium">
                              {warning.metrics.safe_min}-{warning.metrics.safe_max} {warning.metrics.unit}
                            </dd>
                          </div>
                        )}
                      </dl>
                    </div>
                  )}
                </div>
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel onClick={() => handleDismiss(warning.id)}>
                後で確認
              </AlertDialogCancel>
              <AlertDialogAction onClick={() => onAcceptRecommendation?.(warning.id)}>
                推奨事項を適用
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      ))}

      {/* その他の警告 */}
      {otherWarnings.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">健康に関する注意事項</CardTitle>
            <CardDescription>
              以下の項目について確認することをお勧めします
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {otherWarnings.map((warning) => (
              <div
                key={warning.id}
                className={`p-4 rounded-lg border ${getSeverityColor(warning.severity)} 
                  ${expandedWarning === warning.id ? 'shadow-md' : ''} 
                  cursor-pointer transition-all`}
                onClick={() => setExpandedWarning(
                  expandedWarning === warning.id ? null : warning.id
                )}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    {getSeverityIcon(warning.severity)}
                    <div className="flex-1">
                      <h4 className="font-medium flex items-center gap-2">
                        {warning.title}
                        {getCategoryIcon(warning.category)}
                      </h4>
                      <p className="text-sm mt-1 opacity-90">{warning.description}</p>
                      
                      {expandedWarning === warning.id && (
                        <div className="mt-3 space-y-3">
                          <div className="bg-white/60 rounded p-3">
                            <p className="text-sm font-medium mb-1">推奨事項:</p>
                            <p className="text-sm">{warning.recommendation}</p>
                          </div>
                          
                          {warning.metrics && (
                            <div className="bg-white/60 rounded p-3">
                              <div className="flex items-center justify-between text-sm">
                                <span>現在: {warning.metrics.current} {warning.metrics.unit}</span>
                                {warning.metrics.safe_min && (
                                  <span>
                                    推奨: {warning.metrics.safe_min}-{warning.metrics.safe_max} {warning.metrics.unit}
                                  </span>
                                )}
                              </div>
                            </div>
                          )}
                          
                          <div className="flex gap-2 mt-3">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={(e) => {
                                e.stopPropagation()
                                handleDismiss(warning.id)
                              }}
                            >
                              <XCircle className="h-3 w-3 mr-1" />
                              非表示
                            </Button>
                            <Button
                              size="sm"
                              onClick={(e) => {
                                e.stopPropagation()
                                onAcceptRecommendation?.(warning.id)
                              }}
                            >
                              <CheckCircle2 className="h-3 w-3 mr-1" />
                              対応する
                            </Button>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                  <Badge variant="outline" className="ml-2">
                    {warning.severity === 'high' && '高'}
                    {warning.severity === 'medium' && '中'}
                    {warning.severity === 'low' && '低'}
                  </Badge>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  )
}