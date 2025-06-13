import { NextRequest, NextResponse } from 'next/server'
import { routines } from '../route'

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const routine = routines.find(r => r.id === params.id)
    
    if (!routine) {
      return NextResponse.json(
        { error: 'ルーティンが見つかりません' },
        { status: 404 }
      )
    }

    return NextResponse.json(routine)
  } catch (error) {
    console.error('Routine fetch error:', error)
    return NextResponse.json(
      { error: 'ルーティンの取得に失敗しました' },
      { status: 500 }
    )
  }
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const body = await request.json()
    const index = routines.findIndex(r => r.id === params.id)
    
    if (index === -1) {
      return NextResponse.json(
        { error: 'ルーティンが見つかりません' },
        { status: 404 }
      )
    }

    // バリデーション
    if (!body.name || !body.exercises || body.exercises.length === 0) {
      return NextResponse.json(
        { error: '必要な情報が不足しています' },
        { status: 400 }
      )
    }

    // ルーティンを更新
    routines[index] = {
      ...routines[index],
      ...body,
      id: params.id,
      updated_at: new Date().toISOString(),
    }

    return NextResponse.json(routines[index])
  } catch (error) {
    console.error('Routine update error:', error)
    return NextResponse.json(
      { error: 'ルーティンの更新に失敗しました' },
      { status: 500 }
    )
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const index = routines.findIndex(r => r.id === params.id)
    
    if (index === -1) {
      return NextResponse.json(
        { error: 'ルーティンが見つかりません' },
        { status: 404 }
      )
    }

    // TODO: 実際のプロジェクトでは、ユーザー認証と所有権の確認を実装
    // 現在のユーザーがこのルーティンを削除する権限があるか確認

    // ルーティンを削除
    routines.splice(index, 1)

    return NextResponse.json(
      { message: 'ルーティンを削除しました' },
      { status: 200 }
    )
  } catch (error) {
    console.error('Routine deletion error:', error)
    return NextResponse.json(
      { error: 'ルーティンの削除に失敗しました' },
      { status: 500 }
    )
  }
}