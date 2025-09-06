# api/chat.py - Enhanced chat interface with OpenAI
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Optional
import json
from datetime import datetime

from database import Database, AlertCondition, get_database
from models import AlertResponse
from services.nlp_service import OpenAINLPService, ParsedCondition
from config import settings

router = APIRouter()

# Initialize the enhanced NLP service
nlp_service = OpenAINLPService()

@router.post("/message")
async def chat_message(
    message: str,
    user_id: str = "default_user",
    db: Database = Depends(get_database)
):
    """Process a chat message with OpenAI-powered NLP"""
    try:
        # Check if OpenAI is configured
        has_openai = settings.validate_openai_key()
        
        # Get user context (recent alerts for better understanding)
        user_alerts = await db.get_user_alerts(user_id)
        user_context = {
            "recent_alerts": len(user_alerts),
            "tokens_watched": list(set([
                token for alert in user_alerts[:5] 
                for token in alert.condition.tokens
            ]))
        }
        
        # Parse the message with OpenAI
        parsed_condition = await nlp_service.parse_message(message, user_context)
        
        # Generate response
        response_text = await nlp_service.generate_response(parsed_condition, message)
        
        alert_created = False
        alert_id = None
        
        # Create alert if parsing was successful
        if parsed_condition:
            try:
                # Handle special secondary conditions for complex alerts
                secondary_condition = None
                if parsed_condition.secondary_condition:
                    secondary_condition = parsed_condition.secondary_condition
                
                condition = AlertCondition(
                    tokens=parsed_condition.tokens,
                    condition_type=parsed_condition.condition_type,
                    threshold=parsed_condition.threshold,
                    timeframe=parsed_condition.timeframe,
                    secondary_condition=secondary_condition
                )
                
                alert_id = await db.create_alert(
                    user_id=user_id,
                    condition=condition,
                    message=message
                )
                
                alert_created = True
                
                # Add success indicator to response if not already there
                if not response_text.startswith("✅") and not response_text.startswith("🚨"):
                    response_text = "✅ " + response_text
                
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
            "user_id": user_id,
            "ai_powered": has_openai,
            "user_context": user_context
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@router.post("/complex-message")
async def handle_complex_message(
    message: str,
    user_id: str = "default_user",
    context: Optional[Dict] = None,
    db: Database = Depends(get_database)
):
    """Handle complex multi-condition alerts"""
    try:
        # Enhanced context for complex parsing
        enhanced_context = context or {}
        
        # Get current market data for context
        # (This could be enhanced with actual price data)
        enhanced_context.update({
            "query_type": "complex",
            "timestamp": datetime.now().isoformat()
        })
        
        parsed_condition = await nlp_service.parse_message(message, enhanced_context)
        
        if not parsed_condition:
            return {
                "response": "I couldn't understand that complex query. Try breaking it down into simpler parts.",
                "suggestion": "For complex alerts like 'when X drops while Y stays stable', try simpler alerts first.",
                "parsed": None
            }
        
        # For complex conditions, we might create multiple alerts
        if parsed_condition.condition_type == "relative_change" and parsed_condition.secondary_condition:
            # This is a complex condition - handle specially
            response_text = await nlp_service.generate_response(parsed_condition, message)
            
            # Create the main alert
            condition = AlertCondition(
                tokens=parsed_condition.tokens,
                condition_type=parsed_condition.condition_type,
                threshold=parsed_condition.threshold,
                timeframe=parsed_condition.timeframe,
                secondary_condition=parsed_condition.secondary_condition
            )
            
            alert_id = await db.create_alert(
                user_id=user_id,
                condition=condition,
                message=message
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
        return await chat_message(message, user_id, db)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing complex message: {str(e)}")

@router.get("/conversation/{user_id}")
async def get_conversation_history(
    user_id: str,
    limit: int = 20,
    db: Database = Depends(get_database)
):
    """Get enhanced conversation history with AI insights"""
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
            
            # Enhanced assistant response with more context
            condition = alert.condition
            
            # Generate contextual response
            if condition.condition_type == "price_above":
                response = f"✅ I'll monitor {', '.join(condition.tokens)} and alert you when the price goes above ${condition.threshold:,.2f}"
            elif condition.condition_type == "price_below":
                response = f"✅ I'll monitor {', '.join(condition.tokens)} and alert you when the price drops below ${condition.threshold:,.2f}"
            elif condition.condition_type == "price_change":
                percentage = abs(condition.threshold * 100)
                direction = "drops" if condition.threshold < 0 else "rises"
                response = f"✅ I'll alert you when {', '.join(condition.tokens)} {direction} {percentage}%"
            elif condition.condition_type == "relative_change":
                response = f"🚨 Complex monitoring set up for {', '.join(condition.tokens)} with multiple conditions"
            else:
                response = "✅ Alert created successfully!"
            
            # Add status indicator
            status_emoji = {"active": "🟢", "paused": "⏸️", "triggered": "🔔", "expired": "⏹️"}
            status_text = status_emoji.get(alert.status, "⚪")
            
            conversation.append({
                "type": "assistant",
                "message": f"{response} {status_text}",
                "timestamp": alert.created_at.isoformat(),
                "alert_id": alert.id,
                "status": alert.status,
                "metadata": {
                    "condition_type": condition.condition_type,
                    "tokens": condition.tokens,
                    "threshold": condition.threshold,
                    "has_secondary": condition.secondary_condition is not None
                }
            })
        
        return {
            "conversation": list(reversed(conversation)),
            "total_messages": len(conversation),
            "user_id": user_id,
            "ai_enhanced": True,
            "summary": {
                "total_alerts": len(alerts),
                "active_alerts": len([a for a in alerts if a.status == "active"]),
                "tokens_watched": list(set([token for alert in alerts for token in alert.condition.tokens]))
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching conversation: {str(e)}")

@router.get("/suggestions")
async def get_enhanced_suggestions():
    """Get AI-enhanced chat suggestions"""
    return {
        "quick_start": [
            "Alert me when ETH hits $4000",
            "Tell me when BTC drops below $90000",
            "Notify me when AAVE goes above $350"
        ],
        "advanced": [
            "Alert me when any DeFi token drops 15% while BTC stays stable",
            "Tell me when ETH rises 10% in 24 hours",
            "Notify me when UNI and SUSHI both drop 20%"
        ],
        "price_examples": {
            "above": ["ETH above $5000", "BTC hits $100k", "AAVE reaches $400"],
            "below": ["ETH below $3000", "BTC under $80k", "SUSHI drops to $1"],
            "change": ["ETH drops 10%", "BTC rises 5%", "any DeFi token falls 15%"]
        },
        "ai_features": [
            "Natural language understanding",
            "Complex multi-token conditions", 
            "Contextual responses",
            "Smart token recognition"
        ],
        "tip": "Try asking in natural language - I understand complex conditions!"
    }

@router.post("/test-parsing")
async def test_enhanced_parsing(
    message: str,
    include_explanation: bool = True
):
    """Test enhanced message parsing with detailed feedback"""
    try:
        # Test with OpenAI
        parsed_condition = await nlp_service.parse_message(message)
        response_text = await nlp_service.generate_response(parsed_condition, message)
        
        result = {
            "original_message": message,
            "parsed_successfully": parsed_condition is not None,
            "would_create_alert": parsed_condition is not None,
            "response": response_text,
            "ai_powered": settings.validate_openai_key()
        }
        
        if parsed_condition:
            result.update({
                "parsed_condition": {
                    "condition_type": parsed_condition.condition_type,
                    "tokens": parsed_condition.tokens,
                    "threshold": parsed_condition.threshold,
                    "timeframe": parsed_condition.timeframe,
                    "has_secondary_condition": parsed_condition.secondary_condition is not None,
                    "confidence": parsed_condition.confidence
                }
            })
            
            if include_explanation:
                result["explanation"] = parsed_condition.explanation
                
            if parsed_condition.secondary_condition:
                result["secondary_condition"] = parsed_condition.secondary_condition
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error testing parsing: {str(e)}")

@router.get("/status")
async def get_nlp_status():
    """Get NLP service status and capabilities"""
    has_openai = settings.validate_openai_key()
    
    return {
        "nlp_service": "enhanced" if has_openai else "basic",
        "openai_configured": has_openai,
        "capabilities": {
            "natural_language": has_openai,
            "complex_conditions": has_openai,
            "contextual_responses": has_openai,
            "pattern_matching": True
        },
        "supported_conditions": [
            "price_above", "price_below", "price_change", "relative_change"
        ],
        "supported_tokens": [
            "BTC", "ETH", "AAVE", "UNI", "SUSHI", "COMP", "MKR", "SNX", "CRV", "1INCH"
        ],
        "defi_group_support": True,
        "model": settings.OPENAI_MODEL if has_openai else "pattern-based"
    }