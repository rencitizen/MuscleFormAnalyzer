/**
 * MediaPipe utility functions for better initialization and error handling
 */

import { Pose } from '@mediapipe/pose'

interface InitializationOptions {
  maxRetries?: number
  retryDelay?: number
  onRetry?: (attempt: number) => void
}

/**
 * Initialize MediaPipe Pose with retry logic
 */
export async function initializeMediaPipePose(
  options: InitializationOptions = {}
): Promise<Pose> {
  const {
    maxRetries = 3,
    retryDelay = 1000,
    onRetry
  } = options

  let lastError: Error | null = null

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const pose = new Pose({
        locateFile: (file) => {
          return `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`
        }
      })

      // Configure pose detector
      pose.setOptions({
        modelComplexity: 2,
        smoothLandmarks: true,
        enableSegmentation: false,
        smoothSegmentation: false,
        minDetectionConfidence: 0.5,
        minTrackingConfidence: 0.5
      })

      // Initialize and verify
      await pose.initialize()
      
      // Test if pose is working by sending a dummy image
      const testCanvas = document.createElement('canvas')
      testCanvas.width = 100
      testCanvas.height = 100
      const ctx = testCanvas.getContext('2d')
      if (ctx) {
        ctx.fillStyle = 'white'
        ctx.fillRect(0, 0, 100, 100)
      }

      // Send test image with timeout
      const testPromise = new Promise((resolve, reject) => {
        const timeout = setTimeout(() => {
          reject(new Error('Pose initialization test timeout'))
        }, 5000)

        pose.onResults(() => {
          clearTimeout(timeout)
          resolve(true)
        })

        pose.send({ image: testCanvas }).catch(reject)
      })

      await testPromise

      console.log('MediaPipe Pose initialized successfully')
      return pose

    } catch (error) {
      lastError = error as Error
      console.error(`MediaPipe initialization attempt ${attempt} failed:`, error)

      if (attempt < maxRetries) {
        if (onRetry) {
          onRetry(attempt)
        }
        await new Promise(resolve => setTimeout(resolve, retryDelay * attempt))
      }
    }
  }

  throw new Error(
    `Failed to initialize MediaPipe after ${maxRetries} attempts. Last error: ${lastError?.message}`
  )
}

/**
 * Check if MediaPipe models are cached
 */
export async function checkMediaPipeCache(): Promise<boolean> {
  try {
    if ('caches' in window) {
      const cacheNames = await caches.keys()
      return cacheNames.some(name => 
        name.includes('mediapipe') || 
        name.includes('jsdelivr')
      )
    }
  } catch (error) {
    console.error('Failed to check cache:', error)
  }
  return false
}

/**
 * Preload MediaPipe models
 */
export async function preloadMediaPipeModels(): Promise<void> {
  const modelFiles = [
    'pose_landmark_full.tflite',
    'pose_web.binarypb',
    'pose_solution_packed_assets.data',
    'pose_solution_packed_assets_loader.js',
    'pose_solution_simd_wasm_bin.wasm',
    'pose_solution_packed_assets_loader.js'
  ]

  const baseUrl = 'https://cdn.jsdelivr.net/npm/@mediapipe/pose/'

  // Preload model files
  const preloadPromises = modelFiles.map(async (file) => {
    try {
      const response = await fetch(baseUrl + file)
      if (response.ok) {
        // Just fetch to populate browser cache
        await response.blob()
      }
    } catch (error) {
      console.warn(`Failed to preload ${file}:`, error)
    }
  })

  await Promise.allSettled(preloadPromises)
}

/**
 * Get device capabilities for optimization
 */
export function getDeviceCapabilities() {
  const memory = (navigator as any).deviceMemory || 4 // GB
  const cores = navigator.hardwareConcurrency || 4
  const connection = (navigator as any).connection

  const isLowEndDevice = memory < 4 || cores < 4
  const isSlowConnection = connection?.effectiveType === '2g' || 
                          connection?.effectiveType === 'slow-2g'

  return {
    memory,
    cores,
    isLowEndDevice,
    isSlowConnection,
    recommendedSettings: {
      modelComplexity: isLowEndDevice ? 0 : 2,
      maxFrames: isLowEndDevice ? 15 : 30,
      frameSkip: isLowEndDevice ? 3 : 1
    }
  }
}

/**
 * Memory cleanup helper
 */
export function cleanupMediaPipeResources(pose: Pose | null) {
  if (pose) {
    try {
      pose.close()
    } catch (error) {
      console.error('Error closing pose detector:', error)
    }
  }

  // Force garbage collection if available (Chrome DevTools)
  if ((window as any).gc) {
    (window as any).gc()
  }
}