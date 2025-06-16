/**
 * エクササイズデータベース - フェーズ1
 * 基本的な自重トレーニング20種目
 */

import { Exercise } from './exerciseDatabase';

export const PHASE1_EXERCISES: Record<string, Exercise> = {
  // 既存のプッシュアップを上書き（より詳細な情報）
  pushup: {
    id: 'pushup',
    name: 'Push-up',
    nameJa: 'プッシュアップ',
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
      '足を後ろに伸ばし、つま先で体を支える',
      '頭からかかとまで一直線になるよう体を保つ',
      '肘を曲げて胸を床に近づける',
      '床を押して元の位置に戻る'
    ],
    tips: [
      '体を一直線に保つことを意識',
      '肘は45度程度の角度で曲げる',
      '呼吸は下げる時に吸い、上げる時に吐く',
      '首は自然な位置を保つ'
    ],
    commonMistakes: ['腰が落ちる', '肘が外側に開きすぎる', '可動域が狭い', '首が過度に前に出る'],
    variations: ['knee_pushup', 'incline_pushup', 'decline_pushup', 'diamond_pushup', 'wide_pushup'],
    benefits: ['上半身の基礎筋力向上', '体幹の強化', '自宅でも実施可能', '機能的な押す動作の強化']
  },

  // 既存のスクワットは exerciseDatabase.ts にあるのでスキップ

  // 追加の基本種目
  lunge: {
    id: 'lunge',
    name: 'Forward Lunge',
    nameJa: 'フォワードランジ',
    category: 'compound',
    primaryMuscles: ['quadriceps', 'glutes'],
    secondaryMuscles: ['hamstrings', 'calves', 'core'],
    equipment: ['none'],
    difficulty: 'beginner',
    movementPattern: 'squat',
    forceType: 'push',
    mechanics: 'compound',
    instructions: [
      '足を腰幅に開いて立つ',
      '片足を大きく前に踏み出す',
      '両膝を曲げて体を下ろす',
      '前膝が90度、後膝が床に近づくまで下げる',
      '前足で床を押して元の位置に戻る'
    ],
    tips: [
      '上体は垂直に保つ',
      '前膝がつま先を超えないよう注意',
      '体重は前足に乗せる',
      'バランスを保ちながらゆっくり動作'
    ],
    commonMistakes: ['歩幅が狭すぎる', '上体が前傾する', '膝が内側に入る', 'バランスを崩す'],
    variations: ['reverse_lunge', 'side_lunge', 'walking_lunge', 'jumping_lunge'],
    benefits: ['片脚ずつの筋力強化', 'バランス能力向上', '左右差の改善', '日常動作の向上']
  },

  glute_bridge: {
    id: 'glute_bridge',
    name: 'Glute Bridge',
    nameJa: 'グルートブリッジ',
    category: 'isolation',
    primaryMuscles: ['glutes'],
    secondaryMuscles: ['hamstrings', 'core'],
    equipment: ['none'],
    difficulty: 'beginner',
    movementPattern: 'hinge',
    forceType: 'push',
    mechanics: 'isolation',
    instructions: [
      '仰向けに寝て、膝を曲げる',
      '足は腰幅に開き、かかとをお尻に近づける',
      'お尻を締めながら腰を持ち上げる',
      '肩から膝まで一直線になるまで上げる',
      'ゆっくりと元の位置に戻る'
    ],
    tips: [
      'お尻の筋肉を意識して締める',
      '腰を反らせすぎない',
      '最上部で1-2秒キープ',
      'かかとで床を押す意識'
    ],
    commonMistakes: ['腰を反らせすぎる', '足の位置が遠すぎる', 'お尻を使わず腰で上げる', '首に力が入る'],
    variations: ['single_leg_glute_bridge', 'hip_thrust', 'banded_glute_bridge'],
    benefits: ['臀筋の活性化', '腰痛予防', '姿勢改善', 'パワー向上の基礎']
  },

  calf_raise: {
    id: 'calf_raise',
    name: 'Calf Raise',
    nameJa: 'カーフレイズ',
    category: 'isolation',
    primaryMuscles: ['calves'],
    secondaryMuscles: [],
    equipment: ['none'],
    difficulty: 'beginner',
    movementPattern: 'push',
    forceType: 'push',
    mechanics: 'isolation',
    instructions: [
      '足を腰幅に開いて立つ',
      'つま先立ちになるように踵を上げる',
      'ふくらはぎが収縮するのを感じる',
      '最上部で1秒キープ',
      'ゆっくりと踵を下ろす'
    ],
    tips: [
      'バランスが必要な場合は壁に手をつく',
      '母趾球で床を押す',
      '可動域を最大限使う',
      'ゆっくりとコントロールして動作'
    ],
    commonMistakes: ['動作が速すぎる', '可動域が狭い', '膝が曲がる', '重心が前後にぶれる'],
    variations: ['single_leg_calf_raise', 'seated_calf_raise', 'donkey_calf_raise'],
    benefits: ['ふくらはぎの強化', 'ジャンプ力向上', 'ランニング能力向上', '足首の安定性向上']
  },

  side_plank: {
    id: 'side_plank',
    name: 'Side Plank',
    nameJa: 'サイドプランク',
    category: 'core',
    primaryMuscles: ['obliques', 'core'],
    secondaryMuscles: ['shoulders', 'glutes'],
    equipment: ['none'],
    difficulty: 'intermediate',
    movementPattern: 'rotation',
    forceType: 'static',
    mechanics: 'isolation',
    instructions: [
      '横向きに寝て、肘を肩の真下に置く',
      '足を重ねるか、前後にずらす',
      '腰を持ち上げて体を一直線にする',
      'この姿勢を保持する',
      '反対側も同様に行う'
    ],
    tips: [
      '肩から足まで一直線を保つ',
      '腰が落ちないよう注意',
      '呼吸を止めない',
      '首は自然な位置を保つ'
    ],
    commonMistakes: ['腰が落ちる', '体が前後に傾く', '肩に過度な負担', '呼吸を止める'],
    variations: ['knee_side_plank', 'side_plank_with_leg_raise', 'side_plank_rotation'],
    benefits: ['体幹の側面強化', '姿勢改善', '腰痛予防', 'バランス能力向上']
  },

  burpee: {
    id: 'burpee',
    name: 'Burpee',
    nameJa: 'バーピー',
    category: 'compound',
    primaryMuscles: ['full_body'],
    secondaryMuscles: ['cardio'],
    equipment: ['none'],
    difficulty: 'intermediate',
    movementPattern: 'cardio',
    forceType: 'push',
    mechanics: 'compound',
    instructions: [
      '立った状態から始める',
      'しゃがんで両手を床につく',
      '両足を後ろに跳ばしてプランク姿勢',
      'プッシュアップを1回行う（オプション）',
      '足を手の近くに戻す',
      '立ち上がりながらジャンプ'
    ],
    tips: [
      '流れるような動作を心がける',
      'フォームを崩さない範囲でスピードを上げる',
      '呼吸を整えながら行う',
      '着地は柔らかく'
    ],
    commonMistakes: ['動作が雑になる', '腰を痛めやすい姿勢', 'ジャンプを省略', '呼吸が乱れる'],
    variations: ['half_burpee', 'burpee_box_jump', 'burpee_broad_jump'],
    benefits: ['全身の筋力向上', '心肺機能向上', '脂肪燃焼効果', '運動能力の総合的向上']
  },

  jumping_jack: {
    id: 'jumping_jack',
    name: 'Jumping Jack',
    nameJa: 'ジャンピングジャック',
    category: 'cardio',
    primaryMuscles: ['full_body'],
    secondaryMuscles: ['cardio'],
    equipment: ['none'],
    difficulty: 'beginner',
    movementPattern: 'cardio',
    forceType: 'push',
    mechanics: 'compound',
    instructions: [
      '足を閉じて立ち、腕は体の横に',
      'ジャンプしながら足を横に開く',
      '同時に腕を頭上に上げる',
      '再びジャンプして元の位置に戻る',
      'リズミカルに繰り返す'
    ],
    tips: [
      '着地は柔らかく、膝を少し曲げる',
      'リズムを保って動作',
      '腕はしっかり上まで上げる',
      '呼吸を整えながら行う'
    ],
    commonMistakes: ['着地が硬い', 'リズムが乱れる', '腕の動きが不完全', '膝が内側に入る'],
    variations: ['half_jack', 'cross_jack', 'squat_jack'],
    benefits: ['ウォームアップに最適', '心拍数の上昇', '協調性の向上', '全身の活性化']
  },

  mountain_climber: {
    id: 'mountain_climber',
    name: 'Mountain Climber',
    nameJa: 'マウンテンクライマー',
    category: 'compound',
    primaryMuscles: ['core', 'shoulders'],
    secondaryMuscles: ['quadriceps', 'cardio'],
    equipment: ['none'],
    difficulty: 'intermediate',
    movementPattern: 'cardio',
    forceType: 'push',
    mechanics: 'compound',
    instructions: [
      'プランクの姿勢から始める',
      '片膝を胸に向かって引き寄せる',
      '素早く足を入れ替える',
      '腰の位置を一定に保ちながら繰り返す',
      'ランニングのような動作で行う'
    ],
    tips: [
      '腰が上下しないよう注意',
      '体幹をしっかり固定',
      'リズミカルに動作',
      '呼吸を止めない'
    ],
    commonMistakes: ['腰が高く上がる', '体幹が安定しない', 'スピードが速すぎてフォームが崩れる', '肩に過度な負担'],
    variations: ['slow_mountain_climber', 'cross_body_mountain_climber', 'mountain_climber_twist'],
    benefits: ['体幹の強化', '心肺機能向上', '敏捷性の向上', 'カロリー消費']
  },

  high_knee: {
    id: 'high_knee',
    name: 'High Knee',
    nameJa: 'ハイニー',
    category: 'cardio',
    primaryMuscles: ['hip_flexors', 'quadriceps'],
    secondaryMuscles: ['calves', 'core', 'cardio'],
    equipment: ['none'],
    difficulty: 'beginner',
    movementPattern: 'cardio',
    forceType: 'push',
    mechanics: 'compound',
    instructions: [
      'その場で立つ',
      '片膝を腰の高さまで上げる',
      '素早く足を入れ替える',
      '腕を振りながらランニング動作',
      'リズミカルに繰り返す'
    ],
    tips: [
      '膝をしっかり高く上げる',
      '着地は前足部で柔らかく',
      '上体は真っ直ぐ保つ',
      '腕の振りも使う'
    ],
    commonMistakes: ['膝が十分上がらない', '上体が前傾する', '着地が硬い', 'リズムが乱れる'],
    variations: ['high_knee_run', 'high_knee_skip', 'high_knee_with_arm_reach'],
    benefits: ['心拍数上昇', '下半身の筋持久力向上', '協調性向上', 'ウォームアップ効果']
  },

  reverse_crunch: {
    id: 'reverse_crunch',
    name: 'Reverse Crunch',
    nameJa: 'リバースクランチ',
    category: 'core',
    primaryMuscles: ['lower_abs'],
    secondaryMuscles: ['hip_flexors'],
    equipment: ['none'],
    difficulty: 'beginner',
    movementPattern: 'rotation',
    forceType: 'pull',
    mechanics: 'isolation',
    instructions: [
      '仰向けに寝て、腕は体の横に置く',
      '膝を90度に曲げて持ち上げる',
      '膝を胸に向かって引き寄せる',
      '腰を床から少し浮かせる',
      'ゆっくりと元の位置に戻る'
    ],
    tips: [
      '動作はゆっくりコントロール',
      '反動を使わない',
      '腹筋下部を意識',
      '呼吸は引き寄せる時に吐く'
    ],
    commonMistakes: ['反動を使う', '首に力が入る', '可動域が狭い', '速すぎる動作'],
    variations: ['straight_leg_reverse_crunch', 'reverse_crunch_on_bench', 'weighted_reverse_crunch'],
    benefits: ['下腹部の強化', '体幹の安定性向上', '腰への負担が少ない', '姿勢改善']
  },

  side_lunge: {
    id: 'side_lunge',
    name: 'Side Lunge',
    nameJa: 'サイドランジ',
    category: 'compound',
    primaryMuscles: ['quadriceps', 'glutes', 'adductors'],
    secondaryMuscles: ['hamstrings', 'core'],
    equipment: ['none'],
    difficulty: 'beginner',
    movementPattern: 'squat',
    forceType: 'push',
    mechanics: 'compound',
    instructions: [
      '足を大きく横に開いて立つ',
      '片側に体重を移動させながら膝を曲げる',
      '反対の脚は伸ばしたまま',
      '太ももが床と平行になるまで下げる',
      '押し返して元の位置に戻る'
    ],
    tips: [
      '膝とつま先の向きを揃える',
      '背筋を伸ばしたまま動作',
      '内転筋のストレッチを感じる',
      '体重移動をコントロール'
    ],
    commonMistakes: ['膝が内側に入る', '上体が前傾しすぎる', '可動域が狭い', 'バランスを崩す'],
    variations: ['curtsy_lunge', 'lateral_lunge_with_reach', 'cossack_squat'],
    benefits: ['内転筋の強化', '股関節の柔軟性向上', 'バランス能力向上', 'スポーツパフォーマンス向上']
  },

  incline_pushup: {
    id: 'incline_pushup',
    name: 'Incline Push-up',
    nameJa: 'インクラインプッシュアップ',
    category: 'compound',
    primaryMuscles: ['chest', 'triceps'],
    secondaryMuscles: ['shoulders', 'core'],
    equipment: ['bench', 'box', 'stairs'],
    difficulty: 'beginner',
    movementPattern: 'push',
    forceType: 'push',
    mechanics: 'compound',
    instructions: [
      '手を台やベンチの上に置く',
      '体を斜めの一直線に保つ',
      '肘を曲げて胸を台に近づける',
      '押し返して元の位置に戻る',
      '体の角度で難易度調整'
    ],
    tips: [
      '台が高いほど簡単になる',
      '体幹をしっかり固定',
      '肘は45度程度の角度',
      '首は自然な位置を保つ'
    ],
    commonMistakes: ['腰が落ちる', '可動域が狭い', '手の位置が狭すぎる', '頭が下がる'],
    variations: ['wall_pushup', 'knee_pushup', 'standard_pushup'],
    benefits: ['初心者に優しい', '徐々に強度を上げられる', '肩への負担が少ない', 'フォーム習得に最適']
  },

  knee_pushup: {
    id: 'knee_pushup',
    name: 'Knee Push-up',
    nameJa: 'ニープッシュアップ',
    category: 'compound',
    primaryMuscles: ['chest', 'triceps'],
    secondaryMuscles: ['shoulders', 'core'],
    equipment: ['none'],
    difficulty: 'beginner',
    movementPattern: 'push',
    forceType: 'push',
    mechanics: 'compound',
    instructions: [
      '四つん這いの姿勢から始める',
      '手を肩幅より少し広めに置く',
      '膝から頭まで一直線を保つ',
      '肘を曲げて胸を床に近づける',
      '押し返して元の位置に戻る'
    ],
    tips: [
      '膝の下にマットを敷く',
      '体幹を意識して固定',
      '呼吸を忘れずに',
      '徐々に通常のプッシュアップへ移行'
    ],
    commonMistakes: ['腰が反る', '肘が外に開きすぎる', '頭が下がる', '可動域が狭い'],
    variations: ['incline_knee_pushup', 'wide_knee_pushup', 'diamond_knee_pushup'],
    benefits: ['初心者向け', '筋力の基礎作り', '正しいフォームの習得', '関節への負担軽減']
  },

  wall_sit: {
    id: 'wall_sit',
    name: 'Wall Sit',
    nameJa: 'ウォールシット',
    category: 'isolation',
    primaryMuscles: ['quadriceps'],
    secondaryMuscles: ['glutes', 'calves'],
    equipment: ['wall'],
    difficulty: 'beginner',
    movementPattern: 'squat',
    forceType: 'static',
    mechanics: 'isolation',
    instructions: [
      '壁に背中をつけて立つ',
      '足を前に出し、肩幅に開く',
      '壁に沿って体を下ろす',
      '太ももが床と平行になる位置で止める',
      'この姿勢を保持する'
    ],
    tips: [
      '膝の角度は90度を目標',
      '体重は踵にかける',
      '呼吸を止めない',
      '徐々に保持時間を延ばす'
    ],
    commonMistakes: ['膝が内側に入る', '腰が壁から離れる', '太ももが平行でない', '呼吸を止める'],
    variations: ['single_leg_wall_sit', 'wall_sit_with_calf_raise', 'weighted_wall_sit'],
    benefits: ['大腿四頭筋の筋持久力向上', '膝関節の安定性向上', '等尺性収縮の練習', '場所を選ばない']
  },

  leg_raise: {
    id: 'leg_raise',
    name: 'Leg Raise',
    nameJa: 'レッグレイズ',
    category: 'core',
    primaryMuscles: ['lower_abs', 'hip_flexors'],
    secondaryMuscles: ['core'],
    equipment: ['none'],
    difficulty: 'intermediate',
    movementPattern: 'rotation',
    forceType: 'pull',
    mechanics: 'isolation',
    instructions: [
      '仰向けに寝て、手は体の横に置く',
      '脚を伸ばしたまま持ち上げる',
      '垂直になるまで上げる',
      'ゆっくりと下ろすが床にはつけない',
      'この動作を繰り返す'
    ],
    tips: [
      '腰を床に押し付ける意識',
      '動作はゆっくりコントロール',
      '反動を使わない',
      '呼吸は上げる時に吐く'
    ],
    commonMistakes: ['腰が反る', '反動を使う', '下ろす速度が速すぎる', '可動域が狭い'],
    variations: ['bent_knee_leg_raise', 'hanging_leg_raise', 'flutter_kicks'],
    benefits: ['下腹部の強化', '腸腰筋の強化', '体幹の安定性向上', '姿勢改善']
  },

  bicycle_crunch: {
    id: 'bicycle_crunch',
    name: 'Bicycle Crunch',
    nameJa: 'バイシクルクランチ',
    category: 'core',
    primaryMuscles: ['abs', 'obliques'],
    secondaryMuscles: ['hip_flexors'],
    equipment: ['none'],
    difficulty: 'intermediate',
    movementPattern: 'rotation',
    forceType: 'pull',
    mechanics: 'compound',
    instructions: [
      '仰向けに寝て、手を頭の後ろに組む',
      '両膝を90度に曲げて持ち上げる',
      '右肘と左膝を近づけながら体をねじる',
      '反対側も同様に行う',
      '自転車を漕ぐような動作で繰り返す'
    ],
    tips: [
      '肘で引っ張らず体幹でねじる',
      'ゆっくりコントロールして動作',
      '呼吸を止めない',
      '首に力を入れすぎない'
    ],
    commonMistakes: ['動作が速すぎる', '首を引っ張る', '体幹のねじりが不十分', '脚が下がる'],
    variations: ['slow_bicycle_crunch', 'weighted_bicycle_crunch', 'reverse_bicycle_crunch'],
    benefits: ['腹斜筋の強化', '体幹の回旋力向上', '協調性の向上', '腹筋全体の活性化']
  },

  dead_bug: {
    id: 'dead_bug',
    name: 'Dead Bug',
    nameJa: 'デッドバグ',
    category: 'core',
    primaryMuscles: ['core', 'transverse_abdominis'],
    secondaryMuscles: ['hip_flexors', 'shoulders'],
    equipment: ['none'],
    difficulty: 'beginner',
    movementPattern: 'rotation',
    forceType: 'static',
    mechanics: 'compound',
    instructions: [
      '仰向けに寝て、腕を天井に向けて伸ばす',
      '膝を90度に曲げて持ち上げる',
      '右腕と左脚をゆっくり伸ばして下ろす',
      '元の位置に戻る',
      '反対側も同様に行う'
    ],
    tips: [
      '腰を床に押し付けたまま',
      '動作は超ゆっくり',
      '呼吸を止めない',
      '体幹の安定を最優先'
    ],
    commonMistakes: ['腰が反る', '動作が速すぎる', '腕と脚の協調性不足', '呼吸が乱れる'],
    variations: ['single_arm_dead_bug', 'single_leg_dead_bug', 'dead_bug_with_band'],
    benefits: ['深層筋の強化', '体幹の安定性向上', '腰痛予防', '動作の協調性向上']
  },

  crunch: {
    id: 'crunch',
    name: 'Crunch',
    nameJa: 'クランチ',
    category: 'core',
    primaryMuscles: ['upper_abs'],
    secondaryMuscles: ['core'],
    equipment: ['none'],
    difficulty: 'beginner',
    movementPattern: 'rotation',
    forceType: 'pull',
    mechanics: 'isolation',
    instructions: [
      '仰向けに寝て、膝を曲げる',
      '手を頭の後ろか胸の前に置く',
      '肩甲骨が床から離れるまで上体を起こす',
      'ゆっくりと元の位置に戻る',
      '首は自然な位置を保つ'
    ],
    tips: [
      '腹筋を意識して収縮',
      '反動を使わない',
      '呼吸は起き上がる時に吐く',
      '可動域は小さくてOK'
    ],
    commonMistakes: ['首を引っ張る', '反動を使う', '起き上がりすぎる', '呼吸を止める'],
    variations: ['reverse_crunch', 'bicycle_crunch', 'weighted_crunch', 'cable_crunch'],
    benefits: ['腹直筋上部の強化', '基本的な腹筋運動', '初心者に適している', '場所を選ばない']
  },

  hip_thrust: {
    id: 'hip_thrust',
    name: 'Hip Thrust',
    nameJa: 'ヒップスラスト',
    category: 'compound',
    primaryMuscles: ['glutes'],
    secondaryMuscles: ['hamstrings', 'core'],
    equipment: ['bench'],
    difficulty: 'intermediate',
    movementPattern: 'hinge',
    forceType: 'push',
    mechanics: 'compound',
    instructions: [
      '肩甲骨をベンチに乗せる',
      '足は腰幅に開き、膝を90度に曲げる',
      'お尻を締めながら腰を持ち上げる',
      '上部で1-2秒キープ',
      'コントロールしながら下ろす'
    ],
    tips: [
      '顎を引いて視線は前方',
      'お尻の収縮を最大化',
      '腰を反らせすぎない',
      'かかとで床を押す'
    ],
    commonMistakes: ['腰を反らせすぎる', '可動域が狭い', '足の位置が不適切', '上部でキープしない'],
    variations: ['glute_bridge', 'single_leg_hip_thrust', 'banded_hip_thrust', 'barbell_hip_thrust'],
    benefits: ['臀筋の最大活性化', 'パワー向上', '腰痛予防', 'スポーツパフォーマンス向上']
  }
};