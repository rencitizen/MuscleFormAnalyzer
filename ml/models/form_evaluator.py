"""
Form evaluation model for exercise quality assessment.
Provides scores and feedback for exercise form.
"""

import numpy as np
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class FormFeedback:
    """Feedback for a specific form aspect."""
    aspect: str
    score: float  # 0-100
    message: str
    severity: str  # 'good', 'warning', 'error'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'aspect': self.aspect,
            'score': self.score,
            'message': self.message,
            'severity': self.severity
        }


class FormEvaluator:
    """Evaluates exercise form quality."""
    
    def __init__(self, exercise_type: str = 'squat'):
        """
        Initialize form evaluator.
        
        Args:
            exercise_type: Type of exercise to evaluate
        """
        self.exercise_type = exercise_type
        self.ideal_angles = self._get_ideal_angles()
        self.evaluation_criteria = self._get_evaluation_criteria()
    
    def _get_ideal_angles(self) -> Dict[str, float]:
        """Get ideal angles for the exercise."""
        if self.exercise_type == 'squat':
            return {
                'knee_angle_bottom': 90.0,  # degrees
                'hip_angle_bottom': 80.0,
                'back_angle': 15.0,  # Forward lean from vertical
                'knee_tracking': 0.0,  # Knee-toe alignment
            }
        elif self.exercise_type == 'bench_press':
            return {
                'elbow_angle_bottom': 90.0,
                'wrist_alignment': 0.0,  # Wrist straight
                'bar_path_deviation': 0.05,  # Max deviation from vertical
            }
        elif self.exercise_type == 'deadlift':
            return {
                'hip_angle_start': 45.0,
                'back_angle': 10.0,  # Nearly straight back
                'knee_angle_start': 140.0,
                'bar_distance': 0.05,  # Bar close to body
            }
        else:
            return {}
    
    def _get_evaluation_criteria(self) -> Dict[str, Dict[str, Any]]:
        """Get evaluation criteria for the exercise."""
        if self.exercise_type == 'squat':
            return {
                'depth': {
                    'weight': 0.3,
                    'ideal': 90.0,
                    'tolerance': 15.0,
                    'messages': {
                        'good': "Good squat depth!",
                        'warning': "Try to go a bit deeper",
                        'error': "Not reaching proper depth"
                    }
                },
                'knee_tracking': {
                    'weight': 0.25,
                    'ideal': 0.0,
                    'tolerance': 0.1,
                    'messages': {
                        'good': "Knees tracking well over toes",
                        'warning': "Watch your knee alignment",
                        'error': "Knees caving in - push them out"
                    }
                },
                'back_angle': {
                    'weight': 0.25,
                    'ideal': 15.0,
                    'tolerance': 10.0,
                    'messages': {
                        'good': "Good back position",
                        'warning': "Keep your chest up",
                        'error': "Too much forward lean"
                    }
                },
                'balance': {
                    'weight': 0.2,
                    'ideal': 0.0,
                    'tolerance': 0.05,
                    'messages': {
                        'good': "Well balanced",
                        'warning': "Slight balance shift detected",
                        'error': "Weight shifting too much"
                    }
                }
            }
        elif self.exercise_type == 'bench_press':
            return {
                'elbow_angle': {
                    'weight': 0.3,
                    'ideal': 90.0,
                    'tolerance': 10.0,
                    'messages': {
                        'good': "Good elbow position at bottom",
                        'warning': "Elbows could go a bit lower",
                        'error': "Not reaching full range of motion"
                    }
                },
                'bar_path': {
                    'weight': 0.3,
                    'ideal': 0.0,
                    'tolerance': 0.05,
                    'messages': {
                        'good': "Excellent bar path",
                        'warning': "Bar path slightly off",
                        'error': "Bar path too curved"
                    }
                },
                'wrist_position': {
                    'weight': 0.2,
                    'ideal': 0.0,
                    'tolerance': 15.0,
                    'messages': {
                        'good': "Wrists are straight",
                        'warning': "Watch your wrist position",
                        'error': "Wrists are bent too much"
                    }
                },
                'stability': {
                    'weight': 0.2,
                    'ideal': 0.0,
                    'tolerance': 0.02,
                    'messages': {
                        'good': "Very stable movement",
                        'warning': "Some wobbling detected",
                        'error': "Too much instability"
                    }
                }
            }
        elif self.exercise_type == 'deadlift':
            return {
                'back_straightness': {
                    'weight': 0.35,
                    'ideal': 10.0,
                    'tolerance': 10.0,
                    'messages': {
                        'good': "Excellent back position",
                        'warning': "Keep your back neutral",
                        'error': "Back is rounding - dangerous!"
                    }
                },
                'hip_hinge': {
                    'weight': 0.25,
                    'ideal': 45.0,
                    'tolerance': 15.0,
                    'messages': {
                        'good': "Good hip hinge pattern",
                        'warning': "Focus on pushing hips back",
                        'error': "Not enough hip hinge"
                    }
                },
                'bar_path': {
                    'weight': 0.25,
                    'ideal': 0.0,
                    'tolerance': 0.05,
                    'messages': {
                        'good': "Bar staying close to body",
                        'warning': "Keep the bar closer",
                        'error': "Bar drifting away from body"
                    }
                },
                'lockout': {
                    'weight': 0.15,
                    'ideal': 180.0,
                    'tolerance': 10.0,
                    'messages': {
                        'good': "Full lockout achieved",
                        'warning': "Almost at full extension",
                        'error': "Not completing the lift"
                    }
                }
            }
        else:
            return {}
    
    def evaluate_form(
        self, 
        landmarks: np.ndarray,
        phase: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate form for a single frame.
        
        Args:
            landmarks: 33x3 array of pose landmarks
            phase: Current exercise phase (optional)
            
        Returns:
            Evaluation results with scores and feedback
        """
        # Calculate metrics based on exercise type
        metrics = self._calculate_metrics(landmarks, phase)
        
        # Evaluate each criterion
        feedback_list = []
        total_score = 0
        total_weight = 0
        
        for criterion, config in self.evaluation_criteria.items():
            if criterion in metrics:
                score, severity = self._evaluate_criterion(
                    metrics[criterion],
                    config['ideal'],
                    config['tolerance']
                )
                
                feedback = FormFeedback(
                    aspect=criterion,
                    score=score,
                    message=config['messages'][severity],
                    severity=severity
                )
                feedback_list.append(feedback)
                
                # Add to weighted score
                total_score += score * config['weight']
                total_weight += config['weight']
        
        # Calculate overall score
        overall_score = total_score / total_weight if total_weight > 0 else 0
        
        return {
            'overall_score': overall_score,
            'feedback': [f.to_dict() for f in feedback_list],
            'metrics': metrics,
            'phase': phase
        }
    
    def _calculate_metrics(
        self, 
        landmarks: np.ndarray,
        phase: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Calculate form metrics from landmarks.
        
        Args:
            landmarks: 33x3 array of pose landmarks
            phase: Current exercise phase
            
        Returns:
            Dictionary of calculated metrics
        """
        metrics = {}
        
        # MediaPipe landmark indices
        LEFT_SHOULDER = 11
        RIGHT_SHOULDER = 12
        LEFT_HIP = 23
        RIGHT_HIP = 24
        LEFT_KNEE = 25
        RIGHT_KNEE = 26
        LEFT_ANKLE = 27
        RIGHT_ANKLE = 28
        LEFT_ELBOW = 13
        RIGHT_ELBOW = 14
        LEFT_WRIST = 15
        RIGHT_WRIST = 16
        
        if self.exercise_type == 'squat':
            # Only evaluate key metrics at bottom phase
            if phase == 'bottom' or phase is None:
                # Knee angle
                left_knee_angle = self._calculate_angle(
                    landmarks[LEFT_HIP],
                    landmarks[LEFT_KNEE],
                    landmarks[LEFT_ANKLE]
                )
                right_knee_angle = self._calculate_angle(
                    landmarks[RIGHT_HIP],
                    landmarks[RIGHT_KNEE],
                    landmarks[RIGHT_ANKLE]
                )
                metrics['depth'] = (left_knee_angle + right_knee_angle) / 2
                
                # Knee tracking (x-position relative to toes)
                knee_x = (landmarks[LEFT_KNEE][0] + landmarks[RIGHT_KNEE][0]) / 2
                ankle_x = (landmarks[LEFT_ANKLE][0] + landmarks[RIGHT_ANKLE][0]) / 2
                metrics['knee_tracking'] = abs(knee_x - ankle_x)
                
                # Back angle (from vertical)
                hip_center = (landmarks[LEFT_HIP] + landmarks[RIGHT_HIP]) / 2
                shoulder_center = (landmarks[LEFT_SHOULDER] + landmarks[RIGHT_SHOULDER]) / 2
                back_vector = shoulder_center - hip_center
                vertical = np.array([0, -1, 0])
                back_angle = self._angle_between_vectors(back_vector, vertical)
                metrics['back_angle'] = back_angle
                
                # Balance (center of mass shift)
                com_x = (shoulder_center[0] + hip_center[0]) / 2
                base_x = ankle_x
                metrics['balance'] = abs(com_x - base_x)
        
        elif self.exercise_type == 'bench_press':
            if phase == 'bottom' or phase is None:
                # Elbow angle
                left_elbow_angle = self._calculate_angle(
                    landmarks[LEFT_SHOULDER],
                    landmarks[LEFT_ELBOW],
                    landmarks[LEFT_WRIST]
                )
                right_elbow_angle = self._calculate_angle(
                    landmarks[RIGHT_SHOULDER],
                    landmarks[RIGHT_ELBOW],
                    landmarks[RIGHT_WRIST]
                )
                metrics['elbow_angle'] = (left_elbow_angle + right_elbow_angle) / 2
                
                # Bar path (wrist deviation from shoulder)
                wrist_x = (landmarks[LEFT_WRIST][0] + landmarks[RIGHT_WRIST][0]) / 2
                shoulder_x = (landmarks[LEFT_SHOULDER][0] + landmarks[RIGHT_SHOULDER][0]) / 2
                metrics['bar_path'] = abs(wrist_x - shoulder_x)
                
                # Wrist alignment
                left_wrist_angle = self._calculate_wrist_angle(
                    landmarks[LEFT_ELBOW],
                    landmarks[LEFT_WRIST]
                )
                right_wrist_angle = self._calculate_wrist_angle(
                    landmarks[RIGHT_ELBOW],
                    landmarks[RIGHT_WRIST]
                )
                metrics['wrist_position'] = (abs(left_wrist_angle) + abs(right_wrist_angle)) / 2
                
                # Stability (movement variance)
                metrics['stability'] = 0.0  # Would need multiple frames
        
        elif self.exercise_type == 'deadlift':
            # Back straightness
            hip_center = (landmarks[LEFT_HIP] + landmarks[RIGHT_HIP]) / 2
            shoulder_center = (landmarks[LEFT_SHOULDER] + landmarks[RIGHT_SHOULDER]) / 2
            back_vector = shoulder_center - hip_center
            vertical = np.array([0, -1, 0])
            metrics['back_straightness'] = self._angle_between_vectors(back_vector, vertical)
            
            # Hip hinge angle
            knee_center = (landmarks[LEFT_KNEE] + landmarks[RIGHT_KNEE]) / 2
            hip_angle = self._calculate_angle(
                shoulder_center,
                hip_center,
                knee_center
            )
            metrics['hip_hinge'] = 180 - hip_angle  # Convert to hinge angle
            
            # Bar path (wrist distance from body)
            wrist_center = (landmarks[LEFT_WRIST] + landmarks[RIGHT_WRIST]) / 2
            ankle_center = (landmarks[LEFT_ANKLE] + landmarks[RIGHT_ANKLE]) / 2
            metrics['bar_path'] = abs(wrist_center[0] - ankle_center[0])
            
            if phase == 'top':
                # Lockout (hip extension)
                metrics['lockout'] = hip_angle
        
        return metrics
    
    def _calculate_angle(self, p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> float:
        """Calculate angle between three points."""
        v1 = p1 - p2
        v2 = p3 - p2
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
        angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))
        return np.degrees(angle)
    
    def _angle_between_vectors(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """Calculate angle between two vectors."""
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
        angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))
        return np.degrees(angle)
    
    def _calculate_wrist_angle(self, elbow: np.ndarray, wrist: np.ndarray) -> float:
        """Calculate wrist deviation angle."""
        forearm_vector = wrist - elbow
        # Project to xy plane
        forearm_2d = forearm_vector[:2]
        vertical_2d = np.array([0, 1])
        angle = self._angle_between_vectors(forearm_2d, vertical_2d)
        return angle - 90  # Deviation from perpendicular
    
    def _evaluate_criterion(
        self, 
        value: float, 
        ideal: float, 
        tolerance: float
    ) -> Tuple[float, str]:
        """
        Evaluate a single criterion.
        
        Args:
            value: Measured value
            ideal: Ideal value
            tolerance: Acceptable tolerance
            
        Returns:
            Tuple of (score, severity)
        """
        deviation = abs(value - ideal)
        
        if deviation <= tolerance:
            score = 100 - (deviation / tolerance) * 20
            severity = 'good'
        elif deviation <= tolerance * 2:
            score = 80 - ((deviation - tolerance) / tolerance) * 30
            severity = 'warning'
        else:
            score = max(0, 50 - ((deviation - tolerance * 2) / tolerance) * 25)
            severity = 'error'
        
        return score, severity


