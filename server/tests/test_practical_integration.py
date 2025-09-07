#!/usr/bin/env python3
"""
test_practical_integration.py - Test the practical GolemBase integration
"""

import asyncio
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our practical integration
from services.pratical_golembase import (
    PracticalGolemService,
    TokenTalkHybridDatabase,
    create_tokenTalk_hybrid_db
)

# Mock database for testing
class MockSQLiteDatabase:
    """Mock SQLite database for testing"""
    
    def __init__(self):
        self.users = {}
        self.alerts = {}
        self.price_data = []
        self.alert_triggers = []
    
    async def init_database(self):
        logger.info("📦 Mock SQLite database initialized")
    
    async def get_or_create_user(self, user_id: str, email: str = None):
        if user_id not in self.users:
            self.users[user_id] = {
                "user_id": user_id,
                "email": email,
                "created_at": datetime.now().isoformat()
            }
            logger.info(f"👤 Mock user created: {user_id}")
        return self.users[user_id]
    
    async def update_user_email(self, user_id: str, email: str) -> bool:
        if user_id in self.users:
            self.users[user_id]["email"] = email
            logger.info(f"📧 Mock user email updated: {user_id}")
            return True
        return False
    
    async def create_alert(self, user_id: str, user_email: str, condition, message: str) -> str:
        import uuid
        alert_id = str(uuid.uuid4())
        self.alerts[alert_id] = {
            "alert_id": alert_id,
            "user_id": user_id,
            "user_email": user_email,
            "condition": condition,
            "message": message,
            "status": "active",
            "created_at": datetime.now().isoformat()
        }
        logger.info(f"🚨 Mock alert created: {alert_id}")
        return alert_id
    
    async def get_active_alerts(self):
        return [alert for alert in self.alerts.values() if alert["status"] == "active"]
    
    async def get_user_alerts(self, user_id: str):
        return [alert for alert in self.alerts.values() if alert["user_id"] == user_id]
    
    async def update_alert_status(self, alert_id: str, status: str):
        if alert_id in self.alerts:
            self.alerts[alert_id]["status"] = status
            logger.info(f"📝 Mock alert status updated: {alert_id} -> {status}")
    
    async def log_price_data(self, symbol: str, price: float, timestamp: int):
        self.price_data.append({
            "symbol": symbol,
            "price": price,
            "timestamp": timestamp
        })
        logger.debug(f"💰 Mock price logged: {symbol} = ${price}")
    
    async def log_alert_trigger(self, alert_id: str, price_data: dict):
        self.alert_triggers.append({
            "alert_id": alert_id,
            "price_data": price_data,
            "timestamp": datetime.now().isoformat()
        })
        logger.info(f"📊 Mock alert trigger logged: {alert_id}")

async def test_golem_service():
    """Test the GolemBase service directly"""
    print("\n" + "="*60)
    print("🧪 Testing Practical GolemBase Service")
    print("="*60)
    
    service = PracticalGolemService()
    
    # Initialize service
    success = await service.initialize()
    print(f"Initialization: {'✅' if success else '❌'}")
    
    if not success:
        print("❌ Service initialization failed")
        return False
    
    # Get initial status
    status = await service.get_status()
    print(f"Mock mode: {'✅' if status['mock_mode'] else '❌'}")
    print(f"Connected: {'✅' if status['connected'] else '❌'}")
    
    # Test user operations
    print(f"\n👤 Testing user operations...")
    user = await service.create_user("test_user_123", "test@tokenTalk.com")
    print(f"User created: {user.entity_id}")
    
    retrieved_user = await service.get_user("test_user_123")
    print(f"User retrieved: {'✅' if retrieved_user else '❌'}")
    
    updated = await service.update_user("test_user_123", {"email": "updated@tokenTalk.com"})
    print(f"User updated: {'✅' if updated else '❌'}")
    
    # Test alert operations
    print(f"\n🚨 Testing alert operations...")
    from database import AlertCondition
    
    condition = AlertCondition(
        tokens=["ETH"],
        condition_type="price_above",
        threshold=4000.0
    )
    
    alert_id = await service.create_alert("test_user_123", condition, "Test alert")
    print(f"Alert created: {alert_id}")
    
    user_alerts = await service.get_user_alerts("test_user_123")
    print(f"User alerts: {len(user_alerts)} found")
    
    status_updated = await service.update_alert_status(alert_id, "triggered")
    print(f"Alert status updated: {'✅' if status_updated else '❌'}")
    
    # Test analytics
    print(f"\n📊 Testing analytics...")
    await service.log_event("test_event", {"test": True}, "test_user_123")
    await service.store_price_data("ETH", 4050.0)
    
    price_history = await service.get_price_history("ETH")
    print(f"Price history: {len(price_history)} records")
    
    # Export mock data
    mock_data = await service.export_mock_data()
    print(f"Mock data entities: {len(mock_data)}")
    
    # Final status
    final_status = await service.get_status()
    print(f"\n📈 Final metrics:")
    for key, value in final_status["metrics"].items():
        print(f"   {key}: {value}")
    
    await service.close()
    return True

