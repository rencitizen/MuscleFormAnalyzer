import { Pose, Results } from '@mediapipe/pose'
import { initializeMediaPipePose, cleanupMediaPipeResources, getDeviceCapabilities } from './mediapipeUtils'

// Body landmark indices
const POSE_LANDMARKS = {
  NOSE: 0,
  LEFT_EYE_INNER: 1,
  LEFT_EYE: 2,
  LEFT_EYE_OUTER: 3,
  RIGHT_EYE_INNER: 4,
  RIGHT_EYE: 5,
  RIGHT_EYE_OUTER: 6,
  LEFT_EAR: 7,
  RIGHT_EAR: 8,
  MOUTH_LEFT: 9,
  MOUTH_RIGHT: 10,
  LEFT_SHOULDER: 11,
  RIGHT_SHOULDER: 12,
  LEFT_ELBOW: 13,
  RIGHT_ELBOW: 14,
  LEFT_WRIST: 15,
  RIGHT_WRIST: 16,
  LEFT_PINKY: 17,
  RIGHT_PINKY: 18,
  LEFT_INDEX: 19,
  RIGHT_INDEX: 20,
  LEFT_THUMB: 21,
  RIGHT_THUMB: 22,
  LEFT_HIP: 23,
  RIGHT_HIP: 24,
  LEFT_KNEE: 25,
  RIGHT_KNEE: 26,
  LEFT_ANKLE: 27,
  RIGHT_ANKLE: 28,
  LEFT_HEEL: 29,
  RIGHT_HEEL: 30,
  LEFT_FOOT_INDEX: 31,
  RIGHT_FOOT_INDEX: 32
}

interface BodyMeasurements {
  height: number
  shoulderWidth: number
  armLength: { left: number; right: number }
  legLength: { left: number; right: number }
  torsoLength: number
  hipWidth: number
  upperArmLength: { left: number; right: number }
  forearmLength: { left: number; right: number }
  thighLength: { left: number; right: number }
  shinLength: { left: number; right: number }
}

interface ProcessingProgress {
  stage: 'initializing' | 'loading' | 'processing' | 'analyzing' | 'finalizing'
  currentFrame: number
  totalFrames: number
  percentage: number
  message: string
  estimatedTimeRemaining?: number
}

interface ProcessingOptions {
  maxDuration?: number // Maximum video duration in seconds (default: 60)
  maxFrames?: number // Maximum frames to process (default: 30)
  timeout?: number // Processing timeout in milliseconds (default: 300000 = 5 minutes)
  minConfidence?: number // Minimum pose detection confidence (default: 0.5)
}

// Error types for better error handling
export class VideoProcessingError extends Error {
  constructor(
    message: string,
    public code: 'TIMEOUT' | 'FORMAT' | 'INITIALIZATION' | 'PROCESSING' | 'NO_POSE_DETECTED',
    public details?: any
  ) {
    super(message)
    this.name = 'VideoProcessingError'
  }
}

// 3D distance calculation
function calculateDistance3D(
  landmark1: { x: number; y: number; z: number },
  landmark2: { x: number; y: number; z: number }
): number {
  const dx = landmark2.x - landmark1.x
  const dy = landmark2.y - landmark1.y
  const dz = landmark2.z - landmark1.z
  return Math.sqrt(dx * dx + dy * dy + dz * dz)
}

// Estimate real-world scale
function estimateScale(landmarks: any[], imageWidth: number, imageHeight: number): number {
  const leftShoulder = landmarks[POSE_LANDMARKS.LEFT_SHOULDER]
  const rightShoulder = landmarks[POSE_LANDMARKS.RIGHT_SHOULDER]
  
  if (!leftShoulder || !rightShoulder) return 1
  
  const shoulderWidthPixels = calculateDistance3D(leftShoulder, rightShoulder)
  const shoulderWidthNormalized = shoulderWidthPixels * Math.max(imageWidth, imageHeight)
  
  // Average shoulder width ~45cm
  const scale = 45 / shoulderWidthNormalized
  return scale
}

