'use client'

import React, { useRef, useState, useEffect, useCallback } from 'react'
import { Button } from '../ui/button'
import { Card, CardContent } from '../ui/card'
import { Camera, CameraOff, SwitchCamera, Upload, X, AlertCircle } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'

interface CameraCaptureProps {
  onCapture: (imageData: string, file: File) => void
  onClose?: () => void
  aspectRatio?: string
  maxWidth?: number
  maxHeight?: number
}

export function CameraCapture({ 
  onCapture, 
  onClose,
  aspectRatio = '4/3',
  maxWidth = 800,
  maxHeight = 600
}: CameraCaptureProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  
  const [stream, setStream] = useState<MediaStream | null>(null)
  const [isCapturing, setIsCapturing] = useState(false)
  const [facingMode, setFacingMode] = useState<'user' | 'environment'>('environment')
  const [hasPermission, setHasPermission] = useState<boolean | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [devices, setDevices] = useState<MediaDeviceInfo[]>([])
  const [isHttps, setIsHttps] = useState(true)
  
  const { toast } = useToast()

  // Check if running on HTTPS
  useEffect(() => {
    const isSecure = window.location.protocol === 'https:' || 
                     window.location.hostname === 'localhost' || 
                     window.location.hostname === '127.0.0.1'
    setIsHttps(isSecure)
    
    if (!isSecure) {
      setError('カメラを使用するにはHTTPS接続が必要です')
    }
  }, [])

  // Get available camera devices
  const getDevices = useCallback(async () => {
    try {
      const deviceList = await navigator.mediaDevices.enumerateDevices()
      const videoDevices = deviceList.filter(device => device.kind === 'videoinput')
      setDevices(videoDevices)
      
      // Log for debugging
      console.log('Available camera devices:', videoDevices.length)
      videoDevices.forEach((device, index) => {
        console.log(`Camera ${index}: ${device.label || 'Unknown'} (${device.deviceId})`)
      })
    } catch (err) {
      console.error('Failed to enumerate devices:', err)
    }
  }, [])

  // Initialize camera
  const initCamera = useCallback(async () => {
    if (!isHttps) {
      setError('HTTPS接続が必要です')
      return
    }

    try {
      setError(null)
      setIsCapturing(true)
      
      // Stop any existing stream
      if (stream) {
        stream.getTracks().forEach(track => track.stop())
      }

      // Camera constraints
      const constraints: MediaStreamConstraints = {
        video: {
          facingMode: facingMode,
          width: { ideal: maxWidth },
          height: { ideal: maxHeight }
        },
        audio: false
      }

      // Try to get camera access
      const mediaStream = await navigator.mediaDevices.getUserMedia(constraints)
      
      setStream(mediaStream)
      setHasPermission(true)
      
      // Set video source
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream
      }
      
      // Get devices after permission granted
      await getDevices()
      
      toast({
        title: 'カメラ起動成功',
        description: 'カメラの準備ができました',
      })
    } catch (err: any) {
      console.error('Camera error:', err)
      setHasPermission(false)
      
      let errorMessage = 'カメラの起動に失敗しました'
      
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        errorMessage = 'カメラの使用許可が必要です。ブラウザの設定から許可してください。'
      } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        errorMessage = 'カメラが見つかりません。デバイスが接続されているか確認してください。'
      } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
        errorMessage = 'カメラが他のアプリで使用中の可能性があります。'
      } else if (err.name === 'OverconstrainedError' || err.name === 'ConstraintNotSatisfiedError') {
        errorMessage = 'カメラの設定に問題があります。'
      } else if (err.name === 'TypeError') {
        errorMessage = 'お使いのブラウザはカメラ機能に対応していません。'
      }
      
      setError(errorMessage)
      setIsCapturing(false)
      
      toast({
        title: 'カメラエラー',
        description: errorMessage,
        variant: 'destructive',
      })
    }
  }, [facingMode, isHttps, maxWidth, maxHeight, stream, toast, getDevices])

  // Switch camera
  const switchCamera = useCallback(async () => {
    const newFacingMode = facingMode === 'user' ? 'environment' : 'user'
    setFacingMode(newFacingMode)
    
    // Reinitialize with new camera
    if (stream) {
      stream.getTracks().forEach(track => track.stop())
      setStream(null)
    }
    
    // Small delay to ensure cleanup
    setTimeout(() => {
      initCamera()
    }, 100)
  }, [facingMode, stream, initCamera])

  // Capture photo
  const capturePhoto = useCallback(() => {
    if (!videoRef.current || !canvasRef.current) return

    const video = videoRef.current
    const canvas = canvasRef.current
    
    // Set canvas size to match video
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    
    // Draw video frame to canvas
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    
    ctx.drawImage(video, 0, 0)
    
    // Convert to blob
    canvas.toBlob((blob) => {
      if (!blob) return
      
      // Create file from blob
      const file = new File([blob], `meal_${Date.now()}.jpg`, { type: 'image/jpeg' })
      
      // Get data URL for preview
      const reader = new FileReader()
      reader.onloadend = () => {
        const dataUrl = reader.result as string
        onCapture(dataUrl, file)
        
        // Clean up
        if (stream) {
          stream.getTracks().forEach(track => track.stop())
        }
        setStream(null)
        setIsCapturing(false)
        
        toast({
          title: '撮影成功',
          description: '写真を撮影しました',
        })
      }
      reader.readAsDataURL(blob)
    }, 'image/jpeg', 0.9)
  }, [stream, onCapture, toast])

  // Handle file upload fallback
  const handleFileUpload = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Check file type
    if (!file.type.startsWith('image/')) {
      toast({
        title: 'エラー',
        description: '画像ファイルを選択してください',
        variant: 'destructive',
      })
      return
    }

    // Read file
    const reader = new FileReader()
    reader.onloadend = () => {
      const dataUrl = reader.result as string
      onCapture(dataUrl, file)
      
      toast({
        title: 'アップロード成功',
        description: '画像をアップロードしました',
      })
    }
    reader.readAsDataURL(file)
  }, [onCapture, toast])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop())
      }
    }
  }, [stream])

  // Initialize camera on mount
  useEffect(() => {
    if (isHttps && !stream && !error) {
      initCamera()
    }
  }, [isHttps, initCamera, stream, error])

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardContent className="p-4 space-y-4">
        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-start">
              <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 mr-2 flex-shrink-0" />
              <div className="flex-1">
                <p className="text-sm text-red-800">{error}</p>
                {!isHttps && (
                  <p className="text-xs text-red-600 mt-1">
                    HTTPSで接続するか、ローカルホストで実行してください。
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Camera View */}
        {isCapturing && !error && (
          <div className="relative">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="w-full rounded-lg bg-black"
              style={{ aspectRatio }}
            />
            <canvas ref={canvasRef} className="hidden" />
            
            {/* Camera Controls */}
            <div className="absolute bottom-4 left-0 right-0 flex justify-center gap-4">
              <Button
                onClick={capturePhoto}
                size="lg"
                className="rounded-full w-16 h-16 bg-white hover:bg-gray-100"
              >
                <Camera className="w-8 h-8 text-gray-800" />
              </Button>
              
              {devices.length > 1 && (
                <Button
                  onClick={switchCamera}
                  size="icon"
                  variant="secondary"
                  className="rounded-full"
                >
                  <SwitchCamera className="w-5 h-5" />
                </Button>
              )}
            </div>
          </div>
        )}

        {/* Fallback Upload */}
        {(!isCapturing || error || hasPermission === false) && (
          <div className="space-y-4">
            <div className="text-center py-8">
              <CameraOff className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 mb-4">
                {error || 'カメラが利用できません'}
              </p>
              <p className="text-sm text-gray-500 mb-4">
                代わりに画像をアップロードしてください
              </p>
            </div>
            
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              capture="environment"
              onChange={handleFileUpload}
              className="hidden"
            />
            
            <Button
              onClick={() => fileInputRef.current?.click()}
              className="w-full"
              size="lg"
            >
              <Upload className="w-5 h-5 mr-2" />
              画像を選択
            </Button>
          </div>
        )}

        {/* Debug Info (Development Only) */}
        {process.env.NODE_ENV === 'development' && (
          <div className="text-xs text-gray-500 space-y-1 p-3 bg-gray-50 rounded">
            <p>HTTPS: {isHttps ? 'Yes' : 'No'}</p>
            <p>Permission: {hasPermission === null ? 'Not checked' : hasPermission ? 'Granted' : 'Denied'}</p>
            <p>Devices: {devices.length}</p>
            <p>Facing: {facingMode}</p>
            <p>Stream: {stream ? 'Active' : 'Inactive'}</p>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-2">
          {!isCapturing && !error && (
            <Button onClick={initCamera} className="flex-1">
              カメラを起動
            </Button>
          )}
          
          {onClose && (
            <Button 
              onClick={() => {
                if (stream) {
                  stream.getTracks().forEach(track => track.stop())
                }
                onClose()
              }} 
              variant="outline"
              className="flex-1"
            >
              <X className="w-4 h-4 mr-2" />
              キャンセル
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  )
}