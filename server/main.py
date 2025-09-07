# main.py - Updated with GolemDB integration and modern FastAPI lifespan
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import asyncio
import logging
import json
from datetime import datetime

from api.alerts import router as alerts_router
from api.prices import router as prices_router
from api.chat import router as chat_router
from api.users import router as users_router

from database import db, Database
from services.nlp_service import nlp_service
from config import settings

# NEW: GolemDB imports
from services.golemdb_service import create_tokenTalk_golem_hybrid, GolemConfig
from services.enhanced_notification_service import create_enhanced_notification_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
hybrid_db = None
enhanced_notifications = None
alert_engine = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modern FastAPI lifespan handler"""
    global hybrid_db, enhanced_notifications, alert_engine
    
    # Startup
    try:
        logger.info("🚀 tokenTalk starting up...")
        settings.print_status()
        
        # Initialize SQLite database (existing)
        sqlite_db = Database()
        await sqlite_db.init_database()
        
        # NEW: Initialize GolemDB hybrid database
        golem_config = GolemConfig()
        hybrid_db = await create_tokenTalk_golem_hybrid(sqlite_db, golem_config)
        logger.info("✅ GolemDB hybrid database initialized")
        
        # NEW: Initialize enhanced notification service
        enhanced_notifications = create_enhanced_notification_service(hybrid_db.golem)
        logger.info("✅ Enhanced notification service initialized")
        
        # Initialize NLP service
        await nlp_service.init()
        logger.info("✅ NLP service initialized")
        
        # Import and start alert engine with enhanced notifications
        from services.alert_engine import alert_engine as engine
        alert_engine = engine
        # Update alert engine to use enhanced notifications
        alert_engine.notifications = enhanced_notifications
        
        # Start alert engine in background
        asyncio.create_task(alert_engine.start_monitoring())
        logger.info("✅ Alert engine started with enhanced notifications")
        
        # Get GolemDB status for startup message
        golemdb_status = await hybrid_db.get_status()
        golemdb_mode = "blockchain" if not golemdb_status["golemdb"]["status"]["mock_mode"] else "mock"
        golemdb_enabled = golemdb_status["golemdb"]["enabled"]
        
        print("\n" + "="*70)
        print("🚀 tokenTalk API with GolemDB Started Successfully!")
        print("="*70)
        print("📖 API Documentation: http://localhost:8000/docs")
        print("🥽 Health Check:      http://localhost:8000/health")
        print("💰 Price API:         http://localhost:8000/api/prices/")
        print("🚨 Alerts API:        http://localhost:8000/api/alerts/")
        print("💬 Chat API:          http://localhost:8000/api/chat/")
        print("👤 Users API:         http://localhost:8000/api/users/")
        print("🔗 GolemDB Status:    http://localhost:8000/api/golemdb/status")
        print("📊 GolemDB Analytics: http://localhost:8000/api/golemdb/analytics/{user_id}")
        print("📡 WebSocket:         ws://localhost:8000/ws?user_id=YOUR_ID")
        print("🔍 Monitoring:        http://localhost:8000/api/monitoring/services")
        print("🧪 Test Alert:        POST http://localhost:8000/api/test/trigger-fake-alert")
        
        print(f"🔗 GolemDB: {'✅ ENABLED' if golemdb_enabled else '❌ DISABLED'} ({golemdb_mode} mode)")
        if golemdb_enabled and golemdb_mode == "blockchain":
            blockchain_info = golemdb_status["golemdb"]["status"].get("blockchain", {})
            if blockchain_info:
                print(f"💎 Blockchain Address: {blockchain_info.get('address', 'N/A')}")
                print(f"💰 Balance: {blockchain_info.get('balance_eth', 0):.4f} ETH")
        elif golemdb_enabled and golemdb_mode == "mock":
            print("💡 Mock mode active - all features work, no blockchain required!")
        
        if settings.has_resend_key():
            print("📧 Email Alerts:      ✅ ENABLED via Resend")
        else:
            print("📧 Email Alerts:      ❌ Disabled (no Resend key)")
            
        print("✨ Enhanced Features:  Personalized notifications with user insights")
        print("="*70 + "\n")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    
    yield  # App runs here
    
    # Shutdown
    logger.info("🛑 tokenTalk API shutting down...")
    
    # Stop alert engine
    if alert_engine:
        alert_engine.stop_monitoring()
        logger.info("✅ Alert engine stopped")
    
    # Close NLP service
    await nlp_service.close()
    logger.info("✅ NLP service closed")
    
    # Close GolemDB service
    if hybrid_db:
        await hybrid_db.close()
        logger.info("✅ GolemDB service closed")

app = FastAPI(
    title="tokenTalk API", 
    version="1.0.0",
    description="AI-powered crypto price alerts with GolemDB blockchain integration",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan  # Modern lifespan handler
)

# Include API routers
app.include_router(alerts_router, prefix="/api/alerts", tags=["alerts"])
app.include_router(prices_router, prefix="/api/prices", tags=["prices"])
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
app.include_router(users_router, prefix="/api/users", tags=["users"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",    # Create React App
        "http://localhost:5173",    # Vite
        "http://localhost:5000",    # Alternative dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "file://"              # Local HTML files
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": "🪨 tokenTalk API with GolemDB!",
        "version": "1.0.0",
        "description": "AI-powered crypto price alerts with blockchain-secured user data",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "alerts": "/api/alerts/",
            "prices": "/api/prices/",
            "chat": "/api/chat/",
            "users": "/api/users/",
            "golemdb_status": "/api/golemdb/status",
            "golemdb_analytics": "/api/golemdb/analytics/{user_id}",
            "websocket": "/ws?user_id=YOUR_USER_ID",
            "monitoring": "/api/monitoring/services"
        },
        "features": [
            "Real-time crypto price monitoring",
            "Natural language alert creation", 
            "Blockchain-secured user profiles",
            "Enhanced personalized notifications",
            "Immutable audit trails",
            "Cross-platform data sync",
            "WebSocket notifications",
            "Email notifications via Resend",
            "RedStone oracle integration"
        ]
    }

@app.get("/health")
async def health_check():
    """Enhanced health check with GolemDB status"""
    try:
        # Test database connection
        active_alerts = await db.get_active_alerts()
        
        # Get alert engine status
        engine_stats = await alert_engine.get_monitoring_stats()
        
        # Get notification service status
        notification_stats = await enhanced_notifications.get_service_status()
        
        # Get GolemDB status
        golemdb_status = await hybrid_db.get_status() if hybrid_db else {"status": "not_initialized"}
        
        return {
            "status": "healthy",
            "service": "tokenTalk with GolemDB",
            "version": "1.0.0",
            "database": "connected",
            "redstone": "connected",
            "alert_engine": "running" if engine_stats["running"] else "stopped",
            "email_service": "enabled" if settings.has_resend_key() else "disabled",
            "golemdb": {
                "enabled": golemdb_status.get("golemdb", {}).get("enabled", False),
                "mode": "blockchain" if not golemdb_status.get("golemdb", {}).get("status", {}).get("mock_mode", True) else "mock",
                "status": golemdb_status.get("golemdb", {}).get("status", {})
            },
            "metrics": {
                "active_alerts": len(active_alerts),
                "alerts_checked": engine_stats["stats"]["alerts_checked"],
                "alerts_triggered": engine_stats["stats"]["alerts_triggered"],
                "emails_sent": notification_stats["email_stats"]["sent"],
                "emails_failed": notification_stats["email_stats"]["failed"],
                "golemdb_operations": golemdb_status.get("golemdb", {}).get("status", {}).get("metrics", {}).get("blockchain_operations", 0)
            },
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

# NEW: GolemDB API endpoints
@app.get("/api/golemdb/status")
async def golemdb_status():
    """Get GolemDB integration status"""
    if hybrid_db:
        return await hybrid_db.get_status()
    return {"error": "GolemDB not initialized"}

@app.get("/api/golemdb/analytics/{user_id}")
async def user_golemdb_analytics(user_id: str):
    """Get user's GolemDB analytics"""
    if hybrid_db:
        return await hybrid_db.get_user_analytics(user_id)
    return {"error": "GolemDB not initialized"}

