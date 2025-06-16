import React from 'react';
import { Camera, Wifi, WifiOff } from 'lucide-react';

interface CameraStatusDebugProps {
  currentCamera: 'user' | 'environment';
  isLoading: boolean;
  error: string | null;
  isDetecting?: boolean;
  streamActive?: boolean;
}

export const CameraStatusDebug: React.FC<CameraStatusDebugProps> = ({
  currentCamera,
  isLoading,
  error,
  isDetecting,
  streamActive
}) => {
  if (process.env.NODE_ENV === 'production') {
    return null;
  }

  return (
    <div className="absolute bottom-4 left-4 bg-black/80 text-white p-3 rounded-lg text-xs space-y-1 z-50">
      <div className="flex items-center gap-2">
        <Camera className="w-3 h-3" />
        <span className="font-mono">
          Camera: {currentCamera === 'user' ? 'Front (内)' : 'Back (外)'}
        </span>
      </div>
      
      <div className="flex items-center gap-2">
        {streamActive ? <Wifi className="w-3 h-3 text-green-400" /> : <WifiOff className="w-3 h-3 text-red-400" />}
        <span className="font-mono">
          Stream: {streamActive ? 'Active' : 'Inactive'}
        </span>
      </div>
      
      {isLoading && (
        <div className="text-yellow-400">
          Loading...
        </div>
      )}
      
      {error && (
        <div className="text-red-400 max-w-xs">
          Error: {error}
        </div>
      )}
      
      {isDetecting !== undefined && (
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${isDetecting ? 'bg-green-400' : 'bg-gray-400'}`} />
          <span>Detection: {isDetecting ? 'ON' : 'OFF'}</span>
        </div>
      )}
    </div>
  );
};