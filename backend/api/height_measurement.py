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

# Helper functions
async def analyze_height_from_video(
    video_path: str, 
    reference_height: Optional[float] = None
) -> dict:
    """
    Analyze video to estimate height using pose detection
    """
    try:
        import mediapipe as mp
        
        mp_pose = mp.solutions.pose
        pose = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        
        cap = cv2.VideoCapture(video_path)
        frame_count = 0
        valid_measurements = []
        
        while cap.read()[0] and frame_count < 100:  # Limit to 100 frames
            ret, frame = cap.read()
            if not ret:
                break
            
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process with MediaPipe
            results = pose.process(rgb_frame)
            
            if results.pose_landmarks:
                # Extract key points for height calculation
                landmarks = results.pose_landmarks.landmark
                
                # Get head and foot landmarks
                nose = landmarks[mp_pose.PoseLandmark.NOSE]
                left_heel = landmarks[mp_pose.PoseLandmark.LEFT_HEEL]
                right_heel = landmarks[mp_pose.PoseLandmark.RIGHT_HEEL]
                
                # Calculate pixel height
                heel_y = (left_heel.y + right_heel.y) / 2
                pixel_height = abs(heel_y - nose.y) * frame.shape[0]
                
                # Basic height estimation (this is simplified)
                # In a real implementation, you'd use reference objects or camera calibration
                estimated_height_cm = pixel_height * 0.5  # Simplified conversion factor
                
                # Use reference height if provided
                if reference_height:
                    # More sophisticated calculation with reference object
                    estimated_height_cm = calculate_height_with_reference(
                        pixel_height, reference_height, frame
                    )
                
                if 100 < estimated_height_cm < 220:  # Reasonable height range
                    valid_measurements.append(estimated_height_cm)
            
            frame_count += 1
        
        cap.release()
        pose.close()
        
        if not valid_measurements:
            return {
                "success": False,
                "error": "Could not detect person in video or extract height measurements"
            }
        
        # Calculate average and confidence
        avg_height = sum(valid_measurements) / len(valid_measurements)
        height_std = np.std(valid_measurements)
        
        # Confidence based on consistency of measurements
        confidence = max(0.0, 1.0 - (height_std / avg_height))
        confidence = min(confidence, 0.95)  # Cap at 95%
        
        return {
            "success": True,
            "height_cm": round(avg_height, 1),
            "confidence": confidence,
            "measurements_count": len(valid_measurements),
            "measurement_std": height_std
        }
        
    except Exception as e:
        logger.error(f"Video height analysis error: {e}")
        return {
            "success": False,
            "error": f"Video analysis failed: {str(e)}"
        }

def calculate_height_with_reference(
    pixel_height: float, 
    reference_height_mm: float, 
    frame: np.ndarray
) -> float:
    """
    Calculate height using a reference object
    This is a simplified implementation
    """
    # In a real implementation, you would:
    # 1. Detect the reference object in the frame
    # 2. Calculate its pixel size
    # 3. Use the ratio to convert pixel height to real height
    
    # For now, using a simplified conversion
    # Assuming reference object provides scale information
    scale_factor = reference_height_mm / 200  # Simplified assumption
    return pixel_height * scale_factor / 10  # Convert to cm