/**
 * 栄養計算エンジン
 * PFCバランス・栄養素配分・食品推奨
 */

export interface MacroNutrients {
  protein: number;  // グラム
  carbs: number;    // グラム
  fats: number;     // グラム
  calories: number; // 総カロリー
}

export interface NutritionRatios {
  protein: number;  // 比率 (0-1)
  carbs: number;    // 比率 (0-1)
  fats: number;     // 比率 (0-1)
}

export interface FoodRecommendation {
  name: string;
  protein: number;
  benefits: string;
  serving: string;
  calories: number;
}

export interface NutritionPlan {
  dailyMacros: MacroNutrients;
  mealDistribution: {
    breakfast: MacroNutrients;
    lunch: MacroNutrients;
    dinner: MacroNutrients;
    snacks: MacroNutrients;
  };
  proteinPerKg: number;
  recommendations: {
    protein: FoodRecommendation[];
    carbs: FoodRecommendation[];
    fats: FoodRecommendation[];
  };
}

export class NutritionEngine {
  /**
   * 目標別のPFC比率
   */
  getPFCRatios(goal: 'cutting' | 'maintenance' | 'bulking'): NutritionRatios {
    const ratios: Record<string, NutritionRatios> = {
      cutting: { protein: 0.35, fats: 0.25, carbs: 0.40 },      // 高タンパク低炭水化物
      maintenance: { protein: 0.25, fats: 0.25, carbs: 0.50 }, // バランス型
      bulking: { protein: 0.25, fats: 0.20, carbs: 0.55 }      // 高炭水化物
    };
    return ratios[goal];
  }

  /**
   * PFCマクロ栄養素計算
   */
  calculatePFCMacros(calories: number, goal: 'cutting' | 'maintenance' | 'bulking'): MacroNutrients {
    const ratios = this.getPFCRatios(goal);
    
    // カロリーからグラム数を計算
    // タンパク質: 4kcal/g, 炭水化物: 4kcal/g, 脂質: 9kcal/g
    const protein = Math.round((calories * ratios.protein) / 4);
    const carbs = Math.round((calories * ratios.carbs) / 4);
    const fats = Math.round((calories * ratios.fats) / 9);
    
    // 実際のカロリーを再計算（丸め誤差調整）
    const actualCalories = protein * 4 + carbs * 4 + fats * 9;

    return {
      protein,
      carbs,
      fats,
      calories: Math.round(actualCalories)
    };
  }

  /**
   * 体重あたりのタンパク質必要量計算
   */
  calculateProteinNeeds(
    weight: number,
    goal: 'cutting' | 'maintenance' | 'bulking',
    activityLevel: 'sedentary' | 'active' | 'athlete'
  ): number {
    // 体重1kgあたりのタンパク質必要量（g）
    const proteinPerKg: Record<string, Record<string, number>> = {
      cutting: { sedentary: 2.0, active: 2.3, athlete: 2.5 },
      maintenance: { sedentary: 1.6, active: 1.8, athlete: 2.0 },
      bulking: { sedentary: 1.8, active: 2.0, athlete: 2.2 }
    };
    
    return proteinPerKg[goal][activityLevel];
  }

  /**
   * 高タンパク質食品の推奨リスト
   */
  getHighProteinFoods(): Record<string, FoodRecommendation[]> {
    return {
      meat: [
        { name: '鶏胸肉（皮なし）', protein: 23, benefits: '低脂質・高タンパク・カルノシン豊富', serving: '100g', calories: 108 },
        { name: '赤身牛肉', protein: 22, benefits: 'クレアチン・亜鉛・鉄分豊富', serving: '100g', calories: 176 },
        { name: '豚ヒレ肉', protein: 22, benefits: 'ビタミンB1豊富・低脂質', serving: '100g', calories: 115 },
        { name: 'ささみ', protein: 23, benefits: '最も低脂質な肉類', serving: '100g', calories: 105 }
      ],
      fish: [
        { name: 'サーモン', protein: 20, benefits: 'オメガ3脂肪酸・ビタミンD豊富', serving: '100g', calories: 208 },
        { name: 'サバ缶（水煮）', protein: 21, benefits: '手軽・オメガ3・カルシウム', serving: '1缶(190g)', calories: 340 },
        { name: 'マグロ赤身', protein: 26, benefits: '高タンパク・低脂質・鉄分', serving: '100g', calories: 125 },
        { name: 'タラ', protein: 18, benefits: '超低脂質・消化に良い', serving: '100g', calories: 77 }
      ],
      plant: [
        { name: '納豆', protein: 17, benefits: '発酵食品・腸内環境改善・ビタミンK', serving: '100g', calories: 200 },
        { name: '豆腐（木綿）', protein: 7, benefits: '低カロリー・大豆イソフラボン', serving: '100g', calories: 73 },
        { name: '枝豆', protein: 12, benefits: '食物繊維・葉酸豊富', serving: '100g', calories: 135 },
        { name: 'ブロッコリー', protein: 4, benefits: 'ビタミンC・K・食物繊維', serving: '100g', calories: 33 }
      ],
      dairy: [
        { name: 'ギリシャヨーグルト', protein: 10, benefits: '高タンパク・プロバイオティクス', serving: '100g', calories: 90 },
        { name: 'カッテージチーズ', protein: 11, benefits: '低脂質・カゼインタンパク', serving: '100g', calories: 98 },
        { name: '低脂肪牛乳', protein: 3.4, benefits: 'カルシウム・ビタミンD強化', serving: '200ml', calories: 92 }
      ]
    };
  }

