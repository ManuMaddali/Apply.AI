"""
WebSocket API for Real-time Communication

This module provides WebSocket endpoints for real-time processing updates,
Server-Sent Events for analytics, and optimistic updates for immediate UI feedback.
Includes fallback mechanisms for connection issues.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
import asyncio
import json
import uuid
import logging
from datetime import datetime
import time

# Import existing dependencies to maintain compatibility
from config.database import get_db
from models.user import User
from utils.auth import AuthManager
from utils.rate_limiter import limiter

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/websocket", tags=["websocket"])

# ============================================================================
# WEBSOCKET CONNECTION MANAGEMENT
# ============================================================================

class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[str, List[str]] = {}  # user_id -> [connection_ids]
        self.processing_subscriptions: Dict[str, List[str]] = {}  # processing_id -> [connection_ids]
    
    async def connect(self, websocket: WebSocket, connection_id: str, user_id: str):
        """Accept WebSocket connection and register it"""
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        
        # Track user connections
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        self.user_connections[user_id].append(connection_id)
        
        logger.info(f"WebSocket connection established: {connection_id} for user {user_id}")
    
    def disconnect(self, connection_id: str, user_id: str):
        """Remove WebSocket connection"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        # Remove from user connections
        if user_id in self.user_connections:
            if connection_id in self.user_connections[user_id]:
                self.user_connections[user_id].remove(connection_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        # Remove from processing subscriptions
        for processing_id in list(self.processing_subscriptions.keys()):
            if connection_id in self.processing_subscriptions[processing_id]:
                self.processing_subscriptions[processing_id].remove(connection_id)
                if not self.processing_subscriptions[processing_id]:
                    del self.processing_subscriptions[processing_id]
        
        logger.info(f"WebSocket connection closed: {connection_id} for user {user_id}")
    
    async def send_personal_message(self, message: dict, user_id: str):
        """Send message to all connections for a specific user"""
        if user_id in self.user_connections:
            disconnected_connections = []
            
            for connection_id in self.user_connections[user_id]:
                if connection_id in self.active_connections:
                    try:
                        await self.active_connections[connection_id].send_text(json.dumps(message))
                    except Exception as e:
                        logger.error(f"Error sending message to {connection_id}: {e}")
                        disconnected_connections.append(connection_id)
                else:
                    disconnected_connections.append(connection_id)
            
            # Clean up disconnected connections
            for connection_id in disconnected_connections:
                self.disconnect(connection_id, user_id)
    
    async def send_processing_update(self, message: dict, processing_id: str):
        """Send processing update to all subscribed connections"""
        if processing_id in self.processing_subscriptions:
            disconnected_connections = []
            
            for connection_id in self.processing_subscriptions[processing_id]:
                if connection_id in self.active_connections:
                    try:
                        await self.active_connections[connection_id].send_text(json.dumps(message))
                    except Exception as e:
                        logger.error(f"Error sending processing update to {connection_id}: {e}")
                        disconnected_connections.append(connection_id)
                else:
                    disconnected_connections.append(connection_id)
            
            # Clean up disconnected connections
            for connection_id in disconnected_connections:
                if connection_id in self.processing_subscriptions[processing_id]:
                    self.processing_subscriptions[processing_id].remove(connection_id)
    
    def subscribe_to_processing(self, connection_id: str, processing_id: str):
        """Subscribe connection to processing updates"""
        if processing_id not in self.processing_subscriptions:
            self.processing_subscriptions[processing_id] = []
        
        if connection_id not in self.processing_subscriptions[processing_id]:
            self.processing_subscriptions[processing_id].append(connection_id)
            logger.info(f"Connection {connection_id} subscribed to processing {processing_id}")
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        return {
            "total_connections": len(self.active_connections),
            "users_connected": len(self.user_connections),
            "processing_subscriptions": len(self.processing_subscriptions),
            "connections_per_user": {
                user_id: len(connections) 
                for user_id, connections in self.user_connections.items()
            }
        }

# Global connection manager
connection_manager = ConnectionManager()

# ============================================================================
# WEBSOCKET ENDPOINTS
# ============================================================================

@router.websocket("/connect/{user_token}")
async def websocket_endpoint(websocket: WebSocket, user_token: str):
    """
    Main WebSocket endpoint for real-time communication.
    Handles authentication and message routing.
    """
    connection_id = str(uuid.uuid4())
    user_id = None
    
    try:
        # Authenticate user from token
        try:
            # Decode token to get user info
            from jose import jwt
            from utils.auth import SECRET_KEY, ALGORITHM
            
            payload = jwt.decode(user_token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            
            if not user_id:
                await websocket.close(code=4001, reason="Invalid token")
                return
                
        except Exception as e:
            logger.error(f"WebSocket authentication failed: {e}")
            await websocket.close(code=4001, reason="Authentication failed")
            return
        
        # Accept connection
        await connection_manager.connect(websocket, connection_id, user_id)
        
        # Send connection confirmation
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "connection_id": connection_id,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "message": "WebSocket connection established successfully"
        }))
        
        # Handle incoming messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                await handle_websocket_message(websocket, connection_id, user_id, message)
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format",
                    "timestamp": datetime.utcnow().isoformat()
                }))
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Internal server error",
                    "timestamp": datetime.utcnow().isoformat()
                }))
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        if user_id:
            connection_manager.disconnect(connection_id, user_id)

