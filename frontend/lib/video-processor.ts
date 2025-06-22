// TENAX FIT v3.0 - クライアントサイド動画処理
import { FFmpeg } from '@ffmpeg/ffmpeg';
import { toBlobURL } from '@ffmpeg/util';

export interface VideoProcessingOptions {
  quality?: 'low' | 'medium' | 'high';
  maxDuration?: number; // 秒
  outputFormat?: 'mp4' | 'webm';
  extractKeyFrames?: boolean;
  compressVideo?: boolean;
}

export class VideoProcessor {
  private ffmpeg: FFmpeg | null = null;
  private isLoaded = false;

  constructor() {}

  // FFmpegの遅延初期化
  async initialize(): Promise<void> {
    if (this.isLoaded) return;

    try {
      this.ffmpeg = new FFmpeg();
      
      // プログレスハンドラー
      this.ffmpeg.on('progress', ({ progress, time }) => {
        console.log(`Processing: ${progress * 100}% (time: ${time})`);
      });

      // WebAssemblyファイルをCDNから読み込み
      const baseURL = 'https://unpkg.com/@ffmpeg/core@0.12.6/dist/esm';
      await this.ffmpeg.load({
        coreURL: await toBlobURL(`${baseURL}/ffmpeg-core.js`, 'text/javascript'),
        wasmURL: await toBlobURL(`${baseURL}/ffmpeg-core.wasm`, 'application/wasm'),
      });

      this.isLoaded = true;
    } catch (error) {
      console.error('FFmpeg initialization failed:', error);
      throw new Error('動画処理エンジンの初期化に失敗しました');
    }
  }

  // 動画圧縮
  async compressVideo(
    file: File,
    options: VideoProcessingOptions = {},
    onProgress?: (progress: number) => void
  ): Promise<Blob> {
    await this.initialize();

    const {
      quality = 'medium',
      maxDuration = 60,
      outputFormat = 'mp4',
      compressVideo = true
    } = options;

    // 品質設定
    const qualitySettings = {
      low: { crf: 35, scale: '640:-2', bitrate: '500k' },
      medium: { crf: 28, scale: '1280:-2', bitrate: '1000k' },
      high: { crf: 23, scale: '1920:-2', bitrate: '2000k' }
    };

    const settings = qualitySettings[quality];

    try {
      // ファイルをFFmpegに書き込み
      const inputName = 'input.mp4';
      const outputName = `output.${outputFormat}`;
      
      await this.ffmpeg!.writeFile(inputName, await file.arrayBuffer());

      // FFmpegコマンド構築
      const args = [
        '-i', inputName,
        '-t', maxDuration.toString(), // 最大時間制限
        '-vf', `scale=${settings.scale}`, // スケーリング
        '-c:v', outputFormat === 'webm' ? 'libvpx-vp9' : 'libx264', // コーデック
        '-crf', settings.crf.toString(), // 品質
        '-b:v', settings.bitrate, // ビットレート
        '-preset', 'fast', // エンコード速度
        '-movflags', '+faststart', // Web最適化
        outputName
      ];

      // オーディオ設定
      if (compressVideo) {
        args.splice(-1, 0, '-c:a', 'aac', '-b:a', '128k');
      }

      // プログレスコールバック設定
      if (onProgress) {
        this.ffmpeg!.on('progress', ({ progress }) => {
          onProgress(progress);
        });
      }

      // 実行
      await this.ffmpeg!.exec(args);

      // 結果を読み込み
      const data = await this.ffmpeg!.readFile(outputName);
      const blob = new Blob([data], { type: `video/${outputFormat}` });

      // クリーンアップ
      await this.ffmpeg!.deleteFile(inputName);
      await this.ffmpeg!.deleteFile(outputName);

      return blob;
    } catch (error) {
      console.error('Video compression failed:', error);
      throw new Error('動画の圧縮に失敗しました');
    }
  }

  // キーフレーム抽出
  async extractKeyFrames(
    file: File,
    interval: number = 1, // 秒
    onProgress?: (progress: number) => void
  ): Promise<Blob[]> {
    await this.initialize();

    const frames: Blob[] = [];

    try {
      const inputName = 'input.mp4';
      await this.ffmpeg!.writeFile(inputName, await file.arrayBuffer());

      // 動画の長さを取得（簡易的な方法）
      const duration = await this.getVideoDuration(file);
      const frameCount = Math.floor(duration / interval);

      for (let i = 0; i < frameCount; i++) {
        const time = i * interval;
        const outputName = `frame_${i}.jpg`;

        // フレーム抽出コマンド
        await this.ffmpeg!.exec([
          '-i', inputName,
          '-ss', time.toString(),
          '-vframes', '1',
          '-q:v', '2',
          outputName
        ]);

        const data = await this.ffmpeg!.readFile(outputName);
        frames.push(new Blob([data], { type: 'image/jpeg' }));
        
        await this.ffmpeg!.deleteFile(outputName);

        if (onProgress) {
          onProgress((i + 1) / frameCount);
        }
      }

      await this.ffmpeg!.deleteFile(inputName);
      return frames;
    } catch (error) {
      console.error('Key frame extraction failed:', error);
      throw new Error('キーフレームの抽出に失敗しました');
    }
  }

  // サムネイル生成
  async generateThumbnail(file: File, time: number = 0): Promise<Blob> {
    await this.initialize();

    try {
      const inputName = 'input.mp4';
      const outputName = 'thumbnail.jpg';

      await this.ffmpeg!.writeFile(inputName, await file.arrayBuffer());

      await this.ffmpeg!.exec([
        '-i', inputName,
        '-ss', time.toString(),
        '-vframes', '1',
        '-vf', 'scale=320:-1',
        '-q:v', '2',
        outputName
      ]);

      const data = await this.ffmpeg!.readFile(outputName);
      const blob = new Blob([data], { type: 'image/jpeg' });

      await this.ffmpeg!.deleteFile(inputName);
      await this.ffmpeg!.deleteFile(outputName);

      return blob;
    } catch (error) {
      console.error('Thumbnail generation failed:', error);
      throw new Error('サムネイルの生成に失敗しました');
    }
  }

  // 動画の長さを取得
  private async getVideoDuration(file: File): Promise<number> {
    return new Promise((resolve) => {
      const video = document.createElement('video');
      video.preload = 'metadata';
      video.onloadedmetadata = () => {
        window.URL.revokeObjectURL(video.src);
        resolve(video.duration);
      };
      video.src = URL.createObjectURL(file);
    });
  }

  // リソースクリーンアップ
  cleanup(): void {
    this.ffmpeg = null;
    this.isLoaded = false;
  }
}

// シングルトンインスタンス
let processorInstance: VideoProcessor | null = null;

export function getVideoProcessor(): VideoProcessor {
  if (!processorInstance) {
    processorInstance = new VideoProcessor();
  }
  return processorInstance;
}

// 動画処理ユーティリティ関数
export async function optimizeVideoForWeb(
  file: File,
  onProgress?: (progress: number) => void
): Promise<Blob> {
  const processor = getVideoProcessor();
  
  // ファイルサイズに基づいて品質を自動調整
  const fileSizeMB = file.size / (1024 * 1024);
  let quality: 'low' | 'medium' | 'high' = 'medium';
  
  if (fileSizeMB > 100) {
    quality = 'low';
  } else if (fileSizeMB < 10) {
    quality = 'high';
  }

  return processor.compressVideo(file, {
    quality,
    maxDuration: 300, // 最大5分
    compressVideo: true
  }, onProgress);
}