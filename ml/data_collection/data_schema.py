"""
Data schema and structures for pose data collection and anonymization.
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
import hashlib
import json
from datetime import datetime
import numpy as np


@dataclass
class Landmark:
    """Single pose landmark with 3D coordinates and confidence."""
    x: float
    y: float
    z: float
    visibility: float
    name: str
    landmark_id: int


@dataclass
class PoseFrame:
    """Single frame of pose data."""
    landmarks: List[Landmark]
    timestamp: float
    frame_number: int
    confidence: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            'landmarks': [asdict(lm) for lm in self.landmarks],
            'timestamp': self.timestamp,
            'frame_number': self.frame_number,
            'confidence': self.confidence
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PoseFrame':
        """Create from dictionary format."""
        landmarks = [Landmark(**lm) for lm in data['landmarks']]
        return cls(
            landmarks=landmarks,
            timestamp=data['timestamp'],
            frame_number=data['frame_number'],
            confidence=data['confidence']
        )


@dataclass
class ExerciseMetadata:
    """Metadata for an exercise recording."""
    exercise_type: str
    duration_seconds: float
    fps: float
    total_frames: int
    recording_device: Optional[str] = None
    environment: Optional[str] = None  # gym, home, outdoor
    difficulty_level: Optional[str] = None  # beginner, intermediate, advanced
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return asdict(self)


@dataclass
class PoseDataset:
    """Complete dataset for a single exercise recording."""
    dataset_id: str
    user_hash: str  # Anonymized user ID
    frames: List[PoseFrame]
    metadata: ExerciseMetadata
    created_at: datetime
    version: str = "1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for storage."""
        return {
            'dataset_id': self.dataset_id,
            'user_hash': self.user_hash,
            'frames': [frame.to_dict() for frame in self.frames],
            'metadata': self.metadata.to_dict(),
            'created_at': self.created_at.isoformat(),
            'version': self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PoseDataset':
        """Create from dictionary format."""
        frames = [PoseFrame.from_dict(f) for f in data['frames']]
        metadata = ExerciseMetadata(**data['metadata'])
        return cls(
            dataset_id=data['dataset_id'],
            user_hash=data['user_hash'],
            frames=frames,
            metadata=metadata,
            created_at=datetime.fromisoformat(data['created_at']),
            version=data.get('version', '1.0')
        )
    
    def save(self, filepath: str):
        """Save dataset to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, filepath: str) -> 'PoseDataset':
        """Load dataset from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)


class DataAnonymizer:
    """Handles anonymization of user data."""
    
    @staticmethod
    def hash_user_id(user_id: str, salt: Optional[str] = None) -> str:
        """
        Create anonymized hash from user ID.
        
        Args:
            user_id: Original user identifier
            salt: Optional salt for additional security
            
        Returns:
            Anonymized hash string
        """
        if salt:
            user_id = f"{user_id}{salt}"
        return hashlib.sha256(user_id.encode()).hexdigest()[:16]
    
    @staticmethod
    def anonymize_dataset(dataset: PoseDataset, user_id: str, 
                         salt: Optional[str] = None) -> PoseDataset:
        """
        Create anonymized copy of dataset.
        
        Args:
            dataset: Original dataset
            user_id: Original user ID to anonymize
            salt: Optional salt for hashing
            
        Returns:
            New dataset with anonymized user ID
        """
        dataset_copy = PoseDataset(
            dataset_id=dataset.dataset_id,
            user_hash=DataAnonymizer.hash_user_id(user_id, salt),
            frames=dataset.frames,
            metadata=dataset.metadata,
            created_at=dataset.created_at,
            version=dataset.version
        )
        return dataset_copy


class LandmarkMapping:
    """MediaPipe landmark name mapping."""
    POSE_LANDMARKS = {
        0: 'nose',
        1: 'left_eye_inner',
        2: 'left_eye',
        3: 'left_eye_outer',
        4: 'right_eye_inner',
        5: 'right_eye',
        6: 'right_eye_outer',
        7: 'left_ear',
        8: 'right_ear',
        9: 'mouth_left',
        10: 'mouth_right',
        11: 'left_shoulder',
        12: 'right_shoulder',
        13: 'left_elbow',
        14: 'right_elbow',
        15: 'left_wrist',
        16: 'right_wrist',
        17: 'left_pinky',
        18: 'right_pinky',
        19: 'left_index',
        20: 'right_index',
        21: 'left_thumb',
        22: 'right_thumb',
        23: 'left_hip',
        24: 'right_hip',
        25: 'left_knee',
        26: 'right_knee',
        27: 'left_ankle',
        28: 'right_ankle',
        29: 'left_heel',
        30: 'right_heel',
        31: 'left_foot_index',
        32: 'right_foot_index'
    }
    
    @classmethod
    def get_landmark_name(cls, idx: int) -> str:
        """Get landmark name from index."""
        return cls.POSE_LANDMARKS.get(idx, f'unknown_{idx}')


def validate_pose_data(frames: List[PoseFrame]) -> bool:
    """
    Validate pose data quality.
    
    Args:
        frames: List of pose frames to validate
        
    Returns:
        True if data passes validation
    """
    if not frames:
        return False
    
    # Check consistent landmark count
    landmark_counts = [len(frame.landmarks) for frame in frames]
    if len(set(landmark_counts)) > 1:
        return False
    
    # Check reasonable confidence values
    for frame in frames:
        if not (0 <= frame.confidence <= 1):
            return False
        for landmark in frame.landmarks:
            if not (0 <= landmark.visibility <= 1):
                return False
    
    return True


def create_dataset_from_mediapipe(
    pose_results: List[Any],
    user_id: str,
    exercise_type: str,
    fps: float = 30.0,
    anonymize: bool = True,
    salt: Optional[str] = None
) -> PoseDataset:
    """
    Create dataset from MediaPipe pose results.
    
    Args:
        pose_results: List of MediaPipe pose detection results
        user_id: User identifier
        exercise_type: Type of exercise performed
        fps: Frames per second of recording
        anonymize: Whether to anonymize user ID
        salt: Optional salt for anonymization
        
    Returns:
        PoseDataset object
    """
    frames = []
    
    for i, result in enumerate(pose_results):
        if result.pose_landmarks:
            landmarks = []
            for j, lm in enumerate(result.pose_landmarks.landmark):
                landmark = Landmark(
                    x=lm.x,
                    y=lm.y,
                    z=lm.z,
                    visibility=lm.visibility,
                    name=LandmarkMapping.get_landmark_name(j),
                    landmark_id=j
                )
                landmarks.append(landmark)
            
            # Calculate average confidence
            avg_confidence = np.mean([lm.visibility for lm in landmarks])
            
            frame = PoseFrame(
                landmarks=landmarks,
                timestamp=i / fps,
                frame_number=i,
                confidence=avg_confidence
            )
            frames.append(frame)
    
    # Create metadata
    duration = len(frames) / fps if frames else 0
    metadata = ExerciseMetadata(
        exercise_type=exercise_type,
        duration_seconds=duration,
        fps=fps,
        total_frames=len(frames)
    )
    
    # Create dataset
    dataset_id = f"{exercise_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    user_hash = DataAnonymizer.hash_user_id(user_id, salt) if anonymize else user_id
    
    dataset = PoseDataset(
        dataset_id=dataset_id,
        user_hash=user_hash,
        frames=frames,
        metadata=metadata,
        created_at=datetime.now()
    )
    
    return dataset