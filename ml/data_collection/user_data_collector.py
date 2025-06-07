"""
User data collection module with consent management and privacy protection.
"""

import os
import json
import hashlib
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
from pathlib import Path
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserDataCollector:
    """Manages user data collection with consent and privacy protection."""
    
    def __init__(self, data_dir: str = "data/user_contributions"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Subdirectories for different data types
        self.raw_dir = self.data_dir / "raw"
        self.annotated_dir = self.data_dir / "annotated"
        self.metadata_dir = self.data_dir / "metadata"
        
        for dir_path in [self.raw_dir, self.annotated_dir, self.metadata_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # Load consent records
        self.consent_file = self.data_dir / "consent_records.json"
        self.consent_records = self._load_consent_records()
    
    def _load_consent_records(self) -> Dict[str, Any]:
        """Load existing consent records."""
        if self.consent_file.exists():
            try:
                with open(self.consent_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading consent records: {e}")
        return {}
    
    def _save_consent_records(self):
        """Save consent records to file."""
        try:
            with open(self.consent_file, 'w') as f:
                json.dump(self.consent_records, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving consent records: {e}")
    
    def record_consent(
        self, 
        user_id: str, 
        consent_type: str = "full",
        purposes: List[str] = None,
        duration_days: int = 365
    ) -> Dict[str, Any]:
        """
        Record user consent for data collection.
        
        Args:
            user_id: User identifier (anonymized)
            consent_type: Type of consent (full, limited, research_only)
            purposes: List of allowed purposes
            duration_days: Consent duration in days
            
        Returns:
            Consent record
        """
        # Hash user ID for privacy
        hashed_user_id = hashlib.sha256(user_id.encode()).hexdigest()[:16]
        
        if purposes is None:
            purposes = ["model_improvement", "research", "quality_analysis"]
        
        consent_record = {
            "consent_id": str(uuid.uuid4()),
            "user_hash": hashed_user_id,
            "consent_type": consent_type,
            "purposes": purposes,
            "granted_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + datetime.timedelta(days=duration_days)).isoformat(),
            "duration_days": duration_days,
            "revoked": False
        }
        
        self.consent_records[hashed_user_id] = consent_record
        self._save_consent_records()
        
        logger.info(f"Recorded consent for user {hashed_user_id}")
        return consent_record
    
    def check_consent(self, user_id: str) -> bool:
        """Check if user has valid consent."""
        hashed_user_id = hashlib.sha256(user_id.encode()).hexdigest()[:16]
        
        if hashed_user_id not in self.consent_records:
            return False
        
        record = self.consent_records[hashed_user_id]
        
        # Check if consent is revoked
        if record.get("revoked", False):
            return False
        
        # Check if consent is expired
        expires_at = datetime.fromisoformat(record["expires_at"])
        if datetime.now() > expires_at:
            return False
        
        return True
    
    def revoke_consent(self, user_id: str) -> bool:
        """Revoke user consent and remove their data."""
        hashed_user_id = hashlib.sha256(user_id.encode()).hexdigest()[:16]
        
        if hashed_user_id in self.consent_records:
            # Mark consent as revoked
            self.consent_records[hashed_user_id]["revoked"] = True
            self.consent_records[hashed_user_id]["revoked_at"] = datetime.now().isoformat()
            self._save_consent_records()
            
            # Remove user's data
            self._remove_user_data(hashed_user_id)
            
            logger.info(f"Revoked consent and removed data for user {hashed_user_id}")
            return True
        
        return False
    
    def _remove_user_data(self, hashed_user_id: str):
        """Remove all data associated with a user."""
        # Remove raw data
        for file_path in self.raw_dir.glob(f"{hashed_user_id}_*"):
            try:
                file_path.unlink()
            except Exception as e:
                logger.error(f"Error removing file {file_path}: {e}")
        
        # Remove annotated data
        for file_path in self.annotated_dir.glob(f"{hashed_user_id}_*"):
            try:
                file_path.unlink()
            except Exception as e:
                logger.error(f"Error removing file {file_path}: {e}")
    
    def collect_exercise_data(
        self,
        user_id: str,
        exercise_type: str,
        landmarks_sequence: List[List[Dict]],
        analysis_results: Dict[str, Any],
        user_annotations: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Collect exercise data with user consent.
        
        Args:
            user_id: User identifier
            exercise_type: Type of exercise
            landmarks_sequence: Sequence of pose landmarks
            analysis_results: Analysis results from the system
            user_annotations: Optional user-provided annotations
            
        Returns:
            Data ID if successful, None otherwise
        """
        # Check consent
        if not self.check_consent(user_id):
            logger.warning(f"No valid consent for user {user_id}")
            return None
        
        hashed_user_id = hashlib.sha256(user_id.encode()).hexdigest()[:16]
        data_id = f"{hashed_user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        # Prepare data package
        data_package = {
            "data_id": data_id,
            "user_hash": hashed_user_id,
            "collected_at": datetime.now().isoformat(),
            "exercise_type": exercise_type,
            "landmarks_sequence": landmarks_sequence,
            "frame_count": len(landmarks_sequence),
            "analysis_results": analysis_results,
            "user_annotations": user_annotations or {},
            "data_version": "1.0",
            "privacy_level": "anonymized"
        }
        
        # Add quality metrics
        data_package["quality_metrics"] = self._calculate_quality_metrics(landmarks_sequence)
        
        # Save data
        try:
            # Save raw data
            raw_file = self.raw_dir / f"{data_id}.json"
            with open(raw_file, 'w') as f:
                json.dump(data_package, f, indent=2)
            
            # Save metadata
            metadata = {
                "data_id": data_id,
                "user_hash": hashed_user_id,
                "exercise_type": exercise_type,
                "collected_at": data_package["collected_at"],
                "frame_count": data_package["frame_count"],
                "quality_score": data_package["quality_metrics"]["overall_score"],
                "has_annotations": bool(user_annotations)
            }
            
            metadata_file = self.metadata_dir / f"{data_id}_meta.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Collected exercise data: {data_id}")
            return data_id
            
        except Exception as e:
            logger.error(f"Error collecting data: {e}")
            return None
    
    def _calculate_quality_metrics(self, landmarks_sequence: List[List[Dict]]) -> Dict[str, float]:
        """Calculate quality metrics for the collected data."""
        if not landmarks_sequence:
            return {"overall_score": 0.0}
        
        # Calculate average visibility
        visibility_scores = []
        for frame in landmarks_sequence:
            frame_visibility = [lm.get('visibility', 0) for lm in frame]
            if frame_visibility:
                visibility_scores.append(np.mean(frame_visibility))
        
        avg_visibility = np.mean(visibility_scores) if visibility_scores else 0
        
        # Calculate stability (low variance in positions)
        position_variances = []
        for landmark_idx in range(min(33, len(landmarks_sequence[0]) if landmarks_sequence else 0)):
            x_positions = [frame[landmark_idx].get('x', 0) for frame in landmarks_sequence if landmark_idx < len(frame)]
            y_positions = [frame[landmark_idx].get('y', 0) for frame in landmarks_sequence if landmark_idx < len(frame)]
            
            if x_positions and y_positions:
                position_variances.append(np.var(x_positions) + np.var(y_positions))
        
        avg_stability = 1.0 - min(np.mean(position_variances) * 100, 1.0) if position_variances else 0
        
        # Calculate completeness
        expected_landmarks = 33  # MediaPipe pose landmarks
        completeness_scores = []
        for frame in landmarks_sequence:
            visible_count = sum(1 for lm in frame if lm.get('visibility', 0) > 0.5)
            completeness_scores.append(visible_count / expected_landmarks)
        
        avg_completeness = np.mean(completeness_scores) if completeness_scores else 0
        
        # Overall quality score
        overall_score = (avg_visibility * 0.4 + avg_stability * 0.3 + avg_completeness * 0.3)
        
        return {
            "overall_score": round(overall_score, 3),
            "visibility_score": round(avg_visibility, 3),
            "stability_score": round(avg_stability, 3),
            "completeness_score": round(avg_completeness, 3),
            "frame_count": len(landmarks_sequence)
        }
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about collected data."""
        stats = {
            "total_users": len(self.consent_records),
            "active_consents": sum(1 for r in self.consent_records.values() if not r.get("revoked", False)),
            "total_sessions": len(list(self.raw_dir.glob("*.json"))),
            "annotated_sessions": len(list(self.annotated_dir.glob("*.json"))),
            "exercise_types": {},
            "quality_distribution": {"high": 0, "medium": 0, "low": 0}
        }
        
        # Analyze metadata
        for meta_file in self.metadata_dir.glob("*_meta.json"):
            try:
                with open(meta_file, 'r') as f:
                    metadata = json.load(f)
                    
                    # Count exercise types
                    ex_type = metadata.get("exercise_type", "unknown")
                    stats["exercise_types"][ex_type] = stats["exercise_types"].get(ex_type, 0) + 1
                    
                    # Quality distribution
                    quality_score = metadata.get("quality_score", 0)
                    if quality_score >= 0.8:
                        stats["quality_distribution"]["high"] += 1
                    elif quality_score >= 0.6:
                        stats["quality_distribution"]["medium"] += 1
                    else:
                        stats["quality_distribution"]["low"] += 1
                        
            except Exception as e:
                logger.error(f"Error reading metadata {meta_file}: {e}")
        
        return stats
    
    def export_anonymized_dataset(self, output_path: str, min_quality_score: float = 0.6) -> int:
        """
        Export anonymized dataset for training.
        
        Args:
            output_path: Path to save the dataset
            min_quality_score: Minimum quality score for inclusion
            
        Returns:
            Number of samples exported
        """
        exported_data = []
        
        for data_file in self.raw_dir.glob("*.json"):
            try:
                with open(data_file, 'r') as f:
                    data = json.load(f)
                
                # Check quality
                quality_score = data.get("quality_metrics", {}).get("overall_score", 0)
                if quality_score < min_quality_score:
                    continue
                
                # Remove identifying information
                anonymized_data = {
                    "exercise_type": data["exercise_type"],
                    "landmarks_sequence": data["landmarks_sequence"],
                    "frame_count": data["frame_count"],
                    "quality_metrics": data["quality_metrics"]
                }
                
                # Include analysis results if available
                if "analysis_results" in data:
                    anonymized_data["labels"] = {
                        "form_scores": data["analysis_results"].get("scores", {}),
                        "phases": data["analysis_results"].get("phases", [])
                    }
                
                exported_data.append(anonymized_data)
                
            except Exception as e:
                logger.error(f"Error processing {data_file}: {e}")
        
        # Save exported dataset
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump({
                    "dataset_version": "1.0",
                    "exported_at": datetime.now().isoformat(),
                    "sample_count": len(exported_data),
                    "min_quality_score": min_quality_score,
                    "samples": exported_data
                }, f, indent=2)
            
            logger.info(f"Exported {len(exported_data)} samples to {output_path}")
            return len(exported_data)
            
        except Exception as e:
            logger.error(f"Error exporting dataset: {e}")
            return 0


# Singleton instance
_collector_instance = None

def get_data_collector() -> UserDataCollector:
    """Get singleton instance of UserDataCollector."""
    global _collector_instance
    if _collector_instance is None:
        _collector_instance = UserDataCollector()
    return _collector_instance