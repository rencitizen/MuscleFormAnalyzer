"""
Authentication API Endpoints
Firebase Authentication integration
"""
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import firebase_admin
from firebase_admin import auth, credentials
import json
import os

from ..config import settings
from ..database import get_db
from ..models.user import User, UserSession
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()

# Initialize Firebase Admin SDK
def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    try:
        if not firebase_admin._apps:
            if settings.FIREBASE_CREDENTIALS:
                # Use service account from environment variable
                cred_dict = json.loads(settings.FIREBASE_CREDENTIALS)
                cred = credentials.Certificate(cred_dict)
            else:
                # Use default credentials (for local development)
                cred = credentials.ApplicationDefault()
            
            firebase_admin.initialize_app(cred, {
                'projectId': settings.FIREBASE_PROJECT_ID,
            })
            logger.info("Firebase Admin SDK initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        # Don't raise here - let individual endpoints handle auth failures

# Initialize Firebase on import
initialize_firebase()

# Request/Response Models
class LoginRequest(BaseModel):
    id_token: str
    device_info: Optional[dict] = None

class LoginResponse(BaseModel):
    success: bool
    user: Optional[dict] = None
    session_id: Optional[str] = None
    error: Optional[str] = None

class UserProfileRequest(BaseModel):
    display_name: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    fitness_level: Optional[str] = None
    fitness_goals: Optional[list] = None

# Dependency to get current user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    try:
        # Verify Firebase ID token
        id_token = credentials.credentials
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        
        # Get or create user in database
        user = db.query(User).filter(User.id == uid).first()
        
        if not user:
            # Create new user from Firebase data
            firebase_user = auth.get_user(uid)
            user = User(
                id=uid,
                email=firebase_user.email,
                display_name=firebase_user.display_name,
                is_verified=firebase_user.email_verified
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"Created new user: {uid}")
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        return user
        
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )

# Optional authentication (doesn't require token)
async def get_current_user_optional(
    authorization: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, otherwise return None"""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    try:
        token = authorization[7:]  # Remove "Bearer " prefix
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
        
        user = db.query(User).filter(User.id == uid).first()
        return user
        
    except:
        return None

@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    req: Request,
    db: Session = Depends(get_db)
):
    """
    Authenticate user with Firebase ID token
    """
    try:
        # Verify Firebase ID token
        decoded_token = auth.verify_id_token(request.id_token)
        uid = decoded_token['uid']
        
        # Get Firebase user data
        firebase_user = auth.get_user(uid)
        
        # Get or create user in database
        user = db.query(User).filter(User.id == uid).first()
        
        if not user:
            # Create new user
            user = User(
                id=uid,
                email=firebase_user.email,
                display_name=firebase_user.display_name,
                is_verified=firebase_user.email_verified
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"Created new user: {uid}")
        else:
            # Update existing user
            user.display_name = firebase_user.display_name
            user.is_verified = firebase_user.email_verified
            user.last_login = datetime.utcnow()
            db.commit()
        
        # Create user session
        session = UserSession(
            id=generate_session_id(),
            user_id=uid,
            device_type=request.device_info.get('type') if request.device_info else None,
            device_id=request.device_info.get('id') if request.device_info else None,
            ip_address=req.client.host,
            user_agent=req.headers.get('user-agent')
        )
        db.add(session)
        db.commit()
        
        return LoginResponse(
            success=True,
            user={
                "id": user.id,
                "email": user.email,
                "display_name": user.display_name,
                "is_verified": user.is_verified,
                "created_at": user.created_at.isoformat()
            },
            session_id=session.id
        )
        
    except Exception as e:
        logger.error(f"Login failed: {e}")
        return LoginResponse(
            success=False,
            error=str(e)
        )

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout user and invalidate session
    """
    try:
        # Mark all active sessions as inactive
        active_sessions = db.query(UserSession).filter(
            UserSession.user_id == current_user.id,
            UserSession.is_active == True
        ).all()
        
        for session in active_sessions:
            session.is_active = False
            session.logout_at = datetime.utcnow()
        
        db.commit()
        
        return {"success": True, "message": "Logged out successfully"}
        
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        raise HTTPException(status_code=500, detail="Logout failed")

@router.get("/me")
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user profile
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "display_name": current_user.display_name,
        "height_cm": current_user.height_cm,
        "weight_kg": current_user.weight_kg,
        "fitness_level": current_user.fitness_level,
        "fitness_goals": current_user.fitness_goals,
        "is_verified": current_user.is_verified,
        "is_premium": current_user.is_premium,
        "created_at": current_user.created_at.isoformat(),
        "last_login": current_user.last_login.isoformat() if current_user.last_login else None
    }

