"""
Phase detection for exercise movements.
Detects the 5 phases: setup, descent, bottom, ascent, top.
"""

import numpy as np
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
import logging
from collections import deque

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PhaseInfo:
    """Information about a detected phase."""
    phase: str
    start_frame: int
    end_frame: int
    duration_seconds: float
    confidence: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'phase': self.phase,
            'start_frame': self.start_frame,
            'end_frame': self.end_frame,
            'duration_seconds': self.duration_seconds,
            'confidence': self.confidence
        }


class PhaseDetector:
    """Detects exercise phases using state machine approach."""
    
    PHASES = ['setup', 'descent', 'bottom', 'ascent', 'top']
    
    def __init__(self, exercise_type: str = 'squat', fps: float = 30.0):
        """
        Initialize phase detector.
        
        Args:
            exercise_type: Type of exercise (squat, bench_press, deadlift)
            fps: Frames per second for timing calculations
        """
        self.exercise_type = exercise_type
        self.fps = fps
        self.current_phase = 'setup'
        self.phase_history = []
        self.velocity_buffer = deque(maxlen=5)  # For smoothing
        self.position_buffer = deque(maxlen=5)
        self.phase_start_frame = 0
        
        # Phase transition parameters (adjustable per exercise)
        self.setup_velocity_threshold = 0.01  # Movement threshold to exit setup
        self.velocity_zero_threshold = 0.005  # Threshold for zero velocity
        self.min_phase_duration = 0.2  # Minimum seconds per phase
        
        # Exercise-specific parameters
        self._set_exercise_parameters()
    
    def _set_exercise_parameters(self):
        """Set exercise-specific detection parameters."""
        if self.exercise_type == 'squat':
            self.primary_joint = 'hip'  # Track hip height for squat
            self.descent_direction = 1  # Positive y is down
            self.min_descent_distance = 0.15  # Minimum hip drop
        elif self.exercise_type == 'bench_press':
            self.primary_joint = 'wrist'  # Track wrist position
            self.descent_direction = 1  # Positive y is down (bar descends)
            self.min_descent_distance = 0.1
        elif self.exercise_type == 'deadlift':
            self.primary_joint = 'hip'  # Track hip position
            self.descent_direction = 1  # Start from bottom
            self.min_descent_distance = 0.2
        else:
            # Default to squat-like movement
            self.primary_joint = 'hip'
            self.descent_direction = 1
            self.min_descent_distance = 0.15
    
    def detect_phases(self, landmark_sequence: List[np.ndarray]) -> List[PhaseInfo]:
        """
        Detect phases in a sequence of landmarks.
        
        Args:
            landmark_sequence: List of 33x3 landmark arrays
            
        Returns:
            List of detected phases with timing information
        """
        if len(landmark_sequence) < 2:
            return []
        
        # Reset state
        self.current_phase = 'setup'
        self.phase_history = []
        self.velocity_buffer.clear()
        self.position_buffer.clear()
        self.phase_start_frame = 0
        
        # Process each frame
        positions = []
        velocities = []
        
        # Extract positions
        for landmarks in landmark_sequence:
            pos = self._extract_key_position(landmarks)
            positions.append(pos)
        
        # Calculate velocities
        for i in range(1, len(positions)):
            vel = (positions[i] - positions[i-1]) * self.fps
            velocities.append(vel)
        velocities.insert(0, 0)  # First frame has zero velocity
        
        # Smooth velocities
        smoothed_velocities = self._smooth_signal(velocities)
        
        # State machine for phase detection
        detected_phases = []
        
        for frame_idx in range(len(landmark_sequence)):
            velocity = smoothed_velocities[frame_idx]
            position = positions[frame_idx]
            
            # Update buffers
            self.velocity_buffer.append(velocity)
            self.position_buffer.append(position)
            
            # Detect phase transitions
            new_phase = self._detect_phase_transition(
                frame_idx, velocity, position
            )
            
            if new_phase != self.current_phase:
                # Save completed phase
                if frame_idx > self.phase_start_frame:
                    phase_info = PhaseInfo(
                        phase=self.current_phase,
                        start_frame=self.phase_start_frame,
                        end_frame=frame_idx - 1,
                        duration_seconds=(frame_idx - self.phase_start_frame) / self.fps,
                        confidence=self._calculate_phase_confidence()
                    )
                    detected_phases.append(phase_info)
                
                # Transition to new phase
                self.current_phase = new_phase
                self.phase_start_frame = frame_idx
        
        # Add final phase
        if len(landmark_sequence) > self.phase_start_frame:
            phase_info = PhaseInfo(
                phase=self.current_phase,
                start_frame=self.phase_start_frame,
                end_frame=len(landmark_sequence) - 1,
                duration_seconds=(len(landmark_sequence) - self.phase_start_frame) / self.fps,
                confidence=self._calculate_phase_confidence()
            )
            detected_phases.append(phase_info)
        
        return detected_phases
    
    def _extract_key_position(self, landmarks: np.ndarray) -> float:
        """
        Extract key position based on exercise type.
        
        Args:
            landmarks: 33x3 landmark array
            
        Returns:
            Key position value (typically y-coordinate)
        """
        # MediaPipe landmark indices
        LEFT_HIP = 23
        RIGHT_HIP = 24
        LEFT_WRIST = 15
        RIGHT_WRIST = 16
        
        if self.primary_joint == 'hip':
            # Average of left and right hip y-positions
            return (landmarks[LEFT_HIP][1] + landmarks[RIGHT_HIP][1]) / 2
        elif self.primary_joint == 'wrist':
            # Average of left and right wrist y-positions
            return (landmarks[LEFT_WRIST][1] + landmarks[RIGHT_WRIST][1]) / 2
        else:
            # Default to hip
            return (landmarks[LEFT_HIP][1] + landmarks[RIGHT_HIP][1]) / 2
    
    def _smooth_signal(self, signal: List[float], window_size: int = 5) -> List[float]:
        """
        Apply moving average smoothing to signal.
        
        Args:
            signal: Input signal
            window_size: Size of smoothing window
            
        Returns:
            Smoothed signal
        """
        smoothed = []
        half_window = window_size // 2
        
        for i in range(len(signal)):
            start = max(0, i - half_window)
            end = min(len(signal), i + half_window + 1)
            smoothed.append(np.mean(signal[start:end]))
        
        return smoothed
    
    def _detect_phase_transition(
        self, 
        frame_idx: int, 
        velocity: float, 
        position: float
    ) -> str:
        """
        Detect phase transition based on current state and measurements.
        
        Args:
            frame_idx: Current frame index
            velocity: Current velocity
            position: Current position
            
        Returns:
            New phase name
        """
        # Check minimum phase duration
        current_duration = (frame_idx - self.phase_start_frame) / self.fps
        if current_duration < self.min_phase_duration:
            return self.current_phase
        
        # State machine logic
        if self.current_phase == 'setup':
            # Exit setup when significant movement starts
            if abs(velocity) > self.setup_velocity_threshold:
                if velocity * self.descent_direction > 0:
                    return 'descent'
                else:
                    return 'ascent'
        
        elif self.current_phase == 'descent':
            # Transition to bottom when velocity approaches zero
            if abs(velocity) < self.velocity_zero_threshold:
                # Check if we've descended enough
                if len(self.position_buffer) >= 2:
                    descent_distance = abs(position - self.position_buffer[0])
                    if descent_distance >= self.min_descent_distance:
                        return 'bottom'
        
        elif self.current_phase == 'bottom':
            # Transition to ascent when upward movement starts
            if velocity * self.descent_direction < -self.velocity_zero_threshold:
                return 'ascent'
        
        elif self.current_phase == 'ascent':
            # Transition to top when velocity approaches zero again
            if abs(velocity) < self.velocity_zero_threshold:
                # Check if we've returned near starting position
                if len(self.position_buffer) >= 2:
                    return_distance = abs(position - self.position_buffer[0])
                    if return_distance < self.min_descent_distance * 0.3:
                        return 'top'
        
        elif self.current_phase == 'top':
            # Can transition back to descent or remain at top
            if velocity * self.descent_direction > self.setup_velocity_threshold:
                return 'descent'
        
        return self.current_phase
    
    def _calculate_phase_confidence(self) -> float:
        """
        Calculate confidence score for current phase detection.
        
        Returns:
            Confidence score between 0 and 1
        """
        # Simple confidence based on velocity consistency
        if len(self.velocity_buffer) < 2:
            return 0.5
        
        velocities = list(self.velocity_buffer)
        velocity_std = np.std(velocities)
        
        # Lower variance = higher confidence
        confidence = 1.0 - min(velocity_std / 0.1, 1.0)
        return max(0.3, confidence)  # Minimum confidence of 0.3


