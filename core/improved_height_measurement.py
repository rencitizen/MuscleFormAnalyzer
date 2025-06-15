"""
Improved height measurement system with enhanced accuracy
"""
import numpy as np
import mediapipe as mp
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from collections import deque
from scipy import stats
import cv2
import logging

logger = logging.getLogger(__name__)

# MediaPipe pose landmarks
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


@dataclass
class CameraValidation:
    """Camera setup validation result"""
    valid: bool
    message: str = ""
    confidence: float = 0.0


@dataclass
class HeightMeasurement:
    """Single height measurement result"""
    height: float
    confidence: float
    method: str
    timestamp: float


@dataclass
class StableHeightResult:
    """Stable height measurement result"""
    current_height: float
    stable_height: Optional[float]
    confidence: float
    recommendations: List[str]
    calibration_status: str  # 'uncalibrated', 'calibrating', 'calibrated'
    frame_count: int


class CameraCalibration:
    """Camera calibration and validation system"""
    
    @staticmethod
    def validate_camera_setup(landmarks: Any) -> CameraValidation:
        """Validate camera setup for accurate measurement"""
        if not landmarks:
            return CameraValidation(False, "ポーズが検出されませんでした", 0.0)
        
        # Get key landmarks
        nose = landmarks.landmark[mp_pose.PoseLandmark.NOSE]
        left_eye = landmarks.landmark[mp_pose.PoseLandmark.LEFT_EYE]
        right_eye = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_EYE]
        
        # Check face angle
        eye_distance_y = abs(left_eye.y - right_eye.y)
        face_width = abs(left_eye.x - right_eye.x)
        
        if face_width > 0 and eye_distance_y / face_width > 0.1:
            return CameraValidation(
                False, 
                "カメラを正面に向けてください。顔が傾いています。", 
                0.5
            )
        
        # Check distance based on shoulder width
        shoulder_width = CameraCalibration.calculate_shoulder_width(landmarks)
        if shoulder_width < 0.15:
            return CameraValidation(
                False,
                "カメラから離れてください（2-3メートル推奨）",
                0.7
            )
        if shoulder_width > 0.4:
            return CameraValidation(
                False,
                "カメラに近づいてください（2-3メートル推奨）",
                0.7
            )
        
        # Check visibility of key landmarks
        key_landmarks = [
            mp_pose.PoseLandmark.NOSE,
            mp_pose.PoseLandmark.LEFT_SHOULDER,
            mp_pose.PoseLandmark.RIGHT_SHOULDER,
            mp_pose.PoseLandmark.LEFT_HIP,
            mp_pose.PoseLandmark.RIGHT_HIP,
            mp_pose.PoseLandmark.LEFT_ANKLE,
            mp_pose.PoseLandmark.RIGHT_ANKLE
        ]
        
        visibilities = []
        for landmark_id in key_landmarks:
            landmark = landmarks.landmark[landmark_id]
            visibilities.append(landmark.visibility)
        
        avg_visibility = np.mean(visibilities)
        
        if avg_visibility < 0.6:
            return CameraValidation(
                False,
                "全身が見えるようにカメラを調整してください",
                avg_visibility
            )
        
        return CameraValidation(True, confidence=avg_visibility)
    
    @staticmethod
    def calculate_shoulder_width(landmarks: Any) -> float:
        """Calculate normalized shoulder width"""
        left_shoulder = landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        
        return abs(right_shoulder.x - left_shoulder.x)
    
    @staticmethod
    def calculate_distance_correction(landmarks: Any) -> Tuple[float, str]:
        """Calculate distance correction factor"""
        # Method 1: Eye distance
        left_eye = landmarks.landmark[mp_pose.PoseLandmark.LEFT_EYE]
        right_eye = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_EYE]
        
        if left_eye.visibility > 0.8 and right_eye.visibility > 0.8:
            eye_distance = np.sqrt(
                (right_eye.x - left_eye.x)**2 + 
                (right_eye.y - left_eye.y)**2
            )
            # Average interpupillary distance at standard distance
            average_eye_distance = 0.063
            correction = average_eye_distance / eye_distance
            return correction, 'eye_distance'
        
        # Method 2: Shoulder width
        shoulder_width = CameraCalibration.calculate_shoulder_width(landmarks)
        if shoulder_width > 0:
            average_shoulder_width = 0.25
            correction = average_shoulder_width / shoulder_width
            return correction, 'shoulder_width'
        
        return 1.0, 'default'


