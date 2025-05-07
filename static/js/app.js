// Main application logic for Muscle-Form Analyzer
document.addEventListener('DOMContentLoaded', function() {
  // Initialize components
  initUploadForm();
  initVideoProcessing();
  initFeedbackCards();
  initTimelineScrubber();
  initGaugeAnimation();
});

// Upload form handling
function initUploadForm() {
  const uploadForm = document.getElementById('upload-form');
  const videoFile = document.getElementById('video-file');
  const exerciseType = document.getElementById('exercise-type');
  const fileLabel = document.querySelector('.file-label');
  const autoDetect = document.querySelector('.auto-detect');
  
  if (!uploadForm) return;
  
  // File selection styling
  if (videoFile) {
    videoFile.addEventListener('change', function(e) {
      if (this.files && this.files[0]) {
        const fileName = this.files[0].name;
        if (fileLabel) {
          fileLabel.textContent = fileName;
        }
        
        // Auto-detect exercise type (simulated)
        setTimeout(() => {
          if (autoDetect) {
            autoDetect.style.display = 'flex';
            
            // Fake detection based on filename
            if (fileName.toLowerCase().includes('squat')) {
              exerciseType.value = 'squat';
            } else if (fileName.toLowerCase().includes('bench')) {
              exerciseType.value = 'bench';
            } else if (fileName.toLowerCase().includes('dead')) {
              exerciseType.value = 'deadlift';
            }
          }
        }, 500);
      }
    });
  }
  
  // Form submission
  if (uploadForm) {
    uploadForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      if (!videoFile.files || !videoFile.files[0]) {
        alert('Please select a video file first.');
        return;
      }
      
      // Show loading and progress UI
      document.getElementById('upload-container').style.display = 'none';
      document.getElementById('processing-container').style.display = 'block';
      
      // Simulate processing steps
      startProcessingSimulation();
      
      // In a real implementation, we would submit the form via AJAX here
      // For demo, we'll just simulate the steps and then redirect
      setTimeout(() => {
        window.location.href = '/results';
      }, 8000);
    });
  }
}

// Simulate the processing steps for the demo
function startProcessingSimulation() {
  const progressBar = document.querySelector('.progress-fill');
  const steps = document.querySelectorAll('.progress-step');
  
  // Step 1: Pose Detection (after 1 second)
  setTimeout(() => {
    if (progressBar) progressBar.style.width = '33%';
    if (steps[0]) {
      steps[0].querySelector('.step-icon').classList.add('active');
    }
    
    // Step 2: Angle Calculation (after 3 seconds)
    setTimeout(() => {
      if (progressBar) progressBar.style.width = '66%';
      if (steps[0]) {
        steps[0].querySelector('.step-icon').classList.remove('active');
        steps[0].querySelector('.step-icon').classList.add('completed');
      }
      if (steps[1]) {
        steps[1].querySelector('.step-icon').classList.add('active');
      }
      
      // Step 3: Feedback Generation (after 2 seconds)
      setTimeout(() => {
        if (progressBar) progressBar.style.width = '100%';
        if (steps[1]) {
          steps[1].querySelector('.step-icon').classList.remove('active');
          steps[1].querySelector('.step-icon').classList.add('completed');
        }
        if (steps[2]) {
          steps[2].querySelector('.step-icon').classList.add('active');
        }
        
        // Complete (after 1 second)
        setTimeout(() => {
          if (steps[2]) {
            steps[2].querySelector('.step-icon').classList.remove('active');
            steps[2].querySelector('.step-icon').classList.add('completed');
          }
        }, 1000);
      }, 2000);
    }, 3000);
  }, 1000);
}

// Video processing and skeleton overlay
function initVideoProcessing() {
  const videoContainer = document.querySelector('.video-container');
  const videoPlayer = document.querySelector('.video-player');
  const skeletonOverlay = document.querySelector('.skeleton-overlay');
  
  if (!videoContainer || !videoPlayer || !skeletonOverlay) return;
  
  // Set up skeleton overlay canvas
  const canvas = skeletonOverlay;
  const ctx = canvas.getContext('2d');
  
  // When the video is loaded, configure the canvas dimensions
  videoPlayer.addEventListener('loadedmetadata', function() {
    canvas.width = videoPlayer.videoWidth;
    canvas.height = videoPlayer.videoHeight;
    
    // Adjust canvas size to match video display size
    function updateCanvasSize() {
      const rect = videoPlayer.getBoundingClientRect();
      canvas.style.width = `${rect.width}px`;
      canvas.style.height = `${rect.height}px`;
    }
    
    updateCanvasSize();
    window.addEventListener('resize', updateCanvasSize);
  });
  
  // Draw skeleton on the canvas (simulated)
  videoPlayer.addEventListener('play', function() {
    drawSkeleton();
  });
  
  function drawSkeleton() {
    if (videoPlayer.paused || videoPlayer.ended) return;
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw skeleton (this would use actual pose data in a real app)
    drawSimulatedSkeleton(ctx, canvas.width, canvas.height, videoPlayer.currentTime);
    
    // Request next frame
    requestAnimationFrame(drawSkeleton);
  }
}

