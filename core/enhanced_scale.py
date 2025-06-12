"""
Enhanced scaling module with multiple reference points and improved accuracy
"""
import mediapipe as mp
import numpy as np
from typing import Tuple, Dict, Any, List, Optional
from collections import deque
from scipy import stats

try:
    mp_pose = mp.solutions.pose
    PoseLandmark = mp_pose.PoseLandmark
except AttributeError:
    import mediapipe.python as mp_python
    mp_pose = mp_python.solutions.pose
    PoseLandmark = mp_pose.PoseLandmark

class EnhancedScaleCalculator:
    """
    Enhanced pixel-to-cm conversion calculator with multiple reference points
    """
    # Human body proportion constants (based on anthropometric data)
    BODY_PROPORTIONS = {
        'head_to_height': 0.13,  # Head height is ~13% of total height
        'shoulder_width_to_height': 0.26,  # Shoulder width is ~26% of height
        'arm_span_to_height': 1.0,  # Arm span ≈ height
        'torso_to_height': 0.52,  # Torso length is ~52% of height
        'leg_to_height': 0.48,  # Leg length is ~48% of height
    }
    
    def __init__(self, user_height_cm: float, confidence_threshold: float = 0.5):
        """
        Args:
            user_height_cm (float): User's height in cm
            confidence_threshold (float): Minimum landmark visibility confidence
        """
        self.user_height_cm = user_height_cm
        self.confidence_threshold = confidence_threshold
        self.scale_history = deque(maxlen=30)  # Store last 30 scale calculations
        self.scale_px_per_cm = None
        self.reference_distances = {}
        
    def calculate_multi_reference_scale(self, landmarks: Dict[int, Dict[str, float]], 
                                      frame_height: int, frame_width: int) -> Optional[float]:
        """
        Calculate scale using multiple body reference points for improved accuracy
        
        Args:
            landmarks: MediaPipe pose landmarks
            frame_height: Frame height in pixels
            frame_width: Frame width in pixels
            
        Returns:
            Scale factor (pixels per cm) or None if calculation fails
        """
        scales = []
        weights = []
        
        # Method 1: Head-to-ankle distance (traditional)
        scale1, conf1 = self._calculate_height_based_scale(landmarks, frame_height)
        if scale1:
            scales.append(scale1)
            weights.append(conf1 * 1.0)  # Base weight
            
        # Method 2: Shoulder width
        scale2, conf2 = self._calculate_shoulder_width_scale(landmarks, frame_width)
        if scale2:
            scales.append(scale2)
            weights.append(conf2 * 0.8)  # Slightly lower weight
            
        # Method 3: Torso length
        scale3, conf3 = self._calculate_torso_scale(landmarks, frame_height)
        if scale3:
            scales.append(scale3)
            weights.append(conf3 * 0.9)
            
        # Method 4: Arm length (if visible)
        scale4, conf4 = self._calculate_arm_span_scale(landmarks, frame_width)
        if scale4:
            scales.append(scale4)
            weights.append(conf4 * 0.7)
            
        if not scales:
            return None
            
        # Calculate weighted average, removing outliers
        scales_array = np.array(scales)
        weights_array = np.array(weights)
        
        # Remove outliers using z-score
        z_scores = np.abs(stats.zscore(scales_array))
        mask = z_scores < 2.0  # Keep values within 2 standard deviations
        
        if not np.any(mask):
            mask = np.ones_like(z_scores, dtype=bool)  # Keep all if all are outliers
            
        filtered_scales = scales_array[mask]
        filtered_weights = weights_array[mask]
        
        # Weighted average
        weighted_scale = np.average(filtered_scales, weights=filtered_weights)
        
        # Update history and smooth
        self.scale_history.append(weighted_scale)
        
        # Apply temporal smoothing
        if len(self.scale_history) > 5:
            # Use exponential moving average
            smoothed_scale = self._exponential_moving_average(list(self.scale_history), alpha=0.3)
            self.scale_px_per_cm = smoothed_scale
        else:
            self.scale_px_per_cm = weighted_scale
            
        return self.scale_px_per_cm
    
    def _calculate_height_based_scale(self, landmarks: Dict[int, Dict[str, float]], 
                                    frame_height: int) -> Tuple[Optional[float], float]:
        """Calculate scale based on nose-to-ankle distance"""
        nose = landmarks.get(PoseLandmark.NOSE)
        left_ankle = landmarks.get(PoseLandmark.LEFT_ANKLE)
        right_ankle = landmarks.get(PoseLandmark.RIGHT_ANKLE)
        
        if not nose:
            return None, 0.0
            
        # Use the more visible ankle
        ankle_y = None
        confidence = 0.0
        
        if left_ankle and right_ankle:
            left_conf = left_ankle.get('visibility', 0)
            right_conf = right_ankle.get('visibility', 0)
            
            if left_conf > self.confidence_threshold and right_conf > self.confidence_threshold:
                ankle_y = (left_ankle['y'] + right_ankle['y']) / 2
                confidence = (left_conf + right_conf) / 2
            elif left_conf > self.confidence_threshold:
                ankle_y = left_ankle['y']
                confidence = left_conf
            elif right_conf > self.confidence_threshold:
                ankle_y = right_ankle['y']
                confidence = right_conf
                
        if ankle_y is not None and nose.get('visibility', 0) > self.confidence_threshold:
            pixel_height = abs(nose['y'] - ankle_y) * frame_height
            
            # Adjust for the fact that nose is not the top of head
            adjusted_height_cm = self.user_height_cm * 0.94  # ~94% from nose to ankle
            scale = pixel_height / adjusted_height_cm
            
            return scale, confidence * nose.get('visibility', 0)
            
        return None, 0.0
    
    def _calculate_shoulder_width_scale(self, landmarks: Dict[int, Dict[str, float]], 
                                      frame_width: int) -> Tuple[Optional[float], float]:
        """Calculate scale based on shoulder width"""
        left_shoulder = landmarks.get(PoseLandmark.LEFT_SHOULDER)
        right_shoulder = landmarks.get(PoseLandmark.RIGHT_SHOULDER)
        
        if (left_shoulder and right_shoulder and 
            left_shoulder.get('visibility', 0) > self.confidence_threshold and
            right_shoulder.get('visibility', 0) > self.confidence_threshold):
            
            pixel_width = abs(left_shoulder['x'] - right_shoulder['x']) * frame_width
            expected_width_cm = self.user_height_cm * self.BODY_PROPORTIONS['shoulder_width_to_height']
            
            scale = pixel_width / expected_width_cm
            confidence = (left_shoulder['visibility'] + right_shoulder['visibility']) / 2
            
            return scale, confidence
            
        return None, 0.0
    
    def _calculate_torso_scale(self, landmarks: Dict[int, Dict[str, float]], 
                             frame_height: int) -> Tuple[Optional[float], float]:
        """Calculate scale based on torso length (shoulder to hip)"""
        left_shoulder = landmarks.get(PoseLandmark.LEFT_SHOULDER)
        right_shoulder = landmarks.get(PoseLandmark.RIGHT_SHOULDER)
        left_hip = landmarks.get(PoseLandmark.LEFT_HIP)
        right_hip = landmarks.get(PoseLandmark.RIGHT_HIP)
        
        if all([left_shoulder, right_shoulder, left_hip, right_hip]):
            visibilities = [
                left_shoulder.get('visibility', 0),
                right_shoulder.get('visibility', 0),
                left_hip.get('visibility', 0),
                right_hip.get('visibility', 0)
            ]
            
            if all(v > self.confidence_threshold for v in visibilities):
                shoulder_y = (left_shoulder['y'] + right_shoulder['y']) / 2
                hip_y = (left_hip['y'] + right_hip['y']) / 2
                
                pixel_length = abs(shoulder_y - hip_y) * frame_height
                expected_length_cm = self.user_height_cm * 0.25  # Torso is ~25% of height
                
                scale = pixel_length / expected_length_cm
                confidence = np.mean(visibilities)
                
                return scale, confidence
                
        return None, 0.0
    
    def _calculate_arm_span_scale(self, landmarks: Dict[int, Dict[str, float]], 
                                frame_width: int) -> Tuple[Optional[float], float]:
        """Calculate scale based on arm span (wrist to wrist when arms extended)"""
        left_wrist = landmarks.get(PoseLandmark.LEFT_WRIST)
        right_wrist = landmarks.get(PoseLandmark.RIGHT_WRIST)
        left_shoulder = landmarks.get(PoseLandmark.LEFT_SHOULDER)
        right_shoulder = landmarks.get(PoseLandmark.RIGHT_SHOULDER)
        
        # Check if arms are extended (wrists are far from shoulders)
        if all([left_wrist, right_wrist, left_shoulder, right_shoulder]):
            # Check if arms are reasonably extended
            left_arm_extended = abs(left_wrist['x'] - left_shoulder['x']) > 0.1
            right_arm_extended = abs(right_wrist['x'] - right_shoulder['x']) > 0.1
            
            if (left_arm_extended and right_arm_extended and
                left_wrist.get('visibility', 0) > self.confidence_threshold and
                right_wrist.get('visibility', 0) > self.confidence_threshold):
                
                pixel_span = abs(left_wrist['x'] - right_wrist['x']) * frame_width
                expected_span_cm = self.user_height_cm * self.BODY_PROPORTIONS['arm_span_to_height']
                
                scale = pixel_span / expected_span_cm
                confidence = (left_wrist['visibility'] + right_wrist['visibility']) / 2
                
                return scale, confidence
                
        return None, 0.0
    
    def _exponential_moving_average(self, values: List[float], alpha: float = 0.3) -> float:
        """Apply exponential moving average for smoothing"""
        if not values:
            return 0.0
            
        ema = values[0]
        for value in values[1:]:
            ema = alpha * value + (1 - alpha) * ema
            
        return ema
    
    def convert_to_cm(self, pixels: float) -> float:
        """Convert pixel distance to cm"""
        if self.scale_px_per_cm and self.scale_px_per_cm > 0:
            return pixels / self.scale_px_per_cm
        raise ValueError("Scale not calculated. Call calculate_multi_reference_scale() first.")
    
    def distance_px(self, p1: Dict[str, float], p2: Dict[str, float], 
                   frame_dim: Tuple[int, int]) -> float:
        """Calculate pixel distance between two points"""
        frame_width, frame_height = frame_dim
        
        # Convert normalized coordinates to pixel coordinates
        p1_px = np.array([p1['x'] * frame_width, p1['y'] * frame_height, p1.get('z', 0)])
        p2_px = np.array([p2['x'] * frame_width, p2['y'] * frame_height, p2.get('z', 0)])
        
        return float(np.linalg.norm(p1_px - p2_px))
    
    def get_scale_confidence(self) -> float:
        """Get confidence score for current scale calculation"""
        if len(self.scale_history) < 5:
            return 0.5  # Low confidence with few samples
            
        # Calculate coefficient of variation
        cv = np.std(list(self.scale_history)) / np.mean(list(self.scale_history))
        
        # Convert to confidence score (lower CV = higher confidence)
        confidence = max(0.0, min(1.0, 1.0 - cv * 2))
        
        return confidence
    
    def convert_landmarks_to_cm_enhanced(self, landmarks: Dict[int, Dict[str, float]], 
                                       frame_dim: Tuple[int, int]) -> Dict[str, Dict[str, float]]:
        """
        Convert all landmarks to cm with enhanced 3D position estimation
        """
        if not self.scale_px_per_cm:
            raise ValueError("Scale not calculated. Call calculate_multi_reference_scale() first.")
        
        frame_width, frame_height = frame_dim
        center_x, center_y = frame_width / 2, frame_height / 2
        
        joints_cm = {}
        
        # Calculate average Z-depth for torso as reference
        torso_landmarks = [
            PoseLandmark.LEFT_SHOULDER, PoseLandmark.RIGHT_SHOULDER,
            PoseLandmark.LEFT_HIP, PoseLandmark.RIGHT_HIP
        ]
        torso_z_values = []
        
        for landmark_id in torso_landmarks:
            if landmark_id in landmarks:
                torso_z_values.append(landmarks[landmark_id].get('z', 0))
                
        avg_torso_z = np.mean(torso_z_values) if torso_z_values else 0
        
        for landmark_id, landmark in landmarks.items():
            landmark_name = self._get_landmark_name(landmark_id)
            
            # Center-based coordinate system
            x_px = (landmark['x'] * frame_width - center_x)
            y_px = (center_y - landmark['y'] * frame_height)  # Y-axis up positive
            
            # Enhanced Z-depth estimation
            z_normalized = landmark.get('z', 0) - avg_torso_z
            z_px = z_normalized * frame_width * 0.5  # Scale factor for Z
            
            # Convert pixels to cm
            x_cm = self.convert_to_cm(x_px)
            y_cm = self.convert_to_cm(y_px)
            z_cm = self.convert_to_cm(z_px)
            
            joints_cm[landmark_name] = {
                'x': round(x_cm, 1),
                'y': round(y_cm, 1),
                'z': round(z_cm, 1),
                'confidence': round(landmark.get('visibility', 0), 3)
            }
        
        return joints_cm
    
    def _get_landmark_name(self, landmark_id: int) -> str:
        """Get landmark name from ID"""
        for name, value in vars(PoseLandmark).items():
            if not name.startswith('_') and value == landmark_id:
                return name
        return f"UNKNOWN_{landmark_id}"