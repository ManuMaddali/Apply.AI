"""
Webhook Logger - Logging and monitoring for webhook events

This service handles:
- Webhook event logging for debugging and monitoring
- Retry attempt tracking
- Error analysis and reporting
- Webhook performance metrics
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import Column, String, DateTime, Integer, Text, Boolean, Enum
from sqlalchemy.sql import func
import json
import enum

from models.user import Base, GUID
import uuid

logger = logging.getLogger(__name__)


class WebhookEventStatus(enum.Enum):
    RECEIVED = "received"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    RETRYING = "retrying"
    IGNORED = "ignored"


class WebhookEvent(Base):
    """Model for tracking webhook events"""
    __tablename__ = "webhook_events"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    
    # Event details
    event_type = Column(String(100), nullable=False, index=True)
    stripe_event_id = Column(String(255), unique=True, nullable=True, index=True)
    status = Column(Enum(WebhookEventStatus), nullable=False, default=WebhookEventStatus.RECEIVED)
    
    # Processing details
    attempts = Column(Integer, default=0)
    last_attempt_at = Column(DateTime, nullable=True)
    processed_at = Column(DateTime, nullable=True)
    
    # Event data
    payload = Column(Text, nullable=True)  # JSON string of the event payload
    signature = Column(String(500), nullable=True)
    
    # Results
    result = Column(Text, nullable=True)  # JSON string of processing result
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "event_type": self.event_type,
            "stripe_event_id": self.stripe_event_id,
            "status": self.status.value,
            "attempts": self.attempts,
            "last_attempt_at": self.last_attempt_at.isoformat() if self.last_attempt_at else None,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class WebhookLogger:
    """Service for logging and monitoring webhook events"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def log_webhook_received(
        self,
        event_type: str,
        payload: bytes,
        signature: str,
        stripe_event_id: Optional[str] = None
    ) -> WebhookEvent:
        """Log that a webhook event was received"""
        try:
            webhook_event = WebhookEvent(
                event_type=event_type,
                stripe_event_id=stripe_event_id,
                status=WebhookEventStatus.RECEIVED,
                payload=payload.decode('utf-8') if payload else None,
                signature=signature,
                attempts=0
            )
            
            self.db.add(webhook_event)
            self.db.commit()
            self.db.refresh(webhook_event)
            
            logger.info(f"Logged webhook event: {event_type} (ID: {webhook_event.id})")
            return webhook_event
            
        except Exception as e:
            logger.error(f"Error logging webhook event: {e}")
            self.db.rollback()
            raise
    
    def log_processing_start(self, webhook_event_id: str) -> bool:
        """Log that webhook processing has started"""
        try:
            webhook_event = self.db.query(WebhookEvent).filter(
                WebhookEvent.id == webhook_event_id
            ).first()
            
            if webhook_event:
                webhook_event.status = WebhookEventStatus.PROCESSING
                webhook_event.attempts += 1
                webhook_event.last_attempt_at = datetime.utcnow()
                self.db.commit()
                
                logger.info(f"Started processing webhook event {webhook_event_id} (attempt {webhook_event.attempts})")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error logging processing start: {e}")
            self.db.rollback()
            return False
    
    def log_processing_success(
        self,
        webhook_event_id: str,
        result: Dict[str, Any]
    ) -> bool:
        """Log successful webhook processing"""
        try:
            webhook_event = self.db.query(WebhookEvent).filter(
                WebhookEvent.id == webhook_event_id
            ).first()
            
            if webhook_event:
                webhook_event.status = WebhookEventStatus.PROCESSED
                webhook_event.processed_at = datetime.utcnow()
                webhook_event.result = json.dumps(result)
                webhook_event.error_message = None
                self.db.commit()
                
                logger.info(f"Successfully processed webhook event {webhook_event_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error logging processing success: {e}")
            self.db.rollback()
            return False
    
    def log_processing_failure(
        self,
        webhook_event_id: str,
        error_message: str,
        will_retry: bool = False
    ) -> bool:
        """Log failed webhook processing"""
        try:
            webhook_event = self.db.query(WebhookEvent).filter(
                WebhookEvent.id == webhook_event_id
            ).first()
            
            if webhook_event:
                webhook_event.status = WebhookEventStatus.RETRYING if will_retry else WebhookEventStatus.FAILED
                webhook_event.error_message = error_message
                self.db.commit()
                
                status_msg = "retrying" if will_retry else "failed"
                logger.warning(f"Webhook event {webhook_event_id} {status_msg}: {error_message}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error logging processing failure: {e}")
            self.db.rollback()
            return False
    
    def log_processing_ignored(
        self,
        webhook_event_id: str,
        reason: str
    ) -> bool:
        """Log that webhook processing was ignored"""
        try:
            webhook_event = self.db.query(WebhookEvent).filter(
                WebhookEvent.id == webhook_event_id
            ).first()
            
            if webhook_event:
                webhook_event.status = WebhookEventStatus.IGNORED
                webhook_event.processed_at = datetime.utcnow()
                webhook_event.result = json.dumps({"status": "ignored", "reason": reason})
                self.db.commit()
                
                logger.info(f"Ignored webhook event {webhook_event_id}: {reason}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error logging processing ignored: {e}")
            self.db.rollback()
            return False
    
    def get_webhook_events(
        self,
        limit: int = 100,
        event_type: Optional[str] = None,
        status: Optional[WebhookEventStatus] = None,
        hours_back: int = 24
    ) -> List[WebhookEvent]:
        """Get recent webhook events"""
        try:
            query = self.db.query(WebhookEvent)
            
            # Filter by time
            since = datetime.utcnow() - timedelta(hours=hours_back)
            query = query.filter(WebhookEvent.created_at >= since)
            
            # Filter by event type
            if event_type:
                query = query.filter(WebhookEvent.event_type == event_type)
            
            # Filter by status
            if status:
                query = query.filter(WebhookEvent.status == status)
            
            # Order by most recent first
            query = query.order_by(WebhookEvent.created_at.desc())
            
            # Limit results
            return query.limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting webhook events: {e}")
            return []
    
    def get_webhook_statistics(self, hours_back: int = 24) -> Dict[str, Any]:
        """Get webhook processing statistics"""
        try:
            since = datetime.utcnow() - timedelta(hours=hours_back)
            
            # Total events
            total_events = self.db.query(WebhookEvent).filter(
                WebhookEvent.created_at >= since
            ).count()
            
            # Events by status
            status_counts = {}
            for status in WebhookEventStatus:
                count = self.db.query(WebhookEvent).filter(
                    WebhookEvent.created_at >= since,
                    WebhookEvent.status == status
                ).count()
                status_counts[status.value] = count
            
            # Events by type
            type_counts = {}
            event_types = self.db.query(WebhookEvent.event_type).filter(
                WebhookEvent.created_at >= since
            ).distinct().all()
            
            for (event_type,) in event_types:
                count = self.db.query(WebhookEvent).filter(
                    WebhookEvent.created_at >= since,
                    WebhookEvent.event_type == event_type
                ).count()
                type_counts[event_type] = count
            
            # Failed events that need attention
            failed_events = self.db.query(WebhookEvent).filter(
                WebhookEvent.created_at >= since,
                WebhookEvent.status == WebhookEventStatus.FAILED
            ).count()
            
            # Average processing time (for processed events)
            processed_events = self.db.query(WebhookEvent).filter(
                WebhookEvent.created_at >= since,
                WebhookEvent.status == WebhookEventStatus.PROCESSED,
                WebhookEvent.processed_at.isnot(None)
            ).all()
            
            avg_processing_time = 0
            if processed_events:
                total_time = sum([
                    (event.processed_at - event.created_at).total_seconds()
                    for event in processed_events
                ])
                avg_processing_time = total_time / len(processed_events)
            
            return {
                "period_hours": hours_back,
                "total_events": total_events,
                "status_breakdown": status_counts,
                "event_type_breakdown": type_counts,
                "failed_events": failed_events,
                "success_rate": (status_counts.get("processed", 0) / max(1, total_events)) * 100,
                "average_processing_time_seconds": round(avg_processing_time, 2),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting webhook statistics: {e}")
            return {}
    
    def cleanup_old_events(self, days_to_keep: int = 30) -> int:
        """Clean up old webhook events"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            deleted_count = self.db.query(WebhookEvent).filter(
                WebhookEvent.created_at < cutoff_date
            ).delete()
            
            self.db.commit()
            
            logger.info(f"Cleaned up {deleted_count} old webhook events")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old webhook events: {e}")
            self.db.rollback()
            return 0