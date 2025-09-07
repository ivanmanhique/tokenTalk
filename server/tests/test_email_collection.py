#!/usr/bin/env python3
"""
Test script for frontend email collection feature
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_email_collection():
    """Test the email collection in chat API"""
    
    print("📧 Testing Frontend Email Collection\n")
    
    # Test cases
    test_cases = [
        {
            "name": "Alert with Email",
            "data": {
                "message": "Alert me when ETH goes above $4000",
                "user_id": "frontend_user_1",
                "email": "user1@frontend.test"
            },
            "expected_email_registered": True
        },
        {
            "name": "Alert without Email",
            "data": {
                "message": "Alert me when BTC hits $100000",
                "user_id": "frontend_user_2"
            },
            "expected_email_registered": False
        },
        {
            "name": "Invalid Message with Email",
            "data": {
                "message": "Hello there!",
                "user_id": "frontend_user_3", 
                "email": "user3@frontend.test"
            },
            "expected_email_registered": True,
            "expected_alert_created": False
        },
        {
            "name": "Invalid Email Format",
            "data": {
                "message": "Alert me when AAVE hits $200",
                "user_id": "frontend_user_4",
                "email": "invalid-email"
            },
            "expected_error": True
        }
    ]
    
    print("1️⃣ Testing different email collection scenarios...\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['name']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/chat/message-2",
                json=test_case["data"],
                headers={"Content-Type": "application/json"}
            )
            
            if test_case.get("expected_error"):
                if response.status_code != 200:
                    print(f"   ✅ Expected error occurred: {response.status_code}")
                else:
                    print(f"   ❌ Expected error but got success")
            else:
                if response.status_code == 200:
                    result = response.json()
                    
                    # Check email registration
                    email_registered = result.get("email_registered", False)
                    expected_email = test_case.get("expected_email_registered", False)
                    
                    if email_registered == expected_email:
                        print(f"   ✅ Email registration: {email_registered} (expected: {expected_email})")
                    else:
                        print(f"   ❌ Email registration: {email_registered} (expected: {expected_email})")
                    
                    # Check alert creation
                    alert_created = result.get("alert_created", False)
                    expected_alert = test_case.get("expected_alert_created", True)
                    
                    if alert_created == expected_alert:
                        print(f"   ✅ Alert created: {alert_created} (expected: {expected_alert})")
                    else:
                        print(f"   ❌ Alert created: {alert_created} (expected: {expected_alert})")
                    
                    # Check notifications enabled
                    notifications = result.get("notifications_enabled", {})
                    print(f"   📱 WebSocket notifications: {notifications.get('websocket', False)}")
                    print(f"   📧 Email notifications: {notifications.get('email', False)}")
                    
                    # Show response
                    print(f"   💬 Response: {result.get('response', 'No response')[:100]}...")
                    
                else:
                    print(f"   ❌ Request failed: {response.status_code}")
                    print(f"   Error: {response.text}")
                    
        except Exception as e:
            print(f"   ❌ Test error: {e}")
        
        print()  # Empty line between tests
    
    print("2️⃣ Verifying stored user emails...\n")
    
    # Check if emails were stored in database
    users_to_check = ["frontend_user_1", "frontend_user_3"]
    
    for user_id in users_to_check:
        try:
            response = requests.get(f"{BASE_URL}/api/users/{user_id}")
            if response.status_code == 200:
                user_data = response.json()
                email = user_data.get("email")
                print(f"   ✅ {user_id}: {email}")
            else:
                print(f"   ❌ {user_id}: Failed to retrieve ({response.status_code})")
        except Exception as e:
            print(f"   ❌ {user_id}: Error - {e}")
    
    print("\n3️⃣ Testing notification delivery...\n")
    
    # Test notification for user with email
    try:
        response = requests.post(f"{BASE_URL}/api/test/trigger-fake-alert?user_id=frontend_user_1")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Fake alert triggered for user with email: {result.get('success', False)}")
        else:
            print(f"   ❌ Failed to trigger alert: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Notification test error: {e}")
    
    # Test notification for user without email
    try:
        response = requests.post(f"{BASE_URL}/api/test/trigger-fake-alert?user_id=frontend_user_2")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Fake alert triggered for user without email: {result.get('success', False)}")
        else:
            print(f"   ❌ Failed to trigger alert: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Notification test error: {e}")
    
    print("\n4️⃣ Checking email delivery stats...\n")
    
    try:
        response = requests.get(f"{BASE_URL}/api/monitoring/services")
        if response.status_code == 200:
            services = response.json()
            email_stats = services.get("notification_service", {}).get("email_stats", {})
            print(f"   📧 Emails sent: {email_stats.get('sent', 0)}")
            print(f"   ❌ Emails failed: {email_stats.get('failed', 0)}")
            print(f"   🕐 Last sent: {email_stats.get('last_sent', 'Never')}")
        else:
            print(f"   ❌ Failed to get service stats: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Stats check error: {e}")
    
    print(f"\n{'='*60}")
    print("📧 EMAIL COLLECTION TEST SUMMARY")
    print(f"{'='*60}")
    print("✅ If working correctly:")
    print("   - Users with email get both WebSocket + Email notifications")
    print("   - Users without email get only WebSocket notifications") 
    print("   - Invalid emails are rejected with error")
    print("   - Email addresses are stored in database")
    print("   - Chat response confirms notification preferences")
    print(f"{'='*60}")

if __name__ == "__main__":
    try:
        test_email_collection()
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
