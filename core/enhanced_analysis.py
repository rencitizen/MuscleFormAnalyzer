"""
Enhanced body analysis module integrating all improvements
"""
import os
import json
import cv2
import numpy as np
import mediapipe as mp
from typing import Dict, Tuple, List, Any, Optional
from collections import deque
from datetime import datetime

from .enhanced_scale import EnhancedScaleCalculator
from .pose_filters import PoseFilterManager, VelocityFilter, SymmetryEnforcer
from .form_evaluator import ExerciseFormEvaluator, ExerciseType, FormFeedback

try:
    mp_pose = mp.solutions.pose
    PoseLandmark = mp_pose.PoseLandmark
except AttributeError:
    import mediapipe.python as mp_python
    mp_pose = mp_python.solutions.pose
    PoseLandmark = mp_pose.PoseLandmark

class EnhancedBodyAnalyzer:
    """
    Enhanced body analyzer with improved accuracy and form evaluation
    """
    def __init__(self, user_height_cm: float, exercise_type: str = None):
        """
        Args:
            user_height_cm: User's height in cm
            exercise_type: Type of exercise being performed
        """
        self.user_height_cm = user_height_cm
        self.exercise_type = self._parse_exercise_type(exercise_type)
        
        # Initialize components
        self.scale_calculator = EnhancedScaleCalculator(user_height_cm)
        self.pose_filter = PoseFilterManager()
        self.velocity_filter = VelocityFilter()
        self.symmetry_enforcer = SymmetryEnforcer()
        self.form_evaluator = ExerciseFormEvaluator()
        
        # Results storage
        self.results_dir = 'results'
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Frame analysis history
        self.frame_history = deque(maxlen=90)  # 3 seconds at 30fps
        self.phase_detector = ExercisePhaseDetector()
        
    def _parse_exercise_type(self, exercise_type: str) -> Optional[ExerciseType]:
        """Parse exercise type string to enum"""
        if not exercise_type:
            return None
            
        exercise_map = {
            'squat': ExerciseType.SQUAT,
            'deadlift': ExerciseType.DEADLIFT,
            'bench_press': ExerciseType.BENCH_PRESS,
            'pushup': ExerciseType.PUSHUP,
            'pullup': ExerciseType.PULLUP,
            'lunge': ExerciseType.LUNGE,
            'overhead_press': ExerciseType.OVERHEAD_PRESS,
        }
        
        return exercise_map.get(exercise_type.lower())
    
    def analyze_video(self, video_path: str, 
                     output_visualization: bool = True) -> Dict[str, Any]:
        """
        Analyze video with enhanced accuracy
        
        Args:
            video_path: Path to video file
            output_visualization: Whether to create visualization video
            
        Returns:
            Comprehensive analysis results
        """
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if fps <= 0:
            fps = 30
            
        # Initialize MediaPipe
        pose = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=2,  # Use highest complexity for accuracy
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Results accumulator
        all_results = {
            'metadata': {
                'user_height_cm': self.user_height_cm,
                'exercise_type': self.exercise_type.value if self.exercise_type else 'unknown',
                'video_fps': fps,
                'total_frames': frame_count,
                'analysis_date': datetime.now().isoformat()
            },
            'frame_analyses': [],
            'summary': {},
            'form_evaluation': {},
            'measurements': {}
        }
        
        # Video writer for visualization
        out_video = None
        if output_visualization:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out_path = os.path.join(self.results_dir, 'analysis_visualization.mp4')
            out_video = cv2.VideoWriter(out_path, fourcc, fps, 
                                       (int(cap.get(3)), int(cap.get(4))))
        
        frame_idx = 0
        rep_count = 0
        best_form_score = 0
        worst_form_score = 100
        
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                break
                
            # Process frame
            frame_results = self._process_frame(
                image, pose, frame_idx, fps
            )
            
            if frame_results:
                all_results['frame_analyses'].append(frame_results)
                
                # Update statistics
                if 'form_score' in frame_results:
                    best_form_score = max(best_form_score, frame_results['form_score'])
                    worst_form_score = min(worst_form_score, frame_results['form_score'])
                
                # Visualize if requested
                if output_visualization and out_video:
                    viz_frame = self._create_visualization(
                        image, frame_results
                    )
                    out_video.write(viz_frame)
            
            frame_idx += 1
            
            # Show progress
            if frame_idx % 30 == 0:
                progress = (frame_idx / frame_count) * 100
                print(f"Processing: {progress:.1f}% complete")
        
        # Cleanup
        cap.release()
        if out_video:
            out_video.release()
        pose.close()
        
        # Generate summary
        all_results['summary'] = self._generate_summary(all_results['frame_analyses'])
        
        # Save results
        self._save_results(all_results)
        
        return all_results
    
    def _process_frame(self, image: np.ndarray, pose: Any, 
                      frame_idx: int, fps: float) -> Optional[Dict[str, Any]]:
        """Process single frame with all enhancements"""
        
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, _ = image.shape
        
        # Detect pose
        results = pose.process(image_rgb)
        
        if not results.pose_landmarks:
            return None
            
        # Convert landmarks to dict format
        landmarks_raw = {}
        for idx, landmark in enumerate(results.pose_landmarks.landmark):
            landmarks_raw[idx] = {
                'x': landmark.x,
                'y': landmark.y,
                'z': landmark.z,
                'visibility': landmark.visibility
            }
        
        # Apply noise reduction
        landmarks_filtered = self.pose_filter.process_landmarks(landmarks_raw)
        
        # Apply velocity constraints
        if self.scale_calculator.scale_px_per_cm:
            landmarks_filtered = self.velocity_filter.filter_landmarks(
                landmarks_filtered, self.scale_calculator.scale_px_per_cm
            )
        
        # Apply symmetry enforcement
        landmarks_filtered = self.symmetry_enforcer.enforce_symmetry(landmarks_filtered)
        
        # Calculate scale with multiple references
        scale = self.scale_calculator.calculate_multi_reference_scale(
            landmarks_filtered, h, w
        )
        
        if not scale:
            return None
            
        # Convert to cm coordinates
        landmarks_cm = self.scale_calculator.convert_landmarks_to_cm_enhanced(
            landmarks_filtered, (w, h)
        )
        
        # Calculate body measurements
        measurements = self._calculate_enhanced_measurements(
            landmarks_filtered, (w, h)
        )
        
        # Detect exercise phase
        phase = self.phase_detector.detect_phase(
            landmarks_cm, self.exercise_type, self.frame_history
        )
        
        # Evaluate form if exercise type is known
        form_score = 50.0
        form_feedback = []
        
        if self.exercise_type and phase:
            form_score, form_feedback = self.form_evaluator.evaluate_form(
                self.exercise_type, landmarks_cm, phase
            )
        
        # Store frame results
        frame_results = {
            'frame_idx': frame_idx,
            'timestamp': frame_idx / fps,
            'landmarks_cm': landmarks_cm,
            'measurements': measurements,
            'phase': phase,
            'form_score': form_score,
            'form_feedback': [self._feedback_to_dict(fb) for fb in form_feedback],
            'scale_confidence': self.scale_calculator.get_scale_confidence()
        }
        
        # Update history
        self.frame_history.append(frame_results)
        
        return frame_results
    
    def _calculate_enhanced_measurements(self, landmarks: Dict[int, Dict[str, float]], 
                                       frame_dim: Tuple[int, int]) -> Dict[str, float]:
        """Calculate enhanced body measurements"""
        measurements = {}
        
        # Arm lengths
        left_arm = self._calculate_limb_length(
            'LEFT', 'arm', landmarks, frame_dim
        )
        right_arm = self._calculate_limb_length(
            'RIGHT', 'arm', landmarks, frame_dim
        )
        
        if left_arm:
            measurements['left_arm_cm'] = round(left_arm, 1)
        if right_arm:
            measurements['right_arm_cm'] = round(right_arm, 1)
            
        # Leg lengths
        left_leg = self._calculate_limb_length(
            'LEFT', 'leg', landmarks, frame_dim
        )
        right_leg = self._calculate_limb_length(
            'RIGHT', 'leg', landmarks, frame_dim
        )
        
        if left_leg:
            measurements['left_leg_cm'] = round(left_leg, 1)
        if right_leg:
            measurements['right_leg_cm'] = round(right_leg, 1)
            
        # Additional measurements
        shoulder_width = self._calculate_shoulder_width(landmarks, frame_dim)
        if shoulder_width:
            measurements['shoulder_width_cm'] = round(shoulder_width, 1)
            
        hip_width = self._calculate_hip_width(landmarks, frame_dim)
        if hip_width:
            measurements['hip_width_cm'] = round(hip_width, 1)
            
        torso_length = self._calculate_torso_length(landmarks, frame_dim)
        if torso_length:
            measurements['torso_length_cm'] = round(torso_length, 1)
        
        return measurements
    
    def _calculate_limb_length(self, side: str, limb_type: str,
                             landmarks: Dict[int, Dict[str, float]], 
                             frame_dim: Tuple[int, int]) -> Optional[float]:
        """Calculate limb length with improved accuracy"""
        
        if limb_type == 'arm':
            joint_ids = [
                getattr(PoseLandmark, f'{side}_SHOULDER'),
                getattr(PoseLandmark, f'{side}_ELBOW'),
                getattr(PoseLandmark, f'{side}_WRIST')
            ]
        else:  # leg
            joint_ids = [
                getattr(PoseLandmark, f'{side}_HIP'),
                getattr(PoseLandmark, f'{side}_KNEE'),
                getattr(PoseLandmark, f'{side}_ANKLE')
            ]
        
        joints = [landmarks.get(joint_id) for joint_id in joint_ids]
        
        if all(joints) and all(j.get('visibility', 0) > 0.5 for j in joints):
            total_length = 0.0
            
            for i in range(len(joints) - 1):
                segment_length = self.scale_calculator.distance_px(
                    joints[i], joints[i+1], frame_dim
                )
                total_length += self.scale_calculator.convert_to_cm(segment_length)
            
            return total_length
            
        return None
    
    def _calculate_shoulder_width(self, landmarks: Dict[int, Dict[str, float]], 
                                frame_dim: Tuple[int, int]) -> Optional[float]:
        """Calculate shoulder width"""
        left_shoulder = landmarks.get(PoseLandmark.LEFT_SHOULDER)
        right_shoulder = landmarks.get(PoseLandmark.RIGHT_SHOULDER)
        
        if (left_shoulder and right_shoulder and 
            left_shoulder.get('visibility', 0) > 0.5 and
            right_shoulder.get('visibility', 0) > 0.5):
            
            distance_px = self.scale_calculator.distance_px(
                left_shoulder, right_shoulder, frame_dim
            )
            return self.scale_calculator.convert_to_cm(distance_px)
            
        return None
    
    def _calculate_hip_width(self, landmarks: Dict[int, Dict[str, float]], 
                           frame_dim: Tuple[int, int]) -> Optional[float]:
        """Calculate hip width"""
        left_hip = landmarks.get(PoseLandmark.LEFT_HIP)
        right_hip = landmarks.get(PoseLandmark.RIGHT_HIP)
        
        if (left_hip and right_hip and 
            left_hip.get('visibility', 0) > 0.5 and
            right_hip.get('visibility', 0) > 0.5):
            
            distance_px = self.scale_calculator.distance_px(
                left_hip, right_hip, frame_dim
            )
            return self.scale_calculator.convert_to_cm(distance_px)
            
        return None
    
    def _calculate_torso_length(self, landmarks: Dict[int, Dict[str, float]], 
                              frame_dim: Tuple[int, int]) -> Optional[float]:
        """Calculate torso length"""
        # Calculate from shoulder center to hip center
        left_shoulder = landmarks.get(PoseLandmark.LEFT_SHOULDER)
        right_shoulder = landmarks.get(PoseLandmark.RIGHT_SHOULDER)
        left_hip = landmarks.get(PoseLandmark.LEFT_HIP)
        right_hip = landmarks.get(PoseLandmark.RIGHT_HIP)
        
        if all([left_shoulder, right_shoulder, left_hip, right_hip]):
            # Calculate midpoints
            shoulder_center = {
                'x': (left_shoulder['x'] + right_shoulder['x']) / 2,
                'y': (left_shoulder['y'] + right_shoulder['y']) / 2,
                'z': (left_shoulder.get('z', 0) + right_shoulder.get('z', 0)) / 2,
                'visibility': min(left_shoulder.get('visibility', 1), 
                                right_shoulder.get('visibility', 1))
            }
            
            hip_center = {
                'x': (left_hip['x'] + right_hip['x']) / 2,
                'y': (left_hip['y'] + right_hip['y']) / 2,
                'z': (left_hip.get('z', 0) + right_hip.get('z', 0)) / 2,
                'visibility': min(left_hip.get('visibility', 1), 
                                right_hip.get('visibility', 1))
            }
            
            if (shoulder_center['visibility'] > 0.5 and 
                hip_center['visibility'] > 0.5):
                
                distance_px = self.scale_calculator.distance_px(
                    shoulder_center, hip_center, frame_dim
                )
                return self.scale_calculator.convert_to_cm(distance_px)
                
        return None
    
    def _create_visualization(self, image: np.ndarray, 
                            frame_results: Dict[str, Any]) -> np.ndarray:
        """Create visualization frame with analysis results"""
        viz_image = image.copy()
        h, w = viz_image.shape[:2]
        
        # Draw form score
        score = frame_results.get('form_score', 50)
        score_color = self._get_score_color(score)
        
        cv2.putText(viz_image, f"Form Score: {score:.0f}/100", 
                   (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, score_color, 2)
        
        # Draw phase
        phase = frame_results.get('phase', 'unknown')
        cv2.putText(viz_image, f"Phase: {phase}", 
                   (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Draw measurements
        measurements = frame_results.get('measurements', {})
        y_offset = 120
        for key, value in measurements.items():
            text = f"{key.replace('_', ' ').title()}: {value} cm"
            cv2.putText(viz_image, text, 
                       (20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            y_offset += 30
        
        # Draw feedback
        feedback_list = frame_results.get('form_feedback', [])
        y_offset = h - 200
        for feedback in feedback_list[:3]:  # Show top 3 feedback items
            severity = feedback.get('severity', 'info')
            color = self._get_severity_color(severity)
            
            cv2.putText(viz_image, feedback.get('message', ''), 
                       (20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            y_offset += 25
            
            suggestion = feedback.get('improvement_suggestion', '')
            if suggestion:
                cv2.putText(viz_image, f"  → {suggestion}", 
                           (20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
                y_offset += 25
        
        return viz_image
    
    def _get_score_color(self, score: float) -> Tuple[int, int, int]:
        """Get color based on score (BGR format)"""
        if score >= 80:
            return (0, 255, 0)  # Green
        elif score >= 60:
            return (0, 255, 255)  # Yellow
        elif score >= 40:
            return (0, 165, 255)  # Orange
        else:
            return (0, 0, 255)  # Red
    
    def _get_severity_color(self, severity: str) -> Tuple[int, int, int]:
        """Get color based on severity (BGR format)"""
        severity_colors = {
            'critical': (0, 0, 255),     # Red
            'warning': (0, 165, 255),    # Orange
            'info': (255, 255, 0)        # Cyan
        }
        return severity_colors.get(severity, (255, 255, 255))
    
    def _feedback_to_dict(self, feedback: FormFeedback) -> Dict[str, Any]:
        """Convert FormFeedback object to dictionary"""
        return {
            'severity': feedback.severity,
            'message': feedback.message,
            'affected_joints': feedback.affected_joints,
            'improvement_suggestion': feedback.improvement_suggestion
        }
    
    def _generate_summary(self, frame_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics from all frames"""
        if not frame_analyses:
            return {}
            
        # Form scores
        form_scores = [f['form_score'] for f in frame_analyses if 'form_score' in f]
        
        # Measurements
        all_measurements = {}
        measurement_counts = {}
        
        for frame in frame_analyses:
            for key, value in frame.get('measurements', {}).items():
                if key not in all_measurements:
                    all_measurements[key] = []
                    measurement_counts[key] = 0
                all_measurements[key].append(value)
                measurement_counts[key] += 1
        
        # Calculate averages
        avg_measurements = {}
        for key, values in all_measurements.items():
            if values:
                avg_measurements[key] = round(np.mean(values), 1)
        
        # Phase distribution
        phases = [f.get('phase', 'unknown') for f in frame_analyses]
        phase_counts = {}
        for phase in phases:
            phase_counts[phase] = phase_counts.get(phase, 0) + 1
        
        # Feedback summary
        all_feedback = []
        for frame in frame_analyses:
            all_feedback.extend(frame.get('form_feedback', []))
        
        # Count feedback by severity
        feedback_severity_counts = {
            'critical': 0,
            'warning': 0,
            'info': 0
        }
        
        for feedback in all_feedback:
            severity = feedback.get('severity', 'info')
            feedback_severity_counts[severity] += 1
        
        summary = {
            'form_score_stats': {
                'average': round(np.mean(form_scores), 1) if form_scores else 0,
                'best': round(max(form_scores), 1) if form_scores else 0,
                'worst': round(min(form_scores), 1) if form_scores else 0,
                'std_dev': round(np.std(form_scores), 1) if form_scores else 0
            },
            'average_measurements': avg_measurements,
            'phase_distribution': phase_counts,
            'feedback_summary': feedback_severity_counts,
            'total_frames_analyzed': len(frame_analyses),
            'confidence_score': round(np.mean([f.get('scale_confidence', 0.5) 
                                             for f in frame_analyses]), 3)
        }
        
        return summary
    
    def _save_results(self, results: Dict[str, Any]) -> str:
        """Save analysis results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"enhanced_analysis_{timestamp}.json"
        filepath = os.path.join(self.results_dir, filename)
        
        # Remove frame-by-frame data for summary file
        summary_results = {
            'metadata': results['metadata'],
            'summary': results['summary'],
            'form_evaluation': results['form_evaluation'],
            'measurements': results['measurements']
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(summary_results, f, indent=2)
        
        print(f"Analysis results saved to: {filepath}")
        return filepath


class ExercisePhaseDetector:
    """Detect exercise phases (top, bottom, middle) based on joint positions"""
    
    def __init__(self):
        self.phase_history = deque(maxlen=10)
        
    def detect_phase(self, landmarks_cm: Dict[str, Dict[str, float]], 
                    exercise_type: Optional[ExerciseType],
                    frame_history: deque) -> str:
        """Detect current exercise phase"""
        
        if not exercise_type:
            return "unknown"
            
        if exercise_type == ExerciseType.SQUAT:
            return self._detect_squat_phase(landmarks_cm)
        elif exercise_type == ExerciseType.BENCH_PRESS:
            return self._detect_bench_press_phase(landmarks_cm)
        elif exercise_type == ExerciseType.DEADLIFT:
            return self._detect_deadlift_phase(landmarks_cm)
        elif exercise_type == ExerciseType.PUSHUP:
            return self._detect_pushup_phase(landmarks_cm)
        else:
            return "middle"
    
    def _detect_squat_phase(self, landmarks_cm: Dict[str, Dict[str, float]]) -> str:
        """Detect squat phase based on hip height"""
        left_hip = landmarks_cm.get("LEFT_HIP")
        right_hip = landmarks_cm.get("RIGHT_HIP")
        left_knee = landmarks_cm.get("LEFT_KNEE")
        right_knee = landmarks_cm.get("RIGHT_KNEE")
        
        if all([left_hip, right_hip, left_knee, right_knee]):
            hip_height = (left_hip['y'] + right_hip['y']) / 2
            knee_height = (left_knee['y'] + right_knee['y']) / 2
            
            # Calculate relative position
            hip_knee_diff = hip_height - knee_height
            
            if hip_knee_diff < 10:  # Hip near or below knees
                return "bottom"
            elif hip_knee_diff > 40:  # Standing position
                return "top"
            else:
                return "middle"
                
        return "unknown"
    
    def _detect_bench_press_phase(self, landmarks_cm: Dict[str, Dict[str, float]]) -> str:
        """Detect bench press phase based on elbow position"""
        left_elbow = landmarks_cm.get("LEFT_ELBOW")
        left_shoulder = landmarks_cm.get("LEFT_SHOULDER")
        
        if left_elbow and left_shoulder:
            elbow_shoulder_diff = left_elbow['y'] - left_shoulder['y']
            
            if elbow_shoulder_diff < -5:  # Elbows below shoulders
                return "bottom"
            elif elbow_shoulder_diff > 15:  # Arms extended
                return "top"
            else:
                return "middle"
                
        return "unknown"
    
    def _detect_deadlift_phase(self, landmarks_cm: Dict[str, Dict[str, float]]) -> str:
        """Detect deadlift phase based on hip angle"""
        hip_center = self._get_center_point(
            landmarks_cm.get("LEFT_HIP"),
            landmarks_cm.get("RIGHT_HIP")
        )
        shoulder_center = self._get_center_point(
            landmarks_cm.get("LEFT_SHOULDER"),
            landmarks_cm.get("RIGHT_SHOULDER")
        )
        
        if hip_center and shoulder_center:
            # Calculate torso angle
            torso_angle = np.degrees(np.arctan2(
                shoulder_center['y'] - hip_center['y'],
                abs(shoulder_center['x'] - hip_center['x'])
            ))
            
            if torso_angle < 30:  # Bent over
                return "bottom"
            elif torso_angle > 70:  # Standing upright
                return "top"
            else:
                return "middle"
                
        return "unknown"
    
    def _detect_pushup_phase(self, landmarks_cm: Dict[str, Dict[str, float]]) -> str:
        """Detect pushup phase based on chest height"""
        chest_points = [
            landmarks_cm.get("LEFT_SHOULDER"),
            landmarks_cm.get("RIGHT_SHOULDER")
        ]
        wrist_points = [
            landmarks_cm.get("LEFT_WRIST"),
            landmarks_cm.get("RIGHT_WRIST")
        ]
        
        if all(chest_points) and all(wrist_points):
            chest_height = sum(p['y'] for p in chest_points) / len(chest_points)
            wrist_height = sum(p['y'] for p in wrist_points) / len(wrist_points)
            
            chest_wrist_diff = chest_height - wrist_height
            
            if chest_wrist_diff < 10:  # Chest near ground
                return "bottom"
            elif chest_wrist_diff > 30:  # Arms extended
                return "top"
            else:
                return "middle"
                
        return "unknown"
    
    def _get_center_point(self, p1: Optional[Dict[str, float]], 
                         p2: Optional[Dict[str, float]]) -> Optional[Dict[str, float]]:
        """Get center point between two points"""
        if not p1 or not p2:
            return None
            
        return {
            'x': (p1['x'] + p2['x']) / 2,
            'y': (p1['y'] + p2['y']) / 2,
            'z': (p1.get('z', 0) + p2.get('z', 0)) / 2
        }