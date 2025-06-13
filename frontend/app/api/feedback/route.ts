import { NextRequest, NextResponse } from 'next/server'

interface FeedbackData {
  type: 'bug' | 'feature' | 'usability' | 'other'
  severity: 'low' | 'medium' | 'high'
  description: string
  screenshot?: string
  userAgent: string
  timestamp: string
  userId?: string
  pageUrl: string
  sessionId: string
}

// In-memory storage for demo purposes
// TODO: 実際の実装では、データベースに保存
const feedbackStore: FeedbackData[] = []

export async function POST(request: NextRequest) {
  try {
    const body: FeedbackData = await request.json()
    
    // バリデーション
    if (!body.description || !body.type || !body.sessionId) {
      return NextResponse.json(
        { error: '必須項目が不足しています' },
        { status: 400 }
      )
    }

    // フィードバックを保存
    const feedback: FeedbackData = {
      ...body,
      timestamp: new Date().toISOString()
    }
    
    feedbackStore.push(feedback)

    // 開発環境ではコンソールに出力
    if (process.env.NODE_ENV === 'development') {
      console.log('📝 New Feedback:', {
        type: feedback.type,
        severity: feedback.severity,
        description: feedback.description.substring(0, 100) + '...',
        pageUrl: feedback.pageUrl
      })
    }

    // TODO: 実際の実装では以下を行う
    // 1. データベースに保存
    // 2. Slackやメールで通知
    // 3. 重要度が高い場合は即座にアラート
    // 4. スクリーンショットをクラウドストレージに保存

    // 高優先度のバグは即座に通知
    if (feedback.type === 'bug' && feedback.severity === 'high') {
      // await sendUrgentNotification(feedback)
      console.warn('🚨 High priority bug reported:', feedback.description)
    }

    return NextResponse.json({
      success: true,
      message: 'フィードバックを受け付けました',
      id: `fb-${Date.now()}`
    })
  } catch (error) {
    console.error('Feedback submission error:', error)
    return NextResponse.json(
      { error: 'フィードバックの送信に失敗しました' },
      { status: 500 }
    )
  }
}

export async function GET(request: NextRequest) {
  try {
    // クエリパラメータを取得
    const { searchParams } = new URL(request.url)
    const type = searchParams.get('type')
    const severity = searchParams.get('severity')
    const limit = parseInt(searchParams.get('limit') || '50')
    const offset = parseInt(searchParams.get('offset') || '0')

    // フィルタリング
    let filtered = [...feedbackStore]
    
    if (type) {
      filtered = filtered.filter(fb => fb.type === type)
    }
    
    if (severity) {
      filtered = filtered.filter(fb => fb.severity === severity)
    }

    // ソート（最新順）
    filtered.sort((a, b) => 
      new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    )

    // ページネーション
    const total = filtered.length
    const items = filtered.slice(offset, offset + limit)

    // 統計情報
    const stats = {
      total: feedbackStore.length,
      byType: {
        bug: feedbackStore.filter(fb => fb.type === 'bug').length,
        feature: feedbackStore.filter(fb => fb.type === 'feature').length,
        usability: feedbackStore.filter(fb => fb.type === 'usability').length,
        other: feedbackStore.filter(fb => fb.type === 'other').length
      },
      bySeverity: {
        high: feedbackStore.filter(fb => fb.severity === 'high').length,
        medium: feedbackStore.filter(fb => fb.severity === 'medium').length,
        low: feedbackStore.filter(fb => fb.severity === 'low').length
      }
    }

    return NextResponse.json({
      items,
      total,
      limit,
      offset,
      stats
    })
  } catch (error) {
    console.error('Feedback fetch error:', error)
    return NextResponse.json(
      { error: 'フィードバックの取得に失敗しました' },
      { status: 500 }
    )
  }
}