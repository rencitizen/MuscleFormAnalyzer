import { Pose, Results, NormalizedLandmark } from '@mediapipe/pose'

// Camera calibration types
interface CameraValidation {
  valid: boolean
  message?: string
  confidence: number
}

interface DistanceCorrection {
  correction: number
  method: 'eye_distance' | 'shoulder_width' | 'face_height'
}

interface HeightMeasurement {
  height: number
  confidence: number
  method: string
  timestamp: number
}

interface StableHeightResult {
  currentHeight: number
  stableHeight: number | null
  confidence: number
  recommendations: string[]
  calibrationStatus: 'uncalibrated' | 'calibrating' | 'calibrated'
}

interface ReferenceObject {
  detected: boolean
  object: string
  pixelDimensions: { width: number; height: number }
  realDimensions: { width: number; height: number }
}

// MediaPipe Pose landmarks
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

// Face mesh landmarks for better head detection
const FACE_LANDMARKS = {
  FOREHEAD_TOP: 10,
  FOREHEAD_CENTER: 9,
  NOSE_TIP: 1,
  CHIN: 152
}

/**
 * Camera calibration system for pose detection accuracy
 */
export class CameraCalibration {
  static validateCameraSetup(landmarks: NormalizedLandmark[]): CameraValidation {
    if (!landmarks || landmarks.length < 33) {
      return { valid: false, message: 'ポーズが検出されませんでした', confidence: 0 }
    }

    const nose = landmarks[POSE_LANDMARKS.NOSE]
    const leftEye = landmarks[POSE_LANDMARKS.LEFT_EYE]
    const rightEye = landmarks[POSE_LANDMARKS.RIGHT_EYE]

    if (!nose || !leftEye || !rightEye) {
      return { valid: false, message: '顔が正しく検出されませんでした', confidence: 0 }
    }

    // Check face angle
    const eyeDistance = Math.abs(leftEye.y - rightEye.y)
    const faceWidth = Math.abs(leftEye.x - rightEye.x)
    
    if (eyeDistance / faceWidth > 0.1) {
      return { 
        valid: false, 
        message: 'カメラを正面に向けてください。顔が傾いています。', 
        confidence: 0.5 
      }
    }

    // Check if person is too close or too far
    const shoulderWidth = this.calculateShoulderWidth(landmarks)
    if (shoulderWidth < 0.15) {
      return { 
        valid: false, 
        message: 'カメラから離れてください（2-3メートル推奨）', 
        confidence: 0.7 
      }
    }
    if (shoulderWidth > 0.4) {
      return { 
        valid: false, 
        message: 'カメラに近づいてください（2-3メートル推奨）', 
        confidence: 0.7 
      }
    }

    // Check visibility of key landmarks
    const keyLandmarks = [
      landmarks[POSE_LANDMARKS.NOSE],
      landmarks[POSE_LANDMARKS.LEFT_SHOULDER],
      landmarks[POSE_LANDMARKS.RIGHT_SHOULDER],
      landmarks[POSE_LANDMARKS.LEFT_HIP],
      landmarks[POSE_LANDMARKS.RIGHT_HIP],
      landmarks[POSE_LANDMARKS.LEFT_ANKLE],
      landmarks[POSE_LANDMARKS.RIGHT_ANKLE]
    ]

    const avgVisibility = keyLandmarks.reduce((sum, lm) => sum + (lm?.visibility || 0), 0) / keyLandmarks.length

    if (avgVisibility < 0.6) {
      return { 
        valid: false, 
        message: '全身が見えるようにカメラを調整してください', 
        confidence: avgVisibility 
      }
    }

    return { valid: true, confidence: avgVisibility }
  }

  static calculateShoulderWidth(landmarks: NormalizedLandmark[]): number {
    const leftShoulder = landmarks[POSE_LANDMARKS.LEFT_SHOULDER]
    const rightShoulder = landmarks[POSE_LANDMARKS.RIGHT_SHOULDER]
    
    if (!leftShoulder || !rightShoulder) return 0
    
    return Math.abs(rightShoulder.x - leftShoulder.x)
  }

