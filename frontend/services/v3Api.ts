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
  }
}