class ImprovedHeightMeasurement:
    """Improved height measurement algorithms"""
    
    @staticmethod
    def find_accurate_head_top(landmarks: Any) -> Tuple[float, float, float]:
        """Find accurate head top position"""
        # Use multiple landmarks to estimate head top
        nose = landmarks.landmark[mp_pose.PoseLandmark.NOSE]
        left_ear = landmarks.landmark[mp_pose.PoseLandmark.LEFT_EAR]
        right_ear = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_EAR]
        
        # Estimate head top based on nose and ears
        head_landmarks = [nose]
        if left_ear.visibility > 0.5:
            head_landmarks.append(left_ear)
        if right_ear.visibility > 0.5:
            head_landmarks.append(right_ear)
        
        # Find highest point
        head_top_y = min(lm.y for lm in head_landmarks)
        head_top_x = np.mean([lm.x for lm in head_landmarks])
        
        # Add offset for hair (2% of frame height)
        head_top_y -= 0.02
        
        avg_visibility = np.mean([lm.visibility for lm in head_landmarks])
        
        return head_top_x, head_top_y, avg_visibility
    
    @staticmethod
    def find_accurate_feet(landmarks: Any) -> Tuple[float, float, float]:
        """Find accurate feet bottom position"""
        feet_landmarks = []
        
        # Collect all foot-related landmarks
        foot_indices = [
            mp_pose.PoseLandmark.LEFT_ANKLE,
            mp_pose.PoseLandmark.RIGHT_ANKLE,
            mp_pose.PoseLandmark.LEFT_HEEL,
            mp_pose.PoseLandmark.RIGHT_HEEL,
            mp_pose.PoseLandmark.LEFT_FOOT_INDEX,
            mp_pose.PoseLandmark.RIGHT_FOOT_INDEX
        ]
        
        for idx in foot_indices:
            landmark = landmarks.landmark[idx]
            if landmark.visibility > 0.3:
                feet_landmarks.append(landmark)
        
        if not feet_landmarks:
            # Fallback to ankles
            left_ankle = landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE]
            right_ankle = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE]
            
            feet_bottom_y = max(left_ankle.y, right_ankle.y)
            feet_x = (left_ankle.x + right_ankle.x) / 2
            avg_visibility = (left_ankle.visibility + right_ankle.visibility) / 2
        else:
            # Find lowest point
            feet_bottom_y = max(lm.y for lm in feet_landmarks)
            feet_x = np.mean([lm.x for lm in feet_landmarks])
            avg_visibility = np.mean([lm.visibility for lm in feet_landmarks])
        
        return feet_x, feet_bottom_y, avg_visibility
    
    @staticmethod
    def calculate_height(
        landmarks: Any,
        frame_height: int,
        frame_width: int,
        reference_height: Optional[float] = None,
        distance_correction: float = 1.0
    ) -> Dict[str, Any]:
        """Calculate height with multiple methods"""
        
        # Find head and feet positions
        head_x, head_y, head_confidence = ImprovedHeightMeasurement.find_accurate_head_top(landmarks)
        feet_x, feet_y, feet_confidence = ImprovedHeightMeasurement.find_accurate_feet(landmarks)
        
        # Calculate pixel height
        height_in_pixels = abs(feet_y - head_y) * frame_height
        
        # If reference height provided, use for calibration
        if reference_height:
            return {
                'height': reference_height,
                'method': 'user_calibrated',
                'confidence': 1.0
            }
        
        # Method 1: Body proportion based
        shoulder_width = CameraCalibration.calculate_shoulder_width(landmarks)
        if 0.15 < shoulder_width < 0.4:
            # Average human height to shoulder width ratio is approximately 3.8-4.2
            proportion_based_height = (height_in_pixels / (shoulder_width * frame_width)) * 42 * distance_correction
            
            return {
                'height': proportion_based_height,
                'method': 'proportion_based',
                'confidence': (head_confidence + feet_confidence) / 2 * 0.9
            }
        
        # Method 2: Direct conversion with empirical factor
        # This factor needs to be calibrated for your specific setup
        empirical_factor = 2850
        direct_height = (height_in_pixels / frame_height) * empirical_factor * distance_correction
        
        return {
            'height': direct_height,
            'method': 'direct_conversion',
            'confidence': (head_confidence + feet_confidence) / 2 * 0.7
        }


