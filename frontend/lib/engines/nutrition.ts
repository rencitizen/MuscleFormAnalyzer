/**
 * 栄養エンジン - マクロ栄養素計算と食事プラン作成
 */

export interface MacroNutrients {
  protein: number;      // タンパク質 (g)
  carbs: number;        // 炭水化物 (g)
  fats: number;         // 脂質 (g)
  calories: number;     // 総カロリー
}

export interface MealDistribution {
  breakfast: MacroNutrients;
  lunch: MacroNutrients;
  dinner: MacroNutrients;
  snack?: MacroNutrients;
  postWorkout?: MacroNutrients;
}

export interface NutritionPlan {
  dailyMacros: MacroNutrients;
  mealDistribution: MealDistribution;
  proteinPerKg: number;
  carbsPerKg: number;
  fatsPerKg: number;
  fiberTarget: number;
  waterIntake: number;
  recommendations: string[];
  achievability: {
    score: number;
    feedback: string;
  };
}

export type Goal = 'cutting' | 'maintenance' | 'bulking';
export type ActivityType = 'sedentary' | 'active' | 'athlete';
export type MealFrequency = '3meals' | '4meals' | '5meals' | '6meals';

export class NutritionEngine {
  /**
   * マクロ栄養素の比率を目標に応じて決定
   */
  private getMacroRatios(goal: Goal): { protein: number; carbs: number; fats: number } {
    switch (goal) {
      case 'cutting':
        return { protein: 0.35, carbs: 0.35, fats: 0.30 }; // 高タンパク、中炭水化物、中脂質
      case 'bulking':
        return { protein: 0.25, carbs: 0.50, fats: 0.25 }; // 中タンパク、高炭水化物、中脂質
      case 'maintenance':
      default:
        return { protein: 0.30, carbs: 0.40, fats: 0.30 }; // バランス型
    }
  }

  /**
   * 体重あたりの栄養素量を計算
   */
  private calculatePerKgRequirements(
    weight: number,
    goal: Goal,
    activityType: ActivityType
  ): { protein: number; carbs: number; fats: number } {
    let protein: number, carbs: number, fats: number;

    switch (goal) {
      case 'cutting':
        protein = activityType === 'athlete' ? 2.5 : activityType === 'active' ? 2.2 : 2.0;
        carbs = activityType === 'athlete' ? 3.0 : activityType === 'active' ? 2.5 : 2.0;
        fats = 0.8;
        break;

      case 'bulking':
        protein = activityType === 'athlete' ? 2.2 : activityType === 'active' ? 2.0 : 1.8;
        carbs = activityType === 'athlete' ? 5.0 : activityType === 'active' ? 4.0 : 3.5;
        fats = 1.2;
        break;

      case 'maintenance':
      default:
        protein = activityType === 'athlete' ? 2.0 : activityType === 'active' ? 1.8 : 1.6;
        carbs = activityType === 'athlete' ? 4.0 : activityType === 'active' ? 3.0 : 2.5;
        fats = 1.0;
        break;
    }

    return { protein, carbs, fats };
  }

  /**
   * カロリーからマクロ栄養素を計算
   */
  private calculateMacrosFromCalories(
    targetCalories: number,
    weight: number,
    goal: Goal,
    activityType: ActivityType
  ): MacroNutrients {
    const ratios = this.getMacroRatios(goal);
    const perKg = this.calculatePerKgRequirements(weight, goal, activityType);

    // 最初に体重ベースで計算
    let protein = Math.round(weight * perKg.protein);
    let proteinCalories = protein * 4;

    // 残りのカロリーを炭水化物と脂質に配分
    const remainingCalories = targetCalories - proteinCalories;
    const carbsCalories = remainingCalories * (ratios.carbs / (ratios.carbs + ratios.fats));
    const fatsCalories = remainingCalories * (ratios.fats / (ratios.carbs + ratios.fats));

    const carbs = Math.round(carbsCalories / 4);
    const fats = Math.round(fatsCalories / 9);

    // 実際のカロリーを再計算
    const actualCalories = (protein * 4) + (carbs * 4) + (fats * 9);

    return {
      protein,
      carbs,
      fats,
      calories: Math.round(actualCalories)
    };
  }

