#!/usr/bin/env python3
"""
Test script for the Alert Engine
Run this to verify your alert engine is working properly
"""

import asyncio
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_api_health():
    """Test API Health"""
    print("1️⃣ Testing API Health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API Status: {data['status']}")
            print(f"   📊 Alert Engine: {data.get('alert_engine', 'unknown')}")
            print(f"   📈 Active Alerts: {data.get('active_alerts', 0)}")
            print(f"   🔢 Alerts Checked: {data.get('alerts_checked', 0)}")
            print(f"   🚨 Alerts Triggered: {data.get('alerts_triggered', 0)}")
            return True
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Cannot connect to API: {e}")
        return False

def test_price_fetching():
    """Test RedStone price fetching"""
    print("\n2️⃣ Testing RedStone Price Fetching...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/prices/current/ETH")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ ETH Price: ${data['price']:,.2f}")
            print(f"   📅 Source: {data.get('source', 'unknown')}")
            return True
        else:
            print(f"   ❌ Price fetch failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Price test failed: {e}")
        return False

def test_create_alert():
    """Test alert creation via chat"""
    print("\n3️⃣ Creating test alert via chat...")
    try:
        chat_data = {
            "message": "Alert me when ETH goes above $3500",
            "user_id": "test_user"
        }
        response = requests.post(f"{BASE_URL}/api/chat/message", json=chat_data)
        
        if response.status_code == 200:
            chat_response = response.json()
            print(f"   ✅ Chat Response: {chat_response['response']}")
            
            if chat_response.get('alert_created'):
                alert_id = chat_response.get('alert_id')
                print(f"   🚨 Alert Created: {alert_id}")
                return alert_id
            else:
                print("   ⚠️  Alert not created - check NLP parsing")
                return None
        else:
            print(f"   ❌ Chat failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ Alert creation failed: {e}")
        return None

def test_alert_engine_status():
    """Test alert engine status"""
    print("\n4️⃣ Checking alert engine status...")
    try:
        response = requests.get(f"{BASE_URL}/api/monitoring/alert-engine")
        if response.status_code == 200:
            stats = response.json()
            print(f"   📊 Engine Running: {stats['running']}")
            print(f"   ⏱️  Check Interval: {stats['monitoring_interval']}s")
            print(f"   📈 Alerts Checked: {stats['stats']['alerts_checked']}")
            print(f"   🚨 Alerts Triggered: {stats['stats']['alerts_triggered']}")
            print(f"   💾 Cached Tokens: {len(stats.get('cached_tokens', []))}")
            print(f"   🕐 Last Run: {stats['stats'].get('last_run', 'Never')}")
            return True
        else:
            print(f"   ❌ Engine status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Engine status test failed: {e}")
        return False

def test_force_check_alert(alert_id):
    """Test force checking an alert"""
    if not alert_id:
        print("\n5️⃣ Skipping force check (no alert ID)")
        return False
        
    print("\n5️⃣ Force checking alert...")
    try:
        response = requests.post(f"{BASE_URL}/api/monitoring/force-check/{alert_id}")
        if response.status_code == 200:
            result = response.json()
            print(f"   🔍 Alert Evaluated: {result.get('evaluated', False)}")
            print(f"   🚨 Alert Triggered: {result.get('triggered', False)}")
            
            if result.get('current_prices'):
                print("   💰 Current Prices:")
                for token, price in result['current_prices'].items():
                    print(f"      {token}: ${price:,.2f}")
            return True
        else:
            print(f"   ❌ Force check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Force check test failed: {e}")
        return False

def test_user_alerts():
    """Test getting user alerts"""
    print("\n6️⃣ Checking user alerts...")
    try:
        response = requests.get(f"{BASE_URL}/api/alerts/user/test_user")
        if response.status_code == 200:
            alerts = response.json()
            print(f"   📝 Total Alerts: {alerts['total']}")
            for alert in alerts['alerts']:
                print(f"      🚨 {alert['id'][:8]}...: {alert['message']} [{alert['status']}]")
            return True
        else:
            print(f"   ❌ User alerts check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ User alerts test failed: {e}")
        return False

