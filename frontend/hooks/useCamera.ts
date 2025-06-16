import { useState, useEffect, useRef, useCallback } from 'react';
import { CameraManager } from '@/lib/camera/CameraManager';

interface UseCameraReturn {
  videoRef: React.RefObject<HTMLVideoElement>;
  currentCamera: 'user' | 'environment';
  isLoading: boolean;
  error: string | null;
  availableCameras: MediaDeviceInfo[];
  hasMultipleCameras: boolean;
  initializeCamera: (facingMode?: 'user' | 'environment') => Promise<boolean>;
  switchCamera: () => Promise<boolean>;
  stopCamera: () => void;
}

/**
 * Custom hook for camera management with proper cleanup
 */
export const useCamera = (): UseCameraReturn => {
  const [isLoading, setIsLoading] = useState(false);
  const [currentCamera, setCurrentCamera] = useState<'user' | 'environment'>('user');
  const [error, setError] = useState<string | null>(null);
  const [availableCameras, setAvailableCameras] = useState<MediaDeviceInfo[]>([]);
  
  const cameraManagerRef = useRef<CameraManager | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  // Initialize camera manager
  useEffect(() => {
    cameraManagerRef.current = new CameraManager();
    
    return () => {
      if (cameraManagerRef.current) {
        cameraManagerRef.current.dispose();
      }
    };
  }, []);

  // Load available cameras
  useEffect(() => {
    const loadAvailableCameras = async () => {
      if (cameraManagerRef.current) {
        const cameras = await cameraManagerRef.current.getAvailableCameras();
        setAvailableCameras(cameras);
      }
    };

    loadAvailableCameras();
  }, []);

  // Initialize camera
  const initializeCamera = useCallback(async (facingMode: 'user' | 'environment' = 'user'): Promise<boolean> => {
    if (!cameraManagerRef.current || !videoRef.current) {
      setError('Camera manager not initialized');
      return false;
    }

    setIsLoading(true);
    setError(null);

    try {
      const success = await cameraManagerRef.current.initializeCamera(
        facingMode, 
        videoRef.current
      );
      
      if (success) {
        setCurrentCamera(facingMode);
      } else {
        setError('Failed to initialize camera');
      }
      
      return success;
    } catch (err: any) {
      const errorMessage = err.message || 'Unknown camera error';
      setError(errorMessage);
      console.error('Camera initialization error:', err);
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Switch camera
  const switchCamera = useCallback(async (): Promise<boolean> => {
    if (!cameraManagerRef.current || isLoading) {
      console.log('Cannot switch camera: manager not ready or loading');
      return false;
    }

    setIsLoading(true);
    setError(null);

    try {
      const success = await cameraManagerRef.current.switchCamera();
      
      if (success) {
        setCurrentCamera(cameraManagerRef.current.getCurrentCamera());
      } else {
        setError('Failed to switch camera');
      }
      
      return success;
    } catch (err: any) {
      const errorMessage = err.message || 'Camera switch error';
      setError(errorMessage);
      console.error('Camera switch error:', err);
      return false;
    } finally {
      setIsLoading(false);
    }
  }, [isLoading]);

  // Stop camera
  const stopCamera = useCallback(() => {
    if (cameraManagerRef.current) {
      cameraManagerRef.current.stopCurrentStream();
      if (videoRef.current) {
        videoRef.current.srcObject = null;
      }
    }
  }, []);

  // Check if multiple cameras are available
  const hasMultipleCameras = availableCameras.length > 1;

  return {
    videoRef,
    currentCamera,
    isLoading,
    error,
    availableCameras,
    hasMultipleCameras,
    initializeCamera,
    switchCamera,
    stopCamera
  };
};