'use client'

import dynamic from 'next/dynamic'
import { Skeleton } from './ui/skeleton'

// MediaPipe関連のコンポーネント
export const PoseAnalyzerEnhanced = dynamic(
  () => import('./pose-analysis/PoseAnalyzerEnhanced'),
  {
    loading: () => <Skeleton className="h-[600px] w-full" />,
    ssr: false
  }
)

export const RealtimeCameraAnalysis = dynamic(
  () => import('./camera/RealtimeCameraAnalysis'),
  {
    loading: () => <Skeleton className="h-[400px] w-full" />,
    ssr: false
  }
)

// グラフ/チャート関連のコンポーネント
export const ScientificMetrics = dynamic(
  () => import('./dashboard/ScientificMetrics'),
  {
    loading: () => <Skeleton className="h-[300px] w-full" />,
    ssr: false
  }
)

export const AdaptiveProgressTracker = dynamic(
  () => import('./training/AdaptiveProgressTracker'),
  {
    loading: () => <Skeleton className="h-[400px] w-full" />,
    ssr: false
  }
)

export const NutritionDashboard = dynamic(
  () => import('./nutrition/NutritionDashboard'),
  {
    loading: () => <Skeleton className="h-[500px] w-full" />,
    ssr: false
  }
)

// 重いデータ処理コンポーネント
export const ComprehensiveDashboard = dynamic(
  () => import('./dashboard/ComprehensiveDashboard'),
  {
    loading: () => <Skeleton className="h-[600px] w-full" />,
    ssr: false
  }
)

export const ComprehensiveAnalysisDashboard = dynamic(
  () => import('./v3/ComprehensiveAnalysisDashboard'),
  {
    loading: () => <Skeleton className="h-[800px] w-full" />,
    ssr: false
  }
)