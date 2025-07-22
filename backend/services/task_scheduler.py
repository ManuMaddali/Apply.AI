"""
Task Scheduler for Subscription Lifecycle Management

This module provides a background task scheduler that runs subscription lifecycle
management tasks at regular intervals. It uses asyncio for non-blocking execution
and includes proper error handling and logging.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum
import traceback

from services.subscription_lifecycle_service import (
    SubscriptionLifecycleService, 
    LifecycleTaskType,
    LifecycleTaskResult
)

logger = logging.getLogger(__name__)


class ScheduleInterval(Enum):
    """Schedule intervals for tasks"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


@dataclass
class ScheduledTask:
    """Represents a scheduled task"""
    name: str
    task_type: LifecycleTaskType
    interval: ScheduleInterval
    custom_interval_minutes: Optional[int] = None
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    enabled: bool = True
    run_count: int = 0
    error_count: int = 0
    last_error: Optional[str] = None
    last_result: Optional[LifecycleTaskResult] = None


class TaskScheduler:
    """Background task scheduler for subscription lifecycle management"""
    
    def __init__(self):
        self.lifecycle_service = SubscriptionLifecycleService()
        self.tasks: Dict[str, ScheduledTask] = {}
        self.running = False
        self.scheduler_task: Optional[asyncio.Task] = None
        self._setup_default_tasks()
    
    def _setup_default_tasks(self):
        """Setup default scheduled tasks"""
        default_tasks = [
            ScheduledTask(
                name="subscription_sync",
                task_type=LifecycleTaskType.SUBSCRIPTION_SYNC,
                interval=ScheduleInterval.HOURLY
            ),
            ScheduledTask(
                name="weekly_usage_reset",
                task_type=LifecycleTaskType.USAGE_RESET,
                interval=ScheduleInterval.WEEKLY
            ),
            ScheduledTask(
                name="grace_period_check",
                task_type=LifecycleTaskType.GRACE_PERIOD_CHECK,
                interval=ScheduleInterval.DAILY
            ),
            ScheduledTask(
                name="expired_subscription_processing",
                task_type=LifecycleTaskType.EXPIRED_DOWNGRADE,
                interval=ScheduleInterval.DAILY
            ),
            ScheduledTask(
                name="renewal_reminders",
                task_type=LifecycleTaskType.RENEWAL_REMINDERS,
                interval=ScheduleInterval.DAILY
            ),
            ScheduledTask(
                name="data_cleanup",
                task_type=LifecycleTaskType.DATA_CLEANUP,
                interval=ScheduleInterval.WEEKLY
            )
        ]
        
        for task in default_tasks:
            self.tasks[task.name] = task
            self._calculate_next_run(task)
    
    def _calculate_next_run(self, task: ScheduledTask):
        """Calculate next run time for a task"""
        now = datetime.utcnow()
        
        if task.interval == ScheduleInterval.HOURLY:
            task.next_run = now + timedelta(hours=1)
        elif task.interval == ScheduleInterval.DAILY:
            # Run daily tasks at 2 AM UTC
            next_run = now.replace(hour=2, minute=0, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
            task.next_run = next_run
        elif task.interval == ScheduleInterval.WEEKLY:
            # Run weekly tasks on Sunday at 3 AM UTC
            days_until_sunday = (6 - now.weekday()) % 7
            if days_until_sunday == 0 and now.hour >= 3:
                days_until_sunday = 7
            next_run = now.replace(hour=3, minute=0, second=0, microsecond=0)
            next_run += timedelta(days=days_until_sunday)
            task.next_run = next_run
        elif task.interval == ScheduleInterval.MONTHLY:
            # Run monthly tasks on the 1st at 4 AM UTC
            if now.month == 12:
                next_run = now.replace(year=now.year + 1, month=1, day=1, hour=4, minute=0, second=0, microsecond=0)
            else:
                next_run = now.replace(month=now.month + 1, day=1, hour=4, minute=0, second=0, microsecond=0)
            task.next_run = next_run
        elif task.interval == ScheduleInterval.CUSTOM and task.custom_interval_minutes:
            task.next_run = now + timedelta(minutes=task.custom_interval_minutes)
        else:
            # Default to 1 hour
            task.next_run = now + timedelta(hours=1)
    
    async def start(self):
        """Start the task scheduler"""
        if self.running:
            logger.warning("Task scheduler is already running")
            return
        
        self.running = True
        logger.info("🚀 Starting subscription lifecycle task scheduler")
        
        # Start the scheduler loop
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        
        # Run initial sync task immediately
        await self._run_task_safe("subscription_sync")
    
    async def stop(self):
        """Stop the task scheduler"""
        if not self.running:
            return
        
        logger.info("🛑 Stopping subscription lifecycle task scheduler")
        self.running = False
        
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
        
        logger.info("✅ Task scheduler stopped")
    
    async def _scheduler_loop(self):
        """Main scheduler loop"""
        try:
            while self.running:
                await self._check_and_run_tasks()
                # Check every minute
                await asyncio.sleep(60)
        except asyncio.CancelledError:
            logger.info("Scheduler loop cancelled")
        except Exception as e:
            logger.error(f"Scheduler loop error: {e}")
            logger.error(traceback.format_exc())
    
    async def _check_and_run_tasks(self):
        """Check for tasks that need to run and execute them"""
        now = datetime.utcnow()
        
        for task_name, task in self.tasks.items():
            if not task.enabled:
                continue
            
            if task.next_run and now >= task.next_run:
                await self._run_task_safe(task_name)
    
    async def _run_task_safe(self, task_name: str):
        """Run a task with error handling"""
        if task_name not in self.tasks:
            logger.error(f"Task {task_name} not found")
            return
        
        task = self.tasks[task_name]
        
        try:
            logger.info(f"🔄 Running scheduled task: {task_name}")
            
            # Run the lifecycle task
            result = await self.lifecycle_service.run_single_task(task.task_type)
            
            # Update task status
            task.last_run = datetime.utcnow()
            task.last_result = result
            task.run_count += 1
            
            if result.success:
                logger.info(f"✅ Task {task_name} completed successfully: "
                          f"{result.processed_count} items processed")
                task.last_error = None
            else:
                logger.error(f"❌ Task {task_name} failed: {result.error_message}")
                task.error_count += 1
                task.last_error = result.error_message
            
            # Calculate next run time
            self._calculate_next_run(task)
            
        except Exception as e:
            logger.error(f"❌ Task {task_name} crashed: {e}")
            logger.error(traceback.format_exc())
            
            task.error_count += 1
            task.last_error = str(e)
            task.last_run = datetime.utcnow()
            
            # Calculate next run time even on error
            self._calculate_next_run(task)
    
    async def run_task_now(self, task_name: str) -> LifecycleTaskResult:
        """Run a specific task immediately"""
        if task_name not in self.tasks:
            return LifecycleTaskResult(
                LifecycleTaskType.SUBSCRIPTION_SYNC,  # Default
                success=False,
                error_message=f"Task {task_name} not found"
            )
        
        task = self.tasks[task_name]
        
        try:
            logger.info(f"🔄 Running task on demand: {task_name}")
            
            result = await self.lifecycle_service.run_single_task(task.task_type)
            
            # Update task status
            task.last_run = datetime.utcnow()
            task.last_result = result
            task.run_count += 1
            
            if not result.success:
                task.error_count += 1
                task.last_error = result.error_message
            else:
                task.last_error = None
            
            return result
            
        except Exception as e:
            logger.error(f"❌ On-demand task {task_name} crashed: {e}")
            
            task.error_count += 1
            task.last_error = str(e)
            task.last_run = datetime.utcnow()
            
            return LifecycleTaskResult(
                task.task_type,
                success=False,
                error_message=str(e)
            )
    
    async def run_all_tasks_now(self) -> List[LifecycleTaskResult]:
        """Run all lifecycle tasks immediately"""
        logger.info("🔄 Running all lifecycle tasks on demand")
        
        results = []
        for task_name in self.tasks.keys():
            if self.tasks[task_name].enabled:
                result = await self.run_task_now(task_name)
                results.append(result)
        
        return results
    
    def get_task_status(self, task_name: str) -> Optional[Dict]:
        """Get status of a specific task"""
        if task_name not in self.tasks:
            return None
        
        task = self.tasks[task_name]
        return {
            "name": task.name,
            "task_type": task.task_type.value,
            "interval": task.interval.value,
            "custom_interval_minutes": task.custom_interval_minutes,
            "enabled": task.enabled,
            "last_run": task.last_run.isoformat() if task.last_run else None,
            "next_run": task.next_run.isoformat() if task.next_run else None,
            "run_count": task.run_count,
            "error_count": task.error_count,
            "last_error": task.last_error,
            "last_result": task.last_result.to_dict() if task.last_result else None
        }
    
    def get_all_task_status(self) -> Dict[str, Dict]:
        """Get status of all tasks"""
        return {
            task_name: self.get_task_status(task_name)
            for task_name in self.tasks.keys()
        }
    
    def enable_task(self, task_name: str) -> bool:
        """Enable a task"""
        if task_name not in self.tasks:
            return False
        
        self.tasks[task_name].enabled = True
        logger.info(f"✅ Enabled task: {task_name}")
        return True
    
    def disable_task(self, task_name: str) -> bool:
        """Disable a task"""
        if task_name not in self.tasks:
            return False
        
        self.tasks[task_name].enabled = False
        logger.info(f"⏸️ Disabled task: {task_name}")
        return True
    
    def add_custom_task(
        self, 
        name: str, 
        task_type: LifecycleTaskType, 
        interval_minutes: int
    ) -> bool:
        """Add a custom task with specific interval"""
        if name in self.tasks:
            logger.warning(f"Task {name} already exists")
            return False
        
        task = ScheduledTask(
            name=name,
            task_type=task_type,
            interval=ScheduleInterval.CUSTOM,
            custom_interval_minutes=interval_minutes
        )
        
        self.tasks[name] = task
        self._calculate_next_run(task)
        
        logger.info(f"➕ Added custom task: {name} (every {interval_minutes} minutes)")
        return True
    
    def remove_task(self, task_name: str) -> bool:
        """Remove a task"""
        if task_name not in self.tasks:
            return False
        
        del self.tasks[task_name]
        logger.info(f"➖ Removed task: {task_name}")
        return True
    
    def get_scheduler_status(self) -> Dict:
        """Get overall scheduler status"""
        return {
            "running": self.running,
            "total_tasks": len(self.tasks),
            "enabled_tasks": sum(1 for task in self.tasks.values() if task.enabled),
            "disabled_tasks": sum(1 for task in self.tasks.values() if not task.enabled),
            "total_runs": sum(task.run_count for task in self.tasks.values()),
            "total_errors": sum(task.error_count for task in self.tasks.values()),
            "next_task_run": min(
                (task.next_run for task in self.tasks.values() 
                 if task.enabled and task.next_run),
                default=None
            ).isoformat() if min(
                (task.next_run for task in self.tasks.values() 
                 if task.enabled and task.next_run),
                default=None
            ) else None
        }


# Global scheduler instance
_scheduler: Optional[TaskScheduler] = None


def get_scheduler() -> TaskScheduler:
    """Get the global task scheduler instance"""
    global _scheduler
    if _scheduler is None:
        _scheduler = TaskScheduler()
    return _scheduler


async def start_scheduler():
    """Start the global task scheduler"""
    scheduler = get_scheduler()
    await scheduler.start()


async def stop_scheduler():
    """Stop the global task scheduler"""
    global _scheduler
    if _scheduler:
        await _scheduler.stop()
        _scheduler = None