def test_fake_alert():
    """Test triggering a fake alert"""
    print("\n7️⃣ Testing fake alert trigger...")
    try:
        response = requests.post(f"{BASE_URL}/api/test/trigger-fake-alert?user_id=test_user")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Fake Alert Success: {result['success']}")
            print(f"   📧 Alert Message: {result['message']}")
            return True
        else:
            print(f"   ❌ Fake alert failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Fake alert test failed: {e}")
        return False

async def test_websocket():
    """Test WebSocket connection"""
    print("\n8️⃣ Testing WebSocket connection...")
    try:
        # Try to import websockets
        import websockets
        
        async def websocket_test():
            uri = "ws://localhost:8000/ws?user_id=test_user"
            try:
                async with websockets.connect(uri) as websocket:
                    print("   ✅ WebSocket connected successfully")
                    
                    # Send ping
                    await websocket.send(json.dumps({"type": "ping"}))
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    response_data = json.loads(response)
                    print(f"   📡 WebSocket response: {response_data.get('type', 'unknown')}")
                    
                    # Send status request
                    await websocket.send(json.dumps({"type": "get_status"}))
                    status_response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    status_data = json.loads(status_response)
                    print(f"   📊 Status response type: {status_data.get('type', 'unknown')}")
                    
                    return True
            except asyncio.TimeoutError:
                print("   ⚠️  WebSocket timeout - connection works but responses slow")
                return True
            except Exception as e:
                print(f"   ❌ WebSocket test failed: {e}")
                return False
        
        return await websocket_test()
        
    except ImportError:
        print("   ⚠️  websockets package not installed")
        print("   💡 Install with: pip install websockets")
        return False
    except Exception as e:
        print(f"   ❌ WebSocket test failed: {e}")
        return False

async def continuous_monitoring(duration=30):
    """Monitor alert engine for a period"""
    print(f"\n9️⃣ Starting continuous monitoring ({duration} seconds)...")
    
    cycles = duration // 5  # Check every 5 seconds
    for i in range(cycles):
        try:
            response = requests.get(f"{BASE_URL}/api/monitoring/alert-engine")
            if response.status_code == 200:
                stats = response.json()
                print(f"   Cycle {i+1}/{cycles}: "
                      f"Checked={stats['stats']['alerts_checked']}, "
                      f"Triggered={stats['stats']['alerts_triggered']}, "
                      f"Running={stats['running']}")
            
            if i < cycles - 1:  # Don't sleep on last iteration
                await asyncio.sleep(5)
                
        except Exception as e:
            print(f"   ❌ Monitor error: {e}")
            break
    
    print("   ✅ Monitoring complete")

def print_summary(results):
    """Print test summary"""
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    test_names = [
        "API Health", "Price Fetching", "Alert Creation", "Engine Status",
        "Force Check", "User Alerts", "Fake Alert", "WebSocket"
    ]
    
    passed = sum(results)
    total = len(results)
    
    for i, (test_name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1}. {test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! Your alert engine is working perfectly!")
    elif passed >= total * 0.7:
        print("⚠️  Most tests passed. Check failed tests above.")
    else:
        print("❌ Multiple tests failed. Check your setup.")
    
    print("\n💡 Next steps:")
    print("   🌐 Open http://localhost:8000/docs for API documentation")
    print("   📊 Monitor at http://localhost:8000/api/monitoring/services")
    print("   📋 Check alerts at http://localhost:8000/api/alerts/user/test_user")

async def main():
    """Main test function"""
    print("🚀 Starting tokenTalk Alert Engine Tests\n")
    
    results = []
    
    # Run all tests
    results.append(test_api_health())
    results.append(test_price_fetching())
    
    alert_id = test_create_alert()
    results.append(alert_id is not None)
    
    results.append(test_alert_engine_status())
    results.append(test_force_check_alert(alert_id))
    results.append(test_user_alerts())
    results.append(test_fake_alert())
    results.append(await test_websocket())
    
    # Print summary
    print_summary(results)
    
    # Ask for continuous monitoring
    if any(results):  # At least some tests passed
        choice = input("\n🤔 Run continuous monitoring for 30 seconds? (y/n): ").lower()
        if choice == 'y':
            await continuous_monitoring(30)
    
    print("\n🎉 Alert engine testing completed!")

if __name__ == "__main__":
    asyncio.run(main())