"""
Synthetic pose data generator for training data augmentation.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
import random
from datetime import datetime
import uuid

from .data_schema import (
    Landmark, PoseFrame, ExerciseMetadata, PoseDataset,
    LandmarkMapping, DataAnonymizer
)


class SyntheticPoseGenerator:
    """Generate synthetic pose data for various exercises."""
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize generator with optional random seed."""
        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)
    
    def generate_squat_sequence(
        self,
        num_reps: int = 5,
        fps: float = 30.0,
        noise_level: float = 0.02,
        variation_level: float = 0.1
    ) -> List[PoseFrame]:
        """
        Generate synthetic squat sequence.
        
        Args:
            num_reps: Number of repetitions
            fps: Frames per second
            noise_level: Amount of noise to add (0-1)
            variation_level: Amount of variation between reps (0-1)
            
        Returns:
            List of pose frames
        """
        frames = []
        frame_count = 0
        
        # Define key positions for squat
        standing_pose = self._get_standing_pose()
        squat_pose = self._get_squat_pose()
        
        # Generate each rep
        for rep in range(num_reps):
            # Add variation to this rep
            rep_variation = np.random.randn(33, 3) * variation_level
            
            # Down phase (1.5 seconds)
            down_frames = int(1.5 * fps)
            for i in range(down_frames):
                t = i / down_frames
                frame = self._interpolate_pose(
                    standing_pose, squat_pose, t,
                    noise_level, rep_variation
                )
                frames.append(self._create_frame(frame, frame_count / fps, frame_count))
                frame_count += 1
            
            # Hold at bottom (0.5 seconds)
            hold_frames = int(0.5 * fps)
            for i in range(hold_frames):
                frame = self._add_noise_to_pose(squat_pose + rep_variation, noise_level)
                frames.append(self._create_frame(frame, frame_count / fps, frame_count))
                frame_count += 1
            
            # Up phase (1.5 seconds)
            up_frames = int(1.5 * fps)
            for i in range(up_frames):
                t = i / up_frames
                frame = self._interpolate_pose(
                    squat_pose, standing_pose, t,
                    noise_level, rep_variation
                )
                frames.append(self._create_frame(frame, frame_count / fps, frame_count))
                frame_count += 1
            
            # Brief pause between reps (0.5 seconds)
            pause_frames = int(0.5 * fps)
            for i in range(pause_frames):
                frame = self._add_noise_to_pose(standing_pose + rep_variation, noise_level)
                frames.append(self._create_frame(frame, frame_count / fps, frame_count))
                frame_count += 1
        
        return frames
    
    def generate_bench_press_sequence(
        self,
        num_reps: int = 5,
        fps: float = 30.0,
        noise_level: float = 0.02,
        variation_level: float = 0.1
    ) -> List[PoseFrame]:
        """
        Generate synthetic bench press sequence.
        
        Args:
            num_reps: Number of repetitions
            fps: Frames per second
            noise_level: Amount of noise to add (0-1)
            variation_level: Amount of variation between reps (0-1)
            
        Returns:
            List of pose frames
        """
        frames = []
        frame_count = 0
        
        # Define key positions for bench press
        top_pose = self._get_bench_press_top_pose()
        bottom_pose = self._get_bench_press_bottom_pose()
        
        # Generate each rep
        for rep in range(num_reps):
            # Add variation to this rep
            rep_variation = np.random.randn(33, 3) * variation_level
            
            # Down phase (2 seconds)
            down_frames = int(2.0 * fps)
            for i in range(down_frames):
                t = i / down_frames
                frame = self._interpolate_pose(
                    top_pose, bottom_pose, t,
                    noise_level, rep_variation
                )
                frames.append(self._create_frame(frame, frame_count / fps, frame_count))
                frame_count += 1
            
            # Brief pause at bottom (0.3 seconds)
            pause_frames = int(0.3 * fps)
            for i in range(pause_frames):
                frame = self._add_noise_to_pose(bottom_pose + rep_variation, noise_level)
                frames.append(self._create_frame(frame, frame_count / fps, frame_count))
                frame_count += 1
            
            # Up phase (1.5 seconds)
            up_frames = int(1.5 * fps)
            for i in range(up_frames):
                t = i / up_frames
                frame = self._interpolate_pose(
                    bottom_pose, top_pose, t,
                    noise_level, rep_variation
                )
                frames.append(self._create_frame(frame, frame_count / fps, frame_count))
                frame_count += 1
            
            # Brief pause at top (0.5 seconds)
            pause_frames = int(0.5 * fps)
            for i in range(pause_frames):
                frame = self._add_noise_to_pose(top_pose + rep_variation, noise_level)
                frames.append(self._create_frame(frame, frame_count / fps, frame_count))
                frame_count += 1
        
        return frames
    
    def generate_deadlift_sequence(
        self,
        num_reps: int = 5,
        fps: float = 30.0,
        noise_level: float = 0.02,
        variation_level: float = 0.1
    ) -> List[PoseFrame]:
        """
        Generate synthetic deadlift sequence.
        
        Args:
            num_reps: Number of repetitions
            fps: Frames per second
            noise_level: Amount of noise to add (0-1)
            variation_level: Amount of variation between reps (0-1)
            
        Returns:
            List of pose frames
        """
        frames = []
        frame_count = 0
        
        # Define key positions for deadlift
        standing_pose = self._get_standing_pose()
        bottom_pose = self._get_deadlift_bottom_pose()
        
        # Generate each rep
        for rep in range(num_reps):
            # Add variation to this rep
            rep_variation = np.random.randn(33, 3) * variation_level
            
            # Down phase (2 seconds)
            down_frames = int(2.0 * fps)
            for i in range(down_frames):
                t = i / down_frames
                frame = self._interpolate_pose(
                    standing_pose, bottom_pose, t,
                    noise_level, rep_variation
                )
                frames.append(self._create_frame(frame, frame_count / fps, frame_count))
                frame_count += 1
            
            # Brief pause at bottom (0.3 seconds)
            pause_frames = int(0.3 * fps)
            for i in range(pause_frames):
                frame = self._add_noise_to_pose(bottom_pose + rep_variation, noise_level)
                frames.append(self._create_frame(frame, frame_count / fps, frame_count))
                frame_count += 1
            
            # Up phase (2 seconds)
            up_frames = int(2.0 * fps)
            for i in range(up_frames):
                t = i / up_frames
                frame = self._interpolate_pose(
                    bottom_pose, standing_pose, t,
                    noise_level, rep_variation
                )
                frames.append(self._create_frame(frame, frame_count / fps, frame_count))
                frame_count += 1
            
            # Brief pause at top (0.7 seconds)
            pause_frames = int(0.7 * fps)
            for i in range(pause_frames):
                frame = self._add_noise_to_pose(standing_pose + rep_variation, noise_level)
                frames.append(self._create_frame(frame, frame_count / fps, frame_count))
                frame_count += 1
        
        return frames
    
    def generate_dataset(
        self,
        exercise_type: str,
        num_reps: int = 5,
        fps: float = 30.0,
        noise_level: float = 0.02,
        variation_level: float = 0.1,
        user_id: Optional[str] = None
    ) -> PoseDataset:
        """
        Generate complete synthetic dataset.
        
        Args:
            exercise_type: Type of exercise (squat, bench_press, deadlift)
            num_reps: Number of repetitions
            fps: Frames per second
            noise_level: Amount of noise to add
            variation_level: Amount of variation between reps
            user_id: Optional user ID (will be anonymized)
            
        Returns:
            Complete PoseDataset
        """
        # Generate frames based on exercise type
        if exercise_type == 'squat':
            frames = self.generate_squat_sequence(num_reps, fps, noise_level, variation_level)
        elif exercise_type == 'bench_press':
            frames = self.generate_bench_press_sequence(num_reps, fps, noise_level, variation_level)
        elif exercise_type == 'deadlift':
            frames = self.generate_deadlift_sequence(num_reps, fps, noise_level, variation_level)
        else:
            raise ValueError(f"Unknown exercise type: {exercise_type}")
        
        # Create metadata
        duration = len(frames) / fps if frames else 0
        metadata = ExerciseMetadata(
            exercise_type=exercise_type,
            duration_seconds=duration,
            fps=fps,
            total_frames=len(frames),
            recording_device="synthetic",
            environment="synthetic",
            difficulty_level="intermediate"
        )
        
        # Create user ID if not provided
        if user_id is None:
            user_id = f"synthetic_{uuid.uuid4().hex[:8]}"
        
        # Create dataset
        dataset_id = f"synthetic_{exercise_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        user_hash = DataAnonymizer.hash_user_id(user_id)
        
        dataset = PoseDataset(
            dataset_id=dataset_id,
            user_hash=user_hash,
            frames=frames,
            metadata=metadata,
            created_at=datetime.now()
        )
        
        return dataset
    
    def _get_standing_pose(self) -> np.ndarray:
        """Get standard standing pose coordinates."""
        pose = np.zeros((33, 3))
        
        # Head and face landmarks
        pose[0] = [0.5, 0.15, 0]  # nose
        pose[1:7] = [[0.48, 0.13, 0], [0.48, 0.13, 0], [0.47, 0.13, 0],
                     [0.52, 0.13, 0], [0.52, 0.13, 0], [0.53, 0.13, 0]]
        pose[7:9] = [[0.45, 0.14, 0], [0.55, 0.14, 0]]  # ears
        pose[9:11] = [[0.48, 0.17, 0], [0.52, 0.17, 0]]  # mouth
        
        # Upper body
        pose[11:13] = [[0.42, 0.3, 0], [0.58, 0.3, 0]]  # shoulders
        pose[13:15] = [[0.4, 0.5, 0], [0.6, 0.5, 0]]  # elbows
        pose[15:17] = [[0.38, 0.7, 0], [0.62, 0.7, 0]]  # wrists
        
        # Hands
        pose[17:23] = pose[15:17].repeat(3, axis=0) + np.random.randn(6, 3) * 0.01
        
        # Lower body
        pose[23:25] = [[0.45, 0.6, 0], [0.55, 0.6, 0]]  # hips
        pose[25:27] = [[0.44, 0.8, 0], [0.56, 0.8, 0]]  # knees
        pose[27:29] = [[0.43, 0.95, 0], [0.57, 0.95, 0]]  # ankles
        
        # Feet
        pose[29:33] = pose[27:29].repeat(2, axis=0) + np.random.randn(4, 3) * 0.01
        
        return pose
    
    def _get_squat_pose(self) -> np.ndarray:
        """Get squat bottom position pose."""
        pose = self._get_standing_pose().copy()
        
        # Lower the hips and bend knees
        pose[23:25, 1] += 0.25  # hips down
        pose[25:27, 1] += 0.15  # knees slightly down
        pose[25:27, 0] = [[0.42, 0], [0.58, 0]]  # knees out
        
        # Lean torso forward slightly
        pose[11:13, 1] += 0.05  # shoulders forward
        pose[11:13, 2] -= 0.1  # shoulders forward in z
        
        # Adjust upper body accordingly
        pose[0:11, 1] += 0.03  # head/face forward
        pose[13:17, 1] += 0.05  # arms forward
        
        return pose
    
    def _get_bench_press_top_pose(self) -> np.ndarray:
        """Get bench press top position (lying down, arms extended)."""
        pose = np.zeros((33, 3))
        
        # Lying position - rotate standing pose
        # Head and face (lower in frame)
        pose[0] = [0.5, 0.7, 0.1]  # nose
        pose[1:11] = pose[0] + np.random.randn(10, 3) * 0.02
        
        # Shoulders (spread wide)
        pose[11:13] = [[0.35, 0.65, 0.1], [0.65, 0.65, 0.1]]
        
        # Arms extended up (lower y = up in lying position)
        pose[13:15] = [[0.33, 0.45, 0.15], [0.67, 0.45, 0.15]]  # elbows
        pose[15:17] = [[0.32, 0.3, 0.2], [0.68, 0.3, 0.2]]  # wrists
        
        # Hands
        pose[17:23] = pose[15:17].repeat(3, axis=0) + np.random.randn(6, 3) * 0.01
        
        # Lower body (higher in frame)
        pose[23:25] = [[0.45, 0.75, 0.05], [0.55, 0.75, 0.05]]  # hips
        pose[25:27] = [[0.44, 0.85, 0.02], [0.56, 0.85, 0.02]]  # knees
        pose[27:33] = [[0.43, 0.95, 0], [0.57, 0.95, 0]].repeat(3, axis=0)  # ankles/feet
        
        return pose
    
    def _get_bench_press_bottom_pose(self) -> np.ndarray:
        """Get bench press bottom position (arms bent)."""
        pose = self._get_bench_press_top_pose().copy()
        
        # Bring elbows down and out
        pose[13:15] = [[0.25, 0.6, 0.1], [0.75, 0.6, 0.1]]  # elbows
        
        # Bring wrists to chest level
        pose[15:17] = [[0.35, 0.55, 0.12], [0.65, 0.55, 0.12]]  # wrists
        
        # Adjust hands
        pose[17:23] = pose[15:17].repeat(3, axis=0) + np.random.randn(6, 3) * 0.01
        
        return pose
    
    def _get_deadlift_bottom_pose(self) -> np.ndarray:
        """Get deadlift starting position."""
        pose = self._get_standing_pose().copy()
        
        # Bend at hips and knees
        pose[23:25, 1] += 0.2  # hips down and back
        pose[23:25, 2] -= 0.15  # hips back
        pose[25:27, 1] += 0.1  # knees slightly bent
        
        # Lean torso forward significantly
        pose[11:13, 1] += 0.25  # shoulders down
        pose[11:13, 2] -= 0.2  # shoulders forward
        
        # Arms hanging down
        pose[13:15, 1] = 0.55  # elbows down
        pose[15:17, 1] = 0.75  # wrists near ground
        
        # Adjust head and upper body
        pose[0:11, 1] += 0.2  # head forward and down
        pose[0:11, 2] -= 0.15
        
        return pose
    
    def _interpolate_pose(
        self,
        pose1: np.ndarray,
        pose2: np.ndarray,
        t: float,
        noise_level: float,
        variation: np.ndarray
    ) -> np.ndarray:
        """Interpolate between two poses with smooth easing."""
        # Use cubic easing for more natural movement
        t_eased = t * t * (3.0 - 2.0 * t)
        
        # Linear interpolation
        interpolated = pose1 * (1 - t_eased) + pose2 * t_eased
        
        # Add variation
        interpolated += variation * (0.5 + 0.5 * np.sin(t * np.pi))
        
        # Add noise
        interpolated = self._add_noise_to_pose(interpolated, noise_level)
        
        return interpolated
    
    def _add_noise_to_pose(self, pose: np.ndarray, noise_level: float) -> np.ndarray:
        """Add realistic noise to pose."""
        noise = np.random.randn(*pose.shape) * noise_level
        
        # Less noise for stable body parts
        noise[23:25] *= 0.5  # hips are more stable
        noise[11:13] *= 0.7  # shoulders fairly stable
        
        # More noise for extremities
        noise[15:17] *= 1.2  # wrists
        noise[17:23] *= 1.5  # hands
        noise[29:33] *= 1.3  # feet
        
        return pose + noise
    
    def _create_frame(self, pose_coords: np.ndarray, timestamp: float, 
                     frame_number: int) -> PoseFrame:
        """Create PoseFrame from coordinates."""
        landmarks = []
        
        for i, coords in enumerate(pose_coords):
            # Add visibility based on position and noise
            visibility = 0.95 - np.random.random() * 0.1
            
            # Lower visibility for occluded parts in certain poses
            if coords[2] < 0:  # Behind body plane
                visibility *= 0.7
            
            landmark = Landmark(
                x=float(coords[0]),
                y=float(coords[1]),
                z=float(coords[2]),
                visibility=visibility,
                name=LandmarkMapping.get_landmark_name(i),
                landmark_id=i
            )
            landmarks.append(landmark)
        
        # Calculate average confidence
        avg_confidence = np.mean([lm.visibility for lm in landmarks])
        
        return PoseFrame(
            landmarks=landmarks,
            timestamp=timestamp,
            frame_number=frame_number,
            confidence=avg_confidence
        )


