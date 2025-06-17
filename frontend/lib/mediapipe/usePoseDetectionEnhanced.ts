'use client'

import { useEffect, useRef, useState, useCallback } from 'react'
import { Pose, Results } from '@mediapipe/pose'
import { drawConnectors, drawLandmarks } from '@mediapipe/drawing_utils'
import { POSE_CONNECTIONS } from '@mediapipe/pose'
import { Landmark, PoseResults } from './types'
import { useCamera } from '@/hooks/useCamera'
import toast from 'react-hot-toast'

interface UsePoseDetectionEnhancedOptions {
  onResults?: (results: PoseResults) => void
  minDetectionConfidence?: number
  minTrackingConfidence?: number
  modelComplexity?: 0 | 1 | 2
  initialFacingMode?: 'user' | 'environment'
}

export function usePoseDetectionEnhanced(options: UsePoseDetectionEnhancedOptions = {}) {
  const {
    onResults,
    minDetectionConfidence = 0.5,
    minTrackingConfidence = 0.5,
    modelComplexity = 1,
    initialFacingMode = 'environment',
  } = options

  // Use our enhanced camera hook
  const {
    videoRef,
    currentCamera,
    isLoading: cameraLoading,
    error: cameraError,
    hasMultipleCameras,
    initializeCamera,
    switchCamera: cameraSwitchHandler,
    stopCamera
  } = useCamera()

  const canvasRef = useRef<HTMLCanvasElement>(null)
  const poseRef = useRef<Pose | null>(null)
  const animationFrameRef = useRef<number | null>(null)
  
  const [isPoseLoading, setIsPoseLoading] = useState(true)
  const [isDetecting, setIsDetecting] = useState(false)
  const [poseError, setPoseError] = useState<string | null>(null)
  const [isMediaPipeReady, setIsMediaPipeReady] = useState(false)
  
  // Demo mode check
  const isDemoMode = process.env.NEXT_PUBLIC_DEMO_MODE === 'true'

  // Combined loading state
  const isLoading = cameraLoading || isPoseLoading
  const error = cameraError || poseError

  const onResultsCallback = useCallback((results: Results) => {
    if (!canvasRef.current || !videoRef.current) return

    const canvasCtx = canvasRef.current.getContext('2d')
    if (!canvasCtx) return

    canvasCtx.save()
    canvasCtx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height)

    // Draw segmentation mask if available
    if (results.segmentationMask) {
      canvasCtx.drawImage(results.segmentationMask, 0, 0, 
        canvasRef.current.width, canvasRef.current.height)
    }

    // Draw image
    canvasCtx.globalCompositeOperation = results.segmentationMask ? 'source-in' : 'source-over'
    canvasCtx.drawImage(results.image, 0, 0, 
      canvasRef.current.width, canvasRef.current.height)

    // Draw landmarks
    if (results.poseLandmarks) {
      canvasCtx.globalCompositeOperation = 'source-over'
      
      drawConnectors(canvasCtx, results.poseLandmarks, POSE_CONNECTIONS, {
        color: '#00FF00',
        lineWidth: 4,
      })
      
      drawLandmarks(canvasCtx, results.poseLandmarks, {
        color: '#FF0000',
        lineWidth: 2,
        radius: 5,
      })

      // Pass results to callback
      if (onResults) {
        const poseResults: PoseResults = {
          poseLandmarks: results.poseLandmarks as Landmark[],
          poseWorldLandmarks: results.poseWorldLandmarks as Landmark[],
        }
        onResults(poseResults)
      }
    }

    canvasCtx.restore()
  }, [onResults])

  // Initialize MediaPipe Pose (only once)
  useEffect(() => {
    const initializePose = async () => {
      try {
        setIsPoseLoading(true)
        setPoseError(null)

        if (!canvasRef.current) {
          throw new Error('Canvas element not found')
        }

        // Initialize Pose detector
        const pose = new Pose({
          locateFile: (file) => {
            return `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`
          },
        })

        pose.setOptions({
          modelComplexity,
          smoothLandmarks: true,
          enableSegmentation: false,
          smoothSegmentation: false,
          minDetectionConfidence,
          minTrackingConfidence,
        })

        pose.onResults(onResultsCallback)
        poseRef.current = pose
        setIsMediaPipeReady(true)

        console.log('MediaPipe Pose initialized successfully')
      } catch (err) {
        console.error('Failed to initialize MediaPipe:', err)
        setPoseError(err instanceof Error ? err.message : 'Failed to initialize pose detection')
      } finally {
        setIsPoseLoading(false)
      }
    }

    initializePose()

    return () => {
      if (poseRef.current) {
        poseRef.current.close()
        poseRef.current = null
      }
    }
  }, [modelComplexity, minDetectionConfidence, minTrackingConfidence, onResultsCallback])

  // Initialize camera when component mounts
  useEffect(() => {
    initializeCamera(initialFacingMode)
  }, [initialFacingMode, initializeCamera])

  // Process video frames
  const processFrame = useCallback(async () => {
    if (!poseRef.current || !videoRef.current || !isDetecting || !isMediaPipeReady) {
      return
    }

    // Verify video is ready and playing
    if (videoRef.current.readyState < 2) {
      console.log('[MediaPipe] Video not ready, waiting...')
      animationFrameRef.current = requestAnimationFrame(processFrame)
      return
    }

    try {
      await poseRef.current.send({ image: videoRef.current })
    } catch (err) {
      console.error('[MediaPipe] Error processing frame:', err)
      // If error is related to video state, retry
      if (err.message?.includes('video') && isDetecting) {
        setTimeout(() => {
          if (isDetecting) {
            processFrame()
          }
        }, 100)
        return
      }
    }

    // Continue processing
    if (isDetecting) {
      animationFrameRef.current = requestAnimationFrame(processFrame)
    }
  }, [isDetecting, isMediaPipeReady])

  // Start detection
  const startDetection = useCallback(async () => {
    if (isDemoMode) {
      toast.error('カメラ機能はデモモードでは利用できません')
      return
    }

    if (!videoRef.current || !poseRef.current || !isMediaPipeReady) {
      console.error('Not ready to start detection')
      return
    }

    setIsDetecting(true)
    processFrame()
  }, [isDemoMode, isMediaPipeReady, processFrame])

  // Stop detection
  const stopDetection = useCallback(() => {
    setIsDetecting(false)
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current)
      animationFrameRef.current = null
    }
  }, [])

  // Enhanced camera switch with proper cleanup
  const switchCamera = useCallback(async () => {
    console.log('[MediaPipe] Starting camera switch process...')
    
    // Store current detection state
    const wasDetecting = isDetecting
    
    // Stop detection and clear animation frame
    stopDetection()
    
    // Wait for current frame processing to complete
    await new Promise(resolve => setTimeout(resolve, 100))
    
    console.log('[MediaPipe] Switching camera...')
    const success = await cameraSwitchHandler()
    
    if (success) {
      console.log('[MediaPipe] Camera switch successful')
      
      // Wait for video stream to stabilize
      await new Promise(resolve => setTimeout(resolve, 300))
      
      // Verify video element has new stream
      if (videoRef.current && videoRef.current.srcObject) {
        const tracks = (videoRef.current.srcObject as MediaStream).getVideoTracks()
        console.log('[MediaPipe] New video tracks:', tracks.length, tracks[0]?.getSettings())
        
        // Resume detection if it was active before
        if (wasDetecting && poseRef.current && isMediaPipeReady) {
          console.log('[MediaPipe] Resuming detection...')
          startDetection()
        }
      } else {
        console.error('[MediaPipe] Video element not ready after camera switch')
      }
    } else {
      console.error('[MediaPipe] Camera switch failed')
    }
    
    return success
  }, [cameraSwitchHandler, stopDetection, startDetection, isDetecting, isMediaPipeReady])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopDetection()
      stopCamera()
    }
  }, [stopDetection, stopCamera])

  return {
    videoRef,
    canvasRef,
    isLoading,
    isDetecting,
    error,
    startDetection,
    stopDetection,
    switchCamera,
    currentFacingMode: currentCamera,
    hasMultipleCameras,
  }
}