  static calculateDistanceCorrection(landmarks: NormalizedLandmark[]): DistanceCorrection {
    // Method 1: Eye distance (most reliable for face)
    const leftEye = landmarks[POSE_LANDMARKS.LEFT_EYE]
    const rightEye = landmarks[POSE_LANDMARKS.RIGHT_EYE]
    
    if (leftEye && rightEye && leftEye.visibility! > 0.8 && rightEye.visibility! > 0.8) {
      const eyeDistance = Math.sqrt(
        Math.pow(rightEye.x - leftEye.x, 2) + 
        Math.pow(rightEye.y - leftEye.y, 2)
      )
      
      // Average interpupillary distance is 63mm
      const averageEyeDistance = 0.063 // 63mm in normalized coordinates at standard distance
      const correction = averageEyeDistance / eyeDistance
      
      return { correction, method: 'eye_distance' }
    }

    // Method 2: Shoulder width
    const shoulderWidth = this.calculateShoulderWidth(landmarks)
    if (shoulderWidth > 0) {
      // Average shoulder width is 40-45cm
      const averageShoulderWidth = 0.25 // Normalized for standard distance
      const correction = averageShoulderWidth / shoulderWidth
      
      return { correction, method: 'shoulder_width' }
    }

    // Default correction
    return { correction: 1.0, method: 'face_height' }
  }
}

/**
 * Improved height measurement with multiple methods
 */
export class ImprovedHeightMeasurement {
  /**
   * Find accurate head top position
   */
  static findAccurateHeadTop(landmarks: NormalizedLandmark[]): NormalizedLandmark {
    // Use multiple head landmarks to find the highest point
    const headLandmarks = [
      landmarks[FACE_LANDMARKS.FOREHEAD_TOP] || landmarks[POSE_LANDMARKS.NOSE],
      landmarks[FACE_LANDMARKS.FOREHEAD_CENTER] || landmarks[POSE_LANDMARKS.NOSE],
      landmarks[POSE_LANDMARKS.LEFT_EAR],
      landmarks[POSE_LANDMARKS.RIGHT_EAR]
    ].filter(lm => lm && lm.visibility! > 0.5)

    if (headLandmarks.length === 0) {
      // Fallback to nose with offset
      const nose = landmarks[POSE_LANDMARKS.NOSE]
      return {
        x: nose.x,
        y: nose.y - 0.05, // 5% offset upward
        z: nose.z,
        visibility: nose.visibility
      }
    }

    // Find the highest point (lowest y value)
    const headTop = headLandmarks.reduce((highest, current) => 
      current.y < highest.y ? current : highest
    )

    // Add small offset for hair
    return {
      x: headTop.x,
      y: headTop.y - 0.02, // 2% offset for hair
      z: headTop.z,
      visibility: headTop.visibility
    }
  }

  /**
   * Find accurate feet bottom position
   */
  static findAccurateFeet(landmarks: NormalizedLandmark[]): NormalizedLandmark {
    const feetLandmarks = [
      landmarks[POSE_LANDMARKS.LEFT_ANKLE],
      landmarks[POSE_LANDMARKS.RIGHT_ANKLE],
      landmarks[POSE_LANDMARKS.LEFT_HEEL],
      landmarks[POSE_LANDMARKS.RIGHT_HEEL],
      landmarks[POSE_LANDMARKS.LEFT_FOOT_INDEX],
      landmarks[POSE_LANDMARKS.RIGHT_FOOT_INDEX]
    ].filter(lm => lm && lm.visibility! > 0.3)

    if (feetLandmarks.length === 0) {
      // Fallback to ankles
      const leftAnkle = landmarks[POSE_LANDMARKS.LEFT_ANKLE]
      const rightAnkle = landmarks[POSE_LANDMARKS.RIGHT_ANKLE]
      
      if (leftAnkle && rightAnkle) {
        return {
          x: (leftAnkle.x + rightAnkle.x) / 2,
          y: Math.max(leftAnkle.y, rightAnkle.y),
          z: (leftAnkle.z! + rightAnkle.z!) / 2,
          visibility: (leftAnkle.visibility! + rightAnkle.visibility!) / 2
        }
      }
      
      return leftAnkle || rightAnkle || landmarks[0]
    }

    // Find the lowest point (highest y value)
    const feetBottom = feetLandmarks.reduce((lowest, current) => 
      current.y > lowest.y ? current : lowest
    )

    return feetBottom
  }

