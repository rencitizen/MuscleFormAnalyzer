// MediaPipe Pose Landmark indices
export enum PoseLandmark {
  NOSE = 0,
  LEFT_EYE_INNER = 1,
  LEFT_EYE = 2,
  LEFT_EYE_OUTER = 3,
  RIGHT_EYE_INNER = 4,
  RIGHT_EYE = 5,
  RIGHT_EYE_OUTER = 6,
  LEFT_EAR = 7,
  RIGHT_EAR = 8,
  MOUTH_LEFT = 9,
  MOUTH_RIGHT = 10,
  LEFT_SHOULDER = 11,
  RIGHT_SHOULDER = 12,
  LEFT_ELBOW = 13,
  RIGHT_ELBOW = 14,
  LEFT_WRIST = 15,
  RIGHT_WRIST = 16,
  LEFT_PINKY = 17,
  RIGHT_PINKY = 18,
  LEFT_INDEX = 19,
  RIGHT_INDEX = 20,
  LEFT_THUMB = 21,
  RIGHT_THUMB = 22,
  LEFT_HIP = 23,
  RIGHT_HIP = 24,
  LEFT_KNEE = 25,
  RIGHT_KNEE = 26,
  LEFT_ANKLE = 27,
  RIGHT_ANKLE = 28,
  LEFT_HEEL = 29,
  RIGHT_HEEL = 30,
  LEFT_FOOT_INDEX = 31,
  RIGHT_FOOT_INDEX = 32,
}

export interface Landmark {
  x: number
  y: number
  z: number
  visibility?: number
}

export interface PoseResults {
  poseLandmarks: Landmark[]
  poseWorldLandmarks?: Landmark[]
  segmentationMask?: ImageData
}

export interface ExerciseType {
  id: 'squat' | 'deadlift' | 'bench_press'
  name: string
  description: string
}

export interface ExercisePhase {
  name: 'setup' | 'descent' | 'bottom' | 'ascent' | 'top'
  timestamp: number
  landmarks: Landmark[]
  angles: Record<string, number>
}

export interface RepAnalysis {
  phases: ExercisePhase[]
  scores: {
    overall: number
    [key: string]: number
  }
  feedback: string[]
  issues: string[]
}

export interface WorkoutSession {
  id: string
  userId: string
  exercise: ExerciseType['id']
  timestamp: Date
  reps: RepAnalysis[]
  userCalibration?: UserCalibration
  notes?: string
}

export interface UserCalibration {
  height: number // cm
  weight?: number // kg
  femurRatio?: number // 大腿骨比率
  tibiaRatio?: number // 脛骨比率
  armLength?: number // cm
  ankleMobility?: number // degrees
  shoulderWidth?: number // cm
  hipWidth?: number // cm
}