'use client';

import React, { useCallback, useEffect, useRef, useState } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { useCamera } from '@/hooks/useCamera';
import { Camera, CameraOff, Wifi, WifiOff, AlertCircle } from 'lucide-react';

interface RealtimeCameraAnalysisProps {
  exerciseType: string;
  userId: string;
  onAnalysisResult?: (result: any) => void;
}

export default function RealtimeCameraAnalysis({
  exerciseType,
  userId,
  onAnalysisResult,
}: RealtimeCameraAnalysisProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const frameIntervalRef = useRef<NodeJS.Timeout | null>(null);
  
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [facingMode, setFacingMode] = useState<'user' | 'environment'>('user');
  const [frameRate] = useState(10); // Send 10 frames per second
  
  const {
    stream,
    error: cameraError,
    isLoading: cameraLoading,
    hasMultipleCameras,
    switchCamera,
  } = useCamera(videoRef, facingMode);

  // WebSocket connection
  const wsUrl = process.env.NEXT_PUBLIC_WEBSOCKET_URL || 
    (typeof window !== 'undefined' ? 
      `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/api/form/ws/camera/${userId}?exercise_type=${exerciseType}&camera_type=${facingMode}` :
      '');

  const {
    isConnected,
    isConnecting,
    error: wsError,
    sendFrame,
    lastMessage,
  } = useWebSocket({
    url: wsUrl,
    onMessage: (data) => {
      if (data.type === 'analysis' && data.data) {
        onAnalysisResult?.(data.data);
      }
    },
  });

  // Capture and send frames
  const captureFrame = useCallback(() => {
    if (!videoRef.current || !canvasRef.current || !stream || !isConnected) {
      return;
    }

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');

    if (!context) return;

    // Set canvas dimensions to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw video frame to canvas
    context.drawImage(video, 0, 0);

    // Convert to base64
    canvas.toBlob((blob) => {
      if (blob) {
        const reader = new FileReader();
        reader.onloadend = () => {
          const base64data = reader.result as string;
          // Remove data URL prefix
          const base64 = base64data.split(',')[1];
          sendFrame(base64, exerciseType);
        };
        reader.readAsDataURL(blob);
      }
    }, 'image/jpeg', 0.8);
  }, [stream, isConnected, sendFrame, exerciseType]);

  // Start/stop frame capture
  useEffect(() => {
    if (isAnalyzing && stream && isConnected) {
      const interval = 1000 / frameRate;
      frameIntervalRef.current = setInterval(captureFrame, interval);
    } else {
      if (frameIntervalRef.current) {
        clearInterval(frameIntervalRef.current);
        frameIntervalRef.current = null;
      }
    }

    return () => {
      if (frameIntervalRef.current) {
        clearInterval(frameIntervalRef.current);
      }
    };
  }, [isAnalyzing, stream, isConnected, frameRate, captureFrame]);

  // Handle camera switching
  const handleSwitchCamera = async () => {
    const newMode = facingMode === 'user' ? 'environment' : 'user';
    setFacingMode(newMode);
    await switchCamera();
  };

  // Render pose landmarks on video
  useEffect(() => {
    if (lastMessage?.type === 'analysis' && lastMessage.data?.landmarks && videoRef.current) {
      // Here you could render the pose landmarks on a canvas overlay
      // For now, we'll just log them
      console.log('Pose landmarks:', lastMessage.data.landmarks);
    }
  }, [lastMessage]);

  const connectionStatus = () => {
    if (isConnecting) return { icon: Wifi, text: '接続中...', color: 'text-yellow-500' };
    if (isConnected) return { icon: Wifi, text: '接続済み', color: 'text-green-500' };
    return { icon: WifiOff, text: '未接続', color: 'text-red-500' };
  };

  const { icon: ConnectionIcon, text: connectionText, color: connectionColor } = connectionStatus();

  return (
    <div className="space-y-4">
      <div className="relative rounded-lg overflow-hidden bg-gray-900">
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className="w-full h-auto"
        />
        
        <canvas
          ref={canvasRef}
          className="hidden"
        />

        {/* Status overlay */}
        <div className="absolute top-4 left-4 right-4 flex justify-between items-start">
          <div className="bg-black/50 backdrop-blur-sm rounded-lg px-3 py-2 flex items-center gap-2">
            <ConnectionIcon className={`w-4 h-4 ${connectionColor}`} />
            <span className="text-white text-sm">{connectionText}</span>
          </div>

          {hasMultipleCameras && (
            <button
              onClick={handleSwitchCamera}
              className="bg-black/50 backdrop-blur-sm rounded-lg p-2 hover:bg-black/70 transition-colors"
              disabled={cameraLoading}
            >
              <Camera className="w-5 h-5 text-white" />
            </button>
          )}
        </div>

        {/* Error messages */}
        {(cameraError || wsError) && (
          <div className="absolute bottom-4 left-4 right-4">
            <div className="bg-red-500/90 backdrop-blur-sm rounded-lg px-4 py-3 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-white flex-shrink-0 mt-0.5" />
              <div className="text-white text-sm">
                {cameraError || wsError}
              </div>
            </div>
          </div>
        )}

        {/* No camera stream */}
        {!stream && !cameraLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-900">
            <div className="text-center">
              <CameraOff className="w-12 h-12 text-gray-500 mx-auto mb-3" />
              <p className="text-gray-400">カメラを起動してください</p>
            </div>
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="flex gap-3">
        <button
          onClick={() => setIsAnalyzing(!isAnalyzing)}
          disabled={!stream || !isConnected}
          className={`flex-1 py-3 px-4 rounded-lg font-medium transition-colors ${
            isAnalyzing
              ? 'bg-red-500 hover:bg-red-600 text-white'
              : 'bg-blue-500 hover:bg-blue-600 text-white disabled:bg-gray-300 disabled:text-gray-500'
          }`}
        >
          {isAnalyzing ? '分析を停止' : 'リアルタイム分析を開始'}
        </button>

        <button
          onClick={() => setFacingMode(facingMode === 'user' ? 'environment' : 'user')}
          className="px-4 py-3 rounded-lg bg-gray-200 hover:bg-gray-300 transition-colors"
        >
          {facingMode === 'user' ? '外カメラ' : '内カメラ'}
        </button>
      </div>

      {/* Analysis results */}
      {lastMessage?.type === 'analysis' && lastMessage.data && (
        <div className="bg-gray-100 rounded-lg p-4">
          <h3 className="font-semibold mb-2">分析結果</h3>
          {lastMessage.data.pose_detected ? (
            <div className="space-y-2">
              {lastMessage.data.analysis && (
                <>
                  <p className="text-sm">
                    <span className="font-medium">状態:</span> {lastMessage.data.analysis.phase || 'N/A'}
                  </p>
                  <p className="text-sm">
                    <span className="font-medium">スコア:</span> {lastMessage.data.analysis.score || 0}%
                  </p>
                  {lastMessage.data.analysis.feedback && (
                    <p className="text-sm text-blue-600">
                      {lastMessage.data.analysis.feedback}
                    </p>
                  )}
                </>
              )}
            </div>
          ) : (
            <p className="text-sm text-gray-500">ポーズが検出されませんでした</p>
          )}
        </div>
      )}
    </div>
  );
}