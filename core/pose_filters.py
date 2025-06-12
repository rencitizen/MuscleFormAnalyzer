"""
Advanced noise reduction and smoothing filters for pose estimation
"""
import numpy as np
from typing import Dict, List, Tuple, Optional, Deque
from collections import deque
from scipy.signal import savgol_filter
from scipy.ndimage import gaussian_filter1d
import mediapipe as mp

try:
    mp_pose = mp.solutions.pose
    PoseLandmark = mp_pose.PoseLandmark
except AttributeError:
    import mediapipe.python as mp_python
    mp_pose = mp_python.solutions.pose
    PoseLandmark = mp_pose.PoseLandmark

class KalmanFilter3D:
    """3D Kalman filter for smoothing pose landmarks"""
    
    def __init__(self, process_variance: float = 0.01, measurement_variance: float = 0.1):
        self.process_variance = process_variance
        self.measurement_variance = measurement_variance
        self.posteri_estimate = None
        self.posteri_error_estimate = None
        
    def update(self, measurement: np.ndarray) -> np.ndarray:
        """Update filter with new measurement"""
        if self.posteri_estimate is None:
            self.posteri_estimate = measurement.copy()
            self.posteri_error_estimate = np.ones_like(measurement)
            
        # Prediction
        priori_estimate = self.posteri_estimate
        priori_error_estimate = self.posteri_error_estimate + self.process_variance
        
        # Update
        blending_factor = priori_error_estimate / (priori_error_estimate + self.measurement_variance)
        self.posteri_estimate = priori_estimate + blending_factor * (measurement - priori_estimate)
        self.posteri_error_estimate = (1 - blending_factor) * priori_error_estimate
        
        return self.posteri_estimate.copy()
    
    def reset(self):
        """Reset filter state"""
        self.posteri_estimate = None
        self.posteri_error_estimate = None

