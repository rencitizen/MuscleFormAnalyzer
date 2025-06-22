// TENAX FIT v3.0 - クライアントサイドMediaPipe実装
import { Pose, Results } from '@mediapipe/pose';
import { Camera } from '@mediapipe/camera_utils';

export interface PoseDetectionConfig {
  modelComplexity?: 0 | 1 | 2;
  smoothLandmarks?: boolean;
  enableSegmentation?: boolean;
  smoothSegmentation?: boolean;
  minDetectionConfidence?: number;
  minTrackingConfidence?: number;
}

export class MediaPipeClient {
  private pose: Pose | null = null;
  private camera: Camera | null = null;
  private isInitialized = false;
  private worker: Worker | null = null;
  
  constructor(private config: PoseDetectionConfig = {}) {
    // デフォルト設定（パフォーマンス重視）
    this.config = {
      modelComplexity: 1,
      smoothLandmarks: true,
      enableSegmentation: false,
      smoothSegmentation: false,
      minDetectionConfidence: 0.5,
      minTrackingConfidence: 0.5,
      ...config
    };
  }

  // 遅延初期化（必要時のみロード）
  async initialize(): Promise<void> {
    if (this.isInitialized) return;

    try {
      // Web Workerで重い処理を実行
      this.worker = new Worker('/workers/pose-worker.js');
      
      // MediaPipeを動的インポート（バンドルサイズ削減）
      const { Pose } = await import('@mediapipe/pose');
      
      this.pose = new Pose({
        locateFile: (file) => {
          return `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`;
        }
      });

      this.pose.setOptions(this.config);
      
      // 結果ハンドラー設定
      this.pose.onResults(this.handleResults.bind(this));
      
      this.isInitialized = true;
    } catch (error) {
      console.error('MediaPipe initialization failed:', error);
      throw new Error('姿勢検出の初期化に失敗しました');
    }
  }

  // カメラストリーミング開始
  async startCamera(
    videoElement: HTMLVideoElement,
    onResults: (results: Results) => void
  ): Promise<void> {
    if (!this.isInitialized) {
      await this.initialize();
    }

    this.onResultsCallback = onResults;

    const { Camera } = await import('@mediapipe/camera_utils');
    
    this.camera = new Camera(videoElement, {
      onFrame: async () => {
        if (this.pose) {
          await this.pose.send({ image: videoElement });
        }
      },
      width: 1280,
      height: 720,
      facingMode: 'user'
    });

    await this.camera.start();
  }

  // 動画ファイル処理（キーフレームのみ）
  async processVideo(
    videoFile: File,
    onProgress?: (progress: number) => void
  ): Promise<AnalysisResult[]> {
    if (!this.isInitialized) {
      await this.initialize();
    }

    const results: AnalysisResult[] = [];
    
    // ビデオ要素作成
    const video = document.createElement('video');
    video.src = URL.createObjectURL(videoFile);
    video.muted = true;
    
    // メタデータ読み込み
    await new Promise((resolve) => {
      video.onloadedmetadata = resolve;
    });

    const duration = video.duration;
    const fps = 30;
    const keyFrameInterval = 1; // 1秒ごとにキーフレーム
    
    // キーフレームのみ処理
    for (let time = 0; time < duration; time += keyFrameInterval) {
      video.currentTime = time;
      
      await new Promise((resolve) => {
        video.onseeked = resolve;
      });

      if (this.pose) {
        const result = await this.pose.send({ image: video });
        if (result) {
          results.push({
            timestamp: time,
            landmarks: result.poseLandmarks,
            worldLandmarks: result.poseWorldLandmarks,
            score: this.calculateFormScore(result.poseLandmarks)
          });
        }
      }

      if (onProgress) {
        onProgress((time / duration) * 100);
      }
    }

    // クリーンアップ
    URL.revokeObjectURL(video.src);
    
    return results;
  }

  // フォームスコア計算（クライアントサイド）
  private calculateFormScore(landmarks: any[]): number {
    if (!landmarks || landmarks.length === 0) return 0;

    // 簡易的なフォームスコア計算
    let score = 100;
    
    // 肩の水平チェック
    const leftShoulder = landmarks[11];
    const rightShoulder = landmarks[12];
    const shoulderDiff = Math.abs(leftShoulder.y - rightShoulder.y);
    if (shoulderDiff > 0.05) score -= 10;
    
    // 腰の水平チェック
    const leftHip = landmarks[23];
    const rightHip = landmarks[24];
    const hipDiff = Math.abs(leftHip.y - rightHip.y);
    if (hipDiff > 0.05) score -= 10;
    
    // 姿勢の垂直性チェック
    const nose = landmarks[0];
    const midHip = {
      x: (leftHip.x + rightHip.x) / 2,
      y: (leftHip.y + rightHip.y) / 2
    };
    const postureDiff = Math.abs(nose.x - midHip.x);
    if (postureDiff > 0.1) score -= 15;
    
    return Math.max(0, score);
  }

  // リソースクリーンアップ
  async cleanup(): Promise<void> {
    if (this.camera) {
      this.camera.stop();
      this.camera = null;
    }
    
    if (this.pose) {
      this.pose.close();
      this.pose = null;
    }
    
    if (this.worker) {
      this.worker.terminate();
      this.worker = null;
    }
    
    this.isInitialized = false;
  }

  // 結果ハンドラー
  private onResultsCallback?: (results: Results) => void;
  
  private handleResults(results: Results): void {
    if (this.onResultsCallback) {
      // Web Workerで重い計算を実行
      if (this.worker && results.poseLandmarks) {
        this.worker.postMessage({
          type: 'analyze',
          landmarks: results.poseLandmarks,
          worldLandmarks: results.poseWorldLandmarks
        });
        
        this.worker.onmessage = (e) => {
          const enhancedResults = {
            ...results,
            analysis: e.data
          };
          this.onResultsCallback!(enhancedResults);
        };
      } else {
        this.onResultsCallback(results);
      }
    }
  }

  // パフォーマンス設定変更
  async updatePerformanceMode(mode: 'low' | 'medium' | 'high'): Promise<void> {
    const configs = {
      low: {
        modelComplexity: 0,
        minDetectionConfidence: 0.3,
        minTrackingConfidence: 0.3
      },
      medium: {
        modelComplexity: 1,
        minDetectionConfidence: 0.5,
        minTrackingConfidence: 0.5
      },
      high: {
        modelComplexity: 2,
        minDetectionConfidence: 0.7,
        minTrackingConfidence: 0.7
      }
    };

    if (this.pose) {
      this.pose.setOptions(configs[mode]);
    }
  }
}

// 分析結果の型定義
export interface AnalysisResult {
  timestamp: number;
  landmarks: any[];
  worldLandmarks: any[];
  score: number;
  analysis?: {
    formScore: number;
    issues: string[];
    suggestions: string[];
  };
}

// シングルトンインスタンス
let instance: MediaPipeClient | null = null;

export function getMediaPipeClient(config?: PoseDetectionConfig): MediaPipeClient {
  if (!instance) {
    instance = new MediaPipeClient(config);
  }
  return instance;
}