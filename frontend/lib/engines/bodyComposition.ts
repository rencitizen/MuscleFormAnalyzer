/**
 * 身体組成分析エンジン
 * 科学的根拠に基づいた体組成計算
 */

export interface BodyCompositionData {
  bmi: number;
  bodyFatPercentage: number;
  leanBodyMass: number;
  ffmi: number; // Fat-Free Mass Index
  category: string;
  healthRisk: 'none' | 'low' | 'medium' | 'high';
}

export interface VisualBodyFatRange {
  min: number;
  max: number;
  risk: 'none' | 'low' | 'medium' | 'high';
  description: string;
}

export class BodyCompositionEngine {
  /**
   * BMI計算
   */
  calculateBMI(weight: number, height: number): number {
    return weight / Math.pow(height / 100, 2);
  }

  /**
   * 体脂肪率推定（田中式）
   * より正確な日本人向け推定式
   */
  estimateBodyFatTanita(
    weight: number,
    height: number,
    age: number,
    gender: 'male' | 'female'
  ): number {
    const bmi = this.calculateBMI(weight, height);
    const genderValue = gender === 'male' ? 1 : 0;
    
    // 田中式体脂肪率推定
    const bodyFat = 1.2 * bmi + 0.23 * age - 10.8 * genderValue - 5.4;
    
    // 範囲制限（現実的な値に）
    return Math.max(3, Math.min(60, bodyFat));
  }

  /**
   * 除脂肪体重（LBM）計算
   */
  calculateLeanBodyMass(weight: number, bodyFatPercentage: number): number {
    return weight * (1 - bodyFatPercentage / 100);
  }

  /**
   * FFMI（除脂肪量指数）計算
   * 筋肉量の指標
   */
  calculateFFMI(leanBodyMass: number, height: number): number {
    return leanBodyMass / Math.pow(height / 100, 2);
  }

  /**
   * 視覚的体型から体脂肪率範囲をマッピング
   */
  mapVisualToBodyFat(
    visualSelection: string,
    gender: 'male' | 'female'
  ): VisualBodyFatRange {
    const ranges = {
      female: {
        athlete: { min: 15, max: 20, risk: 'high', description: 'アスリート体型' },
        fitness: { min: 16, max: 20, risk: 'low', description: 'フィットネス体型' },
        healthy: { min: 21, max: 25, risk: 'none', description: '健康的' },
        curvy: { min: 26, max: 30, risk: 'low', description: 'ふくよか' },
        overweight: { min: 31, max: 35, risk: 'medium', description: '肥満気味' },
        obese: { min: 36, max: 100, risk: 'high', description: '肥満' }
      },
      male: {
        athlete: { min: 6, max: 12, risk: 'medium', description: 'アスリート体型' },
        fitness: { min: 10, max: 15, risk: 'none', description: 'フィットネス体型' },
        healthy: { min: 16, max: 20, risk: 'none', description: '健康的' },
        average: { min: 21, max: 25, risk: 'low', description: '平均的' },
        overweight: { min: 26, max: 30, risk: 'medium', description: '肥満気味' },
        obese: { min: 31, max: 100, risk: 'high', description: '肥満' }
      }
    };

    return ranges[gender][visualSelection] || ranges[gender].healthy;
  }

  /**
   * BMIカテゴリー判定（日本肥満学会基準）
   */
  getBMICategory(bmi: number): string {
    if (bmi < 18.5) return '低体重';
    if (bmi < 25) return '普通体重';
    if (bmi < 30) return '肥満（1度）';
    if (bmi < 35) return '肥満（2度）';
    if (bmi < 40) return '肥満（3度）';
    return '肥満（4度）';
  }

  /**
   * 健康リスク評価
   */
  assessHealthRisk(
    bmi: number,
    bodyFatPercentage: number,
    gender: 'male' | 'female'
  ): 'none' | 'low' | 'medium' | 'high' {
    const minBodyFat = gender === 'male' ? 8 : 15;
    const maxHealthyBodyFat = gender === 'male' ? 25 : 32;

    if (bodyFatPercentage < minBodyFat || bodyFatPercentage > 40) {
      return 'high';
    }
    if (bmi < 18.5 || bmi > 30 || bodyFatPercentage > maxHealthyBodyFat) {
      return 'medium';
    }
    if (bmi > 25 || bodyFatPercentage > (gender === 'male' ? 20 : 28)) {
      return 'low';
    }
    return 'none';
  }

  /**
   * 包括的な身体組成分析
   */
  analyzeBodyComposition(
    weight: number,
    height: number,
    age: number,
    gender: 'male' | 'female'
  ): BodyCompositionData {
    const bmi = this.calculateBMI(weight, height);
    const bodyFatPercentage = this.estimateBodyFatTanita(weight, height, age, gender);
    const leanBodyMass = this.calculateLeanBodyMass(weight, bodyFatPercentage);
    const ffmi = this.calculateFFMI(leanBodyMass, height);
    const category = this.getBMICategory(bmi);
    const healthRisk = this.assessHealthRisk(bmi, bodyFatPercentage, gender);

    return {
      bmi: Math.round(bmi * 10) / 10,
      bodyFatPercentage: Math.round(bodyFatPercentage * 10) / 10,
      leanBodyMass: Math.round(leanBodyMass * 10) / 10,
      ffmi: Math.round(ffmi * 10) / 10,
      category,
      healthRisk
    };
  }
}

export default BodyCompositionEngine;