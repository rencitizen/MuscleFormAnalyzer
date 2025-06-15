/**
 * 代謝計算エンジン
 * 基礎代謝・活動代謝・目標カロリー計算
 */

export interface MetabolismData {
  bmr: number;
  tdee: number;
  targetCalories: number;
  calorieDeficit?: number;
  calorieSurplus?: number;
  weeklyWeightChange: number;
}

export type ActivityLevel = 'sedentary' | 'light' | 'moderate' | 'active' | 'veryActive';
export type Goal = 'cutting' | 'maintenance' | 'bulking';

export class MetabolismEngine {
  /**
   * Mifflin-St Jeor式による基礎代謝率（BMR）計算
   * 最も正確とされる推定式
   */
  calculateBMRMifflin(
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
   * Harris-Benedict式（改訂版）によるBMR計算
   * 比較用の代替計算式
   */
  calculateBMRHarrisBenedict(
    weight: number,
    height: number,
    age: number,
    gender: 'male' | 'female'
  ): number {
    if (gender === 'male') {
      return 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age);
    } else {
      return 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age);
    }
  }

  /**
   * 活動レベル係数の取得
   * より現実的な係数に調整（理論値よりも控えめに設定）
   */
  getActivityMultiplier(activityLevel: ActivityLevel): number {
    const multipliers: Record<ActivityLevel, number> = {
      sedentary: 1.15,     // 座りがち（運動なし）理論値1.2→1.15
      light: 1.25,         // 軽い活動（週1-3日の運動）理論値1.375→1.25
      moderate: 1.35,      // 中程度（週3-5日の運動）理論値1.55→1.35
      active: 1.45,        // 活発（週6-7日の運動）理論値1.725→1.45
      veryActive: 1.6      // 非常に活発（激しい運動/肉体労働）理論値1.9→1.6
    };
    return multipliers[activityLevel];
  }

  /**
   * 総消費カロリー（TDEE）計算
   */
  calculateTDEE(bmr: number, activityLevel: ActivityLevel): number {
    const multiplier = this.getActivityMultiplier(activityLevel);
    return bmr * multiplier;
  }

  /**
   * 目標に応じたカロリー調整
   * TDEEに対する割合ベースで計算（固定値より現実的）
   */
  getGoalAdjustment(goal: Goal, tdee: number): number {
    const adjustmentRates: Record<Goal, number> = {
      cutting: -0.15,      // 減量: TDEEの15%減（最大-400kcal）
      maintenance: 0,      // 維持
      bulking: 0.12        // 増量: TDEEの12%増（最大+300kcal）
    };
    
    const adjustment = tdee * adjustmentRates[goal];
    
    // 極端な調整を防ぐため上限を設定
    if (goal === 'cutting') {
      return Math.max(adjustment, -400); // 最大-400kcal
    } else if (goal === 'bulking') {
      return Math.min(adjustment, 300);   // 最大+300kcal
    }
    
    return adjustment;
  }

  /**
   * 目標カロリー計算
   */
  calculateCalorieGoals(tdee: number, goal: Goal): number {
    const adjustment = this.getGoalAdjustment(goal, tdee);
    return tdee + adjustment;
  }

  /**
   * 週間体重変化予測
   */
  calculateWeeklyWeightChange(calorieDeficitOrSurplus: number): number {
    // 7700kcal = 1kg の脂肪
    return (calorieDeficitOrSurplus * 7) / 7700;
  }

  /**
   * 安全なカロリー範囲の確認
   */
  isSafeCalorieTarget(bmr: number, targetCalories: number, gender: 'male' | 'female'): boolean {
    // 基礎代謝の最低倍率
    const minMultiplier = gender === 'male' ? 1.2 : 1.1;
    return targetCalories >= bmr * minMultiplier;
  }

  /**
   * 減量ペースの推奨値取得
   */
  getRecommendedWeightLossRate(currentWeight: number): {
    min: number;
    max: number;
    recommended: number;
  } {
    // 体重の0.5-1%/週が推奨
    return {
      min: currentWeight * 0.005,
      max: currentWeight * 0.01,
      recommended: currentWeight * 0.0075
    };
  }

  /**
   * 包括的な代謝分析
   */
  analyzeMetabolism(
    weight: number,
    height: number,
    age: number,
    gender: 'male' | 'female',
    activityLevel: ActivityLevel,
    goal: Goal
  ): MetabolismData {
    const bmr = this.calculateBMRMifflin(weight, height, age, gender);
    const tdee = this.calculateTDEE(bmr, activityLevel);
    const targetCalories = this.calculateCalorieGoals(tdee, goal);
    
    const calorieAdjustment = targetCalories - tdee;
    const weeklyWeightChange = this.calculateWeeklyWeightChange(calorieAdjustment);

    return {
      bmr: Math.round(bmr),
      tdee: Math.round(tdee),
      targetCalories: Math.round(targetCalories),
      calorieDeficit: goal === 'cutting' ? Math.abs(calorieAdjustment) : undefined,
      calorieSurplus: goal === 'bulking' ? calorieAdjustment : undefined,
      weeklyWeightChange: Math.round(weeklyWeightChange * 1000) / 1000
    };
  }

  /**
   * 活動レベルの説明文取得
   */
  getActivityLevelDescription(level: ActivityLevel): string {
    const descriptions: Record<ActivityLevel, string> = {
      sedentary: '座りがち（デスクワーク中心、運動なし）',
      light: '軽い活動（週1-3日の軽い運動）',
      moderate: '中程度の活動（週3-5日の運動）',
      active: '活発な活動（週6-7日の運動）',
      veryActive: '非常に活発（激しい運動や肉体労働）'
    };
    return descriptions[level];
  }
}

export default MetabolismEngine;