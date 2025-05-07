/**
 * Skeleton Overlay Module
 * Renders MediaPipe pose estimation results on a canvas overlay
 */

class SkeletonOverlay {
  constructor(videoElement, canvasElement) {
    this.video = videoElement;
    this.canvas = canvasElement;
    this.ctx = this.canvas.getContext('2d');
    this.poseData = null;
    this.isPlaying = false;
    this.showHeatmap = false;
    
    this.connections = [
      // Face connections
      [0, 1], [1, 2], [2, 3], [3, 7], [0, 4], [4, 5], [5, 6], [6, 8],
      // Upper body connections
      [9, 10], [11, 12], [11, 13], [13, 15], [12, 14], [14, 16],
      // Hand connections
      [15, 17], [15, 19], [15, 21], [17, 19],
      [16, 18], [16, 20], [16, 22], [18, 20],
      // Torso connections
      [11, 23], [12, 24], [23, 24],
      // Leg connections
      [23, 25], [25, 27], [27, 29], [27, 31],
      [24, 26], [26, 28], [28, 30], [28, 32]
    ];
    
    // Problem areas for heatmap visualization (in a real app, would be determined by analysis)
    this.problemAreas = {
      'knees': [25, 26], // Indices for knee landmarks
      'hips': [23, 24],  // Indices for hip landmarks
      'back': [11, 12, 23, 24] // Spine approximation
    };
    
    this.init();
  }
  
  init() {
    // Initialize canvas dimensions to match video
    this.video.addEventListener('loadedmetadata', () => {
      this.resizeCanvas();
      window.addEventListener('resize', () => this.resizeCanvas());
    });
    
    // Start/stop rendering based on video playback
    this.video.addEventListener('play', () => {
      this.isPlaying = true;
      this.render();
    });
    
    this.video.addEventListener('pause', () => {
      this.isPlaying = false;
    });
    
    this.video.addEventListener('ended', () => {
      this.isPlaying = false;
    });
  }
  
  resizeCanvas() {
    // Match canvas to video dimensions with pixel ratio adjustments
    const rect = this.video.getBoundingClientRect();
    const pixelRatio = window.devicePixelRatio || 1;
    
    this.canvas.width = rect.width * pixelRatio;
    this.canvas.height = rect.height * pixelRatio;
    
    this.canvas.style.width = `${rect.width}px`;
    this.canvas.style.height = `${rect.height}px`;
    
    this.ctx.scale(pixelRatio, pixelRatio);
  }
  
  setPoseData(data) {
    // Set pose data from MediaPipe
    this.poseData = data;
  }
  
  toggleHeatmap(show) {
    this.showHeatmap = show;
  }
  
  render() {
    if (!this.isPlaying) return;
    
    // Clear the canvas
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    
    // If we have pose data, render it
    if (this.poseData) {
      this.renderPose();
    } else {
      // For demo/development, render a simulated skeleton
      this.renderSimulatedPose();
    }
    
    // Request next frame
    requestAnimationFrame(() => this.render());
  }
  
