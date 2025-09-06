from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import logging
import json
from datetime import datetime

from api.alerts import router as alerts_router
from api.prices import router as prices_router
from api.chat import router as chat_router
from api.users import router as users_router  # New users API

from database import db
from services.alert_engine import alert_engine
from services.notification_service import notification_service
from services.nlp_service import nlp_service
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="tokenTalk API", 
    version="1.0.0",
    description="AI-powered crypto price alerts using RedStone oracles with Resend email notifications",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",    # Create React App
        "http://localhost:5173",    # Vite
        "http://localhost:5000",    # Alternative dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "file://",                  # Local HTML files
        "*"                         # Allow all for hackathon (remove in production)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(alerts_router, prefix="/api/alerts", tags=["alerts"])
app.include_router(prices_router, prefix="/api/prices", tags=["prices"])
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
app.include_router(users_router, prefix="/api/users", tags=["users"])  # New users API

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": "🪨 tokenTalk API is running!",
        "version": "1.0.0",
        "description": "AI-powered crypto price alerts using RedStone oracles with Resend email notifications",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "alerts": "/api/alerts/",
            "prices": "/api/prices/",
            "chat": "/api/chat/",
            "users": "/api/users/",
            "websocket": "/ws?user_id=YOUR_USER_ID",
            "monitoring": "/api/monitoring/services"
        },
        "features": [
            "Real-time crypto price monitoring",
            "Natural language alert creation",
            "Background alert engine",
            "WebSocket notifications",
            "Email notifications via Resend",
            "RedStone oracle integration",
            "SQLite database storage"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        active_alerts = await db.get_active_alerts()
        
        # Get alert engine status
        engine_stats = await alert_engine.get_monitoring_stats()
        
        # Get notification service status
        notification_stats = await notification_service.get_service_status()
        
        return {
            "status": "healthy",
            "service": "tokenTalk",
            "version": "1.0.0",
            "database": "connected",
            "redstone": "connected",
            "alert_engine": "running" if engine_stats["running"] else "stopped",
            "email_service": "enabled" if settings.has_resend_key() else "disabled",
            "active_alerts": len(active_alerts),
            "alerts_checked": engine_stats["stats"]["alerts_checked"],
            "alerts_triggered": engine_stats["stats"]["alerts_triggered"],
            "emails_sent": notification_stats["email_stats"]["sent"],
            "emails_failed": notification_stats["email_stats"]["failed"],
            "last_run": engine_stats["stats"]["last_run"],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "tokenTalk",
            "error": str(e),
            "database": "error",
            "redstone": "unknown"
        }

# WebSocket endpoint for real-time notifications
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, user_id: str = Query(default="anonymous")):
    """WebSocket endpoint for real-time notifications"""
    await websocket.accept()
    notification_service.add_websocket_connection(websocket, user_id)
    
    try:
        # Send welcome message
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "message": f"Connected to tokenTalk notifications as {user_id}",
            "user_id": user_id,
            "email_enabled": settings.has_resend_key(),
            "timestamp": datetime.now().isoformat()
        }))
        
        logger.info(f"WebSocket connected for user: {user_id}")
        
        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()
            
            # Handle different message types
            try:
                message = json.loads(data)
                message_type = message.get("type", "unknown")
                
                if message_type == "ping":
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    }))
                elif message_type == "get_status":
                    # Send current status
                    engine_stats = await alert_engine.get_monitoring_stats()
                    notification_stats = await notification_service.get_service_status()
                    await websocket.send_text(json.dumps({
                        "type": "status_response",
                        "data": {
                            "alert_engine": engine_stats,
                            "notification_service": notification_stats,
                            "user_id": user_id,
                            "connected_at": datetime.now().isoformat()
                        }
                    }))
                else:
                    # Echo unknown messages
                    await websocket.send_text(json.dumps({
                        "type": "echo",
                        "original_message": data,
                        "timestamp": datetime.now().isoformat()
                    }))
                    
            except json.JSONDecodeError:
                # Handle non-JSON messages
                await websocket.send_text(json.dumps({
                    "type": "echo",
                    "message": f"Received: {data}",
                    "timestamp": datetime.now().isoformat()
                }))
            
    except WebSocketDisconnect:
        notification_service.remove_websocket_connection(websocket, user_id)
        logger.info(f"WebSocket disconnected for user: {user_id}")

# Monitoring endpoints
@app.get("/api/monitoring/alert-engine")
async def get_alert_engine_status():
    """Get alert engine monitoring data"""
    return await alert_engine.get_monitoring_stats()

