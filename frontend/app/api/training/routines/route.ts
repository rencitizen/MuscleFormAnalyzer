import { NextRequest, NextResponse } from 'next/server'
import { auth } from '../../../../lib/firebase'

// モックデータストア（実際のプロジェクトではデータベースを使用）
let routines: any[] = [
  {
    id: '1',
    name: '胸・肩・上腕三頭筋',
    description: 'プッシュ系の日',
    exercises: [
      { exercise_name: 'ベンチプレス', target_sets: 4, target_reps: '8-10', target_weight: 80, rest_time: 120, order_index: 0 },
      { exercise_name: 'インクラインダンベルプレス', target_sets: 3, target_reps: '10-12', target_weight: 30, rest_time: 90, order_index: 1 },
      { exercise_name: 'ショルダープレス', target_sets: 3, target_reps: '10-12', target_weight: 50, rest_time: 90, order_index: 2 },
      { exercise_name: 'サイドレイズ', target_sets: 3, target_reps: '12-15', target_weight: 10, rest_time: 60, order_index: 3 },
      { exercise_name: 'トライセプスエクステンション', target_sets: 3, target_reps: '12-15', target_weight: 30, rest_time: 60, order_index: 4 },
    ]
  },
  {
    id: '2',
    name: '背中・上腕二頭筋',
    description: 'プル系の日',
    exercises: [
      { exercise_name: 'デッドリフト', target_sets: 4, target_reps: '6-8', target_weight: 100, rest_time: 180, order_index: 0 },
      { exercise_name: 'ラットプルダウン', target_sets: 3, target_reps: '10-12', target_weight: 60, rest_time: 90, order_index: 1 },
      { exercise_name: 'ベントオーバーロー', target_sets: 3, target_reps: '10-12', target_weight: 60, rest_time: 90, order_index: 2 },
      { exercise_name: 'バーベルカール', target_sets: 3, target_reps: '10-12', target_weight: 30, rest_time: 60, order_index: 3 },
      { exercise_name: 'ハンマーカール', target_sets: 3, target_reps: '12-15', target_weight: 12, rest_time: 60, order_index: 4 },
    ]
  },
  {
    id: '3',
    name: '脚・腹筋',
    description: '下半身の日',
    exercises: [
      { exercise_name: 'スクワット', target_sets: 4, target_reps: '8-10', target_weight: 90, rest_time: 180, order_index: 0 },
      { exercise_name: 'レッグプレス', target_sets: 3, target_reps: '12-15', target_weight: 140, rest_time: 90, order_index: 1 },
      { exercise_name: 'レッグカール', target_sets: 3, target_reps: '12-15', target_weight: 40, rest_time: 60, order_index: 2 },
      { exercise_name: 'カーフレイズ', target_sets: 3, target_reps: '15-20', target_weight: 80, rest_time: 60, order_index: 3 },
      { exercise_name: 'プランク', target_sets: 3, target_reps: '60秒', rest_time: 60, order_index: 4 },
    ]
  }
]

export async function GET(request: NextRequest) {
  try {
    // TODO: 実際のプロジェクトではユーザー認証とデータベースクエリを実装
    return NextResponse.json(routines)
  } catch (error) {
    console.error('Routines fetch error:', error)
    return NextResponse.json(
      { error: 'ルーティンの取得に失敗しました' },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    // バリデーション
    if (!body.name || !body.exercises || body.exercises.length === 0) {
      return NextResponse.json(
        { error: '必要な情報が不足しています' },
        { status: 400 }
      )
    }

    // 新しいルーティンを作成
    const newRoutine = {
      id: Date.now().toString(),
      ...body,
      created_at: new Date().toISOString(),
    }

    routines.push(newRoutine)

    return NextResponse.json(newRoutine)
  } catch (error) {
    console.error('Routine creation error:', error)
    return NextResponse.json(
      { error: 'ルーティンの作成に失敗しました' },
      { status: 500 }
    )
  }
}