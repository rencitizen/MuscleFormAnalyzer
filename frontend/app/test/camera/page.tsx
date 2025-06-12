import dynamic from 'next/dynamic'
import { Suspense } from 'react'

// Dynamic import with SSR disabled for camera functionality
const CameraTestComponent = dynamic(
  () => import('./CameraTestComponent'),
  { 
    ssr: false,
    loading: () => (
      <div className="container mx-auto p-4 max-w-4xl">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-6"></div>
          <div className="space-y-6">
            <div className="h-48 bg-gray-200 rounded"></div>
            <div className="h-48 bg-gray-200 rounded"></div>
            <div className="h-48 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    )
  }
)

export default function CameraTestPage() {
  return (
    <Suspense fallback={
      <div className="container mx-auto p-4 max-w-4xl">
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading camera test...</p>
        </div>
      </div>
    }>
      <CameraTestComponent />
    </Suspense>
  )
}