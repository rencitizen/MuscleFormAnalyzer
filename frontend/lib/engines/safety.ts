/**
 * 安全性チェックエンジン
 * 健康リスク評価と警告システム
 */

export interface SafetyWarning {
  level: 'info' | 'warning' | 'critical' | 'danger';
  category: string;
  message: string;
  risks: string[];
  recommendations: string[];
}

export interface SafetyAnalysis {
  overallSafety: 'safe' | 'caution' | 'unsafe';
  score: number; // 0-100
  warnings: SafetyWarning[];
  recommendations: string[];
  requiredActions: string[];
}

export class SafetyEngine {
  /**
   * カロリー摂取の安全性チェック
   */
  checkCalorieSafety(
    bmr: number,
    targetCalories: number,
    gender: 'male' | 'female'
  ): SafetyWarning[] {
    const warnings: SafetyWarning[] = [];
    
    // 基礎代謝を下回るチェック
    if (targetCalories < bmr) {
      warnings.push({
        level: 'critical',
        category: 'カロリー不足',
        message: '目標カロリーが基礎代謝量を下回っています',
        risks: [
          '代謝の低下',
          '筋肉量の減少',
          '栄養不足',
          'ホルモンバランスの乱れ',
          '免疫力の低下'
        ],
        recommendations: [
          `最低でも基礎代謝量（${Math.round(bmr)}kcal）以上を摂取してください`,
          '減量ペースを週0.5kg以下に調整することを推奨',
          'タンパク質摂取量を体重1kgあたり2g以上確保'
        ]
      });
    }

    // 極端な低カロリーチェック
    const minSafeCalories = gender === 'male' ? 1500 : 1200;
    if (targetCalories < minSafeCalories) {
      warnings.push({
        level: 'danger',
        category: '極端な低カロリー',
        message: `${gender === 'male' ? '男性' : '女性'}の最低推奨カロリー（${minSafeCalories}kcal）を下回っています`,
        risks: [
          '深刻な栄養失調',
          '骨密度の低下',
          '心臓への負担',
          '脱毛・肌荒れ',
          '生理不順（女性）'
        ],
        recommendations: [
          '医師の指導なしにこのカロリー設定は危険です',
          '段階的な減量計画への変更を強く推奨',
          '専門家への相談を検討してください'
        ]
      });
    }

    return warnings;
  }

  /**
   * 体脂肪率目標の安全性チェック
   */
  checkBodyFatGoals(
    currentBodyFat: number,
    targetBodyFat: number,
    gender: 'male' | 'female'
  ): SafetyWarning[] {
    const warnings: SafetyWarning[] = [];
    const essentialFat = { male: 3, female: 12 };
    const athleteFat = { male: 8, female: 15 };
    const healthyMin = { male: 10, female: 18 };

    // 必須脂肪以下
    if (targetBodyFat <= essentialFat[gender]) {
      warnings.push({
        level: 'danger',
        category: '危険な体脂肪率',
        message: `目標体脂肪率が必須脂肪レベル（${essentialFat[gender]}%）以下です`,
        risks: [
          '臓器機能の障害',
          '神経系の損傷',
          '深刻なホルモン異常',
          '不妊リスク',
          '生命の危険'
        ],
        recommendations: [
          '即座に目標を見直してください',
          `最低でも${healthyMin[gender]}%以上を目標に設定`,
          '医療機関での健康チェックを推奨'
        ]
      });
    }
    // アスリートレベル
    else if (targetBodyFat <= athleteFat[gender]) {
      warnings.push({
        level: 'warning',
        category: 'アスリートレベルの体脂肪率',
        message: `目標体脂肪率がアスリートレベル（${athleteFat[gender]}%以下）です`,
        risks: [
          'ホルモンバランスの乱れ',
          '免疫力の低下',
          'パフォーマンスの低下',
          '怪我のリスク増加',
          gender === 'female' ? '月経異常' : 'テストステロン低下'
        ],
        recommendations: [
          '専門的な指導者のサポートが必要',
          '定期的な健康チェックを実施',
          '十分な休養と栄養摂取を確保',
          '段階的なアプローチを推奨'
        ]
      });
    }

    // 急激な減少
    const weeklyFatLoss = (currentBodyFat - targetBodyFat) / 12; // 12週間想定
    if (weeklyFatLoss > 0.5) {
      warnings.push({
        level: 'warning',
        category: '急激な体脂肪減少',
        message: '体脂肪の減少ペースが速すぎます',
        risks: [
          '筋肉量の大幅な減少',
          'リバウンドリスク',
          '代謝の適応',
          '栄養不足'
        ],
        recommendations: [
          '週0.5%以下の減少ペースに調整',
          'リフィード日の導入を検討',
          '筋力トレーニングの強化'
        ]
      });
    }

    return warnings;
  }

