/**
 * 包括的分析データ統合システム
 * 身体計測、栄養状況、トレーニング履歴、目標設定を統合
 */

export interface BodyMetrics {
  height: number;
  weight: number;
  bodyFat: number;
  muscleMass: number;
  bmr: number;
  tdee: number;
}

export interface NutritionStatus {
  dailyCalories: number;
  protein: number;
  carbs: number;
  fat: number;
  micronutrients?: Record<string, number>;
  hydration?: number;
  mealTiming?: string[];
}

export interface TrainingHistory {
  totalWorkouts: number;
  averageFrequency: number;
  lastWorkoutDate?: Date;
  strengthProgress?: Record<string, number>;
  preferredExercises?: string[];
  injuries?: string[];
}

export interface UserProfile {
  age: number;
  gender: 'male' | 'female';
  experience: 'beginner' | 'intermediate' | 'advanced';
  activityLevel: 'sedentary' | 'light' | 'moderate' | 'active' | 'veryActive';
}

export interface Goals {
  primary: 'fat_loss' | 'muscle_gain' | 'strength' | 'endurance' | 'maintenance';
  secondary?: string;
  targetWeight?: number;
  targetBodyFat?: number;
  timeframe?: number; // weeks
}

export interface Lifestyle {
  weeklyTrainingTime: number; // hours
  sleepHours: number;
  stressLevel: 'low' | 'moderate' | 'high';
  workType: 'sedentary' | 'light' | 'moderate' | 'physical';
  schedule: 'regular' | 'shift' | 'irregular';
}

export interface Preferences {
  equipment: string[];
  avoidExercises?: string[];
  preferredTrainingTime?: 'morning' | 'afternoon' | 'evening';
  trainingLocation: 'home' | 'gym' | 'outdoor';
}

export interface ComprehensiveAnalysisResult {
  bodyComposition: {
    bmi: {
      value: number;
      category: string;
      recommendation: string;
    };
    bodyFat: {
      value: number;
      category: string;
      target: number;
    };
    muscleMass: {
      value: number;
      adequacy: number;
      potential: number;
    };
  };
  nutritionBalance: {
    energyBalance: number;
    macroBalance: {
      protein: number;
      carbs: number;
      fat: number;
    };
    micronutrientStatus: string;
    hydrationLevel: string;
    mealTiming: string;
    supplementNeeds: string[];
  };
  fitnessLevel: {
    strength: { level: number; category: string };
    endurance: { level: number; category: string };
    flexibility: { level: number; category: string };
    balance: { level: number; category: string };
    coordination: { level: number; category: string };
    powerOutput: { level: number; category: string };
    overall: number;
  };
  recoveryStatus: {
    level: number;
    sleepQuality: number;
    stressImpact: number;
    recommendations: string[];
  };
  progressTrend: {
    direction: 'improving' | 'maintaining' | 'declining';
    rate: number;
    consistency: number;
  };
  riskFactors: string[];
  strengths: string[];
  weaknesses: string[];
}

export class ComprehensiveAnalysisData {
  bodyMetrics: BodyMetrics | null = null;
  nutritionStatus: NutritionStatus | null = null;
  trainingHistory: TrainingHistory | null = null;
  userProfile: UserProfile | null = null;
  goals: Goals | null = null;
  lifestyle: Lifestyle | null = null;
  preferences: Preferences | null = null;

  /**
   * 全データを統合して分析
   */
  generateComprehensiveAnalysis(): ComprehensiveAnalysisResult | null {
    if (!this.isDataComplete()) {
      return null;
    }

    return {
      bodyComposition: this.analyzeBodyComposition(),
      nutritionBalance: this.analyzeNutritionBalance(),
      fitnessLevel: this.analyzeFitnessLevel(),
      recoveryStatus: this.analyzeRecoveryStatus(),
      progressTrend: this.analyzeProgressTrend(),
      riskFactors: this.identifyRiskFactors(),
      strengths: this.identifyStrengths(),
      weaknesses: this.identifyWeaknesses()
    };
  }

