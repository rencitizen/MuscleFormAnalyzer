'use client'

import React, { useRef, useEffect, useState, useCallback } from 'react'
import { Camera } from '@mediapipe/camera_utils'
import { Pose, Results } from '@mediapipe/pose'
import { drawConnectors, drawLandmarks } from '@mediapipe/drawing_utils'
import { POSE_CONNECTIONS } from '@mediapipe/pose'
import { CameraGuide } from './CameraGuide'
import { Card } from '../ui/card'
import { Button } from '../ui/button'
import { Badge } from '../ui/badge'
import { Progress } from '../ui/progress'
import { Alert, AlertDescription } from '../ui/alert'
import { 
  Camera as CameraIcon, 
  Play, 
  Pause, 
  RotateCcw, 
  Settings,
  Info,
  CheckCircle,
  AlertCircle
} from 'lucide-react'

interface PoseAnalyzerEnhancedProps {
  exerciseType: 'squat' | 'bench_press' | 'deadlift'
  onAnalysisResult?: (result: AnalysisResult) => void
  onLandmarksUpdate?: (landmarks: any[]) => void
  userProfile?: any
}

interface AnalysisResult {
  score: number
  angle_scores: Record<string, any>
  phase: string
  feedback: Array<{
    type: string
    priority: string
    message: string
    joint?: string
  }>
  confidence: number
  processing_time: number
  analyzer_type: string
  biomechanics?: any
}