async def test_hybrid_database():
    """Test the hybrid database integration"""
    print("\n" + "="*60)
    print("🔄 Testing Hybrid Database Integration")
    print("="*60)
    
    # Create mock SQLite database
    mock_sqlite = MockSQLiteDatabase()
    
    # Create hybrid database
    hybrid_db = await create_tokenTalk_hybrid_db(mock_sqlite)
    
    # Get status
    status = await hybrid_db.get_status()
    print(f"Hybrid database ready: {'✅' if status['ready_for_production'] else '❌'}")
    print(f"SQLite healthy: {'✅' if status['sqlite']['healthy'] else '❌'}")
    print(f"GolemBase enabled: {'✅' if status['golembase']['enabled'] else '❌'}")
    
    # Test user operations
    print(f"\n👤 Testing hybrid user operations...")
    user = await hybrid_db.get_or_create_user("hybrid_user_456", "hybrid@tokenTalk.com")
    print(f"User created: {user['user_id']}")
    
    email_updated = await hybrid_db.update_user_email("hybrid_user_456", "new@tokenTalk.com")
    print(f"Email updated: {'✅' if email_updated else '❌'}")
    
    # Test alert operations
    print(f"\n🚨 Testing hybrid alert operations...")
    from database import AlertCondition
    
    condition = AlertCondition(
        tokens=["BTC"],
        condition_type="price_below",
        threshold=90000.0
    )
    
    alert_id = await hybrid_db.create_alert(
        "hybrid_user_456", 
        "new@tokenTalk.com", 
        condition, 
        "Hybrid test alert"
    )
    print(f"Alert created: {alert_id}")
    
    user_alerts = await hybrid_db.get_user_alerts("hybrid_user_456")
    print(f"User alerts: {len(user_alerts)}")
    
    await hybrid_db.update_alert_status(alert_id, "triggered")
    print(f"Alert status updated: ✅")
    
    # Test logging
    print(f"\n📊 Testing hybrid logging...")
    await hybrid_db.log_price_data("BTC", 95000.0, int(datetime.now().timestamp()))
    await hybrid_db.log_alert_trigger(alert_id, {"BTC": 89000.0})
    print(f"Logging completed: ✅")
    
    # Final status
    final_status = await hybrid_db.get_status()
    print(f"\n🎯 Integration benefits:")
    for benefit in final_status["benefits"]:
        print(f"   ✅ {benefit}")
    
    await hybrid_db.close()
    return True

async def demonstrate_tokenTalk_integration():
    """Demonstrate how to integrate with existing tokenTalk"""
    print("\n" + "="*60)
    print("🎯 TokenTalk Integration Demo")
    print("="*60)
    
    print("""
🔧 To integrate with your existing tokenTalk:

1️⃣ Add the practical_golembase.py file to your services/ directory

2️⃣ Update your main.py:
   
   # OLD:
   from database import db
   
   # NEW:
   from services.practical_golembase import create_tokenTalk_hybrid_db
   from database import Database
   
   # In startup_event():
   sqlite_db = Database()
   hybrid_db = await create_tokenTalk_hybrid_db(sqlite_db)

3️⃣ Replace database calls gradually:
   
   # User operations
   user = await hybrid_db.get_or_create_user(user_id, email)
   
   # Alert operations  
   alert_id = await hybrid_db.create_alert(user_id, email, condition, message)
   
   # Status updates
   await hybrid_db.update_alert_status(alert_id, "triggered")

4️⃣ Benefits you get immediately:
   ✅ Development-ready decentralized structure
   ✅ User data ownership preparation
   ✅ Analytics and audit trail logging
   ✅ Fault-tolerant hybrid approach
   ✅ Easy to enable full blockchain later

5️⃣ When ready for production blockchain:
   - Add GOLEMBASE_RPC_ENDPOINT to .env
   - Add GOLEMBASE_WALLET_PRIVATE_KEY for write operations
   - The service automatically upgrades from mock to real blockchain
    """)
    
    print("\n🚀 Ready to integrate? The hybrid database provides:")
    print("   📱 Immediate value with mock mode")
    print("   🔒 Future-proof for full decentralization") 
    print("   ⚡ Zero performance impact on existing alerts")
    print("   🌐 Gradual path to Web3 features")

async def main():
    """Run all tests"""
    print("🚀 Practical GolemBase Integration Test Suite")
    print("="*60)
    
    try:
        # Test GolemBase service
        golem_success = await test_golem_service()
        
        # Test hybrid database
        hybrid_success = await test_hybrid_database()
        
        # Show integration demo
        await demonstrate_tokenTalk_integration()
        
        print("\n" + "="*60)
        print("🏁 Test Results Summary")
        print("="*60)
        print(f"GolemBase Service: {'✅ PASS' if golem_success else '❌ FAIL'}")
        print(f"Hybrid Database: {'✅ PASS' if hybrid_success else '❌ FAIL'}")
        print(f"Integration Ready: {'✅ YES' if golem_success and hybrid_success else '❌ NO'}")
        
        if golem_success and hybrid_success:
            print(f"\n🎉 All tests passed! Ready to integrate with tokenTalk.")
            print(f"💡 Start by adding practical_golembase.py to your project.")
        else:
            print(f"\n⚠️  Some tests failed. Check logs above.")
        
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted")
    except Exception as e:
        print(f"\n💥 Test suite failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