async def handle_websocket_message(websocket: WebSocket, connection_id: str, user_id: str, message: dict):
    """Handle incoming WebSocket messages"""
    
    message_type = message.get("type")
    
    if message_type == "subscribe_processing":
        # Subscribe to processing updates
        processing_id = message.get("processing_id")
        if processing_id:
            connection_manager.subscribe_to_processing(connection_id, processing_id)
            await websocket.send_text(json.dumps({
                "type": "subscription_confirmed",
                "processing_id": processing_id,
                "timestamp": datetime.utcnow().isoformat()
            }))
    
    elif message_type == "ping":
        # Respond to ping with pong
        await websocket.send_text(json.dumps({
            "type": "pong",
            "timestamp": datetime.utcnow().isoformat()
        }))
    
    elif message_type == "get_status":
        # Send current connection status
        stats = connection_manager.get_connection_stats()
        await websocket.send_text(json.dumps({
            "type": "status_response",
            "connection_stats": stats,
            "your_connection_id": connection_id,
            "timestamp": datetime.utcnow().isoformat()
        }))
    
    else:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": f"Unknown message type: {message_type}",
            "timestamp": datetime.utcnow().isoformat()
        }))

# ============================================================================
# SERVER-SENT EVENTS FOR REAL-TIME ANALYTICS
# ============================================================================

