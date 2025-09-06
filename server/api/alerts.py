# api/alerts.py - Alerts API endpoints
from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime

from database import db, AlertCondition
from models import AlertResponse, CreateAlertRequest, AlertListResponse
from services.nlp_service import nlp_service

router = APIRouter()

@router.get("/")
async def get_all_alerts():
    """Get all alerts (for admin/debugging)"""
    try:
        alerts = await db.get_active_alerts()
        alert_responses = []
        
        for alert in alerts:
            alert_responses.append(AlertResponse(
                id=alert.id,
                message=alert.message,
                status=alert.status,
                condition_type=alert.condition.condition_type,
                tokens=alert.condition.tokens,
                threshold=alert.condition.threshold,
                created_at=alert.created_at.isoformat(),
                triggered_at=alert.triggered_at.isoformat() if alert.triggered_at else None
            ))
        
        return AlertListResponse(
            alerts=alert_responses,
            total=len(alert_responses)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alerts: {str(e)}")

@router.get("/user/{user_id}")
async def get_user_alerts(user_id: str):
    """Get all alerts for a specific user"""
    try:
        alerts = await db.get_user_alerts(user_id)
        alert_responses = []
        
        for alert in alerts:
            alert_responses.append(AlertResponse(
                id=alert.id,
                message=alert.message,
                status=alert.status,
                condition_type=alert.condition.condition_type,
                tokens=alert.condition.tokens,
                threshold=alert.condition.threshold,
                created_at=alert.created_at.isoformat(),
                triggered_at=alert.triggered_at.isoformat() if alert.triggered_at else None
            ))
        
        return AlertListResponse(
            alerts=alert_responses,
            total=len(alert_responses)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user alerts: {str(e)}")

@router.post("/create")
async def create_alert(request: CreateAlertRequest):
    """Create a new alert by parsing natural language"""
    try:
        # Parse the message using NLP service
        parsed_condition = await nlp_service.parse_message(request.message)
        
        if not parsed_condition:
            raise HTTPException(
                status_code=400, 
                detail="Could not understand the alert request. Try: 'Alert me when ETH hits $4000'"
            )
        
        # Create AlertCondition object
        condition = AlertCondition(
            tokens=parsed_condition.tokens,
            condition_type=parsed_condition.condition_type,
            threshold=parsed_condition.threshold,
            timeframe=parsed_condition.timeframe,
            secondary_condition=parsed_condition.secondary_condition
        )
        
        # Create alert in database
        alert_id = await db.create_alert(
            user_id=request.user_id,
            condition=condition,
            message=request.message
        )
        
        return {
            "success": True,
            "alert_id": alert_id,
            "message": f"Alert created successfully for {', '.join(parsed_condition.tokens)}",
            "condition": {
                "type": parsed_condition.condition_type,
                "tokens": parsed_condition.tokens,
                "threshold": parsed_condition.threshold,
                "timeframe": parsed_condition.timeframe
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create alert: {str(e)}")

@router.patch("/{alert_id}/status")
async def update_alert_status(alert_id: str, status: str):
    """Update alert status (active, paused, triggered, expired)"""
    try:
        valid_statuses = ["active", "paused", "triggered", "expired"]
        if status not in valid_statuses:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        
        await db.update_alert_status(alert_id, status)
        
        return {
            "success": True,
            "alert_id": alert_id,
            "new_status": status,
            "updated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update alert status: {str(e)}")

@router.delete("/{alert_id}")
async def delete_alert(alert_id: str, user_id: str):
    """Delete an alert (user must own it)"""
    try:
        success = await db.delete_alert(alert_id, user_id)
        
        if not success:
            raise HTTPException(
                status_code=404, 
                detail="Alert not found or you don't have permission to delete it"
            )
        
        return {
            "success": True,
            "alert_id": alert_id,
            "message": "Alert deleted successfully",
            "deleted_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete alert: {str(e)}")

@router.get("/{alert_id}")
async def get_alert_details(alert_id: str):
    """Get details for a specific alert"""
    try:
        # Get all alerts and find the one with matching ID
        all_alerts = await db.get_active_alerts()
        
        for alert in all_alerts:
            if alert.id == alert_id:
                return AlertResponse(
                    id=alert.id,
                    message=alert.message,
                    status=alert.status,
                    condition_type=alert.condition.condition_type,
                    tokens=alert.condition.tokens,
                    threshold=alert.condition.threshold,
                    created_at=alert.created_at.isoformat(),
                    triggered_at=alert.triggered_at.isoformat() if alert.triggered_at else None
                )
        
        raise HTTPException(status_code=404, detail="Alert not found")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alert details: {str(e)}")

@router.post("/batch-create")
async def create_multiple_alerts(requests: List[CreateAlertRequest]):
    """Create multiple alerts at once"""
    try:
        created_alerts = []
        errors = []
        
        for i, request in enumerate(requests):
            try:
                # Parse the message
                parsed_condition = await nlp_service.parse_message(request.message)
                
                if not parsed_condition:
                    errors.append({
                        "index": i,
                        "message": request.message,
                        "error": "Could not parse alert request"
                    })
                    continue
                
                # Create condition
                condition = AlertCondition(
                    tokens=parsed_condition.tokens,
                    condition_type=parsed_condition.condition_type,
                    threshold=parsed_condition.threshold,
                    timeframe=parsed_condition.timeframe,
                    secondary_condition=parsed_condition.secondary_condition
                )
                
                # Create alert
                alert_id = await db.create_alert(
                    user_id=request.user_id,
                    condition=condition,
                    message=request.message
                )
                
                created_alerts.append({
                    "index": i,
                    "alert_id": alert_id,
                    "message": request.message,
                    "tokens": parsed_condition.tokens
                })
                
            except Exception as e:
                errors.append({
                    "index": i,
                    "message": request.message,
                    "error": str(e)
                })
        
        return {
            "success": len(created_alerts) > 0,
            "created_count": len(created_alerts),
            "error_count": len(errors),
            "created_alerts": created_alerts,
            "errors": errors
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create multiple alerts: {str(e)}")