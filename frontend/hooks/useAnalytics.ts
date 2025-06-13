'use client'

import { useEffect, useCallback } from 'react'
import { usePathname } from 'next/navigation'

interface AnalyticsEvent {
  event: string
  properties?: Record<string, any>
  timestamp: Date
  sessionId: string
  userId?: string
  pageUrl: string
}

interface UserTraits {
  email?: string
  name?: string
  plan?: string
  createdAt?: Date
  [key: string]: any
}

// セッションIDの生成・取得
const getSessionId = () => {
  let sessionId = sessionStorage.getItem('sessionId')
  if (!sessionId) {
    sessionId = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    sessionStorage.setItem('sessionId', sessionId)
  }
  return sessionId
}

// オフラインイベントの保存
const saveOfflineEvent = (event: AnalyticsEvent) => {
  const offlineEvents = JSON.parse(localStorage.getItem('offlineAnalytics') || '[]')
  offlineEvents.push(event)
  localStorage.setItem('offlineAnalytics', JSON.stringify(offlineEvents))
}

// オフラインイベントの送信
const sendOfflineEvents = async () => {
  const offlineEvents = JSON.parse(localStorage.getItem('offlineAnalytics') || '[]')
  if (offlineEvents.length === 0) return

  try {
    const response = await fetch('/api/analytics/batch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ events: offlineEvents })
    })

    if (response.ok) {
      localStorage.removeItem('offlineAnalytics')
    }
  } catch (error) {
    console.error('Failed to send offline analytics:', error)
  }
}

export function useAnalytics() {
  const pathname = usePathname()

  // ページビューの自動トラッキング
  useEffect(() => {
    track('page_view', {
      path: pathname,
      title: document.title,
      referrer: document.referrer
    })
  }, [pathname])

  // オンライン復帰時にオフラインイベントを送信
  useEffect(() => {
    const handleOnline = () => {
      sendOfflineEvents()
    }

    window.addEventListener('online', handleOnline)
    return () => window.removeEventListener('online', handleOnline)
  }, [])

  // イベントトラッキング
  const track = useCallback(async (
    event: string,
    properties?: Record<string, any>
  ) => {
    const analyticsEvent: AnalyticsEvent = {
      event,
      properties,
      timestamp: new Date(),
      sessionId: getSessionId(),
      userId: localStorage.getItem('userId') || undefined,
      pageUrl: window.location.href
    }

    // コンソールログ（開発環境）
    if (process.env.NODE_ENV === 'development') {
      console.log('📊 Analytics Event:', analyticsEvent)
    }

    // サーバーに送信
    try {
      const response = await fetch('/api/analytics/track', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(analyticsEvent)
      })

      if (!response.ok) {
        throw new Error('Failed to send analytics')
      }
    } catch (error) {
      console.error('Analytics error:', error)
      saveOfflineEvent(analyticsEvent)
    }

    // Google Analytics（もし設定されていれば）
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', event, properties)
    }

    // Mixpanel（もし設定されていれば）
    if (typeof window !== 'undefined' && (window as any).mixpanel) {
      (window as any).mixpanel.track(event, properties)
    }
  }, [])

  // ユーザー識別
  const identify = useCallback(async (
    userId: string,
    traits?: UserTraits
  ) => {
    localStorage.setItem('userId', userId)

    // サーバーに送信
    try {
      await fetch('/api/analytics/identify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId,
          traits,
          timestamp: new Date()
        })
      })
    } catch (error) {
      console.error('Identify error:', error)
    }

    // Google Analytics
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('config', process.env.NEXT_PUBLIC_GA_ID, {
        user_id: userId
      })
    }

    // Mixpanel
    if (typeof window !== 'undefined' && (window as any).mixpanel) {
      (window as any).mixpanel.identify(userId)
      if (traits) {
        (window as any).mixpanel.people.set(traits)
      }
    }
  }, [])

  // タイミング計測
  const trackTiming = useCallback((
    category: string,
    variable: string,
    value: number,
    label?: string
  ) => {
    track('timing_complete', {
      timing_category: category,
      timing_variable: variable,
      timing_value: value,
      timing_label: label
    })
  }, [track])

  // エラートラッキング
  const trackError = useCallback((
    error: Error | string,
    context?: Record<string, any>
  ) => {
    track('error', {
      error_message: error instanceof Error ? error.message : error,
      error_stack: error instanceof Error ? error.stack : undefined,
      ...context
    })
  }, [track])

  // 機能使用率トラッキング
  const trackFeatureUsage = useCallback((
    feature: string,
    action: string,
    metadata?: Record<string, any>
  ) => {
    track('feature_usage', {
      feature_name: feature,
      feature_action: action,
      ...metadata
    })
  }, [track])

  // A/Bテストトラッキング
  const trackABTest = useCallback((
    testId: string,
    variant: string,
    action: string
  ) => {
    track('ab_test', {
      test_id: testId,
      variant,
      action
    })
  }, [track])

  return {
    track,
    identify,
    trackTiming,
    trackError,
    trackFeatureUsage,
    trackABTest
  }
}

// パフォーマンス計測用フック
export function usePerformanceTracking() {
  const { trackTiming } = useAnalytics()

  const measurePerformance = useCallback((
    name: string,
    fn: () => Promise<any>
  ) => {
    return async () => {
      const startTime = performance.now()
      try {
        const result = await fn()
        const duration = performance.now() - startTime
        trackTiming('performance', name, duration)
        return result
      } catch (error) {
        const duration = performance.now() - startTime
        trackTiming('performance', `${name}_error`, duration)
        throw error
      }
    }
  }, [trackTiming])

  return { measurePerformance }
}