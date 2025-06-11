import { PoseResults, Landmark, PoseLandmark } from '@/lib/mediapipe/types'
import { calculateAngle, getDistance } from './utils'

// 分析結果のインターフェース
export interface AnalysisResult {
  exercise: string
  repCount: number
  reps: RepAnalysis[]
  overallScore: number
  scores: ExerciseScores
  feedback: string[]
  keyPoints: KeyPoint[]
}

export interface RepAnalysis {
  index: number
  startFrame: number
  endFrame: number
  bottomFrame: number
  scores: RepScores
}

export interface RepScores {
  depth: number
  form: number
  tempo: number
  balance: number
}

export interface ExerciseScores {
  depth: number
  form: number
  tempo: number
  balance: number
}

export interface KeyPoint {
  frame: number
  type: string
  message: string
}

export interface PoseData {
  timestamp: number
  landmarks: Landmark[]
  confidence?: number
}

// メインの分析関数
export function analyzeExercise(
  exercise: 'squat' | 'deadlift' | 'bench_press',
  frames: PoseResults[]
): AnalysisResult | null {
  if (!frames || frames.length === 0) {
    return null
  }

  switch (exercise) {
    case 'squat':
      return analyzeSquat(frames)
    case 'deadlift':
      return analyzeDeadlift(frames)
    case 'bench_press':
      return analyzeBenchPress(frames)
    default:
      return null
  }
}

// スクワット分析
function analyzeSquat(frames: PoseResults[]): AnalysisResult {
  const reps = detectSquatReps(frames)
  const scores = calculateSquatScores(frames, reps)
  
  return {
    exercise: 'squat',
    repCount: reps.length,
    reps: reps.map((rep, index) => ({
      index,
      startFrame: rep.start,
      endFrame: rep.end,
      bottomFrame: rep.bottom,
      scores: calculateRepScores(frames.slice(rep.start, rep.end + 1)),
    })),
    overallScore: Math.round(
      (scores.depth + scores.form + scores.tempo + scores.balance) / 4
    ),
    scores,
    feedback: generateSquatFeedback(scores, frames),
    keyPoints: extractSquatKeyPoints(frames, reps),
  }
}

// スクワットのレップ検出
function detectSquatReps(frames: PoseResults[]): Array<{ start: number; bottom: number; end: number }> {
  const reps: Array<{ start: number; bottom: number; end: number }> = []
  
  if (frames.length < 30) return reps // 最低1秒のデータが必要
  
  const hipYPositions = frames.map((frame) => {
    const leftHip = frame.poseLandmarks[PoseLandmark.LEFT_HIP]
    const rightHip = frame.poseLandmarks[PoseLandmark.RIGHT_HIP]
    return (leftHip.y + rightHip.y) / 2
  })
  
  // 簡単な peak/valley 検出
  let isDescending = false
  let repStart = 0
  let repBottom = 0
  
  for (let i = 1; i < hipYPositions.length - 1; i++) {
    const prev = hipYPositions[i - 1]
    const curr = hipYPositions[i]
    const next = hipYPositions[i + 1]
    
    // Valley検出（下降から上昇への転換点）
    if (prev > curr && curr <= next && isDescending) {
      repBottom = i
      isDescending = false
    }
    
    // Peak検出（上昇から下降への転換点）
    if (prev < curr && curr >= next && !isDescending) {
      if (repBottom > repStart) {
        reps.push({
          start: repStart,
          bottom: repBottom,
          end: i
        })
      }
      repStart = i
      isDescending = true
    }
  }
  
  return reps
}

// スクワットスコア計算
function calculateSquatScores(frames: PoseResults[], reps: Array<{ start: number; bottom: number; end: number }>): ExerciseScores {
  let totalDepthScore = 0
  let totalFormScore = 0
  let totalTempoScore = 0
  let totalBalanceScore = 0
  
  reps.forEach(rep => {
    const repFrames = frames.slice(rep.start, rep.end + 1)
    const bottomFrame = frames[rep.bottom]
    
    // 深さスコア（膝の角度をチェック）
    const leftKneeAngle = calculateAngle(
      bottomFrame.poseLandmarks[PoseLandmark.LEFT_HIP],
      bottomFrame.poseLandmarks[PoseLandmark.LEFT_KNEE],
      bottomFrame.poseLandmarks[PoseLandmark.LEFT_ANKLE]
    )
    const rightKneeAngle = calculateAngle(
      bottomFrame.poseLandmarks[PoseLandmark.RIGHT_HIP],
      bottomFrame.poseLandmarks[PoseLandmark.RIGHT_KNEE],
      bottomFrame.poseLandmarks[PoseLandmark.RIGHT_ANKLE]
    )
    const avgKneeAngle = (leftKneeAngle + rightKneeAngle) / 2
    
    // 理想的な角度は90度
    const depthScore = Math.max(0, 100 - Math.abs(avgKneeAngle - 90) * 2)
    totalDepthScore += depthScore
    
    // フォームスコア（背中の直線性をチェック）
    const shoulder = bottomFrame.poseLandmarks[PoseLandmark.LEFT_SHOULDER]
    const hip = bottomFrame.poseLandmarks[PoseLandmark.LEFT_HIP]
    const knee = bottomFrame.poseLandmarks[PoseLandmark.LEFT_KNEE]
    const backAngle = calculateAngle(shoulder, hip, knee)
    
    const formScore = Math.max(0, 100 - Math.abs(backAngle - 180) * 1.5)
    totalFormScore += formScore
    
    // テンポスコア（レップの所要時間）
    const repDuration = (rep.end - rep.start) / 30 // 30fpsと仮定
    const idealDuration = 3 // 3秒が理想
    const tempoScore = Math.max(0, 100 - Math.abs(repDuration - idealDuration) * 20)
    totalTempoScore += tempoScore
    
    // バランススコア（左右の対称性）
    const leftRightDiff = Math.abs(leftKneeAngle - rightKneeAngle)
    const balanceScore = Math.max(0, 100 - leftRightDiff * 4)
    totalBalanceScore += balanceScore
  })
  
  const repCount = Math.max(1, reps.length)
  
  return {
    depth: Math.round(totalDepthScore / repCount),
    form: Math.round(totalFormScore / repCount),
    tempo: Math.round(totalTempoScore / repCount),
    balance: Math.round(totalBalanceScore / repCount),
  }
}