class MultiFrameHeightMeasurement:
    """Multi-frame measurement for stability"""
    
    def __init__(self, max_measurements: int = 30):
        self.measurements: deque = deque(maxlen=max_measurements)
        self.max_measurements = max_measurements
    
    def add_measurement(self, height: float, confidence: float, method: str, timestamp: float):
        """Add a new measurement"""
        measurement = HeightMeasurement(
            height=height,
            confidence=confidence,
            method=method,
            timestamp=timestamp
        )
        self.measurements.append(measurement)
    
    def get_stable_height(self) -> Optional[float]:
        """Get stable height from multiple measurements"""
        if len(self.measurements) < 10:
            return None
        
        # Filter by confidence
        reliable_measurements = [
            m for m in self.measurements 
            if m.confidence > 0.7
        ]
        
        if len(reliable_measurements) < 5:
            return None
        
        # Extract heights
        heights = [m.height for m in reliable_measurements]
        
        # Remove outliers using IQR method
        q1 = np.percentile(heights, 25)
        q3 = np.percentile(heights, 75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        filtered_heights = [
            h for h in heights 
            if lower_bound <= h <= upper_bound
        ]
        
        if not filtered_heights:
            # If all are outliers, use median of original
            return np.median(heights)
        
        # Return median of filtered heights
        return np.median(filtered_heights)
    
    def get_confidence(self) -> float:
        """Get overall confidence score"""
        if len(self.measurements) < 5:
            return 0.0
        
        recent_measurements = list(self.measurements)[-10:]
        heights = [m.height for m in recent_measurements]
        
        if not heights:
            return 0.0
        
        # Calculate coefficient of variation
        mean_height = np.mean(heights)
        std_height = np.std(heights)
        
        if mean_height == 0:
            return 0.0
        
        cv = std_height / mean_height
        
        # Convert to confidence (lower CV = higher confidence)
        confidence = max(0.0, min(1.0, 1.0 - cv * 5))
        
        return confidence
    
    def clear(self):
        """Clear all measurements"""
        self.measurements.clear()


class AccurateHeightMeasurementSystem:
    """Main height measurement system"""
    
    def __init__(self):
        self.multi_frame = MultiFrameHeightMeasurement()
        self.calibration_factor: Optional[float] = None
        self.user_height: Optional[float] = None
        self.is_calibrated = False
        self.pose = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=2,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.frame_count = 0
    
    def process_frame(
        self,
        frame: np.ndarray,
        user_input_height: Optional[float] = None
    ) -> StableHeightResult:
        """Process a single frame for height measurement"""
        self.frame_count += 1
        
        # Convert BGR to RGB if needed
        if len(frame.shape) == 3 and frame.shape[2] == 3:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        else:
            rgb_frame = frame
        
        # Process with MediaPipe
        results = self.pose.process(rgb_frame)
        
        if not results.pose_landmarks:
            return StableHeightResult(
                current_height=0,
                stable_height=None,
                confidence=0,
                recommendations=["ポーズが検出されませんでした。全身がカメラに映るようにしてください。"],
                calibration_status='uncalibrated',
                frame_count=self.frame_count
            )
        
        # Validate camera setup
        validation = CameraCalibration.validate_camera_setup(results.pose_landmarks)
        if not validation.valid:
            return StableHeightResult(
                current_height=0,
                stable_height=None,
                confidence=validation.confidence,
                recommendations=[validation.message],
                calibration_status='uncalibrated',
                frame_count=self.frame_count
            )
        
        # Calculate distance correction
        distance_correction, correction_method = CameraCalibration.calculate_distance_correction(
            results.pose_landmarks
        )
        
        # Handle user calibration
        if user_input_height:
            self.user_height = user_input_height
            self.is_calibrated = True
            
            # Calculate calibration factor
            measured_result = ImprovedHeightMeasurement.calculate_height(
                results.pose_landmarks,
                frame.shape[0],
                frame.shape[1],
                None,
                distance_correction
            )
            
            self.calibration_factor = user_input_height / measured_result['height']
        
        # Measure height
        measured_result = ImprovedHeightMeasurement.calculate_height(
            results.pose_landmarks,
            frame.shape[0],
            frame.shape[1],
            self.user_height,
            distance_correction
        )
        
        # Apply calibration if available
        if self.calibration_factor and not self.user_height:
            measured_result['height'] *= self.calibration_factor
        
        # Add to multi-frame measurement
        import time
        self.multi_frame.add_measurement(
            measured_result['height'],
            measured_result['confidence'],
            measured_result['method'],
            time.time()
        )
        
        # Get stable height
        stable_height = self.multi_frame.get_stable_height()
        overall_confidence = self.multi_frame.get_confidence()
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            results.pose_landmarks,
            measured_result['confidence'],
            overall_confidence
        )
        
        # Determine calibration status
        if self.is_calibrated:
            calibration_status = 'calibrated'
        elif stable_height is not None:
            calibration_status = 'calibrating'
        else:
            calibration_status = 'uncalibrated'
        
        return StableHeightResult(
            current_height=round(measured_result['height']),
            stable_height=round(stable_height) if stable_height else None,
            confidence=overall_confidence,
            recommendations=recommendations,
            calibration_status=calibration_status,
            frame_count=self.frame_count
        )
    
    def _generate_recommendations(
        self,
        landmarks: Any,
        current_confidence: float,
        overall_confidence: float
    ) -> List[str]:
        """Generate recommendations for better measurement"""
        recommendations = []
        
        if overall_confidence < 0.7:
            recommendations.append("測定精度を上げるため、明るい場所で撮影してください")
        
        # Check posture
        left_shoulder = landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        shoulder_tilt = abs(left_shoulder.y - right_shoulder.y)
        
        if shoulder_tilt > 0.02:
            recommendations.append("背筋を伸ばして直立してください")
        
        # Check full body visibility
        key_landmarks = [
            mp_pose.PoseLandmark.NOSE,
            mp_pose.PoseLandmark.LEFT_ANKLE,
            mp_pose.PoseLandmark.RIGHT_ANKLE
        ]
        
        for landmark_id in key_landmarks:
            if landmarks.landmark[landmark_id].visibility < 0.5:
                recommendations.append("全身（頭から足まで）がカメラに映るようにしてください")
                break
        
        if not self.is_calibrated:
            recommendations.append("より正確な測定のため、実際の身長を入力して較正することをお勧めします")
        
        if not recommendations and overall_confidence > 0.85:
            recommendations.append("測定条件は良好です")
        
        return recommendations
    
    def reset(self):
        """Reset the measurement system"""
        self.multi_frame.clear()
        self.calibration_factor = None
        self.user_height = None
        self.is_calibrated = False
        self.frame_count = 0
    
    def close(self):
        """Clean up resources"""
        if self.pose:
            self.pose.close()


