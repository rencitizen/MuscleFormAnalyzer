/**
 * 代謝エンジン - 基礎代謝・総消費カロリー・目標カロリーの計算
 */

export interface MetabolismResult {
  bmr: number;                    // 基礎代謝率
  tdee: number;                   // 総日常エネルギー消費量
  targetCalories: number;         // 目標カロリー
  calorieDeficit?: number;        // カロリー不足（カッティング時）
  calorieSurplus?: number;        // カロリー余剰（バルキング時）
  weeklyWeightChange: number;     // 週間体重変化予測
  proteinRequirement: number;     // 必要タンパク質量
  activityFactor: number;         // 活動係数
}

export type ActivityLevel = 'sedentary' | 'light' | 'moderate' | 'active' | 'veryActive';
export type Goal = 'cutting' | 'maintenance' | 'bulking';

export class MetabolismEngine {
  /**
   * 基礎代謝率（BMR）を計算
   * Mifflin-St Jeor方程式を使用
   */
  private calculateBMR(
    weight: number,
    height: number,
    age: number,
    gender: 'male' | 'female'
  ): number {
    if (gender === 'male') {
      return 10 * weight + 6.25 * height - 5 * age + 5;
    } else {
      return 10 * weight + 6.25 * height - 5 * age - 161;
    }
  }

  /**
   * 活動レベルに基づく係数を取得
   */
  private getActivityFactor(activityLevel: ActivityLevel): number {
    const factors = {
      sedentary: 1.2,      // デスクワーク中心、運動なし
      light: 1.375,        // 週1-3回の軽い運動
      moderate: 1.55,      // 週3-5回の中程度の運動
      active: 1.725,       // 週6-7回の激しい運動
      veryActive: 1.9      // 1日2回のトレーニング、肉体労働
    };
    return factors[activityLevel];
  }

  /**
   * 目標に基づくカロリー調整を計算
   */
  private calculateTargetAdjustment(
    tdee: number,
    goal: Goal,
    weight: number
  ): {
    targetCalories: number;
    deficit?: number;
    surplus?: number;
    weeklyChange: number;
  } {
    switch (goal) {
      case 'cutting':
        // 週0.5-1%の体重減少を目標（月2-4%）
        const deficitPercent = 0.20; // 20%のカロリー不足
        const deficit = Math.min(tdee * deficitPercent, 750); // 最大750kcal/日の不足
        return {
          targetCalories: tdee - deficit,
          deficit,
          weeklyChange: -(deficit * 7 / 7700) // 1kg脂肪 = 7700kcal
        };

      case 'bulking':
        // 週0.25-0.5%の体重増加を目標
        const surplusPercent = 0.10; // 10%のカロリー余剰
        const surplus = Math.min(tdee * surplusPercent, 500); // 最大500kcal/日の余剰
        return {
          targetCalories: tdee + surplus,
          surplus,
          weeklyChange: (surplus * 7 / 7700)
        };

      case 'maintenance':
      default:
        return {
          targetCalories: tdee,
          weeklyChange: 0
        };
    }
  }

  /**
   * タンパク質必要量を計算
   */
  private calculateProteinRequirement(
    weight: number,
    goal: Goal,
    activityLevel: ActivityLevel
  ): number {
    let proteinPerKg: number;

    switch (goal) {
      case 'cutting':
        // カッティング時は筋肉維持のため高めに設定
        proteinPerKg = 2.2;
        break;
      case 'bulking':
        // バルキング時は筋肉成長のため中程度
        proteinPerKg = 1.8;
        break;
      case 'maintenance':
      default:
        // 維持期は標準的な量
        proteinPerKg = 1.6;
        break;
    }

    // 活動レベルが高い場合は追加
    if (activityLevel === 'active' || activityLevel === 'veryActive') {
      proteinPerKg += 0.2;
    }

    return Math.round(weight * proteinPerKg);
  }

  /**
   * 代謝を包括的に分析
   */
  public analyzeMetabolism(
    weight: number,
    height: number,
    age: number,
    gender: 'male' | 'female',
    activityLevel: ActivityLevel,
    goal: Goal
  ): MetabolismResult {
    // 基礎代謝率を計算
    const bmr = this.calculateBMR(weight, height, age, gender);

    // 活動係数を取得
    const activityFactor = this.getActivityFactor(activityLevel);

    // 総日常エネルギー消費量を計算
    const tdee = Math.round(bmr * activityFactor);

    // 目標に基づくカロリー調整
    const adjustment = this.calculateTargetAdjustment(tdee, goal, weight);

    // タンパク質必要量を計算
    const proteinRequirement = this.calculateProteinRequirement(weight, goal, activityLevel);

    return {
      bmr: Math.round(bmr),
      tdee,
      targetCalories: Math.round(adjustment.targetCalories),
      calorieDeficit: adjustment.deficit,
      calorieSurplus: adjustment.surplus,
      weeklyWeightChange: adjustment.weeklyChange,
      proteinRequirement,
      activityFactor
    };
  }

  /**
   * 代謝適応を考慮した調整
   * 長期間のダイエット/増量で代謝が適応した場合の調整
   */
  public adjustForMetabolicAdaptation(
    currentResult: MetabolismResult,
    weeksDieting: number,
    actualWeightChange: number,
    expectedWeightChange: number
  ): MetabolismResult {
    // 実際の変化と予測の差から代謝適応を推定
    const adaptationFactor = actualWeightChange / expectedWeightChange;
    
    // 適応が大きい場合（実際の変化が予測の80%未満）
    if (adaptationFactor < 0.8) {
      // TDEEを下方修正
      const adjustedTdee = currentResult.tdee * 0.95;
      
      // 新しい目標カロリーを再計算
      const adjustedTarget = currentResult.calorieDeficit 
        ? adjustedTdee - currentResult.calorieDeficit
        : adjustedTdee + (currentResult.calorieSurplus || 0);

      return {
        ...currentResult,
        tdee: Math.round(adjustedTdee),
        targetCalories: Math.round(adjustedTarget)
      };
    }

    return currentResult;
  }

  /**
   * リフィード日のカロリーを計算
   * 長期間のカッティング時に代謝を回復させるため
   */
  public calculateRefeedCalories(
    normalTarget: number,
    tdee: number
  ): number {
    // リフィード日はTDEEの90-100%に設定
    return Math.round(tdee * 0.95);
  }
}