'use client'

// MediaPipeモジュールの動的インポート用ユーティリティ

let mediapipeModules: any = null;

export async function loadMediaPipe() {
  if (mediapipeModules) {
    return mediapipeModules;
  }

  const [cameraUtils, pose, drawingUtils] = await Promise.all([
    import('@mediapipe/camera_utils'),
    import('@mediapipe/pose'),
    import('@mediapipe/drawing_utils'),
  ]);

  mediapipeModules = {
    Camera: cameraUtils.Camera,
    Pose: pose.Pose,
    POSE_CONNECTIONS: pose.POSE_CONNECTIONS,
    drawConnectors: drawingUtils.drawConnectors,
    drawLandmarks: drawingUtils.drawLandmarks,
  };

  return mediapipeModules;
}

// MediaPipeを使用するカスタムフックの動的バージョン
export function useDynamicPoseDetection() {
  const [isLoaded, setIsLoaded] = useState(false);
  const [modules, setModules] = useState<any>(null);

  useEffect(() => {
    loadMediaPipe().then((loadedModules) => {
      setModules(loadedModules);
      setIsLoaded(true);
    });
  }, []);

  return { isLoaded, modules };
}

import { useState, useEffect } from 'react';