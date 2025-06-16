/**
 * 完全なエクササイズデータベース
 * 全フェーズの種目を統合
 */

import { Exercise } from './exerciseDatabase';
import { EXERCISE_DATABASE } from './exerciseDatabase';
import { PHASE1_EXERCISES } from './exerciseDatabasePhase1';

// Phase 1の種目を既存のデータベースにマージ
export const COMPLETE_EXERCISE_DATABASE: Record<string, Exercise> = {
  ...EXERCISE_DATABASE,
  ...PHASE1_EXERCISES
};

// エクササイズの総数を取得
export const getTotalExerciseCount = () => {
  return Object.keys(COMPLETE_EXERCISE_DATABASE).length;
};

// カテゴリー別にエクササイズを取得
export const getExercisesByCategory = (category: string) => {
  return Object.values(COMPLETE_EXERCISE_DATABASE).filter(
    exercise => exercise.category === category
  );
};

// 筋群別にエクササイズを取得
export const getExercisesByMuscleGroup = (muscleGroup: string) => {
  return Object.values(COMPLETE_EXERCISE_DATABASE).filter(
    exercise => 
      exercise.primaryMuscles.includes(muscleGroup) || 
      exercise.secondaryMuscles.includes(muscleGroup)
  );
};

// 難易度別にエクササイズを取得
export const getExercisesByDifficulty = (difficulty: 'beginner' | 'intermediate' | 'advanced') => {
  return Object.values(COMPLETE_EXERCISE_DATABASE).filter(
    exercise => exercise.difficulty === difficulty
  );
};

// 器具別にエクササイズを取得
export const getExercisesByEquipment = (equipment: string) => {
  return Object.values(COMPLETE_EXERCISE_DATABASE).filter(
    exercise => exercise.equipment.includes(equipment)
  );
};

// 動作パターン別にエクササイズを取得
export const getExercisesByMovementPattern = (pattern: string) => {
  return Object.values(COMPLETE_EXERCISE_DATABASE).filter(
    exercise => exercise.movementPattern === pattern
  );
};

// エクササイズ検索（名前で検索）
export const searchExercises = (query: string) => {
  const lowerQuery = query.toLowerCase();
  return Object.values(COMPLETE_EXERCISE_DATABASE).filter(
    exercise => 
      exercise.name.toLowerCase().includes(lowerQuery) ||
      exercise.nameJa.includes(query)
  );
};

// エクササイズ統計情報
export const getExerciseStatistics = () => {
  const exercises = Object.values(COMPLETE_EXERCISE_DATABASE);
  
  return {
    total: exercises.length,
    byCategory: {
      compound: exercises.filter(e => e.category === 'compound').length,
      isolation: exercises.filter(e => e.category === 'isolation').length,
      cardio: exercises.filter(e => e.category === 'cardio').length,
      flexibility: exercises.filter(e => e.category === 'flexibility').length,
      core: exercises.filter(e => e.category === 'core').length
    },
    byDifficulty: {
      beginner: exercises.filter(e => e.difficulty === 'beginner').length,
      intermediate: exercises.filter(e => e.difficulty === 'intermediate').length,
      advanced: exercises.filter(e => e.difficulty === 'advanced').length
    },
    byMovementPattern: {
      push: exercises.filter(e => e.movementPattern === 'push').length,
      pull: exercises.filter(e => e.movementPattern === 'pull').length,
      squat: exercises.filter(e => e.movementPattern === 'squat').length,
      hinge: exercises.filter(e => e.movementPattern === 'hinge').length,
      carry: exercises.filter(e => e.movementPattern === 'carry').length,
      rotation: exercises.filter(e => e.movementPattern === 'rotation').length,
      cardio: exercises.filter(e => e.movementPattern === 'cardio').length
    },
    bodyweightOnly: exercises.filter(e => e.equipment.includes('none')).length
  };
};