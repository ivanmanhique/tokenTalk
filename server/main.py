from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from api.alerts import router as alerts_router
from api.prices import router as prices_router
from api.chat import router as chat_router

from database import db


app = FastAPI(
    title="tokenTalk API", 
    version="1.0.0",
    description="AI-powered crypto price alerts using RedStone oracles",
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
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(alerts_router, prefix="/api/alerts", tags=["alerts"])
app.include_router(prices_router, prefix="/api/prices", tags=["prices"])
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": "🪨 StoneWatch API is running!",
        "version": "1.0.0",
        "description": "AI-powered crypto price alerts using RedStone oracles",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "alerts": "/api/alerts/",
            "prices": "/api/prices/",
        },
        "features": [
            "Real-time crypto price monitoring",
            "Customizable price alerts",
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
        
        return {
            "status": "healthy",
            "service": "tokenTalk",
            "version": "1.0.0",
            "database": "connected",
            "redstone": "connected",
            "active_alerts": len(active_alerts),
            "timestamp": "2024-12-06T12:00:00Z"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "tokenTalk",
            "error": str(e),
            "database": "error",
            "redstone": "unknown"
        }

@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup"""
    try:
        await db.init_database()
        print("✅ Database initialized successfully")
        print("🚀 tokenTalk API started successfully")
        print("📖 API Documentation: http://localhost:8000/docs")
        print("🔍 Health Check: http://localhost:8000/health")
        print("💰 Price API: http://localhost:8000/api/prices/")
        print("🚨 Alerts API: http://localhost:8000/api/alerts/")
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        raise

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("🛑 StoneWatch API shutting down...")

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )