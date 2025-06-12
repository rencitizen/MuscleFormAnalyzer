import { NextRequest, NextResponse } from 'next/server'

// モックデータストア（実際のプロジェクトではデータベースを使用）
import { sessions } from '../route'

export async function GET(request: NextRequest) {
  try {
    // アクティブなセッションを探す
    const activeSession = sessions.find(session => session.status === 'active')
    
    if (activeSession) {
      return NextResponse.json(activeSession)
    } else {
      return NextResponse.json(null)
    }
  } catch (error) {
    console.error('Active session fetch error:', error)
    return NextResponse.json(
      { error: 'アクティブセッションの取得に失敗しました' },
      { status: 500 }
    )
  }
}