/**
 * A/Bテストフレームワーク
 * ユーザーエクスペリエンスの継続的改善のためのテスト基盤
 */

import React from 'react'
import { useAnalytics } from '@/hooks/useAnalytics'

interface ABTestConfig {
  id: string
  name: string
  description: string
  variants: {
    control: any
    treatment: any
  }
  traffic: number // 0-100 (テストに参加するトラフィックの割合)
  active: boolean
  startDate: Date
  endDate?: Date
}

// アクティブなA/Bテスト設定
const AB_TESTS: Record<string, ABTestConfig> = {
  'onboarding_flow': {
    id: 'onboarding_flow',
    name: 'オンボーディングフロー改善',
    description: 'チュートリアルの表示方法をテスト',
    variants: {
      control: 'modal',
      treatment: 'inline'
    },
    traffic: 50,
    active: true,
    startDate: new Date('2024-01-01')
  },
  'cta_button_color': {
    id: 'cta_button_color',
    name: 'CTAボタンカラー',
    description: '主要アクションボタンの色をテスト',
    variants: {
      control: 'blue',
      treatment: 'green'
    },
    traffic: 30,
    active: true,
    startDate: new Date('2024-01-15')
  },
  'feedback_position': {
    id: 'feedback_position',
    name: 'フィードバックボタン位置',
    description: 'フィードバックボタンの配置をテスト',
    variants: {
      control: 'bottom-right',
      treatment: 'bottom-left'
    },
    traffic: 20,
    active: false,
    startDate: new Date('2024-02-01'),
    endDate: new Date('2024-02-28')
  }
}

class ABTestManager {
  private userVariants: Map<string, string> = new Map()
  
  constructor() {
    // ローカルストレージから既存の割り当てを読み込み
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('ab_test_variants')
      if (stored) {
        try {
          const variants = JSON.parse(stored)
          Object.entries(variants).forEach(([testId, variant]) => {
            this.userVariants.set(testId, variant as string)
          })
        } catch (error) {
          console.error('Failed to parse AB test variants:', error)
        }
      }
    }
  }

  /**
   * ユーザーのバリアントを取得
   */
  getVariant(testId: string): 'control' | 'treatment' {
    const test = AB_TESTS[testId]
    
    // テストが存在しない、または非アクティブな場合はコントロールを返す
    if (!test || !test.active) {
      return 'control'
    }

    // 既に割り当てられている場合はそれを返す
    const existingVariant = this.userVariants.get(testId)
    if (existingVariant) {
      return existingVariant as 'control' | 'treatment'
    }

    // 新規割り当て
    const variant = this.assignVariant(testId, test.traffic)
    this.saveVariant(testId, variant)
    
    // 割り当てを記録
    if (typeof window !== 'undefined' && (window as any).analytics) {
      (window as any).analytics.track('ab_test_assigned', {
        test_id: testId,
        variant,
        test_name: test.name
      })
    }

    return variant
  }

  /**
   * バリアントを割り当て
   */
  private assignVariant(testId: string, trafficPercentage: number): 'control' | 'treatment' {
    // ユーザーIDまたはセッションIDをベースにハッシュを生成
    const userId = this.getUserId()
    const hash = this.hashCode(`${testId}-${userId}`)
    const bucket = Math.abs(hash) % 100

    // トラフィックの割合に基づいてテストに参加するか判定
    if (bucket >= trafficPercentage) {
      return 'control' // テストに参加しない
    }

    // 50/50で割り当て
    return bucket % 2 === 0 ? 'control' : 'treatment'
  }

  /**
   * ユーザーIDを取得
   */
  private getUserId(): string {
    if (typeof window === 'undefined') return 'server'
    
    let userId = localStorage.getItem('userId')
    if (!userId) {
      userId = sessionStorage.getItem('sessionId')
      if (!userId) {
        userId = `anon-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
        sessionStorage.setItem('sessionId', userId)
      }
    }
    return userId
  }

  /**
   * 文字列のハッシュ値を計算
   */
  private hashCode(str: string): number {
    let hash = 0
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i)
      hash = ((hash << 5) - hash) + char
      hash = hash & hash // Convert to 32bit integer
    }
    return hash
  }

  /**
   * バリアントを保存
   */
  private saveVariant(testId: string, variant: string) {
    this.userVariants.set(testId, variant)
    
    if (typeof window !== 'undefined') {
      const variants: Record<string, string> = {}
      this.userVariants.forEach((v, id) => {
        variants[id] = v
      })
      localStorage.setItem('ab_test_variants', JSON.stringify(variants))
    }
  }

  /**
   * コンバージョンを記録
   */
  trackConversion(testId: string, conversionType: string = 'default') {
    const variant = this.userVariants.get(testId)
    if (!variant) return

    if (typeof window !== 'undefined' && (window as any).analytics) {
      (window as any).analytics.track('ab_test_conversion', {
        test_id: testId,
        variant,
        conversion_type: conversionType,
        test_name: AB_TESTS[testId]?.name
      })
    }
  }

  /**
   * すべてのアクティブなテストを取得
   */
  getActiveTests(): ABTestConfig[] {
    return Object.values(AB_TESTS).filter(test => test.active)
  }

  /**
   * テスト結果のサマリーを取得（開発用）
   */
  getTestSummary(): Record<string, any> {
    const summary: Record<string, any> = {}
    
    this.userVariants.forEach((variant, testId) => {
      const test = AB_TESTS[testId]
      if (test) {
        summary[testId] = {
          name: test.name,
          variant,
          active: test.active
        }
      }
    })

    return summary
  }
}

// シングルトンインスタンス
export const ABTest = new ABTestManager()

// React Hook for A/B Testing
export function useABTest(testId: string) {
  const { trackABTest } = useAnalytics()
  
  const variant = ABTest.getVariant(testId)
  const test = AB_TESTS[testId]
  
  const trackInteraction = (action: string) => {
    trackABTest(testId, variant, action)
  }
  
  const trackConversion = (conversionType: string = 'default') => {
    ABTest.trackConversion(testId, conversionType)
  }

  return {
    variant,
    isControl: variant === 'control',
    isTreatment: variant === 'treatment',
    value: test?.variants[variant],
    trackInteraction,
    trackConversion
  }
}

// A/Bテストコンポーネントラッパー
interface ABTestComponentProps {
  testId: string
  control: React.ReactNode
  treatment: React.ReactNode
}

export function ABTestComponent({ testId, control, treatment }: ABTestComponentProps) {
  const { variant } = useABTest(testId)
  return variant === 'control' ? control : treatment
}