// Validate video file before processing
export async function validateVideoFile(file: File): Promise<{ valid: boolean; error?: string }> {
  const acceptedFormats = [
    'video/mp4',
    'video/quicktime',
    'video/x-msvideo',
    'video/webm',
    'video/mpeg',
    'video/ogg'
  ]
  
  if (!acceptedFormats.includes(file.type)) {
    return { 
      valid: false, 
      error: `対応していないファイル形式です。対応形式: MP4, MOV, AVI, WebM, MPEG, OGG` 
    }
  }
  
  const maxSize = 100 * 1024 * 1024 // 100MB
  if (file.size > maxSize) {
    return { 
      valid: false, 
      error: `ファイルサイズは100MB以下にしてください（現在: ${(file.size / 1024 / 1024).toFixed(1)}MB）` 
    }
  }
  
  // Check video duration
  const video = document.createElement('video')
  video.src = URL.createObjectURL(file)
  
  return new Promise((resolve) => {
    video.onloadedmetadata = () => {
      URL.revokeObjectURL(video.src)
      
      if (video.duration > 60) {
        resolve({ 
          valid: false, 
          error: `動画は60秒以下にしてください（現在: ${Math.round(video.duration)}秒）` 
        })
      } else {
        resolve({ valid: true })
      }
    }
    
    video.onerror = () => {
      URL.revokeObjectURL(video.src)
      resolve({ valid: false, error: '動画ファイルの読み込みに失敗しました' })
    }
  })
}