def generate_training_batch(
    num_samples_per_exercise: int = 10,
    exercises: List[str] = ['squat', 'bench_press', 'deadlift'],
    output_dir: str = 'ml/data/synthetic',
    seed: Optional[int] = None
) -> List[str]:
    """
    Generate batch of synthetic training data.
    
    Args:
        num_samples_per_exercise: Number of samples per exercise type
        exercises: List of exercises to generate
        output_dir: Directory to save generated data
        seed: Random seed for reproducibility
        
    Returns:
        List of generated file paths
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    generator = SyntheticPoseGenerator(seed=seed)
    generated_files = []
    
    for exercise in exercises:
        for i in range(num_samples_per_exercise):
            # Vary parameters for each sample
            num_reps = random.randint(3, 8)
            fps = random.choice([24.0, 30.0, 60.0])
            noise_level = random.uniform(0.01, 0.04)
            variation_level = random.uniform(0.05, 0.15)
            
            # Generate dataset
            dataset = generator.generate_dataset(
                exercise_type=exercise,
                num_reps=num_reps,
                fps=fps,
                noise_level=noise_level,
                variation_level=variation_level
            )
            
            # Save to file
            filename = f"{dataset.dataset_id}.json"
            filepath = os.path.join(output_dir, filename)
            dataset.save(filepath)
            generated_files.append(filepath)
            
            print(f"Generated {filename} - {exercise} with {num_reps} reps")
    
    return generated_files


if __name__ == "__main__":
    # Example usage
    generator = SyntheticPoseGenerator(seed=42)
    
    # Generate single dataset
    dataset = generator.generate_dataset(
        exercise_type='squat',
        num_reps=5,
        fps=30.0,
        noise_level=0.02,
        variation_level=0.1
    )
    
    print(f"Generated dataset: {dataset.dataset_id}")
    print(f"Total frames: {len(dataset.frames)}")
    print(f"Duration: {dataset.metadata.duration_seconds:.2f} seconds")
    
    # Generate training batch
    print("\nGenerating training batch...")
    files = generate_training_batch(
        num_samples_per_exercise=5,
        exercises=['squat', 'bench_press', 'deadlift']
    )
    print(f"Generated {len(files)} synthetic datasets")