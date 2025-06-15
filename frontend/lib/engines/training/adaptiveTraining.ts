/**
 * 適応的トレーニングシステム
 * 進捗追跡とプログラムの自動調整
 */

import { PersonalizedProgram, ExerciseAssignment } from './aiRecommendation';

export interface UserProgress {
  workoutHistory: WorkoutSession[];
  strengthProgress: StrengthProgress;
  bodyMetricsHistory: BodyMetricsLog[];
  subjectiveFeedback: SubjectiveFeedback[];
}

export interface WorkoutSession {
  date: Date;
  exercises: ExercisePerformance[];
  duration: number;
  completionRate: number;
  rpe: number; // Rating of Perceived Exertion (1-10)
  notes?: string;
}

export interface ExercisePerformance {
  exerciseId: string;
  sets: SetPerformance[];
  formQuality: number; // 1-10
  difficulty: number; // 1-10
}

export interface SetPerformance {
  reps: number;
  weight: number;
  rpe: number;
  completed: boolean;
}

export interface StrengthProgress {
  [exerciseId: string]: {
    oneRepMax: number;
    lastWeight: number;
    lastReps: number;
    progressRate: number; // percentage per week
  };
}

export interface BodyMetricsLog {
  date: Date;
  weight: number;
  bodyFat?: number;
  muscleMass?: number;
  measurements?: {
    chest?: number;
    arms?: number;
    waist?: number;
    thighs?: number;
  };
}

export interface SubjectiveFeedback {
  date: Date;
  energyLevel: number; // 1-10
  muscleStiffness: number; // 1-10
  motivation: number; // 1-10
  sleepQuality: number; // 1-10
  stress: number; // 1-10
  comments?: string;
}

export interface ProgressAnalysis {
  strengthProgress: number;
  volumeTolerance: number;
  recoveryQuality: number;
  adherence: number;
  subjective: SubjectiveAnalysis;
}

export interface SubjectiveAnalysis {
  averageEnergy: number;
  averageMotivation: number;
  averageSleepQuality: number;
  averageStress: number;
  trend: 'improving' | 'stable' | 'declining';
}

export interface ProgramAdaptation {
  type: string;
  amount?: number;
  modifications?: string[];
  reason: string;
}

export interface AdaptedProgram {
  adjustedProgram: PersonalizedProgram;
  reasoning: string[];
  nextWeekFocus: string;
  warnings?: string[];
}

export class AdaptiveTrainingSystem {
  private baseProgram: PersonalizedProgram;
  private userProgress: UserProgress;
  private adaptationHistory: ProgramAdaptation[] = [];

  constructor(baseProgram: PersonalizedProgram, userProgress: UserProgress) {
    this.baseProgram = baseProgram;
    this.userProgress = userProgress;
  }

  /**
   * プログラムの適応調整
   */
  adaptProgram(weekNumber: number): AdaptedProgram {
    const progressAnalysis = this.analyzeProgress(weekNumber);
    const adaptations = this.generateAdaptations(progressAnalysis);
    const adjustedProgram = this.applyAdaptations(adaptations);
    const reasoning = this.explainAdaptations(adaptations);
    const nextWeekFocus = this.determineNextWeekFocus(progressAnalysis);
    const warnings = this.generateWarnings(progressAnalysis);

    return {
      adjustedProgram,
      reasoning,
      nextWeekFocus,
      warnings
    };
  }

  /**
   * 進歩分析
   */
  private analyzeProgress(weekNumber: number): ProgressAnalysis {
    const recentWorkouts = this.getRecentWorkouts(weekNumber - 1, weekNumber);
    
    return {
      strengthProgress: this.analyzeStrengthProgress(recentWorkouts),
      volumeTolerance: this.analyzeVolumeTolerance(recentWorkouts),
      recoveryQuality: this.analyzeRecoveryQuality(recentWorkouts),
      adherence: this.analyzeAdherence(recentWorkouts),
      subjective: this.analyzeSubjectiveFeedback(weekNumber)
    };
  }

  /**
   * 最近のワークアウト取得
   */
  private getRecentWorkouts(startWeek: number, endWeek: number): WorkoutSession[] {
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - (endWeek * 7));
    const endDate = new Date();
    endDate.setDate(endDate.getDate() - (startWeek * 7));