@app.post("/api/golemdb/test-profile")
async def test_golemdb_profile(user_id: str, email: str):
    """Test GolemDB profile creation"""
    if hybrid_db:
        await hybrid_db.get_or_create_user(user_id, email)
        return {"success": True, "user_id": user_id, "message": "Profile synced to GolemDB"}
    return {"error": "GolemDB not initialized"}

# WebSocket endpoint for real-time notifications
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, user_id: str = Query(default="anonymous")):
    """WebSocket endpoint for real-time notifications"""
    await websocket.accept()
    enhanced_notifications.add_websocket_connection(websocket, user_id)
    
    try:
        # Send welcome message with GolemDB status
        golemdb_enabled = hybrid_db.golem_enabled if hybrid_db else False
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "message": f"Connected to tokenTalk with GolemDB as {user_id}",
            "user_id": user_id,
            "features": {
                "email_enabled": settings.has_resend_key(),
                "golemdb_enabled": golemdb_enabled,
                "enhanced_notifications": True
            },
            "timestamp": datetime.now().isoformat()
        }))
        
        logger.info(f"WebSocket connected for user: {user_id}")
        
        # Keep connection alive
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                message_type = message.get("type", "unknown")
                
                if message_type == "ping":
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    }))
                elif message_type == "get_status":
                    # Send enhanced status
                    status = await hybrid_db.get_status() if hybrid_db else {}
                    await websocket.send_text(json.dumps({
                        "type": "status_response",
                        "data": {
                            "golemdb": status,
                            "user_id": user_id,
                            "connected_at": datetime.now().isoformat()
                        }
                    }))
                else:
                    await websocket.send_text(json.dumps({
                        "type": "echo",
                        "original_message": data,
                        "timestamp": datetime.now().isoformat()
                    }))
                    
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "echo",
                    "message": f"Received: {data}",
                    "timestamp": datetime.now().isoformat()
                }))
            
    except WebSocketDisconnect:
        enhanced_notifications.remove_websocket_connection(websocket, user_id)
        logger.info(f"WebSocket disconnected for user: {user_id}")

