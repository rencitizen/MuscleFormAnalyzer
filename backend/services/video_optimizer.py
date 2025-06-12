"""
Video optimization service for reducing processing costs
"""
import cv2
import numpy as np
from pathlib import Path
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class VideoOptimizer:
    """Optimize videos for cost-effective processing"""
    
    def __init__(self, 
                 target_fps: int = 5,
                 target_resolution: int = 720,
                 max_duration: int = 60):
        """
        Initialize video optimizer
        
        Args:
            target_fps: Target frames per second (default: 5)
            target_resolution: Target height in pixels (default: 720p)
            max_duration: Maximum video duration in seconds (default: 60)
        """
        self.target_fps = target_fps
        self.target_resolution = target_resolution
        self.max_duration = max_duration
    
    def optimize_video(self, input_path: str, output_path: str) -> Tuple[bool, str]:
        """
        Optimize video for processing
        
        Args:
            input_path: Path to input video
            output_path: Path to save optimized video
            
        Returns:
            Tuple of (success, message)
        """
        try:
            cap = cv2.VideoCapture(input_path)
            
            # Get video properties
            original_fps = int(cap.get(cv2.CAP_PROP_FPS))
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / original_fps if original_fps > 0 else 0
            
            # Check duration limit
            if duration > self.max_duration:
                cap.release()
                return False, f"Video duration ({duration:.1f}s) exceeds limit ({self.max_duration}s)"
            
            # Calculate new dimensions
            if height > self.target_resolution:
                scale = self.target_resolution / height
                new_width = int(width * scale)
                new_height = self.target_resolution
            else:
                new_width = width
                new_height = height
            
            # Calculate frame sampling rate
            frame_skip = max(1, original_fps // self.target_fps)
            
            # Setup output video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, self.target_fps, (new_width, new_height))
            
            frame_idx = 0
            processed_frames = 0
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Sample frames based on target FPS
                if frame_idx % frame_skip == 0:
                    # Resize frame if needed
                    if new_width != width or new_height != height:
                        frame = cv2.resize(frame, (new_width, new_height), 
                                         interpolation=cv2.INTER_AREA)
                    
                    # Write frame
                    out.write(frame)
                    processed_frames += 1
                
                frame_idx += 1
            
            # Release resources
            cap.release()
            out.release()
            
            # Calculate optimization stats
            original_size = Path(input_path).stat().st_size
            optimized_size = Path(output_path).stat().st_size
            reduction = (1 - optimized_size / original_size) * 100
            
            message = (f"Optimized: {original_fps}fps→{self.target_fps}fps, "
                      f"{height}p→{new_height}p, "
                      f"Size: {original_size/1024/1024:.1f}MB→{optimized_size/1024/1024:.1f}MB "
                      f"({reduction:.1f}% reduction)")
            
            logger.info(message)
            return True, message
            
        except Exception as e:
            logger.error(f"Video optimization failed: {e}")
            return False, f"Optimization failed: {str(e)}"
    
    def extract_key_frames(self, video_path: str, num_frames: int = 10) -> list:
        """
        Extract key frames from video for analysis
        
        Args:
            video_path: Path to video
            num_frames: Number of frames to extract
            
        Returns:
            List of frame arrays
        """
        frames = []
        try:
            cap = cv2.VideoCapture(video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            if total_frames <= num_frames:
                # Extract all frames if video is short
                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break
                    frames.append(frame)
            else:
                # Sample frames evenly
                indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)
                
                for idx in indices:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                    ret, frame = cap.read()
                    if ret:
                        frames.append(frame)
            
            cap.release()
            
        except Exception as e:
            logger.error(f"Frame extraction failed: {e}")
        
        return frames