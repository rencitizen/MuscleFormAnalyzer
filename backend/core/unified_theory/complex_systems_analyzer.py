"""Complex Systems Analyzer for Unified Theory-based Form Analysis.

This module implements complex systems theory, including attractor dynamics,
self-organization patterns, and movement variability analysis.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from scipy import signal, stats
from sklearn.decomposition import PCA
import logging

logger = logging.getLogger(__name__)


@dataclass
class AttractorState:
    """Represents an attractor state in movement dynamics."""
    center: np.ndarray
    strength: float
    basin_radius: float
    stability: float
    

class ComplexSystemsAnalyzer:
    """Implements complex systems analysis for movement patterns."""
    
    def __init__(self):
        """Initialize the complex systems analyzer."""
        self.movement_history = []
        self.attractor_threshold = 0.1
        self.variability_window = 10
        
    def calculate_movement_attractors(self, movement_data: List[Dict[str, np.ndarray]]) -> Dict[str, AttractorState]:
        """Identify attractor states in movement dynamics.
        
        Args:
            movement_data: List of movement states over time
            
        Returns:
            Dictionary of identified attractors
        """
        if len(movement_data) < 10:
            return {}
            
        # Convert movement data to phase space representation
        phase_space_points = self._construct_phase_space(movement_data)
        
        # Identify clusters in phase space (attractors)
        attractors = self._find_attractors(phase_space_points)
        
        # Characterize each attractor
        characterized_attractors = {}
        
        for i, attractor in enumerate(attractors):
            name = f"attractor_{i}"
            
            # Calculate attractor properties
            center = np.mean(attractor['points'], axis=0)
            strength = len(attractor['points']) / len(phase_space_points)
            
            # Basin of attraction radius
            distances = [np.linalg.norm(p - center) for p in attractor['points']]
            basin_radius = np.percentile(distances, 90)
            
            # Stability (inverse of variance)
            stability = 1.0 / (1.0 + np.var(distances))
            
            characterized_attractors[name] = AttractorState(
                center=center,
                strength=strength,
                basin_radius=basin_radius,
                stability=stability
            )
            
        # Identify optimal form attractor
        if characterized_attractors:
            optimal_attractor = self._identify_optimal_attractor(
                characterized_attractors, movement_data
            )
            characterized_attractors['optimal_form'] = optimal_attractor
            
        return characterized_attractors
    
    def assess_movement_variability(self, movement_sequence: List[Dict[str, np.ndarray]]) -> Dict[str, float]:
        """Analyze movement variability using nonlinear dynamics.
        
        Args:
            movement_sequence: Sequence of movement states
            
        Returns:
            Dictionary of variability metrics
        """
        variability_metrics = {
            'adaptive_variability': 0.0,
            'harmful_instability': 0.0,
            'complexity_index': 0.0,
            'predictability': 0.0,
            'flexibility': 0.0
        }
        
        if len(movement_sequence) < self.variability_window:
            return variability_metrics
            
        # Extract time series for key landmarks
        time_series = self._extract_time_series(movement_sequence)
        
        # Calculate detrended fluctuation analysis (DFA)
        for key, series in time_series.items():
            if len(series) > 20:
                # Adaptive variability (healthy variation)
                adaptive_var = self._calculate_adaptive_variability(series)
                variability_metrics['adaptive_variability'] = max(
                    variability_metrics['adaptive_variability'], 
                    adaptive_var
                )
                
                # Harmful instability (excessive variation)
                instability = self._calculate_instability(series)
                variability_metrics['harmful_instability'] = max(
                    variability_metrics['harmful_instability'],
                    instability
                )
                
        # Calculate movement complexity using approximate entropy
        complexity = self._calculate_approximate_entropy(time_series)
        variability_metrics['complexity_index'] = complexity
        
        # Calculate predictability using recurrence quantification
        predictability = self._calculate_predictability(time_series)
        variability_metrics['predictability'] = predictability
        
        # Calculate flexibility (ability to adapt)
        flexibility = self._calculate_movement_flexibility(movement_sequence)
        variability_metrics['flexibility'] = flexibility
        
        return variability_metrics
    
    def detect_self_organization(self, practice_data: List[Dict]) -> Dict[str, float]:
        """Detect self-organization patterns in practice data.
        
        Args:
            practice_data: Historical practice data with performance metrics
            
        Returns:
            Dictionary of self-organization indicators
        """
        organization_metrics = {
            'emergence_score': 0.0,
            'degrees_of_freedom_reduction': 0.0,
            'coordinative_structure_strength': 0.0,
            'learning_rate': 0.0,
            'pattern_stability': 0.0
        }
        
        if len(practice_data) < 5:
            return organization_metrics
            
        # Analyze emergence of coordinative structures
        emergence_score = self._analyze_emergence_patterns(practice_data)
        organization_metrics['emergence_score'] = emergence_score
        
        # Calculate reduction in degrees of freedom
        dof_reduction = self._calculate_dof_reduction(practice_data)
        organization_metrics['degrees_of_freedom_reduction'] = dof_reduction
        
        # Assess strength of coordinative structures
        coord_strength = self._assess_coordinative_structures(practice_data)
        organization_metrics['coordinative_structure_strength'] = coord_strength
        
        # Calculate learning rate from performance progression
        learning_rate = self._calculate_learning_rate(practice_data)
        organization_metrics['learning_rate'] = learning_rate
        
        # Assess pattern stability over time
        pattern_stability = self._assess_pattern_stability(practice_data)
        organization_metrics['pattern_stability'] = pattern_stability
        
        return organization_metrics
    
    def analyze_system_dynamics(self, movement_data: List[Dict[str, np.ndarray]],
                              external_perturbations: Optional[List[float]] = None) -> Dict[str, float]:
        """Analyze overall system dynamics and stability.
        
        Args:
            movement_data: Movement sequence data
            external_perturbations: Optional external disturbances
            
        Returns:
            Dictionary of system dynamics metrics
        """
        dynamics_metrics = {
            'system_stability': 0.0,
            'resilience': 0.0,
            'adaptability': 0.0,
            'critical_fluctuations': 0.0,
            'phase_transitions': 0
        }
        
        if len(movement_data) < 10:
            return dynamics_metrics
            
        # Calculate Lyapunov exponent for stability
        lyapunov = self._calculate_lyapunov_exponent(movement_data)
        dynamics_metrics['system_stability'] = 1.0 / (1.0 + abs(lyapunov))
        
        # Assess resilience to perturbations
        if external_perturbations:
            resilience = self._assess_resilience(movement_data, external_perturbations)
            dynamics_metrics['resilience'] = resilience
            
        # Calculate adaptability
        adaptability = self._calculate_adaptability(movement_data)
        dynamics_metrics['adaptability'] = adaptability
        
        # Detect critical fluctuations (precursors to phase transitions)
        critical_fluct = self._detect_critical_fluctuations(movement_data)
        dynamics_metrics['critical_fluctuations'] = critical_fluct
        
        # Count phase transitions
        transitions = self._count_phase_transitions(movement_data)
        dynamics_metrics['phase_transitions'] = transitions
        
        return dynamics_metrics
    
    def _construct_phase_space(self, movement_data: List[Dict[str, np.ndarray]]) -> np.ndarray:
        """Construct phase space representation of movement."""
        # Use PCA to reduce dimensionality
        all_positions = []
        
        for frame in movement_data:
            positions = []
            for landmark in frame.values():
                positions.extend(landmark[:2])  # Use x, y coordinates
            all_positions.append(positions)
            
        if not all_positions:
            return np.array([])
            
        # Ensure consistent dimensions
        min_len = min(len(p) for p in all_positions)
        all_positions = [p[:min_len] for p in all_positions]
        
        positions_array = np.array(all_positions)
        
        # Apply PCA to get principal components
        if positions_array.shape[0] > 3:
            pca = PCA(n_components=min(3, positions_array.shape[1]))
            phase_space = pca.fit_transform(positions_array)
        else:
            phase_space = positions_array
            
        return phase_space
    
    def _find_attractors(self, phase_space_points: np.ndarray) -> List[Dict]:
        """Find attractor regions in phase space."""
        if len(phase_space_points) < 10:
            return []
            
        # Simple density-based clustering
        attractors = []
        visited = set()
        
        for i, point in enumerate(phase_space_points):
            if i in visited:
                continue
                
            # Find nearby points
            distances = np.linalg.norm(phase_space_points - point, axis=1)
            nearby_indices = np.where(distances < self.attractor_threshold)[0]
            
            if len(nearby_indices) > len(phase_space_points) * 0.1:  # At least 10% of points
                attractor = {
                    'points': phase_space_points[nearby_indices],
                    'indices': nearby_indices.tolist()
                }
                attractors.append(attractor)
                visited.update(nearby_indices.tolist())
                
        return attractors
    
    def _identify_optimal_attractor(self, attractors: Dict[str, AttractorState],
                                  movement_data: List[Dict]) -> AttractorState:
        """Identify the optimal form attractor."""
        # Select attractor with highest stability and reasonable strength
        best_score = -1
        best_attractor = None
        
        for name, attractor in attractors.items():
            if name == 'optimal_form':
                continue
                
            # Score based on stability and strength
            score = attractor.stability * 0.7 + attractor.strength * 0.3
            
            if score > best_score:
                best_score = score
                best_attractor = attractor
                
        return best_attractor or AttractorState(
            center=np.zeros(3),
            strength=0.0,
            basin_radius=0.0,
            stability=0.0
        )
    
    def _extract_time_series(self, movement_sequence: List[Dict[str, np.ndarray]]) -> Dict[str, np.ndarray]:
        """Extract time series data from movement sequence."""
        time_series = {}
        
        # Extract key landmarks
        key_landmarks = ['hip', 'knee', 'shoulder', 'elbow']
        
        for landmark in key_landmarks:
            series = []
            for frame in movement_sequence:
                if landmark in frame:
                    # Use vertical position as primary signal
                    series.append(frame[landmark][1])
                    
            if series:
                time_series[landmark] = np.array(series)
                
        return time_series
    
    def _calculate_adaptive_variability(self, series: np.ndarray) -> float:
        """Calculate healthy adaptive variability."""
        if len(series) < 10:
            return 0.0
            
        # Detrend the series
        detrended = signal.detrend(series)
        
        # Calculate coefficient of variation
        cv = np.std(detrended) / (np.mean(np.abs(series)) + 1e-6)
        
        # Optimal variability is moderate (not too low, not too high)
        optimal_cv = 0.05
        score = np.exp(-((cv - optimal_cv) ** 2) / (2 * 0.02 ** 2))
        
        return score
    
    def _calculate_instability(self, series: np.ndarray) -> float:
        """Calculate harmful instability in movement."""
        if len(series) < 5:
            return 0.0
            
        # Calculate jerk (rate of change of acceleration)
        if len(series) > 3:
            velocity = np.diff(series)
            acceleration = np.diff(velocity)
            jerk = np.diff(acceleration)
            
            # High jerk indicates instability
            jerk_magnitude = np.mean(np.abs(jerk))
            instability = min(jerk_magnitude / 10.0, 1.0)
        else:
            instability = 0.0
            
        return instability
    
    def _calculate_approximate_entropy(self, time_series: Dict[str, np.ndarray]) -> float:
        """Calculate approximate entropy as complexity measure."""
        if not time_series:
            return 0.0
            
        entropies = []
        
        for series in time_series.values():
            if len(series) > 20:
                # Simplified approximate entropy calculation
                m = 2  # Pattern length
                r = 0.2 * np.std(series)  # Tolerance
                
                entropy = self._approx_entropy(series, m, r)
                entropies.append(entropy)
                
        return np.mean(entropies) if entropies else 0.0
    
    def _approx_entropy(self, series: np.ndarray, m: int, r: float) -> float:
        """Calculate approximate entropy."""
        N = len(series)
        patterns = []
        
        for i in range(N - m + 1):
            patterns.append(series[i:i + m])
            
        C = []
        for i in range(N - m + 1):
            count = 0
            for j in range(N - m + 1):
                if np.max(np.abs(patterns[i] - patterns[j])) <= r:
                    count += 1
            C.append(count / (N - m + 1))
            
        phi = np.mean(np.log(C)) if C else 0
        
        return phi
    
    def _calculate_predictability(self, time_series: Dict[str, np.ndarray]) -> float:
        """Calculate movement predictability."""
        if not time_series:
            return 0.0
            
        predictabilities = []
        
        for series in time_series.values():
            if len(series) > 10:
                # Autocorrelation as predictability measure
                autocorr = np.correlate(series, series, mode='full')
                autocorr = autocorr[len(autocorr)//2:]
                autocorr = autocorr / autocorr[0]
                
                # Average autocorrelation for lags 1-5
                avg_autocorr = np.mean(np.abs(autocorr[1:6]))
                predictabilities.append(avg_autocorr)
                
        return np.mean(predictabilities) if predictabilities else 0.5
    
    def _calculate_movement_flexibility(self, movement_sequence: List[Dict]) -> float:
        """Calculate movement flexibility."""
        if len(movement_sequence) < 10:
            return 0.5
            
        # Flexibility as variance in movement patterns
        phase_space = self._construct_phase_space(movement_sequence)
        
        if phase_space.shape[0] > 3:
            # Calculate principal component variances
            pca = PCA()
            pca.fit(phase_space)
            
            # Higher variance in multiple components = more flexibility
            explained_variance = pca.explained_variance_ratio_
            flexibility = 1.0 - explained_variance[0]  # Less dominated by first PC
        else:
            flexibility = 0.5
            
        return flexibility
    
    def _analyze_emergence_patterns(self, practice_data: List[Dict]) -> float:
        """Analyze emergence of new movement patterns."""
        if len(practice_data) < 5:
            return 0.0
            
        # Look for sudden improvements or new patterns
        scores = [d.get('performance_score', 0) for d in practice_data]
        
        if len(scores) > 5:
            # Detect jumps in performance
            diff = np.diff(scores)
            emergence_events = np.sum(diff > np.std(diff) * 2)
            
            emergence_score = min(emergence_events / len(scores), 1.0)
        else:
            emergence_score = 0.0
            
        return emergence_score
    
    def _calculate_dof_reduction(self, practice_data: List[Dict]) -> float:
        """Calculate reduction in degrees of freedom over practice."""
        if len(practice_data) < 5:
            return 0.0
            
        # Compare early vs late movement variability
        mid_point = len(practice_data) // 2
        
        early_data = practice_data[:mid_point]
        late_data = practice_data[mid_point:]
        
        early_var = np.mean([d.get('movement_variability', 1.0) for d in early_data])
        late_var = np.mean([d.get('movement_variability', 1.0) for d in late_data])
        
        # Reduction in variability indicates DOF reduction
        reduction = max(0, (early_var - late_var) / (early_var + 0.01))
        
        return min(reduction, 1.0)
    
    def _assess_coordinative_structures(self, practice_data: List[Dict]) -> float:
        """Assess strength of coordinative structures."""
        if len(practice_data) < 3:
            return 0.0
            
        # Look for consistent movement patterns
        pattern_consistency = []
        
        for i in range(1, len(practice_data)):
            if 'movement_pattern' in practice_data[i]:
                current = practice_data[i]['movement_pattern']
                previous = practice_data[i-1].get('movement_pattern', current)
                
                # Calculate similarity
                similarity = 1.0 - np.mean(np.abs(np.array(current) - np.array(previous)))
                pattern_consistency.append(similarity)
                
        return np.mean(pattern_consistency) if pattern_consistency else 0.0
    
    def _calculate_learning_rate(self, practice_data: List[Dict]) -> float:
        """Calculate learning rate from performance progression."""
        if len(practice_data) < 3:
            return 0.0
            
        scores = [d.get('performance_score', 0) for d in practice_data]
        
        if len(scores) > 2:
            # Fit exponential learning curve
            x = np.arange(len(scores))
            
            # Normalize scores
            scores_norm = (scores - np.min(scores)) / (np.max(scores) - np.min(scores) + 0.01)
            
            # Calculate rate of improvement
            improvements = np.diff(scores_norm)
            avg_improvement = np.mean(improvements[improvements > 0])
            
            learning_rate = min(avg_improvement * 10, 1.0)
        else:
            learning_rate = 0.0
            
        return learning_rate
    
    def _assess_pattern_stability(self, practice_data: List[Dict]) -> float:
        """Assess stability of movement patterns."""
        if len(practice_data) < 5:
            return 0.0
            
        # Calculate consistency in later practice sessions
        recent_data = practice_data[-5:]
        
        variabilities = [d.get('movement_variability', 1.0) for d in recent_data]
        
        # Low variability in recent sessions indicates pattern stability
        stability = 1.0 / (1.0 + np.mean(variabilities))
        
        return min(stability, 1.0)
    
    def _calculate_lyapunov_exponent(self, movement_data: List[Dict]) -> float:
        """Simplified Lyapunov exponent calculation."""
        phase_space = self._construct_phase_space(movement_data)
        
        if phase_space.shape[0] < 10:
            return 0.0
            
        # Simplified calculation: average divergence rate
        lyapunov = 0.0
        pairs = 0
        
        for i in range(len(phase_space) - 1):
            for j in range(i + 1, min(i + 5, len(phase_space))):
                initial_dist = np.linalg.norm(phase_space[i] - phase_space[j])
                
                if initial_dist < 0.1 and i + 1 < len(phase_space) and j + 1 < len(phase_space):
                    final_dist = np.linalg.norm(phase_space[i + 1] - phase_space[j + 1])
                    
                    if initial_dist > 0:
                        divergence = np.log(final_dist / initial_dist)
                        lyapunov += divergence
                        pairs += 1
                        
        return lyapunov / pairs if pairs > 0 else 0.0
    
    def _assess_resilience(self, movement_data: List[Dict], 
                         perturbations: List[float]) -> float:
        """Assess system resilience to perturbations."""
        # Simplified: check recovery after perturbations
        recovery_times = []
        
        for i, pert in enumerate(perturbations):
            if pert > 0 and i < len(movement_data) - 5:
                # Check how quickly system returns to baseline
                recovery_time = 0
                for j in range(i + 1, min(i + 10, len(movement_data))):
                    if j < len(perturbations) and perturbations[j] < pert * 0.1:
                        recovery_time = j - i
                        break
                        
                if recovery_time > 0:
                    recovery_times.append(recovery_time)
                    
        if recovery_times:
            avg_recovery = np.mean(recovery_times)
            resilience = 1.0 / (1.0 + avg_recovery / 5.0)
        else:
            resilience = 0.5
            
        return resilience
    
    def _calculate_adaptability(self, movement_data: List[Dict]) -> float:
        """Calculate system adaptability."""
        if len(movement_data) < 10:
            return 0.5
            
        # Adaptability as ability to explore movement space
        phase_space = self._construct_phase_space(movement_data)
        
        if phase_space.shape[0] > 5:
            # Calculate convex hull volume as exploration measure
            from scipy.spatial import ConvexHull
            
            try:
                hull = ConvexHull(phase_space)
                volume = hull.volume
                
                # Normalize by number of points
                adaptability = min(volume / (len(phase_space) * 0.1), 1.0)
            except:
                adaptability = 0.5
        else:
            adaptability = 0.5
            
        return adaptability
    
    def _detect_critical_fluctuations(self, movement_data: List[Dict]) -> float:
        """Detect critical fluctuations indicating phase transitions."""
        time_series = self._extract_time_series(movement_data)
        
        if not time_series:
            return 0.0
            
        fluctuation_scores = []
        
        for series in time_series.values():
            if len(series) > 20:
                # Calculate variance over sliding windows
                window_size = 5
                variances = []
                
                for i in range(len(series) - window_size):
                    window_var = np.var(series[i:i + window_size])
                    variances.append(window_var)
                    
                if variances:
                    # Increasing variance indicates critical fluctuations
                    trend = np.polyfit(range(len(variances)), variances, 1)[0]
                    fluctuation_scores.append(max(0, min(trend * 100, 1)))
                    
        return np.mean(fluctuation_scores) if fluctuation_scores else 0.0
    
    def _count_phase_transitions(self, movement_data: List[Dict]) -> int:
        """Count number of phase transitions in movement."""
        if len(movement_data) < 10:
            return 0
            
        # Detect sudden changes in movement patterns
        phase_space = self._construct_phase_space(movement_data)
        
        if phase_space.shape[0] > 5:
            # Calculate distances between consecutive states
            distances = []
            for i in range(1, len(phase_space)):
                dist = np.linalg.norm(phase_space[i] - phase_space[i-1])
                distances.append(dist)
                
            if distances:
                # Count peaks above threshold
                mean_dist = np.mean(distances)
                std_dist = np.std(distances)
                threshold = mean_dist + 2 * std_dist
                
                transitions = np.sum(np.array(distances) > threshold)
                return int(transitions)
                
        return 0