# core/__init__.py
"""
TENAX FIT v3.0 Core Engines
科学的フィットネス分析のコアモジュール
"""

# Existing modules
from .analyzer import Analyzer
from .scaler import Scaler
from .json_manager import JsonManager
from .database import Database

# v3.0 Scientific Engines
from .body_composition_engine import BodyCompositionEngine
from .training_engine import TrainingEngine
from .safety_engine import SafetyEngine

__all__ = [
    # Existing
    'Analyzer',
    'Scaler',
    'JsonManager',
    'Database',
    # v3.0
    'BodyCompositionEngine',
    'TrainingEngine',
    'SafetyEngine'
]

__version__ = '3.0.0'