@router.get("/events/analytics/{user_token}")
async def analytics_events_stream(user_token: str):
    """
    Server-Sent Events endpoint for real-time analytics updates.
    Provides continuous stream of analytics data.
    """
    
    async def event_generator():
        try:
            # Authenticate user
            from jose import jwt
            from utils.auth import SECRET_KEY, ALGORITHM
            
            payload = jwt.decode(user_token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            
            if not user_id:
                yield f"event: error\ndata: {json.dumps({'error': 'Invalid token'})}\n\n"
                return
            
            # Send initial connection event
            yield f"event: connected\ndata: {json.dumps({'user_id': user_id, 'timestamp': datetime.utcnow().isoformat()})}\n\n"
            
            # Send periodic analytics updates
            while True:
                try:
                    # Generate sample analytics data (would be real data in production)
                    analytics_data = {
                        "type": "analytics_update",
                        "timestamp": datetime.utcnow().isoformat(),
                        "data": {
                            "active_processing_jobs": len(connection_manager.processing_subscriptions),
                            "total_connections": len(connection_manager.active_connections),
                            "user_activity": {
                                "current_users": len(connection_manager.user_connections),
                                "processing_rate": "2.3 jobs/minute",
                                "success_rate": "94.2%"
                            },
                            "system_metrics": {
                                "cpu_usage": "23%",
                                "memory_usage": "67%",
                                "response_time": "1.2s"
                            }
                        }
                    }
                    
                    yield f"event: analytics\ndata: {json.dumps(analytics_data)}\n\n"
                    
                    # Wait before next update
                    await asyncio.sleep(5)  # Update every 5 seconds
                    
                except Exception as e:
                    logger.error(f"Error in analytics stream: {e}")
                    yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
                    break
                    
        except Exception as e:
            logger.error(f"Analytics stream authentication failed: {e}")
            yield f"event: error\ndata: {json.dumps({'error': 'Authentication failed'})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )

@router.get("/events/processing/{processing_id}/{user_token}")
async def processing_events_stream(processing_id: str, user_token: str):
    """
    Server-Sent Events endpoint for specific processing job updates.
    """
    
    async def event_generator():
        try:
            # Authenticate user
            from jose import jwt
            from utils.auth import SECRET_KEY, ALGORITHM
            
            payload = jwt.decode(user_token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            
            if not user_id:
                yield f"event: error\ndata: {json.dumps({'error': 'Invalid token'})}\n\n"
                return
            
            # Import processing status store from app_redesign_api
            from routes.app_redesign_api import processing_status_store
            
            # Send initial connection event
            yield f"event: connected\ndata: {json.dumps({'processing_id': processing_id, 'user_id': user_id})}\n\n"
            
            last_update = None
            
            # Stream processing updates
            while True:
                try:
                    if processing_id in processing_status_store:
                        status_data = processing_status_store[processing_id]
                        
                        # Check if user owns this processing job
                        if status_data.get("user_id") != user_id:
                            yield f"event: error\ndata: {json.dumps({'error': 'Access denied'})}\n\n"
                            break
                        
                        # Send update if status changed
                        current_update = status_data.get("updated_at", status_data.get("created_at"))
                        if current_update != last_update:
                            
                            update_data = {
                                "type": "processing_update",
                                "processing_id": processing_id,
                                "status": status_data.get("status"),
                                "progress": status_data.get("progress", {}),
                                "current_step": status_data.get("current_step"),
                                "estimated_time_remaining": status_data.get("estimated_time_remaining"),
                                "timestamp": datetime.utcnow().isoformat()
                            }
                            
                            # Include results if completed
                            if status_data.get("status") == "completed":
                                update_data["results"] = status_data.get("results")
                                update_data["analytics"] = status_data.get("analytics")
                            
                            yield f"event: processing_update\ndata: {json.dumps(update_data)}\n\n"
                            last_update = current_update
                            
                            # Stop streaming if processing is completed or failed
                            if status_data.get("status") in ["completed", "failed"]:
                                yield f"event: processing_complete\ndata: {json.dumps({'status': status_data.get('status')})}\n\n"
                                break
                    
                    else:
                        yield f"event: error\ndata: {json.dumps({'error': 'Processing job not found'})}\n\n"
                        break
                    
                    # Wait before next check
                    await asyncio.sleep(2)  # Check every 2 seconds
                    
                except Exception as e:
                    logger.error(f"Error in processing stream: {e}")
                    yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
                    break
                    
        except Exception as e:
            logger.error(f"Processing stream authentication failed: {e}")
            yield f"event: error\ndata: {json.dumps({'error': 'Authentication failed'})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )

# ============================================================================
# OPTIMISTIC UPDATES API
# ============================================================================

@router.post("/optimistic-update")
@limiter.limit("60/minute")
async def create_optimistic_update(
    request: Request,
    update_data: Dict[str, Any],
    user: User = Depends(AuthManager.verify_token)
):
    """
    Create optimistic update for immediate UI feedback.
    Allows UI to update immediately while processing happens in background.
    """
    try:
        update_id = str(uuid.uuid4())
        update_type = update_data.get("type", "unknown")
        
        # Store optimistic update
        optimistic_update = {
            "update_id": update_id,
            "user_id": str(user.id),
            "type": update_type,
            "data": update_data.get("data", {}),
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow().timestamp() + 300)  # 5 minutes expiry
        }
        
        # Send update to user's WebSocket connections
        await connection_manager.send_personal_message({
            "type": "optimistic_update",
            "update": optimistic_update
        }, str(user.id))
        
        return {
            "success": True,
            "update_id": update_id,
            "message": "Optimistic update created",
            "expires_in": 300
        }
        
    except Exception as e:
        logger.error(f"Error creating optimistic update: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimistic-update/{update_id}/confirm")
@limiter.limit("60/minute")
async def confirm_optimistic_update(
    request: Request,
    update_id: str,
    confirmation_data: Dict[str, Any],
    user: User = Depends(AuthManager.verify_token)
):
    """
    Confirm or reject optimistic update based on actual processing results.
    """
    try:
        # Send confirmation to user's WebSocket connections
        await connection_manager.send_personal_message({
            "type": "optimistic_update_confirmed",
            "update_id": update_id,
            "status": confirmation_data.get("status", "confirmed"),
            "actual_data": confirmation_data.get("data", {}),
            "timestamp": datetime.utcnow().isoformat()
        }, str(user.id))
        
        return {
            "success": True,
            "update_id": update_id,
            "status": confirmation_data.get("status", "confirmed"),
            "message": "Optimistic update confirmed"
        }
        
    except Exception as e:
        logger.error(f"Error confirming optimistic update: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# FALLBACK MECHANISMS
# ============================================================================

@router.get("/fallback/polling/{processing_id}")
@limiter.limit("30/minute")
async def fallback_polling_endpoint(
    request: Request,
    processing_id: str,
    user: User = Depends(AuthManager.verify_token)
):
    """
    Fallback polling endpoint for clients that can't use WebSocket or SSE.
    """
    try:
        # Import processing status store
        from routes.app_redesign_api import processing_status_store
        
        if processing_id not in processing_status_store:
            raise HTTPException(status_code=404, detail="Processing job not found")
        
        status_data = processing_status_store[processing_id]
        
        # Verify user owns this processing job
        if status_data.get("user_id") != str(user.id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Return current status
        return {
            "success": True,
            "processing_id": processing_id,
            "status": status_data.get("status"),
            "progress": status_data.get("progress", {}),
            "current_step": status_data.get("current_step"),
            "estimated_time_remaining": status_data.get("estimated_time_remaining"),
            "results": status_data.get("results") if status_data.get("status") == "completed" else None,
            "timestamp": datetime.utcnow().isoformat(),
            "next_poll_in": 5  # Suggest polling every 5 seconds
        }
        
    except Exception as e:
        logger.error(f"Error in fallback polling: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/connection-test")
async def test_connection():
    """Test endpoint to verify WebSocket service is running"""
    stats = connection_manager.get_connection_stats()
    
    return {
        "status": "healthy",
        "service": "WebSocket API",
        "timestamp": datetime.utcnow().isoformat(),
        "connection_stats": stats,
        "endpoints": {
            "websocket": "/api/websocket/connect/{user_token}",
            "analytics_sse": "/api/websocket/events/analytics/{user_token}",
            "processing_sse": "/api/websocket/events/processing/{processing_id}/{user_token}",
            "fallback_polling": "/api/websocket/fallback/polling/{processing_id}"
        }
    }

# ============================================================================
# BACKGROUND TASK FOR SENDING UPDATES
# ============================================================================

async def send_processing_update_via_websocket(processing_id: str, update_data: Dict[str, Any]):
    """
    Helper function to send processing updates via WebSocket.
    Can be called from other modules.
    """
    try:
        message = {
            "type": "processing_update",
            "processing_id": processing_id,
            "data": update_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await connection_manager.send_processing_update(message, processing_id)
        logger.info(f"Sent WebSocket update for processing {processing_id}")
        
    except Exception as e:
        logger.error(f"Error sending WebSocket update: {e}")

async def send_user_notification(user_id: str, notification: Dict[str, Any]):
    """
    Helper function to send notifications to specific user.
    Can be called from other modules.
    """
    try:
        message = {
            "type": "notification",
            "data": notification,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await connection_manager.send_personal_message(message, user_id)
        logger.info(f"Sent notification to user {user_id}")
        
    except Exception as e:
        logger.error(f"Error sending user notification: {e}")

# Export helper functions for use in other modules
__all__ = [
    "connection_manager",
    "send_processing_update_via_websocket", 
    "send_user_notification"
]