  /**
   * Calculate height with multiple correction methods
   */
  static calculateHeight(
    landmarks: NormalizedLandmark[], 
    frameHeight: number,
    referenceHeight: number | null = null,
    distanceCorrection: number = 1.0
  ): { height: number; method: string; confidence: number } {
    const headTop = this.findAccurateHeadTop(landmarks)
    const feetBottom = this.findAccurateFeet(landmarks)

    // Calculate pixel height
    const heightInPixels = Math.abs(feetBottom.y - headTop.y) * frameHeight

    // If reference height is provided, use it for calibration
    if (referenceHeight) {
      return {
        height: referenceHeight,
        method: 'user_calibrated',
        confidence: 1.0
      }
    }

    // Method 1: Body proportion based estimation
    const shoulderWidth = CameraCalibration.calculateShoulderWidth(landmarks)
    const proportionBasedHeight = (heightInPixels / shoulderWidth) * 0.26 * distanceCorrection

    // Method 2: Direct conversion with empirical factor
    const empiricalFactor = 2850 // Empirically determined for average setup
    const directHeight = (heightInPixels / frameHeight) * empiricalFactor * distanceCorrection

    // Method 3: Using torso length as reference
    const torsoHeight = this.calculateTorsoHeight(landmarks, frameHeight)
    const torsoBasedHeight = (heightInPixels / torsoHeight) * 0.52 * distanceCorrection

    // Combine methods with confidence weighting
    const avgConfidence = (headTop.visibility! + feetBottom.visibility!) / 2

    // Use the most reliable method based on landmark visibility
    if (shoulderWidth > 0.15 && shoulderWidth < 0.4) {
      return {
        height: proportionBasedHeight,
        method: 'proportion_based',
        confidence: avgConfidence * 0.9
      }
    } else if (torsoHeight > 0) {
      return {
        height: torsoBasedHeight,
        method: 'torso_based',
        confidence: avgConfidence * 0.85
      }
    } else {
      return {
        height: directHeight,
        method: 'direct_conversion',
        confidence: avgConfidence * 0.7
      }
    }
  }

  private static calculateTorsoHeight(landmarks: NormalizedLandmark[], frameHeight: number): number {
    const leftShoulder = landmarks[POSE_LANDMARKS.LEFT_SHOULDER]
    const rightShoulder = landmarks[POSE_LANDMARKS.RIGHT_SHOULDER]
    const leftHip = landmarks[POSE_LANDMARKS.LEFT_HIP]
    const rightHip = landmarks[POSE_LANDMARKS.RIGHT_HIP]

    if (!leftShoulder || !rightShoulder || !leftHip || !rightHip) return 0

    const shoulderY = (leftShoulder.y + rightShoulder.y) / 2
    const hipY = (leftHip.y + rightHip.y) / 2

    return Math.abs(hipY - shoulderY) * frameHeight
  }
}

/**
 * Reference object detection for calibration
 */
export class ReferenceObjectCalibration {
  static commonObjects = {
    creditCard: { width: 85.6, height: 53.98 }, // mm
    smartphone: { width: 71, height: 144 }, // iPhone average in mm
    coin100yen: { diameter: 26.5 }, // 100円硬貨 in mm
    bottle500ml: { height: 205 }, // 500ml PET bottle in mm
    a4Paper: { width: 210, height: 297 } // A4 paper in mm
  }

  static async detectReferenceObject(frame: HTMLVideoElement | HTMLCanvasElement): Promise<ReferenceObject | null> {
    // This is a placeholder for actual object detection
    // In production, you would use TensorFlow.js or similar for object detection
    
    // For now, return null to indicate no object detected
    return null
  }

  static calibrateWithReference(referenceData: ReferenceObject): number {
    const pixelToMmRatio = referenceData.realDimensions.width / referenceData.pixelDimensions.width
    return pixelToMmRatio / 10 // Convert to cm
  }
}

/**
 * Multi-frame measurement for stability
 */
export class MultiFrameHeightMeasurement {
  private measurements: HeightMeasurement[] = []
  private readonly maxMeasurements = 30

  addMeasurement(height: number, confidence: number, method: string): void {
    this.measurements.push({
      height,
      confidence,
      method,
      timestamp: Date.now()
    })

    // Remove old measurements
    if (this.measurements.length > this.maxMeasurements) {
      this.measurements.shift()
    }
  }

  getStableHeight(): number | null {
    if (this.measurements.length < 10) {
      return null // Not enough data
    }

    // Filter by confidence
    const reliableMeasurements = this.measurements.filter(m => m.confidence > 0.7)
    
    if (reliableMeasurements.length < 5) {
      return null
    }

    // Sort heights
    const heights = reliableMeasurements.map(m => m.height).sort((a, b) => a - b)

    // Remove outliers using IQR method
    const q1 = heights[Math.floor(heights.length * 0.25)]
    const q3 = heights[Math.floor(heights.length * 0.75)]
    const iqr = q3 - q1
    const lowerBound = q1 - 1.5 * iqr
    const upperBound = q3 + 1.5 * iqr

    const filteredHeights = heights.filter(h => h >= lowerBound && h <= upperBound)

    if (filteredHeights.length === 0) {
      return heights[Math.floor(heights.length / 2)] // Return median if all are outliers
    }

    // Return median of filtered heights
    return filteredHeights[Math.floor(filteredHeights.length / 2)]
  }

