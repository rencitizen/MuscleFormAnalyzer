import { NextRequest, NextResponse } from 'next/server'

// モックデータストア
export let sessions: any[] = []

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const start_date = searchParams.get('start_date')
    const end_date = searchParams.get('end_date')

    let filteredSessions = sessions

    if (start_date && end_date) {
      filteredSessions = sessions.filter(session => {
        const sessionDate = new Date(session.date)
        return sessionDate >= new Date(start_date) && sessionDate <= new Date(end_date)
      })
    } else if (start_date) {
      filteredSessions = sessions.filter(session => {
        return new Date(session.date) >= new Date(start_date)
      })
    }

    return NextResponse.json(filteredSessions)
  } catch (error) {
    console.error('Sessions fetch error:', error)
    return NextResponse.json(
      { error: 'セッションの取得に失敗しました' },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    const newSession = {
      id: Date.now().toString(),
      routine_id: body.routine_id || null,
      date: new Date().toISOString(),
      start_time: new Date().toISOString(),
      sets: [],
      status: 'active',
    }

    sessions.push(newSession)

    return NextResponse.json(newSession)
  } catch (error) {
    console.error('Session creation error:', error)
    return NextResponse.json(
      { error: 'セッションの作成に失敗しました' },
      { status: 500 }
    )
  }
}