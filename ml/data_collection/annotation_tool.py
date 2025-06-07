"""
Annotation tool for labeling exercise form data.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExerciseAnnotationTool:
    """Tool for annotating exercise form data with quality labels and corrections."""
    
    def __init__(self, data_dir: str = "data/user_contributions"):
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw"
        self.annotated_dir = self.data_dir / "annotated"
        self.annotation_queue_file = self.data_dir / "annotation_queue.json"
        
        # Ensure directories exist
        self.annotated_dir.mkdir(parents=True, exist_ok=True)
        
        # Load annotation queue
        self.annotation_queue = self._load_annotation_queue()
        
        # Annotation schema
        self.annotation_schema = {
            "form_quality": {
                "overall": {"type": "score", "range": [0, 100], "description": "総合的なフォーム品質"},
                "depth": {"type": "score", "range": [0, 100], "description": "動作の深さ・可動域"},
                "stability": {"type": "score", "range": [0, 100], "description": "動作の安定性"},
                "alignment": {"type": "score", "range": [0, 100], "description": "体のアライメント"}
            },
            "phase_labels": {
                "setup": {"type": "boolean", "description": "セットアップフェーズ"},
                "descent": {"type": "boolean", "description": "下降フェーズ"},
                "bottom": {"type": "boolean", "description": "最下点"},
                "ascent": {"type": "boolean", "description": "上昇フェーズ"},
                "lockout": {"type": "boolean", "description": "フィニッシュ位置"}
            },
            "common_errors": {
                "knee_cave": {"type": "boolean", "description": "膝が内側に入る"},
                "forward_lean": {"type": "boolean", "description": "前傾しすぎ"},
                "butt_wink": {"type": "boolean", "description": "腰の丸まり"},
                "heel_rise": {"type": "boolean", "description": "かかとが浮く"},
                "uneven_bar": {"type": "boolean", "description": "バーの傾き"},
                "partial_rom": {"type": "boolean", "description": "可動域不足"},
                "back_arch": {"type": "boolean", "description": "背中の反りすぎ"}
            },
            "corrections": {
                "type": "text_list",
                "description": "具体的な改善アドバイス"
            },
            "rep_quality": {
                "type": "per_rep_score",
                "description": "各レップの品質スコア"
            }
        }
    
    def _load_annotation_queue(self) -> List[Dict]:
        """Load the annotation queue."""
        if self.annotation_queue_file.exists():
            try:
                with open(self.annotation_queue_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading annotation queue: {e}")
        return []
    
    def _save_annotation_queue(self):
        """Save the annotation queue."""
        try:
            with open(self.annotation_queue_file, 'w') as f:
                json.dump(self.annotation_queue, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving annotation queue: {e}")
    
    def add_to_annotation_queue(self, data_id: str, priority: int = 5):
        """Add a data sample to the annotation queue."""
        queue_item = {
            "data_id": data_id,
            "added_at": datetime.now().isoformat(),
            "priority": priority,
            "status": "pending"
        }
        
        self.annotation_queue.append(queue_item)
        self._save_annotation_queue()
        
        logger.info(f"Added {data_id} to annotation queue")
    
    def get_next_for_annotation(self) -> Optional[Dict]:
        """Get the next item for annotation from the queue."""
        # Sort by priority (higher first) and timestamp (older first)
        pending_items = [item for item in self.annotation_queue if item["status"] == "pending"]
        
        if not pending_items:
            return None
        
        sorted_items = sorted(
            pending_items,
            key=lambda x: (-x["priority"], x["added_at"])
        )
        
        if sorted_items:
            next_item = sorted_items[0]
            
            # Load the data
            data_file = self.raw_dir / f"{next_item['data_id']}.json"
            if data_file.exists():
                try:
                    with open(data_file, 'r') as f:
                        data = json.load(f)
                    
                    # Mark as in_progress
                    for item in self.annotation_queue:
                        if item["data_id"] == next_item["data_id"]:
                            item["status"] = "in_progress"
                            item["started_at"] = datetime.now().isoformat()
                            break
                    
                    self._save_annotation_queue()
                    return data
                    
                except Exception as e:
                    logger.error(f"Error loading data {next_item['data_id']}: {e}")
        
        return None
    
    def create_annotation(
        self,
        data_id: str,
        annotator_id: str,
        annotations: Dict[str, Any]
    ) -> bool:
        """
        Create an annotation for a data sample.
        
        Args:
            data_id: ID of the data to annotate
            annotator_id: ID of the annotator (anonymized)
            annotations: Dictionary of annotations following the schema
            
        Returns:
            Success status
        """
        # Validate annotations against schema
        if not self._validate_annotations(annotations):
            logger.error("Invalid annotations format")
            return False
        
        # Load original data
        data_file = self.raw_dir / f"{data_id}.json"
        if not data_file.exists():
            logger.error(f"Data file not found: {data_id}")
            return False
        
        try:
            with open(data_file, 'r') as f:
                original_data = json.load(f)
            
            # Create annotated data
            annotated_data = {
                "data_id": data_id,
                "original_data": original_data,
                "annotations": annotations,
                "annotator_id": annotator_id,
                "annotated_at": datetime.now().isoformat(),
                "annotation_version": "1.0"
            }
            
            # Add computed features
            annotated_data["computed_features"] = self._compute_annotation_features(
                original_data["landmarks_sequence"],
                annotations
            )
            
            # Save annotated data
            annotated_file = self.annotated_dir / f"{data_id}_annotated.json"
            with open(annotated_file, 'w') as f:
                json.dump(annotated_data, f, indent=2)
            
            # Update queue status
            for item in self.annotation_queue:
                if item["data_id"] == data_id:
                    item["status"] = "completed"
                    item["completed_at"] = datetime.now().isoformat()
                    break
            
            self._save_annotation_queue()
            
            logger.info(f"Created annotation for {data_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating annotation: {e}")
            return False
    
    def _validate_annotations(self, annotations: Dict[str, Any]) -> bool:
        """Validate annotations against the schema."""
        try:
            # Check form quality scores
            if "form_quality" in annotations:
                for key, value in annotations["form_quality"].items():
                    if key not in self.annotation_schema["form_quality"]:
                        return False
                    if not isinstance(value, (int, float)):
                        return False
                    if not 0 <= value <= 100:
                        return False
            
            # Check phase labels
            if "phase_labels" in annotations:
                for key, value in annotations["phase_labels"].items():
                    if key not in self.annotation_schema["phase_labels"]:
                        return False
                    if not isinstance(value, bool):
                        return False
            
            # Check common errors
            if "common_errors" in annotations:
                for key, value in annotations["common_errors"].items():
                    if key not in self.annotation_schema["common_errors"]:
                        return False
                    if not isinstance(value, bool):
                        return False
            
            # Check corrections
            if "corrections" in annotations:
                if not isinstance(annotations["corrections"], list):
                    return False
                for correction in annotations["corrections"]:
                    if not isinstance(correction, str):
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False
    
    def _compute_annotation_features(
        self,
        landmarks_sequence: List[List[Dict]],
        annotations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compute additional features from annotations and landmarks."""
        features = {}
        
        # Compute error timing
        if "common_errors" in annotations:
            error_frames = {}
            for error, present in annotations["common_errors"].items():
                if present:
                    # Simple heuristic: errors likely occur in middle frames
                    # In production, this would be more sophisticated
                    total_frames = len(landmarks_sequence)
                    error_frames[error] = {
                        "start_frame": int(total_frames * 0.3),
                        "end_frame": int(total_frames * 0.7),
                        "severity": "medium"  # Could be computed from landmarks
                    }
            
            features["error_timing"] = error_frames
        
        # Compute phase boundaries
        if "phase_labels" in annotations:
            # Simple phase detection based on frames
            # In production, this would use the actual phase detector
            total_frames = len(landmarks_sequence)
            phase_boundaries = {}
            
            if annotations["phase_labels"].get("setup", False):
                phase_boundaries["setup"] = [0, int(total_frames * 0.1)]
            if annotations["phase_labels"].get("descent", False):
                phase_boundaries["descent"] = [int(total_frames * 0.1), int(total_frames * 0.4)]
            if annotations["phase_labels"].get("bottom", False):
                phase_boundaries["bottom"] = [int(total_frames * 0.4), int(total_frames * 0.5)]
            if annotations["phase_labels"].get("ascent", False):
                phase_boundaries["ascent"] = [int(total_frames * 0.5), int(total_frames * 0.9)]
            if annotations["phase_labels"].get("lockout", False):
                phase_boundaries["lockout"] = [int(total_frames * 0.9), total_frames]
            
            features["phase_boundaries"] = phase_boundaries
        
        # Aggregate quality score
        if "form_quality" in annotations:
            quality_scores = list(annotations["form_quality"].values())
            features["aggregate_quality"] = {
                "mean": np.mean(quality_scores),
                "std": np.std(quality_scores),
                "min": np.min(quality_scores),
                "max": np.max(quality_scores)
            }
        
        return features
    
    def get_annotation_stats(self) -> Dict[str, Any]:
        """Get statistics about annotations."""
        stats = {
            "total_queued": len(self.annotation_queue),
            "pending": sum(1 for item in self.annotation_queue if item["status"] == "pending"),
            "in_progress": sum(1 for item in self.annotation_queue if item["status"] == "in_progress"),
            "completed": sum(1 for item in self.annotation_queue if item["status"] == "completed"),
            "annotated_files": len(list(self.annotated_dir.glob("*_annotated.json"))),
            "quality_distribution": {},
            "common_errors_frequency": {}
        }
        
        # Analyze annotated files
        for annotated_file in self.annotated_dir.glob("*_annotated.json"):
            try:
                with open(annotated_file, 'r') as f:
                    data = json.load(f)
                
                # Quality distribution
                if "computed_features" in data and "aggregate_quality" in data["computed_features"]:
                    mean_quality = data["computed_features"]["aggregate_quality"]["mean"]
                    quality_bucket = int(mean_quality / 10) * 10
                    stats["quality_distribution"][quality_bucket] = \
                        stats["quality_distribution"].get(quality_bucket, 0) + 1
                
                # Error frequency
                if "annotations" in data and "common_errors" in data["annotations"]:
                    for error, present in data["annotations"]["common_errors"].items():
                        if present:
                            stats["common_errors_frequency"][error] = \
                                stats["common_errors_frequency"].get(error, 0) + 1
                
            except Exception as e:
                logger.error(f"Error analyzing {annotated_file}: {e}")
        
        return stats
    
    def export_training_data(
        self,
        output_path: str,
        min_quality: float = 60.0,
        required_annotations: Optional[List[str]] = None
    ) -> int:
        """
        Export annotated data for model training.
        
        Args:
            output_path: Path to save training data
            min_quality: Minimum quality score to include
            required_annotations: Required annotation fields
            
        Returns:
            Number of samples exported
        """
        training_data = []
        
        for annotated_file in self.annotated_dir.glob("*_annotated.json"):
            try:
                with open(annotated_file, 'r') as f:
                    data = json.load(f)
                
                # Check quality threshold
                if "computed_features" in data and "aggregate_quality" in data["computed_features"]:
                    if data["computed_features"]["aggregate_quality"]["mean"] < min_quality:
                        continue
                
                # Check required annotations
                if required_annotations:
                    annotations = data.get("annotations", {})
                    if not all(field in annotations for field in required_annotations):
                        continue
                
                # Extract training sample
                sample = {
                    "data_id": data["data_id"],
                    "exercise_type": data["original_data"]["exercise_type"],
                    "landmarks_sequence": data["original_data"]["landmarks_sequence"],
                    "labels": {
                        "form_quality": data["annotations"].get("form_quality", {}),
                        "common_errors": data["annotations"].get("common_errors", {}),
                        "phase_boundaries": data["computed_features"].get("phase_boundaries", {})
                    },
                    "metadata": {
                        "quality_score": data["computed_features"]["aggregate_quality"]["mean"],
                        "annotated_at": data["annotated_at"]
                    }
                }
                
                training_data.append(sample)
                
            except Exception as e:
                logger.error(f"Error processing {annotated_file}: {e}")
        
        # Save training data
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump({
                    "dataset_version": "1.0",
                    "exported_at": datetime.now().isoformat(),
                    "sample_count": len(training_data),
                    "min_quality": min_quality,
                    "required_annotations": required_annotations,
                    "samples": training_data
                }, f, indent=2)
            
            logger.info(f"Exported {len(training_data)} training samples to {output_path}")
            return len(training_data)
            
        except Exception as e:
            logger.error(f"Error exporting training data: {e}")
            return 0


