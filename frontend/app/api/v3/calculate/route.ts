// TENAX FIT v3.0 - Edge API for Scientific Calculations
import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'edge'; // Edge Runtime使用

// 型定義
interface CalculationRequest {
  type: 'bmr' | 'tdee' | 'body-fat' | 'target-calories' | 'pfc-balance' | 'safety-check';
  data: any;
}

interface UserProfile {
  age: number;
  gender: 'male' | 'female';
  height: number; // cm
  weight: number; // kg
  activityLevel?: 'sedentary' | 'lightly_active' | 'moderately_active' | 'very_active' | 'extra_active';
  goal?: 'lose_weight' | 'maintain' | 'gain_muscle';
  bodyFatPercentage?: number;
  waist?: number; // cm
  neck?: number; // cm
  hip?: number; // cm (女性のみ)
}

// BMR計算（Mifflin-St Jeor方程式）
function calculateBMR(profile: UserProfile): number {
  const { age, gender, height, weight } = profile;
  
  if (gender === 'male') {
    return 10 * weight + 6.25 * height - 5 * age + 5;
  } else {
    return 10 * weight + 6.25 * height - 5 * age - 161;
  }
}

// TDEE計算
function calculateTDEE(bmr: number, activityLevel: string): number {
  const activityMultipliers: Record<string, number> = {
    sedentary: 1.2,
    lightly_active: 1.375,
    moderately_active: 1.55,
    very_active: 1.725,
    extra_active: 1.9
  };
  
  return bmr * (activityMultipliers[activityLevel] || 1.2);
}

// 体脂肪率計算（海軍式）
function calculateBodyFat(profile: UserProfile): number {
  const { gender, height, waist, neck, hip } = profile;
  
  if (!waist || !neck) {
    throw new Error('腰囲と首囲が必要です');
  }
  
  if (gender === 'male') {
    return 495 / (1.0324 - 0.19077 * Math.log10(waist - neck) + 0.15456 * Math.log10(height)) - 450;
  } else {
    if (!hip) {
      throw new Error('女性の場合はヒップ囲も必要です');
    }
    return 495 / (1.29579 - 0.35004 * Math.log10(waist + hip - neck) + 0.22100 * Math.log10(height)) - 450;
  }
}

// 目標カロリー計算
function calculateTargetCalories(tdee: number, goal: string): {
  calories: number;
  deficit: number;
  weeklyLoss: number;
} {
  let deficit = 0;
  let calories = tdee;
  
  switch (goal) {
    case 'lose_weight':
      deficit = 500; // 500kcal/日の赤字で週0.5kg減
      calories = tdee - deficit;
      break;
    case 'gain_muscle':
      deficit = -300; // 300kcal/日の黒字
      calories = tdee + 300;
      break;
    default:
      deficit = 0;
  }
  
  return {
    calories: Math.round(calories),
    deficit: deficit,
    weeklyLoss: (deficit * 7) / 7700 // 1kg = 7700kcal
  };
}

// PFCバランス計算
function calculatePFCBalance(calories: number, goal: string, weight: number): {
  protein: { grams: number; calories: number; percentage: number };
  fat: { grams: number; calories: number; percentage: number };
  carbs: { grams: number; calories: number; percentage: number };
} {
  let proteinRatio = 0.3;
  let fatRatio = 0.25;
  let carbRatio = 0.45;
  
  // 目標に応じて調整
  if (goal === 'gain_muscle') {
    proteinRatio = 0.35;
    fatRatio = 0.25;
    carbRatio = 0.40;
  } else if (goal === 'lose_weight') {
    proteinRatio = 0.40;
    fatRatio = 0.30;
    carbRatio = 0.30;
  }
  
  // 最低タンパク質量を確保（体重1kgあたり1.6g）
  const minProtein = weight * 1.6;
  const proteinCalories = Math.max(minProtein * 4, calories * proteinRatio);
  const proteinGrams = proteinCalories / 4;
  
  const fatCalories = calories * fatRatio;
  const fatGrams = fatCalories / 9;
  
  const carbCalories = calories - proteinCalories - fatCalories;
  const carbGrams = carbCalories / 4;
  
  return {
    protein: {
      grams: Math.round(proteinGrams),
      calories: Math.round(proteinCalories),
      percentage: Math.round((proteinCalories / calories) * 100)
    },
    fat: {
      grams: Math.round(fatGrams),
      calories: Math.round(fatCalories),
      percentage: Math.round((fatCalories / calories) * 100)
    },
    carbs: {
      grams: Math.round(carbGrams),
      calories: Math.round(carbCalories),
      percentage: Math.round((carbCalories / calories) * 100)
    }
  };
}

