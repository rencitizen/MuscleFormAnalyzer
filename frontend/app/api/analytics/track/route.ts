import { NextRequest, NextResponse } from 'next/server'

interface AnalyticsEvent {
  event: string
  properties?: Record<string, any>
  timestamp: string
  sessionId: string
  userId?: string
  pageUrl: string
}

// In-memory storage for demo purposes
// TODO: 実際の実装では、データベースやAnalyticsサービスに送信
const eventStore: AnalyticsEvent[] = []

export async function POST(request: NextRequest) {
  try {
    const body: AnalyticsEvent = await request.json()
    
    // バリデーション
    if (!body.event || !body.sessionId) {
      return NextResponse.json(
        { error: '必須項目が不足しています' },
        { status: 400 }
      )
    }

    // イベントを保存
    const event: AnalyticsEvent = {
      ...body,
      timestamp: new Date().toISOString()
    }
    
    eventStore.push(event)

    // 開発環境ではコンソールに出力
    if (process.env.NODE_ENV === 'development') {
      console.log('📊 Analytics Event:', {
        event: event.event,
        properties: event.properties,
        sessionId: event.sessionId.substring(0, 8) + '...'
      })
    }

    // TODO: 実際の実装では以下を行う
    // 1. Google Analyticsに送信
    // 2. Mixpanelに送信
    // 3. 内部データベースに保存
    // 4. リアルタイムダッシュボードに反映

    // 重要なイベントは特別に処理
    const importantEvents = ['purchase', 'signup', 'error', 'crash']
    if (importantEvents.includes(event.event)) {
      console.log('🔔 Important event:', event)
      // await notifyImportantEvent(event)
    }

    return NextResponse.json({
      success: true,
      message: 'イベントを記録しました'
    })
  } catch (error) {
    console.error('Analytics tracking error:', error)
    return NextResponse.json(
      { error: 'イベントの記録に失敗しました' },
      { status: 500 }
    )
  }
}

export async function GET(request: NextRequest) {
  try {
    // クエリパラメータを取得
    const { searchParams } = new URL(request.url)
    const event = searchParams.get('event')
    const userId = searchParams.get('userId')
    const sessionId = searchParams.get('sessionId')
    const startDate = searchParams.get('startDate')
    const endDate = searchParams.get('endDate')

    // フィルタリング
    let filtered = [...eventStore]
    
    if (event) {
      filtered = filtered.filter(e => e.event === event)
    }
    
    if (userId) {
      filtered = filtered.filter(e => e.userId === userId)
    }
    
    if (sessionId) {
      filtered = filtered.filter(e => e.sessionId === sessionId)
    }
    
    if (startDate) {
      const start = new Date(startDate).getTime()
      filtered = filtered.filter(e => 
        new Date(e.timestamp).getTime() >= start
      )
    }
    
    if (endDate) {
      const end = new Date(endDate).getTime()
      filtered = filtered.filter(e => 
        new Date(e.timestamp).getTime() <= end
      )
    }

    // イベント統計
    const eventCounts: Record<string, number> = {}
    eventStore.forEach(e => {
      eventCounts[e.event] = (eventCounts[e.event] || 0) + 1
    })

    // セッション統計
    const uniqueSessions = new Set(eventStore.map(e => e.sessionId)).size
    const uniqueUsers = new Set(eventStore.filter(e => e.userId).map(e => e.userId)).size

    return NextResponse.json({
      events: filtered,
      total: filtered.length,
      stats: {
        totalEvents: eventStore.length,
        uniqueSessions,
        uniqueUsers,
        eventCounts,
        topEvents: Object.entries(eventCounts)
          .sort(([, a], [, b]) => b - a)
          .slice(0, 10)
          .map(([event, count]) => ({ event, count }))
      }
    })
  } catch (error) {
    console.error('Analytics fetch error:', error)
    return NextResponse.json(
      { error: 'アナリティクスデータの取得に失敗しました' },
      { status: 500 }
    )
  }
}