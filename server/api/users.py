# api/users.py - User email management endpoints
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from datetime import datetime
import logging

from database import db

router = APIRouter()
logger = logging.getLogger(__name__)

class UpdateEmailRequest(BaseModel):
    user_id: str
    email: EmailStr

class UserResponse(BaseModel):
    user_id: str
    email: str = None
    email_notifications: bool = True
    created_at: str

@router.post("/email")
async def update_user_email(request: UpdateEmailRequest):
    """Update user's email address for notifications"""
    try:
        success = await db.update_user_email(request.user_id, request.email)
        
        if success:
            logger.info(f"📧 Updated email for user {request.user_id}: {request.email}")
            return {
                "success": True,
                "message": f"Email updated for user {request.user_id}",
                "user_id": request.user_id,
                "email": request.email,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to update email")
            
    except Exception as e:
        logger.error(f"Error updating email: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/email/{user_id}")
async def get_user_email(user_id: str):
    """Get user's email address"""
    try:
        email = await db.get_user_email(user_id)
        
        return {
            "user_id": user_id,
            "email": email,
            "has_email": email is not None,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting user email: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}")
async def get_user_profile(user_id: str):
    """Get complete user profile"""
    try:
        user = await db.get_or_create_user(user_id)
        
        return UserResponse(
            user_id=user.user_id,
            email=user.email,
            email_notifications=user.email_notifications,
            created_at=user.created_at.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))