  renderPose() {
    const landmarks = this.poseData.poseLandmarks;
    if (!landmarks) return;
    
    const width = this.video.videoWidth;
    const height = this.video.videoHeight;
    
    // Scale factors for mapping normalized coordinates to canvas size
    const scaleX = this.canvas.width / width;
    const scaleY = this.canvas.height / height;
    
    // Draw connections first (so they're behind the points)
    this.ctx.lineWidth = 3;
    this.ctx.strokeStyle = 'rgba(58, 134, 255, 0.8)';
    
    for (const [i, j] of this.connections) {
      const from = landmarks[i];
      const to = landmarks[j];
      
      if (from && to && from.visibility > 0.5 && to.visibility > 0.5) {
        this.ctx.beginPath();
        this.ctx.moveTo(from.x * width * scaleX, from.y * height * scaleY);
        this.ctx.lineTo(to.x * width * scaleX, to.y * height * scaleY);
        this.ctx.stroke();
      }
    }
    
    // Draw joint points
    for (let i = 0; i < landmarks.length; i++) {
      const landmark = landmarks[i];
      
      if (landmark.visibility > 0.5) {
        this.ctx.fillStyle = 'rgba(58, 134, 255, 0.8)';
        
        // Check if this landmark has issues (would come from analysis)
        let hasIssue = false;
        for (const area in this.problemAreas) {
          if (this.problemAreas[area].includes(i)) {
            hasIssue = true;
            break;
          }
        }
        
        if (hasIssue) {
          // Highlight problem areas
          this.ctx.strokeStyle = 'rgba(255, 0, 110, 0.8)';
          this.ctx.lineWidth = 2;
          this.ctx.beginPath();
          this.ctx.arc(
            landmark.x * width * scaleX,
            landmark.y * height * scaleY,
            10, 0, 2 * Math.PI
          );
          this.ctx.stroke();
        }
        
        // Draw the actual joint point
        this.ctx.beginPath();
        this.ctx.arc(
          landmark.x * width * scaleX,
          landmark.y * height * scaleY,
          5, 0, 2 * Math.PI
        );
        this.ctx.fill();
      }
    }
    
    // Draw heatmap if enabled
    if (this.showHeatmap) {
      this.renderHeatmap(landmarks, width, height, scaleX, scaleY);
    }
  }
  
  renderHeatmap(landmarks, width, height, scaleX, scaleY) {
    // Create a gradient for the heatmap
    for (const area in this.problemAreas) {
      const indices = this.problemAreas[area];
      const points = indices.map(i => landmarks[i])
                           .filter(lm => lm && lm.visibility > 0.5);
      
      if (points.length > 0) {
        // Find the center of the problem area
        const center = points.reduce(
          (acc, p) => ({ x: acc.x + p.x / points.length, y: acc.y + p.y / points.length }),
          { x: 0, y: 0 }
        );
        
        // Create radial gradient
        const gradient = this.ctx.createRadialGradient(
          center.x * width * scaleX, center.y * height * scaleY, 5,
          center.x * width * scaleX, center.y * height * scaleY, 50
        );
        
        gradient.addColorStop(0, 'rgba(255, 0, 110, 0.6)');
        gradient.addColorStop(0.7, 'rgba(255, 0, 110, 0.2)');
        gradient.addColorStop(1, 'rgba(255, 0, 110, 0)');
        
        this.ctx.fillStyle = gradient;
        this.ctx.beginPath();
        this.ctx.arc(
          center.x * width * scaleX,
          center.y * height * scaleY,
          50, 0, 2 * Math.PI
        );
        this.ctx.fill();
      }
    }
  }
  