  /**
   * 良質な炭水化物源
   */
  getQualityCarbSources(): FoodRecommendation[] {
    return [
      { name: 'オートミール', protein: 13, benefits: '低GI・食物繊維・β-グルカン', serving: '100g', calories: 380 },
      { name: '玄米', protein: 3, benefits: '低GI・ビタミンB群・食物繊維', serving: '150g(炊飯後)', calories: 248 },
      { name: 'さつまいも', protein: 1, benefits: '低GI・ビタミンA・食物繊維', serving: '100g', calories: 132 },
      { name: 'キヌア', protein: 4, benefits: '完全タンパク質・ミネラル豊富', serving: '100g(炊飯後)', calories: 120 },
      { name: '全粒粉パスタ', protein: 12, benefits: '食物繊維・低GI', serving: '100g(乾燥)', calories: 348 }
    ];
  }

  /**
   * 健康的な脂質源
   */
  getHealthyFatSources(): FoodRecommendation[] {
    return [
      { name: 'アボカド', protein: 2, benefits: '一価不飽和脂肪酸・ビタミンE', serving: '1/2個(100g)', calories: 160 },
      { name: 'アーモンド', protein: 21, benefits: 'ビタミンE・マグネシウム・食物繊維', serving: '28g', calories: 164 },
      { name: 'くるみ', protein: 15, benefits: 'オメガ3脂肪酸・抗酸化物質', serving: '28g', calories: 185 },
      { name: 'オリーブオイル', protein: 0, benefits: '一価不飽和脂肪酸・抗炎症作用', serving: '大さじ1(15ml)', calories: 135 },
      { name: 'MCTオイル', protein: 0, benefits: '即エネルギー化・ケトン体生成', serving: '大さじ1(15ml)', calories: 130 }
    ];
  }

  /**
   * 食事配分の計算
   */
  calculateMealDistribution(dailyMacros: MacroNutrients, mealPattern: '3meals' | '4meals' | '5meals'): NutritionPlan['mealDistribution'] {
    const distributions = {
      '3meals': { breakfast: 0.25, lunch: 0.35, dinner: 0.30, snacks: 0.10 },
      '4meals': { breakfast: 0.25, lunch: 0.30, dinner: 0.25, snacks: 0.20 },
      '5meals': { breakfast: 0.20, lunch: 0.25, dinner: 0.25, snacks: 0.30 }
    };

    const dist = distributions[mealPattern];

    return {
      breakfast: this.applyDistribution(dailyMacros, dist.breakfast),
      lunch: this.applyDistribution(dailyMacros, dist.lunch),
      dinner: this.applyDistribution(dailyMacros, dist.dinner),
      snacks: this.applyDistribution(dailyMacros, dist.snacks)
    };
  }

  /**
   * マクロ栄養素の配分適用
   */
  private applyDistribution(macros: MacroNutrients, percentage: number): MacroNutrients {
    return {
      protein: Math.round(macros.protein * percentage),
      carbs: Math.round(macros.carbs * percentage),
      fats: Math.round(macros.fats * percentage),
      calories: Math.round(macros.calories * percentage)
    };
  }

  /**
   * 包括的な栄養プラン作成
   */
  createNutritionPlan(
    calories: number,
    weight: number,
    goal: 'cutting' | 'maintenance' | 'bulking',
    activityLevel: 'sedentary' | 'active' | 'athlete',
    mealPattern: '3meals' | '4meals' | '5meals' = '4meals'
  ): NutritionPlan {
    const dailyMacros = this.calculatePFCMacros(calories, goal);
    const proteinPerKg = this.calculateProteinNeeds(weight, goal, activityLevel);
    const mealDistribution = this.calculateMealDistribution(dailyMacros, mealPattern);

    return {
      dailyMacros,
      mealDistribution,
      proteinPerKg,
      recommendations: {
        protein: this.getHighProteinFoods().meat.concat(this.getHighProteinFoods().fish),
        carbs: this.getQualityCarbSources(),
        fats: this.getHealthyFatSources()
      }
    };
  }
}

export default NutritionEngine;