"""
Form analysis module with environment-based model selection.
Supports both lite (Replit-compatible) and advanced (GPU-required) versions.
"""

import os
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseFormAnalyzer(ABC):
    """Abstract base class for form analyzers."""
    
    @abstractmethod
    def analyze(self, pose_data: Dict[str, Any], user_profile: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze exercise form from pose data.
        
        Args:
            pose_data: Dictionary containing pose landmarks and metadata
            user_profile: Optional user-specific parameters
            
        Returns:
            Analysis results including score and feedback
        """
        pass
    
    @abstractmethod
    def get_confidence_score(self, pose_data: Dict[str, Any]) -> float:
        """Get confidence score for pose detection quality."""
        pass


class LiteFormAnalyzer(BaseFormAnalyzer):
    """Lightweight form analyzer for Replit and resource-constrained environments."""
    
    def __init__(self):
        # Rule-based angle thresholds for different exercises
        self.angle_thresholds = {
            'squat': {
                'knee': {'ideal': 90, 'acceptable_range': (80, 100), 'critical_range': (70, 110)},
                'hip': {'ideal': 80, 'acceptable_range': (70, 90), 'critical_range': (60, 100)},
                'back': {'ideal': 180, 'acceptable_range': (170, 190), 'critical_range': (160, 200)}
            },
            'deadlift': {
                'hip': {'ideal': 30, 'acceptable_range': (20, 45), 'critical_range': (10, 60)},
                'knee': {'ideal': 170, 'acceptable_range': (160, 180), 'critical_range': (150, 190)},
                'back': {'ideal': 180, 'acceptable_range': (170, 190), 'critical_range': (160, 200)}
            },
            'bench_press': {
                'elbow': {'ideal': 90, 'acceptable_range': (85, 95), 'critical_range': (75, 105)},
                'shoulder': {'ideal': 75, 'acceptable_range': (70, 80), 'critical_range': (60, 90)},
                'wrist': {'ideal': 180, 'acceptable_range': (170, 190), 'critical_range': (160, 200)}
            }
        }
        
        # Movement patterns for phase detection
        self.movement_patterns = {
            'squat': ['standing', 'descending', 'bottom', 'ascending', 'standing'],
            'deadlift': ['setup', 'lift_off', 'lockout', 'descending', 'setup'],
            'bench_press': ['setup', 'descending', 'bottom', 'pressing', 'lockout']
        }
    
    def analyze(self, pose_data: Dict[str, Any], user_profile: Optional[Dict] = None) -> Dict[str, Any]:
        """Perform lightweight form analysis using rule-based approach."""
        start_time = datetime.now()
        
        # Extract landmarks and exercise type
        landmarks = pose_data.get('landmarks', [])
        exercise_type = pose_data.get('exercise_type', 'squat')
        
        # Calculate joint angles
        angles = self._calculate_angles(landmarks)
        
        # Evaluate angles against thresholds
        angle_scores = self._evaluate_angles(angles, exercise_type)
        
        # Detect movement phase
        phase = self._detect_phase(angles, exercise_type)
        
        # Generate feedback
        feedback = self._generate_feedback(angle_scores, phase, exercise_type)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(angle_scores)
        
        # Get pose detection confidence
        confidence = self.get_confidence_score(pose_data)
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return {
            'score': overall_score,
            'angle_scores': angle_scores,
            'phase': phase,
            'feedback': feedback,
            'confidence': confidence,
            'processing_time': processing_time,
            'analyzer_type': 'lite'
        }
    
    def get_confidence_score(self, pose_data: Dict[str, Any]) -> float:
        """Calculate confidence score based on landmark visibility."""
        landmarks = pose_data.get('landmarks', [])
        if not landmarks:
            return 0.0
        
        # Count visible landmarks
        visible_count = sum(1 for lm in landmarks if lm.get('visibility', 0) > 0.5)
        total_count = len(landmarks)
        
        # Calculate base confidence
        visibility_score = visible_count / total_count if total_count > 0 else 0
        
        # Adjust for critical landmarks
        critical_landmarks = self._get_critical_landmarks(pose_data.get('exercise_type', 'squat'))
        critical_visible = sum(1 for idx in critical_landmarks 
                             if idx < len(landmarks) and landmarks[idx].get('visibility', 0) > 0.7)
        critical_score = critical_visible / len(critical_landmarks) if critical_landmarks else 1
        
        # Combined score
        confidence = 0.7 * visibility_score + 0.3 * critical_score
        return round(confidence, 2)
    
    def _calculate_angles(self, landmarks: List[Dict]) -> Dict[str, float]:
        """Calculate joint angles from landmarks."""
        angles = {}
        
        if len(landmarks) < 33:  # MediaPipe pose has 33 landmarks
            return angles
        
        # Helper function to calculate angle between three points
        def calculate_angle(p1, p2, p3):
            """Calculate angle at p2."""
            a = np.array([p1['x'], p1['y']])
            b = np.array([p2['x'], p2['y']])
            c = np.array([p3['x'], p3['y']])
            
            ba = a - b
            bc = c - b
            
            cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
            angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
            return np.degrees(angle)
        
        # Calculate key angles
        try:
            # Knee angles
            angles['left_knee'] = calculate_angle(
                landmarks[23], landmarks[25], landmarks[27]  # Hip, knee, ankle
            )
            angles['right_knee'] = calculate_angle(
                landmarks[24], landmarks[26], landmarks[28]
            )
            
            # Hip angles
            angles['left_hip'] = calculate_angle(
                landmarks[11], landmarks[23], landmarks[25]  # Shoulder, hip, knee
            )
            angles['right_hip'] = calculate_angle(
                landmarks[12], landmarks[24], landmarks[26]
            )
            
            # Elbow angles
            angles['left_elbow'] = calculate_angle(
                landmarks[11], landmarks[13], landmarks[15]  # Shoulder, elbow, wrist
            )
            angles['right_elbow'] = calculate_angle(
                landmarks[12], landmarks[14], landmarks[16]
            )
            
            # Back angle (approximation)
            mid_shoulder = {
                'x': (landmarks[11]['x'] + landmarks[12]['x']) / 2,
                'y': (landmarks[11]['y'] + landmarks[12]['y']) / 2
            }
            mid_hip = {
                'x': (landmarks[23]['x'] + landmarks[24]['x']) / 2,
                'y': (landmarks[23]['y'] + landmarks[24]['y']) / 2
            }
            angles['back'] = calculate_angle(
                {'x': mid_shoulder['x'], 'y': mid_shoulder['y'] - 0.1},
                mid_shoulder,
                mid_hip
            )
            
        except Exception as e:
            logger.error(f"Error calculating angles: {e}")
        
        return angles
    
    def _evaluate_angles(self, angles: Dict[str, float], exercise_type: str) -> Dict[str, Dict]:
        """Evaluate angles against exercise-specific thresholds."""
        scores = {}
        thresholds = self.angle_thresholds.get(exercise_type, {})
        
        for joint, threshold_data in thresholds.items():
            # Get relevant angles
            if joint == 'knee':
                angle = np.mean([angles.get('left_knee', 90), angles.get('right_knee', 90)])
            elif joint == 'hip':
                angle = np.mean([angles.get('left_hip', 90), angles.get('right_hip', 90)])
            elif joint == 'elbow':
                angle = np.mean([angles.get('left_elbow', 90), angles.get('right_elbow', 90)])
            else:
                angle = angles.get(joint, threshold_data['ideal'])
            
            # Calculate score
            ideal = threshold_data['ideal']
            acceptable_range = threshold_data['acceptable_range']
            critical_range = threshold_data['critical_range']
            
            if acceptable_range[0] <= angle <= acceptable_range[1]:
                # Within acceptable range
                deviation = abs(angle - ideal)
                score = 1.0 - (deviation / (acceptable_range[1] - acceptable_range[0]))
            elif critical_range[0] <= angle <= critical_range[1]:
                # Within critical range
                if angle < acceptable_range[0]:
                    deviation = acceptable_range[0] - angle
                    max_deviation = acceptable_range[0] - critical_range[0]
                else:
                    deviation = angle - acceptable_range[1]
                    max_deviation = critical_range[1] - acceptable_range[1]
                score = 0.5 * (1 - deviation / max_deviation)
            else:
                # Outside critical range
                score = 0.0
            
            scores[joint] = {
                'angle': round(angle, 1),
                'score': round(score, 2),
                'ideal': ideal,
                'status': 'good' if score > 0.8 else 'warning' if score > 0.5 else 'critical'
            }
        
        return scores
    
    def _detect_phase(self, angles: Dict[str, float], exercise_type: str) -> str:
        """Detect current movement phase based on angles."""
        # Simplified phase detection based on key angles
        if exercise_type == 'squat':
            knee_angle = np.mean([angles.get('left_knee', 90), angles.get('right_knee', 90)])
            if knee_angle > 160:
                return 'standing'
            elif knee_angle > 120:
                return 'descending' if knee_angle > 140 else 'ascending'
            elif knee_angle > 70:
                return 'bottom'
            else:
                return 'too_deep'
        
        elif exercise_type == 'deadlift':
            hip_angle = np.mean([angles.get('left_hip', 90), angles.get('right_hip', 90)])
            if hip_angle < 30:
                return 'setup'
            elif hip_angle < 90:
                return 'lift_off'
            elif hip_angle > 160:
                return 'lockout'
            else:
                return 'descending'
        
        elif exercise_type == 'bench_press':
            elbow_angle = np.mean([angles.get('left_elbow', 90), angles.get('right_elbow', 90)])
            if elbow_angle > 160:
                return 'lockout'
            elif elbow_angle > 120:
                return 'pressing'
            elif elbow_angle > 70:
                return 'bottom'
            else:
                return 'descending'
        
        return 'unknown'
    
    def _generate_feedback(self, angle_scores: Dict[str, Dict], phase: str, exercise_type: str) -> List[Dict]:
        """Generate specific feedback based on analysis."""
        feedback = []
        
        # Phase-specific feedback
        phase_feedback = {
            'squat': {
                'standing': "良い開始姿勢です。背筋を伸ばしたまま降下を始めてください。",
                'descending': "降下中の姿勢を維持してください。膝がつま先より前に出すぎないよう注意。",
                'bottom': "素晴らしい深さです。この位置から力強く立ち上がってください。",
                'ascending': "良い上昇です。胸を張って最後まで押し上げてください。",
                'too_deep': "深すぎる可能性があります。腰への負担に注意してください。"
            },
            'deadlift': {
                'setup': "セットアップ良好。背中をまっすぐに保ち、腰から持ち上げてください。",
                'lift_off': "良いリフトオフです。背中の角度を維持してください。",
                'lockout': "完璧なロックアウト！肩を後ろに引いて胸を張ってください。",
                'descending': "コントロールを保ちながら降ろしてください。"
            },
            'bench_press': {
                'setup': "肩甲骨を寄せて、アーチを作ってください。",
                'descending': "ゆっくりとコントロールしながら降ろしてください。",
                'bottom': "胸にタッチ。一瞬止めてから押し上げてください。",
                'pressing': "力強く押し上げています。肘を伸ばしきってください。",
                'lockout': "完璧！次のレップの準備をしてください。"
            }
        }
        
        # Add phase feedback
        if exercise_type in phase_feedback and phase in phase_feedback[exercise_type]:
            feedback.append({
                'type': 'phase',
                'priority': 'info',
                'message': phase_feedback[exercise_type][phase]
            })
        
        # Joint-specific feedback
        for joint, score_data in angle_scores.items():
            if score_data['status'] == 'critical':
                feedback.append({
                    'type': 'angle',
                    'joint': joint,
                    'priority': 'critical',
                    'message': f"{joint}の角度が不適切です（{score_data['angle']}°）。理想は{score_data['ideal']}°です。"
                })
            elif score_data['status'] == 'warning':
                feedback.append({
                    'type': 'angle',
                    'joint': joint,
                    'priority': 'warning',
                    'message': f"{joint}の角度を改善できます（{score_data['angle']}°→{score_data['ideal']}°）。"
                })
        
        # Sort by priority
        priority_order = {'critical': 0, 'warning': 1, 'info': 2}
        feedback.sort(key=lambda x: priority_order.get(x['priority'], 3))
        
        return feedback[:3]  # Return top 3 feedback items
    
    def _calculate_overall_score(self, angle_scores: Dict[str, Dict]) -> float:
        """Calculate overall form score."""
        if not angle_scores:
            return 0.0
        
        # Weight different joints differently
        weights = {
            'knee': 0.3,
            'hip': 0.3,
            'back': 0.2,
            'elbow': 0.25,
            'shoulder': 0.25,
            'wrist': 0.1
        }
        
        total_score = 0
        total_weight = 0
        
        for joint, score_data in angle_scores.items():
            weight = weights.get(joint, 0.2)
            total_score += score_data['score'] * weight
            total_weight += weight
        
        overall = total_score / total_weight if total_weight > 0 else 0
        return round(overall * 100, 1)
    
    def _get_critical_landmarks(self, exercise_type: str) -> List[int]:
        """Get critical landmark indices for each exercise."""
        critical_landmarks = {
            'squat': [11, 12, 23, 24, 25, 26, 27, 28],  # Shoulders, hips, knees, ankles
            'deadlift': [11, 12, 15, 16, 23, 24, 25, 26],  # Shoulders, wrists, hips, knees
            'bench_press': [11, 12, 13, 14, 15, 16]  # Shoulders, elbows, wrists
        }
        return critical_landmarks.get(exercise_type, list(range(33)))


class AdvancedFormAnalyzer(BaseFormAnalyzer):
    """
    Advanced form analyzer with ML capabilities (requires GPU and additional dependencies).
    This is the ideal implementation that would be used in production environments.
    """
    
    def __init__(self):
        # Note: The following initialization is for the ideal implementation
        # In Replit environments, these models would not be loaded
        
        self.models_initialized = False
        
        # Placeholder for advanced models
        self.models = {
            'pose_3d': None,  # 3D pose estimation model
            'motion_lstm': None,  # LSTM for motion pattern analysis
            'personal_adaptation': None,  # User-specific adaptation model
            'form_classifier': None  # Multi-class form quality classifier
        }
        
        # Model configuration
        self.config = {
            'use_3d_pose': os.getenv('USE_3D_POSE', 'false').lower() == 'true',
            'use_motion_analysis': os.getenv('USE_MOTION_ANALYSIS', 'false').lower() == 'true',
            'use_personalization': os.getenv('USE_PERSONALIZATION', 'false').lower() == 'true',
            'ensemble_weights': [0.3, 0.3, 0.2, 0.2]  # Weights for model ensemble
        }
        
        # Try to initialize models if in advanced mode
        self._try_initialize_models()
    
    def _try_initialize_models(self):
        """Attempt to initialize ML models if environment supports it."""
        try:
            # Check if we have GPU support
            import torch
            if torch.cuda.is_available():
                logger.info("GPU detected, attempting to load advanced models...")
                # Model loading would happen here in production
                # self.models['pose_3d'] = self._load_pose_3d_model()
                # self.models['motion_lstm'] = self._load_motion_model()
                # etc.
                pass
            else:
                logger.info("No GPU detected, advanced features disabled")
        except ImportError:
            logger.info("PyTorch not available, advanced features disabled")
    
    def analyze(self, pose_data: Dict[str, Any], user_profile: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Perform advanced form analysis using ML models.
        Falls back to lite analysis if models are not available.
        """
        
        # Check if we have any advanced models loaded
        if not self.models_initialized or all(m is None for m in self.models.values()):
            # Fall back to lite analyzer
            logger.info("Advanced models not available, using lite analyzer")
            lite_analyzer = LiteFormAnalyzer()
            result = lite_analyzer.analyze(pose_data, user_profile)
            result['analyzer_type'] = 'advanced_fallback'
            return result
        
        # Advanced analysis implementation
        """
        # === IDEAL IMPLEMENTATION (Currently commented out) ===
        
        start_time = datetime.now()
        
        # Extract sequence data for temporal analysis
        landmark_sequence = pose_data.get('landmark_sequence', [pose_data.get('landmarks', [])])
        exercise_type = pose_data.get('exercise_type', 'squat')
        
        # 1. 3D Pose Estimation
        pose_3d_sequence = []
        if self.models['pose_3d'] and self.config['use_3d_pose']:
            for frame_landmarks in landmark_sequence:
                pose_3d = self._estimate_3d_pose(frame_landmarks)
                pose_3d_sequence.append(pose_3d)
        else:
            # Use 2D landmarks with depth estimation
            pose_3d_sequence = self._estimate_pseudo_3d(landmark_sequence)
        
        # 2. Motion Pattern Analysis
        motion_features = None
        if self.models['motion_lstm'] and self.config['use_motion_analysis']:
            motion_features = self._analyze_motion_patterns(pose_3d_sequence)
        
        # 3. Personal Adaptation
        personalized_criteria = None
        if user_profile and self.models['personal_adaptation'] and self.config['use_personalization']:
            personalized_criteria = self._adapt_criteria_to_user(user_profile, exercise_type)
        
        # 4. Multi-model Ensemble Prediction
        predictions = []
        
        # Form classifier prediction
        if self.models['form_classifier']:
            form_pred = self._classify_form_quality(pose_3d_sequence, motion_features)
            predictions.append(form_pred)
        
        # Rule-based prediction (always included)
        lite_analyzer = LiteFormAnalyzer()
        rule_based = lite_analyzer.analyze(pose_data, user_profile)
        predictions.append({'score': rule_based['score'] / 100, 'confidence': rule_based['confidence']})
        
        # 5. Weighted Ensemble
        final_score, ensemble_confidence = self._weighted_ensemble(predictions)
        
        # 6. Generate Explainable Feedback
        feedback = self._generate_advanced_feedback(
            pose_3d_sequence,
            motion_features,
            final_score,
            personalized_criteria
        )
        
        # 7. Calculate biomechanical metrics
        biomechanics = self._analyze_biomechanics(pose_3d_sequence, exercise_type)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return {
            'score': round(final_score * 100, 1),
            'confidence': ensemble_confidence,
            'feedback': feedback,
            'biomechanics': biomechanics,
            'motion_quality': motion_features,
            'processing_time': processing_time,
            'analyzer_type': 'advanced',
            'models_used': [k for k, v in self.models.items() if v is not None]
        }
        """
        
        # For now, use lite analyzer as fallback
        lite_analyzer = LiteFormAnalyzer()
        result = lite_analyzer.analyze(pose_data, user_profile)
        result['analyzer_type'] = 'advanced_placeholder'
        return result
    
    def get_confidence_score(self, pose_data: Dict[str, Any]) -> float:
        """
        Calculate advanced confidence score using multiple factors.
        """
        # Use lite analyzer's confidence as base
        lite_analyzer = LiteFormAnalyzer()
        base_confidence = lite_analyzer.get_confidence_score(pose_data)
        
        # In ideal implementation, would also consider:
        # - Temporal consistency across frames
        # - 3D reconstruction confidence
        # - Model ensemble agreement
        # - Biomechanical plausibility
        
        return base_confidence
    
    # === ADVANCED METHODS (Ideal Implementation) ===
    
    def _estimate_3d_pose(self, landmarks_2d: List[Dict]) -> np.ndarray:
        """
        Estimate 3D pose from 2D landmarks.
        Ideal implementation would use a trained model.
        """
        # Placeholder for 3D pose estimation
        # In production: return self.models['pose_3d'].predict(landmarks_2d)
        return np.zeros((33, 3))
    
    def _analyze_motion_patterns(self, pose_3d_sequence: List[np.ndarray]) -> Dict[str, Any]:
        """
        Analyze motion patterns using LSTM.
        """
        # Placeholder for motion analysis
        # In production: return self.models['motion_lstm'].analyze(pose_3d_sequence)
        return {
            'smoothness': 0.8,
            'tempo_consistency': 0.9,
            'range_of_motion': 0.85,
            'stability': 0.87
        }
    
    def _adapt_criteria_to_user(self, user_profile: Dict, exercise_type: str) -> Dict[str, Any]:
        """
        Adapt evaluation criteria based on user characteristics.
        """
        # Placeholder for personalization
        # Factors to consider:
        # - User's experience level
        # - Body proportions
        # - Injury history
        # - Personal goals
        return {
            'adjusted_rom': 1.0,
            'tempo_preference': 'moderate',
            'depth_adjustment': 0.0
        }
    
    def _generate_advanced_feedback(
        self, 
        pose_3d_sequence: List[np.ndarray],
        motion_features: Optional[Dict],
        score: float,
        personalized_criteria: Optional[Dict]
    ) -> List[Dict]:
        """
        Generate detailed, explainable feedback.
        """
        feedback = []
        
        # Placeholder for advanced feedback generation
        # Would include:
        # - Biomechanical insights
        # - Personalized recommendations
        # - Progressive cues based on skill level
        # - Video segments highlighting issues
        
        feedback.append({
            'type': 'advanced',
            'priority': 'info',
            'message': 'Advanced analysis is in development. Using standard feedback.'
        })
        
        return feedback
    
    def _analyze_biomechanics(self, pose_3d_sequence: List[np.ndarray], exercise_type: str) -> Dict[str, Any]:
        """
        Analyze biomechanical factors.
        """
        # Placeholder for biomechanical analysis
        return {
            'joint_stress': {'knee': 0.3, 'hip': 0.4, 'back': 0.2},
            'muscle_activation': {'quadriceps': 0.8, 'glutes': 0.7, 'core': 0.6},
            'force_distribution': 'balanced',
            'efficiency_score': 0.85
        }
    
    def _weighted_ensemble(self, predictions: List[Dict]) -> Tuple[float, float]:
        """
        Combine predictions from multiple models.
        """
        if not predictions:
            return 0.0, 0.0
        
        # Simple weighted average for now
        scores = [p.get('score', 0) for p in predictions]
        confidences = [p.get('confidence', 0) for p in predictions]
        
        # Use configured weights or equal weights
        weights = self.config['ensemble_weights'][:len(predictions)]
        if len(weights) < len(predictions):
            weights.extend([1.0] * (len(predictions) - len(weights)))
        
        # Normalize weights
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]
        
        # Calculate weighted averages
        final_score = sum(s * w for s, w in zip(scores, weights))
        final_confidence = sum(c * w for c, w in zip(confidences, weights))
        
        return final_score, final_confidence