  renderSimulatedPose() {
    // For development/demo, create a simulated skeleton when no real data exists
    const width = this.canvas.width;
    const height = this.canvas.height;
    const time = performance.now() / 1000;
    const oscillation = Math.sin(time * 2) * 20;
    
    // Simulated keypoints
    const keypoints = [
      {x: width * 0.5, y: height * 0.2}, // 0: Nose
      {x: width * 0.48, y: height * 0.2}, // 1: Left eye inner
      {x: width * 0.45, y: height * 0.19}, // 2: Left eye
      {x: width * 0.42, y: height * 0.2}, // 3: Left eye outer
      {x: width * 0.52, y: height * 0.2}, // 4: Right eye inner
      {x: width * 0.55, y: height * 0.19}, // 5: Right eye
      {x: width * 0.58, y: height * 0.2}, // 6: Right eye outer
      {x: width * 0.4, y: height * 0.22}, // 7: Left ear
      {x: width * 0.6, y: height * 0.22}, // 8: Right ear
      {x: width * 0.47, y: height * 0.25}, // 9: Mouth left
      {x: width * 0.53, y: height * 0.25}, // 10: Mouth right
      {x: width * 0.4, y: height * 0.35 + oscillation/2}, // 11: Left shoulder
      {x: width * 0.6, y: height * 0.35 + oscillation/2}, // 12: Right shoulder
      {x: width * 0.3, y: height * 0.45 + oscillation}, // 13: Left elbow
      {x: width * 0.7, y: height * 0.45 + oscillation}, // 14: Right elbow
      {x: width * 0.25, y: height * 0.55 + oscillation/1.5}, // 15: Left wrist
      {x: width * 0.75, y: height * 0.55 + oscillation/1.5}, // 16: Right wrist
      {x: width * 0.23, y: height * 0.58 + oscillation/1.5}, // 17: Left pinky
      {x: width * 0.77, y: height * 0.58 + oscillation/1.5}, // 18: Right pinky
      {x: width * 0.24, y: height * 0.57 + oscillation/1.5}, // 19: Left index
      {x: width * 0.76, y: height * 0.57 + oscillation/1.5}, // 20: Right index
      {x: width * 0.26, y: height * 0.56 + oscillation/1.5}, // 21: Left thumb
      {x: width * 0.74, y: height * 0.56 + oscillation/1.5}, // 22: Right thumb
      {x: width * 0.45, y: height * 0.6}, // 23: Left hip
      {x: width * 0.55, y: height * 0.6}, // 24: Right hip
      {x: width * 0.4, y: height * 0.75 - oscillation/3}, // 25: Left knee
      {x: width * 0.6, y: height * 0.75 - oscillation/3}, // 26: Right knee
      {x: width * 0.4, y: height * 0.9}, // 27: Left ankle
      {x: width * 0.6, y: height * 0.9}, // 28: Right ankle
      {x: width * 0.38, y: height * 0.92}, // 29: Left heel
      {x: width * 0.62, y: height * 0.92}, // 30: Right heel
      {x: width * 0.41, y: height * 0.93}, // 31: Left foot index
      {x: width * 0.59, y: height * 0.93}  // 32: Right foot index
    ];
    
    // Draw connections
    this.ctx.lineWidth = 3;
    this.ctx.strokeStyle = 'rgba(58, 134, 255, 0.8)';
    
    for (const [i, j] of this.connections) {
      const from = keypoints[i];
      const to = keypoints[j];
      
      if (from && to) {
        this.ctx.beginPath();
        this.ctx.moveTo(from.x, from.y);
        this.ctx.lineTo(to.x, to.y);
        this.ctx.stroke();
      }
    }
    
    // Draw joints
    this.ctx.fillStyle = 'rgba(58, 134, 255, 0.8)';
    for (let i = 0; i < keypoints.length; i++) {
      const point = keypoints[i];
      
      this.ctx.beginPath();
      this.ctx.arc(point.x, point.y, 5, 0, 2 * Math.PI);
      this.ctx.fill();
    }
    
    // Highlight problem areas for demo
    const problemIndices = [25, 26]; // Highlighting the knees for demo
    this.ctx.strokeStyle = 'rgba(255, 0, 110, 0.8)';
    
    for (const i of problemIndices) {
      const point = keypoints[i];
      
      this.ctx.beginPath();
      this.ctx.lineWidth = 2;
      this.ctx.arc(point.x, point.y, 10, 0, 2 * Math.PI);
      this.ctx.stroke();
    }
    
    // Draw heatmap if enabled
    if (this.showHeatmap) {
      // Simulate a heatmap around the knees
      const center = {
        x: (keypoints[25].x + keypoints[26].x) / 2,
        y: (keypoints[25].y + keypoints[26].y) / 2
      };
      
      const gradient = this.ctx.createRadialGradient(
        center.x, center.y, 5,
        center.x, center.y, 50
      );
      
      gradient.addColorStop(0, 'rgba(255, 0, 110, 0.6)');
      gradient.addColorStop(0.7, 'rgba(255, 0, 110, 0.2)');
      gradient.addColorStop(1, 'rgba(255, 0, 110, 0)');
      
      this.ctx.fillStyle = gradient;
      this.ctx.beginPath();
      this.ctx.arc(center.x, center.y, 50, 0, 2 * Math.PI);
      this.ctx.fill();
    }
  }
}

// Usage:
// const overlay = new SkeletonOverlay(videoElement, canvasElement);
// 
// // When pose data is available from MediaPipe:
// overlay.setPoseData(poseResults);
// 
// // Toggle heatmap visualization:
// overlay.toggleHeatmap(true);