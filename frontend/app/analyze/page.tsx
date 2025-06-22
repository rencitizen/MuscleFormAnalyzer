'use client'

import dynamic from 'next/dynamic'
import { Skeleton } from '@/components/ui/skeleton'

// MediaPipeを使用するページを動的インポート
const AnalyzeContent = dynamic(
  () => import('./page-original'),
  {
    loading: () => (
      <div className="container mx-auto px-4 py-8">
        <div className="mb-6">
          <Skeleton className="h-8 w-48 mb-2" />
          <Skeleton className="h-4 w-96" />
        </div>
        <Skeleton className="h-[600px] w-full" />
      </div>
    ),
    ssr: false
  }
)

export default function AnalyzePage() {
  return <AnalyzeContent />
}