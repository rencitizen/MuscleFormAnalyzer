import { NextRequest, NextResponse } from 'next/server'
import { sessions } from '../route'

export async function PATCH(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const body = await request.json()
    const session = sessions.find(s => s.id === params.id)
    
    if (!session) {
      return NextResponse.json(
        { error: 'セッションが見つかりません' },
        { status: 404 }
      )
    }

    // セッション状態を更新
    if (body.status) {
      session.status = body.status
      if (body.status === 'completed') {
        session.end_time = new Date().toISOString()
      }
    }

    return NextResponse.json(session)
  } catch (error) {
    console.error('Session update error:', error)
    return NextResponse.json(
      { error: 'セッションの更新に失敗しました' },
      { status: 500 }
    )
  }
}