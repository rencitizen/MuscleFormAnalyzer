'use client'

import React, { useRef, useEffect, useState, useCallback } from 'react'
import { Camera } from '@mediapipe/camera_utils'
import { Pose, Results } from '@mediapipe/pose'
import { drawConnectors, drawLandmarks } from '@mediapipe/drawing_utils'
import { POSE_CONNECTIONS } from '@mediapipe/pose'

interface PoseAnalyzerProps {
  exerciseType: 'squat' | 'bench_press' | 'deadlift'
  onAnalysisResult?: (result: AnalysisResult) => void
  onLandmarksUpdate?: (landmarks: any[]) => void
}

interface AnalysisResult {
  angles: {
    left_knee?: number
    right_knee?: number
    left_hip?: number
    right_hip?: number
    left_elbow?: number
    right_elbow?: number
    back_angle?: number
  }
  form_score: number
  feedback: string[]
  timestamp: string
}

export default function PoseAnalyzer({ exerciseType, onAnalysisResult, onLandmarksUpdate }: PoseAnalyzerProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const poseRef = useRef<Pose | null>(null)
  const cameraRef = useRef<Camera | null>(null)
  
  const [isRecording, setIsRecording] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [recordedLandmarks, setRecordedLandmarks] = useState<any[]>([])
  const frameCountRef = useRef(0)

  // MediaPipe結果処理
  const onResults = useCallback(async (results: Results) => {
    if (!canvasRef.current || !videoRef.current) return

    const canvasCtx = canvasRef.current.getContext('2d')
    if (!canvasCtx) return

    // キャンバスをクリア
    canvasCtx.save()
    canvasCtx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height)

    // ビデオフレームを描画
    canvasCtx.drawImage(results.image, 0, 0, canvasRef.current.width, canvasRef.current.height)

    // ランドマークが検出された場合
    if (results.poseLandmarks) {
      // スケルトンを描画
      drawConnectors(canvasCtx, results.poseLandmarks, POSE_CONNECTIONS, {
        color: '#00FF00',
        lineWidth: 4,
      })
      
      // 関節ポイントを描画
      drawLandmarks(canvasCtx, results.poseLandmarks, {
        color: '#FF0000',
        lineWidth: 2,
        radius: 6,
      })

      // ランドマークをオブジェクト形式に変換
      const landmarksObj: { [key: string]: any } = {}
      results.poseLandmarks.forEach((landmark, index) => {
        landmarksObj[index.toString()] = {
          x: landmark.x,
          y: landmark.y,
          z: landmark.z,
          visibility: landmark.visibility
        }
      })

      // 録画中の場合、ランドマークを保存
      if (isRecording) {
        const frameData = {
          frame: frameCountRef.current++,
          landmarks: landmarksObj,
          timestamp: new Date().toISOString()
        }
        setRecordedLandmarks(prev => [...prev, frameData])

        // LocalStorageに保存（最新の100フレームのみ）
        const recentFrames = recordedLandmarks.slice(-100)
        localStorage.setItem('recordedPoseData', JSON.stringify({
          exerciseType,
          frames: recentFrames,
          recordedAt: new Date().toISOString()
        }))
      }

      // リアルタイム分析
      if (onLandmarksUpdate) {
        onLandmarksUpdate(results.poseLandmarks)
      }

      // APIに送信して分析
      try {
        const response = await fetch('http://localhost:5000/api/analyze', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            landmarks: landmarksObj,
            exercise_type: exerciseType,
            frame_number: frameCountRef.current
          })
        })

        if (response.ok) {
          const analysisResult = await response.json()
          if (onAnalysisResult) {
            onAnalysisResult(analysisResult)
          }
        }
      } catch (err) {
        console.error('API分析エラー:', err)
      }
    }

    canvasCtx.restore()
  }, [exerciseType, isRecording, onAnalysisResult, onLandmarksUpdate, recordedLandmarks])

  // MediaPipeの初期化
  useEffect(() => {
    const initializePose = async () => {
      try {
        setIsLoading(true)
        setError(null)

        if (!videoRef.current || !canvasRef.current) {
          throw new Error('ビデオまたはキャンバス要素が見つかりません')
        }

        // Poseインスタンスを作成
        const pose = new Pose({
          locateFile: (file) => {
            return `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`
          },
        })

        // Poseの設定
        pose.setOptions({
          modelComplexity: 1,
          smoothLandmarks: true,
          enableSegmentation: false,
          smoothSegmentation: false,
          minDetectionConfidence: 0.5,
          minTrackingConfidence: 0.5,
        })

        pose.onResults(onResults)
        poseRef.current = pose

        // カメラを初期化
        const camera = new Camera(videoRef.current, {
          onFrame: async () => {
            if (poseRef.current && videoRef.current) {
              await poseRef.current.send({ image: videoRef.current })
            }
          },
          width: 640,
          height: 480,
        })

        cameraRef.current = camera
        await camera.start()
        
        setIsLoading(false)
      } catch (err) {
        console.error('初期化エラー:', err)
        setError(err instanceof Error ? err.message : 'カメラの初期化に失敗しました')
        setIsLoading(false)
      }
    }

    initializePose()

    // クリーンアップ
    return () => {
      if (cameraRef.current) {
        cameraRef.current.stop()
      }
      if (poseRef.current) {
        poseRef.current.close()
      }
    }
  }, [onResults])

  // 録画開始/停止
  const toggleRecording = () => {
    if (isRecording) {
      // 録画停止
      setIsRecording(false)
      console.log(`録画停止: ${recordedLandmarks.length}フレームを保存しました`)
      
      // 最終的なデータをLocalStorageに保存
      localStorage.setItem('lastRecordingData', JSON.stringify({
        exerciseType,
        totalFrames: recordedLandmarks.length,
        landmarks: recordedLandmarks,
        recordedAt: new Date().toISOString()
      }))
    } else {
      // 録画開始
      setRecordedLandmarks([])
      frameCountRef.current = 0
      setIsRecording(true)
      console.log('録画開始')
    }
  }

  return (
    <div className="relative w-full max-w-4xl mx-auto">
      {/* ローディング表示 */}
      {isLoading && (
        <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center z-20">
          <div className="text-white text-lg">カメラを初期化中...</div>
        </div>
      )}

      {/* エラー表示 */}
      {error && (
        <div className="absolute top-4 left-4 right-4 bg-red-500 text-white p-4 rounded-lg z-20">
          <p className="font-semibold">エラー</p>
          <p>{error}</p>
        </div>
      )}

      {/* ビデオとキャンバス */}
      <div className="relative aspect-video bg-gray-900 rounded-lg overflow-hidden">
        <video
          ref={videoRef}
          className="absolute inset-0 w-full h-full object-cover"
          playsInline
          muted
        />
        <canvas
          ref={canvasRef}
          className="absolute inset-0 w-full h-full"
          width={640}
          height={480}
        />

        {/* 録画インジケーター */}
        {isRecording && (
          <div className="absolute top-4 left-4 flex items-center space-x-2 bg-red-500 text-white px-3 py-1 rounded-full">
            <div className="w-3 h-3 bg-white rounded-full animate-pulse" />
            <span className="text-sm font-medium">録画中</span>
          </div>
        )}

        {/* 運動種目表示 */}
        <div className="absolute top-4 right-4 bg-black bg-opacity-50 text-white px-3 py-1 rounded">
          <span className="text-sm font-medium">
            {exerciseType === 'squat' && 'スクワット'}
            {exerciseType === 'bench_press' && 'ベンチプレス'}
            {exerciseType === 'deadlift' && 'デッドリフト'}
          </span>
        </div>
      </div>

      {/* コントロールボタン */}
      <div className="mt-4 flex justify-center">
        <button
          onClick={toggleRecording}
          className={`px-6 py-3 rounded-lg font-medium text-white transition-colors ${
            isRecording
              ? 'bg-red-600 hover:bg-red-700'
              : 'bg-blue-600 hover:bg-blue-700'
          }`}
          disabled={isLoading || !!error}
        >
          {isRecording ? '録画停止' : '録画開始'}
        </button>
      </div>

      {/* デバッグ情報 */}
      {process.env.NODE_ENV === 'development' && (
        <div className="mt-4 p-4 bg-gray-100 rounded-lg text-sm">
          <p>フレーム数: {frameCountRef.current}</p>
          <p>保存済みランドマーク: {recordedLandmarks.length}</p>
        </div>
      )}
    </div>
  )
}