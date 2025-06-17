/**
 * Camera Manager Class
 * Handles camera stream management with proper cleanup and switching
 */
export class CameraManager {
  private currentStream: MediaStream | null = null;
  private currentCamera: 'user' | 'environment' = 'user';
  private isInitializing: boolean = false;
  private availableCameras: MediaDeviceInfo[] = [];
  private mediaConstraints: MediaStreamConstraints | null = null;

  constructor() {
    console.log('CameraManager initialized');
  }

  /**
   * Get available camera devices
   */
  async getAvailableCameras(): Promise<MediaDeviceInfo[]> {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      this.availableCameras = devices.filter(device => device.kind === 'videoinput');
      
      console.log('Available cameras:', this.availableCameras);
      return this.availableCameras;
    } catch (error) {
      console.error('Error getting camera list:', error);
      return [];
    }
  }

  /**
   * Stop current stream safely
   */
  stopCurrentStream(): void {
    if (this.currentStream) {
      console.log('[CameraManager] Stopping current stream...');
      this.currentStream.getTracks().forEach(track => {
        console.log(`[CameraManager] Stopping ${track.kind} track:`, track.label, track.getSettings());
        track.stop();
      });
      this.currentStream = null;
      console.log('[CameraManager] Stream stopped and cleared');
    }
  }

  /**
   * Initialize camera with improved error handling
   */
  async initializeCamera(
    facingMode: 'user' | 'environment' = 'user', 
    videoElement: HTMLVideoElement | null = null
  ): Promise<boolean> {
    // Prevent duplicate initialization
    if (this.isInitializing) {
      console.log('Camera initialization already in progress...');
      return false;
    }

    this.isInitializing = true;

    try {
      // Stop previous stream completely
      this.stopCurrentStream();
      
      // Wait for resources to be released
      await new Promise(resolve => setTimeout(resolve, 500));

      // Set media constraints
      this.mediaConstraints = {
        video: {
          facingMode: { exact: facingMode },
          width: { ideal: 1280, min: 640 },
          height: { ideal: 720, min: 480 },
          frameRate: { ideal: 30, min: 15 },
          // Add additional constraints for better compatibility
          aspectRatio: { ideal: 16/9 }
        },
        audio: false
      };

      console.log('Initializing camera:', facingMode);
      console.log('Constraints:', this.mediaConstraints);

      // Get new stream
      this.currentStream = await navigator.mediaDevices.getUserMedia(this.mediaConstraints);
      this.currentCamera = facingMode;

      // Apply to video element
      if (videoElement) {
        console.log('[CameraManager] Applying stream to video element...');
        
        // Clear previous srcObject first
        if (videoElement.srcObject) {
          console.log('[CameraManager] Clearing previous srcObject');
          videoElement.srcObject = null;
        }
        
        // Apply new stream
        videoElement.srcObject = this.currentStream;
        
        // Wait for metadata to load
        await new Promise<void>((resolve, reject) => {
          const timeoutId = setTimeout(() => {
            console.error('[CameraManager] Metadata load timeout');
            reject(new Error('Metadata load timeout'));
          }, 5000);
          
          videoElement.onloadedmetadata = () => {
            clearTimeout(timeoutId);
            console.log('[CameraManager] Video metadata loaded');
            const settings = this.currentStream?.getVideoTracks()[0]?.getSettings();
            console.log('[CameraManager] Video settings:', settings);
            resolve();
          };
          
          videoElement.onerror = (e) => {
            clearTimeout(timeoutId);
            console.error('[CameraManager] Video element error:', e);
            reject(new Error('Video element error'));
          };
        });

        await videoElement.play();
        console.log('[CameraManager] Video playback started');
      }

      console.log('Camera initialized successfully:', facingMode);
      return true;

    } catch (error: any) {
      console.error('Camera initialization error:', error);
      
      // Retry with ideal constraint if exact fails
      if (error.name === 'OverconstrainedError' && this.mediaConstraints?.video) {
        console.log('Exact mode failed, retrying with ideal mode...');
        
        try {
          this.mediaConstraints.video = {
            ...this.mediaConstraints.video,
            facingMode: { ideal: facingMode }
          };
          
          this.currentStream = await navigator.mediaDevices.getUserMedia(this.mediaConstraints);
          this.currentCamera = facingMode;

          if (videoElement) {
            // Clear previous srcObject first
            if (videoElement.srcObject) {
              videoElement.srcObject = null;
            }
            
            videoElement.srcObject = this.currentStream;
            
            // Wait for video to be ready
            await new Promise<void>((resolve) => {
              videoElement.onloadedmetadata = () => {
                console.log('[CameraManager] Retry: Video metadata loaded');
                resolve();
              };
            });
            
            await videoElement.play();
            console.log('[CameraManager] Retry: Video playback started');
          }

          console.log('Retry successful:', facingMode);
          return true;
        } catch (retryError) {
          console.error('Retry also failed:', retryError);
        }
      }
      
      return false;
    } finally {
      this.isInitializing = false;
    }
  }

  /**
   * Switch camera safely
   */
  async switchCamera(): Promise<boolean> {
    const targetCamera = this.currentCamera === 'user' ? 'environment' : 'user';
    
    console.log(`Switching camera: ${this.currentCamera} → ${targetCamera}`);
    
    const success = await this.initializeCamera(targetCamera);
    
    if (!success) {
      console.warn('Camera switch failed, reverting to previous camera');
      // Revert to original camera
      await this.initializeCamera(this.currentCamera);
    }
    
    return success;
  }

  /**
   * Get current camera facing mode
   */
  getCurrentCamera(): 'user' | 'environment' {
    return this.currentCamera;
  }

  /**
   * Get current stream
   */
  getCurrentStream(): MediaStream | null {
    return this.currentStream;
  }

  /**
   * Check if camera is initializing
   */
  isCurrentlyInitializing(): boolean {
    return this.isInitializing;
  }

  /**
   * Dispose resources
   */
  dispose(): void {
    this.stopCurrentStream();
    this.isInitializing = false;
    console.log('CameraManager disposed');
  }
}