# Helper class for interactive annotation
class InteractiveAnnotator:
    """Helper class for interactive annotation sessions."""
    
    def __init__(self, annotation_tool: ExerciseAnnotationTool):
        self.tool = annotation_tool
        self.current_data = None
        self.current_annotations = {}
    
    def start_session(self) -> bool:
        """Start a new annotation session."""
        self.current_data = self.tool.get_next_for_annotation()
        if self.current_data:
            self.current_annotations = {
                "form_quality": {},
                "phase_labels": {},
                "common_errors": {},
                "corrections": [],
                "rep_quality": []
            }
            return True
        return False
    
    def add_form_quality_score(self, aspect: str, score: float):
        """Add a form quality score."""
        if aspect in self.tool.annotation_schema["form_quality"]:
            self.current_annotations["form_quality"][aspect] = score
    
    def toggle_phase_label(self, phase: str):
        """Toggle a phase label."""
        if phase in self.tool.annotation_schema["phase_labels"]:
            current = self.current_annotations["phase_labels"].get(phase, False)
            self.current_annotations["phase_labels"][phase] = not current
    
    def toggle_error(self, error: str):
        """Toggle an error flag."""
        if error in self.tool.annotation_schema["common_errors"]:
            current = self.current_annotations["common_errors"].get(error, False)
            self.current_annotations["common_errors"][error] = not current
    
    def add_correction(self, correction: str):
        """Add a correction advice."""
        self.current_annotations["corrections"].append(correction)
    
    def save_annotation(self, annotator_id: str) -> bool:
        """Save the current annotation."""
        if self.current_data and self.current_annotations:
            return self.tool.create_annotation(
                self.current_data["data_id"],
                annotator_id,
                self.current_annotations
            )
        return False
    
    def get_progress(self) -> Dict[str, int]:
        """Get annotation progress for current session."""
        if not self.current_annotations:
            return {"total_fields": 0, "completed_fields": 0}
        
        total_fields = (
            len(self.tool.annotation_schema["form_quality"]) +
            len(self.tool.annotation_schema["phase_labels"]) +
            len(self.tool.annotation_schema["common_errors"])
        )
        
        completed_fields = (
            len(self.current_annotations.get("form_quality", {})) +
            len(self.current_annotations.get("phase_labels", {})) +
            len(self.current_annotations.get("common_errors", {}))
        )
        
        return {
            "total_fields": total_fields,
            "completed_fields": completed_fields,
            "completion_percentage": int((completed_fields / total_fields) * 100) if total_fields > 0 else 0
        }