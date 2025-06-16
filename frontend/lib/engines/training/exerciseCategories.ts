/**
 * エクササイズカテゴリーと筋群の定義
 */

// 筋群の定義
export const MUSCLE_GROUPS = {
  // 上半身
  chest: { id: 'chest', name: 'Chest', nameJa: '胸部', category: 'upper' },
  back: { id: 'back', name: 'Back', nameJa: '背中', category: 'upper' },
  shoulders: { id: 'shoulders', name: 'Shoulders', nameJa: '肩', category: 'upper' },
  biceps: { id: 'biceps', name: 'Biceps', nameJa: '上腕二頭筋', category: 'upper' },
  triceps: { id: 'triceps', name: 'Triceps', nameJa: '上腕三頭筋', category: 'upper' },
  forearms: { id: 'forearms', name: 'Forearms', nameJa: '前腕', category: 'upper' },
  
  // 体幹
  core: { id: 'core', name: 'Core', nameJa: '体幹', category: 'core' },
  abs: { id: 'abs', name: 'Abs', nameJa: '腹筋', category: 'core' },
  upper_abs: { id: 'upper_abs', name: 'Upper Abs', nameJa: '上部腹筋', category: 'core' },
  lower_abs: { id: 'lower_abs', name: 'Lower Abs', nameJa: '下部腹筋', category: 'core' },
  obliques: { id: 'obliques', name: 'Obliques', nameJa: '腹斜筋', category: 'core' },
  transverse_abdominis: { id: 'transverse_abdominis', name: 'Transverse Abdominis', nameJa: '腹横筋', category: 'core' },
  lower_back: { id: 'lower_back', name: 'Lower Back', nameJa: '腰部', category: 'core' },
  
  // 下半身
  glutes: { id: 'glutes', name: 'Glutes', nameJa: '臀部', category: 'lower' },
  quadriceps: { id: 'quadriceps', name: 'Quadriceps', nameJa: '大腿四頭筋', category: 'lower' },
  hamstrings: { id: 'hamstrings', name: 'Hamstrings', nameJa: 'ハムストリング', category: 'lower' },
  calves: { id: 'calves', name: 'Calves', nameJa: 'ふくらはぎ', category: 'lower' },
  hip_flexors: { id: 'hip_flexors', name: 'Hip Flexors', nameJa: '腸腰筋', category: 'lower' },
  adductors: { id: 'adductors', name: 'Adductors', nameJa: '内転筋', category: 'lower' },
  
  // その他
  full_body: { id: 'full_body', name: 'Full Body', nameJa: '全身', category: 'other' },
  cardio: { id: 'cardio', name: 'Cardio', nameJa: '有酸素', category: 'other' },
  upper_back: { id: 'upper_back', name: 'Upper Back', nameJa: '上背部', category: 'upper' },
  lats: { id: 'lats', name: 'Lats', nameJa: '広背筋', category: 'upper' },
  traps: { id: 'traps', name: 'Traps', nameJa: '僧帽筋', category: 'upper' },
  delts: { id: 'delts', name: 'Delts', nameJa: '三角筋', category: 'upper' }
} as const;

// エクササイズカテゴリー
export const EXERCISE_CATEGORIES = {
  compound: { id: 'compound', name: 'Compound', nameJa: '複合種目', description: '複数の関節を使う種目' },
  isolation: { id: 'isolation', name: 'Isolation', nameJa: '単関節種目', description: '単一の関節を使う種目' },
  cardio: { id: 'cardio', name: 'Cardio', nameJa: '有酸素', description: '心肺機能を高める種目' },
  flexibility: { id: 'flexibility', name: 'Flexibility', nameJa: '柔軟性', description: '柔軟性を高める種目' },
  core: { id: 'core', name: 'Core', nameJa: '体幹', description: '体幹を鍛える種目' }
} as const;

// 動作パターン
export const MOVEMENT_PATTERNS = {
  push: { id: 'push', name: 'Push', nameJa: 'プッシュ', description: '押す動作' },
  pull: { id: 'pull', name: 'Pull', nameJa: 'プル', description: '引く動作' },
  squat: { id: 'squat', name: 'Squat', nameJa: 'スクワット', description: 'しゃがむ動作' },
  hinge: { id: 'hinge', name: 'Hinge', nameJa: 'ヒンジ', description: '股関節を軸にした動作' },
  carry: { id: 'carry', name: 'Carry', nameJa: 'キャリー', description: '運ぶ動作' },
  rotation: { id: 'rotation', name: 'Rotation', nameJa: '回旋', description: '回転動作' },
  cardio: { id: 'cardio', name: 'Cardio', nameJa: '有酸素', description: '有酸素運動' }
} as const;

// 難易度レベル
export const DIFFICULTY_LEVELS = {
  beginner: { id: 'beginner', name: 'Beginner', nameJa: '初心者', order: 1 },
  intermediate: { id: 'intermediate', name: 'Intermediate', nameJa: '中級者', order: 2 },
  advanced: { id: 'advanced', name: 'Advanced', nameJa: '上級者', order: 3 }
} as const;

// 器具カテゴリー
export const EQUIPMENT_CATEGORIES = {
  none: { id: 'none', name: 'Bodyweight', nameJa: '自重', category: 'bodyweight' },
  
  // フリーウェイト
  dumbbell: { id: 'dumbbell', name: 'Dumbbell', nameJa: 'ダンベル', category: 'free_weight' },
  barbell: { id: 'barbell', name: 'Barbell', nameJa: 'バーベル', category: 'free_weight' },
  kettlebell: { id: 'kettlebell', name: 'Kettlebell', nameJa: 'ケトルベル', category: 'free_weight' },
  plate: { id: 'plate', name: 'Weight Plate', nameJa: 'プレート', category: 'free_weight' },
  
  // マシン
  cable: { id: 'cable', name: 'Cable Machine', nameJa: 'ケーブルマシン', category: 'machine' },
  smith_machine: { id: 'smith_machine', name: 'Smith Machine', nameJa: 'スミスマシン', category: 'machine' },
  leg_press_machine: { id: 'leg_press_machine', name: 'Leg Press Machine', nameJa: 'レッグプレスマシン', category: 'machine' },
  
  // その他の器具
  bench: { id: 'bench', name: 'Bench', nameJa: 'ベンチ', category: 'equipment' },
  box: { id: 'box', name: 'Box', nameJa: 'ボックス', category: 'equipment' },
  stairs: { id: 'stairs', name: 'Stairs', nameJa: '階段', category: 'equipment' },
  wall: { id: 'wall', name: 'Wall', nameJa: '壁', category: 'equipment' },
  pullup_bar: { id: 'pullup_bar', name: 'Pull-up Bar', nameJa: '懸垂バー', category: 'equipment' },
  resistance_band: { id: 'resistance_band', name: 'Resistance Band', nameJa: 'レジスタンスバンド', category: 'equipment' },
  medicine_ball: { id: 'medicine_ball', name: 'Medicine Ball', nameJa: 'メディシンボール', category: 'equipment' },
  bosu_ball: { id: 'bosu_ball', name: 'BOSU Ball', nameJa: 'BOSUボール', category: 'equipment' },
  stability_ball: { id: 'stability_ball', name: 'Stability Ball', nameJa: 'バランスボール', category: 'equipment' },
  foam_roller: { id: 'foam_roller', name: 'Foam Roller', nameJa: 'フォームローラー', category: 'equipment' },
  trx: { id: 'trx', name: 'TRX', nameJa: 'TRX', category: 'equipment' }
} as const;

// カテゴリー別フィルター用のヘルパー関数
export const getMusclesByCategory = (category: 'upper' | 'core' | 'lower' | 'other') => {
  return Object.values(MUSCLE_GROUPS).filter(muscle => muscle.category === category);
};

export const getEquipmentByCategory = (category: 'bodyweight' | 'free_weight' | 'machine' | 'equipment') => {
  return Object.values(EQUIPMENT_CATEGORIES).filter(equipment => equipment.category === category);
};

// 筋群の組み合わせパターン
export const MUSCLE_GROUP_COMBINATIONS = {
  push_muscles: ['chest', 'triceps', 'shoulders'],
  pull_muscles: ['back', 'biceps', 'lats', 'traps'],
  leg_muscles: ['quadriceps', 'hamstrings', 'glutes', 'calves'],
  core_muscles: ['abs', 'obliques', 'lower_back', 'transverse_abdominis'],
  arm_muscles: ['biceps', 'triceps', 'forearms']
};