'use client'

import React, { useState, useRef, useEffect, useCallback } from 'react'
import { 
  heightMeasurementSystem, 
  UserCalibrationSystem,
  type StableHeightResult 
} from '@/lib/mediapipe/improvedHeightMeasurement'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Progress } from '@/components/ui/progress'
import { 
  Camera, 
  Video, 
  Upload, 
  Ruler, 
  Check, 
  AlertCircle, 
  RefreshCw,
  User,
  Activity
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface CalibrationStep {
  id: string
  instruction: string
  completed: boolean
  validation?: (landmarks: any) => boolean
  input?: {
    type: string
    placeholder: string
    unit: string
    min: number
    max: number
  }
}

export function ImprovedHeightMeasurement() {
  const [mode, setMode] = useState<'camera' | 'upload' | 'calibration'>('camera')
  const [isProcessing, setIsProcessing] = useState(false)
  const [result, setResult] = useState<StableHeightResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [stream, setStream] = useState<MediaStream | null>(null)
  const [calibrationSteps, setCalibrationSteps] = useState<CalibrationStep[]>([])
  const [currentStepIndex, setCurrentStepIndex] = useState(0)
  const [userHeight, setUserHeight] = useState<string>('')
  const [measurementHistory, setMeasurementHistory] = useState<number[]>([])
  
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const animationFrameRef = useRef<number | null>(null)

  // Initialize height measurement system
  useEffect(() => {
    const initSystem = async () => {
      try {
        await heightMeasurementSystem.initialize()
      } catch (error) {
        console.error('Failed to initialize height measurement:', error)
        setError('システムの初期化に失敗しました')
      }
    }
    initSystem()

    return () => {
      heightMeasurementSystem.cleanup()
    }
  }, [])

  // Initialize calibration steps
  useEffect(() => {
    const steps = UserCalibrationSystem.createCalibrationSteps().map(step => ({
      ...step,
      completed: false
    }))
    setCalibrationSteps(steps)
  }, [])

  // Start camera stream
  const startCamera = useCallback(async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'user'
        }
      })
      
      setStream(mediaStream)
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream
      }
      
      setError(null)
    } catch (error) {
      console.error('Camera access error:', error)
      setError('カメラへのアクセスが拒否されました')
    }
  }, [])

  // Stop camera stream
  const stopCamera = useCallback(() => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop())
      setStream(null)
    }
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current)
      animationFrameRef.current = null
    }
  }, [stream])

  // Process video frame
  const processFrame = useCallback(async () => {
    if (!videoRef.current || !videoRef.current.readyState === 4) {
      animationFrameRef.current = requestAnimationFrame(processFrame)
      return
    }

    setIsProcessing(true)

    try {
      const result = await heightMeasurementSystem.measureHeight(
        videoRef.current,
        mode === 'calibration' && userHeight ? parseFloat(userHeight) : null
      )

      setResult(result)

      // Update measurement history
      if (result.stableHeight) {
        setMeasurementHistory(prev => [...prev.slice(-9), result.stableHeight!])
      }

      // Handle calibration mode
      if (mode === 'calibration' && currentStepIndex < calibrationSteps.length - 1) {
        const currentStep = calibrationSteps[currentStepIndex]
        if (currentStep.validation && videoRef.current) {
          // Validation logic would go here
          // For now, we'll simulate completion after a few frames
          setTimeout(() => {
            const updatedSteps = [...calibrationSteps]
            updatedSteps[currentStepIndex].completed = true
            setCalibrationSteps(updatedSteps)
            if (currentStepIndex < calibrationSteps.length - 1) {
              setCurrentStepIndex(currentStepIndex + 1)
            }
          }, 2000)
        }
      }
    } catch (error) {
      console.error('Height measurement error:', error)
      setError('測定中にエラーが発生しました')
    }

    setIsProcessing(false)
    animationFrameRef.current = requestAnimationFrame(processFrame)
  }, [mode, userHeight, currentStepIndex, calibrationSteps])

  // Handle mode changes
  useEffect(() => {
    if (mode === 'camera' || mode === 'calibration') {
      startCamera()
    } else {
      stopCamera()
    }

    return () => {
      stopCamera()
    }
  }, [mode, startCamera, stopCamera])

  // Start processing when camera is ready
  useEffect(() => {
    if (stream && videoRef.current) {
      videoRef.current.onloadedmetadata = () => {
        processFrame()
      }
    }
  }, [stream, processFrame])

  // Handle file upload
  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    setIsProcessing(true)
    setError(null)

    try {
      const video = document.createElement('video')
      video.src = URL.createObjectURL(file)
      video.muted = true

      video.onloadedmetadata = async () => {
        const measurements: StableHeightResult[] = []
        const totalFrames = Math.min(30, video.duration * 5)
        
        for (let i = 0; i < totalFrames; i++) {
          video.currentTime = (i / totalFrames) * video.duration
          await new Promise(resolve => {
            video.onseeked = resolve
          })

          const result = await heightMeasurementSystem.measureHeight(video)
          measurements.push(result)
        }

        // Find the most stable measurement
        const bestResult = measurements.reduce((best, current) => 
          current.confidence > best.confidence ? current : best
        )

        setResult(bestResult)
        setIsProcessing(false)
      }

      video.onerror = () => {
        setError('動画の読み込みに失敗しました')
        setIsProcessing(false)
      }
    } catch (error) {
      console.error('Video processing error:', error)
      setError('動画処理中にエラーが発生しました')
      setIsProcessing(false)
    }
  }

  // Handle calibration completion
  const completeCalibration = () => {
    if (userHeight && parseFloat(userHeight) >= 50 && parseFloat(userHeight) <= 250) {
      setMode('camera')
      setCurrentStepIndex(0)
    }
  }

  // Reset measurement
  const resetMeasurement = () => {
    heightMeasurementSystem.reset()
    setResult(null)
    setMeasurementHistory([])
    setUserHeight('')
    setError(null)
  }

  return (
    <div className="max-w-4xl mx-auto p-4 space-y-4">
      {/* Mode Selection */}
      <Card>
        <CardHeader>
          <CardTitle>身長測定モード選択</CardTitle>
          <CardDescription>
            測定方法を選択してください
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4">
            <Button
              variant={mode === 'camera' ? 'default' : 'outline'}
              onClick={() => setMode('camera')}
              className="h-24 flex flex-col gap-2"
            >
              <Camera className="h-6 w-6" />
              <span>カメラ測定</span>
            </Button>
            <Button
              variant={mode === 'upload' ? 'default' : 'outline'}
              onClick={() => setMode('upload')}
              className="h-24 flex flex-col gap-2"
            >
              <Video className="h-6 w-6" />
              <span>動画アップロード</span>
            </Button>
            <Button
              variant={mode === 'calibration' ? 'default' : 'outline'}
              onClick={() => setMode('calibration')}
              className="h-24 flex flex-col gap-2"
            >
              <Ruler className="h-6 w-6" />
              <span>較正モード</span>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Calibration Mode */}
      {mode === 'calibration' && (
        <Card>
          <CardHeader>
            <CardTitle>測定システムの較正</CardTitle>
            <CardDescription>
              より正確な測定のため、以下の手順に従ってください
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {calibrationSteps.map((step, index) => (
                <div
                  key={step.id}
                  className={cn(
                    "p-4 rounded-lg border transition-all",
                    index === currentStepIndex ? "border-primary bg-primary/5" : "border-gray-200",
                    step.completed && "bg-green-50 border-green-500"
                  )}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={cn(
                        "w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold",
                        step.completed ? "bg-green-500 text-white" : 
                        index === currentStepIndex ? "bg-primary text-primary-foreground" :
                        "bg-gray-200 text-gray-600"
                      )}>
                        {step.completed ? <Check className="h-4 w-4" /> : index + 1}
                      </div>
                      <p className="font-medium">{step.instruction}</p>
                    </div>
                  </div>
                  
                  {step.input && index === currentStepIndex && (
                    <div className="mt-4 flex gap-2">
                      <Input
                        type={step.input.type}
                        placeholder={step.input.placeholder}
                        value={userHeight}
                        onChange={(e) => setUserHeight(e.target.value)}
                        min={step.input.min}
                        max={step.input.max}
                        className="w-32"
                      />
                      <span className="flex items-center text-muted-foreground">
                        {step.input.unit}
                      </span>
                      <Button
                        onClick={completeCalibration}
                        disabled={!userHeight || parseFloat(userHeight) < 50 || parseFloat(userHeight) > 250}
                      >
                        較正完了
                      </Button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Video Display */}
      {(mode === 'camera' || mode === 'calibration') && (
        <Card>
          <CardContent className="p-0">
            <div className="relative aspect-video bg-black rounded-lg overflow-hidden">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="w-full h-full object-contain"
              />
              <canvas
                ref={canvasRef}
                className="absolute inset-0 w-full h-full"
              />
              {isProcessing && (
                <div className="absolute top-4 right-4 bg-black/50 text-white px-3 py-1 rounded-full flex items-center gap-2">
                  <Activity className="h-4 w-4 animate-pulse" />
                  <span className="text-sm">処理中...</span>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* File Upload */}
      {mode === 'upload' && (
        <Card>
          <CardContent className="p-8">
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
              <input
                ref={fileInputRef}
                type="file"
                accept="video/*"
                onChange={handleFileUpload}
                className="hidden"
              />
              <Upload className="h-12 w-12 mx-auto text-gray-400 mb-4" />
              <p className="text-lg font-medium mb-2">動画をアップロード</p>
              <p className="text-sm text-muted-foreground mb-4">
                全身が映った動画を選択してください
              </p>
              <Button
                onClick={() => fileInputRef.current?.click()}
                disabled={isProcessing}
              >
                ファイルを選択
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Results */}
      {result && (
        <Card>
          <CardHeader>
            <CardTitle>測定結果</CardTitle>
            <CardDescription>
              AIによる身長推定結果
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Current and Stable Height */}
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-muted-foreground mb-1">現在の測定値</p>
                  <p className="text-3xl font-bold">{result.currentHeight} cm</p>
                </div>
                <div className="text-center p-4 bg-primary/10 rounded-lg">
                  <p className="text-sm text-muted-foreground mb-1">安定測定値</p>
                  <p className="text-3xl font-bold">
                    {result.stableHeight ? `${result.stableHeight} cm` : '計測中...'}
                  </p>
                </div>
              </div>

              {/* Confidence */}
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm font-medium">測定精度</span>
                  <span className="text-sm text-muted-foreground">
                    {Math.round(result.confidence * 100)}%
                  </span>
                </div>
                <Progress value={result.confidence * 100} className="h-2" />
              </div>

              {/* Calibration Status */}
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="text-sm font-medium">較正状態</span>
                <span className={cn(
                  "text-sm font-medium",
                  result.calibrationStatus === 'calibrated' ? "text-green-600" :
                  result.calibrationStatus === 'calibrating' ? "text-yellow-600" :
                  "text-gray-600"
                )}>
                  {result.calibrationStatus === 'calibrated' ? '較正済み' :
                   result.calibrationStatus === 'calibrating' ? '較正中' :
                   '未較正'}
                </span>
              </div>

              {/* Measurement History */}
              {measurementHistory.length > 0 && (
                <div>
                  <p className="text-sm font-medium mb-2">測定履歴</p>
                  <div className="flex gap-2 items-end">
                    {measurementHistory.map((height, index) => (
                      <div
                        key={index}
                        className="flex-1 bg-primary/20 rounded"
                        style={{
                          height: `${(height / Math.max(...measurementHistory)) * 60}px`
                        }}
                      />
                    ))}
                  </div>
                </div>
              )}

              {/* Recommendations */}
              {result.recommendations.length > 0 && (
                <Alert>
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    <ul className="list-disc list-inside space-y-1">
                      {result.recommendations.map((rec, index) => (
                        <li key={index}>{rec}</li>
                      ))}
                    </ul>
                  </AlertDescription>
                </Alert>
              )}

              {/* Actions */}
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  onClick={resetMeasurement}
                  className="flex-1"
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  再測定
                </Button>
                <Button
                  variant="default"
                  onClick={() => {
                    // Save measurement logic
                    console.log('Saving measurement:', result.stableHeight || result.currentHeight)
                  }}
                  disabled={!result.stableHeight}
                  className="flex-1"
                >
                  測定値を保存
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Error Display */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Instructions */}
      <Card>
        <CardHeader>
          <CardTitle>測定のコツ</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2 text-sm text-muted-foreground">
            <li className="flex items-start gap-2">
              <User className="h-4 w-4 mt-0.5" />
              <span>カメラから2-3メートル離れて、全身が映るようにしてください</span>
            </li>
            <li className="flex items-start gap-2">
              <User className="h-4 w-4 mt-0.5" />
              <span>壁に背中をつけて、背筋を伸ばして直立してください</span>
            </li>
            <li className="flex items-start gap-2">
              <User className="h-4 w-4 mt-0.5" />
              <span>明るい場所で、無地の背景がおすすめです</span>
            </li>
            <li className="flex items-start gap-2">
              <Ruler className="h-4 w-4 mt-0.5" />
              <span>より正確な測定のため、較正モードで実際の身長を入力してください</span>
            </li>
          </ul>
        </CardContent>
      </Card>
    </div>
  )
}