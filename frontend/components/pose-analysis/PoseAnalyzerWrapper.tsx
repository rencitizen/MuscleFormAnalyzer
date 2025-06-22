'use client'

import dynamic from 'next/dynamic'
import { Skeleton } from '../ui/skeleton'

// MediaPipeを使用するコンポーネントを動的インポート
const PoseAnalyzerEnhanced = dynamic(
  () => import('./PoseAnalyzerEnhanced'),
  {
    loading: () => (
      <div className="w-full h-[600px] flex items-center justify-center">
        <div className="space-y-4">
          <Skeleton className="h-[400px] w-[600px]" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-3/4" />
        </div>
      </div>
    ),
    ssr: false, // サーバーサイドレンダリングを無効化
  }
)

export { PoseAnalyzerEnhanced }