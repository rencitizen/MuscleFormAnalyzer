"""Biomechanics Analyzer for Unified Theory-based Form Analysis.

This module implements biological and neuromuscular analysis principles,
including movement phase detection, muscle activation patterns, and coordination assessment.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class MovementPhase(Enum):
    """Movement phases for exercise analysis."""
    SETUP = "setup"
    DESCENT = "descent"  # Eccentric phase
    BOTTOM = "bottom"    # Transition point
    ASCENT = "ascent"    # Concentric phase
    TOP = "top"          # Completion
    

@dataclass
class MuscleGroup:
    """Represents a muscle group with activation characteristics."""
    name: str
    primary_joints: List[str]
    activation_threshold: float  # Joint angle for significant activation
    peak_angle: float           # Joint angle for peak activation
    

class BiomechanicsAnalyzer:
    """Implements biomechanical analysis based on neuromuscular principles."""
    
    # Muscle group definitions
    MUSCLE_GROUPS = {
        'quadriceps': MuscleGroup('quadriceps', ['knee', 'hip'], 120, 90),
        'hamstrings': MuscleGroup('hamstrings', ['knee', 'hip'], 45, 90),
        'glutes': MuscleGroup('glutes', ['hip'], 90, 45),
        'erector_spinae': MuscleGroup('erector_spinae', ['spine'], 30, 15),
        'biceps': MuscleGroup('biceps', ['elbow'], 120, 90),
        'triceps': MuscleGroup('triceps', ['elbow'], 90, 180),
        'deltoids': MuscleGroup('deltoids', ['shoulder'], 45, 90),
        'pectorals': MuscleGroup('pectorals', ['shoulder', 'elbow'], 90, 45),
        'latissimus': MuscleGroup('latissimus', ['shoulder'], 120, 180),
        'core': MuscleGroup('core', ['spine', 'hip'], 45, 30)
    }
    
    def __init__(self):
        """Initialize the biomechanics analyzer."""
        self.phase_history = []
        self.movement_velocity_threshold = 0.02  # m/s for phase detection
        
    def detect_movement_phases(self, landmarks_sequence: List[Dict[str, np.ndarray]],
                              exercise_type: str,
                              time_stamps: Optional[List[float]] = None) -> List[MovementPhase]:
        """Detect movement phases based on neuromuscular patterns.
        
        Args:
            landmarks_sequence: Sequence of landmark positions
            exercise_type: Type of exercise being performed
            time_stamps: Optional timestamps for velocity calculation
            
        Returns:
            List of detected movement phases
        """
        if len(landmarks_sequence) < 2:
            return [MovementPhase.SETUP]
            
        phases = []
        
        # Get the primary tracking point based on exercise
        tracking_points = {
            'squat': 'hip',
            'deadlift': 'hip',
            'bench_press': 'elbow',
            'bicep_curl': 'wrist'
        }
        
        tracking_point = tracking_points.get(exercise_type, 'hip')
        
        for i, landmarks in enumerate(landmarks_sequence):
            if tracking_point not in landmarks:
                phases.append(MovementPhase.SETUP)
                continue
                
            # Calculate vertical position and velocity
            current_pos = landmarks[tracking_point][1]  # Y-coordinate
            
            if i == 0:
                phases.append(MovementPhase.SETUP)
                continue
                
            prev_pos = landmarks_sequence[i-1].get(tracking_point, landmarks[tracking_point])[1]
            
            # Calculate velocity if timestamps available
            if time_stamps and i < len(time_stamps):
                dt = time_stamps[i] - time_stamps[i-1] if i > 0 else 0.033  # ~30fps
            else:
                dt = 0.033  # Assume 30fps
                
            velocity = (current_pos - prev_pos) / dt if dt > 0 else 0
            
            # Detect phase based on position and velocity
            phase = self._determine_phase(
                current_pos, prev_pos, velocity, 
                exercise_type, i, landmarks_sequence
            )
            phases.append(phase)
            
        # Smooth phase transitions
        phases = self._smooth_phase_transitions(phases)
        
        return phases
    
    def estimate_muscle_activation(self, joint_angles: Dict[str, float],
                                  forces: Dict[str, float],
                                  exercise_type: str) -> Dict[str, float]:
        """Estimate muscle activation patterns based on joint angles and forces.
        
        Args:
            joint_angles: Dictionary of joint angles in degrees
            forces: Dictionary of forces at joints
            exercise_type: Type of exercise
            
        Returns:
            Dictionary of muscle activation levels (0-1)
        """
        activations = {}
        
        # Exercise-specific muscle groups
        exercise_muscles = {
            'squat': ['quadriceps', 'hamstrings', 'glutes', 'core'],
            'deadlift': ['hamstrings', 'glutes', 'erector_spinae', 'latissimus'],
            'bench_press': ['pectorals', 'triceps', 'deltoids'],
            'bicep_curl': ['biceps', 'deltoids']
        }
        
        relevant_muscles = exercise_muscles.get(exercise_type, [])
        
        for muscle_name in relevant_muscles:
            if muscle_name not in self.MUSCLE_GROUPS:
                continue
                
            muscle = self.MUSCLE_GROUPS[muscle_name]
            activation = 0.0
            
            # Calculate activation based on joint angles
            for joint in muscle.primary_joints:
                if joint in joint_angles:
                    angle = joint_angles[joint]
                    
                    # Activation function: peaks at optimal angle
                    angle_diff = abs(angle - muscle.peak_angle)
                    activation_from_angle = np.exp(-angle_diff**2 / (2 * 30**2))
                    
                    # Increase activation if force is present
                    force_multiplier = 1.0
                    if joint in forces:
                        force_multiplier = 1.0 + min(forces[joint] / 1000, 1.0)
                        
                    activation = max(activation, activation_from_angle * force_multiplier)
                    
            activations[muscle_name] = min(activation, 1.0)
            
        return activations
    
    def assess_neuromuscular_coordination(self, movement_history: List[Dict]) -> float:
        """Assess neuromuscular coordination quality.
        
        Args:
            movement_history: History of movement data including phases and activations
            
        Returns:
            Coordination score (0-1, higher is better)
        """
        if len(movement_history) < 5:
            return 0.5  # Not enough data
            
        coordination_score = 1.0
        
        # Check for smooth phase transitions
        phases = [m.get('phase', MovementPhase.SETUP) for m in movement_history]
        phase_changes = sum(1 for i in range(1, len(phases)) if phases[i] != phases[i-1])
        expected_changes = 4  # Setup -> Descent -> Bottom -> Ascent -> Top
        
        if phase_changes > expected_changes * 1.5:
            coordination_score *= 0.8  # Too many phase changes indicates instability
            
        # Check for consistent muscle activation patterns
        if 'muscle_activation' in movement_history[0]:
            activations = [m['muscle_activation'] for m in movement_history]
            
            # Calculate activation variability
            for muscle in activations[0].keys():
                muscle_values = [a.get(muscle, 0) for a in activations]
                if len(muscle_values) > 1:
                    variability = np.std(muscle_values) / (np.mean(muscle_values) + 0.01)
                    
                    # High variability in same phase indicates poor coordination
                    if variability > 0.5:
                        coordination_score *= 0.9
                        
        # Check for compensatory patterns
        compensation_score = self._detect_compensation_patterns(movement_history)
        coordination_score *= compensation_score
        
        return max(min(coordination_score, 1.0), 0.0)
    
    def analyze_movement_quality(self, landmarks_sequence: List[Dict[str, np.ndarray]],
                               exercise_type: str) -> Dict[str, float]:
        """Comprehensive movement quality analysis.
        
        Args:
            landmarks_sequence: Sequence of landmark positions
            exercise_type: Type of exercise
            
        Returns:
            Dictionary of quality metrics
        """
        quality_metrics = {
            'smoothness': 0.0,
            'stability': 0.0,
            'symmetry': 0.0,
            'tempo_consistency': 0.0,
            'range_of_motion': 0.0
        }
        
        if len(landmarks_sequence) < 3:
            return quality_metrics
            
        # Calculate smoothness (jerk minimization)
        positions = []
        for landmarks in landmarks_sequence:
            if 'hip' in landmarks:
                positions.append(landmarks['hip'])
                
        if len(positions) > 2:
            jerks = []
            for i in range(2, len(positions)):
                acc1 = positions[i-1] - positions[i-2]
                acc2 = positions[i] - positions[i-1]
                jerk = np.linalg.norm(acc2 - acc1)
                jerks.append(jerk)
                
            quality_metrics['smoothness'] = 1.0 / (1.0 + np.mean(jerks) * 10)
            
        # Calculate stability (center of mass variation)
        if exercise_type in ['squat', 'deadlift']:
            com_positions = []
            for landmarks in landmarks_sequence:
                if 'hip' in landmarks and 'shoulder' in landmarks:
                    com = (landmarks['hip'] + landmarks['shoulder']) / 2
                    com_positions.append(com)
                    
            if len(com_positions) > 1:
                com_variance = np.var(com_positions, axis=0)
                quality_metrics['stability'] = 1.0 / (1.0 + np.sum(com_variance) * 100)
                
        # Calculate symmetry (left vs right side)
        symmetry_scores = []
        for landmarks in landmarks_sequence:
            left_right_pairs = [
                ('left_shoulder', 'right_shoulder'),
                ('left_hip', 'right_hip'),
                ('left_knee', 'right_knee')
            ]
            
            for left, right in left_right_pairs:
                if left in landmarks and right in landmarks:
                    diff = np.linalg.norm(landmarks[left] - landmarks[right])
                    symmetry_scores.append(1.0 / (1.0 + diff))
                    
        if symmetry_scores:
            quality_metrics['symmetry'] = np.mean(symmetry_scores)
            
        # Calculate tempo consistency
        phases = self.detect_movement_phases(landmarks_sequence, exercise_type)
        phase_durations = self._calculate_phase_durations(phases)
        
        if len(phase_durations) > 1:
            tempo_variance = np.var(phase_durations)
            quality_metrics['tempo_consistency'] = 1.0 / (1.0 + tempo_variance)
            
        # Calculate range of motion
        rom_score = self._calculate_range_of_motion_score(landmarks_sequence, exercise_type)
        quality_metrics['range_of_motion'] = rom_score
        
        return quality_metrics
    
    def _determine_phase(self, current_pos: float, prev_pos: float,
                        velocity: float, exercise_type: str,
                        index: int, sequence: List[Dict]) -> MovementPhase:
        """Determine current movement phase."""
        # Simple phase detection based on velocity and position
        if abs(velocity) < self.movement_velocity_threshold:
            # Near stationary
            if index < len(sequence) * 0.2:
                return MovementPhase.SETUP
            elif index > len(sequence) * 0.8:
                return MovementPhase.TOP
            else:
                return MovementPhase.BOTTOM
        elif velocity < -self.movement_velocity_threshold:
            return MovementPhase.DESCENT
        else:
            return MovementPhase.ASCENT
            
    def _smooth_phase_transitions(self, phases: List[MovementPhase]) -> List[MovementPhase]:
        """Smooth out noisy phase transitions."""
        if len(phases) < 5:
            return phases
            
        smoothed = phases.copy()
        
        # Simple majority voting for smoothing
        for i in range(2, len(phases) - 2):
            window = phases[i-2:i+3]
            most_common = max(set(window), key=window.count)
            if window.count(most_common) >= 3:
                smoothed[i] = most_common
                
        return smoothed
    
    def _detect_compensation_patterns(self, movement_history: List[Dict]) -> float:
        """Detect compensatory movement patterns."""
        compensation_score = 1.0
        
        # Check for excessive forward lean in squats
        if any('spine_angle' in m for m in movement_history):
            spine_angles = [m.get('spine_angle', 0) for m in movement_history]
            if max(spine_angles) > 45:  # Excessive forward lean
                compensation_score *= 0.8
                
        # Check for knee valgus (knees caving in)
        if any('knee_alignment' in m for m in movement_history):
            alignments = [m.get('knee_alignment', 0) for m in movement_history]
            if any(abs(a) > 10 for a in alignments):  # Misalignment threshold
                compensation_score *= 0.7
                
        return compensation_score
    
    def _calculate_phase_durations(self, phases: List[MovementPhase]) -> List[float]:
        """Calculate duration of each phase transition."""
        durations = []
        current_phase = phases[0]
        phase_start = 0
        
        for i, phase in enumerate(phases[1:], 1):
            if phase != current_phase:
                durations.append(i - phase_start)
                current_phase = phase
                phase_start = i
                
        return durations
    
    def _calculate_range_of_motion_score(self, landmarks_sequence: List[Dict],
                                       exercise_type: str) -> float:
        """Calculate range of motion score based on exercise standards."""
        rom_requirements = {
            'squat': {'knee': (60, 120)},  # Degrees
            'deadlift': {'hip': (20, 90)},
            'bench_press': {'elbow': (90, 180)},
            'bicep_curl': {'elbow': (30, 150)}
        }
        
        if exercise_type not in rom_requirements:
            return 0.5
            
        requirements = rom_requirements[exercise_type]
        scores = []
        
        for joint, (min_angle, max_angle) in requirements.items():
            joint_angles = []
            
            for landmarks in landmarks_sequence:
                # This would use actual angle calculation
                # Simplified for demonstration
                if joint in landmarks:
                    joint_angles.append(90)  # Placeholder
                    
            if joint_angles:
                achieved_range = max(joint_angles) - min(joint_angles)
                expected_range = max_angle - min_angle
                score = min(achieved_range / expected_range, 1.0)
                scores.append(score)
                
        return np.mean(scores) if scores else 0.5