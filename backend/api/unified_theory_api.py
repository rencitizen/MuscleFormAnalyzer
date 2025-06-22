"""API endpoints for Unified Theory-based form analysis."""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional
import numpy as np
import cv2
import base64
import logging
from datetime import datetime

from backend.services.unified_theory_service import UnifiedTheoryService
from backend.utils.auth import get_current_user
from backend.models.analysis import AnalysisSession
from backend.database import SessionLocal

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v3", tags=["unified-theory"])

# Service instance
unified_service = UnifiedTheoryService()


@router.post("/analyze-frame")
async def analyze_frame(
    frame_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Analyze a single frame using unified theory principles.
    
    Args:
        frame_data: Contains base64 encoded frame, user profile, exercise type, and calibration
        current_user: Authenticated user
        
    Returns:
        Comprehensive unified theory analysis results
    """
    try:
        # Extract data
        frame_base64 = frame_data.get('frameData')
        user_profile = frame_data.get('userProfile', {})
        exercise_type = frame_data.get('exerciseType', 'squat')
        calibration_data = frame_data.get('calibrationData')
        
        if not frame_base64:
            raise HTTPException(status_code=400, detail="Frame data is required")
            
        # Decode frame
        frame_bytes = base64.b64decode(frame_base64.split(',')[1] if ',' in frame_base64 else frame_base64)
        nparr = np.frombuffer(frame_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image data")
            
        # Perform unified analysis
        result = await unified_service.analyze_frame_unified(
            frame, exercise_type, user_profile, calibration_data
        )
        
        # Convert annotated frame to base64 if present
        if 'annotated_frame' in result and result['annotated_frame'] is not None:
            _, buffer = cv2.imencode('.jpg', result['annotated_frame'])
            result['annotated_frame'] = base64.b64encode(buffer).decode('utf-8')
            
        return result
        
    except Exception as e:
        logger.error(f"Error in unified frame analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/unified-theory-assessment")
async def unified_theory_assessment(
    assessment_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Perform comprehensive unified theory assessment on movement sequence.
    
    Args:
        assessment_data: Movement sequence data, exercise type, and user profile
        current_user: Authenticated user
        
    Returns:
        Detailed unified theory assessment
    """
    try:
        movement_sequence = assessment_data.get('movementSequence', [])
        exercise_type = assessment_data.get('exerciseType', 'squat')
        user_profile = assessment_data.get('userProfile', {})
        
        if not movement_sequence:
            raise HTTPException(status_code=400, detail="Movement sequence is required")
            
        # Convert movement sequence to frames if needed
        frames = []
        for item in movement_sequence:
            if isinstance(item, str):  # Base64 encoded frame
                frame_bytes = base64.b64decode(item.split(',')[1] if ',' in item else item)
                nparr = np.frombuffer(frame_bytes, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                frames.append(frame)
            elif isinstance(item, dict) and 'frameData' in item:
                # Already analyzed frame data
                continue
                
        # Analyze sequence
        if frames:
            result = await unified_service.analyze_movement_sequence(
                frames, exercise_type, user_profile
            )
        else:
            # Aggregate existing analysis results
            result = unified_service._aggregate_sequence_results(
                movement_sequence, exercise_type
            )
            
        # Calculate detailed analysis
        detailed_analysis = {
            'physicsCompliance': {
                'score': result.get('average_scores', {}).get('physics_efficiency', 0),
                'details': 'Energy efficiency and biomechanical optimization'
            },
            'biologicalEfficiency': {
                'score': result.get('average_scores', {}).get('biological_optimality', 0),
                'details': 'Neuromuscular coordination and movement quality'
            },
            'systemOptimization': {
                'score': result.get('average_scores', {}).get('system_stability', 0),
                'details': 'Movement stability and adaptability'
            },
            'mathematicalOptimality': {
                'score': result.get('average_scores', {}).get('mathematical_optimization', 0),
                'details': 'Optimal form based on individual constraints'
            }
        }
        
        # Generate personalized recommendations
        recommendations = _generate_personalized_recommendations(
            result, user_profile, exercise_type
        )
        
        # Track progress
        progress_tracking = _calculate_progress_tracking(
            unified_service.analysis_results_history, exercise_type
        )
        
        return {
            'overallScore': result.get('average_scores', {}).get('overall', 0),
            'detailedAnalysis': detailed_analysis,
            'personalizedRecommendations': recommendations,
            'progressTracking': progress_tracking,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in unified theory assessment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/unified-scores/{session_id}")
async def get_unified_scores(
    session_id: str,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get unified theory scores for a specific session.
    
    Args:
        session_id: Analysis session ID
        current_user: Authenticated user
        
    Returns:
        Unified theory scores for the session
    """
    try:
        db = SessionLocal()
        
        # Get session
        session = db.query(AnalysisSession).filter(
            AnalysisSession.id == session_id,
            AnalysisSession.user_id == current_user['uid']
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
            
        # Extract unified scores from session data
        if session.analysis_data and 'unified_scores' in session.analysis_data:
            return {
                'session_id': session_id,
                'exercise_type': session.exercise_type,
                'unified_scores': session.analysis_data['unified_scores'],
                'timestamp': session.created_at.isoformat()
            }
        else:
            return {
                'session_id': session_id,
                'exercise_type': session.exercise_type,
                'unified_scores': {
                    'physics_efficiency': 0,
                    'biological_optimality': 0,
                    'system_stability': 0,
                    'mathematical_optimization': 0,
                    'overall': 0
                },
                'timestamp': session.created_at.isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error fetching unified scores: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.post("/calculate-optimal-form")
async def calculate_optimal_form(
    form_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Calculate personalized optimal form based on user constraints.
    
    Args:
        form_data: Current form data and user profile
        current_user: Authenticated user
        
    Returns:
        Optimal form recommendations
    """
    try:
        current_angles = form_data.get('currentJointAngles', {})
        user_profile = form_data.get('userProfile', {})
        exercise_type = form_data.get('exerciseType', 'squat')
        
        # Initialize optimization engine
        optimization_engine = unified_service.optimization_engine
        
        # Define objectives
        objectives = optimization_engine.define_objective_functions(user_profile)
        
        # Apply constraints
        user_measurements = user_profile.get('physicalMeasurements', {})
        constraints = optimization_engine.apply_constraints(user_measurements)
        
        # Solve for optimal form
        optimal_form = optimization_engine.solve_form_optimization(
            current_angles, constraints, exercise_type
        )
        
        # Calculate improvement path
        improvement_path = optimization_engine.generate_personalized_path(
            current_angles, optimal_form, time_steps=10
        )
        
        # Get improvement priorities
        priorities = optimization_engine.calculate_improvement_priority(
            current_angles, optimal_form, user_profile
        )
        
        return {
            'currentForm': current_angles,
            'optimalForm': optimal_form.joint_angles,
            'improvementPriorities': priorities[:5],  # Top 5
            'improvementPath': improvement_path,
            'constraintsSatisfied': optimal_form.constraint_satisfaction,
            'optimizationScore': optimal_form.overall_score,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error calculating optimal form: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def _generate_personalized_recommendations(result: Dict[str, Any],
                                         user_profile: Dict[str, Any],
                                         exercise_type: str) -> List[str]:
    """Generate personalized recommendations based on analysis."""
    recommendations = []
    
    avg_scores = result.get('average_scores', {})
    
    # Physics-based recommendations
    if avg_scores.get('physics_efficiency', 1) < 0.7:
        recommendations.append(
            "Focus on minimizing unnecessary movements to improve energy efficiency"
        )
        
    # Biomechanics recommendations
    if avg_scores.get('biological_optimality', 1) < 0.7:
        recommendations.append(
            "Work on movement coordination and muscle activation patterns"
        )
        
    # System stability recommendations
    if avg_scores.get('system_stability', 1) < 0.6:
        recommendations.append(
            "Practice controlled movements to improve stability and reduce variability"
        )
        
    # Mathematical optimization recommendations
    if avg_scores.get('mathematical_optimization', 1) < 0.7:
        recommendations.append(
            "Adjust form based on your personal biomechanical constraints"
        )
        
    # Exercise-specific recommendations
    top_issues = result.get('top_issues', [])
    for issue in top_issues[:2]:  # Top 2 issues
        recommendations.append(f"Address: {issue['message']}")
        
    # User goal-specific recommendations
    goals = user_profile.get('goals', [])
    if 'strength' in goals and avg_scores.get('overall', 0) < 0.8:
        recommendations.append(
            "For strength gains, prioritize proper positioning over speed"
        )
    elif 'endurance' in goals:
        recommendations.append(
            "For endurance, focus on efficiency and reduced energy expenditure"
        )
        
    return recommendations[:5]  # Return top 5 recommendations


def _calculate_progress_tracking(history: List[Dict[str, Any]],
                               exercise_type: str) -> Dict[str, Any]:
    """Calculate progress tracking metrics."""
    if len(history) < 2:
        return {
            'sessions_analyzed': len(history),
            'improvement_trend': 'insufficient_data',
            'average_improvement': 0,
            'consistency_score': 0
        }
        
    # Extract scores over time
    scores_timeline = []
    for result in history:
        if result.get('exercise_type') == exercise_type:
            overall_score = result.get('unified_scores', {}).get('overall', 0)
            timestamp = result.get('timestamp', '')
            scores_timeline.append({
                'score': overall_score,
                'timestamp': timestamp
            })
            
    if len(scores_timeline) < 2:
        return {
            'sessions_analyzed': len(scores_timeline),
            'improvement_trend': 'insufficient_data',
            'average_improvement': 0,
            'consistency_score': 0
        }
        
    # Calculate improvement
    recent_scores = [s['score'] for s in scores_timeline[-10:]]
    early_scores = [s['score'] for s in scores_timeline[:10]]
    
    avg_recent = np.mean(recent_scores)
    avg_early = np.mean(early_scores)
    
    improvement = avg_recent - avg_early
    
    # Determine trend
    if improvement > 0.1:
        trend = 'improving'
    elif improvement < -0.05:
        trend = 'declining'
    else:
        trend = 'stable'
        
    # Calculate consistency
    consistency = 1.0 - np.std(recent_scores)
    
    return {
        'sessions_analyzed': len(scores_timeline),
        'improvement_trend': trend,
        'average_improvement': float(improvement),
        'consistency_score': float(max(0, consistency)),
        'recent_average': float(avg_recent),
        'timeline': scores_timeline[-20:]  # Last 20 sessions
    }