  /**
   * 食事配分を計算
   */
  private distributeMeals(
    dailyMacros: MacroNutrients,
    mealFrequency: MealFrequency,
    hasWorkout: boolean = true
  ): MealDistribution {
    const distribution: MealDistribution = {
      breakfast: { protein: 0, carbs: 0, fats: 0, calories: 0 },
      lunch: { protein: 0, carbs: 0, fats: 0, calories: 0 },
      dinner: { protein: 0, carbs: 0, fats: 0, calories: 0 }
    };

    // 食事頻度に応じた配分
    let mealRatios: { [key: string]: number } = {};

    switch (mealFrequency) {
      case '3meals':
        mealRatios = { breakfast: 0.30, lunch: 0.35, dinner: 0.35 };
        break;
      case '4meals':
        mealRatios = { breakfast: 0.25, lunch: 0.30, dinner: 0.30, snack: 0.15 };
        distribution.snack = { protein: 0, carbs: 0, fats: 0, calories: 0 };
        break;
      case '5meals':
        mealRatios = { breakfast: 0.20, lunch: 0.25, dinner: 0.25, snack: 0.15, postWorkout: 0.15 };
        distribution.snack = { protein: 0, carbs: 0, fats: 0, calories: 0 };
        distribution.postWorkout = { protein: 0, carbs: 0, fats: 0, calories: 0 };
        break;
      case '6meals':
        mealRatios = { breakfast: 0.17, lunch: 0.20, dinner: 0.20, snack: 0.13, postWorkout: 0.15 };
        distribution.snack = { protein: 0, carbs: 0, fats: 0, calories: 0 };
        distribution.postWorkout = { protein: 0, carbs: 0, fats: 0, calories: 0 };
        break;
    }

    // 各食事にマクロを配分
    Object.keys(mealRatios).forEach(meal => {
      const ratio = mealRatios[meal];
      const mealMacros = {
        protein: Math.round(dailyMacros.protein * ratio),
        carbs: Math.round(dailyMacros.carbs * ratio),
        fats: Math.round(dailyMacros.fats * ratio),
        calories: 0
      };
      mealMacros.calories = (mealMacros.protein * 4) + (mealMacros.carbs * 4) + (mealMacros.fats * 9);
      
      if (meal in distribution) {
        (distribution as any)[meal] = mealMacros;
      }
    });

    // ワークアウト後の栄養調整
    if (hasWorkout && distribution.postWorkout) {
      // ワークアウト後は高タンパク・高炭水化物・低脂質
      const postWorkoutProtein = Math.round(dailyMacros.protein * 0.25);
      const postWorkoutCarbs = Math.round(dailyMacros.carbs * 0.30);
      const postWorkoutFats = Math.round(dailyMacros.fats * 0.05);
      
      distribution.postWorkout = {
        protein: postWorkoutProtein,
        carbs: postWorkoutCarbs,
        fats: postWorkoutFats,
        calories: (postWorkoutProtein * 4) + (postWorkoutCarbs * 4) + (postWorkoutFats * 9)
      };

      // 他の食事から差し引いて調整
      const remainingMeals = ['breakfast', 'lunch', 'dinner', 'snack'].filter(m => m in distribution);
      const adjustmentRatio = 1 - (distribution.postWorkout.calories / dailyMacros.calories);
      
      remainingMeals.forEach(meal => {
        const mealData = (distribution as any)[meal];
        if (mealData) {
          mealData.protein = Math.round(mealData.protein * adjustmentRatio);
          mealData.carbs = Math.round(mealData.carbs * adjustmentRatio);
          mealData.fats = Math.round(mealData.fats * adjustmentRatio);
          mealData.calories = (mealData.protein * 4) + (mealData.carbs * 4) + (mealData.fats * 9);
        }
      });
    }

    return distribution;
  }

  /**
   * 食物繊維の目標量を計算
   */
  private calculateFiberTarget(calories: number, gender: 'male' | 'female' = 'male'): number {
    // 1000kcalあたり14gの食物繊維（アメリカ心臓協会の推奨）
    const baseAmount = (calories / 1000) * 14;
    // 女性は少し少なめ、男性は多めに調整
    return Math.round(gender === 'female' ? baseAmount * 0.9 : baseAmount * 1.1);
  }

  /**
   * 水分摂取量を計算
   */
  private calculateWaterIntake(weight: number, activityType: ActivityType): number {
    // 基本: 体重1kgあたり35ml
    let baseAmount = weight * 35;
    
    // 活動レベルに応じて追加
    switch (activityType) {
      case 'athlete':
        baseAmount *= 1.5;
        break;
      case 'active':
        baseAmount *= 1.3;
        break;
      default:
        baseAmount *= 1.1;
        break;
    }

    return Math.round(baseAmount / 1000); // リットルに変換
  }

  /**
   * 栄養プランの実現可能性を評価
   */
  private assessAchievability(
    dailyMacros: MacroNutrients,
    weight: number
  ): { score: number; feedback: string } {
    const proteinPerKg = dailyMacros.protein / weight;
    const carbsPerKg = dailyMacros.carbs / weight;
    const fatsPerKg = dailyMacros.fats / weight;

    let score = 100;
    const issues: string[] = [];

    // タンパク質チェック
    if (proteinPerKg > 3.0) {
      score -= 20;
      issues.push('タンパク質量が非常に多い');
    } else if (proteinPerKg < 1.2) {
      score -= 15;
      issues.push('タンパク質量が少ない');
    }

    // 炭水化物チェック
    if (carbsPerKg < 1.5) {
      score -= 10;
      issues.push('炭水化物が少なくエネルギー不足の可能性');
    } else if (carbsPerKg > 6.0) {
      score -= 10;
      issues.push('炭水化物が過剰');
    }

    // 脂質チェック
    if (fatsPerKg < 0.5) {
      score -= 20;
      issues.push('脂質が少なすぎてホルモンバランスに影響の可能性');
    } else if (fatsPerKg > 2.0) {
      score -= 10;
      issues.push('脂質が多い');
    }

    // カロリーチェック
    if (dailyMacros.calories < 1200) {
      score -= 30;
      issues.push('総カロリーが低すぎる');
    }

    let feedback: string;
    if (score >= 90) {
      feedback = '実現可能で健康的なプランです';
    } else if (score >= 70) {
      feedback = `注意点があります: ${issues.join('、')}`;
    } else {
      feedback = `見直しが必要です: ${issues.join('、')}`;
    }

    return { score, feedback };
  }

