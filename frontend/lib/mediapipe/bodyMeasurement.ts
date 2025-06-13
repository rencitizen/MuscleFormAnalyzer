import { Pose, Results } from '@mediapipe/pose'

// Body landmark indices based on MediaPipe Pose
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
  armLength: {
    left: number
    right: number
  }
  legLength: {
    left: number
    right: number
  }
  torsoLength: number
  hipWidth: number
  upperArmLength: {
    left: number
    right: number
  }
  forearmLength: {
    left: number
    right: number
  }
  thighLength: {
    left: number
    right: number
  }
  shinLength: {
    left: number
    right: number
  }
}

// 3Dランドマーク間の距離を計算
function calculateDistance3D(
  landmark1: { x: number; y: number; z: number },
  landmark2: { x: number; y: number; z: number }
): number {
  const dx = landmark2.x - landmark1.x
  const dy = landmark2.y - landmark1.y
  const dz = landmark2.z - landmark1.z
  return Math.sqrt(dx * dx + dy * dy + dz * dz)
}

// 実世界のスケールを推定（仮の実装）
// 実際にはカメラキャリブレーションや基準オブジェクトが必要
function estimateScale(landmarks: any[], imageWidth: number, imageHeight: number): number {
  // 平均的な人間の肩幅（約45cm）を基準として使用
  const leftShoulder = landmarks[POSE_LANDMARKS.LEFT_SHOULDER]
  const rightShoulder = landmarks[POSE_LANDMARKS.RIGHT_SHOULDER]
  
  if (!leftShoulder || !rightShoulder) return 1
  
  const shoulderWidthPixels = calculateDistance3D(leftShoulder, rightShoulder)
  const shoulderWidthNormalized = shoulderWidthPixels * Math.max(imageWidth, imageHeight)
  
  // 平均的な肩幅45cmと仮定してスケールを計算
  const scale = 45 / shoulderWidthNormalized
  return scale
}

// 動画からボディ測定を実行
export async function processVideoForBodyMeasurements(
  videoFile: File,
  onProgress?: (progress: number) => void
): Promise<BodyMeasurements> {
  return new Promise((resolve, reject) => {
    const video = document.createElement('video')
    video.src = URL.createObjectURL(videoFile)
    video.muted = true
    
    video.onloadedmetadata = async () => {
      try {
        const pose = new Pose({
          locateFile: (file) => {
            return `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`
          }
        })
        
        pose.setOptions({
          modelComplexity: 2,
          smoothLandmarks: true,
          enableSegmentation: false,
          smoothSegmentation: false,
          minDetectionConfidence: 0.5,
          minTrackingConfidence: 0.5
        })
        
        const measurements: BodyMeasurements[] = []
        let frameCount = 0
        const totalFrames = Math.min(30, video.duration * 10) // 最大30フレーム
        
        pose.onResults((results: Results) => {
          if (results.poseLandmarks && results.poseWorldLandmarks) {
            const scale = estimateScale(
              results.poseLandmarks,
              video.videoWidth,
              video.videoHeight
            )
            
            const worldLandmarks = results.poseWorldLandmarks
            
            // 各部位の測定
            const measurement: BodyMeasurements = {
              // 身長（頭頂部から足首までの推定）
              height: estimateHeight(worldLandmarks, scale),
              
              // 肩幅
              shoulderWidth: calculateDistance3D(
                worldLandmarks[POSE_LANDMARKS.LEFT_SHOULDER],
                worldLandmarks[POSE_LANDMARKS.RIGHT_SHOULDER]
              ) * scale * 100,
              
              // 腕の長さ（肩から手首）
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
              
              // 脚の長さ（腰から足首）
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
              
              // 胴体の長さ
              torsoLength: calculateTorsoLength(worldLandmarks, scale),
              
              // 腰幅
              hipWidth: calculateDistance3D(
                worldLandmarks[POSE_LANDMARKS.LEFT_HIP],
                worldLandmarks[POSE_LANDMARKS.RIGHT_HIP]
              ) * scale * 100,
              
              // 上腕の長さ
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
              
              // 前腕の長さ
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
              
              // 太ももの長さ
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
              
              // すねの長さ
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
            
            measurements.push(measurement)
            frameCount++
            
            if (onProgress) {
              onProgress((frameCount / totalFrames) * 100)
            }
          }
        })
        
        await pose.initialize()
        
        // 動画を複数フレームで処理
        const processFrame = async () => {
          if (frameCount >= totalFrames || video.currentTime >= video.duration) {
            // 測定結果の平均を計算
            const averageMeasurements = calculateAverageMeasurements(measurements)
            resolve(averageMeasurements)
            return
          }
          
          await pose.send({ image: video })
          video.currentTime += video.duration / totalFrames
          requestAnimationFrame(processFrame)
        }
        
        video.play()
        video.pause()
        video.currentTime = 0
        processFrame()
        
      } catch (error) {
        reject(error)
      }
    }
    
    video.onerror = () => {
      reject(new Error('動画の読み込みに失敗しました'))
    }
  })
}

// 身長を推定
function estimateHeight(landmarks: any[], scale: number): number {
  // 鼻から足首までの距離を基準に身長を推定
  const nose = landmarks[POSE_LANDMARKS.NOSE]
  const leftAnkle = landmarks[POSE_LANDMARKS.LEFT_ANKLE]
  const rightAnkle = landmarks[POSE_LANDMARKS.RIGHT_ANKLE]
  
  if (!nose || !leftAnkle || !rightAnkle) return 170 // デフォルト値
  
  // 両足首の中点を計算
  const ankleCenter = {
    x: (leftAnkle.x + rightAnkle.x) / 2,
    y: (leftAnkle.y + rightAnkle.y) / 2,
    z: (leftAnkle.z + rightAnkle.z) / 2
  }
  
  // 鼻から足首中点までの距離
  const noseToAnkle = Math.abs(nose.y - ankleCenter.y) * scale * 100
  
  // 頭頂部と足首下部を考慮して約1.1倍
  return noseToAnkle * 1.1
}

// 胴体の長さを計算
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

// 複数フレームの測定結果の平均を計算
function calculateAverageMeasurements(measurements: BodyMeasurements[]): BodyMeasurements {
  if (measurements.length === 0) {
    throw new Error('測定データがありません')
  }
  
  const sum = measurements.reduce((acc, curr) => {
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
  
  const count = measurements.length
  
  // 平均を計算して小数点第1位で丸める
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