def evaluate_exercise_sequence(
    landmark_sequence: List[np.ndarray],
    exercise_type: str,
    phase_sequence: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Evaluate form throughout an exercise sequence.
    
    Args:
        landmark_sequence: List of 33x3 landmark arrays
        exercise_type: Type of exercise
        phase_sequence: Optional list of phases for each frame
        
    Returns:
        Comprehensive evaluation results
    """
    evaluator = FormEvaluator(exercise_type)
    
    # Evaluate each frame
    frame_evaluations = []
    all_scores = []
    
    for i, landmarks in enumerate(landmark_sequence):
        phase = phase_sequence[i] if phase_sequence else None
        evaluation = evaluator.evaluate_form(landmarks, phase)
        frame_evaluations.append(evaluation)
        all_scores.append(evaluation['overall_score'])
    
    # Aggregate results
    avg_score = np.mean(all_scores) if all_scores else 0
    min_score = np.min(all_scores) if all_scores else 0
    max_score = np.max(all_scores) if all_scores else 0
    
    # Find most common issues
    issue_counts = {}
    for evaluation in frame_evaluations:
        for feedback in evaluation['feedback']:
            if feedback['severity'] in ['warning', 'error']:
                issue = feedback['aspect']
                if issue not in issue_counts:
                    issue_counts[issue] = 0
                issue_counts[issue] += 1
    
    # Get top issues
    top_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    
    # Generate summary feedback
    if avg_score >= 85:
        summary = "Excellent form overall! Keep up the great work."
    elif avg_score >= 70:
        summary = "Good form with some minor areas for improvement."
    elif avg_score >= 50:
        summary = "Form needs work. Focus on the highlighted issues."
    else:
        summary = "Significant form issues detected. Consider reducing weight and focusing on technique."
    
    return {
        'average_score': avg_score,
        'min_score': min_score,
        'max_score': max_score,
        'frame_count': len(landmark_sequence),
        'top_issues': [{'issue': issue, 'count': count} for issue, count in top_issues],
        'summary': summary,
        'exercise_type': exercise_type
    }


if __name__ == "__main__":
    # Test the form evaluator
    evaluator = FormEvaluator('squat')
    
    # Create test landmarks for squat at bottom position
    test_landmarks = np.zeros((33, 3))
    # Set key positions
    test_landmarks[11] = [0.4, 0.3, 0]  # left shoulder
    test_landmarks[12] = [0.6, 0.3, 0]  # right shoulder
    test_landmarks[23] = [0.45, 0.6, 0]  # left hip
    test_landmarks[24] = [0.55, 0.6, 0]  # right hip
    test_landmarks[25] = [0.44, 0.8, 0.1]  # left knee
    test_landmarks[26] = [0.56, 0.8, 0.1]  # right knee
    test_landmarks[27] = [0.43, 0.95, 0]  # left ankle
    test_landmarks[28] = [0.57, 0.95, 0]  # right ankle
    
    # Evaluate
    result = evaluator.evaluate_form(test_landmarks, phase='bottom')
    print(f"Overall score: {result['overall_score']:.1f}")
    print("\nFeedback:")
    for feedback in result['feedback']:
        print(f"- {feedback['aspect']}: {feedback['message']} (score: {feedback['score']:.1f})")