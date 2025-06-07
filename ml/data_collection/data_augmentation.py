"""
Data augmentation module for exercise pose data.
Handles edge cases and expands training dataset.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional, Any
import random
import logging
from copy import deepcopy
import json
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PoseDataAugmenter:
    """Augments pose data to handle edge cases and expand training data."""
    
    def __init__(self, seed: int = 42):
        """
        Initialize the augmenter.
        
        Args:
            seed: Random seed for reproducibility
        """
        np.random.seed(seed)
        random.seed(seed)
        
        # Augmentation parameters
        self.augmentation_params = {
            "spatial": {
                "scale_range": (0.8, 1.2),  # Body size variation
                "translate_range": (-0.1, 0.1),  # Position variation
                "rotate_range": (-15, 15),  # Rotation in degrees
                "horizontal_flip": True,  # Mirror image
                "perspective_warp": (0.9, 1.1)  # Camera angle variation
            },
            "temporal": {
                "speed_variation": (0.7, 1.3),  # Exercise speed
                "frame_drop_rate": 0.1,  # Simulate lower FPS
                "interpolation": True  # Add intermediate frames
            },
            "noise": {
                "gaussian_noise": 0.02,  # Position noise
                "visibility_noise": 0.1,  # Detection confidence noise
                "occlusion_probability": 0.05  # Random landmark occlusion
            },
            "body_types": {
                # Simulate different body proportions
                "proportions": [
                    {"name": "tall_thin", "height_scale": 1.15, "width_scale": 0.9},
                    {"name": "short_stocky", "height_scale": 0.85, "width_scale": 1.1},
                    {"name": "athletic", "height_scale": 1.0, "width_scale": 1.05},
                    {"name": "average", "height_scale": 1.0, "width_scale": 1.0},
                    {"name": "large", "height_scale": 1.1, "width_scale": 1.2}
                ]
            }
        }
        
        # MediaPipe landmark connections for maintaining structure
        self.pose_connections = [
            (0, 1), (1, 2), (2, 3), (3, 7), (0, 4), (4, 5),
            (5, 6), (6, 8), (9, 10), (11, 12), (11, 13),
            (13, 15), (15, 17), (15, 19), (15, 21), (17, 19),
            (12, 14), (14, 16), (16, 18), (16, 20), (16, 22),
            (18, 20), (11, 23), (12, 24), (23, 24), (23, 25),
            (24, 26), (25, 27), (26, 28), (27, 29), (28, 30),
            (29, 31), (30, 32), (27, 31), (28, 32)
        ]
    
    def augment_single_frame(
        self,
        landmarks: List[Dict],
        augmentation_type: str = "all"
    ) -> List[Dict]:
        """
        Augment a single frame of landmarks.
        
        Args:
            landmarks: List of landmark dictionaries
            augmentation_type: Type of augmentation to apply
            
        Returns:
            Augmented landmarks
        """
        augmented = deepcopy(landmarks)
        
        if augmentation_type in ["all", "spatial"]:
            augmented = self._apply_spatial_augmentation(augmented)
        
        if augmentation_type in ["all", "noise"]:
            augmented = self._apply_noise_augmentation(augmented)
        
        return augmented
    
    def augment_sequence(
        self,
        landmark_sequence: List[List[Dict]],
        augmentation_types: List[str] = ["spatial", "temporal", "noise"],
        num_augmentations: int = 1
    ) -> List[List[List[Dict]]]:
        """
        Augment a sequence of landmarks with multiple techniques.
        
        Args:
            landmark_sequence: Original sequence of landmarks
            augmentation_types: Types of augmentation to apply
            num_augmentations: Number of augmented versions to create
            
        Returns:
            List of augmented sequences
        """
        augmented_sequences = []
        
        for i in range(num_augmentations):
            # Start with a copy
            augmented = deepcopy(landmark_sequence)
            
            # Apply temporal augmentations first (affects sequence structure)
            if "temporal" in augmentation_types:
                augmented = self._apply_temporal_augmentation(augmented)
            
            # Apply spatial augmentations (per frame)
            if "spatial" in augmentation_types:
                # Choose consistent augmentation parameters for the sequence
                scale = np.random.uniform(*self.augmentation_params["spatial"]["scale_range"])
                translate = [
                    np.random.uniform(*self.augmentation_params["spatial"]["translate_range"]),
                    np.random.uniform(*self.augmentation_params["spatial"]["translate_range"])
                ]
                rotate = np.random.uniform(*self.augmentation_params["spatial"]["rotate_range"])
                flip = random.random() < 0.5 if self.augmentation_params["spatial"]["horizontal_flip"] else False
                
                for frame_idx in range(len(augmented)):
                    augmented[frame_idx] = self._apply_spatial_transform(
                        augmented[frame_idx], scale, translate, rotate, flip
                    )
            
            # Apply noise augmentations (per frame)
            if "noise" in augmentation_types:
                for frame_idx in range(len(augmented)):
                    augmented[frame_idx] = self._apply_noise_augmentation(augmented[frame_idx])
            
            # Apply body type variations
            if "body_type" in augmentation_types:
                body_type = random.choice(self.augmentation_params["body_types"]["proportions"])
                for frame_idx in range(len(augmented)):
                    augmented[frame_idx] = self._apply_body_proportion(
                        augmented[frame_idx], body_type
                    )
            
            augmented_sequences.append(augmented)
        
        return augmented_sequences
    
    def _apply_spatial_augmentation(self, landmarks: List[Dict]) -> List[Dict]:
        """Apply spatial transformations to landmarks."""
        # Random parameters
        scale = np.random.uniform(*self.augmentation_params["spatial"]["scale_range"])
        translate = [
            np.random.uniform(*self.augmentation_params["spatial"]["translate_range"]),
            np.random.uniform(*self.augmentation_params["spatial"]["translate_range"])
        ]
        rotate = np.random.uniform(*self.augmentation_params["spatial"]["rotate_range"])
        flip = random.random() < 0.5 if self.augmentation_params["spatial"]["horizontal_flip"] else False
        
        return self._apply_spatial_transform(landmarks, scale, translate, rotate, flip)
    
    def _apply_spatial_transform(
        self,
        landmarks: List[Dict],
        scale: float,
        translate: List[float],
        rotate: float,
        flip: bool
    ) -> List[Dict]:
        """Apply specific spatial transformation."""
        augmented = deepcopy(landmarks)
        
        # Convert to numpy array for easier manipulation
        points = np.array([[lm['x'], lm['y']] for lm in landmarks])
        
        # Center the points
        center = np.mean(points, axis=0)
        centered_points = points - center
        
        # Apply scale
        scaled_points = centered_points * scale
        
        # Apply rotation
        angle_rad = np.radians(rotate)
        rotation_matrix = np.array([
            [np.cos(angle_rad), -np.sin(angle_rad)],
            [np.sin(angle_rad), np.cos(angle_rad)]
        ])
        rotated_points = scaled_points @ rotation_matrix.T
        
        # Apply translation and recenter
        final_points = rotated_points + center + np.array(translate)
        
        # Apply horizontal flip if needed
        if flip:
            final_points[:, 0] = 1.0 - final_points[:, 0]
            # Swap left/right landmarks
            final_points = self._swap_left_right_landmarks(final_points)
        
        # Update landmarks
        for i, lm in enumerate(augmented):
            lm['x'] = float(np.clip(final_points[i, 0], 0, 1))
            lm['y'] = float(np.clip(final_points[i, 1], 0, 1))
            # Scale z coordinate proportionally
            if 'z' in lm:
                lm['z'] = lm['z'] * scale
        
        return augmented
    
    def _swap_left_right_landmarks(self, points: np.ndarray) -> np.ndarray:
        """Swap left and right landmarks for horizontal flip."""
        # MediaPipe left/right landmark pairs
        swap_pairs = [
            (1, 2), (3, 6), (4, 5), (7, 8), (9, 10),
            (11, 12), (13, 14), (15, 16), (17, 18),
            (19, 20), (21, 22), (23, 24), (25, 26),
            (27, 28), (29, 30), (31, 32)
        ]
        
        swapped = points.copy()
        for left_idx, right_idx in swap_pairs:
            if left_idx < len(points) and right_idx < len(points):
                swapped[left_idx] = points[right_idx]
                swapped[right_idx] = points[left_idx]
        
        return swapped
    
    def _apply_temporal_augmentation(self, sequence: List[List[Dict]]) -> List[List[Dict]]:
        """Apply temporal augmentations to a sequence."""
        augmented = deepcopy(sequence)
        
        # Speed variation
        speed_factor = np.random.uniform(*self.augmentation_params["temporal"]["speed_variation"])
        if speed_factor != 1.0:
            augmented = self._change_sequence_speed(augmented, speed_factor)
        
        # Frame dropping (simulate lower FPS)
        if self.augmentation_params["temporal"]["frame_drop_rate"] > 0:
            drop_rate = self.augmentation_params["temporal"]["frame_drop_rate"]
            augmented = self._drop_frames(augmented, drop_rate)
        
        return augmented
    
    def _change_sequence_speed(
        self,
        sequence: List[List[Dict]],
        speed_factor: float
    ) -> List[List[Dict]]:
        """Change the speed of a sequence by resampling frames."""
        original_length = len(sequence)
        new_length = int(original_length * speed_factor)
        
        if new_length == original_length:
            return sequence
        
        # Create interpolation indices
        old_indices = np.arange(original_length)
        new_indices = np.linspace(0, original_length - 1, new_length)
        
        # Interpolate each landmark coordinate
        new_sequence = []
        for new_idx in new_indices:
            # Find surrounding frames
            lower_idx = int(np.floor(new_idx))
            upper_idx = min(int(np.ceil(new_idx)), original_length - 1)
            alpha = new_idx - lower_idx
            
            if lower_idx == upper_idx:
                new_sequence.append(deepcopy(sequence[lower_idx]))
            else:
                # Interpolate between frames
                interpolated_frame = []
                for lm_idx in range(len(sequence[lower_idx])):
                    lower_lm = sequence[lower_idx][lm_idx]
                    upper_lm = sequence[upper_idx][lm_idx]
                    
                    interpolated_lm = {
                        'x': lower_lm['x'] * (1 - alpha) + upper_lm['x'] * alpha,
                        'y': lower_lm['y'] * (1 - alpha) + upper_lm['y'] * alpha,
                        'z': lower_lm.get('z', 0) * (1 - alpha) + upper_lm.get('z', 0) * alpha,
                        'visibility': lower_lm.get('visibility', 1) * (1 - alpha) + 
                                    upper_lm.get('visibility', 1) * alpha
                    }
                    
                    if 'landmark_id' in lower_lm:
                        interpolated_lm['landmark_id'] = lower_lm['landmark_id']
                    
                    interpolated_frame.append(interpolated_lm)
                
                new_sequence.append(interpolated_frame)
        
        return new_sequence
    
    def _drop_frames(self, sequence: List[List[Dict]], drop_rate: float) -> List[List[Dict]]:
        """Randomly drop frames from a sequence."""
        keep_indices = []
        for i in range(len(sequence)):
            if random.random() > drop_rate or i == 0 or i == len(sequence) - 1:
                # Always keep first and last frames
                keep_indices.append(i)
        
        return [sequence[i] for i in keep_indices]
    
    def _apply_noise_augmentation(self, landmarks: List[Dict]) -> List[Dict]:
        """Apply noise to landmarks."""
        augmented = deepcopy(landmarks)
        
        for lm in augmented:
            # Position noise
            if self.augmentation_params["noise"]["gaussian_noise"] > 0:
                noise_std = self.augmentation_params["noise"]["gaussian_noise"]
                lm['x'] += np.random.normal(0, noise_std)
                lm['y'] += np.random.normal(0, noise_std)
                if 'z' in lm:
                    lm['z'] += np.random.normal(0, noise_std)
                
                # Clip to valid range
                lm['x'] = float(np.clip(lm['x'], 0, 1))
                lm['y'] = float(np.clip(lm['y'], 0, 1))
            
            # Visibility noise
            if self.augmentation_params["noise"]["visibility_noise"] > 0:
                visibility_noise = self.augmentation_params["noise"]["visibility_noise"]
                if 'visibility' in lm:
                    lm['visibility'] += np.random.normal(0, visibility_noise)
                    lm['visibility'] = float(np.clip(lm['visibility'], 0, 1))
            
            # Random occlusion
            if random.random() < self.augmentation_params["noise"]["occlusion_probability"]:
                lm['visibility'] = 0.0
        
        return augmented
    
    def _apply_body_proportion(
        self,
        landmarks: List[Dict],
        body_type: Dict[str, float]
    ) -> List[Dict]:
        """Apply body proportion changes."""
        augmented = deepcopy(landmarks)
        
        # Get body center (approximate as hip center)
        hip_indices = [23, 24]  # MediaPipe hip landmarks
        if len(landmarks) > max(hip_indices):
            hip_center = np.mean([
                [landmarks[i]['x'], landmarks[i]['y']] 
                for i in hip_indices
            ], axis=0)
        else:
            hip_center = np.array([0.5, 0.5])
        
        # Apply proportional scaling
        for i, lm in enumerate(augmented):
            # Calculate relative position from hip
            rel_x = lm['x'] - hip_center[0]
            rel_y = lm['y'] - hip_center[1]
            
            # Apply height scale (y-axis)
            rel_y *= body_type['height_scale']
            
            # Apply width scale (x-axis) - less aggressive for natural look
            rel_x *= body_type['width_scale'] ** 0.5
            
            # Update position
            lm['x'] = float(np.clip(hip_center[0] + rel_x, 0, 1))
            lm['y'] = float(np.clip(hip_center[1] + rel_y, 0, 1))
        
        return augmented
    
    def create_edge_case_variations(
        self,
        base_sequence: List[List[Dict]],
        exercise_type: str
    ) -> Dict[str, List[List[Dict]]]:
        """
        Create specific edge case variations for training.
        
        Args:
            base_sequence: Base sequence to modify
            exercise_type: Type of exercise
            
        Returns:
            Dictionary of edge case variations
        """
        edge_cases = {}
        
        # Extreme body proportions
        edge_cases['very_tall'] = self.augment_sequence(
            base_sequence,
            augmentation_types=["body_type"],
            num_augmentations=1
        )[0]
        
        # Poor visibility conditions
        noisy_sequence = deepcopy(base_sequence)
        for frame in noisy_sequence:
            for lm in frame:
                lm['visibility'] = lm.get('visibility', 1.0) * 0.5
        edge_cases['low_visibility'] = noisy_sequence
        
        # Partial occlusion
        occluded_sequence = deepcopy(base_sequence)
        # Occlude lower body for upper body exercises and vice versa
        occlusion_indices = range(23, 33) if exercise_type == 'bench_press' else range(11, 17)
        for frame in occluded_sequence:
            for idx in occlusion_indices:
                if idx < len(frame):
                    frame[idx]['visibility'] = 0.0
        edge_cases['partial_occlusion'] = occluded_sequence
        
        # Extreme angles
        edge_cases['extreme_angle'] = self._apply_spatial_transform(
            base_sequence[0], 1.0, [0, 0], 30, False
        )
        
        # Very fast/slow motion
        edge_cases['very_fast'] = self._change_sequence_speed(base_sequence, 2.0)
        edge_cases['very_slow'] = self._change_sequence_speed(base_sequence, 0.5)
        
        return edge_cases
    
    def generate_synthetic_errors(
        self,
        good_sequence: List[List[Dict]],
        exercise_type: str,
        error_type: str
    ) -> List[List[Dict]]:
        """
        Generate synthetic sequences with specific form errors.
        
        Args:
            good_sequence: Sequence with good form
            exercise_type: Type of exercise
            error_type: Type of error to introduce
            
        Returns:
            Sequence with introduced error
        """
        error_sequence = deepcopy(good_sequence)
        
        if exercise_type == 'squat':
            if error_type == 'knee_cave':
                # Make knees move inward during descent
                for i, frame in enumerate(error_sequence):
                    progress = i / len(error_sequence)
                    if 0.3 < progress < 0.7:  # Middle of movement
                        # Move knees inward
                        if 25 < len(frame) and 26 < len(frame):  # Knee indices
                            knee_center = (frame[25]['x'] + frame[26]['x']) / 2
                            frame[25]['x'] = knee_center - 0.02
                            frame[26]['x'] = knee_center + 0.02
            
            elif error_type == 'forward_lean':
                # Excessive forward lean
                for frame in error_sequence:
                    # Rotate upper body forward
                    shoulder_indices = [11, 12]
                    hip_indices = [23, 24]
                    if all(i < len(frame) for i in shoulder_indices + hip_indices):
                        for shoulder_idx in shoulder_indices:
                            frame[shoulder_idx]['y'] += 0.05
                            frame[shoulder_idx]['z'] = frame[shoulder_idx].get('z', 0) - 0.1
        
        elif exercise_type == 'bench_press':
            if error_type == 'uneven_bar':
                # One side higher than the other
                for frame in error_sequence:
                    if 15 < len(frame) and 16 < len(frame):  # Wrist indices
                        frame[15]['y'] -= 0.03
                        frame[16]['y'] += 0.03
        
        elif exercise_type == 'deadlift':
            if error_type == 'rounded_back':
                # Round the back
                spine_indices = [11, 12, 23, 24]  # Simplified spine
                for frame in error_sequence:
                    if all(i < len(frame) for i in spine_indices):
                        # Add curvature
                        mid_point = (frame[11]['y'] + frame[23]['y']) / 2
                        frame[11]['z'] = frame[11].get('z', 0) + 0.05
                        frame[23]['z'] = frame[23].get('z', 0) + 0.05
        
        return error_sequence


def create_balanced_dataset(
    input_data_path: str,
    output_path: str,
    target_samples_per_class: int = 100,
    exercise_types: List[str] = ['squat', 'bench_press', 'deadlift']
) -> Dict[str, int]:
    """
    Create a balanced dataset with augmented samples.
    
    Args:
        input_data_path: Path to input data
        output_path: Path to save augmented dataset
        target_samples_per_class: Target number of samples per exercise type
        exercise_types: List of exercise types to balance
        
    Returns:
        Statistics about the created dataset
    """
    augmenter = PoseDataAugmenter()
    stats = {ex_type: 0 for ex_type in exercise_types}
    augmented_data = []
    
    # Load existing data
    input_path = Path(input_data_path)
    if input_path.exists():
        with open(input_path, 'r') as f:
            existing_data = json.load(f)
            samples = existing_data.get('samples', [])
    else:
        logger.error(f"Input data not found: {input_data_path}")
        return stats
    
    # Group by exercise type
    grouped_samples = {ex_type: [] for ex_type in exercise_types}
    for sample in samples:
        ex_type = sample.get('exercise_type', 'unknown')
        if ex_type in grouped_samples:
            grouped_samples[ex_type].append(sample)
    
    # Augment to reach target count
    for ex_type in exercise_types:
        current_samples = grouped_samples[ex_type]
        current_count = len(current_samples)
        
        if current_count == 0:
            logger.warning(f"No samples found for {ex_type}")
            continue
        
        # Add original samples
        augmented_data.extend(current_samples)
        stats[ex_type] = current_count
        
        # Calculate how many augmentations needed
        if current_count < target_samples_per_class:
            augmentations_needed = target_samples_per_class - current_count
            augmentations_per_sample = augmentations_needed // current_count + 1
            
            for sample in current_samples[:augmentations_needed]:
                # Augment the sequence
                landmark_sequence = sample.get('landmarks_sequence', [])
                if landmark_sequence:
                    augmented_sequences = augmenter.augment_sequence(
                        landmark_sequence,
                        augmentation_types=["spatial", "temporal", "noise"],
                        num_augmentations=augmentations_per_sample
                    )
                    
                    for aug_seq in augmented_sequences[:augmentations_needed - stats[ex_type]]:
                        augmented_sample = deepcopy(sample)
                        augmented_sample['landmarks_sequence'] = aug_seq
                        augmented_sample['is_augmented'] = True
                        augmented_sample['augmentation_id'] = f"{sample.get('data_id', 'unknown')}_aug_{stats[ex_type]}"
                        
                        augmented_data.append(augmented_sample)
                        stats[ex_type] += 1
                        
                        if stats[ex_type] >= target_samples_per_class:
                            break
    
    # Save augmented dataset
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump({
            "dataset_version": "1.0_augmented",
            "created_at": datetime.now().isoformat(),
            "statistics": stats,
            "total_samples": len(augmented_data),
            "samples": augmented_data
        }, f, indent=2)
    
    logger.info(f"Created balanced dataset with {len(augmented_data)} samples")
    logger.info(f"Distribution: {stats}")
    
    return stats