# Monitoring endpoints
@app.get("/api/monitoring/alert-engine")
async def get_alert_engine_status():
    """Get alert engine monitoring data"""
    return await alert_engine.get_monitoring_stats()

@app.get("/api/monitoring/services")
async def get_services_status():
    """Get status of all services including GolemDB"""
    try:
        return {
            "alert_engine": await alert_engine.get_monitoring_stats(),
            "notification_service": await enhanced_notifications.get_service_status(),
            "nlp_service": await nlp_service.get_status(),
            "database": "connected",
            "golemdb": await hybrid_db.get_status() if hybrid_db else {"status": "not_initialized"},
            "resend_configured": settings.has_resend_key(),
            "email_enabled": settings.ENABLE_EMAIL_NOTIFICATIONS,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Services status check failed: {e}")
        return {"error": str(e), "status": "error"}

# Testing endpoints  
@app.post("/api/test/trigger-fake-alert")
async def trigger_fake_alert(user_id: str = "test_user", user_email: str = "test@email.com"):
    """Trigger a fake alert for testing enhanced notifications"""
    try:
        fake_alert_data = {
            "alert_id": "test-alert-123",
            "user_id": user_id,
            "user_email": user_email,
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
        
        await enhanced_notifications.send_alert_notification(fake_alert_data)
        
        return {
            "success": True,
            "message": "Enhanced fake alert triggered successfully",
            "alert_data": fake_alert_data,
            "features_enabled": {
                "email": settings.has_resend_key(),
                "golemdb": hybrid_db.golem_enabled if hybrid_db else False,
                "personalization": True
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to trigger fake alert: {e}")
        return {"success": False, "error": str(e)}

@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup"""
    global hybrid_db, enhanced_notifications, alert_engine
    
    try:
        # Print configuration
        settings.print_status()
        
        # Initialize SQLite database (existing)
        sqlite_db = Database()
        await sqlite_db.init_database()
        
        # NEW: Initialize GolemDB hybrid database
        golem_config = GolemConfig()
        hybrid_db = await create_tokenTalk_golem_hybrid(sqlite_db, golem_config)
        logger.info("✅ GolemDB hybrid database initialized")
        
        # NEW: Initialize enhanced notification service
        enhanced_notifications = create_enhanced_notification_service(hybrid_db.golem)
        logger.info("✅ Enhanced notification service initialized")
        
        # Initialize NLP service
        await nlp_service.init()
        logger.info("✅ NLP service initialized")
        
        # Import and start alert engine with enhanced notifications
        from services.alert_engine import alert_engine as engine
        alert_engine = engine
        # Update alert engine to use enhanced notifications
        alert_engine.notifications = enhanced_notifications
        
        # Start alert engine in background
        asyncio.create_task(alert_engine.start_monitoring())
        logger.info("✅ Alert engine started with enhanced notifications")
        
        # Get GolemDB status for startup message
        golemdb_status = await hybrid_db.get_status()
        golemdb_mode = "blockchain" if not golemdb_status["golemdb"]["status"]["mock_mode"] else "mock"
        golemdb_enabled = golemdb_status["golemdb"]["enabled"]
        
        print("\n" + "="*70)
        print("🚀 tokenTalk API with GolemDB Started Successfully!")
        print("="*70)
        print("📖 API Documentation: http://localhost:8000/docs")
        print("🥽 Health Check:      http://localhost:8000/health")
        print("💰 Price API:         http://localhost:8000/api/prices/")
        print("🚨 Alerts API:        http://localhost:8000/api/alerts/")
        print("💬 Chat API:          http://localhost:8000/api/chat/")
        print("👤 Users API:         http://localhost:8000/api/users/")
        print("🔗 GolemDB Status:    http://localhost:8000/api/golemdb/status")
        print("📊 GolemDB Analytics: http://localhost:8000/api/golemdb/analytics/{user_id}")
        print("📡 WebSocket:         ws://localhost:8000/ws?user_id=YOUR_ID")
        print("🔍 Monitoring:        http://localhost:8000/api/monitoring/services")
        print("🧪 Test Alert:        POST http://localhost:8000/api/test/trigger-fake-alert")
        
        print(f"🔗 GolemDB: {'✅ ENABLED' if golemdb_enabled else '❌ DISABLED'} ({golemdb_mode} mode)")
        if golemdb_enabled and golemdb_mode == "blockchain":
            blockchain_info = golemdb_status["golemdb"]["status"].get("blockchain", {})
            if blockchain_info:
                print(f"💎 Blockchain Address: {blockchain_info.get('address', 'N/A')}")
                print(f"💰 Balance: {blockchain_info.get('balance_eth', 0):.4f} ETH")
        
        if settings.has_resend_key():
            print("📧 Email Alerts:      ✅ ENABLED via Resend")
        else:
            print("📧 Email Alerts:      ❌ Disabled (no Resend key)")
            
        print("✨ Enhanced Features:  Personalized notifications with user insights")
        print("="*70 + "\n")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 tokenTalk API shutting down...")
    
    # Stop alert engine
    if alert_engine:
        alert_engine.stop_monitoring()
        logger.info("✅ Alert engine stopped")
    
    # Close NLP service
    await nlp_service.close()
    logger.info("✅ NLP service closed")
    
    # Close GolemDB service
    if hybrid_db:
        await hybrid_db.close()
        logger.info("✅ GolemDB service closed")

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )