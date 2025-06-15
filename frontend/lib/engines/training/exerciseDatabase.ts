/**
 * エクササイズデータベース
 * トレーニング種目の詳細情報を管理
 */

export interface Exercise {
  id: string;
  name: string;
  nameJa: string;
  category: 'compound' | 'isolation' | 'cardio' | 'flexibility' | 'core';
  primaryMuscles: string[];
  secondaryMuscles: string[];
  equipment: string[];
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  movementPattern: 'push' | 'pull' | 'squat' | 'hinge' | 'carry' | 'rotation' | 'cardio';
  forceType: 'push' | 'pull' | 'static';
  mechanics: 'compound' | 'isolation';
  instructions: string[];
  tips: string[];
  commonMistakes: string[];
  variations: string[];
  benefits: string[];
}

export interface ExerciseParameters {
  sets: number;
  reps: number | string;
  rest: number; // seconds
  tempo?: string; // e.g., "2-0-2-0"
  intensity?: number; // percentage of 1RM
  duration?: number; // for time-based exercises
}

export const EXERCISE_DATABASE: Record<string, Exercise> = {
  // 下半身 - スクワット系
  bodyweight_squat: {
    id: 'bodyweight_squat',
    name: 'Bodyweight Squat',
    nameJa: '自重スクワット',
    category: 'compound',
    primaryMuscles: ['quadriceps', 'glutes'],
    secondaryMuscles: ['hamstrings', 'calves', 'core'],
    equipment: ['none'],
    difficulty: 'beginner',
    movementPattern: 'squat',
    forceType: 'push',
    mechanics: 'compound',
    instructions: [
      '足を肩幅に開いて立つ',
      '胸を張り、背筋を伸ばす',
      '膝と股関節を曲げながら腰を落とす',
      '太ももが床と平行になるまで下げる',
      '踵で床を押して立ち上がる'
    ],
    tips: [
      '膝がつま先より前に出すぎないよう注意',
      '背中は常にまっすぐに保つ',
      '呼吸は下がる時に吸い、上がる時に吐く'
    ],
    commonMistakes: ['膝が内側に入る', '踵が浮く', '背中が丸まる'],
    variations: ['jump_squat', 'pistol_squat', 'bulgarian_split_squat'],
    benefits: ['下半身全体の強化', '基礎的な動作パターンの習得', '日常動作の改善']
  },

  goblet_squat: {
    id: 'goblet_squat',
    name: 'Goblet Squat',
    nameJa: 'ゴブレットスクワット',
    category: 'compound',
    primaryMuscles: ['quadriceps', 'glutes'],
    secondaryMuscles: ['hamstrings', 'core', 'upper_back'],
    equipment: ['dumbbell', 'kettlebell'],
    difficulty: 'intermediate',
    movementPattern: 'squat',
    forceType: 'push',
    mechanics: 'compound',
    instructions: [
      'ダンベルまたはケトルベルを胸の前で持つ',
      '肘を内側に向け、重りを体に近づける',
      '足を肩幅より少し広めに開く',
      'スクワット動作を行う',
      '深くしゃがみ、ゆっくりと立ち上がる'
    ],
    tips: [
      '重りを体に近づけることで体幹が安定',
      '肘で膝を押し開くようにする',
      '上体を起こしたまま動作する'
    ],
    commonMistakes: ['重りが体から離れる', '前傾しすぎる', '膝が内側に入る'],
    variations: ['front_squat', 'zercher_squat'],
    benefits: ['体幹の強化', '正しいスクワットフォームの習得', '上半身も同時に鍛える']
  },

  back_squat: {
    id: 'back_squat',
    name: 'Back Squat',
    nameJa: 'バックスクワット',
    category: 'compound',
    primaryMuscles: ['quadriceps', 'glutes'],
    secondaryMuscles: ['hamstrings', 'core', 'lower_back'],
    equipment: ['barbell', 'squat_rack'],
    difficulty: 'advanced',
    movementPattern: 'squat',
    forceType: 'push',
    mechanics: 'compound',
    instructions: [
      'バーベルを僧帽筋上部に乗せる',
      'ラックから外し、一歩下がる',
      '足を肩幅に開き、つま先をやや外に向ける',
      '胸を張り、腰を落とす',
      '太ももが床と平行になるまで下げ、立ち上がる'
    ],
    tips: [
      'バーの位置はハイバーまたはローバーを選択',
      '腹圧を高めて体幹を安定させる',
      '踵で床を押すイメージで立ち上がる'
    ],
    commonMistakes: ['前傾しすぎる', 'バットウィンク', '膝が内側に入る'],
    variations: ['front_squat', 'box_squat', 'pause_squat'],
    benefits: ['下半身の最大筋力向上', '全身の筋肉量増加', 'ホルモン分泌促進']
  },

  // 上半身 - プッシュ系
  pushup: {
    id: 'pushup',
    name: 'Push-up',
    nameJa: 'プッシュアップ（腕立て伏せ）',
    category: 'compound',
    primaryMuscles: ['chest', 'triceps'],
    secondaryMuscles: ['shoulders', 'core'],
    equipment: ['none'],
    difficulty: 'beginner',
    movementPattern: 'push',
    forceType: 'push',
    mechanics: 'compound',
    instructions: [
      '手を肩幅より少し広めに床につく',
      '体を一直線に保つ',
      '肘を曲げて胸を床に近づける',
      '床を押して元の位置に戻る'
    ],
    tips: [
      '体幹を締めて体を一直線に保つ',
      '肘は45度程度の角度で曲げる',
      '呼吸は下がる時に吸い、上がる時に吐く'
    ],
    commonMistakes: ['腰が落ちる', '肘が外に開きすぎる', '可動域が狭い'],
    variations: ['knee_pushup', 'diamond_pushup', 'decline_pushup'],
    benefits: ['上半身の基礎筋力向上', '体幹の安定性向上', '場所を選ばずトレーニング可能']
  },

  dumbbell_press: {
    id: 'dumbbell_press',
    name: 'Dumbbell Chest Press',
    nameJa: 'ダンベルプレス',
    category: 'compound',
    primaryMuscles: ['chest'],
    secondaryMuscles: ['triceps', 'shoulders'],
    equipment: ['dumbbell', 'bench'],
    difficulty: 'intermediate',
    movementPattern: 'push',
    forceType: 'push',
    mechanics: 'compound',
    instructions: [
      'ベンチに仰向けになる',
      'ダンベルを胸の横で構える',
      'ダンベルを上に押し上げる',
      'コントロールしながら下ろす'
    ],
    tips: [
      '肩甲骨を寄せて胸を張る',
      'ダンベルは弧を描くように動かす',
      '肘は体側から45度程度の角度'
    ],
    commonMistakes: ['肩がすくむ', '腰が反りすぎる', 'ダンベルがぶれる'],
    variations: ['incline_dumbbell_press', 'decline_dumbbell_press', 'dumbbell_fly'],
    benefits: ['胸筋の筋肥大', '左右のバランス改善', '可動域の拡大']
  },

  bench_press: {
    id: 'bench_press',
    name: 'Barbell Bench Press',
    nameJa: 'ベンチプレス',
    category: 'compound',
    primaryMuscles: ['chest'],
    secondaryMuscles: ['triceps', 'shoulders'],
    equipment: ['barbell', 'bench', 'power_rack'],
    difficulty: 'advanced',
    movementPattern: 'push',
    forceType: 'push',
    mechanics: 'compound',
    instructions: [
      'ベンチに仰向けになり、目線がバーの真下',
      '肩甲骨を寄せ、アーチを作る',
      'バーを肩幅の1.5倍程度で握る',
      'バーを胸まで下ろし、押し上げる'
    ],
    tips: [
      '足をしっかり床につけて踏ん張る',
      'バーは胸の下部（乳頭線）に下ろす',
      '手首をまっすぐに保つ'
    ],
    commonMistakes: ['バウンドさせる', 'お尻が浮く', '手首が反る'],
    variations: ['incline_bench_press', 'close_grip_bench_press', 'pause_bench_press'],
    benefits: ['上半身の最大筋力向上', '胸筋の筋肥大', '押す力の総合的な向上']
  },

  // 上半身 - プル系
  assisted_pullup: {
    id: 'assisted_pullup',
    name: 'Assisted Pull-up',
    nameJa: 'アシスト付きプルアップ',
    category: 'compound',
    primaryMuscles: ['lats', 'middle_back'],
    secondaryMuscles: ['biceps', 'rear_delts'],
    equipment: ['pullup_bar', 'resistance_band'],
    difficulty: 'beginner',
    movementPattern: 'pull',
    forceType: 'pull',
    mechanics: 'compound',
    instructions: [
      'バンドを懸垂バーに掛ける',
      '片足または両足をバンドに乗せる',
      '肩幅より少し広めでバーを握る',
      '胸をバーに近づけるように引き上げる',
      'コントロールしながら下ろす'
    ],
    tips: [
      '肩甲骨を下げてから引く',
      '肘を体側に引きつける',
      'バンドの強度は徐々に弱くする'
    ],
    commonMistakes: ['反動を使う', '可動域が狭い', '肩がすくむ'],
    variations: ['negative_pullup', 'jumping_pullup', 'lat_pulldown'],
    benefits: ['懸垂の基礎筋力向上', '背中の筋力強化', '段階的な進歩が可能']
  },

  bent_over_row: {
    id: 'bent_over_row',
    name: 'Bent Over Row',
    nameJa: 'ベントオーバーロウ',
    category: 'compound',
    primaryMuscles: ['middle_back', 'lats'],
    secondaryMuscles: ['biceps', 'rear_delts', 'core'],
    equipment: ['barbell', 'dumbbell'],
    difficulty: 'intermediate',
    movementPattern: 'pull',
    forceType: 'pull',
    mechanics: 'compound',
    instructions: [
      '膝を軽く曲げ、上体を45度前傾',
      'バーを肩幅で握る',
      'バーを腹部に向けて引く',
      '肩甲骨を寄せる',
      'コントロールしながら下ろす'
    ],
    tips: [
      '背中は常にまっすぐに保つ',
      '肘を体側に沿って引く',
      '腹圧を高めて体幹を安定'
    ],
    commonMistakes: ['上体が起きる', '反動を使う', '背中が丸まる'],
    variations: ['pendlay_row', 'yates_row', 'single_arm_row'],
    benefits: ['背中の厚みを作る', '姿勢改善', '引く力の向上']
  },

  // ヒンジ系
  deadlift_variation: {
    id: 'deadlift_variation',
    name: 'Romanian Deadlift',
    nameJa: 'ルーマニアンデッドリフト',
    category: 'compound',
    primaryMuscles: ['hamstrings', 'glutes'],
    secondaryMuscles: ['lower_back', 'traps', 'core'],
    equipment: ['barbell', 'dumbbell'],
    difficulty: 'intermediate',
    movementPattern: 'hinge',
    forceType: 'pull',
    mechanics: 'compound',
    instructions: [
      'バーを腰幅で握る',
      '膝を軽く曲げて固定',
      '股関節を後ろに引きながら上体を倒す',
      'ハムストリングスのストレッチを感じたら戻る'
    ],
    tips: [
      '背中は常にまっすぐに',
      'バーは体に沿って動かす',
      '股関節主導で動く'
    ],
    commonMistakes: ['膝を曲げすぎる', '背中が丸まる', 'バーが体から離れる'],
    variations: ['stiff_leg_deadlift', 'single_leg_rdl', 'trap_bar_deadlift'],
    benefits: ['ハムストリングス強化', 'ヒップヒンジ動作の習得', '後鎖筋群の発達']
  },

  deadlift: {
    id: 'deadlift',
    name: 'Conventional Deadlift',
    nameJa: 'デッドリフト',
    category: 'compound',
    primaryMuscles: ['hamstrings', 'glutes', 'lower_back'],
    secondaryMuscles: ['traps', 'lats', 'core', 'forearms'],
    equipment: ['barbell'],
    difficulty: 'advanced',
    movementPattern: 'hinge',
    forceType: 'pull',
    mechanics: 'compound',
    instructions: [
      '足を腰幅に開き、バーが足の中央上',
      '股関節を曲げてバーを握る',
      '胸を張り、背中をまっすぐに',
      '脚と背中を使って立ち上がる',
      'コントロールしながら下ろす'
    ],
    tips: [
      'バーは体に沿って動かす',
      '最初は脚で押し、後半は股関節を前に',
      '腹圧を高めて腰を保護'
    ],
    commonMistakes: ['背中が丸まる', 'バーが体から離れる', '膝が前に出すぎる'],
    variations: ['sumo_deadlift', 'rack_pull', 'deficit_deadlift'],
    benefits: ['全身の筋力向上', '最大筋力の発達', 'ホルモン分泌促進']
  },

  // コア
  plank: {
    id: 'plank',
    name: 'Plank',
    nameJa: 'プランク',
    category: 'core',
    primaryMuscles: ['abs', 'core'],
    secondaryMuscles: ['shoulders', 'glutes'],
    equipment: ['none'],
    difficulty: 'beginner',
    movementPattern: 'rotation',
    forceType: 'static',
    mechanics: 'isolation',
    instructions: [
      '前腕を床につき、肘は肩の真下',
      '脚を伸ばし、つま先で支える',
      '体を一直線に保つ',
      '指定時間キープする'
    ],
    tips: [
      '腰が落ちないよう注意',
      '呼吸を止めない',
      '肩甲骨を安定させる'
    ],
    commonMistakes: ['腰が落ちる', 'お尻が上がる', '首が落ちる'],
    variations: ['side_plank', 'plank_variations', 'dynamic_plank'],
    benefits: ['体幹の安定性向上', '姿勢改善', '腰痛予防']
  },

  // 肩
  overhead_press: {
    id: 'overhead_press',
    name: 'Overhead Press',
    nameJa: 'オーバーヘッドプレス',
    category: 'compound',
    primaryMuscles: ['shoulders'],
    secondaryMuscles: ['triceps', 'core', 'upper_back'],
    equipment: ['barbell', 'dumbbell'],
    difficulty: 'intermediate',
    movementPattern: 'push',
    forceType: 'push',
    mechanics: 'compound',
    instructions: [
      'バーを鎖骨の前で持つ',
      '肘を前に向ける',
      'バーを頭上に押し上げる',
      '耳の横を通るように動かす',
      'コントロールして下ろす'
    ],
    tips: [
      '体幹を締めて安定させる',
      '肘を少し前に向ける',
      '頭を前に出してバーを通す'
    ],
    commonMistakes: ['腰が反る', 'バーが前に流れる', '可動域が狭い'],
    variations: ['military_press', 'push_press', 'seated_press'],
    benefits: ['肩の筋力向上', '体幹の安定性', '機能的な押す力']
  },

  // 追加の下半身
  leg_press: {
    id: 'leg_press',
    name: 'Leg Press',
    nameJa: 'レッグプレス',
    category: 'compound',
    primaryMuscles: ['quadriceps', 'glutes'],
    secondaryMuscles: ['hamstrings', 'calves'],
    equipment: ['leg_press_machine'],
    difficulty: 'beginner',
    movementPattern: 'squat',
    forceType: 'push',
    mechanics: 'compound',
    instructions: [
      'レッグプレスマシンに座る',
      '足を肩幅に開いてプレートに置く',
      '膝を曲げて重りを下ろす',
      '踵で押して元に戻る'
    ],
    tips: [
      '膝は90度以上曲げない',
      '踵で押すことを意識',
      '膝とつま先の向きを揃える'
    ],
    commonMistakes: ['膝が内側に入る', '可動域が狭い', '腰が丸まる'],
    variations: ['single_leg_press', 'wide_stance_press', 'calf_press'],
    benefits: ['安全に高重量を扱える', '下半身の筋肥大', '初心者でも取り組みやすい']
  },

  // 背中
  lat_pulldown: {
    id: 'lat_pulldown',
    name: 'Lat Pulldown',
    nameJa: 'ラットプルダウン',
    category: 'compound',
    primaryMuscles: ['lats'],
    secondaryMuscles: ['middle_back', 'biceps', 'rear_delts'],
    equipment: ['cable_machine'],
    difficulty: 'beginner',
    movementPattern: 'pull',
    forceType: 'pull',
    mechanics: 'compound',
    instructions: [
      'バーを肩幅より広めに握る',
      '少し後傾して座る',
      'バーを鎖骨に向けて引く',
      '肩甲骨を下げて寄せる',
      'コントロールして戻す'
    ],
    tips: [
      '肘を体側に引きつける',
      '胸を張って行う',
      '反動を使わない'
    ],
    commonMistakes: ['後傾しすぎる', '腕だけで引く', 'バーを首の後ろに引く'],
    variations: ['wide_grip_pulldown', 'reverse_grip_pulldown', 'single_arm_pulldown'],
    benefits: ['背中の広がりを作る', '懸垂の準備運動', '引く力の基礎作り']
  },

  // 肩
  shoulder_press: {
    id: 'shoulder_press',
    name: 'Dumbbell Shoulder Press',
    nameJa: 'ダンベルショルダープレス',
    category: 'compound',
    primaryMuscles: ['shoulders'],
    secondaryMuscles: ['triceps', 'upper_back'],
    equipment: ['dumbbell'],
    difficulty: 'intermediate',
    movementPattern: 'push',
    forceType: 'push',
    mechanics: 'compound',
    instructions: [
      'ダンベルを肩の高さで構える',
      '肘は体の横、前腕は垂直',
      'ダンベルを頭上に押し上げる',
      'コントロールして下ろす'
    ],
    tips: [
      '体幹を安定させる',
      '自然な軌道で動かす',
      '肩がすくまないよう注意'
    ],
    commonMistakes: ['腰が反る', '可動域が狭い', 'ダンベルが前後にぶれる'],
    variations: ['arnold_press', 'seated_shoulder_press', 'neutral_grip_press'],
    benefits: ['肩の筋肥大', '左右のバランス改善', '安定性の向上']
  }
};

