import { Pose } from '@mediapipe/pose'
import { Camera } from '@mediapipe/camera_utils'

// シングルトンパターンでMediaPipeインスタンスを管理
class MediaPipeManager {
  private static instance: MediaPipeManager
  private pose: Pose | null = null
  private isInitializing = false
  private initPromise: Promise<void> | null = null

  private constructor() {}

  static getInstance(): MediaPipeManager {
    if (!MediaPipeManager.instance) {
      MediaPipeManager.instance = new MediaPipeManager()
    }
    return MediaPipeManager.instance
  }

  async initializePose(onResults: (results: any) => void): Promise<Pose> {
    // 既に初期化済みならそれを返す
    if (this.pose) {
      this.pose.onResults(onResults)
      return this.pose
    }

    // 初期化中なら完了を待つ
    if (this.isInitializing && this.initPromise) {
      await this.initPromise
      if (this.pose) {
        this.pose.onResults(onResults)
        return this.pose
      }
    }

    // 初期化開始
    this.isInitializing = true
    this.initPromise = this.performInitialization(onResults)
    
    try {
      await this.initPromise
      return this.pose!
    } finally {
      this.isInitializing = false
    }
  }

  private async performInitialization(onResults: (results: any) => void): Promise<void> {
    console.log('MediaPipe初期化開始...')
    const startTime = performance.now()

    this.pose = new Pose({
      locateFile: (file: string) => {
        return `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`
      }
    })

    this.pose.setOptions({
      modelComplexity: 1, // 0が最速、2が最高精度
      smoothLandmarks: true,
      enableSegmentation: false, // セグメンテーション無効で高速化
      smoothSegmentation: false,
      minDetectionConfidence: 0.5,
      minTrackingConfidence: 0.5
    })

    this.pose.onResults(onResults)

    await this.pose.initialize()
    
    const endTime = performance.now()
    console.log(`MediaPipe初期化完了: ${Math.round(endTime - startTime)}ms`)
  }

  cleanup() {
    if (this.pose) {
      this.pose.close()
      this.pose = null
    }
  }
}

// 最適化されたカメラアクセス
export async function startOptimizedCamera(
  videoElement: HTMLVideoElement,
  onFrame: (results: any) => void
): Promise<() => void> {
  const manager = MediaPipeManager.getInstance()
  
  // MediaPipeの初期化を並行して開始
  const posePromise = manager.initializePose(onFrame)
  
  // カメラアクセスも並行して開始
  const constraints: MediaStreamConstraints = {
    video: {
      width: { ideal: 1280, max: 1920 },
      height: { ideal: 720, max: 1080 },
      facingMode: 'user',
      frameRate: { ideal: 30, max: 60 }
    },
    audio: false
  }

  try {
    // カメラとMediaPipeの初期化を並行実行
    const [stream, pose] = await Promise.all([
      navigator.mediaDevices.getUserMedia(constraints),
      posePromise
    ])

    videoElement.srcObject = stream

    // ビデオメタデータ読み込み完了を待つ
    await new Promise<void>((resolve) => {
      videoElement.onloadedmetadata = () => {
        videoElement.play()
        resolve()
      }
    })

    // MediaPipeカメラの設定
    const camera = new Camera(videoElement, {
      onFrame: async () => {
        await pose.send({ image: videoElement })
      },
      width: videoElement.videoWidth,
      height: videoElement.videoHeight
    })

    camera.start()

    // クリーンアップ関数を返す
    return () => {
      camera.stop()
      stream.getTracks().forEach(track => track.stop())
      videoElement.srcObject = null
    }
  } catch (error) {
    console.error('カメラ起動エラー:', error)
    throw error
  }
}

// プリロード関数（アプリ起動時に呼び出す）
export async function preloadMediaPipe(): Promise<void> {
  const manager = MediaPipeManager.getInstance()
  await manager.initializePose(() => {})
  console.log('MediaPipeプリロード完了')
}