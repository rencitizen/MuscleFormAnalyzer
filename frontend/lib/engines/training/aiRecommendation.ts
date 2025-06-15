/**
 * AI トレーニング推奨エンジン
 * 包括的分析データに基づいて最適なトレーニングプログラムを生成
 */

import { ComprehensiveAnalysisResult } from './comprehensiveAnalysis';
import { 
  Exercise, 
  ExerciseParameters, 
  EXERCISE_DATABASE, 
  CARDIO_EXERCISES,
  MOBILITY_EXERCISES,
  TRAINING_PROGRAMS,
  TrainingProgram 
} from './exerciseDatabase';

export interface PersonalizedProgram {
  programOverview: ProgramOverview;
  weeklySchedule: WeeklySchedule;
  exerciseSelection: ExerciseSelection;
  loadParameters: LoadParameters;
  progressionPlan: ProgressionPlan;
  nutritionSync: NutritionSync;
  recoveryPlan: RecoveryPlan;
  monitoring: MonitoringPlan;
}

export interface ProgramOverview {
  title: string;
  duration: string;
  objective: string;
  expectedOutcomes: string[];
  keyPrinciples: string[];
  successMetrics: string[];
  adaptationPlan: string;
}

export interface WeeklySchedule {
  totalSessions: number;
  weeklyVolume: number;
  schedule: Record<string, DaySchedule>;
}

export interface DaySchedule {
  type: 'full_body' | 'upper_body' | 'lower_body' | 'push' | 'pull' | 'legs' | 'rest';
  focus?: string;
  duration?: number;
  activity?: string;
}

export interface ExerciseSelection {
  primary: ExerciseAssignment[];
  secondary: ExerciseAssignment[];
  accessories: ExerciseAssignment[];
  cardio: ExerciseAssignment[];
  mobility: ExerciseAssignment[];
}

export interface ExerciseAssignment {
  exercise: string;
  reason: string;
  parameters?: ExerciseParameters;
}

export interface LoadParameters {
  strength: WorkoutParameters;
  hypertrophy: WorkoutParameters;
  endurance: WorkoutParameters;
}

export interface WorkoutParameters {
  intensity: number;
  sets: number;
  reps: number | string;
  rest: number;
  weight?: number;
}

export interface ProgressionPlan {
  weeklyIncrement: number;
  deloadWeek: number;
  phases: ProgressionPhase[];
}

export interface ProgressionPhase {
  weeks: number;
  focus: string;
  volumeChange: string;
  intensityChange: string;
}

export interface NutritionSync {
  preWorkout: string;
  postWorkout: string;
  dailyAdjustments: string;
  hydrationPlan: string;
  supplementTiming: string;
}

export interface RecoveryPlan {
  sleepOptimization: {
    targetHours: number;
    bedtimeRoutine: string[];
    sleepHygiene: string[];
  };
  activeRecovery: {
    frequency: number;
    activities: string[];
    duration: string;
  };
  stressManagement: {
    techniques: string[];
    frequency: string;
  };
  monitoringMetrics: string[];
}

export interface MonitoringPlan {
  trackingMetrics: string[];
  assessmentFrequency: string;
  adjustmentTriggers: string[];
}

interface Priority {
  type: string;
  intensity: string;
  reason: string;
  weight: number;
}

interface Limitations {
  injuries: string[];
  equipment: string[];
  timeConstraints: number;
}

export class AITrainingRecommendationEngine {
  private analysis: ComprehensiveAnalysisResult;
  private exerciseDatabase = EXERCISE_DATABASE;
  private cardioExercises = CARDIO_EXERCISES;
  private mobilityExercises = MOBILITY_EXERCISES;
  private templatePrograms = TRAINING_PROGRAMS;

  constructor(analysisData: ComprehensiveAnalysisResult) {
    this.analysis = analysisData;
  }

  /**
   * メイン推奨メソッド
   */
  generatePersonalizedProgram(): PersonalizedProgram {
    const priorities = this.determinePriorities();
    const limitations = this.identifyLimitations();
    const programStructure = this.determineProgramStructure(priorities);
    const selectedExercises = this.selectExercises(priorities, limitations);
    const loadParameters = this.calculateLoadParameters();
    const progressionPlan = this.createProgressionPlan();

    return {
      programOverview: this.createProgramOverview(priorities),
      weeklySchedule: this.createWeeklySchedule(programStructure),
      exerciseSelection: selectedExercises,
      loadParameters: loadParameters,
      progressionPlan: progressionPlan,
      nutritionSync: this.syncWithNutrition(),
      recoveryPlan: this.generateRecoveryPlan(),
      monitoring: this.createMonitoringPlan()
    };
  }

  /**
   * 優先順位決定
   */
  private determinePriorities(): Priority[] {
    const { bodyComposition, fitnessLevel, nutritionBalance } = this.analysis;
    const priorities: Priority[] = [];

    // BMIとbody fatに基づく優先順位
    if (bodyComposition.bodyFat.value > bodyComposition.bodyFat.target + 5) {
      priorities.push({
        type: 'cardio',
        intensity: 'moderate',
        reason: '体脂肪削減が必要',
        weight: 0.3
      });
      priorities.push({
        type: 'strength',
        intensity: 'moderate',
        reason: '筋肉量維持しながら減量',
        weight: 0.7
      });
    } else if (bodyComposition.muscleMass.adequacy < 0.8) {
      priorities.push({
        type: 'strength',
        intensity: 'high',
        reason: '筋肉量増加が必要',
        weight: 0.8
      });
      priorities.push({
        type: 'cardio',
        intensity: 'low',
        reason: '最小限の有酸素運動',
        weight: 0.2
      });
    } else {
      priorities.push({
        type: 'strength',
        intensity: 'moderate',
        reason: 'バランスの取れたトレーニング',
        weight: 0.6
      });
      priorities.push({
        type: 'cardio',
        intensity: 'moderate',
        reason: '心肺機能の維持',
        weight: 0.4
      });
    }

    // フィットネスレベルに基づく調整
    if (fitnessLevel.strength.level < 0.4) {
      priorities.unshift({
        type: 'basic_strength',
        intensity: 'progressive',
        reason: '基礎筋力の構築が最優先',
        weight: 0.9
      });
    }

    // 栄養状況による調整
    if (nutritionBalance.energyBalance < -500) {
      priorities.forEach(p => {
        if (p.intensity === 'high') p.intensity = 'moderate';
      });
    }

    return priorities;
  }

  /**
   * 制限事項の特定
   */
  private identifyLimitations(): Limitations {
    return {
      injuries: this.analysis.riskFactors.filter(risk => risk.includes('既往症')),
      equipment: ['barbell', 'dumbbell', 'pullup_bar', 'bench'], // デフォルト装備
      timeConstraints: 60 // 分/セッション
    };
  }

  /**
   * プログラム構造の決定
   */
  private determineProgramStructure(priorities: Priority[]): string {
    const fitnessLevel = this.analysis.fitnessLevel.overall;
    
    if (fitnessLevel < 0.4) {
      return 'full_body';
    } else if (fitnessLevel < 0.7) {
      return 'upper_lower';
    } else {
      return 'ppl';
    }
  }

  /**
   * エクササイズ選択
   */
  private selectExercises(priorities: Priority[], limitations: Limitations): ExerciseSelection {
    const selectedExercises: ExerciseSelection = {
      primary: [],
      secondary: [],
      accessories: [],
      cardio: [],
      mobility: []
    };

    // 優先順位に基づいてエクササイズを選択
    priorities.forEach(priority => {
      switch (priority.type) {
        case 'strength':
        case 'basic_strength':
          const strengthExercises = this.selectStrengthExercises(priority);
          selectedExercises.primary.push(...strengthExercises.primary);
          selectedExercises.secondary.push(...strengthExercises.secondary);
          break;
        case 'cardio':
          selectedExercises.cardio.push(...this.selectCardioExercises(priority));
          break;
      }
    });

    // バランスとモビリティエクササイズを追加
    selectedExercises.accessories = this.addBalancingExercises(selectedExercises);
    selectedExercises.mobility = this.addMobilityExercises();

    return selectedExercises;
  }

  /**
   * 筋力トレーニング種目選択
   */
  private selectStrengthExercises(priority: Priority): { primary: ExerciseAssignment[], secondary: ExerciseAssignment[] } {
    const fitnessLevel = this.analysis.fitnessLevel.strength.level;
    const primary: ExerciseAssignment[] = [];
    const secondary: ExerciseAssignment[] = [];

    if (fitnessLevel < 0.4) {
      // 初心者向け
      primary.push(
        { exercise: 'bodyweight_squat', reason: '下半身基礎動作の習得' },
        { exercise: 'pushup', reason: '上半身押す動作の基礎' },
        { exercise: 'assisted_pullup', reason: '背中の基礎筋力向上' }
      );
      secondary.push(
        { exercise: 'plank', reason: '体幹安定性の向上' },
        { exercise: 'goblet_squat', reason: '荷重スクワットへの導入' }
      );
    } else if (fitnessLevel < 0.7) {
      // 中級者向け
      primary.push(
        { exercise: 'goblet_squat', reason: '下半身筋力の向上' },
        { exercise: 'dumbbell_press', reason: '胸筋の発達' },
        { exercise: 'bent_over_row', reason: '背中の厚みを作る' },
        { exercise: 'deadlift_variation', reason: '後鎖筋群の強化' }
      );
      secondary.push(
        { exercise: 'overhead_press', reason: '肩の筋力向上' },
        { exercise: 'leg_press', reason: '下半身の筋肥大' }
      );
    } else {
      // 上級者向け
      primary.push(
        { exercise: 'back_squat', reason: '下半身最大筋力の向上' },
        { exercise: 'bench_press', reason: '上半身最大筋力の向上' },
        { exercise: 'deadlift', reason: '全身筋力の統合' }
      );
      secondary.push(
        { exercise: 'overhead_press', reason: '機能的な押す力' },
        { exercise: 'bent_over_row', reason: '引く力のバランス' }
      );
    }

    return { primary, secondary };
  }

  /**
   * 有酸素運動選択
   */
  private selectCardioExercises(priority: Priority): ExerciseAssignment[] {
    const cardioExercises: ExerciseAssignment[] = [];
    
    if (priority.intensity === 'low') {
      cardioExercises.push({
        exercise: 'treadmill_walk',
        reason: '低強度で回復促進',
        parameters: { duration: 20, intensity: 0.5 }
      });
    } else if (priority.intensity === 'moderate') {
      cardioExercises.push({
        exercise: 'cycling',
        reason: '脂肪燃焼と心肺機能向上',
        parameters: { duration: 30, intensity: 0.65 }
      });
    } else {
      cardioExercises.push({
        exercise: 'rowing',
        reason: '高強度全身有酸素運動',
        parameters: { duration: 20, intensity: 0.8 }
      });
    }

    return cardioExercises;
  }

  /**
   * バランシングエクササイズの追加
   */
  private addBalancingExercises(currentSelection: ExerciseSelection): ExerciseAssignment[] {
    const accessories: ExerciseAssignment[] = [];
    
    // プッシュ/プルのバランス確認
    const pushCount = currentSelection.primary.filter(e => 
      this.exerciseDatabase[e.exercise]?.movementPattern === 'push'
    ).length;
    const pullCount = currentSelection.primary.filter(e => 
      this.exerciseDatabase[e.exercise]?.movementPattern === 'pull'
    ).length;

    if (pushCount > pullCount) {
      accessories.push({
        exercise: 'lat_pulldown',
        reason: 'プッシュ/プルのバランス調整'
      });
    }

    return accessories;
  }

  /**
   * モビリティエクササイズの追加
   */
  private addMobilityExercises(): ExerciseAssignment[] {
    return [
      { exercise: 'hip_flexor_stretch', reason: '股関節可動域の改善' },
      { exercise: 'shoulder_dislocations', reason: '肩関節可動域の改善' },
      { exercise: 'cat_cow_stretch', reason: '脊柱の柔軟性向上' }
    ];
  }

  /**
   * 負荷パラメータ計算
   */
  private calculateLoadParameters(): LoadParameters {
    const fitnessLevel = this.analysis.fitnessLevel.strength.level;
    const recoveryLevel = this.analysis.recoveryStatus.level;

    const baseParameters: LoadParameters = {
      strength: {
        intensity: 0.75,
        sets: 3,
        reps: 6,
        rest: 180
      },
      hypertrophy: {
        intensity: 0.65,
        sets: 4,
        reps: 10,
        rest: 90
      },
      endurance: {
        intensity: 0.50,
        sets: 3,
        reps: 15,
        rest: 60
      }
    };

    // フィットネスレベルによる調整
    if (fitnessLevel < 0.4) {
      Object.values(baseParameters).forEach(params => {
        params.intensity *= 0.8;
        params.sets = Math.max(2, params.sets - 1);
      });
    }

    // 回復状況による調整
    if (recoveryLevel < 0.7) {
      Object.values(baseParameters).forEach(params => {
        params.sets = Math.max(2, params.sets - 1);
        params.rest *= 1.2;
      });
    }

    return baseParameters;
  }

  /**
   * 進歩的過負荷プラン作成
   */
  private createProgressionPlan(): ProgressionPlan {
    const fitnessLevel = this.analysis.fitnessLevel.strength.level;
    
    const phases: ProgressionPhase[] = [
      {
        weeks: 4,
        focus: '基礎構築',
        volumeChange: '毎週5%増加',
        intensityChange: '2週間ごとに2.5%増加'
      },
      {
        weeks: 4,
        focus: '筋力向上',
        volumeChange: '維持',
        intensityChange: '毎週2.5%増加'
      },
      {
        weeks: 4,
        focus: '統合',
        volumeChange: '10%減少',
        intensityChange: '5%増加'
      }
    ];

    return {
      weeklyIncrement: fitnessLevel < 0.4 ? 2.5 : 5.0,
      deloadWeek: 4,
      phases
    };
  }

  /**
   * 週間スケジュール作成
   */
  private createWeeklySchedule(programStructure: string): WeeklySchedule {
    const fitnessLevel = this.analysis.fitnessLevel.overall;
    let totalSessions: number;
    let schedule: Record<string, DaySchedule> = {};

    // セッション数の決定
    if (fitnessLevel < 0.4) {
      totalSessions = 3;
    } else if (fitnessLevel < 0.7) {
      totalSessions = 4;
    } else {
      totalSessions = 5;
    }

    // スケジュール作成
    if (programStructure === 'full_body') {
      schedule = {
        day1: { type: 'full_body', focus: '上半身重視', duration: 45 },
        day2: { type: 'rest', activity: 'アクティブリカバリー' },
        day3: { type: 'full_body', focus: '下半身重視', duration: 45 },
        day4: { type: 'rest', activity: 'モビリティ' },
        day5: { type: 'full_body', focus: 'バランス', duration: 50 },
        day6: { type: 'rest', activity: '有酸素運動（任意）' },
        day7: { type: 'rest', activity: '完全休養' }
      };
    } else if (programStructure === 'upper_lower') {
      schedule = {
        day1: { type: 'upper_body', focus: '筋力', duration: 60 },
        day2: { type: 'lower_body', focus: '筋力', duration: 60 },
        day3: { type: 'rest', activity: '有酸素運動' },
        day4: { type: 'upper_body', focus: '筋肥大', duration: 55 },
        day5: { type: 'lower_body', focus: '筋肥大', duration: 55 },
        day6: { type: 'rest', activity: 'アクティブリカバリー' },
        day7: { type: 'rest', activity: '完全休養' }
      };
    } else {
      schedule = {
        day1: { type: 'push', focus: '胸・肩・三頭', duration: 70 },
        day2: { type: 'pull', focus: '背中・二頭', duration: 70 },
        day3: { type: 'legs', focus: '脚・臀部', duration: 75 },
        day4: { type: 'rest', activity: 'アクティブリカバリー' },
        day5: { type: 'push', focus: '肩・三頭', duration: 60 },
        day6: { type: 'pull', focus: '背中・後肩', duration: 60 },
        day7: { type: 'rest', activity: '完全休養' }
      };
    }

    return {
      totalSessions,
      weeklyVolume: totalSessions * 16, // 平均セット数
      schedule
    };
  }

  /**
   * 栄養との同期
   */
  private syncWithNutrition(): NutritionSync {
    const energyBalance = this.analysis.nutritionBalance.energyBalance;
    const proteinIntake = this.analysis.nutritionBalance.macroBalance.protein;

    return {
      preWorkout: energyBalance < 0 
        ? '運動30分前に軽い炭水化物（バナナなど）'
        : '運動1時間前に炭水化物とタンパク質',
      postWorkout: '運動後30分以内にプロテイン20-30g + 炭水化物',
      dailyAdjustments: 'トレーニング日は炭水化物を10-20%増量',
      hydrationPlan: '体重1kgあたり35-40mlの水分摂取、運動中は15分ごとに150-200ml',
      supplementTiming: proteinIntake < 1.6 
        ? 'プロテインパウダーを朝食と運動後に摂取'
        : '現在の食事で十分なタンパク質を摂取'
    };
  }

  /**
   * 回復プラン生成
   */
  private generateRecoveryPlan(): RecoveryPlan {
    const recoveryLevel = this.analysis.recoveryStatus.level;
    const stressLevel = this.analysis.recoveryStatus.stressImpact;

    return {
      sleepOptimization: {
        targetHours: recoveryLevel < 0.7 ? 8 : 7.5,
        bedtimeRoutine: [
          '就寝2時間前からブルーライトを避ける',
          '就寝1時間前に入浴',
          '寝室を涼しく暗くする',
          '規則正しい就寝時間を保つ'
        ],
        sleepHygiene: [
          'カフェインは14時以降摂取しない',
          'アルコールを控える',
          '寝室でスマホを使わない'
        ]
      },
      activeRecovery: {
        frequency: 2,
        activities: ['軽いウォーキング', 'ヨガ', 'スイミング', 'サイクリング'],
        duration: '20-30分'
      },
      stressManagement: {
        techniques: ['深呼吸法', '瞑想', 'プログレッシブ筋弛緩法'],
        frequency: '毎日10-15分'
      },
      monitoringMetrics: [
        '起床時心拍数',
        '主観的疲労度（1-10）',
        '睡眠の質',
        '筋肉痛のレベル'
      ]
    };
  }

  /**
   * モニタリングプラン作成
   */
  private createMonitoringPlan(): MonitoringPlan {
    return {
      trackingMetrics: [
        '各エクササイズの重量と回数',
        '体重・体脂肪率',
        '主観的運動強度（RPE）',
        'トレーニング後の疲労度',
        '睡眠時間と質'
      ],
      assessmentFrequency: '2週間ごと',
      adjustmentTriggers: [
        '2週間進歩が見られない場合',
        '過度の疲労が3日以上続く場合',
        'フォームの崩れが見られる場合',
        '怪我や痛みが発生した場合'
      ]
    };
  }

  /**
   * プログラム概要作成
   */
  private createProgramOverview(priorities: Priority[]): ProgramOverview {
    const primaryGoal = priorities[0];
    const fitnessLevel = this.analysis.fitnessLevel.overall;

    return {
      title: this.generateProgramTitle(primaryGoal, fitnessLevel),
      duration: '12週間',
      objective: this.generateObjectiveStatement(priorities),
      expectedOutcomes: this.generateExpectedOutcomes(priorities),
      keyPrinciples: this.generateKeyPrinciples(priorities),
      successMetrics: this.generateSuccessMetrics(),
      adaptationPlan: '2週間ごとに進捗を評価し、必要に応じて負荷・ボリュームを調整'
    };
  }

  private generateProgramTitle(primaryGoal: Priority, fitnessLevel: number): string {
    const levelStr = fitnessLevel < 0.4 ? '初心者' : fitnessLevel < 0.7 ? '中級者' : '上級者';
    const goalStr = primaryGoal.type === 'strength' ? '筋力向上' : 
                    primaryGoal.type === 'cardio' ? '体脂肪削減' : '基礎構築';
    return `${levelStr}向け${goalStr}プログラム`;
  }

  private generateObjectiveStatement(priorities: Priority[]): string {
    const goals = priorities.map(p => p.reason).join('、');
    return `このプログラムは${goals}を目的として設計されています。`;
  }

  private generateExpectedOutcomes(priorities: Priority[]): string[] {
    const outcomes: string[] = [];
    
    if (priorities.some(p => p.type === 'strength')) {
      outcomes.push('筋力の10-20%向上');
      outcomes.push('筋肉量の増加');
    }
    
    if (priorities.some(p => p.type === 'cardio')) {
      outcomes.push('体脂肪率の2-4%減少');
      outcomes.push('心肺機能の改善');
    }

    outcomes.push('全体的な体力向上');
    outcomes.push('日常動作の改善');

    return outcomes;
  }

  private generateKeyPrinciples(priorities: Priority[]): string[] {
    return [
      '漸進的過負荷の原則',
      '適切な回復時間の確保',
      'フォームを重視した安全なトレーニング',
      '栄養と睡眠の最適化',
      '一貫性のある実施'
    ];
  }

  private generateSuccessMetrics(): string[] {
    return [
      '主要エクササイズの使用重量',
      '体組成の変化（体重・体脂肪率・筋肉量）',
      'トレーニング完遂率',
      '主観的な体調・疲労度',
      '日常生活での体力向上実感'
    ];
  }
}