// カーディオエクササイズ
export const CARDIO_EXERCISES: Record<string, Partial<Exercise>> = {
  treadmill_walk: {
    id: 'treadmill_walk',
    name: 'Treadmill Walking',
    nameJa: 'トレッドミルウォーキング',
    category: 'cardio',
    difficulty: 'beginner',
    movementPattern: 'cardio',
    equipment: ['treadmill'],
    benefits: ['心肺機能向上', '脂肪燃焼', '低衝撃']
  },
  
  cycling: {
    id: 'cycling',
    name: 'Stationary Cycling',
    nameJa: 'エアロバイク',
    category: 'cardio',
    difficulty: 'beginner',
    movementPattern: 'cardio',
    equipment: ['stationary_bike'],
    benefits: ['心肺機能向上', '下半身持久力', '関節に優しい']
  },
  
  rowing: {
    id: 'rowing',
    name: 'Rowing Machine',
    nameJa: 'ローイングマシン',
    category: 'cardio',
    difficulty: 'intermediate',
    movementPattern: 'cardio',
    equipment: ['rowing_machine'],
    benefits: ['全身運動', '心肺機能向上', '筋持久力向上']
  }
};

// モビリティ・柔軟性エクササイズ
export const MOBILITY_EXERCISES: Record<string, Partial<Exercise>> = {
  hip_flexor_stretch: {
    id: 'hip_flexor_stretch',
    name: 'Hip Flexor Stretch',
    nameJa: '腸腰筋ストレッチ',
    category: 'flexibility',
    difficulty: 'beginner',
    primaryMuscles: ['hip_flexors'],
    equipment: ['none'],
    benefits: ['股関節可動域改善', '腰痛予防', '姿勢改善']
  },
  
  shoulder_dislocations: {
    id: 'shoulder_dislocations',
    name: 'Shoulder Dislocations',
    nameJa: 'ショルダーディスロケーション',
    category: 'flexibility',
    difficulty: 'beginner',
    primaryMuscles: ['shoulders'],
    equipment: ['resistance_band', 'pvc_pipe'],
    benefits: ['肩関節可動域改善', '肩こり解消', '姿勢改善']
  },
  
  cat_cow_stretch: {
    id: 'cat_cow_stretch',
    name: 'Cat-Cow Stretch',
    nameJa: 'キャットカウストレッチ',
    category: 'flexibility',
    difficulty: 'beginner',
    primaryMuscles: ['spine', 'core'],
    equipment: ['none'],
    benefits: ['脊柱の柔軟性向上', '腰痛予防', 'コア活性化']
  }
};

