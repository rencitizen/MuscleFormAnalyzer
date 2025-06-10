"""
Progress Tracking API Endpoints
Analytics and progress monitoring
"""
import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from datetime import datetime, date, timedelta
from sqlalchemy import func, desc

from ..database import get_db
from ..models.user import User
from ..models.progress import ProgressSnapshot, Goal, Achievement, ProgressPhoto, Streak
from ..models.workout import FormAnalysis, WorkoutSession
from ..models.nutrition import MealEntry
from ..api.auth import get_current_user
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter()

# Request/Response Models
class GoalRequest(BaseModel):
    goal_type: str
    title: str
    description: Optional[str] = None
    target_value: float
    unit: Optional[str] = None
    target_date: datetime
    priority: str = "medium"

class ProgressResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None

@router.get("/overview")
async def get_progress_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive progress overview
    """
    try:
        # Get recent progress snapshot
        recent_snapshot = db.query(ProgressSnapshot).filter(
            ProgressSnapshot.user_id == current_user.id
        ).order_by(desc(ProgressSnapshot.snapshot_date)).first()
        
        # Get active goals
        active_goals = db.query(Goal).filter(
            Goal.user_id == current_user.id,
            Goal.status == "active"
        ).all()
        
        # Get recent achievements
        recent_achievements = db.query(Achievement).filter(
            Achievement.user_id == current_user.id
        ).order_by(desc(Achievement.achieved_at)).limit(5).all()
        
        # Get active streaks
        active_streaks = db.query(Streak).filter(
            Streak.user_id == current_user.id,
            Streak.is_active == True
        ).all()
        
        # Calculate weekly stats
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        weekly_workouts = db.query(WorkoutSession).filter(
            WorkoutSession.user_id == current_user.id,
            WorkoutSession.started_at >= week_ago
        ).count()
        
        weekly_form_scores = db.query(FormAnalysis).filter(
            FormAnalysis.user_id == current_user.id,
            FormAnalysis.created_at >= week_ago
        ).all()
        
        avg_form_score = 0
        if weekly_form_scores:
            avg_form_score = sum(a.score for a in weekly_form_scores) / len(weekly_form_scores)
        
        weekly_meals = db.query(MealEntry).filter(
            MealEntry.user_id == current_user.id,
            MealEntry.consumed_at >= week_ago
        ).count()
        
        return {
            "success": True,
            "overview": {
                "current_stats": {
                    "weight_kg": recent_snapshot.weight_kg if recent_snapshot else current_user.weight_kg,
                    "height_cm": current_user.height_cm,
                    "body_fat_percentage": recent_snapshot.body_fat_percentage if recent_snapshot else None,
                    "muscle_mass_kg": recent_snapshot.muscle_mass_kg if recent_snapshot else None
                },
                "weekly_summary": {
                    "workouts_completed": weekly_workouts,
                    "average_form_score": round(avg_form_score, 1),
                    "meals_logged": weekly_meals
                },
                "goals": {
                    "active_count": len(active_goals),
                    "goals": [
                        {
                            "id": goal.id,
                            "title": goal.title,
                            "progress_percentage": goal.progress_percentage,
                            "target_date": goal.target_date.isoformat(),
                            "status": goal.status
                        }
                        for goal in active_goals[:3]  # Top 3 goals
                    ]
                },
                "achievements": [
                    {
                        "id": achievement.id,
                        "title": achievement.title,
                        "description": achievement.description,
                        "achieved_at": achievement.achieved_at.isoformat(),
                        "rarity": achievement.rarity
                    }
                    for achievement in recent_achievements
                ],
                "streaks": [
                    {
                        "type": streak.streak_type,
                        "current_count": streak.current_count,
                        "best_count": streak.best_count
                    }
                    for streak in active_streaks
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get progress overview: {e}")
        raise HTTPException(status_code=500, detail="Failed to get progress overview")

@router.get("/trends")
async def get_progress_trends(
    period: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    metrics: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get progress trends over specified period
    """
    try:
        # Calculate date range
        days_map = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}
        days_back = days_map[period]
        start_date = datetime.utcnow() - timedelta(days=days_back)
        
        # Get progress snapshots
        snapshots = db.query(ProgressSnapshot).filter(
            ProgressSnapshot.user_id == current_user.id,
            ProgressSnapshot.snapshot_date >= start_date
        ).order_by(ProgressSnapshot.snapshot_date).all()
        
        # Get form analysis trends
        form_analyses = db.query(FormAnalysis).filter(
            FormAnalysis.user_id == current_user.id,
            FormAnalysis.created_at >= start_date
        ).order_by(FormAnalysis.created_at).all()
        
        # Group form scores by date
        daily_scores = {}
        for analysis in form_analyses:
            date_key = analysis.created_at.date().isoformat()
            if date_key not in daily_scores:
                daily_scores[date_key] = []
            daily_scores[date_key].append(analysis.score)
        
        # Calculate daily averages
        daily_avg_scores = {
            date_key: sum(scores) / len(scores)
            for date_key, scores in daily_scores.items()
        }
        
        # Format trends data
        trends = {
            "period": period,
            "date_range": {
                "start": start_date.isoformat(),
                "end": datetime.utcnow().isoformat()
            },
            "weight_trend": [
                {
                    "date": snapshot.snapshot_date.isoformat(),
                    "value": snapshot.weight_kg
                }
                for snapshot in snapshots if snapshot.weight_kg
            ],
            "form_score_trend": [
                {
                    "date": date_key,
                    "value": round(avg_score, 1)
                }
                for date_key, avg_score in sorted(daily_avg_scores.items())
            ],
            "strength_trends": {
                "squat": [
                    {
                        "date": snapshot.snapshot_date.isoformat(),
                        "value": snapshot.squat_1rm
                    }
                    for snapshot in snapshots if snapshot.squat_1rm
                ],
                "bench_press": [
                    {
                        "date": snapshot.snapshot_date.isoformat(),
                        "value": snapshot.bench_press_1rm
                    }
                    for snapshot in snapshots if snapshot.bench_press_1rm
                ],
                "deadlift": [
                    {
                        "date": snapshot.snapshot_date.isoformat(),
                        "value": snapshot.deadlift_1rm
                    }
                    for snapshot in snapshots if snapshot.deadlift_1rm
                ]
            }
        }
        
        return {"success": True, "trends": trends}
        
    except Exception as e:
        logger.error(f"Failed to get progress trends: {e}")
        raise HTTPException(status_code=500, detail="Failed to get progress trends")