@router.put("/me")
async def update_user_profile(
    profile_data: UserProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user profile
    """
    try:
        # Update user fields
        if profile_data.display_name is not None:
            current_user.display_name = profile_data.display_name
        
        if profile_data.height_cm is not None:
            current_user.height_cm = profile_data.height_cm
        
        if profile_data.weight_kg is not None:
            current_user.weight_kg = profile_data.weight_kg
        
        if profile_data.fitness_level is not None:
            current_user.fitness_level = profile_data.fitness_level
        
        if profile_data.fitness_goals is not None:
            current_user.fitness_goals = profile_data.fitness_goals
        
        current_user.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(current_user)
        
        return {
            "success": True,
            "message": "Profile updated successfully",
            "user": {
                "id": current_user.id,
                "display_name": current_user.display_name,
                "height_cm": current_user.height_cm,
                "weight_kg": current_user.weight_kg,
                "fitness_level": current_user.fitness_level,
                "fitness_goals": current_user.fitness_goals
            }
        }
        
    except Exception as e:
        logger.error(f"Profile update failed: {e}")
        raise HTTPException(status_code=500, detail="Profile update failed")

@router.delete("/me")
async def delete_user_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete user account (soft delete)
    """
    try:
        # Soft delete - mark as inactive
        current_user.is_active = False
        current_user.updated_at = datetime.utcnow()
        
        # Invalidate all sessions
        active_sessions = db.query(UserSession).filter(
            UserSession.user_id == current_user.id,
            UserSession.is_active == True
        ).all()
        
        for session in active_sessions:
            session.is_active = False
            session.logout_at = datetime.utcnow()
        
        db.commit()
        
        return {"success": True, "message": "Account deactivated successfully"}
        
    except Exception as e:
        logger.error(f"Account deletion failed: {e}")
        raise HTTPException(status_code=500, detail="Account deletion failed")

@router.get("/sessions")
async def get_user_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's active sessions
    """
    try:
        sessions = db.query(UserSession).filter(
            UserSession.user_id == current_user.id,
            UserSession.is_active == True
        ).order_by(UserSession.last_activity.desc()).all()
        
        return {
            "sessions": [
                {
                    "id": session.id,
                    "device_type": session.device_type,
                    "ip_address": session.ip_address,
                    "login_at": session.login_at.isoformat(),
                    "last_activity": session.last_activity.isoformat(),
                    "location": {
                        "country": session.country,
                        "city": session.city
                    }
                }
                for session in sessions
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to get sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve sessions")

@router.post("/sessions/{session_id}/revoke")
async def revoke_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Revoke a specific session
    """
    try:
        session = db.query(UserSession).filter(
            UserSession.id == session_id,
            UserSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session.is_active = False
        session.logout_at = datetime.utcnow()
        
        db.commit()
        
        return {"success": True, "message": "Session revoked successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session revocation failed: {e}")
        raise HTTPException(status_code=500, detail="Session revocation failed")

# Helper functions
def generate_session_id() -> str:
    """Generate a unique session ID"""
    import uuid
    return str(uuid.uuid4())

from datetime import datetime