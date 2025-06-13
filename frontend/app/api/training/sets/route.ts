import { NextRequest, NextResponse } from 'next/server'
import { sessions } from '../sessions/route'

// モックデータストア（実際のプロジェクトではデータベースを使用）
let sets: any[] = []

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    if (!body.session_id || !body.exercise_name || body.weight === undefined || body.reps === undefined) {
      return NextResponse.json(
        { error: '必要な情報が不足しています' },
        { status: 400 }
      )
    }

    // セッションを探す
    const session = sessions.find(s => s.id === body.session_id)
    if (!session) {
      return NextResponse.json(
        { error: 'セッションが見つかりません' },
        { status: 404 }
      )
    }

    const newSet = {
      id: Date.now().toString(),
      session_id: body.session_id,
      exercise_name: body.exercise_name,
      set_number: body.set_number,
      weight: body.weight,
      reps: body.reps,
      completed: true,
      created_at: new Date().toISOString(),
    }

    // セッションにセットを追加
    session.sets.push(newSet)
    sets.push(newSet)

    return NextResponse.json(newSet)
  } catch (error) {
    console.error('Set creation error:', error)
    return NextResponse.json(
      { error: 'セットの記録に失敗しました' },
      { status: 500 }
    )
  }
}