  private isDataComplete(): boolean {
    return !!(
      this.bodyMetrics &&
      this.nutritionStatus &&
      this.userProfile &&
      this.goals
    );
  }

  /**
   * 身体組成分析
   */
  private analyzeBodyComposition() {
    const { height, weight, bodyFat, muscleMass } = this.bodyMetrics!;
    const bmi = weight / Math.pow(height / 100, 2);

    return {
      bmi: {
        value: bmi,
        category: this.getBMICategory(bmi),
        recommendation: this.getBMIRecommendation(bmi)
      },
      bodyFat: {
        value: bodyFat,
        category: this.getBodyFatCategory(bodyFat, this.userProfile!.gender),
        target: this.getBodyFatTarget(this.goals!.primary)
      },
      muscleMass: {
        value: muscleMass,
        adequacy: this.getMuscleMassAdequacy(muscleMass, weight),
        potential: this.getMuscleBuildingPotential()
      }
    };
  }

  /**
   * 栄養バランス分析
   */
  private analyzeNutritionBalance() {
    const { dailyCalories, protein, carbs, fat } = this.nutritionStatus!;
    const { tdee } = this.bodyMetrics!;

    return {
      energyBalance: dailyCalories - tdee,
      macroBalance: {
        protein: protein / (this.bodyMetrics!.weight),
        carbs: carbs,
        fat: fat
      },
      micronutrientStatus: 'adequate', // 簡略化
      hydrationLevel: 'adequate',
      mealTiming: 'regular',
      supplementNeeds: this.identifySupplementNeeds()
    };
  }

  /**
   * フィットネスレベル分析
   */
  private analyzeFitnessLevel() {
    const experience = this.userProfile!.experience;
    const trainingFreq = this.trainingHistory?.averageFrequency || 0;

    // 経験とトレーニング頻度に基づく簡易評価
    const baseLevel = {
      beginner: 0.3,
      intermediate: 0.6,
      advanced: 0.85
    }[experience];

    const frequencyBonus = Math.min(trainingFreq * 0.05, 0.15);
    const overallLevel = Math.min(baseLevel + frequencyBonus, 1.0);

    return {
      strength: { level: overallLevel * 0.9, category: this.getLevelCategory(overallLevel * 0.9) },
      endurance: { level: overallLevel * 0.8, category: this.getLevelCategory(overallLevel * 0.8) },
      flexibility: { level: overallLevel * 0.7, category: this.getLevelCategory(overallLevel * 0.7) },
      balance: { level: overallLevel * 0.75, category: this.getLevelCategory(overallLevel * 0.75) },
      coordination: { level: overallLevel * 0.8, category: this.getLevelCategory(overallLevel * 0.8) },
      powerOutput: { level: overallLevel * 0.85, category: this.getLevelCategory(overallLevel * 0.85) },
      overall: overallLevel
    };
  }

  /**
   * 回復状況分析
   */
  private analyzeRecoveryStatus() {
    const sleepHours = this.lifestyle?.sleepHours || 7;
    const stressLevel = this.lifestyle?.stressLevel || 'moderate';

    const sleepScore = Math.min(sleepHours / 8, 1.0);
    const stressScore = {
      low: 1.0,
      moderate: 0.7,
      high: 0.4
    }[stressLevel];

    const recoveryLevel = (sleepScore + stressScore) / 2;

    return {
      level: recoveryLevel,
      sleepQuality: sleepScore,
      stressImpact: 1 - stressScore,
      recommendations: this.getRecoveryRecommendations(recoveryLevel)
    };
  }

  /**
   * 進歩傾向分析
   */
  private analyzeProgressTrend() {
    // 簡略化された実装
    return {
      direction: 'maintaining' as const,
      rate: 0.5,
      consistency: 0.7
    };
  }

