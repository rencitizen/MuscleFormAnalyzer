'use client'

import dynamic from 'next/dynamic'
import { Skeleton } from '../ui/skeleton'

// MediaPipeを使用するコンポーネントを動的インポート
const BodyMeasurementUpload = dynamic(
  () => import('./BodyMeasurementUpload'),
  {
    loading: () => (
      <div className="w-full h-[500px] flex items-center justify-center">
        <Skeleton className="h-full w-full" />
      </div>
    ),
    ssr: false
  }
)

const ImprovedBodyMeasurementUpload = dynamic(
  () => import('./ImprovedBodyMeasurementUpload'),
  {
    loading: () => (
      <div className="w-full h-[500px] flex items-center justify-center">
        <Skeleton className="h-full w-full" />
      </div>
    ),
    ssr: false
  }
)

export { BodyMeasurementUpload, ImprovedBodyMeasurementUpload }