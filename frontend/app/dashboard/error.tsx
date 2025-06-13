'use client'

import { useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { AlertCircle } from 'lucide-react'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error(error)
  }, [error])

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
        <AlertCircle className="w-12 h-12 text-destructive mb-4" />
        <h2 className="text-2xl font-bold mb-2">エラーが発生しました</h2>
        <p className="text-muted-foreground mb-6 max-w-md">
          統計データの読み込み中にエラーが発生しました。
          もう一度お試しください。
        </p>
        <div className="flex gap-4">
          <Button onClick={reset}>再試行</Button>
          <Button variant="outline" onClick={() => window.location.href = '/'}>
            ホームに戻る
          </Button>
        </div>
      </div>
    </div>
  )
}