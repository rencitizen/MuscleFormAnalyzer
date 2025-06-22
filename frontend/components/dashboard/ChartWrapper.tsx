'use client'

import dynamic from 'next/dynamic'
import { Skeleton } from '../ui/skeleton'

// Rechartsコンポーネントを動的インポート
export const PieChart = dynamic(
  () => import('recharts').then(mod => mod.PieChart),
  { 
    loading: () => <Skeleton className="h-[200px] w-full" />,
    ssr: false 
  }
)

export const Pie = dynamic(
  () => import('recharts').then(mod => mod.Pie),
  { ssr: false }
)

export const Cell = dynamic(
  () => import('recharts').then(mod => mod.Cell),
  { ssr: false }
)

export const ResponsiveContainer = dynamic(
  () => import('recharts').then(mod => mod.ResponsiveContainer),
  { ssr: false }
)

export const Legend = dynamic(
  () => import('recharts').then(mod => mod.Legend),
  { ssr: false }
)

export const Tooltip = dynamic(
  () => import('recharts').then(mod => mod.Tooltip),
  { ssr: false }
)

export const LineChart = dynamic(
  () => import('recharts').then(mod => mod.LineChart),
  { 
    loading: () => <Skeleton className="h-[300px] w-full" />,
    ssr: false 
  }
)

export const Line = dynamic(
  () => import('recharts').then(mod => mod.Line),
  { ssr: false }
)

export const XAxis = dynamic(
  () => import('recharts').then(mod => mod.XAxis),
  { ssr: false }
)

export const YAxis = dynamic(
  () => import('recharts').then(mod => mod.YAxis),
  { ssr: false }
)

export const CartesianGrid = dynamic(
  () => import('recharts').then(mod => mod.CartesianGrid),
  { ssr: false }
)

export const BarChart = dynamic(
  () => import('recharts').then(mod => mod.BarChart),
  { 
    loading: () => <Skeleton className="h-[300px] w-full" />,
    ssr: false 
  }
)

export const Bar = dynamic(
  () => import('recharts').then(mod => mod.Bar),
  { ssr: false }
)

export const RadarChart = dynamic(
  () => import('recharts').then(mod => mod.RadarChart),
  { 
    loading: () => <Skeleton className="h-[300px] w-full" />,
    ssr: false 
  }
)

export const Radar = dynamic(
  () => import('recharts').then(mod => mod.Radar),
  { ssr: false }
)

export const PolarGrid = dynamic(
  () => import('recharts').then(mod => mod.PolarGrid),
  { ssr: false }
)

export const PolarAngleAxis = dynamic(
  () => import('recharts').then(mod => mod.PolarAngleAxis),
  { ssr: false }
)

export const PolarRadiusAxis = dynamic(
  () => import('recharts').then(mod => mod.PolarRadiusAxis),
  { ssr: false }
)