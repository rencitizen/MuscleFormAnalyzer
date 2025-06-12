import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const video = formData.get('video') as File
    const exercise = formData.get('exercise') as string

    if (!video) {
      return NextResponse.json(
        { error: '動画ファイルが見つかりません' },
        { status: 400 }
      )
    }

    // ファイルサイズチェック
    if (video.size > 100 * 1024 * 1024) {
      return NextResponse.json(
        { error: 'ファイルサイズは100MB以下にしてください' },
        { status: 400 }
      )
    }

    // ファイルタイプチェック
    if (!video.type.startsWith('video/')) {
      return NextResponse.json(
        { error: '動画ファイルをアップロードしてください' },
        { status: 400 }
      )
    }

    // TODO: ここで実際の動画分析処理を実装
    // 1. 動画をバックエンドAPIに送信
    // 2. MediaPipeで分析
    // 3. 結果を返す

    // 一時的にモックデータを返す
    const mockFrames = []
    for (let i = 0; i < 30; i++) {
      mockFrames.push({
        poseLandmarks: generateMockLandmarks(),
        timestamp: i * 100,
      })
    }

    return NextResponse.json({
      success: true,
      exercise,
      frames: mockFrames,
      analysis: {
        formScore: 85,
        issues: ['膝が前に出すぎています', '背中をまっすぐに保ちましょう'],
        improvements: ['膝の位置を調整しました', '姿勢が改善されました'],
      }
    })
  } catch (error) {
    console.error('Upload error:', error)
    return NextResponse.json(
      { error: '動画の分析中にエラーが発生しました' },
      { status: 500 }
    )
  }
}

function generateMockLandmarks() {
  const landmarks = []
  for (let i = 0; i < 33; i++) {
    landmarks.push({
      x: 0.5 + Math.random() * 0.1 - 0.05,
      y: 0.5 + Math.random() * 0.1 - 0.05,
      z: 0,
      visibility: 1
    })
  }
  return landmarks
}