# Utility functions for video processing
def process_video_for_height(
    video_path: str,
    reference_height: Optional[float] = None,
    progress_callback: Optional[callable] = None
) -> Dict[str, Any]:
    """Process entire video for height measurement"""
    
    system = AccurateHeightMeasurementSystem()
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    # Process every nth frame to reduce computation
    frame_skip = max(1, int(fps / 5))  # Process 5 frames per second
    
    results = []
    frame_count = 0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_skip == 0:
                result = system.process_frame(frame, reference_height)
                results.append(result)
                
                if progress_callback:
                    progress = (frame_count / total_frames) * 100
                    progress_callback(progress)
            
            frame_count += 1
            
            # Limit processing to avoid very long videos
            if len(results) > 100:
                break
    
    finally:
        cap.release()
        system.close()
    
    # Find best result
    if not results:
        return {
            'success': False,
            'error': 'No valid measurements found'
        }
    
    # Get the most confident stable result
    best_result = max(
        (r for r in results if r.stable_height is not None),
        key=lambda r: r.confidence,
        default=results[-1]
    )
    
    return {
        'success': True,
        'height': best_result.stable_height or best_result.current_height,
        'confidence': best_result.confidence,
        'calibration_status': best_result.calibration_status,
        'recommendations': best_result.recommendations,
        'total_frames_processed': len(results)
    }


# Example usage
if __name__ == "__main__":
    # Example: Process a single frame
    system = AccurateHeightMeasurementSystem()
    
    # Simulate processing frames
    import numpy as np
    dummy_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    
    for i in range(30):
        result = system.process_frame(dummy_frame)
        print(f"Frame {i}: Current={result.current_height}cm, "
              f"Stable={result.stable_height}cm, "
              f"Confidence={result.confidence:.2f}")
    
    system.close()