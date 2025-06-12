"""
Exercise-specific form evaluation module with detailed analysis
"""
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import mediapipe as mp

try:
    mp_pose = mp.solutions.pose
    PoseLandmark = mp_pose.PoseLandmark
except AttributeError:
    import mediapipe.python as mp_python
    mp_pose = mp_python.solutions.pose
    PoseLandmark = mp_pose.PoseLandmark

class ExerciseType(Enum):
    SQUAT = "squat"
    DEADLIFT = "deadlift"
    BENCH_PRESS = "bench_press"
    PUSHUP = "pushup"
    PULLUP = "pullup"
    LUNGE = "lunge"
    OVERHEAD_PRESS = "overhead_press"

@dataclass
class FormCriteria:
    """Criteria for evaluating exercise form"""
    name: str
    weight: float  # Importance weight (0-1)
    ideal_value: float
    acceptable_range: Tuple[float, float]
    unit: str = "degrees"
    
@dataclass
class FormFeedback:
    """Feedback for form improvement"""
    severity: str  # "critical", "warning", "info"
    message: str
    affected_joints: List[str]
    improvement_suggestion: str

class ExerciseFormEvaluator:
    """Evaluate exercise form with specific criteria"""
    
    def __init__(self):
        self.exercise_criteria = self._initialize_criteria()
        
    def _initialize_criteria(self) -> Dict[ExerciseType, List[FormCriteria]]:
        """Initialize form criteria for each exercise"""
        return {
            ExerciseType.SQUAT: [
                FormCriteria("knee_angle_bottom", 0.3, 90, (80, 110), "degrees"),
                FormCriteria("hip_angle_bottom", 0.25, 85, (75, 95), "degrees"),
                FormCriteria("knee_over_toes", 0.2, 0, (-5, 10), "cm"),
                FormCriteria("back_angle", 0.15, 75, (65, 85), "degrees"),
                FormCriteria("knee_valgus", 0.1, 0, (-5, 5), "degrees"),
            ],
            ExerciseType.DEADLIFT: [
                FormCriteria("hip_hinge_angle", 0.3, 45, (35, 55), "degrees"),
                FormCriteria("back_straightness", 0.3, 180, (170, 190), "degrees"),
                FormCriteria("bar_path_deviation", 0.2, 0, (-5, 5), "cm"),
                FormCriteria("shoulder_position", 0.1, 0, (-5, 5), "cm"),
                FormCriteria("neck_alignment", 0.1, 0, (-10, 10), "degrees"),
            ],
            ExerciseType.BENCH_PRESS: [
                FormCriteria("elbow_angle_bottom", 0.25, 90, (85, 95), "degrees"),
                FormCriteria("bar_path_angle", 0.25, 0, (-5, 5), "degrees"),
                FormCriteria("wrist_alignment", 0.2, 180, (170, 190), "degrees"),
                FormCriteria("arch_maintenance", 0.15, 15, (10, 25), "degrees"),
                FormCriteria("shoulder_stability", 0.15, 0, (-5, 5), "cm"),
            ],
            ExerciseType.PUSHUP: [
                FormCriteria("elbow_angle_bottom", 0.3, 90, (85, 100), "degrees"),
                FormCriteria("body_alignment", 0.3, 180, (170, 185), "degrees"),
                FormCriteria("hand_width_ratio", 0.2, 1.5, (1.3, 1.7), "ratio"),
                FormCriteria("neck_alignment", 0.1, 0, (-10, 10), "degrees"),
                FormCriteria("hip_sag", 0.1, 0, (-5, 5), "cm"),
            ],
            ExerciseType.LUNGE: [
                FormCriteria("front_knee_angle", 0.3, 90, (85, 95), "degrees"),
                FormCriteria("back_knee_height", 0.25, 5, (2, 10), "cm"),
                FormCriteria("torso_angle", 0.2, 90, (85, 95), "degrees"),
                FormCriteria("knee_over_ankle", 0.15, 0, (-5, 5), "cm"),
                FormCriteria("hip_alignment", 0.1, 0, (-5, 5), "degrees"),
            ],
            ExerciseType.OVERHEAD_PRESS: [
                FormCriteria("elbow_lockout", 0.3, 180, (175, 185), "degrees"),
                FormCriteria("bar_path_vertical", 0.25, 90, (85, 95), "degrees"),
                FormCriteria("shoulder_alignment", 0.2, 0, (-5, 5), "cm"),
                FormCriteria("core_stability", 0.15, 0, (-5, 5), "degrees"),
                FormCriteria("wrist_alignment", 0.1, 180, (170, 190), "degrees"),
            ],
        }
    
    def evaluate_form(self, exercise_type: ExerciseType, 
                     landmarks_cm: Dict[str, Dict[str, float]],
                     phase: str = "bottom") -> Tuple[float, List[FormFeedback]]:
        """
        Evaluate exercise form and return score with feedback
        
        Args:
            exercise_type: Type of exercise
            landmarks_cm: Landmarks in cm coordinates
            phase: Exercise phase ("bottom", "top", "middle")
            
        Returns:
            Tuple of (score 0-100, list of feedback)
        """
        if exercise_type not in self.exercise_criteria:
            return 50.0, [FormFeedback(
                severity="warning",
                message="Exercise type not supported",
                affected_joints=[],
                improvement_suggestion="Use a supported exercise type"
            )]
        
        criteria = self.exercise_criteria[exercise_type]
        total_score = 0.0
        total_weight = 0.0
        feedback_list = []
        
        # Evaluate each criterion
        for criterion in criteria:
            value, is_valid = self._calculate_criterion_value(
                criterion, landmarks_cm, exercise_type, phase
            )
            
            if not is_valid:
                continue
                
            # Calculate score for this criterion
            score = self._score_criterion(value, criterion)
            total_score += score * criterion.weight
            total_weight += criterion.weight
            
            # Generate feedback if needed
            if score < 0.7:  # Below 70% for this criterion
                feedback = self._generate_feedback(
                    criterion, value, score, exercise_type
                )
                feedback_list.append(feedback)
        
        # Normalize score to 0-100
        final_score = (total_score / total_weight * 100) if total_weight > 0 else 50.0
        
        return final_score, feedback_list
    
    def _calculate_criterion_value(self, criterion: FormCriteria,
                                 landmarks_cm: Dict[str, Dict[str, float]],
                                 exercise_type: ExerciseType,
                                 phase: str) -> Tuple[float, bool]:
        """Calculate value for a specific criterion"""
        
        # Exercise-specific calculations
        if exercise_type == ExerciseType.SQUAT:
            return self._calculate_squat_criterion(criterion, landmarks_cm, phase)
        elif exercise_type == ExerciseType.DEADLIFT:
            return self._calculate_deadlift_criterion(criterion, landmarks_cm, phase)
        elif exercise_type == ExerciseType.BENCH_PRESS:
            return self._calculate_bench_press_criterion(criterion, landmarks_cm, phase)
        elif exercise_type == ExerciseType.PUSHUP:
            return self._calculate_pushup_criterion(criterion, landmarks_cm, phase)
        elif exercise_type == ExerciseType.LUNGE:
            return self._calculate_lunge_criterion(criterion, landmarks_cm, phase)
        elif exercise_type == ExerciseType.OVERHEAD_PRESS:
            return self._calculate_overhead_press_criterion(criterion, landmarks_cm, phase)
        
        return 0.0, False
    
    def _calculate_squat_criterion(self, criterion: FormCriteria,
                                 landmarks_cm: Dict[str, Dict[str, float]],
                                 phase: str) -> Tuple[float, bool]:
        """Calculate squat-specific criteria"""
        
        if criterion.name == "knee_angle_bottom" and phase == "bottom":
            # Calculate knee angle
            left_knee_angle = self._calculate_angle(
                landmarks_cm.get("LEFT_HIP"),
                landmarks_cm.get("LEFT_KNEE"),
                landmarks_cm.get("LEFT_ANKLE")
            )
            right_knee_angle = self._calculate_angle(
                landmarks_cm.get("RIGHT_HIP"),
                landmarks_cm.get("RIGHT_KNEE"),
                landmarks_cm.get("RIGHT_ANKLE")
            )
            
            if left_knee_angle and right_knee_angle:
                return (left_knee_angle + right_knee_angle) / 2, True
                
        elif criterion.name == "hip_angle_bottom" and phase == "bottom":
            # Calculate hip angle
            left_hip_angle = self._calculate_angle(
                landmarks_cm.get("LEFT_SHOULDER"),
                landmarks_cm.get("LEFT_HIP"),
                landmarks_cm.get("LEFT_KNEE")
            )
            right_hip_angle = self._calculate_angle(
                landmarks_cm.get("RIGHT_SHOULDER"),
                landmarks_cm.get("RIGHT_HIP"),
                landmarks_cm.get("RIGHT_KNEE")
            )
            
            if left_hip_angle and right_hip_angle:
                return (left_hip_angle + right_hip_angle) / 2, True
                
        elif criterion.name == "knee_over_toes":
            # Check knee position relative to toes
            left_knee = landmarks_cm.get("LEFT_KNEE")
            left_ankle = landmarks_cm.get("LEFT_ANKLE")
            
            if left_knee and left_ankle:
                knee_forward = left_knee['x'] - left_ankle['x']
                return knee_forward, True
                
        elif criterion.name == "back_angle":
            # Calculate back angle from vertical
            shoulder_center = self._get_midpoint(
                landmarks_cm.get("LEFT_SHOULDER"),
                landmarks_cm.get("RIGHT_SHOULDER")
            )
            hip_center = self._get_midpoint(
                landmarks_cm.get("LEFT_HIP"),
                landmarks_cm.get("RIGHT_HIP")
            )
            
            if shoulder_center and hip_center:
                back_angle = self._calculate_angle_from_vertical(
                    hip_center, shoulder_center
                )
                return back_angle, True
                
        elif criterion.name == "knee_valgus":
            # Check for knee caving (valgus)
            left_hip = landmarks_cm.get("LEFT_HIP")
            left_knee = landmarks_cm.get("LEFT_KNEE")
            left_ankle = landmarks_cm.get("LEFT_ANKLE")
            
            if all([left_hip, left_knee, left_ankle]):
                # Calculate deviation from straight line
                expected_x = left_hip['x'] + (left_ankle['x'] - left_hip['x']) * 0.5
                actual_x = left_knee['x']
                valgus_angle = np.degrees(np.arctan2(
                    actual_x - expected_x,
                    left_hip['y'] - left_ankle['y']
                ))
                return abs(valgus_angle), True
        
        return 0.0, False
    
    def _calculate_deadlift_criterion(self, criterion: FormCriteria,
                                    landmarks_cm: Dict[str, Dict[str, float]],
                                    phase: str) -> Tuple[float, bool]:
        """Calculate deadlift-specific criteria"""
        
        if criterion.name == "hip_hinge_angle":
            # Calculate hip hinge angle
            shoulder_center = self._get_midpoint(
                landmarks_cm.get("LEFT_SHOULDER"),
                landmarks_cm.get("RIGHT_SHOULDER")
            )
            hip_center = self._get_midpoint(
                landmarks_cm.get("LEFT_HIP"),
                landmarks_cm.get("RIGHT_HIP")
            )
            knee_center = self._get_midpoint(
                landmarks_cm.get("LEFT_KNEE"),
                landmarks_cm.get("RIGHT_KNEE")
            )
            
            if all([shoulder_center, hip_center, knee_center]):
                hinge_angle = self._calculate_angle(
                    shoulder_center, hip_center, knee_center
                )
                return hinge_angle, True
                
        elif criterion.name == "back_straightness":
            # Check spine alignment
            neck = landmarks_cm.get("NOSE")
            shoulder_center = self._get_midpoint(
                landmarks_cm.get("LEFT_SHOULDER"),
                landmarks_cm.get("RIGHT_SHOULDER")
            )
            hip_center = self._get_midpoint(
                landmarks_cm.get("LEFT_HIP"),
                landmarks_cm.get("RIGHT_HIP")
            )
            
            if all([neck, shoulder_center, hip_center]):
                spine_angle = self._calculate_angle(
                    neck, shoulder_center, hip_center
                )
                return spine_angle, True
        
        return 0.0, False
    
    def _calculate_bench_press_criterion(self, criterion: FormCriteria,
                                       landmarks_cm: Dict[str, Dict[str, float]],
                                       phase: str) -> Tuple[float, bool]:
        """Calculate bench press-specific criteria"""
        
        if criterion.name == "elbow_angle_bottom" and phase == "bottom":
            # Calculate elbow angle at bottom position
            left_elbow_angle = self._calculate_angle(
                landmarks_cm.get("LEFT_SHOULDER"),
                landmarks_cm.get("LEFT_ELBOW"),
                landmarks_cm.get("LEFT_WRIST")
            )
            right_elbow_angle = self._calculate_angle(
                landmarks_cm.get("RIGHT_SHOULDER"),
                landmarks_cm.get("RIGHT_ELBOW"),
                landmarks_cm.get("RIGHT_WRIST")
            )
            
            if left_elbow_angle and right_elbow_angle:
                return (left_elbow_angle + right_elbow_angle) / 2, True
                
        elif criterion.name == "wrist_alignment":
            # Check wrist alignment
            left_alignment = self._calculate_angle(
                landmarks_cm.get("LEFT_ELBOW"),
                landmarks_cm.get("LEFT_WRIST"),
                landmarks_cm.get("LEFT_PINKY")
            )
            
            if left_alignment:
                return left_alignment, True
        
        return 0.0, False
    
    def _calculate_pushup_criterion(self, criterion: FormCriteria,
                                  landmarks_cm: Dict[str, Dict[str, float]],
                                  phase: str) -> Tuple[float, bool]:
        """Calculate pushup-specific criteria"""
        
        if criterion.name == "body_alignment":
            # Check body alignment from head to ankles
            head = landmarks_cm.get("NOSE")
            shoulder_center = self._get_midpoint(
                landmarks_cm.get("LEFT_SHOULDER"),
                landmarks_cm.get("RIGHT_SHOULDER")
            )
            hip_center = self._get_midpoint(
                landmarks_cm.get("LEFT_HIP"),
                landmarks_cm.get("RIGHT_HIP")
            )
            ankle_center = self._get_midpoint(
                landmarks_cm.get("LEFT_ANKLE"),
                landmarks_cm.get("RIGHT_ANKLE")
            )
            
            if all([head, shoulder_center, hip_center, ankle_center]):
                # Calculate deviation from straight line
                alignment_score = self._calculate_line_deviation(
                    [head, shoulder_center, hip_center, ankle_center]
                )
                return 180 - alignment_score, True  # Convert to angle
                
        elif criterion.name == "hand_width_ratio":
            # Check hand position relative to shoulders
            left_wrist = landmarks_cm.get("LEFT_WRIST")
            right_wrist = landmarks_cm.get("RIGHT_WRIST")
            left_shoulder = landmarks_cm.get("LEFT_SHOULDER")
            right_shoulder = landmarks_cm.get("RIGHT_SHOULDER")
            
            if all([left_wrist, right_wrist, left_shoulder, right_shoulder]):
                hand_width = abs(right_wrist['x'] - left_wrist['x'])
                shoulder_width = abs(right_shoulder['x'] - left_shoulder['x'])
                ratio = hand_width / shoulder_width if shoulder_width > 0 else 0
                return ratio, True
        
        return 0.0, False
    
    def _calculate_lunge_criterion(self, criterion: FormCriteria,
                                 landmarks_cm: Dict[str, Dict[str, float]],
                                 phase: str) -> Tuple[float, bool]:
        """Calculate lunge-specific criteria"""
        
        if criterion.name == "front_knee_angle" and phase == "bottom":
            # Determine which leg is forward based on position
            left_ankle = landmarks_cm.get("LEFT_ANKLE")
            right_ankle = landmarks_cm.get("RIGHT_ANKLE")
            
            if left_ankle and right_ankle:
                # Front leg is the one more forward
                if left_ankle['z'] < right_ankle['z']:
                    # Left leg is front
                    knee_angle = self._calculate_angle(
                        landmarks_cm.get("LEFT_HIP"),
                        landmarks_cm.get("LEFT_KNEE"),
                        landmarks_cm.get("LEFT_ANKLE")
                    )
                else:
                    # Right leg is front
                    knee_angle = self._calculate_angle(
                        landmarks_cm.get("RIGHT_HIP"),
                        landmarks_cm.get("RIGHT_KNEE"),
                        landmarks_cm.get("RIGHT_ANKLE")
                    )
                
                if knee_angle:
                    return knee_angle, True
        
        return 0.0, False
    
    def _calculate_overhead_press_criterion(self, criterion: FormCriteria,
                                          landmarks_cm: Dict[str, Dict[str, float]],
                                          phase: str) -> Tuple[float, bool]:
        """Calculate overhead press-specific criteria"""
        
        if criterion.name == "elbow_lockout" and phase == "top":
            # Check elbow extension at top
            left_elbow_angle = self._calculate_angle(
                landmarks_cm.get("LEFT_SHOULDER"),
                landmarks_cm.get("LEFT_ELBOW"),
                landmarks_cm.get("LEFT_WRIST")
            )
            right_elbow_angle = self._calculate_angle(
                landmarks_cm.get("RIGHT_SHOULDER"),
                landmarks_cm.get("RIGHT_ELBOW"),
                landmarks_cm.get("RIGHT_WRIST")
            )
            
            if left_elbow_angle and right_elbow_angle:
                return (left_elbow_angle + right_elbow_angle) / 2, True
        
        return 0.0, False
    
    def _calculate_angle(self, p1: Optional[Dict[str, float]], 
                        p2: Optional[Dict[str, float]], 
                        p3: Optional[Dict[str, float]]) -> Optional[float]:
        """Calculate angle between three points"""
        if not all([p1, p2, p3]):
            return None
            
        # Convert to numpy arrays
        a = np.array([p1['x'], p1['y'], p1['z']])
        b = np.array([p2['x'], p2['y'], p2['z']])
        c = np.array([p3['x'], p3['y'], p3['z']])
        
        # Calculate vectors
        ba = a - b
        bc = c - b
        
        # Calculate angle
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
        angle = np.degrees(np.arccos(cosine_angle))
        
        return angle
    
    def _calculate_angle_from_vertical(self, p1: Dict[str, float], 
                                     p2: Dict[str, float]) -> float:
        """Calculate angle from vertical line"""
        dx = p2['x'] - p1['x']
        dy = p2['y'] - p1['y']
        angle = np.degrees(np.arctan2(dx, dy))
        return abs(angle)
    
    def _get_midpoint(self, p1: Optional[Dict[str, float]], 
                     p2: Optional[Dict[str, float]]) -> Optional[Dict[str, float]]:
        """Get midpoint between two points"""
        if not p1 or not p2:
            return None
            
        return {
            'x': (p1['x'] + p2['x']) / 2,
            'y': (p1['y'] + p2['y']) / 2,
            'z': (p1['z'] + p2['z']) / 2
        }
    
    def _calculate_line_deviation(self, points: List[Dict[str, float]]) -> float:
        """Calculate deviation from straight line"""
        if len(points) < 3:
            return 0.0
            
        # Fit a line through first and last point
        p1 = np.array([points[0]['x'], points[0]['y'], points[0]['z']])
        p2 = np.array([points[-1]['x'], points[-1]['y'], points[-1]['z']])
        
        total_deviation = 0.0
        
        # Calculate deviation for middle points
        for i in range(1, len(points) - 1):
            p = np.array([points[i]['x'], points[i]['y'], points[i]['z']])
            
            # Point-to-line distance
            t = np.dot(p - p1, p2 - p1) / np.dot(p2 - p1, p2 - p1)
            t = np.clip(t, 0, 1)
            closest_point = p1 + t * (p2 - p1)
            
            deviation = np.linalg.norm(p - closest_point)
            total_deviation += deviation
        
        return total_deviation / (len(points) - 2)
    
    def _score_criterion(self, value: float, criterion: FormCriteria) -> float:
        """Score a criterion value (0-1)"""
        min_val, max_val = criterion.acceptable_range
        
        if min_val <= value <= max_val:
            # Within acceptable range
            # Calculate how close to ideal
            distance_from_ideal = abs(value - criterion.ideal_value)
            max_distance = max(abs(criterion.ideal_value - min_val), 
                              abs(criterion.ideal_value - max_val))
            
            if max_distance > 0:
                score = 1.0 - (distance_from_ideal / max_distance) * 0.3
            else:
                score = 1.0
        else:
            # Outside acceptable range
            if value < min_val:
                distance = min_val - value
                penalty_rate = 0.1  # 10% penalty per unit outside range
            else:
                distance = value - max_val
                penalty_rate = 0.1
                
            score = max(0.0, 0.7 - distance * penalty_rate)
        
        return score
    
    def _generate_feedback(self, criterion: FormCriteria, value: float, 
                         score: float, exercise_type: ExerciseType) -> FormFeedback:
        """Generate feedback for a criterion"""
        min_val, max_val = criterion.acceptable_range
        
        # Determine severity
        if score < 0.3:
            severity = "critical"
        elif score < 0.7:
            severity = "warning"
        else:
            severity = "info"
        
        # Generate message
        if value < min_val:
            direction = "too low"
            target = min_val
        elif value > max_val:
            direction = "too high"
            target = max_val
        else:
            direction = "suboptimal"
            target = criterion.ideal_value
        
        message = f"{criterion.name.replace('_', ' ').title()} is {direction} ({value:.1f}{criterion.unit}, target: {target:.1f}{criterion.unit})"
        
        # Exercise-specific suggestions
        suggestions = self._get_improvement_suggestions(
            exercise_type, criterion.name, direction
        )
        
        # Affected joints
        affected_joints = self._get_affected_joints(exercise_type, criterion.name)
        
        return FormFeedback(
            severity=severity,
            message=message,
            affected_joints=affected_joints,
            improvement_suggestion=suggestions
        )
    
    def _get_improvement_suggestions(self, exercise_type: ExerciseType, 
                                   criterion_name: str, direction: str) -> str:
        """Get specific improvement suggestions"""
        suggestions = {
            ExerciseType.SQUAT: {
                "knee_angle_bottom": {
                    "too low": "Don't squat so deep. Aim for thighs parallel to ground.",
                    "too high": "Squat deeper. Try to reach parallel or below.",
                },
                "knee_over_toes": {
                    "too high": "Keep knees behind or in line with toes.",
                    "too low": "Allow knees to track forward naturally.",
                },
                "back_angle": {
                    "too low": "Keep chest up and maintain upright torso.",
                    "too high": "Lean forward slightly for balance.",
                },
            },
            ExerciseType.DEADLIFT: {
                "hip_hinge_angle": {
                    "too low": "Push hips back more at the start.",
                    "too high": "Start with hips lower.",
                },
                "back_straightness": {
                    "too low": "Maintain neutral spine. Don't round back.",
                    "too high": "Avoid hyperextending. Keep neutral spine.",
                },
            },
            ExerciseType.BENCH_PRESS: {
                "elbow_angle_bottom": {
                    "too low": "Don't lower bar too far. Stop at 90 degrees.",
                    "too high": "Lower bar more for full range of motion.",
                },
                "wrist_alignment": {
                    "too low": "Keep wrists straight and stacked over elbows.",
                    "too high": "Avoid bending wrists backward.",
                },
            },
        }
        
        exercise_suggestions = suggestions.get(exercise_type, {})
        criterion_suggestions = exercise_suggestions.get(criterion_name, {})
        
        return criterion_suggestions.get(direction, "Adjust form to meet target range.")
    
    def _get_affected_joints(self, exercise_type: ExerciseType, 
                           criterion_name: str) -> List[str]:
        """Get joints affected by a criterion"""
        joint_mapping = {
            "knee_angle": ["knee", "hip", "ankle"],
            "hip_angle": ["hip", "lower_back"],
            "elbow_angle": ["elbow", "shoulder", "wrist"],
            "back_straightness": ["spine", "lower_back", "neck"],
            "knee_over_toes": ["knee", "ankle"],
            "knee_valgus": ["knee", "hip"],
            "wrist_alignment": ["wrist", "forearm"],
            "body_alignment": ["core", "hip", "shoulders"],
        }
        
        # Find matching joint pattern
        for pattern, joints in joint_mapping.items():
            if pattern in criterion_name:
                return joints
                
        return ["full_body"]