// Simulated skeleton drawing
function drawSimulatedSkeleton(ctx, width, height, time) {
  // Simulated pose keypoints based on time to create animation
  const oscillation = Math.sin(time * 2) * 20; // Create movement
  
  ctx.strokeStyle = 'rgba(58, 134, 255, 0.8)';
  ctx.lineWidth = 3;
  ctx.fillStyle = 'rgba(58, 134, 255, 0.6)';
  
  // Simulated keypoints (would come from MediaPipe in real app)
  const keypoints = [
    {x: width * 0.5, y: height * 0.2}, // Head
    {x: width * 0.5, y: height * 0.3}, // Neck
    {x: width * 0.4, y: height * 0.4 + oscillation}, // Left shoulder
    {x: width * 0.6, y: height * 0.4 + oscillation}, // Right shoulder
    {x: width * 0.3, y: height * 0.5 + oscillation}, // Left elbow
    {x: width * 0.7, y: height * 0.5 + oscillation}, // Right elbow
    {x: width * 0.25, y: height * 0.6}, // Left wrist
    {x: width * 0.75, y: height * 0.6}, // Right wrist
    {x: width * 0.45, y: height * 0.6}, // Left hip
    {x: width * 0.55, y: height * 0.6}, // Right hip
    {x: width * 0.4, y: height * 0.75 - oscillation/2}, // Left knee
    {x: width * 0.6, y: height * 0.75 - oscillation/2}, // Right knee
    {x: width * 0.4, y: height * 0.9}, // Left ankle
    {x: width * 0.6, y: height * 0.9}  // Right ankle
  ];
  
  // Draw joints
  keypoints.forEach(point => {
    ctx.beginPath();
    ctx.arc(point.x, point.y, 5, 0, Math.PI * 2);
    ctx.fill();
  });
  
  // Draw connections
  ctx.beginPath();
  // Neck to head
  ctx.moveTo(keypoints[1].x, keypoints[1].y);
  ctx.lineTo(keypoints[0].x, keypoints[0].y);
  
  // Shoulders
  ctx.moveTo(keypoints[2].x, keypoints[2].y);
  ctx.lineTo(keypoints[1].x, keypoints[1].y);
  ctx.lineTo(keypoints[3].x, keypoints[3].y);
  
  // Arms
  ctx.moveTo(keypoints[2].x, keypoints[2].y);
  ctx.lineTo(keypoints[4].x, keypoints[4].y);
  ctx.lineTo(keypoints[6].x, keypoints[6].y);
  
  ctx.moveTo(keypoints[3].x, keypoints[3].y);
  ctx.lineTo(keypoints[5].x, keypoints[5].y);
  ctx.lineTo(keypoints[7].x, keypoints[7].y);
  
  // Torso
  ctx.moveTo(keypoints[2].x, keypoints[2].y);
  ctx.lineTo(keypoints[8].x, keypoints[8].y);
  ctx.lineTo(keypoints[9].x, keypoints[9].y);
  ctx.lineTo(keypoints[3].x, keypoints[3].y);
  
  // Legs
  ctx.moveTo(keypoints[8].x, keypoints[8].y);
  ctx.lineTo(keypoints[10].x, keypoints[10].y);
  ctx.lineTo(keypoints[12].x, keypoints[12].y);
  
  ctx.moveTo(keypoints[9].x, keypoints[9].y);
  ctx.lineTo(keypoints[11].x, keypoints[11].y);
  ctx.lineTo(keypoints[13].x, keypoints[13].y);
  
  ctx.stroke();
  
  // Draw key problem areas if needed (red highlights)
  const errorPoints = [4, 5, 10, 11]; // Simulate issues with elbows and knees
  errorPoints.forEach(idx => {
    if (Math.random() > 0.7) { // Random highlighting for demo
      ctx.beginPath();
      ctx.strokeStyle = 'rgba(255, 0, 110, 0.8)';
      ctx.arc(keypoints[idx].x, keypoints[idx].y, 12, 0, Math.PI * 2);
      ctx.stroke();
      ctx.strokeStyle = 'rgba(58, 134, 255, 0.8)'; // Reset color
    }
  });
}

