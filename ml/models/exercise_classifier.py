"""
Exercise classifier for identifying exercise types from pose landmarks.
Implements both rule-based and ML-based classification.
"""

import numpy as np
from typing import List, Dict, Optional, Tuple, Any
import logging
import os
from datetime import datetime

# Optional ML imports
try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    import joblib
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logging.warning("scikit-learn not available. Using rule-based classifier only.")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExerciseClassifier:
    """Classifies exercises based on pose landmarks."""
    
    def __init__(self, use_ml: bool = True):
        """
        Initialize the exercise classifier.
        
        Args:
            use_ml: Whether to use ML model if available
        """
        self.use_ml = use_ml and ML_AVAILABLE
        self.model = None
        self.scaler = None
        self.model_path = "ml/models/exercise_classifier_model.pkl"
        
        if self.use_ml:
            try:
                self.load_model()
            except:
                logger.info("No pre-trained model found. Using rule-based classification.")
                self._initialize_ml_model()
    
    def _initialize_ml_model(self):
        """Initialize ML model and scaler."""
        if ML_AVAILABLE:
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            self.scaler = StandardScaler()
    
    def classify_exercise(self, landmarks: List[List[float]]) -> Dict[str, Any]:
        """
        Classify exercise type from pose landmarks.
        
        Args:
            landmarks: 33x3 array of pose landmarks (MediaPipe format)
            
        Returns:
            Dictionary with exercise type and confidence
        """
        if not landmarks or len(landmarks) != 33:
            return {"exercise": "unknown", "confidence": 0.0}
        
        # Convert to numpy array
        landmarks = np.array(landmarks)
        
        # Extract features
        features = self._extract_features(landmarks)
        
        # Try ML classification first if available
        if self.use_ml and self.model is not None:
            try:
                return self._ml_classify(features)
            except:
                logger.warning("ML classification failed, falling back to rules")
        
        # Fall back to rule-based classification
        return self._rule_based_classify(features)
    
    def _extract_features(self, landmarks: np.ndarray) -> Dict[str, float]:
        """
        Extract relevant features from landmarks.
        
        Args:
            landmarks: 33x3 array of pose landmarks
            
        Returns:
            Dictionary of features
        """
        features = {}
        
        # Key landmark indices (MediaPipe)
        LEFT_SHOULDER = 11
        RIGHT_SHOULDER = 12
        LEFT_HIP = 23
        RIGHT_HIP = 24
        LEFT_KNEE = 25
        RIGHT_KNEE = 26
        LEFT_ANKLE = 27
        RIGHT_ANKLE = 28
        LEFT_ELBOW = 13
        RIGHT_ELBOW = 14
        LEFT_WRIST = 15
        RIGHT_WRIST = 16
        
        # Calculate joint angles
        features['left_knee_angle'] = self._calculate_angle(
            landmarks[LEFT_HIP],
            landmarks[LEFT_KNEE],
            landmarks[LEFT_ANKLE]
        )
        features['right_knee_angle'] = self._calculate_angle(
            landmarks[RIGHT_HIP],
            landmarks[RIGHT_KNEE],
            landmarks[RIGHT_ANKLE]
        )
        
        # Hip angle (for deadlift detection)
        features['left_hip_angle'] = self._calculate_angle(
            landmarks[LEFT_SHOULDER],
            landmarks[LEFT_HIP],
            landmarks[LEFT_KNEE]
        )
        features['right_hip_angle'] = self._calculate_angle(
            landmarks[RIGHT_SHOULDER],
            landmarks[RIGHT_HIP],
            landmarks[RIGHT_KNEE]
        )
        
        # Elbow angles (for bench press)
        features['left_elbow_angle'] = self._calculate_angle(
            landmarks[LEFT_SHOULDER],
            landmarks[LEFT_ELBOW],
            landmarks[LEFT_WRIST]
        )
        features['right_elbow_angle'] = self._calculate_angle(
            landmarks[RIGHT_SHOULDER],
            landmarks[RIGHT_ELBOW],
            landmarks[RIGHT_WRIST]
        )
        
        # Body positions
        features['hip_height'] = (landmarks[LEFT_HIP][1] + landmarks[RIGHT_HIP][1]) / 2
        features['shoulder_height'] = (landmarks[LEFT_SHOULDER][1] + landmarks[RIGHT_SHOULDER][1]) / 2
        features['knee_height'] = (landmarks[LEFT_KNEE][1] + landmarks[RIGHT_KNEE][1]) / 2
        
        # Body orientation (lying down detection for bench press)
        torso_vertical = abs(features['shoulder_height'] - features['hip_height'])
        features['torso_vertical_ratio'] = torso_vertical
        
        # Knee position relative to hip (for squat form)
        features['knee_forward_distance'] = (
            (landmarks[LEFT_KNEE][2] + landmarks[RIGHT_KNEE][2]) / 2 -
            (landmarks[LEFT_HIP][2] + landmarks[RIGHT_HIP][2]) / 2
        )
        
        return features
    
    def _calculate_angle(self, p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> float:
        """
        Calculate angle between three points.
        
        Args:
            p1, p2, p3: 3D points where p2 is the vertex
            
        Returns:
            Angle in degrees
        """
        v1 = p1 - p2
        v2 = p3 - p2
        
        # Calculate angle using dot product
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
        angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))
        
        return np.degrees(angle)
    
    def _rule_based_classify(self, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Rule-based exercise classification.
        
        Args:
            features: Extracted features
            
        Returns:
            Classification result
        """
        # Average angles
        avg_knee_angle = (features['left_knee_angle'] + features['right_knee_angle']) / 2
        avg_hip_angle = (features['left_hip_angle'] + features['right_hip_angle']) / 2
        avg_elbow_angle = (features['left_elbow_angle'] + features['right_elbow_angle']) / 2
        
        # Check for bench press (lying position)
        if features['torso_vertical_ratio'] < 0.3 and features['shoulder_height'] > features['hip_height']:
            # Person is likely lying down
            if avg_elbow_angle < 160:  # Arms are bent
                return {"exercise": "bench_press", "confidence": 0.85}
        
        # Check for squat
        if avg_knee_angle < 120 and avg_hip_angle < 160:
            # Deep knee bend with moderate hip bend
            if features['knee_forward_distance'] > 0:  # Knees forward of hips
                return {"exercise": "squat", "confidence": 0.90}
        
        # Check for deadlift
        if avg_hip_angle < 90 and avg_knee_angle > 120:
            # Significant hip hinge with relatively straight knees
            return {"exercise": "deadlift", "confidence": 0.85}
        
        # Default to unknown
        return {"exercise": "unknown", "confidence": 0.3}
    
    def _ml_classify(self, features: Dict[str, float]) -> Dict[str, Any]:
        """
        ML-based classification.
        
        Args:
            features: Extracted features
            
        Returns:
            Classification result
        """
        # Convert features to array
        feature_array = np.array([list(features.values())])
        
        # Scale features
        if hasattr(self, 'scaler') and self.scaler is not None:
            feature_array = self.scaler.transform(feature_array)
        
        # Predict
        prediction = self.model.predict(feature_array)[0]
        probabilities = self.model.predict_proba(feature_array)[0]
        confidence = float(np.max(probabilities))
        
        return {"exercise": prediction, "confidence": confidence}
    
    def train_model(self, training_data: List[Tuple[np.ndarray, str]]):
        """
        Train the ML model with labeled data.
        
        Args:
            training_data: List of (landmarks, exercise_type) tuples
        """
        if not ML_AVAILABLE:
            logger.warning("ML not available for training")
            return
        
        # Extract features and labels
        X = []
        y = []
        
        for landmarks, exercise_type in training_data:
            features = self._extract_features(landmarks)
            X.append(list(features.values()))
            y.append(exercise_type)
        
        X = np.array(X)
        y = np.array(y)
        
        # Initialize model if needed
        if self.model is None:
            self._initialize_ml_model()
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)
        logger.info(f"Model trained on {len(X)} samples")
        
        # Save model
        self.save_model()
    
    def save_model(self):
        """Save the trained model."""
        if not ML_AVAILABLE or self.model is None:
            return
        
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'timestamp': datetime.now().isoformat()
        }
        
        joblib.dump(model_data, self.model_path)
        logger.info(f"Model saved to {self.model_path}")
    
    def load_model(self):
        """Load a pre-trained model."""
        if not ML_AVAILABLE or not os.path.exists(self.model_path):
            return
        
        model_data = joblib.load(self.model_path)
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        logger.info(f"Model loaded from {self.model_path}")


# Batch classification for multiple frames
def classify_exercise_sequence(
    landmark_sequence: List[List[List[float]]],
    classifier: Optional[ExerciseClassifier] = None
) -> Dict[str, Any]:
    """
    Classify exercise from a sequence of frames.
    
    Args:
        landmark_sequence: List of landmark arrays (one per frame)
        classifier: Optional pre-initialized classifier
        
    Returns:
        Most likely exercise type with confidence
    """
    if classifier is None:
        classifier = ExerciseClassifier()
    
    # Classify each frame
    classifications = []
    for landmarks in landmark_sequence:
        result = classifier.classify_exercise(landmarks)
        if result['exercise'] != 'unknown':
            classifications.append(result)
    
    if not classifications:
        return {"exercise": "unknown", "confidence": 0.0}
    
    # Aggregate results (majority vote)
    exercise_counts = {}
    total_confidence = {}
    
    for cls in classifications:
        exercise = cls['exercise']
        confidence = cls['confidence']
        
        if exercise not in exercise_counts:
            exercise_counts[exercise] = 0
            total_confidence[exercise] = 0
        
        exercise_counts[exercise] += 1
        total_confidence[exercise] += confidence
    
    # Find most common exercise
    most_common = max(exercise_counts.items(), key=lambda x: x[1])
    exercise_type = most_common[0]
    avg_confidence = total_confidence[exercise_type] / exercise_counts[exercise_type]
    
    return {
        "exercise": exercise_type,
        "confidence": avg_confidence,
        "frame_count": len(classifications),
        "consensus_ratio": exercise_counts[exercise_type] / len(classifications)
    }


if __name__ == "__main__":
    # Test the classifier
    classifier = ExerciseClassifier(use_ml=False)
    
    # Test data: simulate squat position
    test_landmarks = np.zeros((33, 3))
    # Set some key positions for squat
    test_landmarks[11] = [0.4, 0.3, 0]  # left shoulder
    test_landmarks[12] = [0.6, 0.3, 0]  # right shoulder
    test_landmarks[23] = [0.45, 0.6, 0]  # left hip
    test_landmarks[24] = [0.55, 0.6, 0]  # right hip
    test_landmarks[25] = [0.44, 0.8, 0.1]  # left knee (forward)
    test_landmarks[26] = [0.56, 0.8, 0.1]  # right knee (forward)
    test_landmarks[27] = [0.43, 0.95, 0]  # left ankle
    test_landmarks[28] = [0.57, 0.95, 0]  # right ankle
    
    result = classifier.classify_exercise(test_landmarks.tolist())
    print(f"Classification result: {result}")