// Improved video processing with timeout and cancellation
export async function processVideoForBodyMeasurements(
  videoFile: File,
  onProgress?: (progress: ProcessingProgress) => void,
  options: ProcessingOptions = {}
): Promise<BodyMeasurements> {
  const {
    maxDuration = 60,
    maxFrames = 30,
    timeout = 300000, // 5 minutes
    minConfidence = 0.5
  } = options

  let pose: Pose | null = null
  let isProcessing = true
  let timeoutId: NodeJS.Timeout | null = null

  const cleanup = () => {
    isProcessing = false
    if (timeoutId) {
      clearTimeout(timeoutId)
    }
    cleanupMediaPipeResources(pose)
  }

  return new Promise((resolve, reject) => {
    // Set timeout
    timeoutId = setTimeout(() => {
      cleanup()
      reject(new VideoProcessingError(
        '処理がタイムアウトしました。動画が長すぎるか、処理に問題があります。',
        'TIMEOUT'
      ))
    }, timeout)

    const video = document.createElement('video')
    video.src = URL.createObjectURL(videoFile)
    video.muted = true
    
    video.onloadedmetadata = async () => {
      try {
        // Update progress
        if (onProgress) {
          onProgress({
            stage: 'initializing',
            currentFrame: 0,
            totalFrames: 0,
            percentage: 0,
            message: 'MediaPipeを初期化しています...'
          })
        }

        // Get device capabilities for optimization
        const deviceCaps = getDeviceCapabilities()
        const effectiveMaxFrames = Math.min(
          maxFrames, 
          deviceCaps.recommendedSettings.maxFrames
        )
        
        // Initialize MediaPipe Pose with retry logic
        pose = await initializeMediaPipePose({
          maxRetries: 3,
          retryDelay: 1000,
          onRetry: (attempt) => {
            if (onProgress) {
              onProgress({
                stage: 'initializing',
                currentFrame: 0,
                totalFrames: 0,
                percentage: 2,
                message: `MediaPipe初期化を再試行しています... (${attempt}/3)`
              })
            }
          }
        })
        
        // Override options based on device capabilities
        pose.setOptions({
          modelComplexity: deviceCaps.recommendedSettings.modelComplexity,
          smoothLandmarks: true,
          enableSegmentation: false,
          smoothSegmentation: false,
          minDetectionConfidence,
          minTrackingConfidence: minConfidence
        })
        
        const measurements: BodyMeasurements[] = []
        let frameCount = 0
        let noDetectionCount = 0
        const framesToProcess = Math.min(effectiveMaxFrames, Math.floor(video.duration * 10))
        const frameInterval = video.duration / framesToProcess
        
        // Update progress
        if (onProgress) {
          onProgress({
            stage: 'loading',
            currentFrame: 0,
            totalFrames: framesToProcess,
            percentage: 5,
            message: 'モデルを読み込んでいます...'
          })
        }

        pose.onResults((results: Results) => {
          if (!isProcessing) return

          if (results.poseLandmarks && results.poseWorldLandmarks) {
            noDetectionCount = 0 // Reset no detection counter
            
            const scale = estimateScale(
              results.poseLandmarks,
              video.videoWidth,
              video.videoHeight
            )
            
            const worldLandmarks = results.poseWorldLandmarks
            
            // Calculate measurements
            const measurement = calculateMeasurements(worldLandmarks, scale)
            measurements.push(measurement)
            frameCount++
            
            // Update progress
            if (onProgress) {
              const percentage = 10 + (frameCount / framesToProcess) * 80
              const elapsed = Date.now() - startTime
              const estimatedTotal = (elapsed / frameCount) * framesToProcess
              const estimatedRemaining = Math.max(0, estimatedTotal - elapsed)
              
              onProgress({
                stage: 'processing',
                currentFrame: frameCount,
                totalFrames: framesToProcess,
                percentage,
                message: `フレーム ${frameCount}/${framesToProcess} を処理中...`,
                estimatedTimeRemaining: Math.round(estimatedRemaining / 1000)
              })
            }
          } else {
            noDetectionCount++
            
            // If no pose detected for too many frames, warn user
            if (noDetectionCount > 10) {
              if (onProgress) {
                onProgress({
                  stage: 'processing',
                  currentFrame: frameCount,
                  totalFrames: framesToProcess,
                  percentage: 10 + (frameCount / framesToProcess) * 80,
                  message: '人物を検出できません。全身が映っているか確認してください。'
                })
              }
            }
          }
        })
        
        // Pose is already initialized by initializeMediaPipePose
        
        const startTime = Date.now()
        
        // Process video frames
        const processFrame = async () => {
          if (!isProcessing) return
          
          if (frameCount >= framesToProcess || video.currentTime >= video.duration) {
            // Finalize processing
            if (onProgress) {
              onProgress({
                stage: 'finalizing',
                currentFrame: frameCount,
                totalFrames: framesToProcess,
                percentage: 95,
                message: '測定結果を計算しています...'
              })
            }
            
            if (measurements.length === 0) {
              reject(new VideoProcessingError(
                '動画から人物を検出できませんでした。全身が映る動画を使用してください。',
                'NO_POSE_DETECTED'
              ))
              return
            }
            
            // Calculate average measurements
            const averageMeasurements = calculateAverageMeasurements(measurements)
            
            // Cleanup
            cleanup()
            URL.revokeObjectURL(video.src)
            
            // Final progress update
            if (onProgress) {
              onProgress({
                stage: 'finalizing',
                currentFrame: frameCount,
                totalFrames: framesToProcess,
                percentage: 100,
                message: '完了しました！'
              })
            }
            
            resolve(averageMeasurements)
            return
          }
          
          await pose.send({ image: video })
          video.currentTime = Math.min(video.currentTime + frameInterval, video.duration)
          
          if (isProcessing) {
            requestAnimationFrame(processFrame)
          }
        }
        
        video.play()
        video.pause()
        video.currentTime = 0
        processFrame()
        
      } catch (error) {
        cleanup()
        URL.revokeObjectURL(video.src)
        
        if (error instanceof VideoProcessingError) {
          reject(error)
        } else {
          reject(new VideoProcessingError(
            'MediaPipeの初期化に失敗しました。ブラウザを更新してもう一度お試しください。',
            'INITIALIZATION',
            error
          ))
        }
      }
    }
    
    video.onerror = () => {
      cleanup()
      URL.revokeObjectURL(video.src)
      reject(new VideoProcessingError(
        '動画ファイルの読み込みに失敗しました。ファイルが破損していないか確認してください。',
        'FORMAT'
      ))
    }
  })
}

