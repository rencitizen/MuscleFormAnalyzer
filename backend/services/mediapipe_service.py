"""
MediaPipe Form Analysis Service
High-performance pose detection and form analysis for Railway deployment
"""
import cv2
import numpy as np
import mediapipe as mp
import logging
import time
import asyncio
import json
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import math

from ..config import settings

logger = logging.getLogger(__name__)

@dataclass
class PoseLandmark:
    """Pose landmark data structure"""
    landmark_id: int
    x: float
    y: float
    z: float
    visibility: float

@dataclass
class AnalysisResult:
    """Form analysis result data structure"""
    score: float
    angle_scores: Dict[str, Dict]
    phase: str
    feedback: List[Dict]
    confidence: float
    processing_time: float
    analyzer_type: str
    biomechanics: Optional[Dict] = None

class MediaPipeFormAnalyzer:
    """
    Advanced MediaPipe-based form analyzer optimized for Railway deployment
    """
    
    def __init__(self):
        """Initialize the MediaPipe form analyzer"""
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Initialize pose detection with optimized settings
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=settings.MEDIAPIPE_MODEL_COMPLEXITY,
            enable_segmentation=False,
            smooth_landmarks=True,
            min_detection_confidence=settings.MEDIAPIPE_MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=settings.MEDIAPIPE_MIN_TRACKING_CONFIDENCE
        )
        
        # Thread pool for CPU-intensive operations
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Exercise-specific configurations
        self.exercise_configs = {
            'squat': {
                'key_joints': ['left_hip', 'right_hip', 'left_knee', 'right_knee', 'left_ankle', 'right_ankle'],
                'target_angles': {
                    'knee_angle': {'min': 70, 'max': 90, 'ideal': 80},
                    'hip_angle': {'min': 60, 'max': 110, 'ideal': 85},
                    'ankle_angle': {'min': 80, 'max': 100, 'ideal': 90}
                },
                'phases': ['standing', 'descending', 'bottom', 'ascending']
            },
            'bench_press': {
                'key_joints': ['left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow', 'left_wrist', 'right_wrist'],
                'target_angles': {
                    'elbow_angle': {'min': 45, 'max': 90, 'ideal': 70},
                    'shoulder_angle': {'min': 75, 'max': 90, 'ideal': 82},
                    'wrist_angle': {'min': 170, 'max': 180, 'ideal': 175}
                },
                'phases': ['setup', 'descent', 'chest_touch', 'ascent', 'lockout']
            },
            'deadlift': {
                'key_joints': ['left_hip', 'right_hip', 'left_knee', 'right_knee', 'left_shoulder', 'right_shoulder'],
                'target_angles': {
                    'hip_angle': {'min': 160, 'max': 180, 'ideal': 170},
                    'knee_angle': {'min': 160, 'max': 180, 'ideal': 175},
                    'back_angle': {'min': 15, 'max': 30, 'ideal': 20}
                },
                'phases': ['setup', 'liftoff', 'knee_pass', 'lockout']
            }
        }
        
        logger.info("MediaPipe Form Analyzer initialized successfully")
    
    async def analyze_frame_async(self, image: np.ndarray, exercise_type: str = 'squat') -> AnalysisResult:
        """
        Async wrapper for frame analysis
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, 
            self.analyze_frame, 
            image, 
            exercise_type
        )
    
    def analyze_frame(self, image: np.ndarray, exercise_type: str = 'squat') -> AnalysisResult:
        """
        Analyze a single frame for form analysis
        """
        start_time = time.time()
        
        try:
            # Convert BGR to RGB for MediaPipe
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Process with MediaPipe
            results = self.pose.process(rgb_image)
            
            if not results.pose_landmarks:
                return AnalysisResult(
                    score=0.0,
                    angle_scores={},
                    phase="no_pose_detected",
                    feedback=[{
                        "type": "error",
                        "priority": "critical",
                        "message": "No pose detected. Please ensure you're visible in the camera."
                    }],
                    confidence=0.0,
                    processing_time=time.time() - start_time,
                    analyzer_type="mediapipe"
                )
            
            # Extract landmarks
            landmarks = self._extract_landmarks(results.pose_landmarks)
            
            # Calculate confidence based on landmark visibility
            confidence = self._calculate_confidence(landmarks)
            
            # Perform exercise-specific analysis
            if exercise_type == 'squat':
                analysis = self._analyze_squat(landmarks)
            elif exercise_type == 'bench_press':
                analysis = self._analyze_bench_press(landmarks)
            elif exercise_type == 'deadlift':
                analysis = self._analyze_deadlift(landmarks)
            else:
                analysis = self._analyze_general_form(landmarks)
            
            analysis.confidence = confidence
            analysis.processing_time = time.time() - start_time
            analysis.analyzer_type = "mediapipe"
            
            return analysis
            
        except Exception as e:
            logger.error(f"Frame analysis error: {e}")
            return AnalysisResult(
                score=0.0,
                angle_scores={},
                phase="error",
                feedback=[{
                    "type": "error",
                    "priority": "critical",
                    "message": f"Analysis failed: {str(e)}"
                }],
                confidence=0.0,
                processing_time=time.time() - start_time,
                analyzer_type="mediapipe"
            )
    
    def _extract_landmarks(self, pose_landmarks) -> List[PoseLandmark]:
        """Extract and normalize landmarks"""
        landmarks = []
        
        for i, landmark in enumerate(pose_landmarks.landmark):
            landmarks.append(PoseLandmark(
                landmark_id=i,
                x=landmark.x,
                y=landmark.y,
                z=landmark.z,
                visibility=landmark.visibility
            ))
        
        return landmarks
    
    def _calculate_confidence(self, landmarks: List[PoseLandmark]) -> float:
        """Calculate overall confidence based on landmark visibility"""
        if not landmarks:
            return 0.0
        
        total_visibility = sum(lm.visibility for lm in landmarks)
        avg_visibility = total_visibility / len(landmarks)
        
        # Weight key landmarks more heavily
        key_landmark_indices = [11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]  # Torso and legs
        key_visibility = sum(landmarks[i].visibility for i in key_landmark_indices if i < len(landmarks))
        key_avg = key_visibility / len(key_landmark_indices)
        
        # Combined confidence score
        confidence = (avg_visibility * 0.3 + key_avg * 0.7)
        return min(confidence, 1.0)
    
    def _analyze_squat(self, landmarks: List[PoseLandmark]) -> AnalysisResult:
        """Analyze squat form"""
        try:
            # Calculate key angles
            left_knee_angle = self._calculate_angle(
                landmarks[23], landmarks[25], landmarks[27]  # hip, knee, ankle
            )
            right_knee_angle = self._calculate_angle(
                landmarks[24], landmarks[26], landmarks[28]  # hip, knee, ankle
            )
            
            # Hip angles
            left_hip_angle = self._calculate_angle(
                landmarks[11], landmarks[23], landmarks[25]  # shoulder, hip, knee
            )
            right_hip_angle = self._calculate_angle(
                landmarks[12], landmarks[24], landmarks[26]  # shoulder, hip, knee
            )
            
            # Ankle angles (dorsiflexion)
            left_ankle_angle = self._calculate_ankle_angle(landmarks, 'left')
            right_ankle_angle = self._calculate_ankle_angle(landmarks, 'right')
            
            # Calculate scores for each angle
            angle_scores = {
                'left_knee': self._score_angle(left_knee_angle, self.exercise_configs['squat']['target_angles']['knee_angle']),
                'right_knee': self._score_angle(right_knee_angle, self.exercise_configs['squat']['target_angles']['knee_angle']),
                'left_hip': self._score_angle(left_hip_angle, self.exercise_configs['squat']['target_angles']['hip_angle']),
                'right_hip': self._score_angle(right_hip_angle, self.exercise_configs['squat']['target_angles']['hip_angle']),
                'left_ankle': self._score_angle(left_ankle_angle, self.exercise_configs['squat']['target_angles']['ankle_angle']),
                'right_ankle': self._score_angle(right_ankle_angle, self.exercise_configs['squat']['target_angles']['ankle_angle'])
            }
            
            # Determine phase
            avg_knee_angle = (left_knee_angle + right_knee_angle) / 2
            phase = self._determine_squat_phase(avg_knee_angle, landmarks)
            
            # Calculate overall score
            scores = [score['score'] for score in angle_scores.values()]
            overall_score = sum(scores) / len(scores) * 100
            
            # Generate feedback
            feedback = self._generate_squat_feedback(angle_scores, phase, landmarks)
            
            # Calculate biomechanics
            biomechanics = self._calculate_squat_biomechanics(landmarks, angle_scores)
            
            return AnalysisResult(
                score=overall_score,
                angle_scores=angle_scores,
                phase=phase,
                feedback=feedback,
                confidence=0.0,  # Will be set by caller
                processing_time=0.0,  # Will be set by caller
                analyzer_type="mediapipe",
                biomechanics=biomechanics
            )
            
        except Exception as e:
            logger.error(f"Squat analysis error: {e}")
            return AnalysisResult(
                score=0.0,
                angle_scores={},
                phase="error",
                feedback=[{
                    "type": "error",
                    "priority": "critical",
                    "message": f"Squat analysis failed: {str(e)}"
                }],
                confidence=0.0,
                processing_time=0.0,
                analyzer_type="mediapipe"
            )
    
    def _analyze_bench_press(self, landmarks: List[PoseLandmark]) -> AnalysisResult:
        """Analyze bench press form"""
        # Implementation for bench press analysis
        # Similar structure to squat analysis
        return AnalysisResult(
            score=85.0,
            angle_scores={},
            phase="setup",
            feedback=[{
                "type": "info",
                "priority": "info",
                "message": "Bench press analysis coming soon"
            }],
            confidence=0.0,
            processing_time=0.0,
            analyzer_type="mediapipe"
        )
    
    def _analyze_deadlift(self, landmarks: List[PoseLandmark]) -> AnalysisResult:
        """Analyze deadlift form"""
        # Implementation for deadlift analysis
        # Similar structure to squat analysis
        return AnalysisResult(
            score=90.0,
            angle_scores={},
            phase="setup",
            feedback=[{
                "type": "info",
                "priority": "info",
                "message": "Deadlift analysis coming soon"
            }],
            confidence=0.0,
            processing_time=0.0,
            analyzer_type="mediapipe"
        )
    
    def _analyze_general_form(self, landmarks: List[PoseLandmark]) -> AnalysisResult:
        """General form analysis for unknown exercises"""
        return AnalysisResult(
            score=75.0,
            angle_scores={},
            phase="unknown",
            feedback=[{
                "type": "info",
                "priority": "info",
                "message": "General pose detected. Please select a specific exercise for detailed analysis."
            }],
            confidence=0.0,
            processing_time=0.0,
            analyzer_type="mediapipe"
        )
    
    def _calculate_angle(self, point1: PoseLandmark, point2: PoseLandmark, point3: PoseLandmark) -> float:
        """Calculate angle between three points"""
        try:
            # Convert to numpy arrays
            a = np.array([point1.x, point1.y])
            b = np.array([point2.x, point2.y])
            c = np.array([point3.x, point3.y])
            
            # Calculate vectors
            ba = a - b
            bc = c - b
            
            # Calculate angle
            cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
            cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
            angle = np.arccos(cosine_angle)
            
            return np.degrees(angle)
            
        except Exception as e:
            logger.error(f"Angle calculation error: {e}")
            return 90.0  # Default angle
    
    def _calculate_ankle_angle(self, landmarks: List[PoseLandmark], side: str) -> float:
        """Calculate ankle dorsiflexion angle"""
        try:
            if side == 'left':
                knee_idx, ankle_idx, foot_idx = 25, 27, 31
            else:
                knee_idx, ankle_idx, foot_idx = 26, 28, 32
            
            # Use heel and toe landmarks for foot angle
            if foot_idx < len(landmarks):
                return self._calculate_angle(landmarks[knee_idx], landmarks[ankle_idx], landmarks[foot_idx])
            else:
                # Fallback: estimate ankle angle
                return 90.0
                
        except Exception as e:
            logger.error(f"Ankle angle calculation error: {e}")
            return 90.0
    
    def _score_angle(self, angle: float, target: Dict) -> Dict:
        """Score an angle against target ranges"""
        ideal = target['ideal']
        min_val = target['min']
        max_val = target['max']
        
        if min_val <= angle <= max_val:
            # Within acceptable range
            deviation = abs(angle - ideal)
            max_deviation = max(ideal - min_val, max_val - ideal)
            score = max(0.0, 1.0 - (deviation / max_deviation))
            status = 'good' if score > 0.8 else 'acceptable'
        else:
            # Outside acceptable range
            if angle < min_val:
                score = max(0.0, 1.0 - (min_val - angle) / min_val)
                status = 'too_low'
            else:
                score = max(0.0, 1.0 - (angle - max_val) / max_val)
                status = 'too_high'
        
        return {
            'angle': round(angle, 1),
            'ideal': ideal,
            'score': score,
            'status': status,
            'deviation': round(abs(angle - ideal), 1)
        }
    
    def _determine_squat_phase(self, knee_angle: float, landmarks: List[PoseLandmark]) -> str:
        """Determine the current phase of the squat"""
        if knee_angle > 160:
            return 'standing'
        elif knee_angle > 120:
            return 'descending'
        elif knee_angle > 100:
            return 'bottom'
        else:
            return 'ascending'
    
    def _generate_squat_feedback(self, angle_scores: Dict, phase: str, landmarks: List[PoseLandmark]) -> List[Dict]:
        """Generate specific feedback for squat form"""
        feedback = []
        
        # Check knee angles
        avg_knee_score = (angle_scores['left_knee']['score'] + angle_scores['right_knee']['score']) / 2
        if avg_knee_score < 0.7:
            if avg_knee_score < 0.5:
                priority = 'critical'
            else:
                priority = 'warning'
            
            feedback.append({
                "type": "form_correction",
                "priority": priority,
                "message": "Knee angle needs adjustment. Try to reach 90 degrees at the bottom.",
                "joint": "knee"
            })
        
        # Check hip angles
        avg_hip_score = (angle_scores['left_hip']['score'] + angle_scores['right_hip']['score']) / 2
        if avg_hip_score < 0.7:
            feedback.append({
                "type": "form_correction",
                "priority": "warning",
                "message": "Push your hips back more to engage your glutes properly.",
                "joint": "hip"
            })
        
        # Check ankle mobility
        avg_ankle_score = (angle_scores['left_ankle']['score'] + angle_scores['right_ankle']['score']) / 2
        if avg_ankle_score < 0.6:
            feedback.append({
                "type": "mobility",
                "priority": "info",
                "message": "Work on ankle mobility to improve squat depth.",
                "joint": "ankle"
            })
        
        # Phase-specific feedback
        if phase == 'bottom' and avg_knee_score > 0.8:
            feedback.append({
                "type": "positive",
                "priority": "info",
                "message": "Great depth! Maintain this position and drive up through your heels.",
                "joint": "overall"
            })
        
        return feedback
    
    def _calculate_squat_biomechanics(self, landmarks: List[PoseLandmark], angle_scores: Dict) -> Dict:
        """Calculate biomechanical parameters for squat"""
        try:
            # Center of mass estimation
            com_x = (landmarks[23].x + landmarks[24].x) / 2  # Average of hips
            com_y = (landmarks[23].y + landmarks[24].y) / 2
            
            # Knee tracking (valgus/varus assessment)
            left_knee_x = landmarks[25].x
            right_knee_x = landmarks[26].x
            knee_separation = abs(left_knee_x - right_knee_x)
            
            # Forward lean assessment
            shoulder_center_x = (landmarks[11].x + landmarks[12].x) / 2
            hip_center_x = (landmarks[23].x + landmarks[24].x) / 2
            forward_lean = abs(shoulder_center_x - hip_center_x)
            
            return {
                'center_of_mass': {'x': com_x, 'y': com_y},
                'knee_separation': knee_separation,
                'forward_lean': forward_lean,
                'knee_tracking_score': min(1.0, knee_separation / 0.3),  # Normalized score
                'balance_score': max(0.0, 1.0 - forward_lean * 2)  # Penalty for excessive lean
            }
            
        except Exception as e:
            logger.error(f"Biomechanics calculation error: {e}")
            return {}
    
    async def process_video_sequence(self, frames: List[np.ndarray], exercise_type: str = 'squat') -> Dict:
        """
        Process a sequence of video frames for comprehensive analysis
        """
        try:
            results = []
            
            # Process frames concurrently (in batches to avoid overwhelming the system)
            batch_size = 5
            for i in range(0, len(frames), batch_size):
                batch = frames[i:i + batch_size]
                
                # Process batch concurrently
                tasks = [
                    self.analyze_frame_async(frame, exercise_type) 
                    for frame in batch
                ]
                batch_results = await asyncio.gather(*tasks)
                results.extend(batch_results)
            
            # Aggregate results
            valid_results = [r for r in results if r.score > 0]
            
            if not valid_results:
                return {
                    "success": False,
                    "error": "No valid pose detections in video sequence"
                }
            
            # Calculate average scores
            avg_score = sum(r.score for r in valid_results) / len(valid_results)
            avg_confidence = sum(r.confidence for r in valid_results) / len(valid_results)
            
            # Find best and worst frames
            best_frame = max(valid_results, key=lambda x: x.score)
            worst_frame = min(valid_results, key=lambda x: x.score)
            
            # Aggregate feedback
            all_feedback = []
            for result in valid_results:
                all_feedback.extend(result.feedback)
            
            # Remove duplicates and prioritize
            unique_feedback = self._deduplicate_feedback(all_feedback)
            
            return {
                "success": True,
                "sequence_analysis": {
                    "total_frames": len(frames),
                    "valid_frames": len(valid_results),
                    "average_score": avg_score,
                    "average_confidence": avg_confidence,
                    "best_frame_score": best_frame.score,
                    "worst_frame_score": worst_frame.score,
                    "exercise_type": exercise_type
                },
                "aggregated_feedback": unique_feedback,
                "best_frame_analysis": best_frame,
                "frame_by_frame": valid_results
            }
            
        except Exception as e:
            logger.error(f"Video sequence processing error: {e}")
            return {
                "success": False,
                "error": f"Video processing failed: {str(e)}"
            }
    
    def _deduplicate_feedback(self, feedback_list: List[Dict]) -> List[Dict]:
        """Remove duplicate feedback messages and prioritize by importance"""
        seen_messages = set()
        unique_feedback = []
        
        # Sort by priority (critical first)
        priority_order = {'critical': 0, 'warning': 1, 'info': 2, 'positive': 3}
        sorted_feedback = sorted(
            feedback_list, 
            key=lambda x: priority_order.get(x.get('priority', 'info'), 2)
        )
        
        for item in sorted_feedback:
            message = item.get('message', '')
            if message not in seen_messages:
                seen_messages.add(message)
                unique_feedback.append(item)
        
        return unique_feedback[:10]  # Limit to top 10 feedback items
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if hasattr(self, 'pose') and self.pose:
                self.pose.close()
            
            if hasattr(self, 'executor') and self.executor:
                self.executor.shutdown(wait=True)
                
            logger.info("MediaPipe analyzer cleanup completed")
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

# Global analyzer instance
analyzer = MediaPipeFormAnalyzer()