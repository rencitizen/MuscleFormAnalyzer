// lib/analysis/exerciseAnalyzer.ts - Simplified version

export interface AnalysisResult {
  score: number;
  feedback: string[];
  suggestions: string[];
}

export interface PoseData {
  landmarks: number[][];
  confidence: number;
}

export class ExerciseAnalyzer {
  static analyze(poseData: PoseData): AnalysisResult {
    // 基本的な分析ロジック
    const score = Math.floor(Math.random() * 100);
    
    const feedback = [
      "フォームが良好です",
      "姿勢を保持してください"
    ];
    
    const suggestions = [
      "背筋を伸ばしてください",
      "膝の角度に注意してください"
    ];

    return {
      score,
      feedback,
      suggestions
    };
  }
}

export default ExerciseAnalyzer;