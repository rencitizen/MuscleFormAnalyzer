'use client'

import { useState, useRef, useEffect, Suspense } from 'react'
import { Button } from '../../components/ui/button'
import { Card, CardContent } from '../../components/ui/card'
import { Camera, Circle, Square, ChevronLeft, RefreshCw } from 'lucide-react'
import { usePoseDetectionEnhanced } from '../../lib/mediapipe/usePoseDetectionEnhanced'
import { PoseResults } from '../../lib/mediapipe/types'
import { ExerciseSelector } from '../../components/pose-analysis/ExerciseSelector'
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
  const [showResults, setShowResults] = useState(false)
  const recordingIntervalRef = useRef<NodeJS.Timeout | null>(null)

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
    hasMultipleCameras,
  } = usePoseDetectionEnhanced({
    onResults: handlePoseResults,
    initialFacingMode: 'environment'
  })

  useEffect(() => {
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

  // 身体測定ページの場合
  if (analyzeType === 'body_metrics') {
    return (
      <div className="min-h-screen bg-background">
        <header className="border-b">
          <div className="container mx-auto px-4 py-4">
            <Link href="/">
              <Button variant="ghost" size="icon" className="mr-4">
                <ChevronLeft className="w-5 h-5" />
              </Button>
            </Link>
            <span className="text-xl font-semibold">身体測定</span>
          </div>
        </header>

        <main className="container mx-auto px-4 py-8 max-w-2xl">
          <Card>
            <CardContent className="pt-6">
              <div className="text-center py-8 text-muted-foreground">
                <p>測定機能は準備中です</p>
              </div>
            </CardContent>
          </Card>
        </main>
      </div>
    )
  }

  // フォーム分析ページ
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="container mx-auto px-4 py-4">
          <Link href="/">
            <Button variant="ghost" size="icon" className="mr-4">
              <ChevronLeft className="w-5 h-5" />
            </Button>
          </Link>
          <span className="text-xl font-semibold">フォーム分析</span>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {!showResults ? (
          <>
            <div className="mb-6">
              <ExerciseSelector
                selectedExercise={selectedExercise}
                onSelectExercise={setSelectedExercise}
              />
            </div>

            <div className="max-w-2xl mx-auto">
              <Card>
                <CardContent className="pt-6">
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
                    {hasMultipleCameras && !isLoading && (
                      <Button
                        variant="outline"
                        size="icon"
                        onClick={switchCamera}
                        className="absolute top-4 right-4 z-10"
                        title="カメラを切り替える"
                      >
                        <RefreshCw className="w-4 h-4" />
                      </Button>
                    )}
                  </div>

                  <div className="mt-6 flex justify-center">
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

                  {isRecording && (
                    <div className="mt-4 text-center">
                      <p className="text-sm text-muted-foreground">
                        録画中... {Math.ceil(recordedFrames.length / 30)}秒
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
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