"""
Environment configuration loader for BodyScale Pose Analyzer.
Centralizes all environment variable access with defaults and validation.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional, List
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
env_file = Path('.env')
if not env_file.exists():
    env_file = Path('.env.local')
if env_file.exists():
    load_dotenv(env_file)

logger = logging.getLogger(__name__)


class EnvironmentConfig:
    """Centralized environment configuration."""
    
    def __init__(self):
        self._cache = {}
        self._validate_required_vars()
    
    def _validate_required_vars(self):
        """Validate that required environment variables are set."""
        required_vars = []  # Add any required vars here
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.warning(f"Missing environment variables: {', '.join(missing_vars)}")
    
    def get(self, key: str, default: Any = None, cast_type: type = str) -> Any:
        """
        Get environment variable with caching and type casting.
        
        Args:
            key: Environment variable name
            default: Default value if not found
            cast_type: Type to cast the value to
            
        Returns:
            Environment variable value
        """
        if key in self._cache:
            return self._cache[key]
        
        value = os.getenv(key, default)
        
        # Type casting
        if value is not None and cast_type != str:
            try:
                if cast_type == bool:
                    value = value.lower() in ('true', '1', 'yes', 'on')
                elif cast_type == int:
                    value = int(value)
                elif cast_type == float:
                    value = float(value)
                elif cast_type == list:
                    value = [v.strip() for v in value.split(',')]
            except (ValueError, AttributeError):
                logger.error(f"Failed to cast {key}={value} to {cast_type}")
                value = default
        
        self._cache[key] = value
        return value
    
    # === Server Configuration ===
    @property
    def flask_env(self) -> str:
        return self.get('FLASK_ENV', 'production')
    
    @property
    def is_development(self) -> bool:
        return self.flask_env == 'development'
    
    @property
    def flask_debug(self) -> bool:
        return self.get('FLASK_DEBUG', False, bool)
    
    @property
    def host(self) -> str:
        return self.get('HOST', '0.0.0.0')
    
    @property
    def port(self) -> int:
        return self.get('PORT', 5000, int)
    
    @property
    def backend_url(self) -> str:
        return self.get('BACKEND_URL', f'http://localhost:{self.port}')
    
    @property
    def frontend_url(self) -> str:
        return self.get('FRONTEND_URL', 'http://localhost:3000')
    
    @property
    def session_secret(self) -> str:
        return self.get('SESSION_SECRET', 'dev-secret-key-change-in-production')
    
    # === ML Model Configuration ===
    @property
    def model_mode(self) -> str:
        """Get model mode: 'lite' or 'advanced'."""
        return self.get('MODEL_MODE', 'lite')
    
    @property
    def is_advanced_mode(self) -> bool:
        """Check if running in advanced mode."""
        return self.model_mode == 'advanced'
    
    @property
    def use_3d_pose(self) -> bool:
        return self.get('USE_3D_POSE', False, bool) and self.is_advanced_mode
    
    @property
    def use_motion_analysis(self) -> bool:
        return self.get('USE_MOTION_ANALYSIS', False, bool) and self.is_advanced_mode
    
    @property
    def use_personalization(self) -> bool:
        return self.get('USE_PERSONALIZATION', False, bool) and self.is_advanced_mode
    
    @property
    def ml_models_path(self) -> str:
        return self.get('ML_MODELS_PATH', './ml/models')
    
    # === Pose Detection Settings ===
    @property
    def pose_model_complexity(self) -> int:
        return self.get('POSE_MODEL_COMPLEXITY', 1, int)
    
    @property
    def min_detection_confidence(self) -> float:
        return self.get('MIN_DETECTION_CONFIDENCE', 0.7, float)
    
    @property
    def min_tracking_confidence(self) -> float:
        return self.get('MIN_TRACKING_CONFIDENCE', 0.7, float)
    
    @property
    def smooth_landmarks(self) -> bool:
        return self.get('SMOOTH_LANDMARKS', True, bool)
    
    @property
    def max_fps(self) -> int:
        return self.get('MAX_FPS', 30, int)
    
    @property
    def video_width(self) -> int:
        return self.get('VIDEO_WIDTH', 1280, int)
    
    @property
    def video_height(self) -> int:
        return self.get('VIDEO_HEIGHT', 720, int)
    
    # === Data Collection Settings ===
    @property
    def enable_data_collection(self) -> bool:
        return self.get('ENABLE_DATA_COLLECTION', False, bool)
    
    @property
    def data_collection_consent_required(self) -> bool:
        return self.get('DATA_COLLECTION_CONSENT_REQUIRED', True, bool)
    
    @property
    def data_retention_days(self) -> int:
        return self.get('DATA_RETENTION_DAYS', 365, int)
    
    @property
    def data_storage_path(self) -> str:
        return self.get('DATA_STORAGE_PATH', './ml/data')
    
    @property
    def anonymize_user_data(self) -> bool:
        return self.get('ANONYMIZE_USER_DATA', True, bool)
    
    @property
    def min_quality_score_for_collection(self) -> float:
        return self.get('MIN_QUALITY_SCORE_FOR_COLLECTION', 0.6, float)
    
    # === Feature Flags ===
    @property
    def enable_meal_analysis(self) -> bool:
        return self.get('ENABLE_MEAL_ANALYSIS', True, bool)
    
    @property
    def enable_exercise_database(self) -> bool:
        return self.get('ENABLE_EXERCISE_DATABASE', True, bool)
    
    @property
    def enable_phase_detection(self) -> bool:
        return self.get('ENABLE_PHASE_DETECTION', True, bool)
    
    @property
    def enable_advanced_feedback(self) -> bool:
        return self.get('ENABLE_ADVANCED_FEEDBACK', True, bool)
    
    @property
    def enable_real_time_analysis(self) -> bool:
        return self.get('ENABLE_REAL_TIME_ANALYSIS', True, bool)
    
    # === UI/UX Settings ===
    @property
    def show_confidence_scores(self) -> bool:
        return self.get('SHOW_CONFIDENCE_SCORES', True, bool)
    
    @property
    def show_processing_time(self) -> bool:
        return self.get('SHOW_PROCESSING_TIME', False, bool)
    
    @property
    def camera_guide_enabled(self) -> bool:
        return self.get('CAMERA_GUIDE_ENABLED', True, bool)
    
    # === Privacy Settings ===
    @property
    def blur_faces_in_recordings(self) -> bool:
        return self.get('BLUR_FACES_IN_RECORDINGS', False, bool)
    
    @property
    def save_analysis_frames(self) -> bool:
        return self.get('SAVE_ANALYSIS_FRAMES', False, bool)
    
    @property
    def delete_videos_after_analysis(self) -> bool:
        return self.get('DELETE_VIDEOS_AFTER_ANALYSIS', True, bool)
    
    # === File Upload Settings ===
    @property
    def upload_folder(self) -> str:
        return self.get('UPLOAD_FOLDER', './static/videos')
    
    @property
    def max_content_length(self) -> int:
        return self.get('MAX_CONTENT_LENGTH', 52428800, int)  # 50MB
    
    @property
    def allowed_extensions(self) -> List[str]:
        return self.get('ALLOWED_EXTENSIONS', 'mp4,mov,avi,webm', list)
    
    # === Logging Configuration ===
    @property
    def log_level(self) -> str:
        return self.get('LOG_LEVEL', 'INFO')
    
    @property
    def log_file(self) -> str:
        return self.get('LOG_FILE', './logs/bodyscale_analyzer.log')
    
    # === Performance Settings ===
    @property
    def cache_analysis_results(self) -> bool:
        return self.get('CACHE_ANALYSIS_RESULTS', True, bool)
    
    @property
    def cache_ttl_seconds(self) -> int:
        return self.get('CACHE_TTL_SECONDS', 300, int)
    
    @property
    def parallel_processing(self) -> bool:
        return self.get('PARALLEL_PROCESSING', True, bool)
    
    @property
    def max_workers(self) -> int:
        return self.get('MAX_WORKERS', 4, int)
    
    # === CORS Configuration ===
    @property
    def cors_origins(self) -> List[str]:
        return self.get('CORS_ORIGINS', 'http://localhost:3000,http://localhost:3001', list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Export all configuration as dictionary."""
        return {
            'model_mode': self.model_mode,
            'is_development': self.is_development,
            'enable_data_collection': self.enable_data_collection,
            'enable_advanced_feedback': self.enable_advanced_feedback,
            'show_confidence_scores': self.show_confidence_scores,
            'camera_guide_enabled': self.camera_guide_enabled,
            'features': {
                'meal_analysis': self.enable_meal_analysis,
                'exercise_database': self.enable_exercise_database,
                'phase_detection': self.enable_phase_detection,
                'real_time_analysis': self.enable_real_time_analysis,
            },
            'ml_settings': {
                'model_complexity': self.pose_model_complexity,
                'detection_confidence': self.min_detection_confidence,
                'tracking_confidence': self.min_tracking_confidence,
            },
            'privacy': {
                'anonymize_data': self.anonymize_user_data,
                'blur_faces': self.blur_faces_in_recordings,
                'delete_videos': self.delete_videos_after_analysis,
            }
        }


# Singleton instance
_config_instance = None

def get_config() -> EnvironmentConfig:
    """Get singleton environment configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = EnvironmentConfig()
    return _config_instance


# Convenience access
config = get_config()