"""
Height Analyzer Service
Provides accurate height measurement from video using computer vision
"""
import logging
from typing import Optional, List, Tuple, Dict
import cv2
import numpy as np
import mediapipe as mp
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ReferenceObject:
    """Known reference objects for scale calibration"""
    name: str
    height_mm: float
    width_mm: float
    detection_method: str

# Common reference objects
REFERENCE_OBJECTS = {
    "credit_card": ReferenceObject("Credit Card", 53.98, 85.60, "template_matching"),
    "a4_paper": ReferenceObject("A4 Paper", 210.0, 297.0, "contour_detection"),
    "smartphone": ReferenceObject("Standard Smartphone", 140.0, 70.0, "template_matching"),
    "door_frame": ReferenceObject("Standard Door Frame", 2030.0, 900.0, "line_detection"),
}

class HeightAnalyzer:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.pose = None
        
    def analyze_video(
        self, 
        video_path: str, 
        reference_object: Optional[str] = None,
        reference_height_mm: Optional[float] = None
    ) -> Dict:
        """
        Analyze video to estimate person's height
        
        Args:
            video_path: Path to video file
            reference_object: Type of reference object (if any)
            reference_height_mm: Custom reference object height in mm
            
        Returns:
            Dictionary with height estimation results
        """
        try:
            self.pose = self.mp_pose.Pose(
                static_image_mode=False,
                model_complexity=2,
                enable_segmentation=True,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.7
            )
            
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return {"success": False, "error": "Failed to open video file"}
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Sample frames at intervals
            sample_interval = max(1, int(fps / 10))  # 10 samples per second
            frame_measurements = []
            reference_scale = None
            
            frame_idx = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_idx % sample_interval == 0:
                    # Detect reference object if specified
                    if reference_object and reference_scale is None:
                        scale_result = self._detect_reference_object(
                            frame, reference_object, reference_height_mm
                        )
                        if scale_result:
                            reference_scale = scale_result
                            logger.info(f"Reference object detected: scale={reference_scale:.4f}")
                    
                    # Analyze pose
                    height_result = self._analyze_frame_height(frame, reference_scale)
                    if height_result:
                        frame_measurements.append(height_result)
                
                frame_idx += 1
                
                # Limit analysis to prevent excessive processing
                if frame_idx > total_frames * 0.8 or len(frame_measurements) > 100:
                    break
            
            cap.release()
            
            if not frame_measurements:
                return {
                    "success": False,
                    "error": "No valid height measurements extracted from video"
                }
            
            # Calculate final height estimation
            result = self._calculate_final_height(frame_measurements)
            result["reference_object_used"] = reference_object is not None
            result["reference_scale"] = reference_scale
            
            return result
            
        except Exception as e:
            logger.error(f"Height analysis error: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
        finally:
            if self.pose:
                self.pose.close()
    
    def _analyze_frame_height(
        self, 
        frame: np.ndarray, 
        reference_scale: Optional[float] = None
    ) -> Optional[Dict]:
        """Analyze single frame for height estimation"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_frame)
        
        if not results.pose_landmarks:
            return None
        
        landmarks = results.pose_landmarks.landmark
        h, w = frame.shape[:2]
        
        # Extract key body points
        body_points = self._extract_body_keypoints(landmarks, h, w)
        if not body_points:
            return None
        
        # Calculate pixel height
        pixel_height = body_points["pixel_height"]
        
        # Estimate real height
        if reference_scale:
            # Use reference object scale
            height_cm = pixel_height * reference_scale / 10
        else:
            # Use statistical body proportion estimation
            height_cm = self._estimate_height_from_proportions(body_points, h)
        
        # Validate reasonable height range
        if not (120 < height_cm < 220):
            return None
        
        return {
            "height_cm": height_cm,
            "pixel_height": pixel_height,
            "confidence": body_points["confidence"],
            "pose_quality": body_points["pose_quality"]
        }
    
    def _extract_body_keypoints(
        self, 
        landmarks, 
        height: int, 
        width: int
    ) -> Optional[Dict]:
        """Extract and validate body keypoints for height measurement"""
        try:
            # Get critical landmarks
            nose = landmarks[self.mp_pose.PoseLandmark.NOSE]
            left_eye = landmarks[self.mp_pose.PoseLandmark.LEFT_EYE]
            right_eye = landmarks[self.mp_pose.PoseLandmark.RIGHT_EYE]
            left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
            left_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP]
            right_hip = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP]
            left_ankle = landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE]
            right_ankle = landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE]
            left_heel = landmarks[self.mp_pose.PoseLandmark.LEFT_HEEL]
            right_heel = landmarks[self.mp_pose.PoseLandmark.RIGHT_HEEL]
            
            # Calculate visibility confidence
            visibility_scores = [
                nose.visibility,
                (left_shoulder.visibility + right_shoulder.visibility) / 2,
                (left_hip.visibility + right_hip.visibility) / 2,
                (left_ankle.visibility + right_ankle.visibility) / 2,
                (left_heel.visibility + right_heel.visibility) / 2
            ]
            
            avg_visibility = sum(visibility_scores) / len(visibility_scores)
            
            if avg_visibility < 0.6:
                return None
            
            # Calculate head top approximation
            eye_center_y = (left_eye.y + right_eye.y) / 2 * height
            nose_y = nose.y * height
            head_offset = abs(eye_center_y - nose_y) * 1.3  # Approximate head top
            head_top_y = min(eye_center_y, nose_y) - head_offset
            
            # Calculate feet position
            heel_y = (left_heel.y + right_heel.y) / 2 * height
            ankle_y = (left_ankle.y + right_ankle.y) / 2 * height
            feet_y = max(heel_y, ankle_y)
            
            # Calculate pixel height
            pixel_height = feet_y - head_top_y
            
            # Check pose quality (standing straight)
            shoulder_level = abs(left_shoulder.y - right_shoulder.y) * height
            hip_level = abs(left_hip.y - right_hip.y) * height
            pose_quality = 1.0 - (shoulder_level + hip_level) / (2 * pixel_height)
            
            return {
                "pixel_height": pixel_height,
                "head_top_y": head_top_y,
                "feet_y": feet_y,
                "shoulder_width": abs(left_shoulder.x - right_shoulder.x) * width,
                "hip_width": abs(left_hip.x - right_hip.x) * width,
                "confidence": avg_visibility,
                "pose_quality": pose_quality
            }
            
        except Exception as e:
            logger.error(f"Keypoint extraction error: {e}")
            return None
    
    def _estimate_height_from_proportions(
        self, 
        body_points: Dict, 
        frame_height: int
    ) -> float:
        """Estimate height using body proportions and camera perspective"""
        pixel_height = body_points["pixel_height"]
        
        # Estimate camera distance based on body width in frame
        shoulder_width_ratio = body_points["shoulder_width"] / frame_height
        
        # Average human shoulder width is ~45cm
        # Use this to estimate scale
        avg_shoulder_width_cm = 45
        estimated_scale = avg_shoulder_width_cm / (shoulder_width_ratio * frame_height)
        
        # Apply perspective correction
        # People further from camera appear smaller
        perspective_factor = 1.0 + (0.2 * (1.0 - shoulder_width_ratio))
        
        # Estimate height
        height_cm = pixel_height * estimated_scale * perspective_factor
        
        return height_cm
    
    def _detect_reference_object(
        self, 
        frame: np.ndarray, 
        object_type: str,
        custom_height_mm: Optional[float] = None
    ) -> Optional[float]:
        """Detect reference object and calculate scale factor"""
        if object_type == "credit_card":
            return self._detect_credit_card(frame, custom_height_mm)
        elif object_type == "a4_paper":
            return self._detect_a4_paper(frame, custom_height_mm)
        elif object_type == "custom" and custom_height_mm:
            return self._detect_custom_marker(frame, custom_height_mm)
        
        return None
    
    def _detect_credit_card(
        self, 
        frame: np.ndarray,
        height_mm: Optional[float] = None
    ) -> Optional[float]:
        """Detect credit card using edge detection and aspect ratio"""
        height_mm = height_mm or REFERENCE_OBJECTS["credit_card"].height_mm
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 1000:  # Too small
                continue
            
            # Approximate polygon
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            if len(approx) == 4:  # Rectangle
                rect = cv2.minAreaRect(contour)
                width, height = rect[1]
                
                if width < height:
                    width, height = height, width
                
                # Check aspect ratio (credit card is 1.586:1)
                aspect_ratio = width / height
                if 1.5 < aspect_ratio < 1.7:
                    # Found credit card
                    pixel_height = height
                    scale = height_mm / pixel_height  # mm per pixel
                    return scale
        
        return None
    
    def _detect_a4_paper(
        self, 
        frame: np.ndarray,
        height_mm: Optional[float] = None
    ) -> Optional[float]:
        """Detect A4 paper using contour detection"""
        height_mm = height_mm or REFERENCE_OBJECTS["a4_paper"].height_mm
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive threshold for paper detection
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Find largest rectangular contour
        max_area = 0
        best_rect = None
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 10000:  # Too small for A4
                continue
            
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            if len(approx) == 4:
                rect = cv2.minAreaRect(contour)
                width, height = rect[1]
                
                if width < height:
                    width, height = height, width
                
                # Check A4 aspect ratio (1.414:1)
                aspect_ratio = width / height
                if 1.3 < aspect_ratio < 1.5 and area > max_area:
                    max_area = area
                    best_rect = (width, height)
        
        if best_rect:
            pixel_height = best_rect[1]
            scale = height_mm / pixel_height
            return scale
        
        return None
    
    def _detect_custom_marker(
        self, 
        frame: np.ndarray, 
        height_mm: float
    ) -> Optional[float]:
        """Detect custom ArUco marker for precise calibration"""
        try:
            import cv2.aruco as aruco
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
            parameters = aruco.DetectorParameters_create()
            
            corners, ids, _ = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
            
            if ids is not None and len(corners) > 0:
                # Use first detected marker
                marker_corners = corners[0][0]
                
                # Calculate marker size in pixels
                marker_height = np.linalg.norm(marker_corners[0] - marker_corners[3])
                
                # Calculate scale
                scale = height_mm / marker_height
                return scale
                
        except ImportError:
            logger.warning("ArUco not available for custom marker detection")
        
        return None
    
    def _calculate_final_height(self, measurements: List[Dict]) -> Dict:
        """Calculate final height from multiple measurements"""
        heights = [m["height_cm"] for m in measurements]
        confidences = [m["confidence"] for m in measurements]
        pose_qualities = [m["pose_quality"] for m in measurements]
        
        # Weight measurements by confidence and pose quality
        weights = [c * p for c, p in zip(confidences, pose_qualities)]
        
        # Remove outliers using IQR
        q1 = np.percentile(heights, 25)
        q3 = np.percentile(heights, 75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        filtered_data = [
            (h, w) for h, w in zip(heights, weights)
            if lower_bound <= h <= upper_bound
        ]
        
        if not filtered_data:
            filtered_data = list(zip(heights, weights))
        
        filtered_heights, filtered_weights = zip(*filtered_data)
        
        # Calculate weighted average
        weighted_height = np.average(filtered_heights, weights=filtered_weights)
        
        # Calculate confidence based on consistency
        height_std = np.std(filtered_heights)
        consistency_score = 1.0 - min(height_std / weighted_height, 0.1) * 10
        
        # Overall confidence
        avg_confidence = np.mean(confidences)
        avg_pose_quality = np.mean(pose_qualities)
        final_confidence = (consistency_score * 0.5 + 
                          avg_confidence * 0.3 + 
                          avg_pose_quality * 0.2)
        
        return {
            "success": True,
            "height_cm": round(weighted_height, 1),
            "confidence": round(final_confidence, 3),
            "measurements_count": len(measurements),
            "filtered_count": len(filtered_data),
            "height_std": round(height_std, 2),
            "consistency_score": round(consistency_score, 3)
        }