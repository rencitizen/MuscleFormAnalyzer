import { UserCalibration, Landmark, PoseLandmark } from '../mediapipe/types'
import { calculateAngle, getDistance } from '../analysis/utils'

export interface PersonalizedRecommendation {
  exercise: 'squat' | 'deadlift' | 'bench_press'
  adjustments: {
    stanceWidth?: number // cm
    footAngle?: number // degrees
    depthTarget?: number // degrees (knee angle)
    gripWidth?: number // cm
    elbowAngle?: number // degrees
  }
  rationale: string[]
}

export class PersonalizedSquatAnalyzer {
  private calibration: UserCalibration

  constructor(calibration: UserCalibration) {
    this.calibration = calibration
  }

  /**
   * 身体測定から個人に最適化されたスクワットパラメータを計算
   */
  calculateOptimalSquatParameters(): PersonalizedRecommendation {
    const adjustments: any = {}
    const rationale: string[] = []

    // 1. スタンス幅の計算
    const heightCm = this.calibration.height
    const femurRatio = this.calibration.femurRatio || this.estimateFemurRatio(heightCm)
    
    // 基本スタンス幅: 肩幅の1.2-1.5倍
    const shoulderWidth = this.calibration.shoulderWidth || heightCm * 0.25
    let optimalStance = shoulderWidth * 1.3

    // 大腿骨が長い場合は広めのスタンスを推奨
    if (femurRatio > 0.27) {
      optimalStance = shoulderWidth * 1.4
      rationale.push('大腿骨が長めなので、スタンスを広めに設定しました')
    } else if (femurRatio < 0.24) {
      optimalStance = shoulderWidth * 1.2
      rationale.push('大腿骨が短めなので、スタンスを狭めに設定しました')
    }

    adjustments.stanceWidth = Math.round(optimalStance)

    // 2. 足の角度の計算
    const ankleMobility = this.calibration.ankleMobility || 25
    let footAngle = 15 // デフォルト15度外旋

    if (ankleMobility < 20) {
      footAngle = 25
      rationale.push('足首の柔軟性が低いため、つま先を外側に向けることを推奨します')
    } else if (ankleMobility > 35) {
      footAngle = 10
      rationale.push('足首の柔軟性が高いため、より前向きなスタンスが可能です')
    }

    adjustments.footAngle = footAngle

    // 3. 目標深度の計算
    let targetKneeAngle = 90 // デフォルト90度

    // 身長と大腿骨比率から調整
    if (heightCm > 180 && femurRatio > 0.26) {
      targetKneeAngle = 95
      rationale.push('身長と脚の長さを考慮し、少し浅めの深度を推奨します')
    } else if (heightCm < 165 && femurRatio < 0.25) {
      targetKneeAngle = 85
      rationale.push('より深いスクワットが可能な体型です')
    }

    // 足首の柔軟性による調整
    if (ankleMobility < 20) {
      targetKneeAngle = Math.max(targetKneeAngle, 100)
      rationale.push('足首の柔軟性を考慮し、無理のない深度に調整しました')
    }

    adjustments.depthTarget = targetKneeAngle

    return {
      exercise: 'squat',
      adjustments,
      rationale,
    }
  }

  /**
   * リアルタイムでフォームを個人に合わせて評価
   */
  evaluatePersonalizedForm(landmarks: Landmark[]): {
    score: number
    feedback: string[]
    deviations: Record<string, number>
  } {
    const feedback: string[] = []
    const deviations: Record<string, number> = {}
    let totalScore = 100

    const params = this.calculateOptimalSquatParameters()

    // 1. スタンス幅の評価
    const leftAnkle = landmarks[PoseLandmark.LEFT_ANKLE]
    const rightAnkle = landmarks[PoseLandmark.RIGHT_ANKLE]
    const actualStance = getDistance(leftAnkle, rightAnkle) * this.calibration.height // cmに変換

    const stanceDeviation = Math.abs(actualStance - params.adjustments.stanceWidth!)
    deviations.stanceWidth = stanceDeviation

    if (stanceDeviation > 10) {
      totalScore -= 10
      if (actualStance > params.adjustments.stanceWidth!) {
        feedback.push('スタンスが広すぎます。少し狭めてみましょう')
      } else {
        feedback.push('スタンスが狭すぎます。もう少し広げてみましょう')
      }
    }

    // 2. 膝の角度評価
    const kneeAngle = calculateAngle(
      landmarks[PoseLandmark.LEFT_HIP],
      landmarks[PoseLandmark.LEFT_KNEE],
      landmarks[PoseLandmark.LEFT_ANKLE]
    )

    const depthDeviation = Math.abs(kneeAngle - params.adjustments.depthTarget!)
    deviations.depth = depthDeviation

    if (depthDeviation > 15) {
      totalScore -= 15
      if (kneeAngle > params.adjustments.depthTarget!) {
        feedback.push('もう少し深くしゃがむことができます')
      } else {
        feedback.push('深すぎる可能性があります。少し浅くしても大丈夫です')
      }
    }

    // 3. 膝の軌道評価（個人の骨格に基づく）
    const kneeTrackingScore = this.evaluateKneeTracking(landmarks)
    totalScore -= (100 - kneeTrackingScore)

    return {
      score: Math.max(0, totalScore),
      feedback,
      deviations,
    }
  }

