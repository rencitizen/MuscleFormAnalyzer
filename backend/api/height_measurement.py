"""
Height Measurement API Endpoints
Video-based and manual height measurement
"""
import logging
import tempfile
import os
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from pydantic import BaseModel
import cv2
import numpy as np

from ..database import get_db
from ..models.user import User, UserBodyMeasurement
from ..api.auth import get_current_user
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter()

# Request/Response Models
class ManualHeightRequest(BaseModel):
    height_cm: float
    measurement_method: str = "manual"
    notes: Optional[str] = None

class HeightMeasurementResponse(BaseModel):
    success: bool
    height_cm: Optional[float] = None
    confidence: Optional[float] = None
    method: str
    measurement_id: Optional[int] = None
    error: Optional[str] = None

@router.post("/measure/manual", response_model=HeightMeasurementResponse)
async def record_manual_height(
    request: ManualHeightRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Record manual height measurement
    """
    try:
        # Validate height range
        if request.height_cm < 50 or request.height_cm > 250:
            raise HTTPException(
                status_code=400,
                detail="Height must be between 50cm and 250cm"
            )
        
        # Create measurement record
        measurement = UserBodyMeasurement(
            user_id=current_user.id,
            height_cm=request.height_cm,
            measurement_method=request.measurement_method,
            measurement_notes=request.notes,
            measured_by="self"
        )
        
        db.add(measurement)
        db.commit()
        db.refresh(measurement)
        
        # Update user profile
        current_user.height_cm = request.height_cm
        current_user.height_measure_method = request.measurement_method
        db.commit()
        
        logger.info(f"Recorded manual height measurement: {request.height_cm}cm for user {current_user.id}")
        
        return HeightMeasurementResponse(
            success=True,
            height_cm=request.height_cm,
            confidence=1.0,  # Manual measurements have 100% confidence
            method=request.measurement_method,
            measurement_id=measurement.id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Manual height measurement failed: {e}")
        return HeightMeasurementResponse(
            success=False,
            method="manual",
            error=str(e)
        )

@router.post("/measure/video", response_model=HeightMeasurementResponse)
async def measure_height_from_video(
    file: UploadFile = File(...),
    reference_object_height: Optional[float] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Measure height from video using AI analysis
    """
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
            # Analyze video for height measurement
            height_result = await analyze_height_from_video(
                temp_path, 
                reference_object_height
            )
            
            if not height_result["success"]:
                raise HTTPException(
                    status_code=400,
                    detail=height_result.get("error", "Height analysis failed")
                )
            
            height_cm = height_result["height_cm"]
            confidence = height_result["confidence"]
            
            # Create measurement record
            measurement = UserBodyMeasurement(
                user_id=current_user.id,
                height_cm=height_cm,
                measurement_method="video",
                measurement_notes=f"AI analysis with {confidence:.1%} confidence",
                measured_by="ai"
            )
            
            db.add(measurement)
            db.commit()
            db.refresh(measurement)
            
            # Update user profile only if confidence is high
            if confidence > 0.8:
                current_user.height_cm = height_cm
                current_user.height_measure_method = "video"
                db.commit()
                logger.info(f"Updated user profile with video height: {height_cm}cm")
            
            return HeightMeasurementResponse(
                success=True,
                height_cm=height_cm,
                confidence=confidence,
                method="video",
                measurement_id=measurement.id
            )
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Video height measurement failed: {e}")
        return HeightMeasurementResponse(
            success=False,
            method="video",
            error=str(e)
        )

@router.get("/history")
async def get_height_measurement_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 20
):
    """
    Get user's height measurement history
    """
    try:
        measurements = db.query(UserBodyMeasurement).filter(
            UserBodyMeasurement.user_id == current_user.id,
            UserBodyMeasurement.height_cm.isnot(None)
        ).order_by(
            UserBodyMeasurement.measured_at.desc()
        ).limit(limit).all()
        
        return {
            "success": True,
            "measurements": [
                {
                    "id": m.id,
                    "height_cm": m.height_cm,
                    "method": m.measurement_method,
                    "measured_by": m.measured_by,
                    "notes": m.measurement_notes,
                    "measured_at": m.measured_at.isoformat(),
                    "created_at": m.created_at.isoformat()
                }
                for m in measurements
            ],
            "current_height": current_user.height_cm,
            "current_method": current_user.height_measure_method
        }
        
    except Exception as e:
        logger.error(f"Failed to get height history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve height history")

