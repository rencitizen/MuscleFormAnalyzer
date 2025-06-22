"""Optimization Engine for Unified Theory-based Form Analysis.

This module implements mathematical optimization techniques for finding
optimal movement patterns based on individual constraints and objectives.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
from scipy.optimize import minimize, differential_evolution
from scipy.interpolate import interp1d
import logging

logger = logging.getLogger(__name__)


@dataclass
class OptimizationObjective:
    """Represents an optimization objective function."""
    name: str
    function: Callable
    weight: float
    minimize: bool = True
    

@dataclass
class Constraint:
    """Represents an optimization constraint."""
    name: str
    type: str  # 'ineq' or 'eq'
    function: Callable
    

@dataclass
class OptimalForm:
    """Represents an optimal form solution."""
    joint_angles: Dict[str, float]
    positions: Dict[str, np.ndarray]
    objective_values: Dict[str, float]
    constraint_satisfaction: Dict[str, bool]
    overall_score: float
    

class OptimizationEngine:
    """Implements mathematical optimization for form analysis."""
    
    # Standard joint angle ranges (degrees)
    JOINT_RANGES = {
        'ankle': (70, 130),
        'knee': (0, 160),
        'hip': (0, 120),
        'spine': (0, 45),
        'shoulder': (0, 180),
        'elbow': (0, 150),
        'wrist': (60, 120)
    }
    
    def __init__(self):
        """Initialize the optimization engine."""
        self.objectives = []
        self.constraints = []
        
    def define_objective_functions(self, user_profile: Dict) -> Dict[str, OptimizationObjective]:
        """Define objective functions based on user profile and goals.
        
        Args:
            user_profile: User's physical measurements and goals
            
        Returns:
            Dictionary of objective functions
        """
        objectives = {}
        
        # Energy efficiency objective
        objectives['energy_efficiency'] = OptimizationObjective(
            name='energy_efficiency',
            function=self._energy_efficiency_objective,
            weight=0.3,
            minimize=True
        )
        
        # Joint stress minimization
        objectives['joint_stress'] = OptimizationObjective(
            name='joint_stress',
            function=self._joint_stress_objective,
            weight=0.3,
            minimize=True
        )
        
        # Force production maximization
        objectives['force_production'] = OptimizationObjective(
            name='force_production',
            function=self._force_production_objective,
            weight=0.2,
            minimize=False  # Maximize
        )
        
        # Stability objective
        objectives['stability'] = OptimizationObjective(
            name='stability',
            function=self._stability_objective,
            weight=0.2,
            minimize=False  # Maximize
        )
        
        # Adjust weights based on user goals
        if 'goals' in user_profile:
            goals = user_profile['goals']
            
            if 'strength' in goals:
                objectives['force_production'].weight = 0.4
                objectives['energy_efficiency'].weight = 0.2
                
            elif 'endurance' in goals:
                objectives['energy_efficiency'].weight = 0.5
                objectives['joint_stress'].weight = 0.3
                
            elif 'hypertrophy' in goals:
                objectives['force_production'].weight = 0.3
                objectives['joint_stress'].weight = 0.3
                
        self.objectives = list(objectives.values())
        return objectives
    
    def apply_constraints(self, user_measurements: Dict) -> Dict[str, Constraint]:
        """Apply constraints based on user's physical limitations.
        
        Args:
            user_measurements: User's physical measurements and limitations
            
        Returns:
            Dictionary of constraints
        """
        constraints = {}
        
        # Joint range of motion constraints
        for joint, (min_angle, max_angle) in self.JOINT_RANGES.items():
            # Adjust based on user limitations
            if 'limitations' in user_measurements:
                limitations = user_measurements['limitations']
                
                if f'{joint}_limited' in limitations:
                    # Reduce range by 20% for limited joints
                    range_reduction = 0.2
                    min_angle = min_angle + (max_angle - min_angle) * range_reduction
                    max_angle = max_angle - (max_angle - min_angle) * range_reduction
                    
            constraints[f'{joint}_min'] = Constraint(
                name=f'{joint}_min',
                type='ineq',
                function=lambda x, j=joint, min_a=min_angle: x[self._get_joint_index(j)] - min_a
            )
            
            constraints[f'{joint}_max'] = Constraint(
                name=f'{joint}_max',
                type='ineq',
                function=lambda x, j=joint, max_a=max_angle: max_a - x[self._get_joint_index(j)]
            )
            
        # Balance constraint (center of mass within base of support)
        constraints['balance'] = Constraint(
            name='balance',
            type='ineq',
            function=self._balance_constraint
        )
        
        # Spine safety constraint
        constraints['spine_safety'] = Constraint(
            name='spine_safety',
            type='ineq',
            function=self._spine_safety_constraint
        )
        
        # User-specific constraints
        if 'height' in user_measurements:
            height_cm = user_measurements['height']
            
            # Anthropometric constraints based on height
            constraints['reach'] = Constraint(
                name='reach',
                type='ineq',
                function=lambda x: self._reach_constraint(x, height_cm)
            )
            
        self.constraints = list(constraints.values())
        return constraints
    
    def solve_form_optimization(self, current_form: Dict[str, float],
                              constraints: Dict[str, Constraint],
                              exercise_type: str) -> OptimalForm:
        """Solve for optimal form given current state and constraints.
        
        Args:
            current_form: Current joint angles and positions
            constraints: Applied constraints
            exercise_type: Type of exercise
            
        Returns:
            Optimal form solution
        """
        # Convert current form to optimization vector
        x0 = self._form_to_vector(current_form)
        
        # Set bounds based on joint ranges
        bounds = []
        for joint in self.JOINT_RANGES:
            if joint in current_form:
                bounds.append(self.JOINT_RANGES[joint])
                
        # Define combined objective function
        def combined_objective(x):
            total = 0
            for obj in self.objectives:
                value = obj.function(x, exercise_type)
                if obj.minimize:
                    total += obj.weight * value
                else:
                    total -= obj.weight * value  # Negative for maximization
            return total
            
        # Convert constraints to scipy format
        scipy_constraints = []
        for constraint in self.constraints:
            scipy_constraints.append({
                'type': constraint.type,
                'fun': constraint.function
            })
            
        # Solve optimization problem
        try:
            # Try local optimization first
            result = minimize(
                combined_objective,
                x0,
                method='SLSQP',
                bounds=bounds,
                constraints=scipy_constraints,
                options={'maxiter': 100}
            )
            
            # If local optimization fails, try global optimization
            if not result.success:
                result = differential_evolution(
                    combined_objective,
                    bounds,
                    constraints=scipy_constraints,
                    maxiter=50,
                    popsize=15
                )
                
        except Exception as e:
            logger.error(f"Optimization failed: {e}")
            # Return current form if optimization fails
            return self._create_optimal_form(x0, current_form, exercise_type)
            
        # Convert result back to form representation
        optimal_vector = result.x
        optimal_form = self._vector_to_form(optimal_vector, current_form)
        
        # Calculate objective values for the optimal solution
        objective_values = {}
        for obj in self.objectives:
            value = obj.function(optimal_vector, exercise_type)
            objective_values[obj.name] = value
            
        # Check constraint satisfaction
        constraint_satisfaction = {}
        for constraint in self.constraints:
            satisfied = constraint.function(optimal_vector) >= 0
            constraint_satisfaction[constraint.name] = satisfied
            
        # Calculate overall score
        overall_score = 1.0 - result.fun  # Convert minimization result to score
        
        return OptimalForm(
            joint_angles=optimal_form,
            positions=self._calculate_positions_from_angles(optimal_form),
            objective_values=objective_values,
            constraint_satisfaction=constraint_satisfaction,
            overall_score=max(0, min(1, overall_score))
        )
    
    def calculate_improvement_priority(self, current_form: Dict[str, float],
                                     optimal_form: OptimalForm,
                                     user_profile: Dict) -> List[Dict[str, float]]:
        """Calculate priority of improvements needed.
        
        Args:
            current_form: Current joint angles
            optimal_form: Optimal form solution
            user_profile: User profile and goals
            
        Returns:
            List of improvements sorted by priority
        """
        improvements = []
        
        # Calculate differences between current and optimal
        for joint, optimal_angle in optimal_form.joint_angles.items():
            if joint in current_form:
                current_angle = current_form[joint]
                difference = abs(optimal_angle - current_angle)
                
                # Calculate impact on objectives
                impact = self._calculate_improvement_impact(
                    joint, difference, user_profile
                )
                
                improvements.append({
                    'joint': joint,
                    'current': current_angle,
                    'optimal': optimal_angle,
                    'difference': difference,
                    'impact': impact,
                    'priority': impact * difference
                })
                
        # Sort by priority
        improvements.sort(key=lambda x: x['priority'], reverse=True)
        
        return improvements
    
    def generate_personalized_path(self, current_form: Dict[str, float],
                                 optimal_form: OptimalForm,
                                 time_steps: int = 10) -> List[Dict[str, float]]:
        """Generate a personalized path from current to optimal form.
        
        Args:
            current_form: Current joint angles
            optimal_form: Target optimal form
            time_steps: Number of intermediate steps
            
        Returns:
            List of intermediate forms
        """
        path = []
        
        # Create interpolation functions for each joint
        interpolators = {}
        for joint in current_form:
            if joint in optimal_form.joint_angles:
                current = current_form[joint]
                optimal = optimal_form.joint_angles[joint]
                
                # Use smooth interpolation
                t = np.linspace(0, 1, time_steps)
                # S-curve for natural progression
                s_curve = 0.5 * (1 - np.cos(np.pi * t))
                
                values = current + (optimal - current) * s_curve
                interpolators[joint] = values
                
        # Generate intermediate forms
        for i in range(time_steps):
            intermediate_form = {}
            for joint, values in interpolators.items():
                intermediate_form[joint] = values[i]
            path.append(intermediate_form)
            
        return path
    
    def _energy_efficiency_objective(self, x: np.ndarray, exercise_type: str) -> float:
        """Calculate energy efficiency objective."""
        # Simplified: penalize excessive joint angles and velocities
        energy = 0
        
        # Penalize deviation from neutral positions
        neutral_angles = {'knee': 90, 'hip': 90, 'elbow': 90, 'spine': 15}
        
        for i, (joint, neutral) in enumerate(neutral_angles.items()):
            if i < len(x):
                deviation = abs(x[i] - neutral)
                energy += deviation ** 2 / 1000
                
        return energy
    
    def _joint_stress_objective(self, x: np.ndarray, exercise_type: str) -> float:
        """Calculate joint stress objective."""
        stress = 0
        
        # Penalize extreme joint angles
        for i, angle in enumerate(x):
            if i < len(self.JOINT_RANGES):
                joint_name = list(self.JOINT_RANGES.keys())[i]
                min_angle, max_angle = self.JOINT_RANGES[joint_name]
                
                # Stress increases near limits
                range_size = max_angle - min_angle
                normalized = (angle - min_angle) / range_size
                
                # Quadratic penalty near limits
                if normalized < 0.2:
                    stress += (0.2 - normalized) ** 2
                elif normalized > 0.8:
                    stress += (normalized - 0.8) ** 2
                    
        return stress
    
    def _force_production_objective(self, x: np.ndarray, exercise_type: str) -> float:
        """Calculate force production objective."""
        force = 0
        
        # Exercise-specific optimal angles for force production
        optimal_angles = {
            'squat': {'knee': 90, 'hip': 90},
            'deadlift': {'hip': 45, 'knee': 135},
            'bench_press': {'elbow': 90, 'shoulder': 45},
            'bicep_curl': {'elbow': 90}
        }
        
        if exercise_type in optimal_angles:
            target_angles = optimal_angles[exercise_type]
            
            for i, (joint, optimal) in enumerate(target_angles.items()):
                if i < len(x):
                    # Force production peaks at optimal angle
                    angle_diff = abs(x[i] - optimal)
                    force += np.exp(-angle_diff ** 2 / (2 * 20 ** 2))
                    
        return force
    
    def _stability_objective(self, x: np.ndarray, exercise_type: str) -> float:
        """Calculate stability objective."""
        # Simplified: favor positions with lower center of mass
        # and wider base of support
        stability = 1.0
        
        # Penalize excessive forward lean (spine angle)
        spine_idx = self._get_joint_index('spine')
        if spine_idx < len(x):
            spine_angle = x[spine_idx]
            if spine_angle > 30:
                stability *= 0.8
                
        # Favor moderate knee bend for stability
        knee_idx = self._get_joint_index('knee')
        if knee_idx < len(x):
            knee_angle = x[knee_idx]
            optimal_knee = 110  # Slightly bent for stability
            stability *= np.exp(-(knee_angle - optimal_knee) ** 2 / (2 * 30 ** 2))
            
        return stability
    
    def _balance_constraint(self, x: np.ndarray) -> float:
        """Ensure center of mass is within base of support."""
        # Simplified: check that certain angles maintain balance
        spine_idx = self._get_joint_index('spine')
        
        if spine_idx < len(x):
            spine_angle = x[spine_idx]
            # Constraint: spine angle should not exceed safe limit
            return 60 - spine_angle  # Positive if satisfied
            
        return 1.0  # Satisfied by default
    
    def _spine_safety_constraint(self, x: np.ndarray) -> float:
        """Ensure spine is in safe position."""
        spine_idx = self._get_joint_index('spine')
        hip_idx = self._get_joint_index('hip')
        
        if spine_idx < len(x) and hip_idx < len(x):
            spine_angle = x[spine_idx]
            hip_angle = x[hip_idx]
            
            # Spine should not be excessively flexed when hip is hinged
            if hip_angle < 90:  # Hip hinged
                max_spine = 30  # Limit spine flexion
            else:
                max_spine = 45
                
            return max_spine - spine_angle
            
        return 1.0
    
    def _reach_constraint(self, x: np.ndarray, height_cm: float) -> float:
        """Ensure positions are within anthropometric reach."""
        # Simplified: check that extreme positions are reachable
        max_reach = height_cm * 0.4  # 40% of height
        
        # This would be more complex with actual position calculations
        return max_reach - 50  # Placeholder
    
    def _get_joint_index(self, joint_name: str) -> int:
        """Get index of joint in optimization vector."""
        joint_list = list(self.JOINT_RANGES.keys())
        if joint_name in joint_list:
            return joint_list.index(joint_name)
        return -1
    
    def _form_to_vector(self, form: Dict[str, float]) -> np.ndarray:
        """Convert form dictionary to optimization vector."""
        vector = []
        for joint in self.JOINT_RANGES:
            if joint in form:
                vector.append(form[joint])
            else:
                # Use middle of range as default
                min_a, max_a = self.JOINT_RANGES[joint]
                vector.append((min_a + max_a) / 2)
        return np.array(vector)
    
    def _vector_to_form(self, vector: np.ndarray, 
                       reference_form: Dict[str, float]) -> Dict[str, float]:
        """Convert optimization vector to form dictionary."""
        form = {}
        joint_list = list(self.JOINT_RANGES.keys())
        
        for i, angle in enumerate(vector):
            if i < len(joint_list):
                joint = joint_list[i]
                if joint in reference_form:  # Only include joints from reference
                    form[joint] = angle
                    
        return form
    
    def _calculate_positions_from_angles(self, joint_angles: Dict[str, float]) -> Dict[str, np.ndarray]:
        """Calculate joint positions from angles (simplified)."""
        positions = {}
        
        # This would involve forward kinematics in a real implementation
        # For now, return placeholder positions
        for joint in joint_angles:
            positions[joint] = np.array([0, 0, 0])
            
        return positions
    
    def _create_optimal_form(self, x: np.ndarray, 
                           current_form: Dict[str, float],
                           exercise_type: str) -> OptimalForm:
        """Create optimal form result from vector."""
        form = self._vector_to_form(x, current_form)
        
        return OptimalForm(
            joint_angles=form,
            positions=self._calculate_positions_from_angles(form),
            objective_values={},
            constraint_satisfaction={},
            overall_score=0.5
        )
    
    def _calculate_improvement_impact(self, joint: str, difference: float,
                                    user_profile: Dict) -> float:
        """Calculate impact of improving a specific joint angle."""
        # Base impact on joint importance for user goals
        impact_weights = {
            'knee': 0.9,
            'hip': 0.9,
            'spine': 0.8,
            'shoulder': 0.7,
            'elbow': 0.6,
            'ankle': 0.5,
            'wrist': 0.4
        }
        
        base_impact = impact_weights.get(joint, 0.5)
        
        # Adjust based on user goals
        if 'goals' in user_profile:
            goals = user_profile['goals']
            
            if 'strength' in goals and joint in ['hip', 'knee']:
                base_impact *= 1.2
            elif 'endurance' in goals and joint == 'spine':
                base_impact *= 1.3
                
        return min(base_impact, 1.0)