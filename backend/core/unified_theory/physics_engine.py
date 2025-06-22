"""Physics Engine for Unified Theory-based Form Analysis.

This module implements physical laws and principles for biomechanical analysis,
including Newton's laws, lever mechanics, and energy optimization.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class BodySegment:
    """Represents a body segment with physical properties."""
    name: str
    mass_ratio: float  # Percentage of total body mass
    com_ratio: float   # Center of mass position from proximal joint (0-1)


class PhysicsEngine:
    """Implements physics-based calculations for movement analysis."""
    
    # Body segment parameters from biomechanical literature
    BODY_SEGMENTS = {
        'head': BodySegment('head', 0.08, 0.5),
        'trunk': BodySegment('trunk', 0.497, 0.5),
        'upper_arm': BodySegment('upper_arm', 0.028, 0.436),
        'forearm': BodySegment('forearm', 0.016, 0.430),
        'hand': BodySegment('hand', 0.006, 0.506),
        'thigh': BodySegment('thigh', 0.100, 0.433),
        'shank': BodySegment('shank', 0.0465, 0.433),
        'foot': BodySegment('foot', 0.0145, 0.5)
    }
    
    def __init__(self):
        """Initialize the physics engine."""
        self.gravity = 9.81  # m/s^2
        
    def calculate_joint_angles(self, landmarks: Dict[str, np.ndarray]) -> Dict[str, float]:
        """Calculate joint angles using Newton's laws and vector mechanics.
        
        Args:
            landmarks: Dictionary of landmark positions {name: [x, y, z]}
            
        Returns:
            Dictionary of joint angles in degrees
        """
        angles = {}
        
        # Calculate elbow angle (for bicep curls)
        if all(key in landmarks for key in ['shoulder', 'elbow', 'wrist']):
            angles['elbow'] = self._calculate_angle_3points(
                landmarks['shoulder'], 
                landmarks['elbow'], 
                landmarks['wrist']
            )
            
        # Calculate knee angle (for squats)
        if all(key in landmarks for key in ['hip', 'knee', 'ankle']):
            angles['knee'] = self._calculate_angle_3points(
                landmarks['hip'],
                landmarks['knee'],
                landmarks['ankle']
            )
            
        # Calculate hip angle (for deadlifts)
        if all(key in landmarks for key in ['shoulder', 'hip', 'knee']):
            angles['hip'] = self._calculate_angle_3points(
                landmarks['shoulder'],
                landmarks['hip'],
                landmarks['knee']
            )
            
        # Calculate spine angle (for posture assessment)
        if all(key in landmarks for key in ['shoulder', 'hip', 'vertical_ref']):
            spine_vector = landmarks['shoulder'] - landmarks['hip']
            vertical_vector = landmarks['vertical_ref']
            angles['spine'] = self._calculate_angle_vectors(spine_vector, vertical_vector)
            
        return angles
    
    def calculate_moment_arms(self, landmarks: Dict[str, np.ndarray], 
                             height_cm: float,
                             load_position: Optional[np.ndarray] = None) -> Dict[str, float]:
        """Calculate moment arms based on lever principles.
        
        Args:
            landmarks: Dictionary of landmark positions
            height_cm: User height in centimeters for scaling
            load_position: Position of external load (e.g., barbell)
            
        Returns:
            Dictionary of moment arms in meters
        """
        moment_arms = {}
        scale_factor = height_cm / 100.0  # Convert to meters
        
        # Calculate moment arm for deadlift (bar to lower back)
        if load_position is not None and 'lower_back' in landmarks:
            # Horizontal distance from load to spine
            moment_arms['deadlift_spine'] = abs(
                load_position[0] - landmarks['lower_back'][0]
            ) * scale_factor
            
        # Calculate moment arm for squat (load to knee joint)
        if load_position is not None and 'knee' in landmarks:
            moment_arms['squat_knee'] = abs(
                load_position[0] - landmarks['knee'][0]
            ) * scale_factor
            
        # Calculate moment arm for bench press (bar to shoulder)
        if load_position is not None and 'shoulder' in landmarks:
            moment_arms['bench_shoulder'] = np.linalg.norm(
                load_position[:2] - landmarks['shoulder'][:2]
            ) * scale_factor
            
        return moment_arms
    
    def calculate_center_of_mass(self, landmarks: Dict[str, np.ndarray],
                                body_weight_kg: float = 70) -> Tuple[float, float, float]:
        """Calculate whole body center of mass using segmental method.
        
        Args:
            landmarks: Dictionary of landmark positions
            body_weight_kg: Total body weight in kg
            
        Returns:
            Center of mass position (x, y, z)
        """
        total_mass = 0
        weighted_position = np.zeros(3)
        
        # Simplified COM calculation using major segments
        segments = {
            'head': ('head', 0.08),
            'trunk': ('spine_mid', 0.497),
            'left_arm': ('left_elbow', 0.05),
            'right_arm': ('right_elbow', 0.05),
            'left_leg': ('left_knee', 0.161),
            'right_leg': ('right_knee', 0.161)
        }
        
        for segment_name, (landmark_key, mass_ratio) in segments.items():
            if landmark_key in landmarks:
                segment_mass = body_weight_kg * mass_ratio
                total_mass += segment_mass
                weighted_position += landmarks[landmark_key] * segment_mass
                
        if total_mass > 0:
            com = weighted_position / total_mass
            return tuple(com)
        else:
            # Fallback to geometric center
            positions = np.array(list(landmarks.values()))
            return tuple(np.mean(positions, axis=0))
    
    def assess_energy_efficiency(self, movement_data: List[Dict[str, np.ndarray]],
                                time_stamps: List[float]) -> float:
        """Assess energy efficiency based on minimum action principle.
        
        Args:
            movement_data: List of landmark positions over time
            time_stamps: Corresponding time stamps
            
        Returns:
            Energy efficiency score (0-1, higher is better)
        """
        if len(movement_data) < 2:
            return 0.0
            
        total_displacement = 0.0
        total_acceleration = 0.0
        
        for i in range(1, len(movement_data)):
            dt = time_stamps[i] - time_stamps[i-1]
            if dt <= 0:
                continue
                
            # Calculate COM for each frame
            com_prev = self.calculate_center_of_mass(movement_data[i-1])
            com_curr = self.calculate_center_of_mass(movement_data[i])
            
            # Calculate displacement and velocity
            displacement = np.linalg.norm(np.array(com_curr) - np.array(com_prev))
            velocity = displacement / dt
            
            total_displacement += displacement
            
            # Estimate acceleration (simplified)
            if i > 1:
                com_prev2 = self.calculate_center_of_mass(movement_data[i-2])
                velocity_prev = np.linalg.norm(
                    np.array(com_prev) - np.array(com_prev2)
                ) / (time_stamps[i-1] - time_stamps[i-2])
                acceleration = abs(velocity - velocity_prev) / dt
                total_acceleration += acceleration
                
        # Energy efficiency inversely related to unnecessary acceleration
        # Normalized score where less acceleration = higher efficiency
        if total_acceleration > 0:
            efficiency = 1.0 / (1.0 + total_acceleration / len(movement_data))
        else:
            efficiency = 1.0
            
        return min(max(efficiency, 0.0), 1.0)
    
    def calculate_force_distribution(self, landmarks: Dict[str, np.ndarray],
                                   external_load_kg: float = 0) -> Dict[str, float]:
        """Calculate force distribution across joints.
        
        Args:
            landmarks: Dictionary of landmark positions
            external_load_kg: External load in kilograms
            
        Returns:
            Dictionary of forces at each joint in Newtons
        """
        forces = {}
        total_force = (70 + external_load_kg) * self.gravity  # Assume 70kg body weight
        
        # Simplified force distribution based on posture
        if 'spine_angle' in self.calculate_joint_angles(landmarks):
            spine_angle = self.calculate_joint_angles(landmarks)['spine_angle']
            
            # More forward lean = more force on lower back
            lumbar_force_ratio = 0.3 + 0.4 * (spine_angle / 90.0)
            forces['lumbar_spine'] = total_force * lumbar_force_ratio
            
        # Knee forces in squat position
        if 'knee' in landmarks and 'hip' in landmarks:
            knee_angle = self.calculate_joint_angles(landmarks).get('knee', 90)
            # Peak forces around 90 degrees
            knee_force_ratio = 0.5 + 0.3 * np.sin(np.radians(knee_angle))
            forces['knee'] = total_force * knee_force_ratio
            
        return forces
    
    def _calculate_angle_3points(self, p1: np.ndarray, p2: np.ndarray, 
                                p3: np.ndarray) -> float:
        """Calculate angle between three points with p2 as vertex."""
        v1 = p1 - p2
        v2 = p3 - p2
        
        # Handle 2D or 3D vectors
        v1 = v1[:2] if len(v1) > 2 else v1
        v2 = v2[:2] if len(v2) > 2 else v2
        
        cosine = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
        angle = np.arccos(np.clip(cosine, -1.0, 1.0))
        
        return np.degrees(angle)
    
    def _calculate_angle_vectors(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """Calculate angle between two vectors."""
        cosine = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
        angle = np.arccos(np.clip(cosine, -1.0, 1.0))
        return np.degrees(angle)