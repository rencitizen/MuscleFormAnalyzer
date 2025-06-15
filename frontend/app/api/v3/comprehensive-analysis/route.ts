import { NextRequest, NextResponse } from 'next/server';
import { BodyCompositionEngine } from '@/lib/engines/bodyComposition';
import { MetabolismEngine } from '@/lib/engines/metabolism';
import { NutritionEngine } from '@/lib/engines/nutrition';
import { SafetyEngine } from '@/lib/engines/safety';
import { ComprehensiveAnalysisData } from '@/lib/engines/training/comprehensiveAnalysis';
import { AITrainingRecommendationEngine } from '@/lib/engines/training/aiRecommendation';

interface UserInput {
  gender: 'male' | 'female';
  age: number;
  height: number;
  weight: number;
  activityLevel: 'sedentary' | 'light' | 'moderate' | 'active' | 'veryActive';
  goal: 'cutting' | 'maintenance' | 'bulking';
  experience: 'beginner' | 'intermediate' | 'advanced';
  trainingDaysPerWeek: number;
  targetBodyFat?: number;
}

function validateUserInput(data: any): { isValid: boolean; errors: string[] } {
  const errors: string[] = [];
  
  // 性別チェック
  if (!data.gender || !['male', 'female'].includes(data.gender)) {
    errors.push('有効な性別を選択してください');
  }
  
  // 年齢チェック
  if (!data.age || data.age < 15 || data.age > 100) {
    errors.push('年齢は15-100歳の範囲で入力してください');
  }
  
  // 身長チェック
  if (!data.height || data.height < 100 || data.height > 250) {
    errors.push('身長は100-250cmの範囲で入力してください');
  }
  
  // 体重チェック
  if (!data.weight || data.weight < 30 || data.weight > 300) {
    errors.push('体重は30-300kgの範囲で入力してください');
  }
  
  // 活動レベルチェック
  const validActivityLevels = ['sedentary', 'light', 'moderate', 'active', 'veryActive'];
  if (!data.activityLevel || !validActivityLevels.includes(data.activityLevel)) {
    errors.push('有効な活動レベルを選択してください');
  }
  
  // 目標チェック
  const validGoals = ['cutting', 'maintenance', 'bulking'];
  if (!data.goal || !validGoals.includes(data.goal)) {
    errors.push('有効な目標を選択してください');
  }
  
  // 経験レベルチェック
  const validExperience = ['beginner', 'intermediate', 'advanced'];
  if (!data.experience || !validExperience.includes(data.experience)) {
    errors.push('有効な経験レベルを選択してください');
  }
  
  // トレーニング日数チェック
  if (data.trainingDaysPerWeek < 0 || data.trainingDaysPerWeek > 7) {
    errors.push('トレーニング日数は0-7日の範囲で入力してください');
  }
  
  // 目標体脂肪率チェック（オプション）
  if (data.targetBodyFat !== undefined && (data.targetBodyFat < 3 || data.targetBodyFat > 50)) {
    errors.push('目標体脂肪率は3-50%の範囲で入力してください');
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
}

export async function POST(request: NextRequest) {
  try {
    const data: UserInput = await request.json();
    
    // バリデーション
    const validation = validateUserInput(data);
    if (!validation.isValid) {
      return NextResponse.json(
        { error: 'Validation failed', details: validation.errors },
        { status: 400 }
      );
    }
    
    // エンジン初期化
    const bodyEngine = new BodyCompositionEngine();
    const metabolismEngine = new MetabolismEngine();
    const nutritionEngine = new NutritionEngine();
    const safetyEngine = new SafetyEngine();
    
    // 身体組成分析
    const bodyComposition = bodyEngine.analyzeBodyComposition(
      data.weight,
      data.height,
      data.age,
      data.gender
    );
    
    // 代謝分析
    const metabolism = metabolismEngine.analyzeMetabolism(
      data.weight,
      data.height,
      data.age,
      data.gender,
      data.activityLevel,
      data.goal
    );
    
    // 栄養プラン作成
    const activityMapping = {
      sedentary: 'sedentary' as const,
      light: 'sedentary' as const,
      moderate: 'active' as const,
      active: 'active' as const,
      veryActive: 'athlete' as const
    };
    
    const nutritionPlan = nutritionEngine.createNutritionPlan(
      metabolism.targetCalories,
      data.weight,
      data.goal,
      activityMapping[data.activityLevel],
      '4meals'
    );
    
    // 目標体脂肪率の設定（指定がない場合はデフォルト値）
    const targetBodyFat = data.targetBodyFat || getDefaultTargetBodyFat(
      data.goal,
      data.gender,
      bodyComposition.bodyFatPercentage
    );
    
    // 安全性チェック
    const safetyAnalysis = safetyEngine.comprehensiveSafetyCheck(
      {
        bmr: metabolism.bmr,
        weight: data.weight,
        currentBodyFat: bodyComposition.bodyFatPercentage,
        gender: data.gender,
        experience: data.experience
      },
      {
        targetCalories: metabolism.targetCalories,
        targetBodyFat: targetBodyFat,
        trainingDaysPerWeek: data.trainingDaysPerWeek
      }
    );
    
    // 水分摂取量の推奨
    const waterIntake = safetyEngine.calculateWaterIntake(
      data.weight,
      activityMapping[data.activityLevel]
    );
    
    // 包括的分析データの構築
    const comprehensiveAnalysis = new ComprehensiveAnalysisData();
    comprehensiveAnalysis.bodyMetrics = {
      height: data.height,
      weight: data.weight,
      bodyFat: bodyComposition.bodyFatPercentage,
      muscleMass: bodyComposition.leanBodyMass,
      bmr: metabolism.bmr,
      tdee: metabolism.tdee
    };
    comprehensiveAnalysis.nutritionStatus = {
      dailyCalories: metabolism.targetCalories,
      protein: nutritionPlan.dailyMacros.protein,
      carbs: nutritionPlan.dailyMacros.carbs,
      fat: nutritionPlan.dailyMacros.fats,
      hydration: waterIntake.daily
    };
    comprehensiveAnalysis.userProfile = {
      age: data.age,
      gender: data.gender,
      experience: data.experience,
      activityLevel: data.activityLevel
    };
    comprehensiveAnalysis.goals = {
      primary: data.goal === 'cutting' ? 'fat_loss' : 
               data.goal === 'bulking' ? 'muscle_gain' : 
               'maintenance',
      targetBodyFat: targetBodyFat
    };
    comprehensiveAnalysis.lifestyle = {
      weeklyTrainingTime: data.trainingDaysPerWeek * 1, // 1時間/セッションと仮定
      sleepHours: 7, // デフォルト値
      stressLevel: 'moderate', // デフォルト値
      workType: 'sedentary', // デフォルト値
      schedule: 'regular' // デフォルト値
    };
    comprehensiveAnalysis.preferences = {
      equipment: ['barbell', 'dumbbell', 'bench', 'pullup_bar'],
      trainingLocation: 'gym'
    };
    
    // 包括的分析の実行
    const analysisResult = comprehensiveAnalysis.generateComprehensiveAnalysis();
    
    // AIトレーニング推奨の生成（分析結果がある場合のみ）
    let trainingRecommendation = null;
    if (analysisResult) {
      const aiEngine = new AITrainingRecommendationEngine(analysisResult);
      trainingRecommendation = aiEngine.generatePersonalizedProgram();
    }
    
    // 統合結果
    const results = {
      userProfile: {
        ...data,
        currentBodyFat: bodyComposition.bodyFatPercentage,
        targetBodyFat
      },
      bodyComposition,
      metabolism,
      nutrition: {
        pfcMacros: nutritionPlan.dailyMacros,
        mealDistribution: nutritionPlan.mealDistribution,
        proteinPerKg: nutritionPlan.proteinPerKg,
        recommendations: nutritionPlan.recommendations,
        achievability: nutritionPlan.achievability
      },
      hydration: waterIntake,
      safetyAnalysis,
      trainingRecommendation,
      comprehensiveAnalysis: analysisResult,
      summary: {
        dailyCalorieDeficit: data.goal === 'cutting' ? metabolism.calorieDeficit : undefined,
        dailyCalorieSurplus: data.goal === 'bulking' ? metabolism.calorieSurplus : undefined,
        estimatedTimeToGoal: calculateTimeToGoal(
          data.weight,
          bodyComposition.bodyFatPercentage,
          targetBodyFat,
          metabolism.weeklyWeightChange
        ),
        keyRecommendations: generateKeyRecommendations(
          data,
          bodyComposition,
          metabolism,
          safetyAnalysis
        )
      },
      timestamp: new Date().toISOString()
    };
    
    return NextResponse.json(results);
    
  } catch (error) {
    console.error('Comprehensive analysis error:', error);
    return NextResponse.json(
      { error: 'Internal server error', message: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

// ヘルパー関数

function getDefaultTargetBodyFat(
  goal: 'cutting' | 'maintenance' | 'bulking',
  gender: 'male' | 'female',
  currentBodyFat: number
): number {
  const targets = {
    male: {
      cutting: Math.max(10, currentBodyFat - 5),
      maintenance: currentBodyFat,
      bulking: Math.min(20, currentBodyFat + 3)
    },
    female: {
      cutting: Math.max(18, currentBodyFat - 5),
      maintenance: currentBodyFat,
      bulking: Math.min(28, currentBodyFat + 3)
    }
  };
  
  return targets[gender][goal];
}

function calculateTimeToGoal(
  currentWeight: number,
  currentBodyFat: number,
  targetBodyFat: number,
  weeklyWeightChange: number
): string {
  if (currentBodyFat === targetBodyFat || weeklyWeightChange === 0) {
    return '現在の目標に到達しています';
  }
  
  const currentFatMass = currentWeight * (currentBodyFat / 100);
  const targetFatMass = currentWeight * (targetBodyFat / 100);
  const fatToChange = Math.abs(currentFatMass - targetFatMass);
  
  // 週間の脂肪変化量を推定（体重変化の70%が脂肪と仮定）
  const weeklyFatChange = Math.abs(weeklyWeightChange) * 0.7;
  const weeksToGoal = fatToChange / weeklyFatChange;
  
  if (weeksToGoal < 4) {
    return '約1ヶ月';
  } else if (weeksToGoal < 12) {
    return `約${Math.round(weeksToGoal)}週間`;
  } else {
    return `約${Math.round(weeksToGoal / 4)}ヶ月`;
  }
}

function generateKeyRecommendations(
  userData: UserInput,
  bodyComposition: any,
  metabolism: any,
  safetyAnalysis: any
): string[] {
  const recommendations: string[] = [];
  
  // 安全性に基づく推奨
  if (safetyAnalysis.overallSafety !== 'safe') {
    recommendations.push('安全性の警告を確認し、必要に応じて目標を調整してください');
  }
  
  // 目標別の推奨
  if (userData.goal === 'cutting') {
    recommendations.push('高タンパク質食を心がけ、筋肉量の維持に努めてください');
    recommendations.push('週2-3回の筋力トレーニングを継続してください');
    if (metabolism.targetCalories < metabolism.bmr * 1.2) {
      recommendations.push('カロリー制限が厳しすぎる可能性があります。段階的なアプローチを検討してください');
    }
  } else if (userData.goal === 'bulking') {
    recommendations.push('トレーニング後のタンパク質摂取を忘れずに');
    recommendations.push('十分な休養と睡眠（7-9時間）を確保してください');
    recommendations.push('週3-4回の筋力トレーニングを推奨します');
  } else {
    recommendations.push('現在の習慣を維持し、定期的に進捗を確認してください');
    recommendations.push('栄養バランスを意識した食事を心がけてください');
  }
  
  // 体組成に基づく推奨
  if (bodyComposition.bmi > 25) {
    recommendations.push('有酸素運動を週150分以上行うことを推奨します');
  }
  
  // 経験レベルに基づく推奨
  if (userData.experience === 'beginner') {
    recommendations.push('フォームの習得を優先し、段階的に負荷を増やしてください');
    recommendations.push('専門家の指導を受けることを検討してください');
  }
  
  return recommendations.slice(0, 5); // 最大5つの推奨事項
}

// OPTIONS メソッドの追加（CORS対応）
export async function OPTIONS(request: NextRequest) {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
}