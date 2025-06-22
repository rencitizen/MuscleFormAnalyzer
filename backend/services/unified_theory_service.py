"""Unified Theory Service for comprehensive form analysis.

This service integrates physics, biomechanics, complex systems, and optimization
engines to provide scientifically-grounded form analysis and recommendations.
"""

import numpy as np
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

from backend.core.unified_theory import (
    PhysicsEngine,
    BiomechanicsAnalyzer,
    ComplexSystemsAnalyzer,
    OptimizationEngine,
    MovementPhase
)
from backend.services.mediapipe_service import MediaPipeService

logger = logging.getLogger(__name__)


class UnifiedTheoryService:
    """Service that applies unified theory principles to form analysis."""
    
    def __init__(self):
        """Initialize the unified theory service."""
        self.mediapipe_service = MediaPipeService()
        self.physics_engine = PhysicsEngine()
        self.biomechanics_analyzer = BiomechanicsAnalyzer()
        self.complex_systems_analyzer = ComplexSystemsAnalyzer()
        self.optimization_engine = OptimizationEngine()
        
        # Analysis history for temporal analysis
        self.movement_history = []
        self.analysis_results_history = []
        
    async def analyze_frame_unified(self, frame: np.ndarray,
                                   exercise_type: str,
                                   user_profile: Dict[str, Any],
                                   calibration_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Analyze a single frame using unified theory principles.
        
        Args:
            frame: Video frame as numpy array
            exercise_type: Type of exercise being performed
            user_profile: User's physical measurements and goals
            calibration_data: Optional calibration information
            
        Returns:
            Comprehensive analysis results
        """
        # Get basic pose detection from MediaPipe
        basic_analysis = await self.mediapipe_service.analyze_frame(
            frame, exercise_type
        )
        
        if not basic_analysis or not basic_analysis.get('pose_landmarks'):
            return {
                'success': False,
                'error': 'No pose detected',
                'timestamp': datetime.now().isoformat()
            }
            
        # Convert MediaPipe landmarks to unified format
        landmarks = self._convert_mediapipe_landmarks(
            basic_analysis['pose_landmarks'],
            calibration_data
        )
        
        # Apply physics engine
        physics_results = self._apply_physics_analysis(
            landmarks, user_profile, calibration_data
        )
        
        # Apply biomechanics analysis
        biomechanics_results = self._apply_biomechanics_analysis(
            landmarks, physics_results, exercise_type
        )
        
        # Update movement history
        self.movement_history.append(landmarks)
        if len(self.movement_history) > 100:  # Keep last 100 frames
            self.movement_history.pop(0)
            
        # Apply complex systems analysis if enough history
        complex_systems_results = {}
        if len(self.movement_history) >= 10:
            complex_systems_results = self._apply_complex_systems_analysis(
                self.movement_history, exercise_type
            )
            
        # Apply optimization engine
        optimization_results = self._apply_optimization(
            physics_results.get('joint_angles', {}),
            user_profile,
            exercise_type
        )
        
        # Calculate unified theory scores
        unified_scores = self._calculate_unified_scores(
            physics_results,
            biomechanics_results,
            complex_systems_results,
            optimization_results
        )
        
        # Generate comprehensive feedback
        feedback = self._generate_unified_feedback(
            unified_scores,
            physics_results,
            biomechanics_results,
            optimization_results
        )
        
        # Compile results
        result = {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'frame_number': len(self.movement_history),
            'exercise_type': exercise_type,
            'landmarks': self._landmarks_to_dict(landmarks),
            'basic_analysis': basic_analysis,
            'physics': physics_results,
            'biomechanics': biomechanics_results,
            'complex_systems': complex_systems_results,
            'optimization': optimization_results,
            'unified_scores': unified_scores,
            'feedback': feedback,
            'annotated_frame': basic_analysis.get('annotated_frame')
        }
        
        # Store in history
        self.analysis_results_history.append(result)
        if len(self.analysis_results_history) > 100:
            self.analysis_results_history.pop(0)
            
        return result
    
    async def analyze_movement_sequence(self, frames: List[np.ndarray],
                                      exercise_type: str,
                                      user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a complete movement sequence.
        
        Args:
            frames: List of video frames
            exercise_type: Type of exercise
            user_profile: User profile
            
        Returns:
            Comprehensive sequence analysis
        """
        sequence_results = []
        
        # Analyze each frame
        for frame in frames:
            result = await self.analyze_frame_unified(
                frame, exercise_type, user_profile
            )
            sequence_results.append(result)
            
        # Aggregate results
        aggregated = self._aggregate_sequence_results(
            sequence_results, exercise_type
        )
        
        return aggregated
    
    def _convert_mediapipe_landmarks(self, mediapipe_landmarks: List[Any],
                                   calibration_data: Optional[Dict]) -> Dict[str, np.ndarray]:
        """Convert MediaPipe landmarks to unified format."""
        landmarks = {}
        
        # Key landmark mappings
        landmark_map = {
            11: 'left_shoulder',
            12: 'right_shoulder',
            13: 'left_elbow',
            14: 'right_elbow',
            15: 'left_wrist',
            16: 'right_wrist',
            23: 'left_hip',
            24: 'right_hip',
            25: 'left_knee',
            26: 'right_knee',
            27: 'left_ankle',
            28: 'right_ankle'
        }
        
        # Extract landmarks
        for idx, name in landmark_map.items():
            if idx < len(mediapipe_landmarks):
                landmark = mediapipe_landmarks[idx]
                landmarks[name] = np.array([landmark.x, landmark.y, landmark.z])
                
        # Calculate derived landmarks
        if 'left_shoulder' in landmarks and 'right_shoulder' in landmarks:
            landmarks['shoulder'] = (landmarks['left_shoulder'] + landmarks['right_shoulder']) / 2
            
        if 'left_hip' in landmarks and 'right_hip' in landmarks:
            landmarks['hip'] = (landmarks['left_hip'] + landmarks['right_hip']) / 2
            
        if 'left_knee' in landmarks and 'right_knee' in landmarks:
            landmarks['knee'] = (landmarks['left_knee'] + landmarks['right_knee']) / 2
            
        if 'left_elbow' in landmarks and 'right_elbow' in landmarks:
            landmarks['elbow'] = (landmarks['left_elbow'] + landmarks['right_elbow']) / 2
            
        # Add spine approximation
        if 'shoulder' in landmarks and 'hip' in landmarks:
            landmarks['spine_mid'] = (landmarks['shoulder'] + landmarks['hip']) / 2
            
        # Add vertical reference
        landmarks['vertical_ref'] = np.array([0, 1, 0])
        
        # Apply calibration if available
        if calibration_data and 'height_reference' in calibration_data:
            scale_factor = calibration_data['height_reference'] / 100.0
            for key in landmarks:
                if key != 'vertical_ref':
                    landmarks[key] *= scale_factor
                    
        return landmarks
    
    def _apply_physics_analysis(self, landmarks: Dict[str, np.ndarray],
                              user_profile: Dict[str, Any],
                              calibration_data: Optional[Dict]) -> Dict[str, Any]:
        """Apply physics engine analysis."""
        results = {}
        
        # Calculate joint angles
        results['joint_angles'] = self.physics_engine.calculate_joint_angles(landmarks)
        
        # Calculate moment arms
        height_cm = user_profile.get('physicalMeasurements', {}).get('height', 170)
        results['moment_arms'] = self.physics_engine.calculate_moment_arms(
            landmarks, height_cm
        )
        
        # Calculate center of mass
        weight_kg = user_profile.get('physicalMeasurements', {}).get('weight', 70)
        results['center_of_mass'] = self.physics_engine.calculate_center_of_mass(
            landmarks, weight_kg
        )
        
        # Calculate force distribution
        external_load = user_profile.get('current_load_kg', 0)
        results['force_distribution'] = self.physics_engine.calculate_force_distribution(
            landmarks, external_load
        )
        
        # Energy efficiency (requires movement history)
        if len(self.movement_history) > 1:
            time_stamps = [i * 0.033 for i in range(len(self.movement_history))]  # 30fps
            results['energy_efficiency'] = self.physics_engine.assess_energy_efficiency(
                self.movement_history[-10:], time_stamps[-10:]
            )
        else:
            results['energy_efficiency'] = 0.5
            
        return results
    
    def _apply_biomechanics_analysis(self, landmarks: Dict[str, np.ndarray],
                                    physics_results: Dict[str, Any],
                                    exercise_type: str) -> Dict[str, Any]:
        """Apply biomechanics analyzer."""
        results = {}
        
        # Detect movement phase
        if len(self.movement_history) > 1:
            phases = self.biomechanics_analyzer.detect_movement_phases(
                self.movement_history[-10:], exercise_type
            )
            results['current_phase'] = phases[-1] if phases else MovementPhase.SETUP
            results['phase_history'] = phases
        else:
            results['current_phase'] = MovementPhase.SETUP
            
        # Estimate muscle activation
        joint_angles = physics_results.get('joint_angles', {})
        forces = physics_results.get('force_distribution', {})
        results['muscle_activation'] = self.biomechanics_analyzer.estimate_muscle_activation(
            joint_angles, forces, exercise_type
        )
        
        # Movement quality analysis
        if len(self.movement_history) >= 5:
            results['movement_quality'] = self.biomechanics_analyzer.analyze_movement_quality(
                self.movement_history[-20:], exercise_type
            )
            
            # Neuromuscular coordination
            movement_data = []
            for i, landmarks in enumerate(self.movement_history[-20:]):
                movement_data.append({
                    'phase': results.get('phase_history', [MovementPhase.SETUP])[min(i, len(results.get('phase_history', [])) - 1)],
                    'muscle_activation': results['muscle_activation']
                })
            results['coordination_score'] = self.biomechanics_analyzer.assess_neuromuscular_coordination(
                movement_data
            )
        else:
            results['movement_quality'] = {
                'smoothness': 0.5,
                'stability': 0.5,
                'symmetry': 0.5,
                'tempo_consistency': 0.5,
                'range_of_motion': 0.5
            }
            results['coordination_score'] = 0.5
            
        return results
    
    def _apply_complex_systems_analysis(self, movement_history: List[Dict[str, np.ndarray]],
                                      exercise_type: str) -> Dict[str, Any]:
        """Apply complex systems analyzer."""
        results = {}
        
        # Calculate movement attractors
        results['attractors'] = self.complex_systems_analyzer.calculate_movement_attractors(
            movement_history
        )
        
        # Assess movement variability
        results['variability'] = self.complex_systems_analyzer.assess_movement_variability(
            movement_history
        )
        
        # Analyze system dynamics
        results['dynamics'] = self.complex_systems_analyzer.analyze_system_dynamics(
            movement_history
        )
        
        # Detect self-organization (if we have practice history)
        if len(self.analysis_results_history) >= 5:
            practice_data = [
                {
                    'performance_score': r.get('unified_scores', {}).get('overall', 0),
                    'movement_variability': r.get('complex_systems', {}).get('variability', {}).get('adaptive_variability', 0),
                    'movement_pattern': r.get('physics', {}).get('joint_angles', {})
                }
                for r in self.analysis_results_history[-20:]
            ]
            results['self_organization'] = self.complex_systems_analyzer.detect_self_organization(
                practice_data
            )
        else:
            results['self_organization'] = {
                'emergence_score': 0.0,
                'degrees_of_freedom_reduction': 0.0,
                'coordinative_structure_strength': 0.0,
                'learning_rate': 0.0,
                'pattern_stability': 0.0
            }
            
        return results
    
    def _apply_optimization(self, current_joint_angles: Dict[str, float],
                          user_profile: Dict[str, Any],
                          exercise_type: str) -> Dict[str, Any]:
        """Apply optimization engine."""
        results = {}
        
        # Define objectives based on user profile
        objectives = self.optimization_engine.define_objective_functions(user_profile)
        results['objectives'] = {
            name: {'weight': obj.weight, 'minimize': obj.minimize}
            for name, obj in objectives.items()
        }
        
        # Apply constraints
        user_measurements = user_profile.get('physicalMeasurements', {})
        constraints = self.optimization_engine.apply_constraints(user_measurements)
        results['constraints'] = [c.name for c in constraints.values()]
        
        # Solve for optimal form
        if current_joint_angles:
            optimal_form = self.optimization_engine.solve_form_optimization(
                current_joint_angles, constraints, exercise_type
            )
            
            results['optimal_form'] = {
                'joint_angles': optimal_form.joint_angles,
                'objective_values': optimal_form.objective_values,
                'constraint_satisfaction': optimal_form.constraint_satisfaction,
                'overall_score': optimal_form.overall_score
            }
            
            # Calculate improvement priorities
            improvements = self.optimization_engine.calculate_improvement_priority(
                current_joint_angles, optimal_form, user_profile
            )
            results['improvement_priorities'] = improvements[:3]  # Top 3
            
            # Generate personalized path
            path = self.optimization_engine.generate_personalized_path(
                current_joint_angles, optimal_form, time_steps=5
            )
            results['improvement_path'] = path
        else:
            results['optimal_form'] = None
            results['improvement_priorities'] = []
            results['improvement_path'] = []
            
        return results
    
    def _calculate_unified_scores(self, physics_results: Dict[str, Any],
                                biomechanics_results: Dict[str, Any],
                                complex_systems_results: Dict[str, Any],
                                optimization_results: Dict[str, Any]) -> Dict[str, float]:
        """Calculate unified theory scores."""
        scores = {
            'physics_efficiency': 0.0,
            'biological_optimality': 0.0,
            'system_stability': 0.0,
            'mathematical_optimization': 0.0,
            'overall': 0.0
        }
        
        # Physics efficiency score
        energy_eff = physics_results.get('energy_efficiency', 0.5)
        moment_arms = physics_results.get('moment_arms', {})
        
        # Lower moment arms = better efficiency
        avg_moment = np.mean(list(moment_arms.values())) if moment_arms else 0.1
        moment_score = 1.0 / (1.0 + avg_moment * 10)
        
        scores['physics_efficiency'] = (energy_eff + moment_score) / 2
        
        # Biological optimality score
        movement_quality = biomechanics_results.get('movement_quality', {})
        coord_score = biomechanics_results.get('coordination_score', 0.5)
        
        quality_score = np.mean(list(movement_quality.values())) if movement_quality else 0.5
        scores['biological_optimality'] = (quality_score + coord_score) / 2
        
        # System stability score
        if complex_systems_results:
            dynamics = complex_systems_results.get('dynamics', {})
            variability = complex_systems_results.get('variability', {})
            
            stability = dynamics.get('system_stability', 0.5)
            adaptive_var = variability.get('adaptive_variability', 0.5)
            
            scores['system_stability'] = (stability + adaptive_var) / 2
        else:
            scores['system_stability'] = 0.5
            
        # Mathematical optimization score
        if optimization_results.get('optimal_form'):
            scores['mathematical_optimization'] = optimization_results['optimal_form']['overall_score']
        else:
            scores['mathematical_optimization'] = 0.5
            
        # Overall score (weighted average)
        weights = {
            'physics_efficiency': 0.25,
            'biological_optimality': 0.30,
            'system_stability': 0.20,
            'mathematical_optimization': 0.25
        }
        
        scores['overall'] = sum(
            scores[key] * weight
            for key, weight in weights.items()
        )
        
        return scores
    
    def _generate_unified_feedback(self, unified_scores: Dict[str, float],
                                 physics_results: Dict[str, Any],
                                 biomechanics_results: Dict[str, Any],
                                 optimization_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate comprehensive feedback based on unified analysis."""
        feedback = []
        
        # Physics-based feedback
        if unified_scores['physics_efficiency'] < 0.7:
            joint_angles = physics_results.get('joint_angles', {})
            
            if 'spine' in joint_angles and joint_angles['spine'] > 30:
                feedback.append({
                    'type': 'physics',
                    'priority': 'high',
                    'message': 'Reduce forward lean to minimize spinal loading',
                    'metric': 'spine_angle',
                    'current_value': joint_angles['spine'],
                    'target_value': 20
                })
                
        # Biomechanics-based feedback
        if unified_scores['biological_optimality'] < 0.7:
            movement_quality = biomechanics_results.get('movement_quality', {})
            
            if movement_quality.get('smoothness', 1.0) < 0.6:
                feedback.append({
                    'type': 'biomechanics',
                    'priority': 'medium',
                    'message': 'Focus on smoother, more controlled movements',
                    'metric': 'smoothness',
                    'current_value': movement_quality.get('smoothness', 0),
                    'target_value': 0.8
                })
                
        # Optimization-based feedback
        improvements = optimization_results.get('improvement_priorities', [])
        for i, improvement in enumerate(improvements[:2]):  # Top 2 improvements
            feedback.append({
                'type': 'optimization',
                'priority': 'high' if i == 0 else 'medium',
                'message': f"Adjust {improvement['joint']} angle from {improvement['current']:.0f}° to {improvement['optimal']:.0f}°",
                'metric': f"{improvement['joint']}_angle",
                'current_value': improvement['current'],
                'target_value': improvement['optimal']
            })
            
        # Sort by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        feedback.sort(key=lambda x: priority_order.get(x['priority'], 3))
        
        return feedback
    
    def _landmarks_to_dict(self, landmarks: Dict[str, np.ndarray]) -> Dict[str, List[float]]:
        """Convert numpy landmarks to serializable format."""
        return {
            key: value.tolist() if isinstance(value, np.ndarray) else value
            for key, value in landmarks.items()
        }
    
    def _aggregate_sequence_results(self, sequence_results: List[Dict[str, Any]],
                                  exercise_type: str) -> Dict[str, Any]:
        """Aggregate results from a movement sequence."""
        if not sequence_results:
            return {'success': False, 'error': 'No results to aggregate'}
            
        # Extract successful results
        successful_results = [r for r in sequence_results if r.get('success', False)]
        
        if not successful_results:
            return {'success': False, 'error': 'No successful analyses'}
            
        # Aggregate scores
        all_scores = [r['unified_scores'] for r in successful_results]
        avg_scores = {}
        
        for key in all_scores[0]:
            values = [s[key] for s in all_scores]
            avg_scores[key] = np.mean(values)
            
        # Identify movement phases
        all_phases = []
        for r in successful_results:
            phase = r.get('biomechanics', {}).get('current_phase', MovementPhase.SETUP)
            all_phases.append(phase)
            
        # Find most common issues
        all_feedback = []
        for r in successful_results:
            all_feedback.extend(r.get('feedback', []))
            
        # Count feedback frequency
        feedback_counts = {}
        for fb in all_feedback:
            key = fb['message']
            feedback_counts[key] = feedback_counts.get(key, 0) + 1
            
        # Get top issues
        top_issues = sorted(
            feedback_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        return {
            'success': True,
            'exercise_type': exercise_type,
            'total_frames': len(sequence_results),
            'successful_frames': len(successful_results),
            'average_scores': avg_scores,
            'phases_detected': list(set(all_phases)),
            'top_issues': [
                {'message': issue, 'frequency': count}
                for issue, count in top_issues
            ],
            'overall_assessment': self._generate_overall_assessment(avg_scores)
        }
    
    def _generate_overall_assessment(self, avg_scores: Dict[str, float]) -> str:
        """Generate overall assessment based on average scores."""
        overall = avg_scores.get('overall', 0)
        
        if overall >= 0.8:
            return "Excellent form! Minor refinements can further optimize performance."
        elif overall >= 0.6:
            return "Good form with room for improvement. Focus on the suggested adjustments."
        elif overall >= 0.4:
            return "Form needs significant improvement. Practice the recommended corrections."
        else:
            return "Major form issues detected. Consider working with a trainer for safety."