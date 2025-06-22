'use client'

import dynamic from 'next/dynamic'
import { Skeleton } from '@/components/ui/skeleton'

// Rechartsを使用するページを動的インポート
const ProgressContent = dynamic(
  () => import('./page-original'),
  {
    loading: () => (
      <div className="container mx-auto px-4 py-8">
        <div className="mb-6">
          <Skeleton className="h-8 w-48 mb-2" />
          <Skeleton className="h-4 w-96" />
        </div>
        <div className="grid gap-6">
          <Skeleton className="h-[300px]" />
          <div className="grid gap-4 md:grid-cols-2">
            <Skeleton className="h-[200px]" />
            <Skeleton className="h-[200px]" />
          </div>
        </div>
      </div>
    ),
    ssr: false
  }
)

export default function ProgressPage() {
  return <ProgressContent />
}