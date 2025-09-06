# api/chat.py - Fixed to accept JSON data like the test expects
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional
import json
from datetime import datetime

from database import Database, AlertCondition, get_database
from models import AlertResponse
from services.nlp_service import nlp_service
from config import settings

router = APIRouter()

# Add Pydantic models for request bodies
class ChatRequest(BaseModel):
    message: str
    user_id: str = "default_user"

class TestParsingRequest(BaseModel):
    message: str
    include_explanation: bool = True

class ComplexMessageRequest(BaseModel):
    message: str
    user_id: str = "default_user"
    context: Optional[Dict] = None

@router.post("/message")
async def chat_message(
    request: ChatRequest,  # Now accepts JSON instead of query params
    db: Database = Depends(get_database)
):
    """Process chat message with Ollama AI - accepts JSON data"""
    try:
        # Get user context for better parsing
        user_alerts = await db.get_user_alerts(request.user_id)
        user_context = {
            "recent_alerts": len(user_alerts),
            "tokens_watched": list(set([
                token for alert in user_alerts[:5] 
                for token in alert.condition.tokens
            ]))
        }
        
        # Parse message with AI
        parsed_condition = await nlp_service.parse_message(request.message, user_context)
        
        # Generate response
        response_text = await nlp_service.generate_response(parsed_condition, request.message)
        
        alert_created = False
        alert_id = None
        
        # Create alert if successful
        if parsed_condition:
            try:
                condition = AlertCondition(
                    tokens=parsed_condition.tokens,
                    condition_type=parsed_condition.condition_type,
                    threshold=parsed_condition.threshold,
                    timeframe=parsed_condition.timeframe,
                    secondary_condition=parsed_condition.secondary_condition
                )
                
                alert_id = await db.create_alert(
                    user_id=request.user_id,
                    condition=condition,
                    message=request.message
                )
                
                alert_created = True
                
            except Exception as e:
                response_text += f"\n\n⚠️ Error creating alert: {str(e)}"
        
        return {
            "response": response_text,
            "parsed": {
                "condition_type": parsed_condition.condition_type if parsed_condition else None,
                "tokens": parsed_condition.tokens if parsed_condition else None,
                "threshold": parsed_condition.threshold if parsed_condition else None,
                "confidence": parsed_condition.confidence if parsed_condition else 0.0,
                "explanation": parsed_condition.explanation if parsed_condition else None
            },
            "alert_created": alert_created,
            "alert_id": alert_id,
            "timestamp": datetime.now().isoformat(),
            "user_id": request.user_id,
            "backend": settings.get_active_backend()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@router.get("/status")
async def get_chat_status():
    """Get chat service status"""
    nlp_status = await nlp_service.get_status()
    
    return {
        "service": "StoneWatch Chat",
        "nlp_service": nlp_status,
        "configuration": {
            "primary_backend": "Ollama",
            "ollama_url": settings.OLLAMA_URL,
            "cloud_api_enabled": settings.USE_CLOUD_API,
            "active_backend": settings.get_active_backend()
        },
        "capabilities": {
            "natural_language": nlp_status["capabilities"]["natural_language"],
            "complex_conditions": nlp_status["capabilities"]["complex_conditions"], 
            "unlimited_usage": nlp_status["capabilities"]["unlimited_usage"],
            "offline_capable": nlp_status["ollama_available"]
        },
        "switch_instructions": {
            "to_claude": "Set USE_CLOUD_API=True and add CLAUDE_API_KEY in .env",
            "to_openai": "Set USE_CLOUD_API=True and add OPENAI_API_KEY in .env",
            "to_ollama": "Set USE_CLOUD_API=False in .env (default)"
        }
    }

@router.post("/test-parsing")
async def test_parsing(request: TestParsingRequest):
    """Test message parsing"""
    try:
        parsed_condition = await nlp_service.parse_message(request.message)
        response_text = await nlp_service.generate_response(parsed_condition, request.message)
        
        result = {
            "original_message": request.message,
            "parsed_successfully": parsed_condition is not None,
            "would_create_alert": parsed_condition is not None,
            "response": response_text,
            "backend": settings.get_active_backend()
        }
        
        if parsed_condition:
            result["parsed_condition"] = {
                "condition_type": parsed_condition.condition_type,
                "tokens": parsed_condition.tokens,
                "threshold": parsed_condition.threshold,
                "timeframe": parsed_condition.timeframe,
                "has_secondary_condition": parsed_condition.secondary_condition is not None,
                "confidence": parsed_condition.confidence
            }
            
            if request.include_explanation:
                result["explanation"] = parsed_condition.explanation
                
            if parsed_condition.secondary_condition:
                result["secondary_condition"] = parsed_condition.secondary_condition
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error testing parsing: {str(e)}")

@router.get("/suggestions")
async def get_suggestions():
    """Get chat suggestions based on capabilities"""
    nlp_status = await nlp_service.get_status()
    has_ai = nlp_status["capabilities"]["natural_language"]
    
    suggestions = {
        "basic": [
            "Alert me when ETH hits $4000",
            "Tell me when BTC drops below $90000",
            "Notify me when AAVE goes above $350"
        ]
    }
    
    if has_ai:
        suggestions.update({
            "natural_language": [
                "I want to be notified when ethereum reaches five thousand dollars",
                "Please tell me if bitcoin goes over one hundred thousand",
                "Let me know when any DeFi token drops fifteen percent"
            ],
            "conversational": [
                "Hey, can you watch ETH for me and let me know if it drops below 3k?",
                "I'm worried about my AAVE position, tell me if it falls 25%",
                "Keep an eye on bitcoin for me"
            ]
        })
    
    return {
        "suggestions": suggestions,
        "backend": settings.get_active_backend(),
        "ai_available": has_ai,
        "tip": "Try natural language!" if has_ai else "Use simple patterns like 'ETH above $4000'",
        "examples": {
            "price_above": ["ETH hits $5000", "Bitcoin reaches 100k"],
            "price_below": ["ETH drops below $3000", "BTC under $80k"], 
            "price_change": ["ETH drops 10%", "Bitcoin falls 5%"]
        }
    }

@router.post("/complex-message")
async def handle_complex_message(
    request: ComplexMessageRequest,
    db: Database = Depends(get_database)
):
    """Handle complex multi-condition alerts"""
    try:
        # Enhanced context for complex parsing
        enhanced_context = request.context or {}
        
        # Get current market data for context
        enhanced_context.update({
            "query_type": "complex",
            "timestamp": datetime.now().isoformat()
        })
        
        parsed_condition = await nlp_service.parse_message(request.message, enhanced_context)
        
        if not parsed_condition:
            return {
                "response": "I couldn't understand that complex query. Try breaking it down into simpler parts.",
                "suggestion": "For complex alerts like 'when X drops while Y stays stable', try simpler alerts first.",
                "parsed": None
            }
        
        # For complex conditions, we might create multiple alerts
        if parsed_condition.condition_type == "relative_change" and parsed_condition.secondary_condition:
            # This is a complex condition - handle specially
            response_text = await nlp_service.generate_response(parsed_condition, request.message)
            
            # Create the main alert
            condition = AlertCondition(
                tokens=parsed_condition.tokens,
                condition_type=parsed_condition.condition_type,
                threshold=parsed_condition.threshold,
                timeframe=parsed_condition.timeframe,
                secondary_condition=parsed_condition.secondary_condition
            )
            
            alert_id = await db.create_alert(
                user_id=request.user_id,
                condition=condition,
                message=request.message
            )
            
            return {
                "response": f"🚨 Complex alert created! {response_text}",
                "alert_id": alert_id,
                "complexity": "high",
                "requires_monitoring": True,
                "parsed": {
                    "primary_condition": {
                        "tokens": parsed_condition.tokens,
                        "type": parsed_condition.condition_type,
                        "threshold": parsed_condition.threshold
                    },
                    "secondary_condition": parsed_condition.secondary_condition
                }
            }
        
        # Fall back to simple processing
        chat_request = ChatRequest(message=request.message, user_id=request.user_id)
        return await chat_message(chat_request, db)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing complex message: {str(e)}")

@router.get("/conversation/{user_id}")
async def get_conversation(
    user_id: str,
    limit: int = 20,
    db: Database = Depends(get_database)
):
    """Get conversation history"""
    try:
        alerts = await db.get_user_alerts(user_id)
        
        conversation = []
        for alert in alerts[:limit]:
            # User message
            conversation.append({
                "type": "user",
                "message": alert.message,
                "timestamp": alert.created_at.isoformat()
            })
            
            # Assistant response
            condition = alert.condition
            if condition.condition_type == "price_above":
                response = f"✅ I'll monitor {', '.join(condition.tokens)} and alert you when it goes above ${condition.threshold:,.2f}"
            elif condition.condition_type == "price_below":
                response = f"✅ I'll monitor {', '.join(condition.tokens)} and alert you when it drops below ${condition.threshold:,.2f}"
            elif condition.condition_type == "price_change":
                percentage = abs(condition.threshold * 100)
                direction = "drops" if condition.threshold < 0 else "rises"
                response = f"✅ I'll alert you when {', '.join(condition.tokens)} {direction} {percentage}%"
            else:
                response = f"✅ Alert set for {', '.join(condition.tokens)}"
            
            # Add status indicator
            status_emoji = {"active": "🟢", "paused": "⏸️", "triggered": "🔔", "expired": "⏹️"}
            status = status_emoji.get(alert.status, "⚪")
            
            conversation.append({
                "type": "assistant",
                "message": f"{response} {status}",
                "timestamp": alert.created_at.isoformat(),
                "alert_id": alert.id,
                "status": alert.status
            })
        
        return {
            "conversation": list(reversed(conversation)),
            "total_messages": len(conversation),
            "user_id": user_id,
            "backend": settings.get_active_backend(),
            "summary": {
                "total_alerts": len(alerts),
                "active_alerts": len([a for a in alerts if a.status == "active"]),
                "tokens_watched": list(set([token for alert in alerts for token in alert.condition.tokens]))
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching conversation: {str(e)}")

# Cleanup on shutdown
@router.on_event("shutdown")
async def shutdown_chat():
    """Cleanup chat service"""
    await nlp_service.close()