@router.get("/methods")
async def get_measurement_methods():
    """
    Get available height measurement methods
    """
    return {
        "methods": [
            {
                "id": "manual",
                "name": "手動測定",
                "description": "測定テープまたは身長計を使用",
                "accuracy": "高精度",
                "time_required": "1分",
                "equipment_needed": ["身長計", "測定テープ"],
                "pros": [
                    "最も正確",
                    "シンプル",
                    "機器不要"
                ],
                "cons": [
                    "手動入力が必要",
                    "測定器具が必要"
                ]
            },
            {
                "id": "video",
                "name": "動画解析",
                "description": "AIを使用した動画からの身長測定",
                "accuracy": "中〜高精度",
                "time_required": "3-5分",
                "equipment_needed": ["スマートフォン", "基準物体（任意）"],
                "pros": [
                    "自動測定",
                    "記録が残る",
                    "便利"
                ],
                "cons": [
                    "照明に依存",
                    "角度に敏感",
                    "基準物体が必要な場合がある"
                ]
            }
        ],
        "recommendations": [
            "初回は手動測定で正確な値を記録することをお勧めします",
            "動画測定は定期的な変化の追跡に便利です",
            "基準物体として、一般的なクレジットカード（85.6mm）やA4用紙（297mm）を使用できます"
        ]
    }

@router.delete("/measurements/{measurement_id}")
async def delete_height_measurement(
    measurement_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a height measurement record
    """
    try:
        measurement = db.query(UserBodyMeasurement).filter(
            UserBodyMeasurement.id == measurement_id,
            UserBodyMeasurement.user_id == current_user.id
        ).first()
        
        if not measurement:
            raise HTTPException(status_code=404, detail="Measurement not found")
        
        db.delete(measurement)
        db.commit()
        
        return {"success": True, "message": "Measurement deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete measurement: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete measurement")

# Import the enhanced height analyzer
from ..services.height_analyzer import HeightAnalyzer

# Update the video analysis endpoint to use request body
class VideoHeightRequest(BaseModel):
    reference_object: Optional[str] = None
    reference_height_mm: Optional[float] = None

@router.post("/measure/video/upload", response_model=HeightMeasurementResponse)
async def measure_height_from_video_upload(
    file: UploadFile = File(...),
    reference_object: Optional[str] = None,
    reference_height_mm: Optional[float] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Measure height from uploaded video using enhanced AI analysis
    
    Supported reference objects:
    - credit_card: Standard credit card (85.6mm x 53.98mm)
    - a4_paper: A4 paper (297mm x 210mm)
    - custom: Custom marker with specified height
    """
    try:
        # Validate file type
        if not file.content_type.startswith('video/'):
            raise HTTPException(
                status_code=400,
                detail="File must be a video"
            )
        
        # Validate reference object
        valid_objects = ["credit_card", "a4_paper", "smartphone", "door_frame", "custom"]
        if reference_object and reference_object not in valid_objects:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid reference object. Must be one of: {', '.join(valid_objects)}"
            )
        
        # Save uploaded video to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            # Use enhanced height analyzer
            analyzer = HeightAnalyzer()
            height_result = analyzer.analyze_video(
                temp_path, 
                reference_object,
                reference_height_mm
            )
            
            if not height_result["success"]:
                raise HTTPException(
                    status_code=400,
                    detail=height_result.get("error", "Height analysis failed")
                )
            
            height_cm = height_result["height_cm"]
            confidence = height_result["confidence"]
            
            # Create measurement record with detailed notes
            notes = f"AI analysis with {confidence:.1%} confidence"
            if reference_object:
                notes += f", using {reference_object} as reference"
            notes += f", {height_result['measurements_count']} measurements"
            notes += f", consistency: {height_result.get('consistency_score', 0):.1%}"
            
            measurement = UserBodyMeasurement(
                user_id=current_user.id,
                height_cm=height_cm,
                measurement_method="video",
                measurement_notes=notes,
                measured_by="ai"
            )
            
            db.add(measurement)
            db.commit()
            db.refresh(measurement)
            
            # Update user profile only if confidence is high
            if confidence > 0.8:
                current_user.height_cm = height_cm
                current_user.height_measure_method = "video"
                db.commit()
                logger.info(f"Updated user profile with video height: {height_cm}cm")
            
            return HeightMeasurementResponse(
                success=True,
                height_cm=height_cm,
                confidence=confidence,
                method="video",
                measurement_id=measurement.id
            )
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Video height measurement failed: {e}", exc_info=True)
        return HeightMeasurementResponse(
            success=False,
            method="video",
            error=str(e)
        )

# Helper functions for backward compatibility
async def analyze_height_from_video(
    video_path: str, 
    reference_height: Optional[float] = None
) -> dict:
    """
    Legacy function - redirects to new analyzer
    """
    analyzer = HeightAnalyzer()
    if reference_height:
        # Convert mm to object type
        reference_object = "custom"
    else:
        reference_object = None
        
    return analyzer.analyze_video(video_path, reference_object, reference_height)