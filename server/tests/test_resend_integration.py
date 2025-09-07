#!/usr/bin/env python3
"""
Test script for Resend email integration
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_resend_integration():
    """Test complete Resend email integration"""
    
    print("📧 Testing Resend Email Integration\n")
    
    # Test data
    test_user_id = "email_test_user"
    test_email = input("Enter your email address for testing: ").strip()
    
    if not test_email or "@" not in test_email:
        print("❌ Invalid email address. Exiting.")
        return
    
    print(f"Testing with user: {test_user_id}")
    print(f"Testing with email: {test_email}\n")
    
    print("1️⃣ Checking API health and email status...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API Status: {data['status']}")
            print(f"   📧 Email Service: {data.get('email_service', 'unknown')}")
            print(f"   📨 Emails Sent: {data.get('emails_sent', 0)}")
            print(f"   ❌ Emails Failed: {data.get('emails_failed', 0)}")
            
            if data.get('email_service') != 'enabled':
                print("   ⚠️  Email service not enabled. Check your RESEND_API_KEY in .env")
                print("   💡 Get your Resend API key from: https://resend.com/api-keys")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Cannot connect to API: {e}")
        return
    
    print("\n2️⃣ Setting up user email...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/test/setup-user-email",
            params={"user_id": test_user_id, "email": test_email}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Email setup: {data['success']}")
            print(f"   📧 Email: {data['email']}")
        else:
            print(f"   ❌ Email setup failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return
            
    except Exception as e:
        print(f"   ❌ Email setup error: {e}")
        return
    
    print("\n3️⃣ Creating a real alert...")
    try:
        response = requests.post(f"{BASE_URL}/api/chat/message", json={
            "message": "Alert me when ETH goes above $4000",
            "user_id": test_user_id
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Alert created: {data.get('alert_created', False)}")
            print(f"   🆔 Alert ID: {data.get('alert_id', 'N/A')}")
        else:
            print(f"   ❌ Alert creation failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Alert creation error: {e}")
    
    print("\n4️⃣ Triggering test email notification...")
    try:
        response = requests.post(f"{BASE_URL}/api/test/trigger-fake-alert?user_id={test_user_id}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Alert triggered: {data['success']}")
            print(f"   📧 Email enabled: {data.get('email_enabled', False)}")
            
            if data.get('email_enabled'):
                print(f"   📨 Email should be sent to: {test_email}")
                print(f"   💡 Check your inbox (including spam folder)")
            else:
                print(f"   ⚠️  Email not enabled - check Resend configuration")
        else:
            print(f"   ❌ Alert trigger failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Alert trigger error: {e}")
    
    print("\n5️⃣ Waiting 5 seconds for email delivery...")
    time.sleep(5)
    
    print("\n6️⃣ Checking email delivery stats...")
    try:
        response = requests.get(f"{BASE_URL}/api/monitoring/services")
        if response.status_code == 200:
            data = response.json()
            notification_service = data.get('notification_service', {})
            email_stats = notification_service.get('email_stats', {})
            
            print(f"   📨 Total emails sent: {email_stats.get('sent', 0)}")
            print(f"   ❌ Total emails failed: {email_stats.get('failed', 0)}")
            print(f"   🕐 Last email sent: {email_stats.get('last_sent', 'Never')}")
            
            capabilities = notification_service.get('capabilities', {})
            print(f"   📧 Email capability: {capabilities.get('email', False)}")
            print(f"   🔧 Resend configured: {capabilities.get('resend_configured', False)}")
            
        else:
            print(f"   ❌ Stats check failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Stats check error: {e}")
    
    print("\n7️⃣ Testing user profile retrieval...")
    try:
        response = requests.get(f"{BASE_URL}/api/users/{test_user_id}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ User found: {data['user_id']}")
            print(f"   📧 Email: {data.get('email', 'No email')}")
            print(f"   🔔 Notifications: {data.get('email_notifications', False)}")
        else:
            print(f"   ❌ User profile check failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ User profile error: {e}")
    
    print(f"\n{'='*60}")
    print("📧 RESEND INTEGRATION TEST SUMMARY")
    print(f"{'='*60}")
    
    # Final health check for summary
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            emails_sent = data.get('emails_sent', 0)
            emails_failed = data.get('emails_failed', 0)
            
            print(f"✅ API Status: {data['status']}")
            print(f"📧 Email Service: {data.get('email_service', 'unknown')}")
            print(f"📨 Emails Sent: {emails_sent}")
            print(f"❌ Emails Failed: {emails_failed}")
            
            if emails_sent > 0:
                print(f"\n🎉 SUCCESS! Email notification sent to {test_email}")
                print(f"📬 Check your inbox for the alert email")
                print(f"📱 You should see a beautifully formatted HTML email")
            elif data.get('email_service') == 'enabled':
                print(f"\n⚠️  Email service enabled but no emails sent")
                print(f"🔍 Check Resend dashboard for delivery status")
                print(f"🔗 https://resend.com/emails")
            else:
                print(f"\n❌ Email service not properly configured")
                print(f"💡 Check your .env file for RESEND_API_KEY")
                
    except Exception as e:
        print(f"❌ Final check failed: {e}")
    
    print(f"\n💡 Next steps:")
    print(f"   🌐 Open http://localhost:8000/docs to explore all endpoints")
    print(f"   📊 Monitor at http://localhost:8000/api/monitoring/services")
    print(f"   📧 Check Resend dashboard: https://resend.com/emails")
    print(f"   🧪 Create real alerts with: POST /api/chat/message")

def test_email_templates():
    """Test different email template scenarios"""
    print("\n🎨 Testing Email Templates...")
    
    test_scenarios = [
        {
            "name": "Price Above Alert",
            "condition": {"type": "price_above", "tokens": ["BTC"], "threshold": 100000},
            "prices": {"BTC": {"current_price": 105000, "formatted": "$105,000.00"}}
        },
        {
            "name": "Price Drop Alert", 
            "condition": {"type": "price_below", "tokens": ["ETH"], "threshold": 3000},
            "prices": {"ETH": {"current_price": 2800, "formatted": "$2,800.00"}}
        },
        {
            "name": "Percentage Change Alert",
            "condition": {"type": "price_change", "tokens": ["AAVE"], "threshold": -0.15},
            "prices": {"AAVE": {"current_price": 180, "formatted": "$180.00"}}
        }
    ]
    
    test_user = "template_test_user"
    
    for i, scenario in enumerate(test_scenarios):
        print(f"\n{i+1}. Testing {scenario['name']}...")
        
        # This would trigger different email templates
        # For demo purposes, just show what would be sent
        print(f"   📧 Template: {scenario['condition']['type']}")
        print(f"   🪙 Tokens: {scenario['condition']['tokens']}")
        print(f"   💰 Threshold: {scenario['condition']['threshold']}")

if __name__ == "__main__":
    try:
        test_resend_integration()
        
        # Ask if user wants to test templates
        choice = input("\n🤔 Test different email templates? (y/n): ").lower()
        if choice == 'y':
            test_email_templates()
            
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")