@router.post("/goals")
async def create_goal(
    goal_data: GoalRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new goal
    """
    try:
        goal = Goal(
            user_id=current_user.id,
            goal_type=goal_data.goal_type,
            title=goal_data.title,
            description=goal_data.description,
            target_value=goal_data.target_value,
            unit=goal_data.unit,
            start_date=datetime.utcnow(),
            target_date=goal_data.target_date,
            priority=goal_data.priority
        )
        
        db.add(goal)
        db.commit()
        db.refresh(goal)
        
        return {
            "success": True,
            "goal": {
                "id": goal.id,
                "title": goal.title,
                "goal_type": goal.goal_type,
                "target_value": goal.target_value,
                "current_value": goal.current_value,
                "progress_percentage": goal.progress_percentage,
                "target_date": goal.target_date.isoformat(),
                "status": goal.status
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to create goal: {e}")
        raise HTTPException(status_code=500, detail="Failed to create goal")

@router.get("/goals")
async def get_goals(
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's goals
    """
    try:
        query = db.query(Goal).filter(Goal.user_id == current_user.id)
        
        if status:
            query = query.filter(Goal.status == status)
        
        goals = query.order_by(desc(Goal.created_at)).all()
        
        return {
            "success": True,
            "goals": [
                {
                    "id": goal.id,
                    "title": goal.title,
                    "description": goal.description,
                    "goal_type": goal.goal_type,
                    "target_value": goal.target_value,
                    "current_value": goal.current_value,
                    "unit": goal.unit,
                    "progress_percentage": goal.progress_percentage,
                    "status": goal.status,
                    "priority": goal.priority,
                    "start_date": goal.start_date.isoformat(),
                    "target_date": goal.target_date.isoformat(),
                    "completed_date": goal.completed_date.isoformat() if goal.completed_date else None
                }
                for goal in goals
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to get goals: {e}")
        raise HTTPException(status_code=500, detail="Failed to get goals")

@router.put("/goals/{goal_id}/progress")
async def update_goal_progress(
    goal_id: int,
    current_value: float,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update goal progress
    """
    try:
        goal = db.query(Goal).filter(
            Goal.id == goal_id,
            Goal.user_id == current_user.id
        ).first()
        
        if not goal:
            raise HTTPException(status_code=404, detail="Goal not found")
        
        # Update progress
        goal.current_value = current_value
        goal.progress_percentage = min((current_value / goal.target_value) * 100, 100)
        goal.updated_at = datetime.utcnow()
        
        # Check if goal is completed
        if goal.progress_percentage >= 100 and goal.status == "active":
            goal.status = "completed"
            goal.completed_date = datetime.utcnow()
            
            # Create achievement
            achievement = Achievement(
                user_id=current_user.id,
                achievement_type="goal_completed",
                title=f"目標達成: {goal.title}",
                description=f"{goal.title}を達成しました！",
                goal_id=goal.id,
                achieved_at=datetime.utcnow()
            )
            db.add(achievement)
        
        db.commit()
        
        return {
            "success": True,
            "goal": {
                "id": goal.id,
                "current_value": goal.current_value,
                "progress_percentage": goal.progress_percentage,
                "status": goal.status,
                "completed": goal.status == "completed"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update goal progress: {e}")
        raise HTTPException(status_code=500, detail="Failed to update goal progress")

@router.get("/achievements")
async def get_achievements(
    limit: int = Query(50, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's achievements
    """
    try:
        achievements = db.query(Achievement).filter(
            Achievement.user_id == current_user.id
        ).order_by(desc(Achievement.achieved_at)).limit(limit).all()
        
        return {
            "success": True,
            "achievements": [
                {
                    "id": achievement.id,
                    "title": achievement.title,
                    "description": achievement.description,
                    "achievement_type": achievement.achievement_type,
                    "value": achievement.value,
                    "unit": achievement.unit,
                    "category": achievement.category,
                    "rarity": achievement.rarity,
                    "points": achievement.points,
                    "achieved_at": achievement.achieved_at.isoformat()
                }
                for achievement in achievements
            ],
            "total_points": sum(a.points for a in achievements)
        }
        
    except Exception as e:
        logger.error(f"Failed to get achievements: {e}")
        raise HTTPException(status_code=500, detail="Failed to get achievements")

@router.get("/streaks")
async def get_streaks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's activity streaks
    """
    try:
        streaks = db.query(Streak).filter(
            Streak.user_id == current_user.id
        ).all()
        
        return {
            "success": True,
            "streaks": [
                {
                    "streak_type": streak.streak_type,
                    "current_count": streak.current_count,
                    "best_count": streak.best_count,
                    "is_active": streak.is_active,
                    "current_start_date": streak.current_start_date.isoformat() if streak.current_start_date else None,
                    "last_activity_date": streak.last_activity_date.isoformat() if streak.last_activity_date else None,
                    "best_start_date": streak.best_start_date.isoformat() if streak.best_start_date else None,
                    "best_end_date": streak.best_end_date.isoformat() if streak.best_end_date else None
                }
                for streak in streaks
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to get streaks: {e}")
        raise HTTPException(status_code=500, detail="Failed to get streaks")

@router.post("/snapshot")
async def create_progress_snapshot(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new progress snapshot
    """
    try:
        # Calculate metrics for snapshot
        today = datetime.utcnow().date()
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        # Get workout stats
        recent_workouts = db.query(WorkoutSession).filter(
            WorkoutSession.user_id == current_user.id,
            WorkoutSession.started_at >= week_ago
        ).all()
        
        total_workouts = len(recent_workouts)
        total_workout_time = sum(
            (w.ended_at - w.started_at).total_seconds() / 60
            for w in recent_workouts if w.ended_at
        )
        
        # Get form analysis stats
        recent_analyses = db.query(FormAnalysis).filter(
            FormAnalysis.user_id == current_user.id,
            FormAnalysis.created_at >= week_ago
        ).all()
        
        avg_form_score = 0
        if recent_analyses:
            avg_form_score = sum(a.score for a in recent_analyses) / len(recent_analyses)
        
        # Create snapshot
        snapshot = ProgressSnapshot(
            user_id=current_user.id,
            snapshot_type="weekly",
            snapshot_date=datetime.utcnow(),
            weight_kg=current_user.weight_kg,
            total_workouts=total_workouts,
            total_workout_time=total_workout_time,
            average_form_score=avg_form_score
        )
        
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)
        
        return {
            "success": True,
            "snapshot": {
                "id": snapshot.id,
                "snapshot_date": snapshot.snapshot_date.isoformat(),
                "total_workouts": snapshot.total_workouts,
                "average_form_score": snapshot.average_form_score,
                "weight_kg": snapshot.weight_kg
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to create progress snapshot: {e}")
        raise HTTPException(status_code=500, detail="Failed to create progress snapshot")