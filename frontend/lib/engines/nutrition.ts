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
  achievability?: {
    score: number;
    level: string;
    challenges: string[];
  };
}

export class NutritionEngine {
  /**
   * 目標別のPFC比率
   * より現実的で継続可能なバランスに調整
   */
  getPFCRatios(goal: 'cutting' | 'maintenance' | 'bulking'): NutritionRatios {
    const ratios: Record<string, NutritionRatios> = {
      cutting: { protein: 0.30, fats: 0.25, carbs: 0.45 },      // 理論値P35% → P30%（継続しやすい）
      maintenance: { protein: 0.25, fats: 0.25, carbs: 0.50 },  // バランス型（変更なし）
      bulking: { protein: 0.20, fats: 0.25, carbs: 0.55 }       // 理論値P25% → P20%（炭水化物重視）
    };
    return ratios[goal];
  }

  /**
   * PFCマクロ栄養素計算
   * 体重に基づく現実的な上限を設定
   */
  calculatePFCMacros(calories: number, goal: 'cutting' | 'maintenance' | 'bulking', weight?: number): MacroNutrients {
    const ratios = this.getPFCRatios(goal);
    
    // カロリーからグラム数を計算
    // タンパク質: 4kcal/g, 炭水化物: 4kcal/g, 脂質: 9kcal/g
    let protein = Math.round((calories * ratios.protein) / 4);
    
    // 体重が提供されている場合、現実的な上限を適用
    if (weight) {
      const maxProtein = Math.round(weight * 2.0); // 体重×2gが現実的な上限
      protein = Math.min(protein, maxProtein);
    }
    
    // プロテインが制限された場合、残りのカロリーを炭水化物と脂質に再配分
    const proteinCalories = protein * 4;
    const remainingCalories = calories - proteinCalories;
    const remainingRatio = ratios.carbs + ratios.fats;
    
    const carbs = Math.round((remainingCalories * (ratios.carbs / remainingRatio)) / 4);
    const fats = Math.round((remainingCalories * (ratios.fats / remainingRatio)) / 9);
    
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
   * 現実的に摂取・継続可能な範囲に調整（1.2-2.0g/kg）
   */
  calculateProteinNeeds(
    weight: number,
    goal: 'cutting' | 'maintenance' | 'bulking',
    activityLevel: 'sedentary' | 'active' | 'athlete'
  ): number {
    // 体重1kgあたりのタンパク質必要量（g）
    // 理論値から現実的な値に調整
    const proteinPerKg: Record<string, Record<string, number>> = {
      cutting: { sedentary: 1.6, active: 1.8, athlete: 2.0 },      // 理論値2.0-2.5 → 1.6-2.0
      maintenance: { sedentary: 1.2, active: 1.4, athlete: 1.6 },  // 理論値1.6-2.0 → 1.2-1.6
      bulking: { sedentary: 1.4, active: 1.6, athlete: 1.8 }      // 理論値1.8-2.2 → 1.4-1.8
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
   * 栄養目標の達成可能性評価
   */
  assessAchievability(macros: MacroNutrients, weight: number): NutritionPlan['achievability'] {
    const proteinPerKg = macros.protein / weight;
    let score = 100;
    const challenges: string[] = [];

    // プロテイン評価
    if (proteinPerKg > 2.2) {
      score -= 30;
      challenges.push('プロテイン摂取量が多すぎます（体重×2.2g以上）');
    } else if (proteinPerKg > 1.8) {
      score -= 15;
      challenges.push('プロテイン摂取に相当な努力が必要です');
    }

    // 脂質評価
    if (macros.fats < 40) {
      score -= 20;
      challenges.push('脂質が少なすぎて満足感を得にくい可能性');
    } else if (macros.fats > 100) {
      score -= 10;
      challenges.push('脂質が多めですが、良質な脂質を選びましょう');
    }

    // 炭水化物評価
    if (macros.carbs < 100) {
      score -= 25;
      challenges.push('炭水化物が少なすぎて活力不足の恐れ');
    } else if (macros.carbs > 350) {
      score -= 15;
      challenges.push('炭水化物が多く、消化に負担がかかる可能性');
    }

    // カロリー評価
    if (macros.calories < 1200) {
      score -= 30;
      challenges.push('カロリーが低すぎて健康リスクがあります');
    } else if (macros.calories > 3500) {
      score -= 20;
      challenges.push('カロリーが多く、実際に摂取するのが困難');
    }

    // レベル判定
    let level: string;
    if (score >= 80) {
      level = '達成しやすい';
    } else if (score >= 60) {
      level = '努力次第で達成可能';
    } else if (score >= 40) {
      level = '達成困難';
    } else {
      level = '非現実的';
    }

    // 最低スコアを30に設定
    score = Math.max(score, 30);

    return {
      score,
      level,
      challenges
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
    const dailyMacros = this.calculatePFCMacros(calories, goal, weight);
    const proteinPerKg = this.calculateProteinNeeds(weight, goal, activityLevel);
    const mealDistribution = this.calculateMealDistribution(dailyMacros, mealPattern);

    const achievability = this.assessAchievability(dailyMacros, weight);

    return {
      dailyMacros,
      mealDistribution,
      proteinPerKg,
      recommendations: {
        protein: this.getHighProteinFoods().meat.concat(this.getHighProteinFoods().fish),
        carbs: this.getQualityCarbSources(),
        fats: this.getHealthyFatSources()
      },
      achievability
    };
  }
}

export default NutritionEngine;