  private evaluateKneeTracking(landmarks: Landmark[]): number {
    // 膝がつま先の方向に向いているかを評価
    const leftKnee = landmarks[PoseLandmark.LEFT_KNEE]
    const leftAnkle = landmarks[PoseLandmark.LEFT_ANKLE]
    const leftToe = landmarks[PoseLandmark.LEFT_FOOT_INDEX]

    // 膝-足首-つま先の角度を計算
    const kneeAlignment = calculateAngle(leftKnee, leftAnkle, leftToe)
    
    // 理想は180度に近い（一直線）
    const deviation = Math.abs(180 - kneeAlignment)
    
    if (deviation < 10) return 100
    if (deviation < 20) return 90
    if (deviation < 30) return 80
    return 70
  }

  private estimateFemurRatio(heightCm: number): number {
    // 身長から大腿骨比率を推定（統計的な平均値）
    if (heightCm < 160) return 0.24
    if (heightCm < 170) return 0.25
    if (heightCm < 180) return 0.26
    return 0.27
  }
}

export class PersonalizedDeadliftAnalyzer {
  private calibration: UserCalibration

  constructor(calibration: UserCalibration) {
    this.calibration = calibration
  }

  calculateOptimalDeadliftParameters(): PersonalizedRecommendation {
    const adjustments: any = {}
    const rationale: string[] = []

    // 1. スタンス幅（コンベンショナル vs スモウ）
    const heightCm = this.calibration.height
    const femurRatio = this.calibration.femurRatio || this.estimateFemurRatio(heightCm)
    const armLength = this.calibration.armLength || heightCm * 0.45
    
    // 腕が短い、または大腿骨が長い場合はスモウを推奨
    const armToLegRatio = armLength / (heightCm * femurRatio)
    
    if (armToLegRatio < 1.7) {
      adjustments.stanceWidth = this.calibration.shoulderWidth! * 1.5
      rationale.push('体型的にスモウデッドリフトが適しています')
    } else {
      adjustments.stanceWidth = this.calibration.shoulderWidth! * 0.8
      rationale.push('コンベンショナルデッドリフトが適しています')
    }

    // 2. グリップ幅
    adjustments.gripWidth = adjustments.stanceWidth + 10
    
    return {
      exercise: 'deadlift',
      adjustments,
      rationale,
    }
  }

  private estimateFemurRatio(heightCm: number): number {
    if (heightCm < 160) return 0.24
    if (heightCm < 170) return 0.25
    if (heightCm < 180) return 0.26
    return 0.27
  }
}

export class PersonalizedBenchPressAnalyzer {
  private calibration: UserCalibration

  constructor(calibration: UserCalibration) {
    this.calibration = calibration
  }

  calculateOptimalBenchPressParameters(): PersonalizedRecommendation {
    const adjustments: any = {}
    const rationale: string[] = []

    // 1. グリップ幅の計算
    const shoulderWidth = this.calibration.shoulderWidth || this.calibration.height * 0.25
    const armLength = this.calibration.armLength || this.calibration.height * 0.45
    
    // 基本グリップ幅: 肩幅の1.5-2倍
    let optimalGrip = shoulderWidth * 1.6
    
    // 腕が長い場合は広めのグリップ
    if (armLength > this.calibration.height * 0.47) {
      optimalGrip = shoulderWidth * 1.8
      rationale.push('腕が長めなので、グリップを広めに設定しました')
    } else if (armLength < this.calibration.height * 0.43) {
      optimalGrip = shoulderWidth * 1.5
      rationale.push('腕が短めなので、グリップを狭めに設定しました')
    }
    
    adjustments.gripWidth = Math.round(optimalGrip)

    // 2. 肘の角度
    adjustments.elbowAngle = 60 // 60度が標準
    
    if (shoulderWidth > this.calibration.height * 0.27) {
      adjustments.elbowAngle = 70
      rationale.push('肩幅が広いため、肘をやや開き気味にすることを推奨します')
    }

    return {
      exercise: 'bench_press',
      adjustments,
      rationale,
    }
  }
}

// 自動測定用の関数
export async function autoMeasureBodyDimensions(
  landmarks: Landmark[],
  heightCm: number
): Promise<Partial<UserCalibration>> {
  const measurements: Partial<UserCalibration> = {
    height: heightCm,
  }

  // 肩幅の計算
  const leftShoulder = landmarks[PoseLandmark.LEFT_SHOULDER]
  const rightShoulder = landmarks[PoseLandmark.RIGHT_SHOULDER]
  const shoulderWidthNormalized = getDistance(leftShoulder, rightShoulder)
  measurements.shoulderWidth = shoulderWidthNormalized * heightCm

  // 腰幅の計算
  const leftHip = landmarks[PoseLandmark.LEFT_HIP]
  const rightHip = landmarks[PoseLandmark.RIGHT_HIP]
  const hipWidthNormalized = getDistance(leftHip, rightHip)
  measurements.hipWidth = hipWidthNormalized * heightCm

  // 大腿骨比率の推定
  const leftKnee = landmarks[PoseLandmark.LEFT_KNEE]
  const femurLengthNormalized = getDistance(leftHip, leftKnee)
  measurements.femurRatio = femurLengthNormalized

  // 腕の長さの推定
  const leftElbow = landmarks[PoseLandmark.LEFT_ELBOW]
  const leftWrist = landmarks[PoseLandmark.LEFT_WRIST]
  const upperArmLength = getDistance(leftShoulder, leftElbow)
  const forearmLength = getDistance(leftElbow, leftWrist)
  const armLengthNormalized = upperArmLength + forearmLength
  measurements.armLength = armLengthNormalized * heightCm

  // 脛骨比率の推定
  const leftAnkle = landmarks[PoseLandmark.LEFT_ANKLE]
  const tibiaLengthNormalized = getDistance(leftKnee, leftAnkle)
  measurements.tibiaRatio = tibiaLengthNormalized

  return measurements
}