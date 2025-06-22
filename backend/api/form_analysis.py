"""
Form Analysis API Endpoints
FastAPI routes for pose analysis and form evaluation
"""
import asyncio
import logging
import tempfile
import os
from typing import Optional, List
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import cv2
import numpy as np

from ..services.mediapipe_service import analyzer, AnalysisResult
from ..database import get_db
from ..models.workout import WorkoutSession, FormAnalysis
from sqlalchemy.orm import Session, joinedload
from ..services.cache_service import cached
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

# Request/Response Models
class AnalysisRequest(BaseModel):
    exercise_type: str = "squat"
    session_id: Optional[str] = None
    user_id: Optional[str] = None

class FrameAnalysisResponse(BaseModel):
    success: bool
    analysis: Optional[dict] = None
    error: Optional[str] = None
    processing_time: float
    session_id: Optional[str] = None

class VideoAnalysisResponse(BaseModel):
    success: bool
    sequence_analysis: Optional[dict] = None
    aggregated_feedback: List[dict] = []
    best_frame_analysis: Optional[dict] = None
    error: Optional[str] = None
    processing_time: float
    session_id: Optional[str] = None

@router.post("/analyze/frame", response_model=FrameAnalysisResponse)
async def analyze_single_frame(
    file: UploadFile = File(...),
    exercise_type: str = "squat",
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Analyze a single frame/image for form analysis
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="File must be an image"
            )
        
        # Read image data
        image_data = await file.read()
        
        # Convert to OpenCV format
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(
                status_code=400,
                detail="Could not decode image"
            )
        
        # Perform analysis
        result = await analyzer.analyze_frame_async(image, exercise_type)
        
        # Save to database if session_id provided
        if session_id and user_id:
            try:
                form_analysis = FormAnalysis(
                    session_id=session_id,
                    user_id=user_id,
                    exercise_type=exercise_type,
                    score=result.score,
                    feedback=result.feedback,
                    angle_scores=result.angle_scores,
                    phase=result.phase,
                    confidence=result.confidence,
                    biomechanics=result.biomechanics
                )
                db.add(form_analysis)
                db.commit()
                logger.info(f"Saved form analysis for session {session_id}")
            except Exception as e:
                logger.error(f"Failed to save form analysis: {e}")
                # Don't fail the request if saving fails
        
        # Convert result to dict for response
        analysis_dict = {
            "score": result.score,
            "angle_scores": result.angle_scores,
            "phase": result.phase,
            "feedback": result.feedback,
            "confidence": result.confidence,
            "processing_time": result.processing_time,
            "analyzer_type": result.analyzer_type,
            "biomechanics": result.biomechanics
        }
        
        return FrameAnalysisResponse(
            success=True,
            analysis=analysis_dict,
            processing_time=result.processing_time,
            session_id=session_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Frame analysis error: {e}")
        return FrameAnalysisResponse(
            success=False,
            error=str(e),
            processing_time=0.0,
            session_id=session_id
        )

@router.post("/analyze/video", response_model=VideoAnalysisResponse)
async def analyze_video_sequence(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    exercise_type: str = "squat",
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Analyze a video file for comprehensive form analysis
    """
    import time
    start_time = time.time()
    
    try:
        # Validate file type
        if not file.content_type.startswith('video/'):
            raise HTTPException(
                status_code=400,
                detail="File must be a video"
            )
        
        # Save uploaded video to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            # Extract frames from video
            frames = await extract_video_frames(temp_path)
            
            if not frames:
                raise HTTPException(
                    status_code=400,
                    detail="Could not extract frames from video"
                )
            
            # Analyze video sequence
            result = await analyzer.process_video_sequence(frames, exercise_type)
            
            if not result.get("success"):
                raise HTTPException(
                    status_code=400,
                    detail=result.get("error", "Video analysis failed")
                )
            
            # Save comprehensive analysis to database
            if session_id and user_id:
                background_tasks.add_task(
                    save_video_analysis,
                    db,
                    session_id,
                    user_id,
                    exercise_type,
                    result
                )
            
            processing_time = time.time() - start_time
            
            return VideoAnalysisResponse(
                success=True,
                sequence_analysis=result.get("sequence_analysis"),
                aggregated_feedback=result.get("aggregated_feedback", []),
                best_frame_analysis=result.get("best_frame_analysis").__dict__ if result.get("best_frame_analysis") else None,
                processing_time=processing_time,
                session_id=session_id
            )
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Video analysis error: {e}")
        return VideoAnalysisResponse(
            success=False,
            error=str(e),
            processing_time=time.time() - start_time,
            session_id=session_id
        )

@router.get("/exercises/supported")
async def get_supported_exercises(request: Request = None):
    """
    Get list of supported exercises for analysis
    """
    # Use cache from request state if available
    cache_service = getattr(request.app.state, 'cache_service', None) if request else None
    
    if cache_service:
        cache_key = "exercises:supported"
        cached_data = cache_service.get(cache_key)
        if cached_data:
            return cached_data
    
    result = {
        "exercises": [
            {
                "id": "squat",
                "name": "スクワット",
                "description": "BIG3の基本種目。下半身の複合運動",
                "key_points": [
                    "膝が90度まで曲がること",
                    "背中をまっすぐ保つこと",
                    "足首の柔軟性"
                ]
            },
            {
                "id": "bench_press",
                "name": "ベンチプレス",
                "description": "上半身の複合運動。胸・肩・三頭筋を鍛える",
                "key_points": [
                    "肘の角度",
                    "肩甲骨の安定性",
                    "バーパスの軌道"
                ]
            },
            {
                "id": "deadlift",
                "name": "デッドリフト",
                "description": "全身の複合運動。背中・臀部・ハムストリングスが主働筋",
                "key_points": [
                    "背中の中立位置",
                    "ヒップヒンジの動作",
                    "膝とつま先の方向"
                ]
            }
        ]
    }
    
    # Cache result
    if cache_service:
        cache_service.set(cache_key, result, ttl=3600)  # Cache for 1 hour
    
    return result

@router.get("/analysis/history/{user_id}")
async def get_analysis_history(
    user_id: str,
    exercise_type: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Get user's form analysis history
    """
    # Use cache from request state if available
    cache_service = getattr(request.app.state, 'cache_service', None) if request else None
    
    if cache_service:
        cache_key = f"analysis_history:{user_id}:{exercise_type}:{limit}:{offset}"
        cached_data = cache_service.get(cache_key)
        if cached_data:
            return cached_data
    
    try:
        # Use eager loading to avoid N+1 queries
        query = db.query(FormAnalysis).options(
            joinedload(FormAnalysis.session)
        ).filter(FormAnalysis.user_id == user_id)
        
        if exercise_type:
            query = query.filter(FormAnalysis.exercise_type == exercise_type)
        
        # Get total count before applying limit/offset
        total_count = query.count()
        
        analyses = query.order_by(FormAnalysis.created_at.desc()).offset(offset).limit(limit).all()
        
        result = {
            "success": True,
            "analyses": [
                {
                    "id": analysis.id,
                    "exercise_type": analysis.exercise_type,
                    "score": analysis.score,
                    "phase": analysis.phase,
                    "confidence": analysis.confidence,
                    "feedback_count": len(analysis.feedback) if analysis.feedback else 0,
                    "created_at": analysis.created_at.isoformat(),
                    "session_id": analysis.session_id
                }
                for analysis in analyses
            ],
            "total": total_count
        }
        
        # Cache result for 5 minutes
        if cache_service:
            cache_service.set(cache_key, result, ttl=300)
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to get analysis history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analysis history")

@router.get("/analysis/{analysis_id}")
async def get_analysis_detail(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed analysis results
    """
    try:
        analysis = db.query(FormAnalysis).filter(FormAnalysis.id == analysis_id).first()
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return {
            "success": True,
            "analysis": {
                "id": analysis.id,
                "exercise_type": analysis.exercise_type,
                "score": analysis.score,
                "angle_scores": analysis.angle_scores,
                "phase": analysis.phase,
                "feedback": analysis.feedback,
                "confidence": analysis.confidence,
                "biomechanics": analysis.biomechanics,
                "created_at": analysis.created_at.isoformat(),
                "session_id": analysis.session_id,
                "user_id": analysis.user_id
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analysis detail: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analysis detail")

@router.post("/session/start")
async def start_analysis_session(
    request: AnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Start a new form analysis session
    """
    try:
        # Create new workout session
        session = WorkoutSession(
            user_id=request.user_id,
            exercise_type=request.exercise_type,
            status="active"
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return {
            "success": True,
            "session_id": session.id,
            "exercise_type": request.exercise_type,
            "started_at": session.started_at.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to start session: {e}")
        raise HTTPException(status_code=500, detail="Failed to start analysis session")

@router.post("/session/{session_id}/end")
async def end_analysis_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    End an analysis session
    """
    try:
        session = db.query(WorkoutSession).filter(WorkoutSession.id == session_id).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session.status = "completed"
        session.ended_at = datetime.utcnow()
        
        db.commit()
        
        # Calculate session summary
        analyses = db.query(FormAnalysis).filter(FormAnalysis.session_id == session_id).all()
        
        if analyses:
            avg_score = sum(a.score for a in analyses) / len(analyses)
            avg_confidence = sum(a.confidence for a in analyses) / len(analyses)
        else:
            avg_score = avg_confidence = 0.0
        
        return {
            "success": True,
            "session_summary": {
                "session_id": session_id,
                "total_analyses": len(analyses),
                "average_score": avg_score,
                "average_confidence": avg_confidence,
                "duration_minutes": (session.ended_at - session.started_at).total_seconds() / 60,
                "exercise_type": session.exercise_type
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to end session: {e}")
        raise HTTPException(status_code=500, detail="Failed to end analysis session")

# Helper functions
async def extract_video_frames(video_path: str, max_frames: int = 30) -> List[np.ndarray]:
    """
    Extract frames from video file
    """
    frames = []
    
    try:
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Calculate frame interval for sampling
        if total_frames > max_frames:
            interval = total_frames // max_frames
        else:
            interval = 1
        
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % interval == 0:
                frames.append(frame)
                
                if len(frames) >= max_frames:
                    break
            
            frame_count += 1
        
        cap.release()
        logger.info(f"Extracted {len(frames)} frames from video")
        
    except Exception as e:
        logger.error(f"Error extracting frames: {e}")
    
    return frames

async def save_video_analysis(
    db: Session,
    session_id: str,
    user_id: str,
    exercise_type: str,
    analysis_result: dict
):
    """
    Save video analysis results to database
    """
    try:
        # Save aggregate analysis
        best_frame = analysis_result.get("best_frame_analysis")
        if best_frame:
            form_analysis = FormAnalysis(
                session_id=session_id,
                user_id=user_id,
                exercise_type=exercise_type,
                score=best_frame.score,
                feedback=analysis_result.get("aggregated_feedback", []),
                angle_scores=best_frame.angle_scores,
                phase=best_frame.phase,
                confidence=best_frame.confidence,
                biomechanics=best_frame.biomechanics,
                is_video_analysis=True,
                video_metadata=analysis_result.get("sequence_analysis")
            )
            
            db.add(form_analysis)
            db.commit()
            
            logger.info(f"Saved video analysis for session {session_id}")
        
    except Exception as e:
        logger.error(f"Failed to save video analysis: {e}")