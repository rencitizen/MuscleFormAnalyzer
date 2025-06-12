"""
Real-time feedback system for dangerous exercise forms
"""
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
from collections import deque
import time

@dataclass
class SafetyAlert:
    """Safety alert for dangerous form"""
    severity: str  # "danger", "warning", "caution"
    issue: str
    body_part: str
    immediate_action: str
    audio_cue: str
    visual_indicator: Dict[str, Any]

class SafetyLevel(Enum):
    SAFE = "safe"
    CAUTION = "caution"
    WARNING = "warning"
    DANGER = "danger"

class RealtimeSafetyMonitor:
    """Monitor exercise form in real-time for safety issues"""
    
    def __init__(self, alert_cooldown: float = 2.0):
        """
        Args:
            alert_cooldown: Minimum seconds between same alerts
        """
        self.alert_cooldown = alert_cooldown
        self.last_alert_time = {}
        self.alert_history = deque(maxlen=100)
        
        # Define safety thresholds
        self.safety_thresholds = self._initialize_safety_thresholds()
        
    def _initialize_safety_thresholds(self) -> Dict[str, Dict[str, Any]]:
        """Initialize safety thresholds for various conditions"""
        return {
            'spine_flexion': {
                'caution': 20,    # degrees from neutral
                'warning': 30,
                'danger': 40,
                'body_part': 'lower_back',
                'issue': 'excessive spine flexion'
            },
            'knee_valgus': {
                'caution': 10,    # degrees of inward collapse
                'warning': 15,
                'danger': 20,
                'body_part': 'knees',
                'issue': 'knee caving inward'
            },
            'forward_lean': {
                'caution': 30,    # degrees from vertical
                'warning': 45,
                'danger': 60,
                'body_part': 'torso',
                'issue': 'excessive forward lean'
            },
            'shoulder_impingement': {
                'caution': 70,    # shoulder elevation angle
                'warning': 80,
                'danger': 90,
                'body_part': 'shoulders',
                'issue': 'shoulder impingement risk'
            },
            'wrist_deviation': {
                'caution': 20,    # degrees from neutral
                'warning': 30,
                'danger': 40,
                'body_part': 'wrists',
                'issue': 'wrist deviation'
            },
            'hip_shift': {
                'caution': 5,     # cm lateral shift
                'warning': 10,
                'danger': 15,
                'body_part': 'hips',
                'issue': 'lateral hip shift'
            },
            'neck_hyperextension': {
                'caution': 30,    # degrees from neutral
                'warning': 45,
                'danger': 60,
                'body_part': 'neck',
                'issue': 'neck hyperextension'
            }
        }
    
    def check_form_safety(self, landmarks_cm: Dict[str, Dict[str, float]], 
                         exercise_type: str,
                         current_phase: str) -> List[SafetyAlert]:
        """
        Check current form for safety issues
        
        Args:
            landmarks_cm: Landmarks in cm coordinates
            exercise_type: Type of exercise
            current_phase: Current exercise phase
            
        Returns:
            List of safety alerts (prioritized by severity)
        """
        alerts = []
        current_time = time.time()
        
        # Exercise-specific safety checks
        if exercise_type == 'squat':
            alerts.extend(self._check_squat_safety(landmarks_cm, current_phase))
        elif exercise_type == 'deadlift':
            alerts.extend(self._check_deadlift_safety(landmarks_cm, current_phase))
        elif exercise_type == 'bench_press':
            alerts.extend(self._check_bench_press_safety(landmarks_cm, current_phase))
        elif exercise_type == 'overhead_press':
            alerts.extend(self._check_overhead_press_safety(landmarks_cm, current_phase))
        
        # General safety checks applicable to all exercises
        alerts.extend(self._check_general_safety(landmarks_cm))
        
        # Filter alerts based on cooldown
        filtered_alerts = []
        for alert in alerts:
            alert_key = f"{alert.issue}_{alert.body_part}"
            last_time = self.last_alert_time.get(alert_key, 0)
            
            if current_time - last_time >= self.alert_cooldown:
                filtered_alerts.append(alert)
                self.last_alert_time[alert_key] = current_time
                self.alert_history.append({
                    'alert': alert,
                    'timestamp': current_time
                })
        
        # Sort by severity (danger > warning > caution)
        severity_order = {'danger': 0, 'warning': 1, 'caution': 2}
        filtered_alerts.sort(key=lambda a: severity_order.get(a.severity, 3))
        
        return filtered_alerts
    
    def _check_squat_safety(self, landmarks_cm: Dict[str, Dict[str, float]], 
                           phase: str) -> List[SafetyAlert]:
        """Check squat-specific safety issues"""
        alerts = []
        
        # Check knee valgus (knee caving)
        knee_valgus_angle = self._calculate_knee_valgus(landmarks_cm)
        if knee_valgus_angle is not None:
            alert = self._create_alert_from_threshold(
                'knee_valgus', knee_valgus_angle,
                immediate_actions={
                    'caution': "Focus on pushing knees out",
                    'warning': "Push knees out over toes",
                    'danger': "STOP - Reset and push knees out"
                }
            )
            if alert:
                alerts.append(alert)
        
        # Check forward lean
        if phase in ['bottom', 'middle']:
            forward_lean = self._calculate_forward_lean(landmarks_cm)
            if forward_lean is not None:
                alert = self._create_alert_from_threshold(
                    'forward_lean', forward_lean,
                    immediate_actions={
                        'caution': "Keep chest up",
                        'warning': "Chest up, weight on heels",
                        'danger': "STOP - Too much forward lean"
                    }
                )
                if alert:
                    alerts.append(alert)
        
        # Check hip shift
        hip_shift = self._calculate_hip_shift(landmarks_cm)
        if hip_shift is not None:
            alert = self._create_alert_from_threshold(
                'hip_shift', hip_shift,
                immediate_actions={
                    'caution': "Center your weight",
                    'warning': "Shift weight to center",
                    'danger': "STOP - Major hip shift detected"
                }
            )
            if alert:
                alerts.append(alert)
        
        return alerts
    
    def _check_deadlift_safety(self, landmarks_cm: Dict[str, Dict[str, float]], 
                             phase: str) -> List[SafetyAlert]:
        """Check deadlift-specific safety issues"""
        alerts = []
        
        # Check spine flexion (most critical for deadlifts)
        spine_flexion = self._calculate_spine_flexion(landmarks_cm)
        if spine_flexion is not None:
            alert = self._create_alert_from_threshold(
                'spine_flexion', spine_flexion,
                immediate_actions={
                    'caution': "Maintain neutral spine",
                    'warning': "Straighten your back",
                    'danger': "STOP - Back rounding detected"
                }
            )
            if alert:
                alerts.append(alert)
        
        # Check neck position
        neck_angle = self._calculate_neck_angle(landmarks_cm)
        if neck_angle is not None:
            alert = self._create_alert_from_threshold(
                'neck_hyperextension', neck_angle,
                immediate_actions={
                    'caution': "Keep neck neutral",
                    'warning': "Look down slightly",
                    'danger': "STOP - Neck hyperextended"
                }
            )
            if alert:
                alerts.append(alert)
        
        return alerts
    
    def _check_bench_press_safety(self, landmarks_cm: Dict[str, Dict[str, float]], 
                                phase: str) -> List[SafetyAlert]:
        """Check bench press-specific safety issues"""
        alerts = []
        
        # Check wrist alignment
        wrist_deviation = self._calculate_wrist_deviation(landmarks_cm)
        if wrist_deviation is not None:
            alert = self._create_alert_from_threshold(
                'wrist_deviation', wrist_deviation,
                immediate_actions={
                    'caution': "Keep wrists straight",
                    'warning': "Straighten wrists now",
                    'danger': "STOP - Wrist position dangerous"
                }
            )
            if alert:
                alerts.append(alert)
        
        # Check shoulder position (to avoid impingement)
        if phase == 'bottom':
            shoulder_angle = self._calculate_shoulder_angle(landmarks_cm)
            if shoulder_angle is not None:
                alert = self._create_alert_from_threshold(
                    'shoulder_impingement', shoulder_angle,
                    immediate_actions={
                        'caution': "Tuck elbows slightly",
                        'warning': "Bring elbows closer to body",
                        'danger': "STOP - Shoulder position risky"
                    }
                )
                if alert:
                    alerts.append(alert)
        
        return alerts
    
    def _check_overhead_press_safety(self, landmarks_cm: Dict[str, Dict[str, float]], 
                                   phase: str) -> List[SafetyAlert]:
        """Check overhead press-specific safety issues"""
        alerts = []
        
        # Check lower back hyperextension
        back_arch = self._calculate_back_arch(landmarks_cm)
        if back_arch is not None and back_arch > 25:  # degrees
            severity = 'danger' if back_arch > 40 else 'warning' if back_arch > 30 else 'caution'
            alert = SafetyAlert(
                severity=severity,
                issue='excessive back arch',
                body_part='lower_back',
                immediate_action={
                    'caution': "Engage core",
                    'warning': "Tighten abs, reduce arch",
                    'danger': "STOP - Excessive back arch"
                }[severity],
                audio_cue=f"{severity.upper()}: Back arch",
                visual_indicator={'type': 'spine_highlight', 'color': 'red'}
            )
            alerts.append(alert)
        
        return alerts
    
    def _check_general_safety(self, landmarks_cm: Dict[str, Dict[str, float]]) -> List[SafetyAlert]:
        """Check general safety issues applicable to all exercises"""
        alerts = []
        
        # Check for sudden position changes (potential loss of control)
        if hasattr(self, 'previous_landmarks'):
            max_movement = self._calculate_max_movement(
                self.previous_landmarks, landmarks_cm
            )
            
            if max_movement > 50:  # cm in one frame
                alert = SafetyAlert(
                    severity='warning',
                    issue='sudden movement detected',
                    body_part='full_body',
                    immediate_action="Slow down and control the movement",
                    audio_cue="WARNING: Control movement",
                    visual_indicator={'type': 'flash', 'color': 'yellow'}
                )
                alerts.append(alert)
        
        self.previous_landmarks = landmarks_cm.copy()
        
        return alerts
    
    def _calculate_knee_valgus(self, landmarks: Dict[str, Dict[str, float]]) -> Optional[float]:
        """Calculate knee valgus angle (inward collapse)"""
        left_hip = landmarks.get("LEFT_HIP")
        left_knee = landmarks.get("LEFT_KNEE")
        left_ankle = landmarks.get("LEFT_ANKLE")
        
        if all([left_hip, left_knee, left_ankle]):
            # Calculate expected knee position on straight line from hip to ankle
            expected_x = left_hip['x'] + (left_ankle['x'] - left_hip['x']) * 0.5
            actual_x = left_knee['x']
            
            # Calculate deviation angle
            valgus_angle = np.degrees(np.arctan2(
                actual_x - expected_x,
                left_hip['y'] - left_ankle['y']
            ))
            
            return abs(valgus_angle)
        
        return None
    
    def _calculate_spine_flexion(self, landmarks: Dict[str, Dict[str, float]]) -> Optional[float]:
        """Calculate spine flexion angle"""
        nose = landmarks.get("NOSE")
        left_shoulder = landmarks.get("LEFT_SHOULDER")
        right_shoulder = landmarks.get("RIGHT_SHOULDER")
        left_hip = landmarks.get("LEFT_HIP")
        right_hip = landmarks.get("RIGHT_HIP")
        
        if all([nose, left_shoulder, right_shoulder, left_hip, right_hip]):
            # Calculate spine line
            shoulder_center = {
                'x': (left_shoulder['x'] + right_shoulder['x']) / 2,
                'y': (left_shoulder['y'] + right_shoulder['y']) / 2,
                'z': (left_shoulder['z'] + right_shoulder['z']) / 2
            }
            hip_center = {
                'x': (left_hip['x'] + right_hip['x']) / 2,
                'y': (left_hip['y'] + right_hip['y']) / 2,
                'z': (left_hip['z'] + right_hip['z']) / 2
            }
            
            # Calculate angle between upper spine (nose-shoulders) and lower spine (shoulders-hips)
            upper_vector = np.array([
                nose['x'] - shoulder_center['x'],
                nose['y'] - shoulder_center['y'],
                nose['z'] - shoulder_center['z']
            ])
            lower_vector = np.array([
                shoulder_center['x'] - hip_center['x'],
                shoulder_center['y'] - hip_center['y'],
                shoulder_center['z'] - hip_center['z']
            ])
            
            # Calculate angle
            cos_angle = np.dot(upper_vector, lower_vector) / (
                np.linalg.norm(upper_vector) * np.linalg.norm(lower_vector)
            )
            flexion_angle = np.degrees(np.arccos(np.clip(cos_angle, -1, 1)))
            
            # Return deviation from straight line (180 degrees)
            return abs(180 - flexion_angle)
        
        return None
    
    def _calculate_forward_lean(self, landmarks: Dict[str, Dict[str, float]]) -> Optional[float]:
        """Calculate forward lean angle from vertical"""
        left_shoulder = landmarks.get("LEFT_SHOULDER")
        right_shoulder = landmarks.get("RIGHT_SHOULDER")
        left_hip = landmarks.get("LEFT_HIP")
        right_hip = landmarks.get("RIGHT_HIP")
        
        if all([left_shoulder, right_shoulder, left_hip, right_hip]):
            shoulder_center = {
                'x': (left_shoulder['x'] + right_shoulder['x']) / 2,
                'y': (left_shoulder['y'] + right_shoulder['y']) / 2
            }
            hip_center = {
                'x': (left_hip['x'] + right_hip['x']) / 2,
                'y': (left_hip['y'] + right_hip['y']) / 2
            }
            
            # Calculate angle from vertical
            dx = shoulder_center['x'] - hip_center['x']
            dy = shoulder_center['y'] - hip_center['y']
            angle = np.degrees(np.arctan2(abs(dx), dy))
            
            return angle
        
        return None
    
    def _calculate_hip_shift(self, landmarks: Dict[str, Dict[str, float]]) -> Optional[float]:
        """Calculate lateral hip shift"""
        left_hip = landmarks.get("LEFT_HIP")
        right_hip = landmarks.get("RIGHT_HIP")
        left_ankle = landmarks.get("LEFT_ANKLE")
        right_ankle = landmarks.get("RIGHT_ANKLE")
        
        if all([left_hip, right_hip, left_ankle, right_ankle]):
            # Calculate hip center and ankle center
            hip_center_x = (left_hip['x'] + right_hip['x']) / 2
            ankle_center_x = (left_ankle['x'] + right_ankle['x']) / 2
            
            # Calculate lateral shift
            shift_cm = abs(hip_center_x - ankle_center_x)
            
            return shift_cm
        
        return None
    
    def _calculate_neck_angle(self, landmarks: Dict[str, Dict[str, float]]) -> Optional[float]:
        """Calculate neck angle from neutral"""
        nose = landmarks.get("NOSE")
        left_shoulder = landmarks.get("LEFT_SHOULDER")
        right_shoulder = landmarks.get("RIGHT_SHOULDER")
        
        if all([nose, left_shoulder, right_shoulder]):
            shoulder_center = {
                'x': (left_shoulder['x'] + right_shoulder['x']) / 2,
                'y': (left_shoulder['y'] + right_shoulder['y']) / 2,
                'z': (left_shoulder['z'] + right_shoulder['z']) / 2
            }
            
            # Calculate neck vector
            neck_vector = np.array([
                nose['x'] - shoulder_center['x'],
                nose['y'] - shoulder_center['y'],
                nose['z'] - shoulder_center['z']
            ])
            
            # Calculate angle from vertical (neutral neck)
            vertical = np.array([0, 1, 0])
            cos_angle = np.dot(neck_vector, vertical) / np.linalg.norm(neck_vector)
            angle = np.degrees(np.arccos(np.clip(cos_angle, -1, 1)))
            
            return angle
        
        return None
    
    def _calculate_wrist_deviation(self, landmarks: Dict[str, Dict[str, float]]) -> Optional[float]:
        """Calculate wrist deviation from neutral"""
        left_elbow = landmarks.get("LEFT_ELBOW")
        left_wrist = landmarks.get("LEFT_WRIST")
        left_index = landmarks.get("LEFT_INDEX")
        
        if all([left_elbow, left_wrist, left_index]):
            # Calculate forearm vector
            forearm = np.array([
                left_wrist['x'] - left_elbow['x'],
                left_wrist['y'] - left_elbow['y'],
                left_wrist['z'] - left_elbow['z']
            ])
            
            # Calculate hand vector
            hand = np.array([
                left_index['x'] - left_wrist['x'],
                left_index['y'] - left_wrist['y'],
                left_index['z'] - left_wrist['z']
            ])
            
            # Calculate angle
            cos_angle = np.dot(forearm, hand) / (
                np.linalg.norm(forearm) * np.linalg.norm(hand)
            )
            deviation = np.degrees(np.arccos(np.clip(cos_angle, -1, 1)))
            
            # Return deviation from straight (180 degrees)
            return abs(180 - deviation)
        
        return None
    
    def _calculate_shoulder_angle(self, landmarks: Dict[str, Dict[str, float]]) -> Optional[float]:
        """Calculate shoulder abduction angle"""
        left_shoulder = landmarks.get("LEFT_SHOULDER")
        left_elbow = landmarks.get("LEFT_ELBOW")
        left_hip = landmarks.get("LEFT_HIP")
        
        if all([left_shoulder, left_elbow, left_hip]):
            # Calculate upper arm vector
            upper_arm = np.array([
                left_elbow['x'] - left_shoulder['x'],
                left_elbow['y'] - left_shoulder['y'],
                left_elbow['z'] - left_shoulder['z']
            ])
            
            # Calculate torso vector
            torso = np.array([
                left_shoulder['x'] - left_hip['x'],
                left_shoulder['y'] - left_hip['y'],
                left_shoulder['z'] - left_hip['z']
            ])
            
            # Calculate angle
            cos_angle = np.dot(upper_arm, torso) / (
                np.linalg.norm(upper_arm) * np.linalg.norm(torso)
            )
            angle = np.degrees(np.arccos(np.clip(cos_angle, -1, 1)))
            
            return angle
        
        return None
    
    def _calculate_back_arch(self, landmarks: Dict[str, Dict[str, float]]) -> Optional[float]:
        """Calculate lower back arch angle"""
        left_shoulder = landmarks.get("LEFT_SHOULDER")
        right_shoulder = landmarks.get("RIGHT_SHOULDER")
        left_hip = landmarks.get("LEFT_HIP")
        right_hip = landmarks.get("RIGHT_HIP")
        
        if all([left_shoulder, right_shoulder, left_hip, right_hip]):
            shoulder_center = {
                'z': (left_shoulder['z'] + right_shoulder['z']) / 2
            }
            hip_center = {
                'z': (left_hip['z'] + right_hip['z']) / 2
            }
            
            # Calculate arch based on z-displacement
            arch_displacement = abs(shoulder_center['z'] - hip_center['z'])
            
            # Convert to approximate angle (rough estimation)
            arch_angle = arch_displacement * 10  # Scaling factor
            
            return arch_angle
        
        return None
    
    def _calculate_max_movement(self, prev_landmarks: Dict[str, Dict[str, float]], 
                              curr_landmarks: Dict[str, Dict[str, float]]) -> float:
        """Calculate maximum movement of any landmark between frames"""
        max_movement = 0.0
        
        for landmark_name in curr_landmarks:
            if landmark_name in prev_landmarks:
                prev = prev_landmarks[landmark_name]
                curr = curr_landmarks[landmark_name]
                
                movement = np.sqrt(
                    (curr['x'] - prev['x'])**2 +
                    (curr['y'] - prev['y'])**2 +
                    (curr['z'] - prev['z'])**2
                )
                
                max_movement = max(max_movement, movement)
        
        return max_movement
    
    def _create_alert_from_threshold(self, metric_name: str, value: float,
                                   immediate_actions: Dict[str, str]) -> Optional[SafetyAlert]:
        """Create alert based on threshold configuration"""
        config = self.safety_thresholds.get(metric_name)
        if not config:
            return None
            
        severity = None
        if value >= config['danger']:
            severity = 'danger'
        elif value >= config['warning']:
            severity = 'warning'
        elif value >= config['caution']:
            severity = 'caution'
            
        if severity:
            return SafetyAlert(
                severity=severity,
                issue=config['issue'],
                body_part=config['body_part'],
                immediate_action=immediate_actions[severity],
                audio_cue=f"{severity.upper()}: {config['issue']}",
                visual_indicator={
                    'type': 'highlight',
                    'body_part': config['body_part'],
                    'color': {'danger': 'red', 'warning': 'orange', 'caution': 'yellow'}[severity]
                }
            )
        
        return None
    
    def get_safety_summary(self) -> Dict[str, Any]:
        """Get summary of safety alerts from current session"""
        if not self.alert_history:
            return {'total_alerts': 0, 'by_severity': {}, 'by_body_part': {}}
            
        summary = {
            'total_alerts': len(self.alert_history),
            'by_severity': {'danger': 0, 'warning': 0, 'caution': 0},
            'by_body_part': {},
            'most_common_issues': []
        }
        
        issue_counts = {}
        
        for entry in self.alert_history:
            alert = entry['alert']
            summary['by_severity'][alert.severity] += 1
            
            if alert.body_part not in summary['by_body_part']:
                summary['by_body_part'][alert.body_part] = 0
            summary['by_body_part'][alert.body_part] += 1
            
            if alert.issue not in issue_counts:
                issue_counts[alert.issue] = 0
            issue_counts[alert.issue] += 1
        
        # Get top 3 most common issues
        sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
        summary['most_common_issues'] = [
            {'issue': issue, 'count': count} 
            for issue, count in sorted_issues[:3]
        ]
        
        return summary