// Calculate all measurements from landmarks
function calculateMeasurements(worldLandmarks: any[], scale: number): BodyMeasurements {
  return {
    height: estimateHeight(worldLandmarks, scale),
    shoulderWidth: calculateDistance3D(
      worldLandmarks[POSE_LANDMARKS.LEFT_SHOULDER],
      worldLandmarks[POSE_LANDMARKS.RIGHT_SHOULDER]
    ) * scale * 100,
    armLength: {
      left: calculateDistance3D(
        worldLandmarks[POSE_LANDMARKS.LEFT_SHOULDER],
        worldLandmarks[POSE_LANDMARKS.LEFT_WRIST]
      ) * scale * 100,
      right: calculateDistance3D(
        worldLandmarks[POSE_LANDMARKS.RIGHT_SHOULDER],
        worldLandmarks[POSE_LANDMARKS.RIGHT_WRIST]
      ) * scale * 100
    },
    legLength: {
      left: calculateDistance3D(
        worldLandmarks[POSE_LANDMARKS.LEFT_HIP],
        worldLandmarks[POSE_LANDMARKS.LEFT_ANKLE]
      ) * scale * 100,
      right: calculateDistance3D(
        worldLandmarks[POSE_LANDMARKS.RIGHT_HIP],
        worldLandmarks[POSE_LANDMARKS.RIGHT_ANKLE]
      ) * scale * 100
    },
    torsoLength: calculateTorsoLength(worldLandmarks, scale),
    hipWidth: calculateDistance3D(
      worldLandmarks[POSE_LANDMARKS.LEFT_HIP],
      worldLandmarks[POSE_LANDMARKS.RIGHT_HIP]
    ) * scale * 100,
    upperArmLength: {
      left: calculateDistance3D(
        worldLandmarks[POSE_LANDMARKS.LEFT_SHOULDER],
        worldLandmarks[POSE_LANDMARKS.LEFT_ELBOW]
      ) * scale * 100,
      right: calculateDistance3D(
        worldLandmarks[POSE_LANDMARKS.RIGHT_SHOULDER],
        worldLandmarks[POSE_LANDMARKS.RIGHT_ELBOW]
      ) * scale * 100
    },
    forearmLength: {
      left: calculateDistance3D(
        worldLandmarks[POSE_LANDMARKS.LEFT_ELBOW],
        worldLandmarks[POSE_LANDMARKS.LEFT_WRIST]
      ) * scale * 100,
      right: calculateDistance3D(
        worldLandmarks[POSE_LANDMARKS.RIGHT_ELBOW],
        worldLandmarks[POSE_LANDMARKS.RIGHT_WRIST]
      ) * scale * 100
    },
    thighLength: {
      left: calculateDistance3D(
        worldLandmarks[POSE_LANDMARKS.LEFT_HIP],
        worldLandmarks[POSE_LANDMARKS.LEFT_KNEE]
      ) * scale * 100,
      right: calculateDistance3D(
        worldLandmarks[POSE_LANDMARKS.RIGHT_HIP],
        worldLandmarks[POSE_LANDMARKS.RIGHT_KNEE]
      ) * scale * 100
    },
    shinLength: {
      left: calculateDistance3D(
        worldLandmarks[POSE_LANDMARKS.LEFT_KNEE],
        worldLandmarks[POSE_LANDMARKS.LEFT_ANKLE]
      ) * scale * 100,
      right: calculateDistance3D(
        worldLandmarks[POSE_LANDMARKS.RIGHT_KNEE],
        worldLandmarks[POSE_LANDMARKS.RIGHT_ANKLE]
      ) * scale * 100
    }
  }
}

// Estimate height from landmarks
function estimateHeight(landmarks: any[], scale: number): number {
  const nose = landmarks[POSE_LANDMARKS.NOSE]
  const leftAnkle = landmarks[POSE_LANDMARKS.LEFT_ANKLE]
  const rightAnkle = landmarks[POSE_LANDMARKS.RIGHT_ANKLE]
  
  if (!nose || !leftAnkle || !rightAnkle) return 170
  
  const ankleCenter = {
    x: (leftAnkle.x + rightAnkle.x) / 2,
    y: (leftAnkle.y + rightAnkle.y) / 2,
    z: (leftAnkle.z + rightAnkle.z) / 2
  }
  
  const noseToAnkle = Math.abs(nose.y - ankleCenter.y) * scale * 100
  return noseToAnkle * 1.1 // Account for head and feet
}

