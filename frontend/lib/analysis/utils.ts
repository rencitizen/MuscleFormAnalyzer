import { Landmark } from '@/lib/mediapipe/types'

/**
 * 3点間の角度を計算
 * @param a 始点
 * @param b 頂点
 * @param c 終点
 * @returns 角度（度）
 */
export function calculateAngle(a: Landmark, b: Landmark, c: Landmark): number {
  const radians = Math.atan2(c.y - b.y, c.x - b.x) - Math.atan2(a.y - b.y, a.x - b.x)
  let angle = Math.abs((radians * 180) / Math.PI)
  
  if (angle > 180) {
    angle = 360 - angle
  }
  
  return angle
}

/**
 * 2点間の距離を計算
 * @param a 点1
 * @param b 点2
 * @returns 距離
 */
export function getDistance(a: Landmark, b: Landmark): number {
  const dx = a.x - b.x
  const dy = a.y - b.y
  const dz = a.z - b.z
  return Math.sqrt(dx * dx + dy * dy + dz * dz)
}

/**
 * 2点間の2D距離を計算（Z軸を無視）
 * @param a 点1
 * @param b 点2
 * @returns 2D距離
 */
export function getDistance2D(a: Landmark, b: Landmark): number {
  const dx = a.x - b.x
  const dy = a.y - b.y
  return Math.sqrt(dx * dx + dy * dy)
}

/**
 * ランドマークの中点を計算
 * @param a 点1
 * @param b 点2
 * @returns 中点
 */
export function getMidpoint(a: Landmark, b: Landmark): Landmark {
  return {
    x: (a.x + b.x) / 2,
    y: (a.y + b.y) / 2,
    z: (a.z + b.z) / 2,
    visibility: (a.visibility || 0 + (b.visibility || 0)) / 2,
  }
}

/**
 * ベクトルの正規化
 * @param vector ベクトル
 * @returns 正規化されたベクトル
 */
export function normalizeVector(vector: { x: number; y: number; z: number }): {
  x: number
  y: number
  z: number
} {
  const magnitude = Math.sqrt(vector.x ** 2 + vector.y ** 2 + vector.z ** 2)
  
  if (magnitude === 0) {
    return { x: 0, y: 0, z: 0 }
  }
  
  return {
    x: vector.x / magnitude,
    y: vector.y / magnitude,
    z: vector.z / magnitude,
  }
}

/**
 * 2つのベクトルの内積を計算
 * @param a ベクトル1
 * @param b ベクトル2
 * @returns 内積
 */
export function dotProduct(
  a: { x: number; y: number; z: number },
  b: { x: number; y: number; z: number }
): number {
  return a.x * b.x + a.y * b.y + a.z * b.z
}

/**
 * 移動平均を計算
 * @param values 値の配列
 * @param windowSize ウィンドウサイズ
 * @returns 移動平均の配列
 */
export function movingAverage(values: number[], windowSize: number): number[] {
  const result: number[] = []
  
  for (let i = 0; i < values.length; i++) {
    const start = Math.max(0, i - Math.floor(windowSize / 2))
    const end = Math.min(values.length, i + Math.floor(windowSize / 2) + 1)
    const window = values.slice(start, end)
    const avg = window.reduce((sum, val) => sum + val, 0) / window.length
    result.push(avg)
  }
  
  return result
}

/**
 * 時系列データのピークを検出
 * @param values 値の配列
 * @param threshold 閾値
 * @returns ピークのインデックス配列
 */
export function findPeaks(values: number[], threshold: number = 0.1): number[] {
  const peaks: number[] = []
  
  for (let i = 1; i < values.length - 1; i++) {
    const prev = values[i - 1]
    const curr = values[i]
    const next = values[i + 1]
    
    if (curr > prev + threshold && curr > next + threshold) {
      peaks.push(i)
    }
  }
  
  return peaks
}

/**
 * 時系列データの谷を検出
 * @param values 値の配列
 * @param threshold 閾値
 * @returns 谷のインデックス配列
 */
export function findValleys(values: number[], threshold: number = 0.1): number[] {
  const valleys: number[] = []
  
  for (let i = 1; i < values.length - 1; i++) {
    const prev = values[i - 1]
    const curr = values[i]
    const next = values[i + 1]
    
    if (curr < prev - threshold && curr < next - threshold) {
      valleys.push(i)
    }
  }
  
  return valleys
}