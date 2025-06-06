'use client'

import { useEffect, useRef, useState, useCallback } from 'react'
import { Pose, Results } from '@mediapipe/pose'
import { Camera } from '@mediapipe/camera_utils'
import { drawConnectors, drawLandmarks } from '@mediapipe/drawing_utils'
import { POSE_CONNECTIONS } from '@mediapipe/pose'
import { Landmark, PoseResults } from './types'
import toast from 'react-hot-toast'

interface UsePoseDetectionOptions {
  onResults?: (results: PoseResults) => void
  minDetectionConfidence?: number
  minTrackingConfidence?: number
  modelComplexity?: 0 | 1 | 2
}

export function usePoseDetection(options: UsePoseDetectionOptions = {}) {
  const {
    onResults,
    minDetectionConfidence = 0.5,
    minTrackingConfidence = 0.5,
    modelComplexity = 1,
  } = options

  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const poseRef = useRef<Pose | null>(null)
  const cameraRef = useRef<Camera | null>(null)
  
  const [isLoading, setIsLoading] = useState(true)
  const [isDetecting, setIsDetecting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // デモモードチェック
  const isDemoMode = process.env.NEXT_PUBLIC_DEMO_MODE === 'true'

  const onResultsCallback = useCallback((results: Results) => {
    if (!canvasRef.current || !videoRef.current) return

    const canvasCtx = canvasRef.current.getContext('2d')
    if (!canvasCtx) return

    canvasCtx.save()
    canvasCtx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height)

    // segmentationMaskが存在する場合は描画
    if (results.segmentationMask) {
      canvasCtx.drawImage(results.segmentationMask, 0, 0, 
        canvasRef.current.width, canvasRef.current.height)
    }

    // 画像を描画
    canvasCtx.globalCompositeOperation = results.segmentationMask ? 'source-in' : 'source-over'
    canvasCtx.drawImage(results.image, 0, 0, 
      canvasRef.current.width, canvasRef.current.height)

    // ランドマークを描画
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

      // 結果をコールバックに渡す
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

  const initializePose = useCallback(async () => {
    try {
      setIsLoading(true)
      setError(null)

      if (!videoRef.current || !canvasRef.current) {
        throw new Error('Video or canvas element not found')
      }

      // Pose検出器を初期化
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

      // デモモードの場合はダミーのカメラセットアップ
      if (isDemoMode) {
        setIsLoading(false)
        toast.success('デモモードで起動しました')
        
        // デモ用のダミーポーズデータを定期的に送信
        const demoInterval = setInterval(() => {
          if (poseRef.current && onResults) {
            // ダミーのポーズデータを生成
            const dummyResults: PoseResults = {
              poseLandmarks: generateDemoLandmarks(),
            }
            onResults(dummyResults)
          }
        }, 100)
        
        // クリーンアップ用に保存
        cameraRef.current = { stop: () => clearInterval(demoInterval) } as any
      } else {
        // 通常のカメラを初期化
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
        
        setIsLoading(false)
        toast.success('カメラを初期化しました')
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'カメラの初期化に失敗しました'
      setError(errorMessage)
      setIsLoading(false)
      toast.error(errorMessage)
    }
  }, [minDetectionConfidence, minTrackingConfidence, modelComplexity, onResultsCallback, isDemoMode])

  // デモ用ランドマーク生成関数
  const generateDemoLandmarks = (): Landmark[] => {
    const time = Date.now() / 1000
    const squatPhase = Math.sin(time * 0.5) * 0.5 + 0.5 // 0-1の値で上下運動
    
    // 基本的なスクワットのポーズを生成
    const landmarks: Landmark[] = []
    
    // 33個のランドマークを生成（MediaPipeの標準）
    for (let i = 0; i < 33; i++) {
      landmarks.push({
        x: 0.5,
        y: 0.5,
        z: 0,
        visibility: 1
      })
    }
    
    // 主要なランドマークを設定（スクワットのデモ）
    // 頭部
    landmarks[0] = { x: 0.5, y: 0.1 + squatPhase * 0.1, z: 0, visibility: 1 } // 鼻
    
    // 肩
    landmarks[11] = { x: 0.4, y: 0.3 + squatPhase * 0.15, z: 0, visibility: 1 } // 左肩
    landmarks[12] = { x: 0.6, y: 0.3 + squatPhase * 0.15, z: 0, visibility: 1 } // 右肩
    
    // 腰
    landmarks[23] = { x: 0.45, y: 0.5 + squatPhase * 0.2, z: 0, visibility: 1 } // 左腰
    landmarks[24] = { x: 0.55, y: 0.5 + squatPhase * 0.2, z: 0, visibility: 1 } // 右腰
    
    // 膝（スクワットで曲がる）
    landmarks[25] = { x: 0.45, y: 0.7 + squatPhase * 0.1, z: 0, visibility: 1 } // 左膝
    landmarks[26] = { x: 0.55, y: 0.7 + squatPhase * 0.1, z: 0, visibility: 1 } // 右膝
    
    // 足首
    landmarks[27] = { x: 0.45, y: 0.9, z: 0, visibility: 1 } // 左足首
    landmarks[28] = { x: 0.55, y: 0.9, z: 0, visibility: 1 } // 右足首
    
    return landmarks
  }

  const startDetection = useCallback(async () => {
    if (!cameraRef.current) {
      await initializePose()
    }
    
    if (cameraRef.current) {
      await cameraRef.current.start()
      setIsDetecting(true)
    }
  }, [initializePose])

  const stopDetection = useCallback(() => {
    if (cameraRef.current) {
      cameraRef.current.stop()
      setIsDetecting(false)
    }
  }, [])

  // クリーンアップ
  useEffect(() => {
    return () => {
      if (cameraRef.current) {
        cameraRef.current.stop()
      }
      if (poseRef.current) {
        poseRef.current.close()
      }
    }
  }, [])

  return {
    videoRef,
    canvasRef,
    isLoading,
    isDetecting,
    error,
    startDetection,
    stopDetection,
    initializePose,
  }
}