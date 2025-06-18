// services/v3Api.ts
/**
 * TENAX FIT v3.0 API Service
 * 包括的フィットネス分析APIとの通信を管理
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001'
const V3_API_PREFIX = '/api/v3'

export interface UserProfile {
  weight: number
  height: number
  age: number
  gender: 'male' | 'female'
  activity_level: 'sedentary' | 'light' | 'moderate' | 'active' | 'very_active'
  goal: 'cutting' | 'maintenance' | 'bulking'
  experience?: 'beginner' | 'intermediate' | 'advanced'
  available_days?: number
  equipment?: 'bodyweight' | 'full_gym' | 'home_gym'
  target_body_fat?: number
  waist_cm?: number
  neck_cm?: number
  hip_cm?: number
  timeframe_weeks?: number
}

// 科学計算用の型定義
export interface BMRInput {
  weight: number
  height: number
  age: number
  gender: 'male' | 'female'
}

export interface BMRResult {
  bmr: number
  formula: string
  unit: string
}

export interface TDEEInput extends BMRInput {
  activity_level: 'sedentary' | 'light' | 'moderate' | 'active' | 'very_active'
}

export interface TDEEResult {
  tdee: number
  bmr: number
  activity_multiplier: number
  activity_level_description: string
}

export interface BodyFatInput {
  gender: 'male' | 'female'
  waist_cm?: number
  neck_cm?: number
  hip_cm?: number
  weight?: number
  height?: number
}

export interface BodyFatResult {
  body_fat_percentage: number
  method: string
  lean_body_mass: number
  fat_mass: number
}

export interface TargetCaloriesInput {
  tdee: number
  goal: 'cutting' | 'maintenance' | 'bulking'
  experience_level: 'beginner' | 'intermediate' | 'advanced'
}

export interface TargetCaloriesResult {
  daily_calories: number
  deficit_or_surplus: number
  weekly_weight_change_estimate: number
  description: string
}

export interface PFCBalanceInput {
  daily_calories: number
  goal: 'cutting' | 'maintenance' | 'bulking'
  weight: number
  experience_level: 'beginner' | 'intermediate' | 'advanced'
}

export interface PFCBalanceResult {
  protein: {
    grams: number
    calories: number
    percentage: number
  }
  fat: {
    grams: number
    calories: number
    percentage: number
  }
  carbs: {
    grams: number
    calories: number
    percentage: number
  }
  total_calories: number
}

export interface CalorieSafetyInput {
  daily_calories: number
  bmr: number
  gender: 'male' | 'female'
  age: number
  goal: 'cutting' | 'maintenance' | 'bulking'
}

export interface CalorieSafetyResult {
  is_safe: boolean
  warnings: string[]
  minimum_safe_calories: number
  recommendation: string
}

export interface ComprehensiveAnalysisResult {
  analysis_id: string
  user_profile: any
  body_composition: {
    bmi: number
    bmi_category: string
    estimated_body_fat: number
    lean_body_mass: any
    ffmi: any
    ideal_weight_range: any
    health_warnings: any[]
  }
  metabolism: {
    bmr_calculations: any
    tdee: any
    calorie_goals: any
    metabolic_type: string
  }
  nutrition: {
    daily_macros: any
    protein_requirements: any
    meal_plan: any
    workout_nutrition: any
    high_protein_foods: any
    hydration: any
  }
  training: {
    workout_plan: any
    exercise_calories: any
    recovery_needs: any
    form_analysis_integration: any
  }
  safety_analysis: {
    overall_safety: string
    risk_score: number
    warnings: any[]
    recommendations: any[]
    monitoring_plan: any
    emergency_signs: any
  }
  ai_integration: any
  next_steps: any
  generated_at: string
}

export interface ProgressData {
  date?: string
  weight?: number
  body_fat?: number
  measurements?: {
    waist?: number
    chest?: number
    arms?: number
    thighs?: number
  }
  performance?: {
    squat_1rm?: number
    bench_1rm?: number
    deadlift_1rm?: number
  }
  subjective?: {
    energy_level?: number
    sleep_quality?: number
    mood?: number
    soreness?: number
  }
}

class V3ApiService {
  private baseUrl: string

  constructor() {
    this.baseUrl = `${API_BASE_URL}${V3_API_PREFIX}`
  }

  /**
   * 包括的フィットネス分析を実行
   */
  async performComprehensiveAnalysis(
    userProfile: UserProfile
  ): Promise<ComprehensiveAnalysisResult> {
    try {
      const response = await fetch(`${this.baseUrl}/comprehensive_analysis`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(userProfile),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.message || '分析に失敗しました')
      }

      return await response.json()
    } catch (error) {
      console.error('Comprehensive analysis error:', error)
      throw error
    }
  }

  /**
   * フィットネス目標を更新
   */
  async updateGoals(userId: string, newGoals: any): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/update_goals`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          user_id: userId,
          ...newGoals,
        }),
      })

      if (!response.ok) {
        throw new Error('目標の更新に失敗しました')
      }

      return await response.json()
    } catch (error) {
      console.error('Update goals error:', error)
      throw error
    }
  }

  /**
   * 進捗を追跡
   */
  async trackProgress(userId: string, progressData: ProgressData): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/track_progress`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          user_id: userId,
          ...progressData,
        }),
      })

      if (!response.ok) {
        throw new Error('進捗の記録に失敗しました')
      }

      return await response.json()
    } catch (error) {
      console.error('Track progress error:', error)
      throw error
    }
  }

  /**
   * AI分析結果を統合
   */
  async integrateAIAnalysis(
    type: 'pose' | 'meal' | 'phase',
    analysisData: any
  ): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/integrate_ai_analysis`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          type,
          ...analysisData,
        }),
      })

      if (!response.ok) {
        throw new Error('AI分析の統合に失敗しました')
      }

      return await response.json()
    } catch (error) {
      console.error('Integrate AI analysis error:', error)
      throw error
    }
  }

  /**
   * 包括的レポートを生成
   */
  async generateReport(
    userId: string,
    reportType: 'weekly' | 'monthly' | 'progress' = 'weekly'
  ): Promise<any> {
    try {
      const response = await fetch(
        `${this.baseUrl}/generate_reports?user_id=${userId}&type=${reportType}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
        }
      )

      if (!response.ok) {
        throw new Error('レポートの生成に失敗しました')
      }

      return await response.json()
    } catch (error) {
      console.error('Generate report error:', error)
      throw error
    }
  }

  /**
   * 保存されたプロファイルを取得（ローカルストレージ）
   */
  getSavedProfile(): UserProfile | null {
    try {
      const saved = localStorage.getItem('tenax_fit_user_profile')
      return saved ? JSON.parse(saved) : null
    } catch {
      return null
    }
  }

  /**
   * プロファイルを保存（ローカルストレージ）
   */
  saveProfile(profile: UserProfile): void {
    try {
      localStorage.setItem('tenax_fit_user_profile', JSON.stringify(profile))
    } catch (error) {
      console.error('Failed to save profile:', error)
    }
  }

  /**
   * 最後の分析結果を取得（ローカルストレージ）
   */
  getLastAnalysis(): ComprehensiveAnalysisResult | null {
    try {
      const saved = localStorage.getItem('tenax_fit_last_analysis')
      return saved ? JSON.parse(saved) : null
    } catch {
      return null
    }
  }

  /**
   * 分析結果を保存（ローカルストレージ）
   */
  saveAnalysis(analysis: ComprehensiveAnalysisResult): void {
    try {
      localStorage.setItem('tenax_fit_last_analysis', JSON.stringify(analysis))
      localStorage.setItem('tenax_fit_last_analysis_date', new Date().toISOString())
    } catch (error) {
      console.error('Failed to save analysis:', error)
    }
  }

  /**
   * 分析が古いかチェック（24時間以上）
   */
  isAnalysisStale(): boolean {
    try {
      const lastDate = localStorage.getItem('tenax_fit_last_analysis_date')
      if (!lastDate) return true

      const hoursSince = (Date.now() - new Date(lastDate).getTime()) / (1000 * 60 * 60)
      return hoursSince > 24
    } catch {
      return true
    }
  }

  /**
   * BMR（基礎代謝率）を計算
   */
  async calculateBMR(data: BMRInput): Promise<BMRResult> {
    try {
      const response = await fetch(`${this.baseUrl}/calculations/bmr`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.message || 'BMR計算に失敗しました')
      }

      return await response.json()
    } catch (error) {
      console.error('BMR calculation error:', error)
      throw error
    }
  }

  /**
   * TDEE（総消費カロリー）を計算
   */
  async calculateTDEE(data: TDEEInput): Promise<TDEEResult> {
    try {
      const response = await fetch(`${this.baseUrl}/calculations/tdee`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.message || 'TDEE計算に失敗しました')
      }

      return await response.json()
    } catch (error) {
      console.error('TDEE calculation error:', error)
      throw error
    }
  }

  /**
   * 体脂肪率を推定
   */
  async estimateBodyFat(data: BodyFatInput): Promise<BodyFatResult> {
    try {
      const response = await fetch(`${this.baseUrl}/calculations/body-fat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.message || '体脂肪率推定に失敗しました')
      }

      return await response.json()
    } catch (error) {
      console.error('Body fat estimation error:', error)
      throw error
    }
  }

  /**
   * 目標カロリーを計算
   */
  async getTargetCalories(data: TargetCaloriesInput): Promise<TargetCaloriesResult> {
    try {
      const response = await fetch(`${this.baseUrl}/calculations/target-calories`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.message || '目標カロリー計算に失敗しました')
      }

      return await response.json()
    } catch (error) {
      console.error('Target calories calculation error:', error)
      throw error
    }
  }

  /**
   * PFCバランスを計算
   */
  async getPFCBalance(data: PFCBalanceInput): Promise<PFCBalanceResult> {
    try {
      const response = await fetch(`${this.baseUrl}/nutrition/pfc-balance`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.message || 'PFCバランス計算に失敗しました')
      }

      return await response.json()
    } catch (error) {
      console.error('PFC balance calculation error:', error)
      throw error
    }
  }

  /**
   * カロリー設定の安全性をチェック
   */
  async checkCalorieSafety(data: CalorieSafetyInput): Promise<CalorieSafetyResult> {
    try {
      const response = await fetch(`${this.baseUrl}/safety/calorie-check`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.message || '安全性チェックに失敗しました')
      }

      return await response.json()
    } catch (error) {
      console.error('Calorie safety check error:', error)
      throw error
    }
  }
}

// シングルトンインスタンスをエクスポート
export const v3Api = new V3ApiService()

// 便利なフック
export function useV3Api() {
  return {
    performAnalysis: v3Api.performComprehensiveAnalysis.bind(v3Api),
    updateGoals: v3Api.updateGoals.bind(v3Api),
    trackProgress: v3Api.trackProgress.bind(v3Api),
    integrateAIAnalysis: v3Api.integrateAIAnalysis.bind(v3Api),
    generateReport: v3Api.generateReport.bind(v3Api),
    getSavedProfile: v3Api.getSavedProfile.bind(v3Api),
    saveProfile: v3Api.saveProfile.bind(v3Api),
    getLastAnalysis: v3Api.getLastAnalysis.bind(v3Api),
    saveAnalysis: v3Api.saveAnalysis.bind(v3Api),
    isAnalysisStale: v3Api.isAnalysisStale.bind(v3Api),
    // 科学計算メソッド
    calculateBMR: v3Api.calculateBMR.bind(v3Api),
    calculateTDEE: v3Api.calculateTDEE.bind(v3Api),
    estimateBodyFat: v3Api.estimateBodyFat.bind(v3Api),
    getTargetCalories: v3Api.getTargetCalories.bind(v3Api),
    getPFCBalance: v3Api.getPFCBalance.bind(v3Api),
    checkCalorieSafety: v3Api.checkCalorieSafety.bind(v3Api),
  }
}