class PoseFilterManager:
    """Manages multiple filtering techniques for pose landmarks"""
    
    def __init__(self, 
                 enable_kalman: bool = True,
                 enable_savgol: bool = True,
                 enable_gaussian: bool = True,
                 window_size: int = 15,
                 confidence_threshold: float = 0.5):
        """
        Args:
            enable_kalman: Enable Kalman filtering
            enable_savgol: Enable Savitzky-Golay filtering
            enable_gaussian: Enable Gaussian smoothing
            window_size: Window size for filters
            confidence_threshold: Minimum confidence for landmarks
        """
        self.enable_kalman = enable_kalman
        self.enable_savgol = enable_savgol
        self.enable_gaussian = enable_gaussian
        self.window_size = window_size
        self.confidence_threshold = confidence_threshold
        
        # Kalman filters for each landmark
        self.kalman_filters = {}
        
        # History buffers for temporal filtering
        self.landmark_history = {}
        self.max_history = window_size
        
        # Outlier detection parameters
        self.outlier_threshold = 3.0  # Standard deviations
        
    def process_landmarks(self, landmarks: Dict[int, Dict[str, float]]) -> Dict[int, Dict[str, float]]:
        """
        Apply multiple filtering techniques to reduce noise
        
        Args:
            landmarks: Raw MediaPipe landmarks
            
        Returns:
            Filtered landmarks
        """
        filtered_landmarks = {}
        
        for landmark_id, landmark_data in landmarks.items():
            # Skip low confidence landmarks
            if landmark_data.get('visibility', 0) < self.confidence_threshold:
                continue
                
            # Convert to numpy array for processing
            position = np.array([
                landmark_data['x'],
                landmark_data['y'],
                landmark_data.get('z', 0)
            ])
            
            # Apply Kalman filter
            if self.enable_kalman:
                if landmark_id not in self.kalman_filters:
                    self.kalman_filters[landmark_id] = KalmanFilter3D()
                position = self.kalman_filters[landmark_id].update(position)
            
            # Update history
            if landmark_id not in self.landmark_history:
                self.landmark_history[landmark_id] = deque(maxlen=self.max_history)
            self.landmark_history[landmark_id].append(position)
            
            # Apply temporal filtering if enough history
            if len(self.landmark_history[landmark_id]) >= 5:
                position = self._apply_temporal_filters(
                    list(self.landmark_history[landmark_id]),
                    position
                )
            
            # Outlier detection and correction
            position = self._detect_and_correct_outliers(
                landmark_id,
                position,
                list(self.landmark_history[landmark_id])
            )
            
            filtered_landmarks[landmark_id] = {
                'x': float(position[0]),
                'y': float(position[1]),
                'z': float(position[2]),
                'visibility': landmark_data.get('visibility', 1.0)
            }
        
        return filtered_landmarks
    
    def _apply_temporal_filters(self, history: List[np.ndarray], 
                               current: np.ndarray) -> np.ndarray:
        """Apply temporal smoothing filters"""
        if len(history) < 5:
            return current
            
        # Convert history to array
        history_array = np.array(history)
        
        # Apply Savitzky-Golay filter
        if self.enable_savgol and len(history) >= 7:
            try:
                window_length = min(len(history), 7)
                if window_length % 2 == 0:
                    window_length -= 1
                    
                for dim in range(3):
                    history_array[:, dim] = savgol_filter(
                        history_array[:, dim],
                        window_length=window_length,
                        polyorder=2
                    )
            except:
                pass  # Fall back to original if filter fails
        
        # Apply Gaussian smoothing
        if self.enable_gaussian:
            for dim in range(3):
                history_array[:, dim] = gaussian_filter1d(
                    history_array[:, dim],
                    sigma=1.0
                )
        
        # Return the last filtered value
        return history_array[-1]
    
    def _detect_and_correct_outliers(self, landmark_id: int, 
                                   position: np.ndarray,
                                   history: List[np.ndarray]) -> np.ndarray:
        """Detect and correct outlier positions"""
        if len(history) < 5:
            return position
            
        # Calculate statistics from recent history
        recent_history = np.array(history[-10:])  # Last 10 frames
        mean_pos = np.mean(recent_history, axis=0)
        std_pos = np.std(recent_history, axis=0)
        
        # Check if current position is an outlier
        z_scores = np.abs((position - mean_pos) / (std_pos + 1e-6))
        
        if np.any(z_scores > self.outlier_threshold):
            # Replace with predicted position
            if len(history) >= 3:
                # Simple linear prediction
                velocity = recent_history[-1] - recent_history[-2]
                predicted = recent_history[-1] + velocity
                
                # Blend outlier with prediction
                alpha = 0.3  # Weight for original outlier
                position = alpha * position + (1 - alpha) * predicted
        
        return position
    
    def reset(self):
        """Reset all filter states"""
        for kalman in self.kalman_filters.values():
            kalman.reset()
        self.kalman_filters.clear()
        self.landmark_history.clear()

class VelocityFilter:
    """Filter based on velocity constraints to remove physically impossible movements"""
    
    def __init__(self, max_velocity: float = 5.0, fps: float = 30.0):
        """
        Args:
            max_velocity: Maximum allowed velocity in meters/second
            fps: Frames per second of the video
        """
        self.max_velocity = max_velocity
        self.fps = fps
        self.previous_positions = {}
        
    def filter_landmarks(self, landmarks: Dict[int, Dict[str, float]], 
                        scale_px_per_cm: float) -> Dict[int, Dict[str, float]]:
        """
        Filter landmarks based on velocity constraints
        
        Args:
            landmarks: Current frame landmarks
            scale_px_per_cm: Scale factor for pixel to cm conversion
            
        Returns:
            Filtered landmarks
        """
        filtered_landmarks = {}
        time_delta = 1.0 / self.fps
        
        for landmark_id, landmark_data in landmarks.items():
            current_pos = np.array([
                landmark_data['x'],
                landmark_data['y'],
                landmark_data.get('z', 0)
            ])
            
            if landmark_id in self.previous_positions:
                prev_pos = self.previous_positions[landmark_id]
                
                # Calculate velocity in cm/s
                displacement = current_pos - prev_pos
                displacement_cm = displacement * 100 / scale_px_per_cm  # Convert to cm
                velocity = np.linalg.norm(displacement_cm) / time_delta / 100  # m/s
                
                if velocity > self.max_velocity:
                    # Limit movement to maximum velocity
                    direction = displacement / np.linalg.norm(displacement)
                    max_displacement = self.max_velocity * time_delta * 100 * scale_px_per_cm / 100
                    current_pos = prev_pos + direction * max_displacement
            
            filtered_landmarks[landmark_id] = {
                'x': float(current_pos[0]),
                'y': float(current_pos[1]),
                'z': float(current_pos[2]),
                'visibility': landmark_data.get('visibility', 1.0)
            }
            
            self.previous_positions[landmark_id] = current_pos
        
        return filtered_landmarks

