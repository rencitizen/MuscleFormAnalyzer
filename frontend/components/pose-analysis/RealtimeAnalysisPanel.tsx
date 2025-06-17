'use client'

import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Button } from '../ui/button'
import { Activity, TrendingUp, AlertCircle } from 'lucide-react'
import { PoseResults } from '../../lib/mediapipe/types'
import { useEffect, useState } from 'react'
import { calculateJointAngles } from '../../lib/analysis/jointAngles'

interface RealtimeAnalysisPanelProps {
  poseData: PoseResults | null
  exercise: 'squat' | 'deadlift' | 'bench_press'
  onDetailedAnalysis?: () => void
}

export function RealtimeAnalysisPanel({ 
  poseData, 
  exercise,
  onDetailedAnalysis 
}: RealtimeAnalysisPanelProps) {
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisResults, setAnalysisResults] = useState<any>(null)
  const [confidence, setConfidence] = useState(0)

  // 信頼度の計算
  useEffect(() => {
    if (poseData?.landmarks) {
      const avgConfidence = poseData.landmarks.reduce((sum, landmark) => 
        sum + (landmark.visibility || 0), 0
      ) / poseData.landmarks.length
      setConfidence(Math.round(avgConfidence * 100))
    }
  }, [poseData])

  // リアルタイム分析の実行
  const performRealtimeAnalysis = async () => {
    if (!poseData?.landmarks || isAnalyzing) return

    try {
      setIsAnalyzing(true)

      // 関節角度の計算
      const jointAngles = calculateJointAngles(poseData.landmarks, exercise)

      // 簡易的な分析結果を生成
      const results = {
        overallScore: Math.round(Math.random() * 20 + 70), // TODO: 実際の計算ロジック
        formAccuracy: Math.round(Math.random() * 20 + 75),
        jointAngles: jointAngles,
        improvements: generateImprovements(jointAngles, exercise),
        timestamp: Date.now()
      }

      setAnalysisResults(results)
    } catch (error) {
      console.error('リアルタイム分析エラー:', error)
    } finally {
      setIsAnalyzing(false)
    }
  }

  // 改善点の生成
  const generateImprovements = (angles: Record<string, number>, exerciseType: string) => {
    const improvements = []
    
    if (exerciseType === 'squat') {
      if (angles.knee && angles.knee < 70) {
        improvements.push('膝の角度が深すぎます。70-90度を目指しましょう')
      }
      if (angles.hip && angles.hip > 120) {
        improvements.push('腰が高すぎます。もう少し深くしゃがみましょう')
      }
    } else if (exerciseType === 'deadlift') {
      if (angles.back && Math.abs(angles.back - 180) > 15) {
        improvements.push('背中をまっすぐに保ちましょう')
      }
    }

    if (improvements.length === 0) {
      improvements.push('良いフォームです！この調子で続けましょう')
    }

    return improvements
  }

  return (
    <div className="space-y-4">
      {/* 検出状態 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="w-5 h-5" />
            検出状態
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm">姿勢検出</span>
              <span className={`text-sm font-semibold ${poseData ? 'text-green-600' : 'text-red-600'}`}>
                {poseData ? '検出中' : '未検出'}
              </span>
            </div>
            
            {poseData && (
              <>
                <div className="flex justify-between items-center">
                  <span className="text-sm">信頼度</span>
                  <span className="text-sm font-semibold">{confidence}%</span>
                </div>
                
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${confidence}%` }}
                  />
                </div>
              </>
            )}
          </div>
        </CardContent>
      </Card>

      {/* リアルタイム分析結果 */}
      {analysisResults && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5" />
              分析結果
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* スコア表示 */}
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-3 bg-blue-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    {analysisResults.overallScore}%
                  </div>
                  <div className="text-xs text-gray-600">総合スコア</div>
                </div>
                <div className="text-center p-3 bg-green-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {analysisResults.formAccuracy}%
                  </div>
                  <div className="text-xs text-gray-600">フォーム精度</div>
                </div>
              </div>

              {/* 改善点 */}
              {analysisResults.improvements.length > 0 && (
                <div>
                  <h4 className="font-medium mb-2 flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 text-orange-500" />
                    アドバイス
                  </h4>
                  <ul className="space-y-1">
                    {analysisResults.improvements.map((improvement: string, index: number) => (
                      <li key={index} className="text-sm text-gray-700 flex items-start gap-2">
                        <span className="text-orange-500 mt-0.5">•</span>
                        <span>{improvement}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* 関節角度 */}
              {analysisResults.jointAngles && Object.keys(analysisResults.jointAngles).length > 0 && (
                <div>
                  <h4 className="font-medium mb-2">関節角度</h4>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    {Object.entries(analysisResults.jointAngles).map(([joint, angle]: [string, any]) => (
                      <div key={joint} className="flex justify-between bg-gray-50 p-2 rounded">
                        <span className="text-gray-600">{joint}:</span>
                        <span className="font-mono">{Math.round(angle)}°</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* コントロールボタン */}
      <Card>
        <CardContent className="pt-6">
          <div className="space-y-2">
            <Button
              onClick={performRealtimeAnalysis}
              disabled={!poseData || isAnalyzing}
              className="w-full"
              variant={isAnalyzing ? "secondary" : "default"}
            >
              {isAnalyzing ? '分析中...' : 'リアルタイム分析'}
            </Button>
            
            {onDetailedAnalysis && (
              <Button
                onClick={onDetailedAnalysis}
                variant="outline"
                className="w-full"
              >
                詳細分析を実行
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}