// 安全性チェック
function performSafetyCheck(profile: UserProfile, targetCalories: number): {
  safe: boolean;
  warnings: string[];
  recommendations: string[];
} {
  const warnings: string[] = [];
  const recommendations: string[] = [];
  
  // BMI計算
  const bmi = profile.weight / Math.pow(profile.height / 100, 2);
  
  // カロリー下限チェック
  const minCalories = profile.gender === 'male' ? 1500 : 1200;
  if (targetCalories < minCalories) {
    warnings.push(`目標カロリーが推奨下限値（${minCalories}kcal）を下回っています`);
    recommendations.push('より緩やかな減量ペースを検討してください');
  }
  
  // BMIチェック
  if (bmi < 18.5) {
    warnings.push('BMIが低体重の範囲です');
    recommendations.push('減量よりも筋肉量の増加を優先することをお勧めします');
  } else if (bmi > 30) {
    warnings.push('BMIが肥満の範囲です');
    recommendations.push('医師の指導のもとで減量を行うことをお勧めします');
  }
  
  // 年齢チェック
  if (profile.age < 18) {
    warnings.push('18歳未満の方は成長期のため特別な配慮が必要です');
    recommendations.push('医師や栄養士に相談することをお勧めします');
  } else if (profile.age > 65) {
    warnings.push('65歳以上の方は筋肉量の維持が特に重要です');
    recommendations.push('タンパク質摂取量を増やし、適度な運動を心がけてください');
  }
  
  return {
    safe: warnings.length === 0,
    warnings,
    recommendations
  };
}

// メインハンドラー
export async function POST(request: NextRequest) {
  try {
    const body: CalculationRequest = await request.json();
    const { type, data } = body;
    
    let result: any;
    
    switch (type) {
      case 'bmr': {
        const bmr = calculateBMR(data);
        result = {
          bmr: Math.round(bmr),
          formula: 'Mifflin-St Jeor',
          unit: 'kcal/day'
        };
        break;
      }
      
      case 'tdee': {
        const bmr = calculateBMR(data);
        const tdee = calculateTDEE(bmr, data.activityLevel);
        result = {
          bmr: Math.round(bmr),
          tdee: Math.round(tdee),
          activityLevel: data.activityLevel,
          unit: 'kcal/day'
        };
        break;
      }
      
      case 'body-fat': {
        const bodyFat = calculateBodyFat(data);
        const leanMass = data.weight * (1 - bodyFat / 100);
        result = {
          percentage: Math.round(bodyFat * 10) / 10,
          leanMass: Math.round(leanMass * 10) / 10,
          fatMass: Math.round((data.weight - leanMass) * 10) / 10,
          category: getBodyFatCategory(bodyFat, data.gender)
        };
        break;
      }
      
      case 'target-calories': {
        const bmr = calculateBMR(data);
        const tdee = calculateTDEE(bmr, data.activityLevel);
        const target = calculateTargetCalories(tdee, data.goal);
        result = {
          ...target,
          tdee: Math.round(tdee),
          goal: data.goal
        };
        break;
      }
      
      case 'pfc-balance': {
        const pfc = calculatePFCBalance(data.calories, data.goal, data.weight);
        result = pfc;
        break;
      }
      
      case 'safety-check': {
        result = performSafetyCheck(data.profile, data.targetCalories);
        break;
      }
      
      default:
        return NextResponse.json(
          { error: '不正な計算タイプです' },
          { status: 400 }
        );
    }
    
    return NextResponse.json({
      success: true,
      type,
      result,
      timestamp: new Date().toISOString()
    });
    
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || '計算中にエラーが発生しました' },
      { status: 500 }
    );
  }
}

// 体脂肪率カテゴリー判定
function getBodyFatCategory(percentage: number, gender: 'male' | 'female'): string {
  if (gender === 'male') {
    if (percentage < 6) return '必須脂肪';
    if (percentage < 14) return 'アスリート';
    if (percentage < 18) return 'フィットネス';
    if (percentage < 25) return '標準';
    return '肥満';
  } else {
    if (percentage < 14) return '必須脂肪';
    if (percentage < 21) return 'アスリート';
    if (percentage < 25) return 'フィットネス';
    if (percentage < 32) return '標準';
    return '肥満';
  }
}