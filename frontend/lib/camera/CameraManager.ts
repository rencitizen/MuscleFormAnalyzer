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
      this.currentStream.getTracks().forEach(track => {
        track.stop();
        console.log('Track stopped:', track.label);
      });
      this.currentStream = null;
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
          frameRate: { ideal: 30, min: 15 }
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
        videoElement.srcObject = this.currentStream;
        
        // Wait for metadata to load
        await new Promise<void>((resolve, reject) => {
          videoElement.onloadedmetadata = () => resolve();
          videoElement.onerror = () => reject(new Error('Video element error'));
          setTimeout(() => reject(new Error('Metadata load timeout')), 5000);
        });

        await videoElement.play();
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
            videoElement.srcObject = this.currentStream;
            await videoElement.play();
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