@app.get("/api/monitoring/services")
async def get_services_status():
    """Get status of all services"""
    try:
        return {
            "alert_engine": await alert_engine.get_monitoring_stats(),
            "notification_service": await notification_service.get_service_status(),
            "nlp_service": await nlp_service.get_status(),
            "database": "connected",
            "resend_configured": settings.has_resend_key(),
            "email_enabled": settings.ENABLE_EMAIL_NOTIFICATIONS,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Services status check failed: {e}")
        return {"error": str(e), "status": "error"}

@app.post("/api/monitoring/force-check/{alert_id}")
async def force_check_alert(alert_id: str):
    """Force check a specific alert (for testing)"""
    try:
        return await alert_engine.force_check_alert(alert_id)
    except Exception as e:
        logger.error(f"Force check failed for alert {alert_id}: {e}")
        return {"error": str(e), "alert_id": alert_id}

@app.get("/api/notifications")
async def get_notifications(user_id: str = "default_user", limit: int = 10):
    """Get recent notifications for a user"""
    return {
        "notifications": await notification_service.get_recent_notifications(user_id, limit),
        "user_id": user_id,
        "limit": limit,
        "timestamp": datetime.now().isoformat()
    }

# Development/Testing endpoints
@app.post("/api/test/trigger-fake-alert")
async def trigger_fake_alert(user_id: str = "test_user"):
    """Trigger a fake alert for testing notifications"""
    try:
        fake_alert_data = {
            "alert_id": "test-alert-123",
            "user_id": user_id,
            "message": "Test alert triggered via API",
            "condition": {
                "type": "price_above",
                "tokens": ["ETH"],
                "threshold": 4000.0
            },
            "triggered_at": datetime.now().isoformat(),
            "prices": {
                "ETH": {
                    "current_price": 4050.0,
                    "formatted": "$4,050.00"
                }
            }
        }
        
        await notification_service.send_alert_notification(fake_alert_data)
        
        return {
            "success": True,
            "message": "Fake alert triggered successfully",
            "alert_data": fake_alert_data,
            "email_enabled": settings.has_resend_key()
        }
        
    except Exception as e:
        logger.error(f"Failed to trigger fake alert: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/test/setup-user-email")
async def setup_user_email(user_id: str, email: str):
    """Quick setup for user email (testing endpoint)"""
    try:
        success = await db.update_user_email(user_id, email)
        
        return {
            "success": success,
            "user_id": user_id,
            "email": email,
            "message": "Email setup complete. You'll receive notifications at this address!",
            "next_step": f"Trigger a test alert with: POST /api/test/trigger-fake-alert?user_id={user_id}"
        }
        
    except Exception as e:
        logger.error(f"Failed to setup user email: {e}")
        return {"success": False, "error": str(e)}

@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup"""
    try:
        # Print configuration
        settings.print_status()
        
        # Initialize database
        await db.init_database()
        logger.info("✅ Database initialized successfully")
        
        # Initialize NLP service
        await nlp_service.init()
        logger.info("✅ NLP service initialized")
        
        # Start alert engine in background
        asyncio.create_task(alert_engine.start_monitoring())
        logger.info("✅ Alert engine started in background")
        
        print("\n" + "="*60)
        print("🚀 tokenTalk API Started Successfully!")
        print("="*60)
        print("📖 API Documentation: http://localhost:8000/docs")
        print("🏥 Health Check:      http://localhost:8000/health")
        print("💰 Price API:         http://localhost:8000/api/prices/")
        print("🚨 Alerts API:        http://localhost:8000/api/alerts/")
        print("💬 Chat API:          http://localhost:8000/api/chat/")
        print("👤 Users API:         http://localhost:8000/api/users/")
        print("📡 WebSocket:         ws://localhost:8000/ws?user_id=YOUR_ID")
        print("🔍 Monitoring:        http://localhost:8000/api/monitoring/services")
        print("🧪 Test Alert:        POST http://localhost:8000/api/test/trigger-fake-alert")
        if settings.has_resend_key():
            print("📧 Email Alerts:      ✅ ENABLED via Resend")
        else:
            print("📧 Email Alerts:      ❌ Disabled (no Resend key)")
        print("="*60 + "\n")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 tokenTalk API shutting down...")
    
    # Stop alert engine
    alert_engine.stop_monitoring()
    logger.info("✅ Alert engine stopped")
    
    # Close NLP service
    await nlp_service.close()
    logger.info("✅ NLP service closed")

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )