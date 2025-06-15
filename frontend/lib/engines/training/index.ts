// 包括的分析
export { ComprehensiveAnalysisData } from './comprehensiveAnalysis';
export type { 
  BodyMetrics,
  NutritionStatus,
  TrainingHistory,
  UserProfile,
  Goals,
  Lifestyle,
  Preferences,
  ComprehensiveAnalysisResult
} from './comprehensiveAnalysis';

// AI推奨エンジン
export { AITrainingRecommendationEngine } from './aiRecommendation';
export type {
  PersonalizedProgram,
  ProgramOverview,
  WeeklySchedule,
  DaySchedule,
  ExerciseSelection,
  ExerciseAssignment,
  LoadParameters,
  WorkoutParameters,
  ProgressionPlan,
  ProgressionPhase,
  NutritionSync,
  RecoveryPlan,
  MonitoringPlan
} from './aiRecommendation';

// エクササイズデータベース
export { EXERCISE_DATABASE, CARDIO_EXERCISES, MOBILITY_EXERCISES, TRAINING_PROGRAMS } from './exerciseDatabase';
export type { Exercise, ExerciseParameters, TrainingProgram } from './exerciseDatabase';

// 適応的トレーニング
export { AdaptiveTrainingSystem } from './adaptiveTraining';
export type {
  UserProgress,
  WorkoutSession,
  ExercisePerformance,
  SetPerformance,
  StrengthProgress,
  BodyMetricsLog,
  SubjectiveFeedback,
  ProgressAnalysis,
  SubjectiveAnalysis,
  ProgramAdaptation,
  AdaptedProgram
} from './adaptiveTraining';