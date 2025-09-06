# api/alerts.py - Complete Alert API endpoints
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
import json
from datetime import datetime

from database import Database, AlertCondition, get_database
from models import AlertResponse, AlertListResponse

router = APIRouter()

@router.get("/", response_model=AlertListResponse)
async def get_alerts(
    user_id: str = Query(default="default_user", description="User ID to get alerts for"),
    status: Optional[str] = Query(default=None, description="Filter by status: active, paused, triggered"),
    db: Database = Depends(get_database)
):
    """Get all alerts for a user with optional status filter"""
    try:
        if status:
            # Get alerts filtered by status
            alerts = await db.get_user_alerts_by_status(user_id, status)
        else:
            alerts = await db.get_user_alerts(user_id)
        
        alert_responses = []
        for alert in alerts:
            alert_response = AlertResponse(
                id=alert.id,
                message=alert.message,
                status=alert.status,
                condition_type=alert.condition.condition_type,
                tokens=alert.condition.tokens,
                threshold=alert.condition.threshold,
                created_at=alert.created_at.isoformat(),
                triggered_at=alert.triggered_at.isoformat() if alert.triggered_at else None
            )
            alert_responses.append(alert_response)
        
        return AlertListResponse(alerts=alert_responses, total=len(alert_responses))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching alerts: {str(e)}")

@router.post("/create")
async def create_alert_simple(
    user_id: str = Query(..., description="User ID"),
    message: str = Query(..., description="Human readable alert message"),
    condition_type: str = Query(..., description="Type: price_above, price_below, price_change"),
    tokens: str = Query(..., description="Comma-separated tokens: ETH,BTC"),
    threshold: float = Query(..., description="Price threshold or percentage change"),
    timeframe: str = Query(default="24h", description="Time window: 1h, 24h, 7d"),
    db: Database = Depends(get_database)
):
    """Create a simple alert (for testing before NLP integration)"""
    try:
        # Parse tokens
        token_list = [token.strip().upper() for token in tokens.split(",")]
        
        # Validate condition type
        valid_types = ["price_above", "price_below", "price_change", "relative_change"]
        if condition_type not in valid_types:
            raise HTTPException(status_code=400, detail=f"Invalid condition_type. Must be one of: {valid_types}")
        
        # Create condition
        condition = AlertCondition(
            tokens=token_list,
            condition_type=condition_type,
            threshold=threshold,
            timeframe=timeframe
        )
        
        # Create alert
        alert_id = await db.create_alert(
            user_id=user_id,
            condition=condition,
            message=message
        )
        
        return {
            "success": True,
            "alert_id": alert_id,
            "message": f"Created alert: {message}",
            "condition": {
                "type": condition_type,
                "tokens": token_list,
                "threshold": threshold,
                "timeframe": timeframe
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating alert: {str(e)}")

@router.put("/{alert_id}/status")
async def update_alert_status(
    alert_id: str,
    status: str = Query(..., description="New status: active, paused, triggered, expired"),
    user_id: str = Query(default="default_user", description="User ID for ownership verification"),
    db: Database = Depends(get_database)
):
    """Update alert status (pause, resume, etc.)"""
    try:
        # Validate status
        valid_statuses = ["active", "paused", "triggered", "expired"]
        if status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
        
        await db.update_alert_status(alert_id, status)
        
        return {
            "success": True,
            "message": f"Alert {alert_id[:8]} status updated to {status}"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating alert: {str(e)}")

@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: str,
    user_id: str = Query(default="default_user", description="User ID for ownership verification"),
    db: Database = Depends(get_database)
):
    """Delete an alert"""
    try:
        success = await db.delete_alert(alert_id, user_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Alert not found or not owned by user")
        
        return {
            "success": True,
            "message": f"Alert {alert_id[:8]} deleted"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting alert: {str(e)}")

@router.get("/active")
async def get_active_alerts(db: Database = Depends(get_database)):
    """Get all active alerts (for monitoring system)"""
    try:
        alerts = await db.get_active_alerts()
        
        return {
            "active_alerts": len(alerts),
            "alerts": [
                {
                    "id": alert.id[:8],  # Show short ID for security
                    "user_id": alert.user_id,
                    "message": alert.message,
                    "condition": {
                        "type": alert.condition.condition_type,
                        "tokens": alert.condition.tokens,
                        "threshold": alert.condition.threshold
                    },
                    "created_at": alert.created_at.isoformat()
                }
                for alert in alerts
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching active alerts: {str(e)}")