export default function PoseAnalyzerEnhanced({ 
  exerciseType, 
  onAnalysisResult, 
  onLandmarksUpdate,
  userProfile 
}: PoseAnalyzerEnhancedProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const poseRef = useRef<Pose | null>(null)
  const cameraRef = useRef<Camera | null>(null)
  
  const [isRecording, setIsRecording] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showCameraGuide, setShowCameraGuide] = useState(true)
  const [cameraSetupComplete, setCameraSetupComplete] = useState(false)
  const [currentAnalysis, setCurrentAnalysis] = useState<AnalysisResult | null>(null)
  const [landmarks, setLandmarks] = useState<any[]>([])
  const [modelMode, setModelMode] = useState<string>('lite')
  
  const frameCountRef = useRef(0)
  const recordedFrames = useRef<any[]>([])

  // Get model mode from environment or localStorage
  useEffect(() => {
    const envMode = process.env.NEXT_PUBLIC_MODEL_MODE || 'lite'
    const storedMode = localStorage.getItem('modelMode') || envMode
    setModelMode(storedMode)
  }, [])

  // MediaPipe results processing with enhanced analysis
  const onResults = useCallback(async (results: Results) => {
    if (!canvasRef.current || !videoRef.current) return

    const canvasCtx = canvasRef.current.getContext('2d')
    if (!canvasCtx) return

    // Clear canvas
    canvasCtx.save()
    canvasCtx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height)

    // Draw video frame
    canvasCtx.drawImage(results.image, 0, 0, canvasRef.current.width, canvasRef.current.height)

    // If landmarks detected
    if (results.poseLandmarks) {
      // Update landmarks for camera guide
      setLandmarks(results.poseLandmarks)
      
      // Draw pose visualization with confidence-based colors
      const avgConfidence = results.poseLandmarks.reduce((sum, lm) => sum + (lm.visibility || 0), 0) / results.poseLandmarks.length
      const color = avgConfidence > 0.8 ? '#00FF00' : avgConfidence > 0.6 ? '#FFFF00' : '#FF0000'
      
      drawConnectors(canvasCtx, results.poseLandmarks, POSE_CONNECTIONS, {
        color: color,
        lineWidth: 4,
      })
      
      drawLandmarks(canvasCtx, results.poseLandmarks, {
        color: color,
        lineWidth: 2,
        radius: 6,
      })

      // Convert landmarks to API format
      const landmarksArray = results.poseLandmarks.map((landmark, index) => ({
        landmark_id: index,
        x: landmark.x,
        y: landmark.y,
        z: landmark.z,
        visibility: landmark.visibility || 0
      }))

      // Update parent component
      if (onLandmarksUpdate) {
        onLandmarksUpdate(landmarksArray)
      }

      // Record frames if recording
      if (isRecording) {
        recordedFrames.current.push({
          frame: frameCountRef.current++,
          landmarks: landmarksArray,
          timestamp: new Date().toISOString()
        })
      }

      // Send to enhanced analysis API
      if (cameraSetupComplete && frameCountRef.current % 10 === 0) { // Analyze every 10 frames
        try {
          const response = await fetch('/api/analyze/enhanced', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              landmarks: landmarksArray,
              exercise_type: exerciseType,
              frame_number: frameCountRef.current,
              model_mode: modelMode,
              user_profile: userProfile,
              // Include recent frames for temporal analysis
              landmark_sequence: recordedFrames.current.slice(-30).map(f => f.landmarks)
            })
          })

          if (response.ok) {
            const analysisResult = await response.json()
            setCurrentAnalysis(analysisResult)
            if (onAnalysisResult) {
              onAnalysisResult(analysisResult)
            }
          }
        } catch (err) {
          console.error('Enhanced analysis error:', err)
          // Fall back to basic analysis
          try {
            const basicResponse = await fetch('/api/analyze', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                landmarks: landmarksArray,
                exercise_type: exerciseType,
                frame_number: frameCountRef.current
              })
            })

            if (basicResponse.ok) {
              const basicResult = await basicResponse.json()
              setCurrentAnalysis(basicResult)
              if (onAnalysisResult) {
                onAnalysisResult(basicResult)
              }
            }
          } catch (basicErr) {
            console.error('Basic analysis error:', basicErr)
          }
        }
      }
    }

    canvasCtx.restore()
  }, [exerciseType, isRecording, onAnalysisResult, onLandmarksUpdate, cameraSetupComplete, modelMode, userProfile])

  // Initialize MediaPipe
  useEffect(() => {
    const initializePose = async () => {
      try {
        setIsLoading(true)
        setError(null)

        if (!videoRef.current || !canvasRef.current) {
          throw new Error('Video or canvas element not found')
        }

        // Create Pose instance
        const pose = new Pose({
          locateFile: (file) => {
            return `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`
          },
        })

        // Configure Pose with enhanced settings
        pose.setOptions({
          modelComplexity: modelMode === 'advanced' ? 2 : 1,
          smoothLandmarks: true,
          enableSegmentation: false,
          smoothSegmentation: false,
          minDetectionConfidence: 0.7,
          minTrackingConfidence: 0.7,
        })

        pose.onResults(onResults)
        poseRef.current = pose

        // Initialize camera
        const camera = new Camera(videoRef.current, {
          onFrame: async () => {
            if (poseRef.current && videoRef.current) {
              await poseRef.current.send({ image: videoRef.current })
            }
          },
          width: 1280,
          height: 720,
        })

        cameraRef.current = camera
        await camera.start()
        
        setIsLoading(false)
      } catch (err) {
        console.error('Initialization error:', err)
        setError(err instanceof Error ? err.message : 'Failed to initialize camera')
        setIsLoading(false)
      }
    }

    initializePose()

    // Cleanup
    return () => {
      if (cameraRef.current) {
        cameraRef.current.stop()
      }
      if (poseRef.current) {
        poseRef.current.close()
      }
    }
  }, [onResults, modelMode])

  // Toggle recording
  const toggleRecording = () => {
    if (isRecording) {
      // Stop recording
      setIsRecording(false)
      console.log(`Recording stopped: ${recordedFrames.current.length} frames saved`)
      
      // Save to localStorage
      const recordingData = {
        exerciseType,
        totalFrames: recordedFrames.current.length,
        frames: recordedFrames.current,
        modelMode,
        recordedAt: new Date().toISOString()
      }
      localStorage.setItem('lastRecording', JSON.stringify(recordingData))
      
      // Reset for next recording
      recordedFrames.current = []
      frameCountRef.current = 0
    } else {
      // Start recording
      recordedFrames.current = []
      frameCountRef.current = 0
      setIsRecording(true)
      console.log('Recording started')
    }
  }

  // Reset analysis
  const resetAnalysis = () => {
    setCurrentAnalysis(null)
    recordedFrames.current = []
    frameCountRef.current = 0
    setIsRecording(false)
  }

  const getFeedbackIcon = (priority: string) => {
    switch (priority) {
      case 'critical':
        return <AlertCircle className="w-4 h-4 text-red-500" />
      case 'warning':
        return <AlertCircle className="w-4 h-4 text-yellow-500" />
      default:
        return <Info className="w-4 h-4 text-blue-500" />
    }
  }

  const getFeedbackBadgeVariant = (priority: string): "default" | "secondary" | "destructive" | "outline" => {
    switch (priority) {
      case 'critical':
        return 'destructive'
      case 'warning':
        return 'secondary'
      default:
        return 'default'
    }
  }

  return (
    <div className="space-y-4">
      {/* Camera Guide */}
      {showCameraGuide && !cameraSetupComplete && (
        <CameraGuide
          landmarks={landmarks}
          exerciseType={exerciseType}
          onGuideComplete={() => {
            setCameraSetupComplete(true)
            setTimeout(() => setShowCameraGuide(false), 2000)
          }}
        />
      )}

      {/* Main Analysis View */}
      <div className="grid gap-4 lg:grid-cols-3">
        {/* Video Feed */}
        <div className="lg:col-span-2">
          <Card className="relative overflow-hidden">
            {/* Loading overlay */}
            {isLoading && (
              <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center z-20">
                <div className="text-white text-lg">カメラを初期化中...</div>
              </div>
            )}

            {/* Error display */}
            {error && (
              <Alert variant="destructive" className="absolute top-4 left-4 right-4 z-20">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {/* Video and canvas */}
            <div className="relative aspect-video bg-gray-900">
              <video
                ref={videoRef}
                className="absolute inset-0 w-full h-full object-cover"
                playsInline
                muted
              />
              <canvas
                ref={canvasRef}
                className="absolute inset-0 w-full h-full"
                width={1280}
                height={720}
              />

              {/* Recording indicator */}
              {isRecording && (
                <div className="absolute top-4 left-4 flex items-center space-x-2 bg-red-600 text-white px-3 py-1.5 rounded-full">
                  <div className="w-3 h-3 bg-white rounded-full animate-pulse" />
                  <span className="text-sm font-medium">録画中</span>
                </div>
              )}

              {/* Exercise type badge */}
              <Badge className="absolute top-4 right-4">
                {exerciseType === 'squat' && 'スクワット'}
                {exerciseType === 'bench_press' && 'ベンチプレス'}
                {exerciseType === 'deadlift' && 'デッドリフト'}
              </Badge>

              {/* Model mode indicator */}
              <div className="absolute bottom-4 right-4 bg-black bg-opacity-50 text-white px-2 py-1 rounded text-xs">
                {modelMode === 'advanced' ? 'Advanced Mode' : 'Lite Mode'}
              </div>
            </div>

            {/* Control buttons */}
            <div className="p-4 bg-gray-50 flex items-center justify-between">
              <div className="flex gap-2">
                <Button
                  onClick={toggleRecording}
                  variant={isRecording ? 'destructive' : 'default'}
                  disabled={isLoading || !!error || !cameraSetupComplete}
                >
                  {isRecording ? (
                    <>
                      <Pause className="w-4 h-4 mr-2" />
                      停止
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4 mr-2" />
                      録画開始
                    </>
                  )}
                </Button>
                
                <Button
                  onClick={resetAnalysis}
                  variant="outline"
                  disabled={isLoading || isRecording}
                >
                  <RotateCcw className="w-4 h-4 mr-2" />
                  リセット
                </Button>
              </div>

              <Button
                onClick={() => setShowCameraGuide(!showCameraGuide)}
                variant="ghost"
                size="sm"
              >
                <Settings className="w-4 h-4 mr-2" />
                カメラ設定
              </Button>
            </div>
          </Card>
        </div>

        {/* Real-time Analysis Panel */}
        <div className="space-y-4">
          {/* Score Card */}
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">フォーム分析</h3>
              
              {currentAnalysis ? (
                <div className="space-y-4">
                  {/* Overall Score */}
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span>総合スコア</span>
                      <span className="font-bold">{currentAnalysis.score}%</span>
                    </div>
                    <Progress value={currentAnalysis.score} className="h-3" />
                  </div>

                  {/* Confidence */}
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span>検出信頼度</span>
                      <span>{Math.round(currentAnalysis.confidence * 100)}%</span>
                    </div>
                    <Progress 
                      value={currentAnalysis.confidence * 100} 
                      className="h-2"
                    />
                  </div>

                  {/* Phase */}
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">フェーズ</span>
                    <Badge variant="outline">{currentAnalysis.phase}</Badge>
                  </div>

                  {/* Processing Time */}
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>処理時間</span>
                    <span>{(currentAnalysis.processing_time * 1000).toFixed(0)}ms</span>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  {cameraSetupComplete ? '分析待機中...' : 'カメラセットアップを完了してください'}
                </div>
              )}
            </div>
          </Card>

          {/* Feedback Card */}
          <Card>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">リアルタイムフィードバック</h3>
              
              {currentAnalysis && currentAnalysis.feedback.length > 0 ? (
                <div className="space-y-3">
                  {currentAnalysis.feedback.map((item, index) => (
                    <div key={index} className="flex items-start gap-3">
                      {getFeedbackIcon(item.priority)}
                      <div className="flex-1">
                        <p className="text-sm">{item.message}</p>
                        {item.joint && (
                          <Badge 
                            variant={getFeedbackBadgeVariant(item.priority)}
                            className="mt-1"
                            size="sm"
                          >
                            {item.joint}
                          </Badge>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground text-center py-4">
                  フィードバックはここに表示されます
                </p>
              )}
            </div>
          </Card>

          {/* Joint Angles (if available) */}
          {currentAnalysis && currentAnalysis.angle_scores && (
            <Card>
              <div className="p-6">
                <h3 className="text-lg font-semibold mb-4">関節角度</h3>
                <div className="space-y-3">
                  {Object.entries(currentAnalysis.angle_scores).map(([joint, data]: [string, any]) => (
                    <div key={joint}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="capitalize">{joint}</span>
                        <span className={`font-medium ${
                          data.status === 'good' ? 'text-green-600' :
                          data.status === 'warning' ? 'text-yellow-600' :
                          'text-red-600'
                        }`}>
                          {data.angle}° / {data.ideal}°
                        </span>
                      </div>
                      <Progress 
                        value={data.score * 100} 
                        className="h-2"
                      />
                    </div>
                  ))}
                </div>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}