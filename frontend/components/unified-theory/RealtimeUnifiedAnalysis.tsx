'use client'

import React, { useRef, useEffect, useState, useCallback } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Slider } from '@/components/ui/slider'
import { 
  Camera, 
  CameraOff, 
  Video,
  VideoOff,
  Settings,
  Loader2,
  AlertCircle,
  CheckCircle
} from 'lucide-react'
import UnifiedTheoryDashboard from './UnifiedTheoryDashboard'

interface UserProfile {
  physicalMeasurements: {
    height: number
    weight: number
    limbLengths?: Record<string, number>
  }
  experienceLevel: 'beginner' | 'intermediate' | 'advanced'
  goals: string[]
  limitations: string[]
}

interface CalibrationData {
  heightReference: number
  cameraAngle: number
}

interface RealtimeUnifiedAnalysisProps {
  userProfile: UserProfile
  onAnalysisUpdate?: (analysis: any) => void
}

export default function RealtimeUnifiedAnalysis({ 
  userProfile,
  onAnalysisUpdate 
}: RealtimeUnifiedAnalysisProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  
  const [isStreaming, setIsStreaming] = useState(false)
  const [isConnected, setIsConnected] = useState(false)
  const [exerciseType, setExerciseType] = useState('squat')
  const [cameraFacing, setCameraFacing] = useState<'user' | 'environment'>('user')
  const [showSettings, setShowSettings] = useState(false)
  const [analysisInterval, setAnalysisInterval] = useState(100) // ms
  
  const [currentAnalysis, setCurrentAnalysis] = useState<any>(null)
  const [connectionStatus, setConnectionStatus] = useState<'disconnected' | 'connecting' | 'connected' | 'error'>('disconnected')
  const [calibrationData, setCalibrationData] = useState<CalibrationData>({
    heightReference: userProfile.physicalMeasurements.height,
    cameraAngle: 0
  })

  // Connect to WebSocket
  const connectWebSocket = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return

    setConnectionStatus('connecting')
    const token = localStorage.getItem('auth_token') || ''
    const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'}/ws/unified-theory?token=${token}&exercise_type=${exerciseType}`
    
    const ws = new WebSocket(wsUrl)
    
    ws.onopen = () => {
      console.log('WebSocket connected')
      setIsConnected(true)
      setConnectionStatus('connected')
      
      // Send initial configuration
      ws.send(JSON.stringify({
        type: 'user_profile',
        data: { profile: userProfile }
      }))
      
      ws.send(JSON.stringify({
        type: 'calibration',
        data: { calibration: calibrationData }
      }))
      
      ws.send(JSON.stringify({
        type: 'settings',
        data: { 
          settings: { 
            exercise_type: exerciseType,
            analysis_interval: analysisInterval / 1000
          }
        }
      }))
    }
    
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data)
      
      if (message.type === 'analysis') {
        setCurrentAnalysis(message.data)
        onAnalysisUpdate?.(message.data)
      } else if (message.type === 'error') {
        console.error('Analysis error:', message.data)
      }
    }
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      setConnectionStatus('error')
    }
    
    ws.onclose = () => {
      console.log('WebSocket disconnected')
      setIsConnected(false)
      setConnectionStatus('disconnected')
      
      // Attempt to reconnect after 3 seconds
      setTimeout(() => {
        if (isStreaming) {
          connectWebSocket()
        }
      }, 3000)
    }
    
    wsRef.current = ws
  }, [exerciseType, userProfile, calibrationData, analysisInterval, isStreaming, onAnalysisUpdate])

  // Start camera stream
  const startCamera = async () => {
    try {
      const constraints = {
        video: {
          facingMode: cameraFacing,
          width: { ideal: 1280 },
          height: { ideal: 720 }
        }
      }
      
      const stream = await navigator.mediaDevices.getUserMedia(constraints)
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        streamRef.current = stream
        setIsStreaming(true)
        
        // Connect WebSocket after camera starts
        connectWebSocket()
      }
    } catch (error) {
      console.error('Error accessing camera:', error)
      setConnectionStatus('error')
    }
  }

  // Stop camera stream
  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
      streamRef.current = null
    }
    
    if (videoRef.current) {
      videoRef.current.srcObject = null
    }
    
    if (wsRef.current) {
      wsRef.current.close()
    }
    
    setIsStreaming(false)
    setIsConnected(false)
    setCurrentAnalysis(null)
  }

  // Send frame to WebSocket
  const sendFrame = useCallback(() => {
    if (!isConnected || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return
    if (!videoRef.current || !canvasRef.current) return
    
    const video = videoRef.current
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    
    if (!ctx) return
    
    // Set canvas size to match video
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    
    // Draw video frame to canvas
    ctx.drawImage(video, 0, 0)
    
    // Convert to base64
    canvas.toBlob((blob) => {
      if (!blob) return
      
      const reader = new FileReader()
      reader.onloadend = () => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
          wsRef.current.send(JSON.stringify({
            type: 'frame',
            data: { frame: reader.result }
          }))
        }
      }
      reader.readAsDataURL(blob)
    }, 'image/jpeg', 0.8)
  }, [isConnected])

  // Set up frame sending interval
  useEffect(() => {
    if (!isStreaming || !isConnected) return
    
    const interval = setInterval(sendFrame, analysisInterval)
    return () => clearInterval(interval)
  }, [isStreaming, isConnected, analysisInterval, sendFrame])

  // Update settings when changed
  useEffect(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'settings',
        data: {
          settings: {
            exercise_type: exerciseType,
            analysis_interval: analysisInterval / 1000
          }
        }
      }))
    }
  }, [exerciseType, analysisInterval])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopCamera()
    }
  }, [])

  const getStatusColor = () => {
    switch (connectionStatus) {
      case 'connected': return 'text-green-600'
      case 'connecting': return 'text-yellow-600'
      case 'error': return 'text-red-600'
      default: return 'text-gray-600'
    }
  }

  const getStatusIcon = () => {
    switch (connectionStatus) {
      case 'connected': return <CheckCircle className="w-4 h-4" />
      case 'connecting': return <Loader2 className="w-4 h-4 animate-spin" />
      case 'error': return <AlertCircle className="w-4 h-4" />
      default: return null
    }
  }

  return (
    <div className="space-y-6">
      {/* Control Bar */}
      <Card className="p-4">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-4">
            <Button
              onClick={isStreaming ? stopCamera : startCamera}
              variant={isStreaming ? "destructive" : "default"}
              className="gap-2"
            >
              {isStreaming ? (
                <>
                  <VideoOff className="w-4 h-4" />
                  Stop Analysis
                </>
              ) : (
                <>
                  <Video className="w-4 h-4" />
                  Start Analysis
                </>
              )}
            </Button>
            
            <Select value={exerciseType} onValueChange={setExerciseType}>
              <SelectTrigger className="w-40">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="squat">Squat</SelectItem>
                <SelectItem value="deadlift">Deadlift</SelectItem>
                <SelectItem value="bench_press">Bench Press</SelectItem>
                <SelectItem value="bicep_curl">Bicep Curl</SelectItem>
              </SelectContent>
            </Select>
            
            <Button
              variant="outline"
              size="icon"
              onClick={() => setCameraFacing(prev => prev === 'user' ? 'environment' : 'user')}
              disabled={isStreaming}
            >
              <Camera className="w-4 h-4" />
            </Button>
            
            <Button
              variant="outline"
              size="icon"
              onClick={() => setShowSettings(!showSettings)}
            >
              <Settings className="w-4 h-4" />
            </Button>
          </div>
          
          <div className={`flex items-center gap-2 ${getStatusColor()}`}>
            {getStatusIcon()}
            <span className="text-sm font-medium capitalize">{connectionStatus}</span>
          </div>
        </div>
        
        {/* Settings Panel */}
        {showSettings && (
          <div className="mt-4 pt-4 border-t space-y-4">
            <div>
              <label className="text-sm font-medium block mb-2">
                Analysis Interval: {analysisInterval}ms
              </label>
              <Slider
                value={[analysisInterval]}
                onValueChange={([value]) => setAnalysisInterval(value)}
                min={50}
                max={500}
                step={50}
                className="w-full"
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium block mb-1">
                  Height Reference (cm)
                </label>
                <input
                  type="number"
                  value={calibrationData.heightReference}
                  onChange={(e) => setCalibrationData(prev => ({
                    ...prev,
                    heightReference: parseInt(e.target.value) || 170
                  }))}
                  className="w-full px-3 py-2 border rounded"
                />
              </div>
              
              <div>
                <label className="text-sm font-medium block mb-1">
                  Camera Angle (degrees)
                </label>
                <input
                  type="number"
                  value={calibrationData.cameraAngle}
                  onChange={(e) => setCalibrationData(prev => ({
                    ...prev,
                    cameraAngle: parseInt(e.target.value) || 0
                  }))}
                  className="w-full px-3 py-2 border rounded"
                />
              </div>
            </div>
          </div>
        )}
      </Card>

      {/* Video Display */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-4">
          <div className="relative aspect-video bg-gray-100 rounded-lg overflow-hidden">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="absolute inset-0 w-full h-full object-cover"
            />
            <canvas
              ref={canvasRef}
              className="hidden"
            />
            
            {!isStreaming && (
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <Camera className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                  <p className="text-gray-600">Click "Start Analysis" to begin</p>
                </div>
              </div>
            )}
            
            {isStreaming && currentAnalysis && (
              <div className="absolute top-4 left-4 right-4">
                <div className="bg-black/70 text-white rounded-lg p-3 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Overall Score</span>
                    <span className="text-xl font-bold">
                      {(currentAnalysis.unified_scores?.overall * 100 || 0).toFixed(0)}%
                    </span>
                  </div>
                  
                  {currentAnalysis.feedback?.length > 0 && (
                    <div className="text-xs">
                      <p className="font-medium mb-1">Top Issue:</p>
                      <p>{currentAnalysis.feedback[0].message}</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </Card>

        {/* Analysis Dashboard */}
        <div className="h-full">
          {currentAnalysis ? (
            <UnifiedTheoryDashboard
              scores={currentAnalysis.unified_scores || {
                physics_efficiency: 0,
                biological_optimality: 0,
                system_stability: 0,
                mathematical_optimization: 0,
                overall: 0
              }}
              feedback={currentAnalysis.feedback || []}
              physics={currentAnalysis.physics || {}}
              biomechanics={currentAnalysis.biomechanics || {}}
              optimization={currentAnalysis.optimization || {}}
              isLoading={false}
            />
          ) : (
            <Card className="h-full flex items-center justify-center p-8">
              <div className="text-center">
                <Activity className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                <p className="text-gray-600">
                  {isStreaming ? 'Waiting for analysis data...' : 'Start analysis to see results'}
                </p>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}