  /**
   * 推奨事項を生成
   */
  private generateRecommendations(
    goal: Goal,
    dailyMacros: MacroNutrients,
    weight: number
  ): string[] {
    const recommendations: string[] = [];

    // 目標別の基本推奨
    switch (goal) {
      case 'cutting':
        recommendations.push('高タンパク食品を各食事に含めましょう');
        recommendations.push('食物繊維豊富な野菜を積極的に摂取しましょう');
        recommendations.push('空腹感対策として、食事の回数を増やすことを検討してください');
        break;
      case 'bulking':
        recommendations.push('トレーニング前後の栄養摂取を重視しましょう');
        recommendations.push('消化の良い炭水化物源を選びましょう');
        recommendations.push('良質な脂質（オメガ3脂肪酸）を摂取しましょう');
        break;
      case 'maintenance':
        recommendations.push('栄養バランスを意識した食事を心がけましょう');
        recommendations.push('加工食品を避け、自然食品を選びましょう');
        break;
    }

    // タンパク質源の推奨
    const proteinPerKg = dailyMacros.protein / weight;
    if (proteinPerKg > 2.0) {
      recommendations.push('鶏胸肉、魚、卵白、プロテインパウダーなど多様なタンパク質源を活用しましょう');
    }

    // 水分摂取の推奨
    recommendations.push('こまめな水分補給を心がけましょう');

    // サプリメントの推奨
    if (goal === 'cutting' || goal === 'bulking') {
      recommendations.push('必要に応じてマルチビタミンの摂取を検討してください');
    }

    return recommendations;
  }

  /**
   * 栄養プランを作成
   */
  public createNutritionPlan(
    targetCalories: number,
    weight: number,
    goal: Goal,
    activityType: ActivityType,
    mealFrequency: MealFrequency = '4meals'
  ): NutritionPlan {
    // 日々のマクロ栄養素を計算
    const dailyMacros = this.calculateMacrosFromCalories(
      targetCalories,
      weight,
      goal,
      activityType
    );

    // 食事配分を計算
    const mealDistribution = this.distributeMeals(
      dailyMacros,
      mealFrequency,
      activityType !== 'sedentary'
    );

    // 体重あたりの栄養素量
    const proteinPerKg = Number((dailyMacros.protein / weight).toFixed(2));
    const carbsPerKg = Number((dailyMacros.carbs / weight).toFixed(2));
    const fatsPerKg = Number((dailyMacros.fats / weight).toFixed(2));

    // その他の栄養目標
    const fiberTarget = this.calculateFiberTarget(targetCalories);
    const waterIntake = this.calculateWaterIntake(weight, activityType);

    // 実現可能性の評価
    const achievability = this.assessAchievability(dailyMacros, weight);

    // 推奨事項の生成
    const recommendations = this.generateRecommendations(goal, dailyMacros, weight);

    return {
      dailyMacros,
      mealDistribution,
      proteinPerKg,
      carbsPerKg,
      fatsPerKg,
      fiberTarget,
      waterIntake,
      recommendations,
      achievability
    };
  }

  /**
   * カーボサイクリングプランを作成
   * トレーニング日と休息日で炭水化物量を調整
   */
  public createCarbCyclingPlan(
    basePlan: NutritionPlan,
    isTrainingDay: boolean
  ): NutritionPlan {
    const adjustedMacros = { ...basePlan.dailyMacros };

    if (isTrainingDay) {
      // トレーニング日: 炭水化物を20%増加、脂質を減少
      adjustedMacros.carbs = Math.round(adjustedMacros.carbs * 1.2);
      adjustedMacros.fats = Math.round(adjustedMacros.fats * 0.8);
    } else {
      // 休息日: 炭水化物を20%減少、脂質を増加
      adjustedMacros.carbs = Math.round(adjustedMacros.carbs * 0.8);
      adjustedMacros.fats = Math.round(adjustedMacros.fats * 1.2);
    }

    // カロリーを再計算
    adjustedMacros.calories = (adjustedMacros.protein * 4) + 
                             (adjustedMacros.carbs * 4) + 
                             (adjustedMacros.fats * 9);

    return {
      ...basePlan,
      dailyMacros: adjustedMacros,
      recommendations: [
        ...basePlan.recommendations,
        isTrainingDay 
          ? 'トレーニング日: 炭水化物を増やしてパフォーマンスを最大化'
          : '休息日: 炭水化物を控えめにして回復を促進'
      ]
    };
  }
}