// トレーニングプログラムテンプレート
export interface TrainingProgram {
  id: string;
  name: string;
  goal: string;
  duration: number; // weeks
  frequency: number; // sessions per week
  level: 'beginner' | 'intermediate' | 'advanced';
  structure: 'full_body' | 'upper_lower' | 'ppl' | 'body_part';
  phases: {
    phase: number;
    weeks: number;
    focus: string;
    volumeProgression: string;
  }[];
}

export const TRAINING_PROGRAMS: TrainingProgram[] = [
  {
    id: 'beginner_full_body',
    name: '初心者向け全身トレーニング',
    goal: '基礎筋力構築',
    duration: 8,
    frequency: 3,
    level: 'beginner',
    structure: 'full_body',
    phases: [
      {
        phase: 1,
        weeks: 4,
        focus: '動作習得',
        volumeProgression: '3x10-12'
      },
      {
        phase: 2,
        weeks: 4,
        focus: '筋力向上',
        volumeProgression: '3x8-10'
      }
    ]
  },
  
  {
    id: 'intermediate_upper_lower',
    name: '中級者向け上下分割',
    goal: '筋肥大・筋力向上',
    duration: 12,
    frequency: 4,
    level: 'intermediate',
    structure: 'upper_lower',
    phases: [
      {
        phase: 1,
        weeks: 4,
        focus: '筋肥大',
        volumeProgression: '4x8-12'
      },
      {
        phase: 2,
        weeks: 4,
        focus: '筋力向上',
        volumeProgression: '4x6-8'
      },
      {
        phase: 3,
        weeks: 4,
        focus: '統合',
        volumeProgression: '3-4x6-12'
      }
    ]
  },
  
  {
    id: 'advanced_ppl',
    name: '上級者向けPPL分割',
    goal: '筋肥大特化',
    duration: 16,
    frequency: 6,
    level: 'advanced',
    structure: 'ppl',
    phases: [
      {
        phase: 1,
        weeks: 4,
        focus: '高ボリューム',
        volumeProgression: '4-5x8-15'
      },
      {
        phase: 2,
        weeks: 4,
        focus: '高強度',
        volumeProgression: '3-4x4-8'
      },
      {
        phase: 3,
        weeks: 4,
        focus: '特化',
        volumeProgression: '5-6x8-12'
      },
      {
        phase: 4,
        weeks: 4,
        focus: 'ピーキング',
        volumeProgression: '3x3-6'
      }
    ]
  }
];

export default EXERCISE_DATABASE;