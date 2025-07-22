"""
Lifecycle Management API Routes

This module provides API endpoints for managing and monitoring subscription
lifecycle tasks including manual task execution and status monitoring.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import logging

from config.database import get_db
from utils.auth import get_current_user, require_admin
from models.user import User
from services.task_scheduler import get_scheduler, LifecycleTaskType
from services.subscription_lifecycle_service import (
    SubscriptionLifecycleService,
    LifecycleTaskResult
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/lifecycle", tags=["lifecycle-management"])
security = HTTPBearer()


@router.get("/status")
async def get_scheduler_status(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get overall scheduler status and task information
    Admin only endpoint
    """
    try:
        scheduler = get_scheduler()
        
        return {
            "scheduler": scheduler.get_scheduler_status(),
            "tasks": scheduler.get_all_task_status()
        }
        
    except Exception as e:
        logger.error(f"Error getting scheduler status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get scheduler status")


@router.get("/tasks/{task_name}/status")
async def get_task_status(
    task_name: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get status of a specific task
    Admin only endpoint
    """
    try:
        scheduler = get_scheduler()
        task_status = scheduler.get_task_status(task_name)
        
        if not task_status:
            raise HTTPException(status_code=404, detail=f"Task {task_name} not found")
        
        return task_status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task status for {task_name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get task status")


@router.post("/tasks/{task_name}/run")
async def run_task_now(
    task_name: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Run a specific lifecycle task immediately
    Admin only endpoint
    """
    try:
        scheduler = get_scheduler()
        
        # Check if task exists
        if not scheduler.get_task_status(task_name):
            raise HTTPException(status_code=404, detail=f"Task {task_name} not found")
        
        # Run task in background
        result = await scheduler.run_task_now(task_name)
        
        return {
            "message": f"Task {task_name} executed",
            "result": result.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running task {task_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to run task: {str(e)}")


@router.post("/tasks/run-all")
async def run_all_tasks_now(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Run all lifecycle tasks immediately
    Admin only endpoint
    """
    try:
        scheduler = get_scheduler()
        
        # Run all tasks
        results = await scheduler.run_all_tasks_now()
        
        return {
            "message": "All lifecycle tasks executed",
            "results": [result.to_dict() for result in results],
            "summary": {
                "total_tasks": len(results),
                "successful": sum(1 for r in results if r.success),
                "failed": sum(1 for r in results if not r.success)
            }
        }
        
    except Exception as e:
        logger.error(f"Error running all tasks: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to run tasks: {str(e)}")


@router.post("/tasks/{task_name}/enable")
async def enable_task(
    task_name: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Enable a specific task
    Admin only endpoint
    """
    try:
        scheduler = get_scheduler()
        
        if not scheduler.enable_task(task_name):
            raise HTTPException(status_code=404, detail=f"Task {task_name} not found")
        
        return {"message": f"Task {task_name} enabled"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enabling task {task_name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to enable task")


@router.post("/tasks/{task_name}/disable")
async def disable_task(
    task_name: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Disable a specific task
    Admin only endpoint
    """
    try:
        scheduler = get_scheduler()
        
        if not scheduler.disable_task(task_name):
            raise HTTPException(status_code=404, detail=f"Task {task_name} not found")
        
        return {"message": f"Task {task_name} disabled"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disabling task {task_name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to disable task")


@router.get("/tasks/types")
async def get_task_types(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get available task types
    Admin only endpoint
    """
    return {
        "task_types": [task_type.value for task_type in LifecycleTaskType],
        "descriptions": {
            LifecycleTaskType.SUBSCRIPTION_SYNC.value: "Synchronize subscription status with Stripe",
            LifecycleTaskType.USAGE_RESET.value: "Reset weekly usage counters for Free users",
            LifecycleTaskType.GRACE_PERIOD_CHECK.value: "Handle grace periods for failed payments",
            LifecycleTaskType.EXPIRED_DOWNGRADE.value: "Process expired subscriptions and downgrade users",
            LifecycleTaskType.RENEWAL_REMINDERS.value: "Send renewal reminders to users",
            LifecycleTaskType.DATA_CLEANUP.value: "Clean up old data and expired sessions"
        }
    }


@router.post("/tasks/custom")
async def add_custom_task(
    task_data: Dict,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Add a custom task with specific interval
    Admin only endpoint
    
    Expected payload:
    {
        "name": "custom_task_name",
        "task_type": "subscription_sync",
        "interval_minutes": 30
    }
    """
    try:
        name = task_data.get("name")
        task_type_str = task_data.get("task_type")
        interval_minutes = task_data.get("interval_minutes")
        
        if not all([name, task_type_str, interval_minutes]):
            raise HTTPException(
                status_code=400, 
                detail="Missing required fields: name, task_type, interval_minutes"
            )
        
        # Validate task type
        try:
            task_type = LifecycleTaskType(task_type_str)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid task type: {task_type_str}"
            )
        
        # Validate interval
        if not isinstance(interval_minutes, int) or interval_minutes < 1:
            raise HTTPException(
                status_code=400,
                detail="interval_minutes must be a positive integer"
            )
        
        scheduler = get_scheduler()
        
        if not scheduler.add_custom_task(name, task_type, interval_minutes):
            raise HTTPException(
                status_code=400,
                detail=f"Task {name} already exists"
            )
        
        return {
            "message": f"Custom task {name} added successfully",
            "task": scheduler.get_task_status(name)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding custom task: {e}")
        raise HTTPException(status_code=500, detail="Failed to add custom task")


@router.delete("/tasks/{task_name}")
async def remove_task(
    task_name: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Remove a task (custom tasks only)
    Admin only endpoint
    """
    try:
        scheduler = get_scheduler()
        
        # Don't allow removal of default tasks
        default_tasks = [
            "subscription_sync",
            "weekly_usage_reset", 
            "grace_period_check",
            "expired_subscription_processing",
            "renewal_reminders",
            "data_cleanup"
        ]
        
        if task_name in default_tasks:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot remove default task: {task_name}"
            )
        
        if not scheduler.remove_task(task_name):
            raise HTTPException(status_code=404, detail=f"Task {task_name} not found")
        
        return {"message": f"Task {task_name} removed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing task {task_name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to remove task")


@router.get("/health")
async def lifecycle_health_check(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Health check for lifecycle management system
    Available to all authenticated users
    """
    try:
        scheduler = get_scheduler()
        scheduler_status = scheduler.get_scheduler_status()
        
        # Basic health info for non-admin users
        if not current_user.is_premium():
            return {
                "status": "healthy" if scheduler_status["running"] else "unhealthy",
                "scheduler_running": scheduler_status["running"],
                "total_tasks": scheduler_status["total_tasks"]
            }
        
        # Detailed info for admin users
        return {
            "status": "healthy" if scheduler_status["running"] else "unhealthy",
            "scheduler": scheduler_status,
            "recent_errors": sum(
                task.get("error_count", 0) 
                for task in scheduler.get_all_task_status().values()
            )
        }
        
    except Exception as e:
        logger.error(f"Error in lifecycle health check: {e}")
        return {
            "status": "unhealthy",
            "error": "Health check failed"
        }


# Manual lifecycle service endpoints (for direct service access)

@router.post("/service/sync-subscriptions")
async def manual_sync_subscriptions(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Manually trigger subscription synchronization
    Admin only endpoint
    """
    try:
        lifecycle_service = SubscriptionLifecycleService()
        result = await lifecycle_service.sync_subscription_status()
        
        return {
            "message": "Subscription sync completed",
            "result": result.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Error in manual subscription sync: {e}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@router.post("/service/reset-usage")
async def manual_reset_usage(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Manually trigger weekly usage reset
    Admin only endpoint
    """
    try:
        lifecycle_service = SubscriptionLifecycleService()
        result = await lifecycle_service.reset_weekly_usage()
        
        return {
            "message": "Usage reset completed",
            "result": result.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Error in manual usage reset: {e}")
        raise HTTPException(status_code=500, detail=f"Usage reset failed: {str(e)}")


@router.post("/service/cleanup-data")
async def manual_cleanup_data(
    retention_days: int = 90,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Manually trigger data cleanup
    Admin only endpoint
    """
    try:
        lifecycle_service = SubscriptionLifecycleService()
        result = await lifecycle_service.cleanup_old_data(retention_days)
        
        return {
            "message": "Data cleanup completed",
            "result": result.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Error in manual data cleanup: {e}")
        raise HTTPException(status_code=500, detail=f"Data cleanup failed: {str(e)}")