'use client'

import { useState, useRef, useEffect, Suspense } from 'react'
import { Button } from '../../components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'
import { Camera, Circle, Square, ChevronLeft, Activity, Ruler, TrendingUp, Upload, RefreshCw } from 'lucide-react'
import { usePoseDetection } from '../../lib/mediapipe/usePoseDetection'
import { PoseResults } from '../../lib/mediapipe/types'
import { ExerciseSelector } from '../../components/pose-analysis/ExerciseSelector'
import { CalibrationModal } from '../../components/pose-analysis/CalibrationModal'
import { AnalysisResults } from '../../components/pose-analysis/AnalysisResults'
import Link from 'next/link'
import toast from 'react-hot-toast'
import { useSearchParams } from 'next/navigation'

function AnalyzeContent() {
  const searchParams = useSearchParams()
  const analyzeType = searchParams.get('type') || 'form'
  const [selectedExercise, setSelectedExercise] = useState<'squat' | 'deadlift' | 'bench_press'>('squat')
  const [isRecording, setIsRecording] = useState(false)
  const [recordedFrames, setRecordedFrames] = useState<PoseResults[]>([])
  const [showCalibration, setShowCalibration] = useState(false)
  const [showResults, setShowResults] = useState(false)
  const [recordingMode, setRecordingMode] = useState<'camera' | 'upload'>('camera')
  const recordingIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handlePoseResults = (results: PoseResults) => {
    if (isRecording) {
      setRecordedFrames(prev => [...prev, results])
    }
  }

  const {
    videoRef,
    canvasRef,
    isLoading,
    isDetecting,
    error,
    startDetection,
    stopDetection,
    switchCamera,
    currentFacingMode,
  } = usePoseDetection({
    onResults: handlePoseResults,
  })

  useEffect(() => {
    // ページロード時にカメラを開始
    startDetection()
    
    return () => {
      stopDetection()
      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current)
      }
    }
  }, [])

  const handleStartRecording = () => {
    if (!isDetecting) {
      startDetection()
    }
    setIsRecording(true)
    setRecordedFrames([])
    toast.success('録画を開始しました')
    
    // 10秒後に自動停止
    recordingIntervalRef.current = setTimeout(() => {
      handleStopRecording()
    }, 10000)
  }

  const handleStopRecording = () => {
    setIsRecording(false)
    if (recordingIntervalRef.current) {
      clearTimeout(recordingIntervalRef.current)
    }
    
    if (recordedFrames.length > 0) {
      toast.success('録画を停止しました。分析中...')
      // TODO: 分析処理を実行
      setTimeout(() => {
        setShowResults(true)
      }, 1000)
    } else {
      toast.error('録画データがありません')
    }
  }

  const handleToggleRecording = () => {
    if (isRecording) {
      handleStopRecording()
    } else {
      handleStartRecording()
    }
  }

  // 動画ファイル選択処理
  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    if (!file.type.startsWith('video/')) {
      toast.error('動画ファイルを選択してください')
      return
    }

    const maxSize = 100 * 1024 * 1024 // 100MB
    if (file.size > maxSize) {
      toast.error('ファイルサイズは100MB以下にしてください')
      return
    }

    toast.loading('動画をアップロード中...')

    const formData = new FormData()
    formData.append('video', file)
    formData.append('exercise', selectedExercise)

    try {
      const response = await fetch('/api/analyze/upload', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('アップロードに失敗しました')
      }

      const result = await response.json()
      toast.success('分析が完了しました')
      
      // 分析結果を表示
      setRecordedFrames(result.frames || [])
      setShowResults(true)
    } catch (error) {
      console.error('Upload error:', error)
      toast.error('動画の分析に失敗しました')
    }
  }

  // 身体測定ページの場合
  if (analyzeType === 'body_metrics') {
    return (
      <div className="min-h-screen bg-background">
        <header className="border-b">
          <div className="container mx-auto px-4 py-4 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link href="/">
                <Button variant="ghost" size="icon">
                  <ChevronLeft className="w-5 h-5" />
                </Button>
              </Link>
              <h1 className="text-2xl font-bold flex items-center gap-2">
                <Ruler className="w-6 h-6" />
                身体測定
              </h1>
            </div>
          </div>
        </header>

        <main className="container mx-auto px-4 py-8 max-w-4xl">
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>身体測定記録</CardTitle>
              <CardDescription>
                定期的に身体を測定して、トレーニングの効果を確認しましょう
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-6 md:grid-cols-2">
                <div className="space-y-4">
                  <h3 className="font-semibold text-lg">基本測定</h3>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                      <span className="text-sm font-medium">身長</span>
                      <span className="font-mono">175.5 cm</span>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                      <span className="text-sm font-medium">体重</span>
                      <span className="font-mono">72.3 kg</span>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                      <span className="text-sm font-medium">BMI</span>
                      <span className="font-mono">23.5</span>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="font-semibold text-lg">部位別測定</h3>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                      <span className="text-sm font-medium">左腕の長さ</span>
                      <span className="font-mono">62.8 cm</span>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                      <span className="text-sm font-medium">右腕の長さ</span>
                      <span className="font-mono">63.1 cm</span>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                      <span className="text-sm font-medium">左脚の長さ</span>
                      <span className="font-mono">95.2 cm</span>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                      <span className="text-sm font-medium">右脚の長さ</span>
                      <span className="font-mono">95.0 cm</span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                測定履歴
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12 text-muted-foreground">
                <p>測定履歴がありません</p>
                <p className="text-sm mt-2">定期的に測定を行うことで、進捗を確認できます</p>
              </div>
            </CardContent>
          </Card>
        </main>
      </div>
    )
  }

  // フォーム分析ページ（既存のコード）
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/">
              <Button variant="ghost" size="icon">
                <ChevronLeft className="w-5 h-5" />
              </Button>
            </Link>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <Camera className="w-6 h-6" />
              フォーム分析
            </h1>
          </div>
          <Button
            variant="outline"
            onClick={() => setShowCalibration(true)}
          >
            キャリブレーション
          </Button>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {!showResults ? (
          <>
            <div className="mb-6 space-y-4">
              <ExerciseSelector
                selectedExercise={selectedExercise}
                onSelectExercise={setSelectedExercise}
              />
              
              {/* モード選択 */}
              <div className="flex gap-2 justify-center">
                <Button
                  variant={recordingMode === 'camera' ? 'default' : 'outline'}
                  onClick={() => setRecordingMode('camera')}
                  className="flex items-center gap-2"
                >
                  <Camera className="w-4 h-4" />
                  カメラで撮影
                </Button>
                <Button
                  variant={recordingMode === 'upload' ? 'default' : 'outline'}
                  onClick={() => setRecordingMode('upload')}
                  className="flex items-center gap-2"
                >
                  <Upload className="w-4 h-4" />
                  動画をアップロード
                </Button>
              </div>
            </div>

            <div className="grid gap-6 lg:grid-cols-3">
              <div className="lg:col-span-2">
                <Card>
                  <CardHeader>
                    <CardTitle>カメラビュー</CardTitle>
                    <CardDescription>
                      全身が映るようにカメラを設置してください
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    {recordingMode === 'camera' ? (
                      <>
                        <div className="video-container relative">
                          <video
                            ref={videoRef}
                            className="video-element rounded-lg bg-black"
                            playsInline
                            muted
                          />
                          <canvas
                            ref={canvasRef}
                            className="canvas-overlay"
                            width={1280}
                            height={720}
                          />
                          {isLoading && (
                            <div className="absolute inset-0 flex items-center justify-center bg-black/50 rounded-lg">
                              <div className="text-white text-center">
                                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-2"></div>
                                <p>カメラを準備中...</p>
                              </div>
                            </div>
                          )}
                          {error && (
                            <div className="absolute inset-0 flex items-center justify-center bg-black/50 rounded-lg">
                              <div className="text-white text-center bg-red-600/90 p-4 rounded">
                                <p className="font-semibold">エラー</p>
                                <p className="text-sm">{error}</p>
                              </div>
                            </div>
                          )}
                        </div>

                        <div className="mt-6 flex justify-center gap-4">
                          <Button
                            variant="outline"
                            onClick={switchCamera}
                            disabled={isLoading || !!error || isRecording}
                          >
                            <RefreshCw className="w-5 h-5 mr-2" />
                            {currentFacingMode === 'user' ? '外カメラ' : '内カメラ'}
                          </Button>
                          <Button
                            size="lg"
                            onClick={handleToggleRecording}
                            disabled={isLoading || !!error}
                            className={isRecording ? 'bg-red-600 hover:bg-red-700' : ''}
                          >
                            {isRecording ? (
                              <>
                                <Square className="w-5 h-5 mr-2" />
                                録画停止
                              </>
                            ) : (
                              <>
                                <Circle className="w-5 h-5 mr-2" />
                                録画開始
                              </>
                            )}
                          </Button>
                        </div>
                      </>
                    ) : (
                      <>
                        <div className="upload-area border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-12 text-center">
                          <input
                            ref={fileInputRef}
                            type="file"
                            accept="video/*"
                            onChange={handleFileSelect}
                            className="hidden"
                          />
                          <Upload className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                          <Button
                            onClick={() => fileInputRef.current?.click()}
                            size="lg"
                            className="mb-4"
                          >
                            動画ファイルを選択
                          </Button>
                          <p className="text-sm text-muted-foreground">
                            MP4, MOV, AVI形式の動画をアップロードできます<br />
                            最大ファイルサイズ: 100MB
                          </p>
                        </div>
                      </>
                    )}

                    {isRecording && (
                      <div className="mt-4 text-center">
                        <div className="flex items-center justify-center gap-2 text-red-600">
                          <Activity className="w-5 h-5 animate-pulse" />
                          <span className="font-semibold">録画中...</span>
                        </div>
                        <p className="text-sm text-muted-foreground mt-1">
                          フレーム数: {recordedFrames.length}
                        </p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>

              <div className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>セットアップガイド</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <div className="flex items-start gap-2">
                      <div className="w-5 h-5 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <span className="text-xs font-semibold">1</span>
                      </div>
                      <p className="text-sm">カメラから2-3m離れて立つ</p>
                    </div>
                    <div className="flex items-start gap-2">
                      <div className="w-5 h-5 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <span className="text-xs font-semibold">2</span>
                      </div>
                      <p className="text-sm">全身が画面に収まることを確認</p>
                    </div>
                    <div className="flex items-start gap-2">
                      <div className="w-5 h-5 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <span className="text-xs font-semibold">3</span>
                      </div>
                      <p className="text-sm">明るい場所で撮影する</p>
                    </div>
                    <div className="flex items-start gap-2">
                      <div className="w-5 h-5 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <span className="text-xs font-semibold">4</span>
                      </div>
                      <p className="text-sm">横向きで撮影する（スクワット・デッドリフト）</p>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>検出状態</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm">カメラ</span>
                        <span className={`text-sm font-semibold ${isDetecting ? 'text-green-600' : 'text-gray-500'}`}>
                          {isDetecting ? 'アクティブ' : '停止中'}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm">姿勢検出</span>
                        <span className={`text-sm font-semibold ${recordedFrames.length > 0 ? 'text-green-600' : 'text-gray-500'}`}>
                          {recordedFrames.length > 0 ? '検出中' : '待機中'}
                        </span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </>
        ) : (
          <AnalysisResults
            exercise={selectedExercise}
            frames={recordedFrames}
            onClose={() => {
              setShowResults(false)
              setRecordedFrames([])
            }}
          />
        )}
      </main>

      <CalibrationModal
        open={showCalibration}
        onClose={() => setShowCalibration(false)}
      />
    </div>
  )
}

export default function AnalyzePage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    }>
      <AnalyzeContent />
    </Suspense>
  )
}