// Calculate torso length
function calculateTorsoLength(landmarks: any[], scale: number): number {
  const leftShoulder = landmarks[POSE_LANDMARKS.LEFT_SHOULDER]
  const rightShoulder = landmarks[POSE_LANDMARKS.RIGHT_SHOULDER]
  const leftHip = landmarks[POSE_LANDMARKS.LEFT_HIP]
  const rightHip = landmarks[POSE_LANDMARKS.RIGHT_HIP]
  
  if (!leftShoulder || !rightShoulder || !leftHip || !rightHip) return 50
  
  const shoulderCenter = {
    x: (leftShoulder.x + rightShoulder.x) / 2,
    y: (leftShoulder.y + rightShoulder.y) / 2,
    z: (leftShoulder.z + rightShoulder.z) / 2
  }
  
  const hipCenter = {
    x: (leftHip.x + rightHip.x) / 2,
    y: (leftHip.y + rightHip.y) / 2,
    z: (leftHip.z + rightHip.z) / 2
  }
  
  return calculateDistance3D(shoulderCenter, hipCenter) * scale * 100
}

// Calculate average measurements with outlier removal
function calculateAverageMeasurements(measurements: BodyMeasurements[]): BodyMeasurements {
  if (measurements.length === 0) {
    throw new Error('測定データがありません')
  }
  
  // Remove outliers using IQR method for height
  const heights = measurements.map(m => m.height).sort((a, b) => a - b)
  const q1 = heights[Math.floor(heights.length * 0.25)]
  const q3 = heights[Math.floor(heights.length * 0.75)]
  const iqr = q3 - q1
  const lowerBound = q1 - 1.5 * iqr
  const upperBound = q3 + 1.5 * iqr
  
  // Filter out outliers
  const validMeasurements = measurements.filter(m => 
    m.height >= lowerBound && m.height <= upperBound
  )
  
  if (validMeasurements.length === 0) {
    // If all measurements are outliers, use all measurements
    validMeasurements.push(...measurements)
  }
  
  // Calculate average
  const sum = validMeasurements.reduce((acc, curr) => {
    return {
      height: acc.height + curr.height,
      shoulderWidth: acc.shoulderWidth + curr.shoulderWidth,
      armLength: {
        left: acc.armLength.left + curr.armLength.left,
        right: acc.armLength.right + curr.armLength.right
      },
      legLength: {
        left: acc.legLength.left + curr.legLength.left,
        right: acc.legLength.right + curr.legLength.right
      },
      torsoLength: acc.torsoLength + curr.torsoLength,
      hipWidth: acc.hipWidth + curr.hipWidth,
      upperArmLength: {
        left: acc.upperArmLength.left + curr.upperArmLength.left,
        right: acc.upperArmLength.right + curr.upperArmLength.right
      },
      forearmLength: {
        left: acc.forearmLength.left + curr.forearmLength.left,
        right: acc.forearmLength.right + curr.forearmLength.right
      },
      thighLength: {
        left: acc.thighLength.left + curr.thighLength.left,
        right: acc.thighLength.right + curr.thighLength.right
      },
      shinLength: {
        left: acc.shinLength.left + curr.shinLength.left,
        right: acc.shinLength.right + curr.shinLength.right
      }
    }
  })
  
  const count = validMeasurements.length
  const roundToOne = (num: number) => Math.round(num * 10) / 10
  
  return {
    height: roundToOne(sum.height / count),
    shoulderWidth: roundToOne(sum.shoulderWidth / count),
    armLength: {
      left: roundToOne(sum.armLength.left / count),
      right: roundToOne(sum.armLength.right / count)
    },
    legLength: {
      left: roundToOne(sum.legLength.left / count),
      right: roundToOne(sum.legLength.right / count)
    },
    torsoLength: roundToOne(sum.torsoLength / count),
    hipWidth: roundToOne(sum.hipWidth / count),
    upperArmLength: {
      left: roundToOne(sum.upperArmLength.left / count),
      right: roundToOne(sum.upperArmLength.right / count)
    },
    forearmLength: {
      left: roundToOne(sum.forearmLength.left / count),
      right: roundToOne(sum.forearmLength.right / count)
    },
    thighLength: {
      left: roundToOne(sum.thighLength.left / count),
      right: roundToOne(sum.thighLength.right / count)
    },
    shinLength: {
      left: roundToOne(sum.shinLength.left / count),
      right: roundToOne(sum.shinLength.right / count)
    }
  }
}