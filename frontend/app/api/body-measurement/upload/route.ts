import { NextRequest, NextResponse } from 'next/server'
import { writeFile, mkdir } from 'fs/promises'
import { join } from 'path'
import { existsSync } from 'fs'

// 対応する動画形式のMIMEタイプ
const ACCEPTED_VIDEO_TYPES = [
  'video/mp4',
  'video/quicktime',
  'video/x-msvideo',
  'video/webm',
  'video/mpeg',
  'video/ogg',
  'video/3gpp',
  'video/3gpp2'
]

const MAX_FILE_SIZE = 100 * 1024 * 1024 // 100MB

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const video = formData.get('video') as File
    const measurementType = formData.get('measurementType') as string

    // ファイルの検証
    if (!video) {
      return NextResponse.json(
        { error: '動画ファイルが見つかりません' },
        { status: 400 }
      )
    }

    // ファイルタイプの検証
    if (!ACCEPTED_VIDEO_TYPES.includes(video.type)) {
      return NextResponse.json(
        { error: '対応していないファイル形式です' },
        { status: 400 }
      )
    }

    // ファイルサイズの検証
    if (video.size > MAX_FILE_SIZE) {
      return NextResponse.json(
        { error: 'ファイルサイズは100MB以下にしてください' },
        { status: 400 }
      )
    }

    // 一時ファイルとして保存
    const bytes = await video.arrayBuffer()
    const buffer = Buffer.from(bytes)

    // アップロードディレクトリの作成
    const uploadDir = join(process.cwd(), 'public', 'uploads', 'body-measurements')
    if (!existsSync(uploadDir)) {
      await mkdir(uploadDir, { recursive: true })
    }

    // ユニークなファイル名を生成
    const fileName = `${Date.now()}-${Math.random().toString(36).substring(7)}-${video.name}`
    const filePath = join(uploadDir, fileName)

    // ファイルを保存
    await writeFile(filePath, buffer)

    // MediaPipeを使用して身体測定を実行
    // Note: 実際のMediaPipe処理はクライアントサイドで実行する必要があるため、
    // ここではモックデータを返す。実際の実装では、クライアントサイドで
    // processVideoForBodyMeasurements関数を使用する

    const mockMeasurements = generateMockMeasurements()

    // 処理が完了したら一時ファイルを削除
    // 実際の実装では非同期で削除
    // setTimeout(() => {
    //   unlink(filePath).catch(console.error)
    // }, 60000)

    return NextResponse.json({
      success: true,
      measurements: mockMeasurements,
      metadata: {
        fileName: video.name,
        fileSize: video.size,
        processingTime: Math.random() * 3000 + 2000, // 2-5秒のランダムな処理時間
        confidence: 0.85 + Math.random() * 0.1 // 85-95%の信頼度
      }
    })

  } catch (error) {
    console.error('Body measurement upload error:', error)
    return NextResponse.json(
      { error: '動画の処理中にエラーが発生しました' },
      { status: 500 }
    )
  }
}

// モックの測定結果を生成
function generateMockMeasurements() {
  const baseMeasurements = {
    height: 175 + Math.random() * 10 - 5,
    shoulderWidth: 45 + Math.random() * 4 - 2,
    armLength: {
      left: 62 + Math.random() * 3 - 1.5,
      right: 62 + Math.random() * 3 - 1.5
    },
    legLength: {
      left: 95 + Math.random() * 4 - 2,
      right: 95 + Math.random() * 4 - 2
    },
    torsoLength: 50 + Math.random() * 3 - 1.5,
    hipWidth: 35 + Math.random() * 3 - 1.5,
    neckToShoulder: {
      left: 15 + Math.random() * 2 - 1,
      right: 15 + Math.random() * 2 - 1
    },
    upperArmLength: {
      left: 32 + Math.random() * 2 - 1,
      right: 32 + Math.random() * 2 - 1
    },
    forearmLength: {
      left: 28 + Math.random() * 2 - 1,
      right: 28 + Math.random() * 2 - 1
    },
    thighLength: {
      left: 45 + Math.random() * 3 - 1.5,
      right: 45 + Math.random() * 3 - 1.5
    },
    shinLength: {
      left: 42 + Math.random() * 3 - 1.5,
      right: 42 + Math.random() * 3 - 1.5
    }
  }

  // 小数点第1位で丸める
  const roundMeasurements = (obj: any): any => {
    if (typeof obj === 'number') {
      return Math.round(obj * 10) / 10
    }
    if (typeof obj === 'object') {
      const rounded: any = {}
      for (const key in obj) {
        rounded[key] = roundMeasurements(obj[key])
      }
      return rounded
    }
    return obj
  }

  return {
    ...roundMeasurements(baseMeasurements),
    timestamp: new Date().toISOString(),
    measurementId: `BM-${Date.now()}-${Math.random().toString(36).substring(7)}`
  }
}