    return this.userProgress.workoutHistory.filter(
      workout => workout.date >= startDate && workout.date <= endDate
    );
  }

  /**
   * 筋力進歩分析
   */
  private analyzeStrengthProgress(recentWorkouts: WorkoutSession[]): number {
    if (recentWorkouts.length === 0) return 0;

    const progressRates: number[] = [];
    
    // 主要エクササイズの進歩率を計算
    Object.entries(this.userProgress.strengthProgress).forEach(([exerciseId, progress]) => {
      if (progress.progressRate > 0) {
        progressRates.push(progress.progressRate);
      }
    });

    if (progressRates.length === 0) return 0.5;

    const averageProgress = progressRates.reduce((a, b) => a + b, 0) / progressRates.length;
    
    // 週2.5%の進歩を100%として正規化
    return Math.min(averageProgress / 2.5, 1.0);
  }

  /**
   * ボリューム耐性分析
   */
  private analyzeVolumeTolerance(recentWorkouts: WorkoutSession[]): number {
    if (recentWorkouts.length === 0) return 0.5;

    const completionRates = recentWorkouts.map(w => w.completionRate);
    const averageCompletion = completionRates.reduce((a, b) => a + b, 0) / completionRates.length;
    
    const rpeValues = recentWorkouts.map(w => w.rpe);
    const averageRPE = rpeValues.reduce((a, b) => a + b, 0) / rpeValues.length;
    
    // 完遂率が高く、RPEが適度（6-8）であれば良好
    const completionScore = averageCompletion;
    const rpeScore = 1 - Math.abs(averageRPE - 7) / 3; // 7が最適
    
    return (completionScore * 0.6 + rpeScore * 0.4);
  }

  /**
   * 回復品質分析
   */
  private analyzeRecoveryQuality(recentWorkouts: WorkoutSession[]): number {
    const recentFeedback = this.userProgress.subjectiveFeedback.slice(-7); // 最近7日分
    
    if (recentFeedback.length === 0) return 0.7;

    const sleepScores = recentFeedback.map(f => f.sleepQuality / 10);
    const stiffnessScores = recentFeedback.map(f => 1 - (f.muscleStiffness / 10));
    const energyScores = recentFeedback.map(f => f.energyLevel / 10);

    const avgSleep = sleepScores.reduce((a, b) => a + b, 0) / sleepScores.length;
    const avgStiffness = stiffnessScores.reduce((a, b) => a + b, 0) / stiffnessScores.length;
    const avgEnergy = energyScores.reduce((a, b) => a + b, 0) / energyScores.length;

    return (avgSleep * 0.4 + avgStiffness * 0.3 + avgEnergy * 0.3);
  }

  /**
   * 遵守率分析
   */
  private analyzeAdherence(recentWorkouts: WorkoutSession[]): number {
    const plannedSessions = this.baseProgram.weeklySchedule.totalSessions;
    const completedSessions = recentWorkouts.length;
    
    return Math.min(completedSessions / plannedSessions, 1.0);
  }

  /**
   * 主観的フィードバック分析
   */
  private analyzeSubjectiveFeedback(weekNumber: number): SubjectiveAnalysis {
    const recentFeedback = this.userProgress.subjectiveFeedback.slice(-14); // 2週間分
    
    if (recentFeedback.length < 7) {
      return {
        averageEnergy: 5,
        averageMotivation: 5,
        averageSleepQuality: 5,
        averageStress: 5,
        trend: 'stable'
      };
    }

    const firstWeek = recentFeedback.slice(0, 7);
    const secondWeek = recentFeedback.slice(7);

    const avgEnergy = this.calculateAverage(recentFeedback.map(f => f.energyLevel));
    const avgMotivation = this.calculateAverage(recentFeedback.map(f => f.motivation));
    const avgSleep = this.calculateAverage(recentFeedback.map(f => f.sleepQuality));
    const avgStress = this.calculateAverage(recentFeedback.map(f => f.stress));

    // トレンド分析
    const firstWeekAvg = this.calculateAverage(firstWeek.map(f => 
      (f.energyLevel + f.motivation + f.sleepQuality - f.stress) / 4
    ));
    const secondWeekAvg = this.calculateAverage(secondWeek.map(f => 
      (f.energyLevel + f.motivation + f.sleepQuality - f.stress) / 4
    ));

    let trend: 'improving' | 'stable' | 'declining';
    if (secondWeekAvg > firstWeekAvg + 0.5) {
      trend = 'improving';
    } else if (secondWeekAvg < firstWeekAvg - 0.5) {
      trend = 'declining';
    } else {
      trend = 'stable';
    }

    return {
      averageEnergy: avgEnergy,
      averageMotivation: avgMotivation,
      averageSleepQuality: avgSleep,
      averageStress: avgStress,
      trend
    };
  }

  /**
   * 適応生成
   */
  private generateAdaptations(progressAnalysis: ProgressAnalysis): ProgramAdaptation[] {
    const adaptations: ProgramAdaptation[] = [];

    // 筋力進歩に基づく調整
    if (progressAnalysis.strengthProgress > 0.9) {
      adaptations.push({
        type: 'load_increase',
        amount: 0.05,
        reason: '順調な筋力向上により負荷を増加'
      });
    } else if (progressAnalysis.strengthProgress < 0.3) {
      adaptations.push({
        type: 'load_maintenance',
        reason: '筋力向上が停滞しているため現状維持'
      });
    }

    // ボリューム耐性に基づく調整
    if (progressAnalysis.volumeTolerance > 0.85 && progressAnalysis.recoveryQuality > 0.7) {
      adaptations.push({
        type: 'volume_increase',
        amount: 0.1,
        reason: '良好な回復とボリューム耐性'
      });
    } else if (progressAnalysis.volumeTolerance < 0.6) {
      adaptations.push({
        type: 'volume_reduction',
        amount: 0.2,
        reason: 'ボリューム過多の兆候'
      });
    }

    // 回復品質に基づく調整
    if (progressAnalysis.recoveryQuality < 0.6) {
      adaptations.push({
        type: 'recovery_focus',
        modifications: ['追加休息日を設定', '強度を10%減少', 'アクティブリカバリーを増加'],
        reason: '回復不足の兆候'
      });
    }

    // 遵守率に基づく調整
    if (progressAnalysis.adherence < 0.7) {
      adaptations.push({
        type: 'program_simplification',
        modifications: ['セッション時間短縮', 'エクササイズ数削減'],
        reason: '遵守率向上のためプログラムを簡略化'
      });
    }

    // 主観的フィードバックに基づく調整
    if (progressAnalysis.subjective.trend === 'declining') {
      adaptations.push({
        type: 'deload',
        amount: 0.4,
        reason: '主観的指標の悪化'
      });
    } else if (progressAnalysis.subjective.averageMotivation < 4) {
      adaptations.push({
        type: 'variety_increase',
        modifications: ['新しいエクササイズ追加', 'レップレンジ変更'],
        reason: 'モチベーション向上のため変化を導入'
      });
    }

    return adaptations;
  }

  /**
   * 適応の適用
   */
  private applyAdaptations(adaptations: ProgramAdaptation[]): PersonalizedProgram {
    const adjustedProgram = JSON.parse(JSON.stringify(this.baseProgram));

    adaptations.forEach(adaptation => {
      switch (adaptation.type) {
        case 'load_increase':
          this.adjustLoadParameters(adjustedProgram, adaptation.amount || 0.05);
          break;
        case 'volume_reduction':
          this.adjustVolume(adjustedProgram, -(adaptation.amount || 0.2));
          break;
        case 'volume_increase':
          this.adjustVolume(adjustedProgram, adaptation.amount || 0.1);
          break;
        case 'recovery_focus':
          this.enhanceRecovery(adjustedProgram, adaptation.modifications || []);
          break;
        case 'program_simplification':
          this.simplifyProgram(adjustedProgram);
          break;
        case 'deload':
          this.applyDeload(adjustedProgram, adaptation.amount || 0.4);
          break;
        case 'variety_increase':
          this.addVariety(adjustedProgram);
          break;
      }
    });

    // 適応履歴に追加
    this.adaptationHistory.push(...adaptations);

    return adjustedProgram;
  }

  /**
   * 負荷パラメータ調整
   */
  private adjustLoadParameters(program: PersonalizedProgram, increase: number): void {
    Object.values(program.loadParameters).forEach(params => {
      params.intensity *= (1 + increase);
    });
  }

  /**
   * ボリューム調整
   */
  private adjustVolume(program: PersonalizedProgram, change: number): void {
    Object.values(program.loadParameters).forEach(params => {
      params.sets = Math.max(2, Math.round(params.sets * (1 + change)));
    });
  }

  /**
   * 回復強化
   */
  private enhanceRecovery(program: PersonalizedProgram, modifications: string[]): void {
    // 休息時間を延長
    Object.values(program.loadParameters).forEach(params => {
      params.rest *= 1.2;
    });

    // 回復プランを更新
    program.recoveryPlan.activeRecovery.frequency += 1;
    program.recoveryPlan.sleepOptimization.targetHours += 0.5;
  }

  /**
   * プログラム簡略化
   */
  private simplifyProgram(program: PersonalizedProgram): void {
    // アクセサリー種目を削減
    program.exerciseSelection.accessories = program.exerciseSelection.accessories.slice(0, 2);
    
    // セッション時間を短縮
    Object.values(program.weeklySchedule.schedule).forEach(day => {
      if (day.duration) {
        day.duration = Math.round(day.duration * 0.8);
      }
    });
  }

  /**
   * デロード適用
   */
  private applyDeload(program: PersonalizedProgram, reduction: number): void {
    // 強度とボリュームを大幅に削減
    Object.values(program.loadParameters).forEach(params => {
      params.intensity *= (1 - reduction);
      params.sets = Math.max(2, Math.round(params.sets * 0.6));
    });
  }

  /**
   * バリエーション追加
   */
  private addVariety(program: PersonalizedProgram): void {
    // エクササイズのバリエーションを追加（実装は簡略化）
    program.exerciseSelection.secondary.push({
      exercise: 'new_variation',
      reason: 'トレーニングに変化を加える'
    });
  }

  /**
   * 適応の説明
   */
  private explainAdaptations(adaptations: ProgramAdaptation[]): string[] {
    return adaptations.map(adaptation => {
      const typeExplanation = {
        load_increase: '負荷を増加',
        volume_reduction: 'ボリュームを削減',
        volume_increase: 'ボリュームを増加',
        recovery_focus: '回復を重視',
        program_simplification: 'プログラムを簡略化',
        deload: 'デロード週を実施',
        variety_increase: 'バリエーションを追加'
      }[adaptation.type] || adaptation.type;

      return `${typeExplanation}: ${adaptation.reason}`;
    });
  }

  /**
   * 次週のフォーカス決定
   */
  private determineNextWeekFocus(progressAnalysis: ProgressAnalysis): string {
    if (progressAnalysis.recoveryQuality < 0.6) {
      return '回復を優先し、強度を抑えめに';
    } else if (progressAnalysis.strengthProgress > 0.9) {
      return '順調な進歩を維持し、新しい刺激を導入';
    } else if (progressAnalysis.volumeTolerance < 0.6) {
      return 'フォームと質を重視し、ボリュームを調整';
    } else if (progressAnalysis.subjective.averageMotivation < 5) {
      return '楽しさを重視し、新しいエクササイズに挑戦';
    } else {
      return '計画通りに継続し、漸進的過負荷を適用';
    }
  }

  /**
   * 警告生成
   */
  private generateWarnings(progressAnalysis: ProgressAnalysis): string[] {
    const warnings: string[] = [];

    if (progressAnalysis.recoveryQuality < 0.5) {
      warnings.push('回復不足の兆候があります。睡眠と栄養を見直してください。');
    }

    if (progressAnalysis.adherence < 0.5) {
      warnings.push('トレーニング頻度が低下しています。スケジュールを見直しましょう。');
    }

    if (progressAnalysis.subjective.averageStress > 8) {
      warnings.push('ストレスレベルが高いです。トレーニング強度の調整を検討してください。');
    }

    if (progressAnalysis.strengthProgress < 0.1 && progressAnalysis.volumeTolerance > 0.8) {
      warnings.push('プラトーの可能性があります。プログラムの変更を検討してください。');
    }

    return warnings;
  }

  /**
   * ユーティリティメソッド
   */
  private calculateAverage(values: number[]): number {
    if (values.length === 0) return 0;
    return values.reduce((a, b) => a + b, 0) / values.length;
  }

  /**
   * 進捗レポート生成
   */
  generateProgressReport(): ProgressReport {
    const totalWorkouts = this.userProgress.workoutHistory.length;
    const recentWorkouts = this.userProgress.workoutHistory.slice(-28); // 4週間分
    
    const strengthGains = this.calculateStrengthGains();
    const bodyCompositionChanges = this.calculateBodyCompositionChanges();
    const consistencyMetrics = this.calculateConsistencyMetrics(recentWorkouts);

    return {
      summary: {
        totalWorkouts,
        trainingWeeks: Math.floor(totalWorkouts / this.baseProgram.weeklySchedule.totalSessions),
        overallProgress: this.calculateOverallProgress()
      },
      strengthGains,
      bodyCompositionChanges,
      consistencyMetrics,
      recommendations: this.generateRecommendations(),
      achievements: this.identifyAchievements()
    };
  }

  private calculateStrengthGains(): Record<string, number> {
    const gains: Record<string, number> = {};
    
    Object.entries(this.userProgress.strengthProgress).forEach(([exercise, progress]) => {
      gains[exercise] = progress.progressRate * 4; // 4週間の進歩率
    });

    return gains;
  }

  private calculateBodyCompositionChanges(): BodyCompositionChange {
    const metrics = this.userProgress.bodyMetricsHistory;
    if (metrics.length < 2) {
      return { weightChange: 0, bodyFatChange: 0, muscleMassChange: 0 };
    }

    const initial = metrics[0];
    const latest = metrics[metrics.length - 1];

    return {
      weightChange: latest.weight - initial.weight,
      bodyFatChange: (latest.bodyFat || 0) - (initial.bodyFat || 0),
      muscleMassChange: (latest.muscleMass || 0) - (initial.muscleMass || 0)
    };
  }

  private calculateConsistencyMetrics(recentWorkouts: WorkoutSession[]): ConsistencyMetrics {
    const plannedSessions = this.baseProgram.weeklySchedule.totalSessions * 4;
    const completedSessions = recentWorkouts.length;
    
    return {
      adherenceRate: completedSessions / plannedSessions,
      averageCompletionRate: this.calculateAverage(recentWorkouts.map(w => w.completionRate)),
      missedSessions: plannedSessions - completedSessions
    };
  }

  private calculateOverallProgress(): number {
    const recentAnalysis = this.analyzeProgress(4);
    
    return (
      recentAnalysis.strengthProgress * 0.3 +
      recentAnalysis.volumeTolerance * 0.2 +
      recentAnalysis.recoveryQuality * 0.2 +
      recentAnalysis.adherence * 0.2 +
      (recentAnalysis.subjective.trend === 'improving' ? 0.1 : 
       recentAnalysis.subjective.trend === 'stable' ? 0.05 : 0)
    );
  }

  private generateRecommendations(): string[] {
    const analysis = this.analyzeProgress(4);
    const recommendations: string[] = [];

    if (analysis.strengthProgress < 0.5) {
      recommendations.push('進歩が停滞しています。栄養摂取量を見直しましょう。');
    }

    if (analysis.recoveryQuality < 0.7) {
      recommendations.push('回復に注力してください。睡眠時間を増やしましょう。');
    }

    if (analysis.subjective.averageMotivation < 6) {
      recommendations.push('新しい目標を設定して、モチベーションを高めましょう。');
    }

    return recommendations;
  }

  private identifyAchievements(): string[] {
    const achievements: string[] = [];
    const strengthGains = this.calculateStrengthGains();

    Object.entries(strengthGains).forEach(([exercise, gain]) => {
      if (gain > 10) {
        achievements.push(`${exercise}で10%以上の筋力向上！`);
      }
    });

    const consistency = this.calculateConsistencyMetrics(this.userProgress.workoutHistory.slice(-28));
    if (consistency.adherenceRate > 0.9) {
      achievements.push('90%以上の高い遵守率を達成！');
    }

    return achievements;
  }
}

// 型定義
interface ProgressReport {
  summary: {
    totalWorkouts: number;
    trainingWeeks: number;
    overallProgress: number;
  };
  strengthGains: Record<string, number>;
  bodyCompositionChanges: BodyCompositionChange;
  consistencyMetrics: ConsistencyMetrics;
  recommendations: string[];
  achievements: string[];
}

interface BodyCompositionChange {
  weightChange: number;
  bodyFatChange: number;
  muscleMassChange: number;
}

interface ConsistencyMetrics {
  adherenceRate: number;
  averageCompletionRate: number;
  missedSessions: number;
}