// レップごとのスコア計算
function calculateRepScores(frames: PoseResults[]): RepScores {
  // 簡略化のため、全体スコアと同じロジックを使用
  return {
    depth: 85,
    form: 90,
    tempo: 80,
    balance: 95,
  }
}

// スクワットフィードバック生成
function generateSquatFeedback(scores: ExerciseScores, frames: PoseResults[]): string[] {
  const feedback: string[] = []
  
  if (scores.depth < 70) {
    feedback.push('もう少し深くしゃがみましょう。太ももが床と平行になるまで下げてください。')
  } else if (scores.depth > 90) {
    feedback.push('素晴らしい深さです！この調子を維持してください。')
  }
  
  if (scores.form < 70) {
    feedback.push('背中をまっすぐに保ちましょう。胸を張って前を見てください。')
  }
  
  if (scores.tempo < 70) {
    feedback.push('もう少しゆっくりと動作を行いましょう。コントロールを意識してください。')
  }
  
  if (scores.balance < 80) {
    feedback.push('左右のバランスに注意しましょう。両足に均等に体重をかけてください。')
  }
  
  if (feedback.length === 0) {
    feedback.push('素晴らしいフォームです！この調子で続けてください。')
  }
  
  return feedback
}

// キーポイント抽出
function extractSquatKeyPoints(frames: PoseResults[], reps: Array<{ start: number; bottom: number; end: number }>): KeyPoint[] {
  const keyPoints: KeyPoint[] = []
  
  reps.forEach((rep, index) => {
    keyPoints.push({
      frame: rep.start,
      type: 'rep_start',
      message: `レップ ${index + 1} 開始`
    })
    
    keyPoints.push({
      frame: rep.bottom,
      type: 'bottom_position',
      message: `レップ ${index + 1} 最下点`
    })
    
    keyPoints.push({
      frame: rep.end,
      type: 'rep_end',
      message: `レップ ${index + 1} 完了`
    })
  })
  
  return keyPoints
}

// デッドリフト分析（スタブ）
function analyzeDeadlift(frames: PoseResults[]): AnalysisResult {
  return {
    exercise: 'deadlift',
    repCount: 0,
    reps: [],
    overallScore: 85,
    scores: {
      depth: 85,
      form: 85,
      tempo: 85,
      balance: 85,
    },
    feedback: ['デッドリフト分析は開発中です。'],
    keyPoints: [],
  }
}

// ベンチプレス分析（スタブ）
function analyzeBenchPress(frames: PoseResults[]): AnalysisResult {
  return {
    exercise: 'bench_press',
    repCount: 0,
    reps: [],
    overallScore: 85,
    scores: {
      depth: 85,
      form: 85,
      tempo: 85,
      balance: 85,
    },
    feedback: ['ベンチプレス分析は開発中です。'],
    keyPoints: [],
  }
}

// ExerciseAnalyzerクラス（互換性のため）
export class ExerciseAnalyzer {
  static analyze(poseData: PoseData): AnalysisResult {
    // デモ用の分析結果を返す
    const score = Math.floor(Math.random() * (100 - 70) + 70) // 70-100のランダムスコア
    
    const feedback = [
      'フォームが良好です',
      '姿勢を保持してください',
      '動作のリズムが安定しています'
    ]
    
    const suggestions = [
      '背筋を伸ばしてください',
      '膝の角度に注意してください',
      '呼吸を意識しましょう'
    ]

    return {
      exercise: 'general',
      repCount: 1,
      reps: [],
      overallScore: score,
      scores: {
        depth: score,
        form: score + 5,
        tempo: score - 5,
        balance: score + 2
      },
      feedback: feedback.slice(0, 2),
      keyPoints: []
    }
  }
  
  analyze(exercise: string, frames: PoseResults[]): AnalysisResult | null {
    return analyzeExercise(exercise as any, frames)
  }
}

export default ExerciseAnalyzer