class SymmetryEnforcer:
    """Enforce bilateral symmetry constraints for human pose"""
    
    # Pairs of symmetric landmarks
    SYMMETRIC_PAIRS = [
        (PoseLandmark.LEFT_SHOULDER, PoseLandmark.RIGHT_SHOULDER),
        (PoseLandmark.LEFT_ELBOW, PoseLandmark.RIGHT_ELBOW),
        (PoseLandmark.LEFT_WRIST, PoseLandmark.RIGHT_WRIST),
        (PoseLandmark.LEFT_HIP, PoseLandmark.RIGHT_HIP),
        (PoseLandmark.LEFT_KNEE, PoseLandmark.RIGHT_KNEE),
        (PoseLandmark.LEFT_ANKLE, PoseLandmark.RIGHT_ANKLE),
    ]
    
    def __init__(self, symmetry_weight: float = 0.3):
        """
        Args:
            symmetry_weight: Weight for symmetry enforcement (0-1)
        """
        self.symmetry_weight = symmetry_weight
        
    def enforce_symmetry(self, landmarks: Dict[int, Dict[str, float]]) -> Dict[int, Dict[str, float]]:
        """
        Enforce bilateral symmetry constraints
        
        Args:
            landmarks: Input landmarks
            
        Returns:
            Landmarks with symmetry constraints applied
        """
        filtered_landmarks = landmarks.copy()
        
        # Get body center (midpoint between hips)
        left_hip = landmarks.get(PoseLandmark.LEFT_HIP)
        right_hip = landmarks.get(PoseLandmark.RIGHT_HIP)
        
        if left_hip and right_hip:
            center_x = (left_hip['x'] + right_hip['x']) / 2
            
            for left_id, right_id in self.SYMMETRIC_PAIRS:
                left_lm = landmarks.get(left_id)
                right_lm = landmarks.get(right_id)
                
                if left_lm and right_lm:
                    # Check if landmarks have similar confidence
                    left_conf = left_lm.get('visibility', 0)
                    right_conf = right_lm.get('visibility', 0)
                    
                    if left_conf > 0.5 and right_conf > 0.5:
                        # Calculate expected symmetric positions
                        left_dist = center_x - left_lm['x']
                        right_dist = right_lm['x'] - center_x
                        
                        # Average the distances for symmetry
                        avg_dist = (left_dist + right_dist) / 2
                        
                        # Apply symmetry constraint
                        new_left_x = center_x - avg_dist
                        new_right_x = center_x + avg_dist
                        
                        # Blend with original positions
                        filtered_landmarks[left_id]['x'] = (
                            self.symmetry_weight * new_left_x + 
                            (1 - self.symmetry_weight) * left_lm['x']
                        )
                        filtered_landmarks[right_id]['x'] = (
                            self.symmetry_weight * new_right_x + 
                            (1 - self.symmetry_weight) * right_lm['x']
                        )
        
        return filtered_landmarks