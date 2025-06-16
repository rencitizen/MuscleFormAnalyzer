/**
 * エクササイズデータベース - フェーズ2
 * 器具使用種目（ダンベル、バーベル、プルアップバー）40種目
 */

import { Exercise } from './exerciseDatabase';

export const PHASE2_EXERCISES: Record<string, Exercise> = {
  // ダンベル種目 - 胸部
  dumbbell_bench_press: {
    id: 'dumbbell_bench_press',
    name: 'Dumbbell Bench Press',
    nameJa: 'ダンベルベンチプレス',
    category: 'compound',
    primaryMuscles: ['chest', 'triceps'],
    secondaryMuscles: ['shoulders'],
    equipment: ['dumbbell', 'bench'],
    difficulty: 'intermediate',
    movementPattern: 'push',
    forceType: 'push',
    mechanics: 'compound',
    instructions: [
      'ベンチに仰向けになる',
      'ダンベルを胸の横で構える',
      'ダンベルを真上に押し上げる',
      '肘を曲げてゆっくりと下ろす',
      '胸の横まで下ろしたら押し上げる'
    ],
    tips: [
      '肩甲骨を寄せて胸を張る',
      'ダンベルは弧を描くように動かす',
      '手首を真っ直ぐに保つ',
      '呼吸は下ろす時に吸い、上げる時に吐く'
    ],
    commonMistakes: ['肘が過度に外側に開く', 'ダンベルがぐらつく', '可動域が狭い', '腰が反りすぎる'],
    variations: ['incline_dumbbell_press', 'decline_dumbbell_press', 'dumbbell_floor_press'],
    benefits: ['左右独立した筋力強化', 'スタビライザー筋の活性化', '可動域が広い', 'バランス能力向上']
  },

  dumbbell_fly: {
    id: 'dumbbell_fly',
    name: 'Dumbbell Fly',
    nameJa: 'ダンベルフライ',
    category: 'isolation',
    primaryMuscles: ['chest'],
    secondaryMuscles: ['shoulders'],
    equipment: ['dumbbell', 'bench'],
    difficulty: 'intermediate',
    movementPattern: 'push',
    forceType: 'push',
    mechanics: 'isolation',
    instructions: [
      'ベンチに仰向けになり、ダンベルを真上に構える',
      '肘を軽く曲げたまま、腕を横に開く',
      '胸が伸びるのを感じながら下ろす',
      '胸を使って元の位置に戻す',
      '上部で胸を絞る意識'
    ],
    tips: [
      '肘の角度は一定に保つ',
      '肩の高さより下まで下ろさない',
      '弧を描くような軌道',
      '重量よりもフォーム重視'
    ],
    commonMistakes: ['肘を伸ばしすぎる', '下ろしすぎて肩を痛める', '反動を使う', '手首が曲がる'],
    variations: ['incline_dumbbell_fly', 'decline_dumbbell_fly', 'cable_fly'],
    benefits: ['胸筋の集中的な刺激', 'ストレッチ効果', '筋肉の形を整える', '胸の内側を鍛える']
  },

  // ダンベル種目 - 背中
  dumbbell_row: {
    id: 'dumbbell_row',
    name: 'One-Arm Dumbbell Row',
    nameJa: 'ワンアームダンベルロウ',
    category: 'compound',
    primaryMuscles: ['back', 'lats'],
    secondaryMuscles: ['biceps', 'shoulders'],
    equipment: ['dumbbell', 'bench'],
    difficulty: 'intermediate',
    movementPattern: 'pull',
    forceType: 'pull',
    mechanics: 'compound',
    instructions: [
      '片手と片膝をベンチに置く',
      '反対の手でダンベルを持つ',
      '背中を使ってダンベルを引き上げる',
      '肘を体の横を通して引く',
      'ゆっくりと下ろす'
    ],
    tips: [
      '背中は真っ直ぐに保つ',
      '肩を下げて肩甲骨を寄せる',
      '腕で引かず背中で引く',
      '体幹を安定させる'
    ],
    commonMistakes: ['体をひねる', '腕で引く', '背中が丸まる', '可動域が狭い'],
    variations: ['bent_over_dumbbell_row', 'chest_supported_row', 'renegade_row'],
    benefits: ['背中の厚みを作る', '左右のバランス調整', '体幹の安定性向上', '握力強化']
  },

  // ダンベル種目 - 肩
  dumbbell_shoulder_press: {
    id: 'dumbbell_shoulder_press',
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
      '肘は前方に向ける',
      'ダンベルを真上に押し上げる',
      '頭上で軽く触れる程度まで上げる',
      'コントロールしながら下ろす'
    ],
    tips: [
      '体幹を締めて安定させる',
      '腰を反らせない',
      'ダンベルは頭の真上へ',
      '肩甲骨を安定させる'
    ],
    commonMistakes: ['腰を反らせすぎる', 'ダンベルが前後にぶれる', '可動域が狭い', '反動を使う'],
    variations: ['seated_dumbbell_press', 'arnold_press', 'neutral_grip_press'],
    benefits: ['肩全体の発達', '体幹の強化', 'オーバーヘッド動作の改善', '左右のバランス調整']
  },

  lateral_raise: {
    id: 'lateral_raise',
    name: 'Lateral Raise',
    nameJa: 'サイドレイズ',
    category: 'isolation',
    primaryMuscles: ['shoulders'],
    secondaryMuscles: ['traps'],
    equipment: ['dumbbell'],
    difficulty: 'beginner',
    movementPattern: 'pull',
    forceType: 'pull',
    mechanics: 'isolation',
    instructions: [
      'ダンベルを体の横に持つ',
      '肘を軽く曲げた状態を保つ',
      '腕を横に上げる',
      '肩の高さまで上げる',
      'ゆっくりと下ろす'
    ],
    tips: [
      '肩をすくめない',
      '反動を使わない',
      '肘は肩より低く',
      '軽い重量から始める'
    ],
    commonMistakes: ['重すぎる重量', '反動を使う', '肩をすくめる', '腕を上げすぎる'],
    variations: ['front_raise', 'rear_delt_fly', 'cable_lateral_raise'],
    benefits: ['肩の幅を作る', '三角筋中部の発達', '肩関節の安定性', '姿勢改善']
  },

  // ダンベル種目 - 腕
  bicep_curl: {
    id: 'bicep_curl',
    name: 'Dumbbell Bicep Curl',
    nameJa: 'ダンベルバイセップカール',
    category: 'isolation',
    primaryMuscles: ['biceps'],
    secondaryMuscles: ['forearms'],
    equipment: ['dumbbell'],
    difficulty: 'beginner',
    movementPattern: 'pull',
    forceType: 'pull',
    mechanics: 'isolation',
    instructions: [
      'ダンベルを持って腕を下ろす',
      '肘を体の横に固定',
      '前腕を曲げてダンベルを上げる',
      '上腕二頭筋を収縮させる',
      'ゆっくりと下ろす'
    ],
    tips: [
      '肘を動かさない',
      '手首を真っ直ぐに保つ',
      '反動を使わない',
      'フルレンジで動作'
    ],
    commonMistakes: ['肘が前後に動く', '反動を使う', '体を揺らす', '手首が曲がる'],
    variations: ['hammer_curl', 'concentration_curl', 'preacher_curl'],
    benefits: ['上腕二頭筋の発達', '腕の太さ増加', '握力向上', '日常動作の改善']
  },

  hammer_curl: {
    id: 'hammer_curl',
    name: 'Hammer Curl',
    nameJa: 'ハンマーカール',
    category: 'isolation',
    primaryMuscles: ['biceps', 'forearms'],
    secondaryMuscles: [],
    equipment: ['dumbbell'],
    difficulty: 'beginner',
    movementPattern: 'pull',
    forceType: 'pull',
    mechanics: 'isolation',
    instructions: [
      'ダンベルを縦に持つ（ハンマーグリップ）',
      '肘を体の横に固定',
      'グリップを変えずに曲げる',
      '上腕二頭筋と前腕を収縮',
      'コントロールして下ろす'
    ],
    tips: [
      '親指を上に向けたまま',
      '肘を固定する',
      '両腕同時でも交互でも可',
      'ゆっくりとした動作'
    ],
    commonMistakes: ['手首が回転する', '肘が動く', '反動を使う', '可動域が狭い'],
    variations: ['cross_body_hammer_curl', 'rope_hammer_curl', 'seated_hammer_curl'],
    benefits: ['前腕の強化', '上腕筋の発達', '握力向上', '腕全体のバランス']
  },

  tricep_extension: {
    id: 'tricep_extension',
    name: 'Overhead Tricep Extension',
    nameJa: 'オーバーヘッドトライセップエクステンション',
    category: 'isolation',
    primaryMuscles: ['triceps'],
    secondaryMuscles: [],
    equipment: ['dumbbell'],
    difficulty: 'intermediate',
    movementPattern: 'push',
    forceType: 'push',
    mechanics: 'isolation',
    instructions: [
      'ダンベルを両手で持ち頭上に上げる',
      '肘を頭の横で固定',
      '前腕だけを曲げて下ろす',
      '肘の位置は変えない',
      '三頭筋で押し上げる'
    ],
    tips: [
      '肘を外に開かない',
      '上腕は垂直に保つ',
      'ゆっくりと下ろす',
      '深く下ろして伸ばす'
    ],
    commonMistakes: ['肘が動く', '肩に負担がかかる', '反動を使う', '首が前に出る'],
    variations: ['lying_tricep_extension', 'single_arm_extension', 'cable_overhead_extension'],
    benefits: ['上腕三頭筋の発達', '腕の太さ増加', 'プレス動作の強化', '長頭の特別な刺激']
  },

  // ダンベル種目 - 脚
  dumbbell_lunge: {
    id: 'dumbbell_lunge',
    name: 'Dumbbell Lunge',
    nameJa: 'ダンベルランジ',
    category: 'compound',
    primaryMuscles: ['quadriceps', 'glutes'],
    secondaryMuscles: ['hamstrings', 'calves', 'core'],
    equipment: ['dumbbell'],
    difficulty: 'intermediate',
    movementPattern: 'squat',
    forceType: 'push',
    mechanics: 'compound',
    instructions: [
      '両手にダンベルを持つ',
      '片足を前に大きく踏み出す',
      '両膝を曲げて体を下ろす',
      '前膝90度、後膝が床に近づく',
      '前足で押して戻る'
    ],
    tips: [
      'ダンベルは体の横に下げる',
      '上体は垂直に保つ',
      '歩幅を十分に取る',
      'バランスを保つ'
    ],
    commonMistakes: ['上体が前傾', '歩幅が狭い', '膝が内側に入る', 'ダンベルが揺れる'],
    variations: ['walking_dumbbell_lunge', 'reverse_dumbbell_lunge', 'bulgarian_split_squat'],
    benefits: ['片脚の筋力強化', '負荷を増やせる', 'バランス能力向上', '実用的な動作']
  },

  romanian_deadlift: {
    id: 'romanian_deadlift',
    name: 'Romanian Deadlift',
    nameJa: 'ルーマニアンデッドリフト',
    category: 'compound',
    primaryMuscles: ['hamstrings', 'glutes'],
    secondaryMuscles: ['lower_back', 'traps'],
    equipment: ['dumbbell'],
    difficulty: 'intermediate',
    movementPattern: 'hinge',
    forceType: 'pull',
    mechanics: 'compound',
    instructions: [
      'ダンベルを太ももの前で持つ',
      '膝を軽く曲げた状態を保つ',
      '股関節から体を前傾させる',
      'ハムストリングスが伸びるまで下ろす',
      '臀部を締めて起き上がる'
    ],
    tips: [
      '背中は真っ直ぐに保つ',
      '膝の角度は一定',
      'ダンベルは体に沿って動かす',
      'ハムストリングスの伸びを感じる'
    ],
    commonMistakes: ['背中が丸まる', '膝を曲げすぎる', 'ダンベルが体から離れる', '腰で引く'],
    variations: ['single_leg_rdl', 'sumo_rdl', 'barbell_rdl'],
    benefits: ['ハムストリングス強化', 'ヒップヒンジ動作習得', '姿勢改善', '腰痛予防']
  },

  // バーベル種目 - 胸
  barbell_bench_press: {
    id: 'barbell_bench_press',
    name: 'Barbell Bench Press',
    nameJa: 'バーベルベンチプレス',
    category: 'compound',
    primaryMuscles: ['chest', 'triceps'],
    secondaryMuscles: ['shoulders'],
    equipment: ['barbell', 'bench'],
    difficulty: 'intermediate',
    movementPattern: 'push',
    forceType: 'push',
    mechanics: 'compound',
    instructions: [
      'ベンチに仰向けになる',
      'バーを肩幅より広めに握る',
      'バーを胸まで下ろす',
      '胸で押し上げる',
      '肘を完全に伸ばす'
    ],
    tips: [
      '肩甲骨を寄せて胸を張る',
      '足はしっかり床につける',
      'バーは胸の下部に下ろす',
      'アーチは自然な範囲で'
    ],
    commonMistakes: ['バウンドさせる', 'お尻が浮く', '手幅が不適切', '肩がすくむ'],
    variations: ['incline_barbell_press', 'decline_barbell_press', 'close_grip_bench_press'],
    benefits: ['上半身の最大筋力向上', '複数筋群の協調', '重量を扱いやすい', '測定可能な進歩']
  },

  // バーベル種目 - 背中
  barbell_row: {
    id: 'barbell_row',
    name: 'Barbell Row',
    nameJa: 'バーベルロウ',
    category: 'compound',
    primaryMuscles: ['back', 'lats'],
    secondaryMuscles: ['biceps', 'rear_delts'],
    equipment: ['barbell'],
    difficulty: 'intermediate',
    movementPattern: 'pull',
    forceType: 'pull',
    mechanics: 'compound',
    instructions: [
      'バーベルを肩幅で握る',
      '膝を軽く曲げ、上体を前傾',
      'バーを腹部に向かって引く',
      '肩甲骨を寄せる',
      'コントロールして下ろす'
    ],
    tips: [
      '背中は真っ直ぐに保つ',
      '肘を体に近づけて引く',
      '腕ではなく背中で引く',
      '体の角度は45度程度'
    ],
    commonMistakes: ['体を起こしすぎる', '反動を使う', '背中が丸まる', '肘が外に開く'],
    variations: ['pendlay_row', 'yates_row', 't_bar_row'],
    benefits: ['背中の厚み増加', '複合的な筋力向上', '姿勢改善', 'デッドリフトの補助']
  },

  // バーベル種目 - 脚
  barbell_squat: {
    id: 'barbell_squat',
    name: 'Barbell Back Squat',
    nameJa: 'バーベルバックスクワット',
    category: 'compound',
    primaryMuscles: ['quadriceps', 'glutes'],
    secondaryMuscles: ['hamstrings', 'core', 'calves'],
    equipment: ['barbell', 'squat_rack'],
    difficulty: 'intermediate',
    movementPattern: 'squat',
    forceType: 'push',
    mechanics: 'compound',
    instructions: [
      'バーを僧帽筋上部に乗せる',
      '足を肩幅より少し広めに開く',
      '胸を張り、体幹を締める',
      '股関節と膝を曲げて下ろす',
      '太ももが平行になったら立ち上がる'
    ],
    tips: [
      '膝とつま先の向きを揃える',
      '踵に重心を置く',
      '深呼吸して体幹を固定',
      '目線は前方やや上'
    ],
    commonMistakes: ['膝が内側に入る', '踵が浮く', '前傾しすぎる', '深さが不十分'],
    variations: ['front_squat', 'box_squat', 'pause_squat', 'high_bar_squat'],
    benefits: ['下半身の総合的強化', '成長ホルモン分泌', '基礎代謝向上', '全身の筋力向上']
  },

  conventional_deadlift: {
    id: 'conventional_deadlift',
    name: 'Conventional Deadlift',
    nameJa: 'コンベンショナルデッドリフト',
    category: 'compound',
    primaryMuscles: ['glutes', 'hamstrings', 'lower_back'],
    secondaryMuscles: ['traps', 'lats', 'core', 'forearms'],
    equipment: ['barbell'],
    difficulty: 'advanced',
    movementPattern: 'hinge',
    forceType: 'pull',
    mechanics: 'compound',
    instructions: [
      'バーの前に立ち、足を腰幅に開く',
      '腰を落とし、肩幅でバーを握る',
      '胸を張り、背中を真っ直ぐに',
      '脚と背中で同時に引き上げる',
      '完全に立ち上がったら下ろす'
    ],
    tips: [
      'バーは体に沿って動かす',
      '肩甲骨を下げて胸を張る',
      '腹圧を高めて体幹固定',
      '踵で床を押す'
    ],
    commonMistakes: ['背中が丸まる', 'バーが体から離れる', '膝が前に出すぎる', '腰で引く'],
    variations: ['sumo_deadlift', 'romanian_deadlift', 'trap_bar_deadlift', 'deficit_deadlift'],
    benefits: ['全身の筋力向上', '後側連鎖の強化', 'パワー向上', '機能的な動作パターン']
  },

  // バーベル種目 - 肩
  military_press: {
    id: 'military_press',
    name: 'Military Press',
    nameJa: 'ミリタリープレス',
    category: 'compound',
    primaryMuscles: ['shoulders'],
    secondaryMuscles: ['triceps', 'core', 'upper_back'],
    equipment: ['barbell'],
    difficulty: 'intermediate',
    movementPattern: 'push',
    forceType: 'push',
    mechanics: 'compound',
    instructions: [
      'バーベルを鎖骨の前で持つ',
      '足を肩幅に開いて立つ',
      'バーを頭上に押し上げる',
      '肘を完全に伸ばす',
      'コントロールして下ろす'
    ],
    tips: [
      '体幹をしっかり締める',
      '腰を反らせすぎない',
      '肘は前方に向ける',
      'バーは頭の真上へ'
    ],
    commonMistakes: ['腰を反らせすぎる', '脚で反動をつける', 'バーが前後する', '手幅が狭すぎる'],
    variations: ['push_press', 'behind_neck_press', 'seated_military_press'],
    benefits: ['肩の筋力向上', '体幹の安定性', 'オーバーヘッド強化', '全身の連動性']
  },

  upright_row: {
    id: 'upright_row',
    name: 'Upright Row',
    nameJa: 'アップライトロウ',
    category: 'compound',
    primaryMuscles: ['shoulders', 'traps'],
    secondaryMuscles: ['biceps'],
    equipment: ['barbell'],
    difficulty: 'intermediate',
    movementPattern: 'pull',
    forceType: 'pull',
    mechanics: 'compound',
    instructions: [
      'バーベルを肩幅より狭く握る',
      '腕を下ろした状態から始める',
      '肘を高く上げながらバーを引く',
      '顎の下まで引き上げる',
      'ゆっくりと下ろす'
    ],
    tips: [
      '肘が手首より高く',
      'バーは体に沿って動かす',
      '肩をすくめない',
      '無理な高さまで上げない'
    ],
    commonMistakes: ['手幅が狭すぎる', '肩をすくめる', '手首が曲がる', '反動を使う'],
    variations: ['wide_grip_upright_row', 'cable_upright_row', 'dumbbell_upright_row'],
    benefits: ['肩と僧帽筋の発達', '上半身の引く力', '肩幅を広く見せる', '握力向上']
  },

  // プルアップバー種目
  pullup: {
    id: 'pullup',
    name: 'Pull-up',
    nameJa: 'プルアップ',
    category: 'compound',
    primaryMuscles: ['lats', 'back'],
    secondaryMuscles: ['biceps', 'core', 'shoulders'],
    equipment: ['pullup_bar'],
    difficulty: 'intermediate',
    movementPattern: 'pull',
    forceType: 'pull',
    mechanics: 'compound',
    instructions: [
      'バーを肩幅より広めに順手で握る',
      '肩甲骨を下げて胸を張る',
      '肘を体に引き付けながら引き上げる',
      '顎がバーを越えるまで上げる',
      'コントロールして下ろす'
    ],
    tips: [
      '反動を使わない',
      '体幹を締めて安定させる',
      '肩甲骨から動かす',
      'フルレンジで動作'
    ],
    commonMistakes: ['反動を使う', '可動域が狭い', '肩がすくむ', '体が前後に揺れる'],
    variations: ['wide_grip_pullup', 'neutral_grip_pullup', 'weighted_pullup', 'l_sit_pullup'],
    benefits: ['背中の広がりを作る', '相対的筋力向上', '握力強化', 'V字体型形成']
  },

  chinup: {
    id: 'chinup',
    name: 'Chin-up',
    nameJa: 'チンアップ',
    category: 'compound',
    primaryMuscles: ['lats', 'biceps'],
    secondaryMuscles: ['back', 'core', 'shoulders'],
    equipment: ['pullup_bar'],
    difficulty: 'intermediate',
    movementPattern: 'pull',
    forceType: 'pull',
    mechanics: 'compound',
    instructions: [
      'バーを肩幅で逆手に握る',
      '肩甲骨を下げて準備',
      '肘を曲げて体を引き上げる',
      '顎がバーを越えるまで',
      'ゆっくりと下ろす'
    ],
    tips: [
      '二頭筋も使って引く',
      '体を真っ直ぐに保つ',
      '肩甲骨を寄せる',
      '呼吸を整える'
    ],
    commonMistakes: ['半分しか上がらない', '反動を使う', '下で完全に伸ばさない', '首を前に出す'],
    variations: ['close_grip_chinup', 'weighted_chinup', 'negative_chinup'],
    benefits: ['上腕二頭筋の発達', '背中の厚み', '引く力の向上', 'プルアップより易しい']
  },

  hanging_knee_raise: {
    id: 'hanging_knee_raise',
    name: 'Hanging Knee Raise',
    nameJa: 'ハンギングニーレイズ',
    category: 'core',
    primaryMuscles: ['lower_abs', 'hip_flexors'],
    secondaryMuscles: ['core', 'forearms'],
    equipment: ['pullup_bar'],
    difficulty: 'intermediate',
    movementPattern: 'rotation',
    forceType: 'pull',
    mechanics: 'compound',
    instructions: [
      'バーにぶら下がる',
      '肩幅で握る',
      '膝を胸に向かって引き上げる',
      '腹筋を収縮させる',
      'コントロールして下ろす'
    ],
    tips: [
      '体の揺れを最小限に',
      '反動を使わない',
      '呼吸は上げる時に吐く',
      '腹筋に意識を集中'
    ],
    commonMistakes: ['体が揺れる', '反動を使う', '腰が反る', '握力が先に疲れる'],
    variations: ['hanging_leg_raise', 'hanging_oblique_raise', 'toes_to_bar'],
    benefits: ['下腹部の強化', '体幹の安定性', '握力向上', '腸腰筋の強化']
  },

  // その他の器具
  cable_fly: {
    id: 'cable_fly',
    name: 'Cable Fly',
    nameJa: 'ケーブルフライ',
    category: 'isolation',
    primaryMuscles: ['chest'],
    secondaryMuscles: ['shoulders'],
    equipment: ['cable'],
    difficulty: 'intermediate',
    movementPattern: 'push',
    forceType: 'push',
    mechanics: 'isolation',
    instructions: [
      'ケーブルを胸の高さに設定',
      'ハンドルを持って一歩前に出る',
      '腕を横に開いた状態から始める',
      '胸の前で手を合わせる',
      'ゆっくりと開いて戻す'
    ],
    tips: [
      '肘は軽く曲げたまま',
      '胸の収縮を意識',
      '肩甲骨を寄せて胸を張る',
      '一定のテンポで動作'
    ],
    commonMistakes: ['肘を伸ばしすぎる', '腕で引く', '体が前後する', '可動域が狭い'],
    variations: ['low_cable_fly', 'high_cable_fly', 'single_arm_cable_fly'],
    benefits: ['胸筋の形を整える', '一定の負荷', '安全性が高い', '収縮感が得やすい']
  },

  tricep_pushdown: {
    id: 'tricep_pushdown',
    name: 'Tricep Pushdown',
    nameJa: 'トライセッププッシュダウン',
    category: 'isolation',
    primaryMuscles: ['triceps'],
    secondaryMuscles: [],
    equipment: ['cable'],
    difficulty: 'beginner',
    movementPattern: 'push',
    forceType: 'push',
    mechanics: 'isolation',
    instructions: [
      'ケーブルマシンの前に立つ',
      'バーを肩幅で握る',
      '肘を体の横に固定',
      '前腕だけを動かして押し下げる',
      'ゆっくりと戻す'
    ],
    tips: [
      '肘を動かさない',
      '体を少し前傾',
      '三頭筋を絞る',
      '肩をすくめない'
    ],
    commonMistakes: ['肘が前後する', '反動を使う', '体重をかける', '可動域が狭い'],
    variations: ['rope_pushdown', 'reverse_grip_pushdown', 'single_arm_pushdown'],
    benefits: ['三頭筋の集中強化', '肘への負担が少ない', '初心者に優しい', '高回数可能']
  },

  face_pull: {
    id: 'face_pull',
    name: 'Face Pull',
    nameJa: 'フェイスプル',
    category: 'compound',
    primaryMuscles: ['rear_delts', 'upper_back'],
    secondaryMuscles: ['traps', 'rhomboids'],
    equipment: ['cable'],
    difficulty: 'beginner',
    movementPattern: 'pull',
    forceType: 'pull',
    mechanics: 'compound',
    instructions: [
      'ケーブルを顔の高さに設定',
      'ロープを両手で握る',
      '顔に向かって引く',
      '肘を高く保ちながら引く',
      '肩甲骨を寄せる'
    ],
    tips: [
      '肘は肩より高く',
      '後ろ肩を意識',
      'ゆっくりとした動作',
      '体幹を安定させる'
    ],
    commonMistakes: ['肘が下がる', '腰を反る', '引きすぎる', '首に力が入る'],
    variations: ['high_face_pull', 'seated_face_pull', 'band_face_pull'],
    benefits: ['肩の健康維持', '姿勢改善', '肩甲骨周りの強化', 'ベンチプレスのバランス']
  },

  // 追加のダンベル種目
  dumbbell_step_up: {
    id: 'dumbbell_step_up',
    name: 'Dumbbell Step-up',
    nameJa: 'ダンベルステップアップ',
    category: 'compound',
    primaryMuscles: ['quadriceps', 'glutes'],
    secondaryMuscles: ['hamstrings', 'calves', 'core'],
    equipment: ['dumbbell', 'box'],
    difficulty: 'intermediate',
    movementPattern: 'squat',
    forceType: 'push',
    mechanics: 'compound',
    instructions: [
      'ダンベルを両手に持つ',
      '片足を台に乗せる',
      '前足で押して体を持ち上げる',
      '後ろ足を台に揃える',
      'コントロールして下りる'
    ],
    tips: [
      '前足の力で上がる',
      '膝とつま先の向きを揃える',
      '上体は真っ直ぐ',
      'バランスを保つ'
    ],
    commonMistakes: ['後ろ足で押す', '前傾しすぎる', '台が高すぎる', '下りる時に落ちる'],
    variations: ['lateral_step_up', 'crossover_step_up', 'explosive_step_up'],
    benefits: ['片脚の筋力強化', '機能的動作', 'バランス向上', '心肺機能向上']
  },

  arnold_press: {
    id: 'arnold_press',
    name: 'Arnold Press',
    nameJa: 'アーノルドプレス',
    category: 'compound',
    primaryMuscles: ['shoulders'],
    secondaryMuscles: ['triceps', 'upper_chest'],
    equipment: ['dumbbell'],
    difficulty: 'intermediate',
    movementPattern: 'push',
    forceType: 'push',
    mechanics: 'compound',
    instructions: [
      'ダンベルを顔の前で持つ（手のひらが自分向き）',
      '肘を開きながらダンベルを回転',
      '通常のプレス位置まで回転',
      'そのまま頭上に押し上げる',
      '逆の動作で戻す'
    ],
    tips: [
      '回転はスムーズに',
      '肩全体を使う',
      '体幹を安定させる',
      '軽い重量から始める'
    ],
    commonMistakes: ['回転が速すぎる', '腰を反る', '可動域が狭い', '左右のタイミングがずれる'],
    variations: ['seated_arnold_press', 'single_arm_arnold_press', 'standing_arnold_press'],
    benefits: ['肩の全範囲刺激', '三角筋前部の発達', '安定筋の強化', '筋肉への新しい刺激']
  },

  // バーベル追加種目
  front_squat: {
    id: 'front_squat',
    name: 'Front Squat',
    nameJa: 'フロントスクワット',
    category: 'compound',
    primaryMuscles: ['quadriceps', 'core'],
    secondaryMuscles: ['glutes', 'upper_back'],
    equipment: ['barbell', 'squat_rack'],
    difficulty: 'advanced',
    movementPattern: 'squat',
    forceType: 'push',
    mechanics: 'compound',
    instructions: [
      'バーを肩の前、鎖骨の上に乗せる',
      '肘を高く上げて前に向ける',
      '上体を立てたまま下ろす',
      '太ももが平行まで下げる',
      '踵で押して立ち上がる'
    ],
    tips: [
      '肘を高く保つ',
      '体幹をより強く締める',
      '膝を前に出してOK',
      '手首の柔軟性が必要'
    ],
    commonMistakes: ['肘が下がる', 'バーが前に落ちる', '前傾する', '深さ不足'],
    variations: ['zombie_front_squat', 'front_squat_with_straps', 'goblet_squat'],
    benefits: ['大腿四頭筋の集中強化', '体幹の超強化', 'オリンピックリフトの基礎', '膝に優しい']
  },

  sumo_deadlift: {
    id: 'sumo_deadlift',
    name: 'Sumo Deadlift',
    nameJa: 'スモウデッドリフト',
    category: 'compound',
    primaryMuscles: ['glutes', 'quadriceps', 'hamstrings'],
    secondaryMuscles: ['lower_back', 'traps', 'adductors'],
    equipment: ['barbell'],
    difficulty: 'advanced',
    movementPattern: 'hinge',
    forceType: 'pull',
    mechanics: 'compound',
    instructions: [
      '足を大きく開いてつま先を外に向ける',
      'バーの内側を肩幅で握る',
      '胸を張り、腰を落とす',
      '脚で押しながら引き上げる',
      '腰と膝を同時に伸ばす'
    ],
    tips: [
      '膝をつま先方向に開く',
      '上体はより立てる',
      'バーは体に近づける',
      '内転筋を使う'
    ],
    commonMistakes: ['膝が内側に入る', '腰が高すぎる', 'つま先が前を向く', '股関節が硬い'],
    variations: ['semi_sumo_deadlift', 'sumo_deadlift_high_pull', 'deficit_sumo_deadlift'],
    benefits: ['股関節への負担軽減', '内転筋の強化', '短い可動域', '高重量を扱いやすい']
  },

  barbell_curl: {
    id: 'barbell_curl',
    name: 'Barbell Curl',
    nameJa: 'バーベルカール',
    category: 'isolation',
    primaryMuscles: ['biceps'],
    secondaryMuscles: ['forearms'],
    equipment: ['barbell'],
    difficulty: 'beginner',
    movementPattern: 'pull',
    forceType: 'pull',
    mechanics: 'isolation',
    instructions: [
      'バーベルを肩幅で下から握る',
      '肘を体の横に固定',
      '前腕を曲げてバーを上げる',
      '二頭筋を収縮させる',
      'ゆっくりと下ろす'
    ],
    tips: [
      '肘を前後させない',
      '反動を使わない',
      '手首を真っ直ぐ',
      'フルレンジで動作'
    ],
    commonMistakes: ['体を揺らす', '肘が動く', '手首が曲がる', '肩をすくめる'],
    variations: ['ez_bar_curl', 'preacher_curl', 'reverse_curl', '21s'],
    benefits: ['二頭筋の総負荷量増加', '左右同時に鍛える', '重量設定が簡単', 'プログレッシブオーバーロード']
  },

  close_grip_bench_press: {
    id: 'close_grip_bench_press',
    name: 'Close Grip Bench Press',
    nameJa: 'クローズグリップベンチプレス',
    category: 'compound',
    primaryMuscles: ['triceps', 'chest'],
    secondaryMuscles: ['shoulders'],
    equipment: ['barbell', 'bench'],
    difficulty: 'intermediate',
    movementPattern: 'push',
    forceType: 'push',
    mechanics: 'compound',
    instructions: [
      'バーを肩幅かそれより狭く握る',
      'ベンチに仰向けになる',
      'バーを胸の下部に下ろす',
      '肘を体に近づけたまま',
      '三頭筋で押し上げる'
    ],
    tips: [
      '肘を開かない',
      '手首を真っ直ぐ保つ',
      '胸ではなく三頭筋で押す',
      'グリップは狭すぎない'
    ],
    commonMistakes: ['グリップが狭すぎる', '肘が開く', '手首が痛い', 'バーが不安定'],
    variations: ['dumbbell_close_grip_press', 'floor_press', 'board_press'],
    benefits: ['三頭筋の高重量トレーニング', '複合的な上半身強化', 'ベンチプレスの補助', 'ロックアウト強化']
  },

  barbell_hip_thrust: {
    id: 'barbell_hip_thrust',
    name: 'Barbell Hip Thrust',
    nameJa: 'バーベルヒップスラスト',
    category: 'compound',
    primaryMuscles: ['glutes'],
    secondaryMuscles: ['hamstrings', 'core'],
    equipment: ['barbell', 'bench'],
    difficulty: 'intermediate',
    movementPattern: 'hinge',
    forceType: 'push',
    mechanics: 'compound',
    instructions: [
      '肩甲骨をベンチに乗せる',
      'バーベルを腰骨の上に乗せる',
      '足を腰幅に開く',
      'お尻を締めながら腰を上げる',
      'トップで1-2秒キープ'
    ],
    tips: [
      'パッドを使用する',
      '顎を引く',
      '腰を反らせない',
      'お尻の収縮を最大化'
    ],
    commonMistakes: ['腰を反る', '足の位置が悪い', 'テンポが速すぎる', '可動域が狭い'],
    variations: ['single_leg_hip_thrust', 'banded_hip_thrust', 'pause_hip_thrust'],
    benefits: ['臀筋の最大活性化', 'スプリント力向上', 'ジャンプ力向上', '腰痛予防']
  },

  // ケトルベル種目
  kettlebell_swing: {
    id: 'kettlebell_swing',
    name: 'Kettlebell Swing',
    nameJa: 'ケトルベルスイング',
    category: 'compound',
    primaryMuscles: ['glutes', 'hamstrings'],
    secondaryMuscles: ['core', 'shoulders', 'back'],
    equipment: ['kettlebell'],
    difficulty: 'intermediate',
    movementPattern: 'hinge',
    forceType: 'pull',
    mechanics: 'compound',
    instructions: [
      'ケトルベルを両手で持つ',
      '足を肩幅より広めに開く',
      'ヒップヒンジで後ろに引く',
      '臀部の力で前に振り出す',
      '肩の高さまで振り上げる'
    ],
    tips: [
      '腕は鞭のように使う',
      '臀部の爆発的な収縮',
      '背中は常に真っ直ぐ',
      '呼吸のタイミングを合わせる'
    ],
    commonMistakes: ['スクワット動作になる', '腕で持ち上げる', '腰が反る', 'コントロール不足'],
    variations: ['single_arm_swing', 'american_swing', 'double_kettlebell_swing'],
    benefits: ['爆発的パワー向上', '心肺機能向上', '後側連鎖の強化', '脂肪燃焼効果']
  },

  turkish_getup: {
    id: 'turkish_getup',
    name: 'Turkish Get-up',
    nameJa: 'ターキッシュゲットアップ',
    category: 'compound',
    primaryMuscles: ['full_body', 'core'],
    secondaryMuscles: ['shoulders', 'glutes'],
    equipment: ['kettlebell'],
    difficulty: 'advanced',
    movementPattern: 'carry',
    forceType: 'static',
    mechanics: 'compound',
    instructions: [
      '仰向けでケトルベルを片手で持ち上げる',
      '反対の肘をついて起き上がる',
      '手をついて腰を上げる',
      '脚を後ろに引いてランジ姿勢',
      '立ち上がる（逆の手順で戻る）'
    ],
    tips: [
      '各段階でしっかり安定',
      '重りは常に真上に',
      '目線は重りを見続ける',
      'ゆっくりと正確に'
    ],
    commonMistakes: ['動作が速すぎる', '重りが不安定', '段階を飛ばす', '呼吸を止める'],
    variations: ['half_turkish_getup', 'reverse_turkish_getup', 'bottoms_up_getup'],
    benefits: ['全身の協調性', '肩の安定性', '体幹の強化', '機能的動作の習得']
  },

  farmers_walk: {
    id: 'farmers_walk',
    name: 'Farmers Walk',
    nameJa: 'ファーマーズウォーク',
    category: 'compound',
    primaryMuscles: ['full_body', 'grip'],
    secondaryMuscles: ['core', 'traps', 'shoulders'],
    equipment: ['dumbbell', 'kettlebell'],
    difficulty: 'intermediate',
    movementPattern: 'carry',
    forceType: 'static',
    mechanics: 'compound',
    instructions: [
      '重りを両手に持つ',
      '胸を張って立つ',
      '自然な歩幅で歩く',
      '体幹を安定させる',
      '指定距離または時間歩く'
    ],
    tips: [
      '肩を下げてリラックス',
      '握力が限界まで保持',
      '呼吸を続ける',
      '姿勢を崩さない'
    ],
    commonMistakes: ['前傾する', '肩がすくむ', '歩幅が大きすぎる', '体が左右に揺れる'],
    variations: ['single_arm_farmers_walk', 'overhead_carry', 'mixed_carry'],
    benefits: ['握力の強化', '体幹の安定性', '全身の筋持久力', '実用的な筋力']
  }
};