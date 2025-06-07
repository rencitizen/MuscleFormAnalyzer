'use client'

import { useEffect, useState } from 'react'
import { Card } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Progress } from '@/components/ui/progress'
import { 
  Camera, 
  Move, 
  RotateCw, 
  Check, 
  X, 
  AlertTriangle,
  Smartphone,
  Monitor,
  ZoomIn,
  ZoomOut
} from 'lucide-react'

interface CameraGuideProps {
  landmarks?: any[]
  exerciseType: string
  onGuideComplete?: () => void
}

interface CameraStatus {
  position: 'too_close' | 'too_far' | 'good' | 'off_center'
  angle: 'too_high' | 'too_low' | 'tilted' | 'good'
  visibility: 'full' | 'partial' | 'poor'
  confidence: number
}

export function CameraGuide({ landmarks, exerciseType, onGuideComplete }: CameraGuideProps) {
  const [cameraStatus, setCameraStatus] = useState<CameraStatus>({
    position: 'good',
    angle: 'good',
    visibility: 'full',
    confidence: 0
  })
  const [device, setDevice] = useState<'mobile' | 'desktop'>('desktop')

  useEffect(() => {
    // Detect device type
    const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent)
    setDevice(isMobile ? 'mobile' : 'desktop')
  }, [])

  useEffect(() => {
    if (!landmarks || landmarks.length === 0) return

    // Analyze camera position and angle
    const status = analyzeCameraSetup(landmarks, exerciseType)
    setCameraStatus(status)

    // Notify when guide is complete
    if (status.position === 'good' && status.angle === 'good' && status.visibility === 'full') {
      onGuideComplete?.()
    }
  }, [landmarks, exerciseType, onGuideComplete])

  const analyzeCameraSetup = (landmarks: any[], exercise: string): CameraStatus => {
    // Count visible landmarks
    const visibleCount = landmarks.filter(lm => lm.visibility > 0.5).length
    const totalLandmarks = landmarks.length
    const visibilityRatio = visibleCount / totalLandmarks

    // Calculate bounding box
    const visibleLandmarks = landmarks.filter(lm => lm.visibility > 0.5)
    const xs = visibleLandmarks.map(lm => lm.x)
    const ys = visibleLandmarks.map(lm => lm.y)
    
    const minX = Math.min(...xs)
    const maxX = Math.max(...xs)
    const minY = Math.min(...ys)
    const maxY = Math.max(...ys)
    
    const width = maxX - minX
    const height = maxY - minY
    const centerX = (minX + maxX) / 2
    const centerY = (minY + maxY) / 2

    // Determine position status
    let position: CameraStatus['position'] = 'good'
    if (width < 0.3 || height < 0.4) {
      position = 'too_far'
    } else if (width > 0.8 || height > 0.9) {
      position = 'too_close'
    } else if (Math.abs(centerX - 0.5) > 0.2) {
      position = 'off_center'
    }

    // Determine angle status based on exercise
    let angle: CameraStatus['angle'] = 'good'
    const shoulderHipRatio = calculateShoulderHipRatio(landmarks)
    
    if (exercise === 'squat' || exercise === 'deadlift') {
      // Side view is preferred
      if (shoulderHipRatio < 0.7) {
        angle = 'tilted'
      }
    } else if (exercise === 'bench_press') {
      // Different angle requirements for bench press
      if (centerY < 0.3) {
        angle = 'too_high'
      } else if (centerY > 0.7) {
        angle = 'too_low'
      }
    }

    // Determine visibility
    let visibility: CameraStatus['visibility'] = 'full'
    if (visibilityRatio < 0.7) {
      visibility = 'poor'
    } else if (visibilityRatio < 0.85) {
      visibility = 'partial'
    }

    // Calculate overall confidence
    let confidence = visibilityRatio
    if (position === 'good') confidence += 0.2
    if (angle === 'good') confidence += 0.2
    confidence = Math.min(confidence, 1.0)

    return { position, angle, visibility, confidence: confidence * 100 }
  }

  const calculateShoulderHipRatio = (landmarks: any[]): number => {
    // MediaPipe indices
    const LEFT_SHOULDER = 11
    const RIGHT_SHOULDER = 12
    const LEFT_HIP = 23
    const RIGHT_HIP = 24

    if (landmarks.length < 33) return 1

    const shoulderWidth = Math.abs(landmarks[LEFT_SHOULDER].x - landmarks[RIGHT_SHOULDER].x)
    const hipWidth = Math.abs(landmarks[LEFT_HIP].x - landmarks[RIGHT_HIP].x)

    return hipWidth > 0 ? shoulderWidth / hipWidth : 1
  }

  const getPositionAdvice = () => {
    switch (cameraStatus.position) {
      case 'too_close':
        return {
          icon: <ZoomOut className="w-5 h-5" />,
          message: 'カメラから離れてください',
          detail: '全身が画面に収まるように調整してください'
        }
      case 'too_far':
        return {
          icon: <ZoomIn className="w-5 h-5" />,
          message: 'カメラに近づいてください',
          detail: '体がはっきり見えるように近づいてください'
        }
      case 'off_center':
        return {
          icon: <Move className="w-5 h-5" />,
          message: '中央に移動してください',
          detail: '画面の中央に立ってください'
        }
      default:
        return {
          icon: <Check className="w-5 h-5 text-green-500" />,
          message: '位置OK',
          detail: '適切な距離です'
        }
    }
  }

  const getAngleAdvice = () => {
    const deviceSpecific = device === 'mobile' 
      ? 'スマートフォンを胸の高さに設置してください' 
      : 'カメラを胸の高さに調整してください'

    switch (cameraStatus.angle) {
      case 'too_high':
        return {
          icon: <RotateCw className="w-5 h-5" />,
          message: 'カメラ位置が高すぎます',
          detail: deviceSpecific
        }
      case 'too_low':
        return {
          icon: <RotateCw className="w-5 h-5" />,
          message: 'カメラ位置が低すぎます',
          detail: deviceSpecific
        }
      case 'tilted':
        return {
          icon: <RotateCw className="w-5 h-5" />,
          message: '横から撮影してください',
          detail: exerciseType === 'squat' ? 'スクワットは横からの撮影が最適です' : '横向きで撮影してください'
        }
      default:
        return {
          icon: <Check className="w-5 h-5 text-green-500" />,
          message: '角度OK',
          detail: '適切な角度です'
        }
    }
  }

  const isSetupComplete = cameraStatus.position === 'good' && 
                          cameraStatus.angle === 'good' && 
                          cameraStatus.visibility === 'full'

  return (
    <div className="space-y-4">
      {/* Setup Status Overview */}
      <Card className="p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <Camera className="w-5 h-5" />
            カメラセットアップ
          </h3>
          <div className="flex items-center gap-2">
            {device === 'mobile' ? <Smartphone className="w-4 h-4" /> : <Monitor className="w-4 h-4" />}
            <span className="text-sm text-muted-foreground">
              {device === 'mobile' ? 'モバイル' : 'デスクトップ'}
            </span>
          </div>
        </div>

        {/* Confidence Score */}
        <div className="mb-4">
          <div className="flex justify-between text-sm mb-1">
            <span>検出精度</span>
            <span className="font-medium">{Math.round(cameraStatus.confidence)}%</span>
          </div>
          <Progress value={cameraStatus.confidence} className="h-2" />
        </div>

        {/* Setup Checklist */}
        <div className="space-y-3">
          {/* Position Check */}
          <div className="flex items-start gap-3">
            {getPositionAdvice().icon}
            <div className="flex-1">
              <p className="font-medium text-sm">{getPositionAdvice().message}</p>
              <p className="text-xs text-muted-foreground">{getPositionAdvice().detail}</p>
            </div>
          </div>

          {/* Angle Check */}
          <div className="flex items-start gap-3">
            {getAngleAdvice().icon}
            <div className="flex-1">
              <p className="font-medium text-sm">{getAngleAdvice().message}</p>
              <p className="text-xs text-muted-foreground">{getAngleAdvice().detail}</p>
            </div>
          </div>

          {/* Visibility Check */}
          <div className="flex items-start gap-3">
            {cameraStatus.visibility === 'full' ? (
              <Check className="w-5 h-5 text-green-500" />
            ) : cameraStatus.visibility === 'partial' ? (
              <AlertTriangle className="w-5 h-5 text-yellow-500" />
            ) : (
              <X className="w-5 h-5 text-red-500" />
            )}
            <div className="flex-1">
              <p className="font-medium text-sm">
                {cameraStatus.visibility === 'full' ? '全身が見えています' :
                 cameraStatus.visibility === 'partial' ? '一部が見えにくいです' :
                 '体が十分に見えません'}
              </p>
              <p className="text-xs text-muted-foreground">
                {cameraStatus.visibility === 'full' ? '検出精度が最適です' :
                 '明るい場所で、無地の背景を推奨します'}
              </p>
            </div>
          </div>
        </div>
      </Card>

      {/* Exercise-specific tips */}
      {!isSetupComplete && (
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            <strong>{exerciseType === 'squat' ? 'スクワット' : 
                     exerciseType === 'bench_press' ? 'ベンチプレス' : 
                     'デッドリフト'}のコツ:</strong>
            <ul className="mt-2 space-y-1 text-sm">
              {exerciseType === 'squat' && (
                <>
                  <li>• 真横から撮影すると膝と腰の角度が正確に測定できます</li>
                  <li>• カメラは腰の高さに設置するのが理想的です</li>
                  <li>• 2-3m離れて全身が映るようにしてください</li>
                </>
              )}
              {exerciseType === 'bench_press' && (
                <>
                  <li>• 斜め45度から撮影すると腕の動きがよく見えます</li>
                  <li>• ベンチの横にカメラを設置してください</li>
                  <li>• 上半身全体が映るように調整してください</li>
                </>
              )}
              {exerciseType === 'deadlift' && (
                <>
                  <li>• 真横から撮影すると背中の角度が正確に測定できます</li>
                  <li>• カメラは膝の高さに設置するのが理想的です</li>
                  <li>• バーベルと体全体が映るようにしてください</li>
                </>
              )}
            </ul>
          </AlertDescription>
        </Alert>
      )}

      {/* Success Message */}
      {isSetupComplete && (
        <Alert className="border-green-200 bg-green-50">
          <Check className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">
            カメラセットアップ完了！分析を開始できます。
          </AlertDescription>
        </Alert>
      )}
    </div>
  )
}