  /**
   * リスク要因特定
   */
  private identifyRiskFactors(): string[] {
    const risks: string[] = [];

    if (this.bodyMetrics!.bodyFat > 30) {
      risks.push('高体脂肪率');
    }

    if (this.lifestyle?.stressLevel === 'high') {
      risks.push('高ストレス');
    }

    if (this.trainingHistory?.injuries && this.trainingHistory.injuries.length > 0) {
      risks.push('既往症あり');
    }

    return risks;
  }

  /**
   * 強み特定
   */
  private identifyStrengths(): string[] {
    const strengths: string[] = [];

    if (this.trainingHistory && this.trainingHistory.averageFrequency >= 3) {
      strengths.push('継続的なトレーニング習慣');
    }

    if (this.nutritionStatus && this.nutritionStatus.protein >= this.bodyMetrics!.weight * 1.6) {
      strengths.push('適切なタンパク質摂取');
    }

    return strengths;
  }

  /**
   * 弱点特定
   */
  private identifyWeaknesses(): string[] {
    const weaknesses: string[] = [];

    if (this.lifestyle && this.lifestyle.sleepHours < 7) {
      weaknesses.push('睡眠不足');
    }

    if (this.trainingHistory && this.trainingHistory.averageFrequency < 2) {
      weaknesses.push('トレーニング頻度不足');
    }

    return weaknesses;
  }

  // ヘルパーメソッド
  private getBMICategory(bmi: number): string {
    if (bmi < 18.5) return '低体重';
    if (bmi < 25) return '標準';
    if (bmi < 30) return '過体重';
    return '肥満';
  }

  private getBMIRecommendation(bmi: number): string {
    if (bmi < 18.5) return '体重増加を推奨';
    if (bmi < 25) return '現状維持または筋肉量増加';
    return '体重減少を推奨';
  }

  private getBodyFatCategory(bodyFat: number, gender: 'male' | 'female'): string {
    const thresholds = gender === 'male' 
      ? { essential: 6, athletic: 14, fit: 18, average: 25 }
      : { essential: 14, athletic: 21, fit: 25, average: 32 };

    if (bodyFat < thresholds.essential) return '必須脂肪レベル';
    if (bodyFat < thresholds.athletic) return 'アスリート';
    if (bodyFat < thresholds.fit) return 'フィット';
    if (bodyFat < thresholds.average) return '平均';
    return '高め';
  }

  private getBodyFatTarget(goal: Goals['primary']): number {
    const targets = {
      fat_loss: 15,
      muscle_gain: 18,
      strength: 16,
      endurance: 12,
      maintenance: 18
    };
    return targets[goal];
  }

  private getMuscleMassAdequacy(muscleMass: number, weight: number): number {
    const ratio = muscleMass / weight;
    return Math.min(ratio / 0.45, 1.0); // 45%を理想として正規化
  }

  private getMuscleBuildingPotential(): number {
    const age = this.userProfile!.age;
    const experience = this.userProfile!.experience;

    let potential = 1.0;
    
    // 年齢による減少
    if (age > 30) potential -= (age - 30) * 0.01;
    
    // 経験による減少
    if (experience === 'intermediate') potential *= 0.7;
    if (experience === 'advanced') potential *= 0.5;

    return Math.max(potential, 0.1);
  }

  private identifySupplementNeeds(): string[] {
    const needs: string[] = [];

    if (this.nutritionStatus!.protein < this.bodyMetrics!.weight * 1.6) {
      needs.push('プロテインパウダー');
    }

    if (this.goals!.primary === 'muscle_gain') {
      needs.push('クレアチン');
    }

    return needs;
  }

  private getLevelCategory(level: number): string {
    if (level < 0.3) return '初級';
    if (level < 0.6) return '中級';
    if (level < 0.85) return '上級';
    return 'エリート';
  }

  private getRecoveryRecommendations(level: number): string[] {
    const recommendations: string[] = [];

    if (level < 0.7) {
      recommendations.push('睡眠時間を増やす');
      recommendations.push('ストレス管理を改善');
    }

    recommendations.push('定期的なストレッチング');
    
    return recommendations;
  }
}

export type { ComprehensiveAnalysisResult };