  getConfidence(): number {
    if (this.measurements.length < 5) return 0

    const recentMeasurements = this.measurements.slice(-10)
    const heights = recentMeasurements.map(m => m.height)
    
    // Calculate standard deviation
    const mean = heights.reduce((sum, h) => sum + h, 0) / heights.length
    const variance = heights.reduce((sum, h) => sum + Math.pow(h - mean, 2), 0) / heights.length
    const stdDev = Math.sqrt(variance)

    // Convert to confidence (lower std dev = higher confidence)
    const cv = stdDev / mean // Coefficient of variation
    const confidence = Math.max(0, Math.min(1, 1 - cv * 5))

    return confidence
  }

  clear(): void {
    this.measurements = []
  }
}

/**
 * User calibration system
 */
export class UserCalibrationSystem {
  static createCalibrationSteps() {
    return [
      {
        id: 'distance',
        instruction: 'カメラから2-3メートル離れて立ってください',
        validation: (landmarks: NormalizedLandmark[]) => {
          const shoulderWidth = CameraCalibration.calculateShoulderWidth(landmarks)
          return shoulderWidth > 0.15 && shoulderWidth < 0.35
        }
      },
      {
        id: 'posture',
        instruction: '壁に背中をつけて、背筋を伸ばして直立してください',
        validation: (landmarks: NormalizedLandmark[]) => this.validatePosture(landmarks)
      },
      {
        id: 'visibility',
        instruction: '全身（頭から足まで）がカメラに映るようにしてください',
        validation: (landmarks: NormalizedLandmark[]) => this.validateFullBodyVisible(landmarks)
      },
      {
        id: 'input',
        instruction: '実際の身長を入力してください',
        input: {
          type: 'number',
          placeholder: '170',
          unit: 'cm',
          min: 50,
          max: 250
        }
      }
    ]
  }

  static validatePosture(landmarks: NormalizedLandmark[]): boolean {
    const leftShoulder = landmarks[POSE_LANDMARKS.LEFT_SHOULDER]
    const rightShoulder = landmarks[POSE_LANDMARKS.RIGHT_SHOULDER]
    const leftHip = landmarks[POSE_LANDMARKS.LEFT_HIP]
    const rightHip = landmarks[POSE_LANDMARKS.RIGHT_HIP]

    if (!leftShoulder || !rightShoulder || !leftHip || !rightHip) return false

    // Check shoulder tilt
    const shoulderTilt = Math.abs(leftShoulder.y - rightShoulder.y)
    const hipTilt = Math.abs(leftHip.y - rightHip.y)

    // Check if person is standing straight
    const shoulderCenterX = (leftShoulder.x + rightShoulder.x) / 2
    const hipCenterX = (leftHip.x + rightHip.x) / 2
    const bodyLean = Math.abs(shoulderCenterX - hipCenterX)

    return shoulderTilt < 0.02 && hipTilt < 0.02 && bodyLean < 0.03
  }

  static validateFullBodyVisible(landmarks: NormalizedLandmark[]): boolean {
    const requiredLandmarks = [
      POSE_LANDMARKS.NOSE,
      POSE_LANDMARKS.LEFT_SHOULDER,
      POSE_LANDMARKS.RIGHT_SHOULDER,
      POSE_LANDMARKS.LEFT_HIP,
      POSE_LANDMARKS.RIGHT_HIP,
      POSE_LANDMARKS.LEFT_ANKLE,
      POSE_LANDMARKS.RIGHT_ANKLE
    ]

    for (const landmarkIdx of requiredLandmarks) {
      const landmark = landmarks[landmarkIdx]
      if (!landmark || landmark.visibility! < 0.5) {
        return false
      }
    }

    return true
  }
}

/**
 * Main accurate height measurement system
 */
export class AccurateHeightMeasurement {
  private multiFrameMeasurement = new MultiFrameHeightMeasurement()
  private calibrationData: number | null = null
  private userHeight: number | null = null
  private pose: Pose | null = null
  private isCalibrated = false

