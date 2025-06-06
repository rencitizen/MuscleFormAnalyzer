'use client'

import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { CheckCircle, XCircle, AlertCircle, Home, Download } from 'lucide-react'
import { PoseResults } from '@/lib/mediapipe/types'
import { analyzeExercise } from '@/lib/analysis/exerciseAnalyzer'
import Link from 'next/link'

interface AnalysisResultsProps {
  exercise: 'squat' | 'deadlift' | 'bench_press'
  frames: PoseResults[]
  onClose: () => void
}

export function AnalysisResults({ exercise, frames, onClose }: AnalysisResultsProps) {
  const [analysisResult, setAnalysisResult] = useState<any>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(true)

  useEffect(() => {
    // 分析を実行
    setTimeout(() => {
      const result = analyzeExercise(exercise, frames)
      setAnalysisResult(result)
      setIsAnalyzing(false)
    }, 2000) // デモ用の遅延
  }, [exercise, frames])

  if (isAnalyzing) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-lg font-semibold">分析中...</p>
          <p className="text-sm text-muted-foreground mt-2">
            {frames.length} フレームを処理しています
          </p>
        </div>
      </div>
    )
  }

  // ダミーの分析結果
  const dummyResult = {
    overallScore: 82,
    repCount: 5,
    scores: {
      depth: 85,
      form: 88,
      tempo: 75,
      balance: 80,
    },
    feedback: [
      { type: 'good', message: '膝の位置が適切です' },
      { type: 'good', message: '背中がまっすぐ保たれています' },
      { type: 'warning', message: 'もう少し深くしゃがむことができます' },
      { type: 'error', message: 'テンポが速すぎます。ゆっくりと下ろしましょう' },
    ],
    keyPoints: [
      { label: '最大深度', value: '大腿が床と平行' },
      { label: '膝の移動', value: '3cm 内側' },
      { label: '平均テンポ', value: '1.2秒/レップ' },
      { label: '体幹の安定性', value: '良好' },
    ],
  }

  const result = analysisResult || dummyResult

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600'
    if (score >= 70) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getFeedbackIcon = (type: string) => {
    switch (type) {
      case 'good':
        return <CheckCircle className="w-5 h-5 text-green-600" />
      case 'warning':
        return <AlertCircle className="w-5 h-5 text-yellow-600" />
      case 'error':
        return <XCircle className="w-5 h-5 text-red-600" />
      default:
        return null
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold">分析結果</h2>
        <div className="flex gap-2">
          <Button variant="outline" onClick={onClose}>
            もう一度分析
          </Button>
          <Link href="/">
            <Button variant="ghost">
              <Home className="w-4 h-4 mr-2" />
              ホーム
            </Button>
          </Link>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>総合スコア</CardTitle>
            <CardDescription>
              {result.repCount} レップの平均スコア
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center">
              <div className={`text-6xl font-bold ${getScoreColor(result.overallScore)}`}>
                {result.overallScore}
              </div>
              <p className="text-sm text-muted-foreground mt-2">/ 100</p>
            </div>
            <div className="mt-6 space-y-3">
              {Object.entries(result.scores).map(([key, value]) => (
                <div key={key}>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm capitalize">{key}</span>
                    <span className={`text-sm font-semibold ${getScoreColor(value as number)}`}>
                      {value}%
                    </span>
                  </div>
                  <Progress value={value as number} className="h-2" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>主要測定値</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {result.keyPoints.map((point: any, index: number) => (
                <div key={index} className="flex justify-between py-2 border-b last:border-0">
                  <span className="text-sm">{point.label}</span>
                  <span className="text-sm font-semibold">{point.value}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>フィードバック</CardTitle>
          <CardDescription>
            改善のためのアドバイス
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {result.feedback.map((item: any, index: number) => (
              <div key={index} className="flex items-start gap-3">
                {getFeedbackIcon(item.type)}
                <p className="text-sm">{item.message}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-center gap-4">
        <Button size="lg" className="gap-2">
          <Download className="w-4 h-4" />
          レポートをダウンロード
        </Button>
      </div>
    </div>
  )
}