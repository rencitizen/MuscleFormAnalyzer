// 実戦テスト用の架空ユーザーデータ

export interface MockUser {
  id: string;
  email: string;
  displayName: string;
  profile: {
    age: number;
    height: number; // cm
    weight: number; // kg
    experience: 'beginner' | 'intermediate' | 'advanced' | 'senior';
    goals: string[];
  };
  stats: {
    totalWorkouts: number;
    currentStreak: number;
    averageFormScore: number;
  };
}

export interface MockWorkoutSession {
  id: string;
  userId: string;
  date: string;
  exercises: MockExercise[];
  duration: number; // minutes
  notes?: string;
}

export interface MockExercise {
  name: string;
  sets: Array<{
    weight: number;
    reps: number;
    restTime: number; // seconds
  }>;
  formScore?: number;
}

// 架空ユーザーデータ
export const mockUsers: MockUser[] = [
  {
    id: 'user1',
    email: 'tanaka.taro@example.com',
    displayName: '田中太郎',
    profile: {
      age: 30,
      height: 175,
      weight: 70,
      experience: 'beginner',
      goals: ['筋力向上', '体重増加', 'フォーム改善']
    },
    stats: {
      totalWorkouts: 12,
      currentStreak: 3,
      averageFormScore: 65
    }
  },
  {
    id: 'user2',
    email: 'sato.hanako@example.com',
    displayName: '佐藤花子',
    profile: {
      age: 25,
      height: 160,
      weight: 52,
      experience: 'intermediate',
      goals: ['ダイエット', '引き締め', '持久力向上']
    },
    stats: {
      totalWorkouts: 48,
      currentStreak: 12,
      averageFormScore: 82
    }
  },
  {
    id: 'user3',
    email: 'yamada.kenta@example.com',
    displayName: '山田健太',
    profile: {
      age: 35,
      height: 180,
      weight: 85,
      experience: 'advanced',
      goals: ['競技力向上', 'パワーリフティング', 'コーチング']
    },
    stats: {
      totalWorkouts: 156,
      currentStreak: 45,
      averageFormScore: 94
    }
  },
  {
    id: 'user4',
    email: 'suzuki.ichiro@example.com',
    displayName: '鈴木一郎',
    profile: {
      age: 60,
      height: 170,
      weight: 68,
      experience: 'senior',
      goals: ['健康維持', '筋力維持', '怪我予防']
    },
    stats: {
      totalWorkouts: 24,
      currentStreak: 5,
      averageFormScore: 78
    }
  }
];

// 3ヶ月分のトレーニング履歴生成
export function generateWorkoutHistory(userId: string, months: number = 3): MockWorkoutSession[] {
  const user = mockUsers.find(u => u.id === userId);
  if (!user) return [];

  const sessions: MockWorkoutSession[] = [];
  const now = new Date();
  const daysToGenerate = months * 30;

  // ユーザーのレベルに応じた基準値
  const levelMultipliers = {
    beginner: { weight: 0.6, volume: 0.7, frequency: 2 },
    intermediate: { weight: 0.8, volume: 0.9, frequency: 3 },
    advanced: { weight: 1.0, volume: 1.0, frequency: 4 },
    senior: { weight: 0.5, volume: 0.6, frequency: 2 }
  };

  const multiplier = levelMultipliers[user.profile.experience];

  // 週あたりのトレーニング頻度に基づいて生成
  for (let i = 0; i < daysToGenerate; i++) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);
    
    // 週に指定回数トレーニング
    if (Math.random() < multiplier.frequency / 7) {
      const sessionType = ['push', 'pull', 'legs'][Math.floor(Math.random() * 3)];
      const session = generateSession(userId, date, sessionType, multiplier);
      sessions.push(session);
    }
  }

  return sessions.reverse(); // 古い順に並べ替え
}

function generateSession(
  userId: string, 
  date: Date, 
  type: string,
  multiplier: any
): MockWorkoutSession {
  const exercises: MockExercise[] = [];
  
  // セッションタイプに応じたエクササイズ
  const exerciseTemplates = {
    push: [
      { name: 'ベンチプレス', baseWeight: 80, baseReps: 10 },
      { name: 'ショルダープレス', baseWeight: 50, baseReps: 12 },
      { name: 'インクラインダンベルプレス', baseWeight: 30, baseReps: 12 }
    ],
    pull: [
      { name: 'デッドリフト', baseWeight: 100, baseReps: 8 },
      { name: 'ラットプルダウン', baseWeight: 60, baseReps: 12 },
      { name: 'ベントオーバーロー', baseWeight: 60, baseReps: 10 }
    ],
    legs: [
      { name: 'スクワット', baseWeight: 90, baseReps: 10 },
      { name: 'レッグプレス', baseWeight: 140, baseReps: 15 },
      { name: 'レッグカール', baseWeight: 40, baseReps: 12 }
    ]
  };

  const templates = exerciseTemplates[type as keyof typeof exerciseTemplates] || exerciseTemplates.push;
  
  templates.forEach(template => {
    const sets = [];
    const setCount = Math.floor(3 + Math.random() * 2); // 3-4セット
    
    for (let i = 0; i < setCount; i++) {
      // 徐々に重量を増やし、レップ数を減らす
      const weightVariation = 1 + (Math.random() * 0.1 - 0.05); // ±5%
      const repsVariation = Math.max(6, template.baseReps - i * 2);
      
      sets.push({
        weight: Math.round(template.baseWeight * multiplier.weight * weightVariation),
        reps: Math.round(repsVariation * multiplier.volume),
        restTime: 90 + Math.random() * 60 // 90-150秒
      });
    }
    
    exercises.push({
      name: template.name,
      sets,
      formScore: 60 + Math.random() * 35 // 60-95のスコア
    });
  });

  return {
    id: `session_${userId}_${date.getTime()}`,
    userId,
    date: date.toISOString(),
    exercises,
    duration: 45 + Math.random() * 30, // 45-75分
    notes: Math.random() > 0.7 ? generateRandomNote() : undefined
  };
}