  async initialize(): Promise<void> {
    this.pose = new Pose({
      locateFile: (file) => {
        return `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`
      }
    })

    this.pose.setOptions({
      modelComplexity: 2,
      smoothLandmarks: true,
      enableSegmentation: false,
      smoothSegmentation: false,
      minDetectionConfidence: 0.5,
      minTrackingConfidence: 0.5
    })

    await this.pose.initialize()
  }

  async measureHeight(
    videoFrame: HTMLVideoElement | HTMLCanvasElement,
    userInputHeight: number | null = null
  ): Promise<StableHeightResult> {
    if (!this.pose) {
      throw new Error('AccurateHeightMeasurement not initialized. Call initialize() first.')
    }

    // Send frame to MediaPipe
    await this.pose.send({ image: videoFrame })

    return new Promise((resolve) => {
      this.pose!.onResults((results: Results) => {
        if (!results.poseLandmarks) {
          resolve({
            currentHeight: 0,
            stableHeight: null,
            confidence: 0,
            recommendations: ['ポーズが検出されませんでした。全身がカメラに映るようにしてください。'],
            calibrationStatus: 'uncalibrated'
          })
          return
        }

        const landmarks = results.poseLandmarks

        // Validate camera setup
        const cameraValidation = CameraCalibration.validateCameraSetup(landmarks)
        if (!cameraValidation.valid) {
          resolve({
            currentHeight: 0,
            stableHeight: null,
            confidence: cameraValidation.confidence,
            recommendations: [cameraValidation.message!],
            calibrationStatus: 'uncalibrated'
          })
          return
        }

        // Calculate distance correction
        const distanceCorrection = CameraCalibration.calculateDistanceCorrection(landmarks)

        // Handle user calibration
        if (userInputHeight) {
          this.userHeight = userInputHeight
          this.isCalibrated = true
          
          // Calculate calibration factor
          const measuredResult = ImprovedHeightMeasurement.calculateHeight(
            landmarks,
            videoFrame.height,
            null,
            distanceCorrection.correction
          )
          
          this.calibrationData = userInputHeight / measuredResult.height
        }

        // Measure height
        let measuredResult = ImprovedHeightMeasurement.calculateHeight(
          landmarks,
          videoFrame.height,
          this.userHeight,
          distanceCorrection.correction
        )

        // Apply calibration if available
        if (this.calibrationData && !this.userHeight) {
          measuredResult.height *= this.calibrationData
        }

        // Add to multi-frame measurement
        this.multiFrameMeasurement.addMeasurement(
          measuredResult.height,
          measuredResult.confidence,
          measuredResult.method
        )

        // Get stable height
        const stableHeight = this.multiFrameMeasurement.getStableHeight()
        const overallConfidence = this.multiFrameMeasurement.getConfidence()

        // Generate recommendations
        const recommendations = this.getRecommendations(
          landmarks,
          measuredResult.confidence,
          overallConfidence
        )

        resolve({
          currentHeight: Math.round(measuredResult.height),
          stableHeight: stableHeight ? Math.round(stableHeight) : null,
          confidence: overallConfidence,
          recommendations,
          calibrationStatus: this.isCalibrated ? 'calibrated' : 
                           stableHeight ? 'calibrating' : 'uncalibrated'
        })
      })
    })
  }

  private getRecommendations(
    landmarks: NormalizedLandmark[],
    currentConfidence: number,
    overallConfidence: number
  ): string[] {
    const recommendations: string[] = []

    if (overallConfidence < 0.7) {
      recommendations.push('測定精度を上げるため、明るい場所で撮影してください')
    }

    if (!UserCalibrationSystem.validatePosture(landmarks)) {
      recommendations.push('背筋を伸ばして直立してください')
    }

    if (!UserCalibrationSystem.validateFullBodyVisible(landmarks)) {
      recommendations.push('全身（頭から足まで）がカメラに映るようにしてください')
    }

    if (!this.isCalibrated) {
      recommendations.push('より正確な測定のため、実際の身長を入力して較正することをお勧めします')
    }

    if (recommendations.length === 0 && overallConfidence > 0.85) {
      recommendations.push('測定条件は良好です')
    }

    return recommendations
  }

  reset(): void {
    this.multiFrameMeasurement.clear()
    this.calibrationData = null
    this.userHeight = null
    this.isCalibrated = false
  }

  async cleanup(): Promise<void> {
    if (this.pose) {
      this.pose.close()
      this.pose = null
    }
  }
}

// Export a singleton instance
export const heightMeasurementSystem = new AccurateHeightMeasurement()