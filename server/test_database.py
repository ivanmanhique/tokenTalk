# test_database.py - Test the database setup
import asyncio
from database import Database, AlertCondition

async def test_database():
    """Test database operations"""
    print("🧪 Testing database setup...")
    
    # Initialize database
    db = Database("test_stonewatch.db")
    await db.init_database()
    
    # Create test alert condition
    condition = AlertCondition(
        tokens=["ETH"],
        condition_type="price_above",
        threshold=4000.0,
        timeframe="24h"
    )
    
    # Create alert
    alert_id = await db.create_alert(
        user_id="test_user_123",
        condition=condition,
        message="Alert me when ETH hits $4000"
    )
    
    # Get active alerts
    alerts = await db.get_active_alerts()
    print(f"📋 Active alerts: {len(alerts)}")
    
    if alerts:
        alert = alerts[0]
        print(f"   Alert: {alert.message}")
        print(f"   Condition: {alert.condition.condition_type}")
        print(f"   Tokens: {alert.condition.tokens}")
        print(f"   Threshold: ${alert.condition.threshold}")
    
    # Test complex alert condition
    complex_condition = AlertCondition(
        tokens=["AAVE", "UNI", "SUSHI", "COMP"],  # DeFi tokens
        condition_type="relative_change",
        threshold=-0.15,  # -15%
        timeframe="24h",
        secondary_condition={
            "token": "BTC",
            "condition": "stable",
            "threshold": 0.03  # ±3%
        }
    )
    
    complex_alert_id = await db.create_alert(
        user_id="test_user_123",
        condition=complex_condition,
        message="Alert me when any DeFi token drops 15% while BTC stays stable"
    )
    
    # Get user alerts
    user_alerts = await db.get_user_alerts("test_user_123")
    print(f"👤 User alerts: {len(user_alerts)}")
    
    # Test updating alert status
    await db.update_alert_status(alert_id, "triggered")
    print(f"🔔 Updated alert status to triggered")
    
    # Test logging price data
    await db.log_price_data("ETH", 3724.12, 1733511234)
    await db.log_alert_trigger(alert_id, {"ETH": 4050.0, "triggered_condition": "price_above"})
    
    print("✅ Database tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_database())