function generateRandomNote(): string {
  const notes = [
    '調子が良かった',
    '少し疲れ気味',
    'フォームを意識した',
    '新記録達成！',
    '次回は重量を上げる',
    '関節に違和感あり'
  ];
  return notes[Math.floor(Math.random() * notes.length)];
}

// 栄養データ生成
export interface MockMealData {
  id: string;
  userId: string;
  date: string;
  meals: Array<{
    type: 'breakfast' | 'lunch' | 'dinner' | 'snack';
    foods: Array<{
      name: string;
      calories: number;
      protein: number;
      carbs: number;
      fat: number;
    }>;
    totalCalories: number;
  }>;
  dailyTotal: {
    calories: number;
    protein: number;
    carbs: number;
    fat: number;
  };
}

export function generateNutritionHistory(userId: string, days: number = 30): MockMealData[] {
  const user = mockUsers.find(u => u.id === userId);
  if (!user) return [];

  const meals: MockMealData[] = [];
  const now = new Date();

  // ユーザーの目標に応じた栄養目標
  const nutritionTargets = {
    beginner: { calories: 2400, protein: 120, carbs: 300, fat: 80 },
    intermediate: { calories: 2200, protein: 140, carbs: 250, fat: 70 },
    advanced: { calories: 2800, protein: 180, carbs: 350, fat: 90 },
    senior: { calories: 2000, protein: 100, carbs: 250, fat: 65 }
  };

  const target = nutritionTargets[user.profile.experience];

  for (let i = 0; i < days; i++) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);
    
    const dailyMeals = generateDailyMeals(target);
    
    meals.push({
      id: `meal_${userId}_${date.getTime()}`,
      userId,
      date: date.toISOString(),
      meals: dailyMeals,
      dailyTotal: calculateDailyTotal(dailyMeals)
    });
  }

  return meals.reverse();
}

function generateDailyMeals(target: any) {
  // 実際の食事パターンを模倣
  const breakfastOptions = [
    { name: 'オートミール', calories: 300, protein: 10, carbs: 50, fat: 6 },
    { name: '卵かけご飯', calories: 350, protein: 15, carbs: 45, fat: 8 },
    { name: 'プロテインスムージー', calories: 280, protein: 25, carbs: 30, fat: 5 }
  ];

  const lunchOptions = [
    { name: '鶏胸肉弁当', calories: 550, protein: 40, carbs: 60, fat: 12 },
    { name: 'サーモン定食', calories: 600, protein: 35, carbs: 65, fat: 18 },
    { name: '牛丼', calories: 650, protein: 25, carbs: 80, fat: 20 }
  ];

  const dinnerOptions = [
    { name: 'ステーキセット', calories: 700, protein: 50, carbs: 50, fat: 25 },
    { name: '刺身定食', calories: 500, protein: 40, carbs: 45, fat: 10 },
    { name: 'パスタ', calories: 600, protein: 20, carbs: 85, fat: 15 }
  ];

  return [
    {
      type: 'breakfast' as const,
      foods: [breakfastOptions[Math.floor(Math.random() * breakfastOptions.length)]],
      totalCalories: 0
    },
    {
      type: 'lunch' as const,
      foods: [lunchOptions[Math.floor(Math.random() * lunchOptions.length)]],
      totalCalories: 0
    },
    {
      type: 'dinner' as const,
      foods: [dinnerOptions[Math.floor(Math.random() * dinnerOptions.length)]],
      totalCalories: 0
    }
  ].map(meal => ({
    ...meal,
    totalCalories: meal.foods.reduce((sum, food) => sum + food.calories, 0)
  }));
}

function calculateDailyTotal(meals: any[]) {
  return meals.reduce((total, meal) => {
    meal.foods.forEach((food: any) => {
      total.calories += food.calories;
      total.protein += food.protein;
      total.carbs += food.carbs;
      total.fat += food.fat;
    });
    return total;
  }, { calories: 0, protein: 0, carbs: 0, fat: 0 });
}