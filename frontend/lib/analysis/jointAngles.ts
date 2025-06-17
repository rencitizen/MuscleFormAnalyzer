import { NormalizedLandmark } from '@mediapipe/pose'

/**
 * 3点から角度を計算
 */
function calculateAngle(
  point1: NormalizedLandmark,
  point2: NormalizedLandmark,
  point3: NormalizedLandmark
): number {
  const radians = Math.atan2(point3.y - point2.y, point3.x - point2.x) -
                  Math.atan2(point1.y - point2.y, point1.x - point2.x)
  let angle = Math.abs(radians * 180.0 / Math.PI)
  
  if (angle > 180.0) {
    angle = 360 - angle
  }
  
  return angle
}

/**
 * エクササイズごとの主要な関節角度を計算
 */
export function calculateJointAngles(
  landmarks: NormalizedLandmark[],
  exercise: 'squat' | 'deadlift' | 'bench_press'
): Record<string, number> {
  const angles: Record<string, number> = {}

  // MediaPipeのランドマークインデックス
  const POSE_LANDMARKS = {
    LEFT_SHOULDER: 11,
    RIGHT_SHOULDER: 12,
    LEFT_ELBOW: 13,
    RIGHT_ELBOW: 14,
    LEFT_WRIST: 15,
    RIGHT_WRIST: 16,
    LEFT_HIP: 23,
    RIGHT_HIP: 24,
    LEFT_KNEE: 25,
    RIGHT_KNEE: 26,
    LEFT_ANKLE: 27,
    RIGHT_ANKLE: 28,
  }

  switch (exercise) {
    case 'squat':
      // 膝の角度
      angles.knee = calculateAngle(
        landmarks[POSE_LANDMARKS.LEFT_HIP],
        landmarks[POSE_LANDMARKS.LEFT_KNEE],
        landmarks[POSE_LANDMARKS.LEFT_ANKLE]
      )
      
      // 股関節の角度
      angles.hip = calculateAngle(
        landmarks[POSE_LANDMARKS.LEFT_SHOULDER],
        landmarks[POSE_LANDMARKS.LEFT_HIP],
        landmarks[POSE_LANDMARKS.LEFT_KNEE]
      )
      
      // 足首の角度
      angles.ankle = calculateAngle(
        landmarks[POSE_LANDMARKS.LEFT_KNEE],
        landmarks[POSE_LANDMARKS.LEFT_ANKLE],
        { 
          x: landmarks[POSE_LANDMARKS.LEFT_ANKLE].x,
          y: landmarks[POSE_LANDMARKS.LEFT_ANKLE].y - 0.1,
          z: landmarks[POSE_LANDMARKS.LEFT_ANKLE].z || 0,
          visibility: 1
        }
      )
      break

    case 'deadlift':
      // 背中の角度（垂直からの偏差）
      const shoulderToHip = Math.atan2(
        landmarks[POSE_LANDMARKS.LEFT_HIP].y - landmarks[POSE_LANDMARKS.LEFT_SHOULDER].y,
        landmarks[POSE_LANDMARKS.LEFT_HIP].x - landmarks[POSE_LANDMARKS.LEFT_SHOULDER].x
      )
      angles.back = Math.abs(shoulderToHip * 180 / Math.PI - 90)
      
      // 膝の角度
      angles.knee = calculateAngle(
        landmarks[POSE_LANDMARKS.LEFT_HIP],
        landmarks[POSE_LANDMARKS.LEFT_KNEE],
        landmarks[POSE_LANDMARKS.LEFT_ANKLE]
      )
      
      // 股関節の角度
      angles.hip = calculateAngle(
        landmarks[POSE_LANDMARKS.LEFT_SHOULDER],
        landmarks[POSE_LANDMARKS.LEFT_HIP],
        landmarks[POSE_LANDMARKS.LEFT_KNEE]
      )
      break

    case 'bench_press':
      // 肘の角度
      angles.elbow = calculateAngle(
        landmarks[POSE_LANDMARKS.LEFT_SHOULDER],
        landmarks[POSE_LANDMARKS.LEFT_ELBOW],
        landmarks[POSE_LANDMARKS.LEFT_WRIST]
      )
      
      // 肩の角度（体幹との角度）
      angles.shoulder = calculateAngle(
        landmarks[POSE_LANDMARKS.LEFT_HIP],
        landmarks[POSE_LANDMARKS.LEFT_SHOULDER],
        landmarks[POSE_LANDMARKS.LEFT_ELBOW]
      )
      
      // 手首の角度
      const wristToElbow = Math.atan2(
        landmarks[POSE_LANDMARKS.LEFT_ELBOW].y - landmarks[POSE_LANDMARKS.LEFT_WRIST].y,
        landmarks[POSE_LANDMARKS.LEFT_ELBOW].x - landmarks[POSE_LANDMARKS.LEFT_WRIST].x
      )
      angles.wrist = Math.abs(wristToElbow * 180 / Math.PI)
      break
  }

  return angles
}

/**
 * 関節角度が適切な範囲内にあるかチェック
 */
export function checkJointAngleRanges(
  angles: Record<string, number>,
  exercise: 'squat' | 'deadlift' | 'bench_press'
): Record<string, { isGood: boolean; message: string }> {
  const feedback: Record<string, { isGood: boolean; message: string }> = {}

  switch (exercise) {
    case 'squat':
      if (angles.knee) {
        feedback.knee = {
          isGood: angles.knee >= 70 && angles.knee <= 100,
          message: angles.knee < 70 ? '膝が深すぎます' : 
                   angles.knee > 100 ? '膝の曲がりが浅いです' : '良い深さです'
        }
      }
      
      if (angles.hip) {
        feedback.hip = {
          isGood: angles.hip >= 60 && angles.hip <= 90,
          message: angles.hip < 60 ? '前傾しすぎています' :
                   angles.hip > 90 ? 'もう少し深くしゃがみましょう' : '良い姿勢です'
        }
      }
      break

    case 'deadlift':
      if (angles.back) {
        feedback.back = {
          isGood: angles.back <= 15,
          message: angles.back > 15 ? '背中をまっすぐに保ちましょう' : '良い背中の角度です'
        }
      }
      
      if (angles.knee) {
        feedback.knee = {
          isGood: angles.knee >= 120 && angles.knee <= 170,
          message: angles.knee < 120 ? '膝を曲げすぎです' :
                   angles.knee > 170 ? '膝をもう少し曲げましょう' : '良い膝の角度です'
        }
      }
      break

    case 'bench_press':
      if (angles.elbow) {
        feedback.elbow = {
          isGood: angles.elbow >= 75 && angles.elbow <= 90,
          message: angles.elbow < 75 ? '肘を下げすぎです' :
                   angles.elbow > 90 ? 'もう少し深く下ろしましょう' : '良い肘の角度です'
        }
      }
      
      if (angles.shoulder) {
        feedback.shoulder = {
          isGood: angles.shoulder >= 45 && angles.shoulder <= 75,
          message: angles.shoulder < 45 ? '肘が体に近すぎます' :
                   angles.shoulder > 75 ? '肘を体に近づけましょう' : '良い肩の角度です'
        }
      }
      break
  }

  return feedback
}