class FormAnalyzerFactory:
    """Factory class to create appropriate analyzer based on environment."""
    
    @staticmethod
    def create_analyzer() -> BaseFormAnalyzer:
        """
        Create form analyzer based on MODEL_MODE environment variable.
        
        Returns:
            BaseFormAnalyzer: Either LiteFormAnalyzer or AdvancedFormAnalyzer
        """
        mode = os.getenv('MODEL_MODE', 'lite').lower()
        
        if mode == 'advanced':
            # Check if we have the resources for advanced mode
            if FormAnalyzerFactory._check_advanced_requirements():
                logger.info("Creating AdvancedFormAnalyzer")
                return AdvancedFormAnalyzer()
            else:
                logger.warning("Advanced mode requested but requirements not met, falling back to lite")
        
        logger.info("Creating LiteFormAnalyzer")
        return LiteFormAnalyzer()
    
    @staticmethod
    def _check_advanced_requirements() -> bool:
        """Check if system meets requirements for advanced analyzer."""
        requirements_met = True
        
        # Check for GPU
        try:
            import torch
            if not torch.cuda.is_available():
                logger.info("No GPU available for advanced mode")
                requirements_met = False
        except ImportError:
            logger.info("PyTorch not installed for advanced mode")
            requirements_met = False
        
        # Check for sufficient memory
        try:
            import psutil
            available_memory = psutil.virtual_memory().available / (1024 ** 3)  # GB
            if available_memory < 4:
                logger.info(f"Insufficient memory for advanced mode: {available_memory:.1f}GB")
                requirements_met = False
        except ImportError:
            pass
        
        # Check for ML model files (in production)
        # model_path = os.path.join(os.path.dirname(__file__), 'weights')
        # if not os.path.exists(model_path):
        #     logger.info("Model weights not found for advanced mode")
        #     requirements_met = False
        
        return requirements_met


# Convenience function for direct usage
def analyze_form(pose_data: Dict[str, Any], user_profile: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Analyze exercise form using the appropriate analyzer.
    
    Args:
        pose_data: Pose landmark data and metadata
        user_profile: Optional user-specific parameters
        
    Returns:
        Analysis results
    """
    analyzer = FormAnalyzerFactory.create_analyzer()
    return analyzer.analyze(pose_data, user_profile)