  /**
   * トレーニング頻度の安全性チェック
   */
  checkTrainingFrequency(
    trainingDaysPerWeek: number,
    experience: 'beginner' | 'intermediate' | 'advanced'
  ): SafetyWarning[] {
    const warnings: SafetyWarning[] = [];
    const maxRecommended = { beginner: 4, intermediate: 5, advanced: 6 };

    if (trainingDaysPerWeek > maxRecommended[experience]) {
      warnings.push({
        level: 'warning',
        category: 'オーバートレーニング',
        message: `経験レベルに対してトレーニング頻度が多すぎます`,
        risks: [
          'オーバートレーニング症候群',
          '怪我のリスク増加',
          'パフォーマンス低下',
          '慢性疲労',
          '免疫力低下'
        ],
        recommendations: [
          `週${maxRecommended[experience]}日以下に調整を推奨`,
          '十分な休養日の確保',
          'アクティブリカバリーの導入',
          '睡眠時間の確保（7-9時間）'
        ]
      });
    }

    return warnings;
  }

  /**
   * 水分摂取量の推奨
   */
  calculateWaterIntake(
    weight: number,
    activityLevel: 'sedentary' | 'active' | 'athlete'
  ): {
    minimum: number;
    recommended: number;
    training: number;
  } {
    const baseWater = weight * 30; // 体重1kgあたり30ml
    const activityMultiplier = {
      sedentary: 1.0,
      active: 1.3,
      athlete: 1.5
    };

    return {
      minimum: Math.round(baseWater / 100) * 100,
      recommended: Math.round(baseWater * activityMultiplier[activityLevel] / 100) * 100,
      training: 500 // トレーニング1時間あたり追加
    };
  }

  /**
   * 総合的な安全性評価
   */
  comprehensiveSafetyCheck(
    userData: {
      bmr: number;
      weight: number;
      currentBodyFat: number;
      gender: 'male' | 'female';
      experience: 'beginner' | 'intermediate' | 'advanced';
    },
    goals: {
      targetCalories: number;
      targetBodyFat: number;
      trainingDaysPerWeek: number;
    }
  ): SafetyAnalysis {
    const warnings: SafetyWarning[] = [];

    // 各項目の安全性チェック
    warnings.push(...this.checkCalorieSafety(userData.bmr, goals.targetCalories, userData.gender));
    warnings.push(...this.checkBodyFatGoals(userData.currentBodyFat, goals.targetBodyFat, userData.gender));
    warnings.push(...this.checkTrainingFrequency(goals.trainingDaysPerWeek, userData.experience));

    // 追加の一般的な推奨事項
    const generalRecommendations = [
      '定期的な健康診断の受診',
      '十分な睡眠時間の確保（7-9時間）',
      '適切な水分摂取',
      'ストレス管理の実施',
      '進捗の定期的なモニタリング'
    ];

    // 安全スコアの計算（100点満点）
    let score = 100;
    warnings.forEach(warning => {
      switch (warning.level) {
        case 'danger': score -= 40; break;
        case 'critical': score -= 25; break;
        case 'warning': score -= 15; break;
        case 'info': score -= 5; break;
      }
    });
    score = Math.max(0, score);

    // 総合評価
    let overallSafety: 'safe' | 'caution' | 'unsafe';
    if (score >= 80) overallSafety = 'safe';
    else if (score >= 50) overallSafety = 'caution';
    else overallSafety = 'unsafe';

    // 必須アクション
    const requiredActions = warnings
      .filter(w => w.level === 'danger' || w.level === 'critical')
      .flatMap(w => w.recommendations.slice(0, 2));

    return {
      overallSafety,
      score,
      warnings,
      recommendations: [...new Set([...warnings.flatMap(w => w.recommendations), ...generalRecommendations])].slice(0, 10),
      requiredActions
    };
  }

  /**
   * リスクレベルの色取得（UI表示用）
   */
  getRiskLevelColor(level: SafetyWarning['level']): string {
    const colors = {
      info: 'blue',
      warning: 'yellow',
      critical: 'orange',
      danger: 'red'
    };
    return colors[level];
  }
}

export default SafetyEngine;