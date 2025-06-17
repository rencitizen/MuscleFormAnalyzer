'use client'

import { useState, useRef, useCallback } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Camera, 
  Upload, 
  Play, 
  Pause, 
  Download,
  Info,
  RefreshCw
} from 'lucide-react'
import { usePoseDetectionEnhanced } from '@/lib/mediapipe/usePoseDetectionEnhanced'

export default function PoseAnalysisPage() {
  const [mode, setMode] = useState<'camera' | 'upload'>('camera')
  const [height, setHeight] = useState<string>('170')
  const [selectedExercise, setSelectedExercise] = useState<string>('squat')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisResults, setAnalysisResults] = useState<any>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const videoRef = useRef<HTMLVideoElement>(null)

  const { 
    isInitialized,
    isProcessing,
    landmarks,
    startCamera,
    stopCamera,
    processImage
  } = usePoseDetectionEnhanced()

  const exercises = [
    { value: 'squat', label: 'スクワット' },
    { value: 'deadlift', label: 'デッドリフト' },
    { value: 'bench_press', label: 'ベンチプレス' },
    { value: 'shoulder_press', label: 'ショルダープレス' },
    { value: 'lunge', label: 'ランジ' },
    { value: 'plank', label: 'プランク' }
  ]

  const handleStartAnalysis = useCallback(async () => {
    if (mode === 'camera') {
      setIsAnalyzing(true)
      await startCamera()
    }
  }, [mode, startCamera])

  const handleStopAnalysis = useCallback(() => {
    setIsAnalyzing(false)
    stopCamera()
  }, [stopCamera])

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    const url = URL.createObjectURL(file)
    if (videoRef.current) {
      videoRef.current.src = url
      setIsAnalyzing(true)
    }
  }

  const exportResults = () => {
    if (!analysisResults) return
    
    const dataStr = JSON.stringify(analysisResults, null, 2)
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr)
    
    const exportFileDefaultName = `pose_analysis_${new Date().toISOString()}.json`
    
    const linkElement = document.createElement('a')
    linkElement.setAttribute('href', dataUri)
    linkElement.setAttribute('download', exportFileDefaultName)
    linkElement.click()
  }

  const saveToDatabase = async () => {
    // API呼び出し実装予定
    console.log('Saving to database...', analysisResults)
  }

  return (
    <div className="container mx-auto px-4 py-8 pb-24 md:pb-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">姿勢分析</h1>
        <p className="text-muted-foreground">カメラまたは動画から運動フォームを分析します</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* 左側：設定パネル */}
        <div className="lg:col-span-1 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>分析設定</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Tabs value={mode} onValueChange={(v) => setMode(v as 'camera' | 'upload')}>
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="camera">
                    <Camera className="w-4 h-4 mr-2" />
                    カメラ
                  </TabsTrigger>
                  <TabsTrigger value="upload">
                    <Upload className="w-4 h-4 mr-2" />
                    動画アップロード
                  </TabsTrigger>
                </TabsList>
              </Tabs>

              <div>
                <Label htmlFor="exercise">エクササイズ種目</Label>
                <Select value={selectedExercise} onValueChange={setSelectedExercise}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {exercises.map((exercise) => (
                      <SelectItem key={exercise.value} value={exercise.value}>
                        {exercise.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="height">身長 (cm)</Label>
                <Input
                  id="height"
                  type="number"
                  value={height}
                  onChange={(e) => setHeight(e.target.value)}
                  placeholder="170"
                />
              </div>

              {mode === 'camera' ? (
                <Button 
                  onClick={isAnalyzing ? handleStopAnalysis : handleStartAnalysis}
                  className="w-full"
                  disabled={!isInitialized}
                >
                  {isAnalyzing ? (
                    <>
                      <Pause className="w-4 h-4 mr-2" />
                      分析停止
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4 mr-2" />
                      分析開始
                    </>
                  )}
                </Button>
              ) : (
                <div>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="video/*"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                  <Button
                    onClick={() => fileInputRef.current?.click()}
                    className="w-full"
                  >
                    <Upload className="w-4 h-4 mr-2" />
                    動画を選択
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          {/* リアルタイム情報 */}
          {landmarks && (
            <Card>
              <CardHeader>
                <CardTitle>検出情報</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>検出状態:</span>
                  <span className="text-green-600">検出中</span>
                </div>
                <div className="flex justify-between">
                  <span>関節数:</span>
                  <span>{landmarks.length}</span>
                </div>
                <div className="flex justify-between">
                  <span>信頼度:</span>
                  <span>{(landmarks[0]?.visibility * 100).toFixed(1)}%</span>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* 中央：ビデオ表示 */}
        <div className="lg:col-span-2">
          <Card className="h-full">
            <CardHeader>
              <CardTitle>映像プレビュー</CardTitle>
              <CardDescription>
                {mode === 'camera' ? 'カメラからのライブ映像' : '動画ファイル'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="relative aspect-video bg-gray-100 rounded-lg overflow-hidden">
                {mode === 'camera' ? (
                  <div id="camera-container" className="w-full h-full" />
                ) : (
                  <video
                    ref={videoRef}
                    className="w-full h-full object-contain"
                    controls
                  />
                )}
                {!isAnalyzing && (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-center">
                      <Camera className="w-12 h-12 mx-auto mb-2 text-gray-400" />
                      <p className="text-gray-500">
                        {mode === 'camera' ? '分析を開始してください' : '動画をアップロードしてください'}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* 分析結果 */}
      {analysisResults && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>分析結果</CardTitle>
            <CardDescription>フォーム評価と改善点</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-3 mb-4">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600">
                  {analysisResults.formScore || 85}
                </div>
                <div className="text-sm text-muted-foreground">フォームスコア</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600">
                  {analysisResults.phaseDetected || 'ボトム'}
                </div>
                <div className="text-sm text-muted-foreground">検出位相</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-600">
                  {analysisResults.repCount || 12}
                </div>
                <div className="text-sm text-muted-foreground">レップ数</div>
              </div>
            </div>

            <div className="space-y-2 mb-4">
              <h4 className="font-semibold">計測値</h4>
              <div className="grid gap-2 text-sm">
                <div className="flex justify-between">
                  <span>推定腕長:</span>
                  <span>{analysisResults.armLength || '65.2'} cm</span>
                </div>
                <div className="flex justify-between">
                  <span>推定脚長:</span>
                  <span>{analysisResults.legLength || '89.5'} cm</span>
                </div>
                <div className="flex justify-between">
                  <span>膝角度:</span>
                  <span>{analysisResults.kneeAngle || '92.3'}°</span>
                </div>
                <div className="flex justify-between">
                  <span>股関節角度:</span>
                  <span>{analysisResults.hipAngle || '87.5'}°</span>
                </div>
              </div>
            </div>

            <div className="flex gap-2">
              <Button onClick={exportResults} variant="outline">
                <Download className="w-4 h-4 mr-2" />
                JSONエクスポート
              </Button>
              <Button onClick={saveToDatabase}>
                データ保存
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}