// Expandable feedback cards
function initFeedbackCards() {
  const feedbackCards = document.querySelectorAll('.feedback-card');
  
  feedbackCards.forEach(card => {
    const header = card.querySelector('.feedback-header');
    if (header) {
      header.addEventListener('click', function() {
        const expanded = card.getAttribute('data-expanded') === 'true';
        card.setAttribute('data-expanded', !expanded);
      });
    }
  });
}

// Timeline scrubber for video navigation
function initTimelineScrubber() {
  const timeline = document.querySelector('.timeline-scrubber');
  const videoPlayer = document.querySelector('.video-player');
  const playhead = document.querySelector('.playhead');
  
  if (!timeline || !videoPlayer) return;
  
  // Generate timeline frames (would be based on actual video analysis)
  if (timeline) {
    const totalFrames = 100; // Simulated number of frames
    
    for (let i = 0; i < totalFrames; i++) {
      const frame = document.createElement('div');
      frame.classList.add('timeline-frame');
      
      // Position the frame within the timeline
      frame.style.left = `${(i / totalFrames) * 100}%`;
      frame.style.width = `${100 / totalFrames}%`;
      
      // Add error class to some frames for demonstration
      if (
        (i > 15 && i < 20) || 
        (i > 45 && i < 50) || 
        (i > 75 && i < 80)
      ) {
        frame.classList.add('error');
      }
      
      // Click to jump to that part of the video
      frame.addEventListener('click', function() {
        const seekPosition = (i / totalFrames) * videoPlayer.duration;
        videoPlayer.currentTime = seekPosition;
      });
      
      timeline.appendChild(frame);
    }
  }
  
  // Update playhead position as video plays
  if (videoPlayer && playhead) {
    videoPlayer.addEventListener('timeupdate', function() {
      const progress = (videoPlayer.currentTime / videoPlayer.duration) * 100;
      playhead.style.left = `${progress}%`;
    });
  }
}

// Animate the form score gauge
function initGaugeAnimation() {
  const scoreGauge = document.querySelector('.gauge-container');
  
  if (!scoreGauge) return;
  
  // Get the score value from the data attribute
  const score = parseInt(scoreGauge.getAttribute('data-score') || '0');
  const circlePath = scoreGauge.querySelector('.gauge-fill');
  const scoreText = scoreGauge.querySelector('.gauge-text');
  
  if (circlePath && scoreText) {
    // Calculate stroke-dasharray and stroke-dashoffset
    const radius = 85;
    const circumference = 2 * Math.PI * radius;
    
    circlePath.style.strokeDasharray = circumference;
    circlePath.style.strokeDashoffset = circumference;
    
    // Animate the gauge filling
    setTimeout(() => {
      // Update the text with counting animation
      let currentScore = 0;
      const interval = setInterval(() => {
        currentScore += 1;
        if (currentScore > score) {
          clearInterval(interval);
          currentScore = score;
        }
        scoreText.textContent = currentScore;
      }, 20);
      
      // Update the circle fill
      const offset = circumference - (score / 100) * circumference;
      circlePath.style.strokeDashoffset = offset;
      
      // Update color based on score
      if (score < 50) {
        circlePath.style.stroke = 'var(--danger-color)';
      } else if (score < 80) {
        circlePath.style.stroke = 'var(--warning-color)';
      } else {
        circlePath.style.stroke = 'var(--success-color)';
      }
    }, 500);
  }
}

// Toggle heatmap overlay
function toggleHeatmap() {
  const heatmapOverlay = document.querySelector('.heatmap-overlay');
  if (heatmapOverlay) {
    heatmapOverlay.style.display = heatmapOverlay.style.display === 'none' ? 'block' : 'none';
  }
}

// Toggle 3D model comparison
function toggle3DComparison() {
  const comparisonViewer = document.querySelector('.comparison-viewer');
  if (comparisonViewer) {
    comparisonViewer.style.display = comparisonViewer.style.display === 'none' ? 'block' : 'none';
  }
}

// Update 3D model opacity
function updateModelOpacity(opacity) {
  // This would update the actual 3D models' opacity
  console.log(`Setting model opacity to ${opacity}`);
}

// Play voice feedback
function playVoiceFeedback() {
  // This would trigger text-to-speech with the feedback
  alert('Voice feedback would play here in a complete implementation.');
}