'use client'

import dynamic from 'next/dynamic'
import { Skeleton } from '@/components/ui/skeleton'

// 重いMediaPipeを使用するページを動的インポート
const PoseAnalysisContent = dynamic(
  () => import('./page-original'),
  {
    loading: () => (
      <div className="container mx-auto px-4 py-8">
        <div className="mb-6">
          <Skeleton className="h-8 w-48 mb-2" />
          <Skeleton className="h-4 w-96" />
        </div>
        <div className="grid gap-6 lg:grid-cols-3">
          <Skeleton className="h-[400px]" />
          <Skeleton className="lg:col-span-2 h-[400px]" />
        </div>
      </div>
    ),
    ssr: false
  }
)

export default function PoseAnalysisPage() {
  return <PoseAnalysisContent />
}