def analyze_exercise_phases(
    landmark_sequence: List[np.ndarray],
    exercise_type: str,
    fps: float = 30.0
) -> Dict[str, Any]:
    """
    Analyze phases in an exercise sequence.
    
    Args:
        landmark_sequence: List of 33x3 landmark arrays
        exercise_type: Type of exercise
        fps: Frames per second
        
    Returns:
        Analysis results including phase breakdown
    """
    detector = PhaseDetector(exercise_type, fps)
    phases = detector.detect_phases(landmark_sequence)
    
    # Calculate phase statistics
    phase_counts = {phase: 0 for phase in PhaseDetector.PHASES}
    phase_durations = {phase: [] for phase in PhaseDetector.PHASES}
    
    for phase_info in phases:
        phase_counts[phase_info.phase] += 1
        phase_durations[phase_info.phase].append(phase_info.duration_seconds)
    
    # Count complete repetitions (descent -> bottom -> ascent -> top)
    rep_count = 0
    i = 0
    while i < len(phases) - 3:
        if (phases[i].phase == 'descent' and 
            phases[i+1].phase == 'bottom' and 
            phases[i+2].phase == 'ascent' and 
            phases[i+3].phase == 'top'):
            rep_count += 1
            i += 4
        else:
            i += 1
    
    # Calculate average phase durations
    avg_durations = {}
    for phase, durations in phase_durations.items():
        if durations:
            avg_durations[phase] = np.mean(durations)
        else:
            avg_durations[phase] = 0.0
    
    return {
        'phases': [p.to_dict() for p in phases],
        'phase_counts': phase_counts,
        'average_phase_durations': avg_durations,
        'repetition_count': rep_count,
        'total_duration': sum(p.duration_seconds for p in phases),
        'exercise_type': exercise_type
    }


if __name__ == "__main__":
    # Test with synthetic data
    from ml.data_collection.synthetic_data_generator import SyntheticPoseGenerator
    
    # Generate test data
    generator = SyntheticPoseGenerator(seed=42)
    dataset = generator.generate_dataset(
        exercise_type='squat',
        num_reps=3,
        fps=30.0
    )
    
    # Extract landmark sequence
    landmark_sequence = []
    for frame in dataset.frames:
        landmarks = np.zeros((33, 3))
        for lm in frame.landmarks:
            landmarks[lm.landmark_id] = [lm.x, lm.y, lm.z]
        landmark_sequence.append(landmarks)
    
    # Analyze phases
    results = analyze_exercise_phases(
        landmark_sequence,
        exercise_type='squat',
        fps=30.0
    )
    
    print(f"Detected {results['repetition_count']} repetitions")
    print(f"Phase counts: {results['phase_counts']}")
    print(f"Average phase durations: {results['average_phase_durations']}")