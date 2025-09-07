#!/usr/bin/env python3
"""
Simple WebSocket test script for tokenTalk API
Run this to test WebSocket connectivity separately
"""

import asyncio
import json
import sys

try:
    import websockets
except ImportError:
    print("❌ websockets package not installed")
    print("💡 Install with: pip install websockets")
    sys.exit(1)

async def test_websocket_connection():
    """Test WebSocket connection to tokenTalk API"""
    
    uri = "ws://localhost:8000/ws?user_id=test_user"
    
    try:
        print(f"🔌 Connecting to {uri}...")
        
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected successfully!")
            
            # Wait for welcome message
            try:
                welcome_message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                welcome_data = json.loads(welcome_message)
                print(f"📨 Welcome: {welcome_data.get('message', 'No message')}")
            except asyncio.TimeoutError:
                print("⏰ No welcome message received (timeout)")
            except json.JSONDecodeError:
                print(f"📨 Welcome (raw): {welcome_message}")
            
            # Test ping/pong
            print("\n🏓 Testing ping/pong...")
            ping_message = {"type": "ping"}
            await websocket.send(json.dumps(ping_message))
            
            try:
                pong_response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                pong_data = json.loads(pong_response)
                print(f"🏓 Pong received: {pong_data.get('type', 'unknown')}")
            except asyncio.TimeoutError:
                print("⏰ Ping/pong timeout")
            except json.JSONDecodeError:
                print(f"🏓 Pong (raw): {pong_response}")
            
            # Test status request
            print("\n📊 Testing status request...")
            status_message = {"type": "get_status"}
            await websocket.send(json.dumps(status_message))
            
            try:
                status_response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                status_data = json.loads(status_response)
                print(f"📊 Status response: {status_data.get('type', 'unknown')}")
                
                if status_data.get('type') == 'status_response':
                    engine_data = status_data.get('data', {}).get('alert_engine', {})
                    print(f"   Alert engine running: {engine_data.get('running', 'unknown')}")
                    print(f"   Alerts checked: {engine_data.get('stats', {}).get('alerts_checked', 0)}")
                    
            except asyncio.TimeoutError:
                print("⏰ Status request timeout")
            except json.JSONDecodeError:
                print(f"📊 Status (raw): {status_response}")
            
            # Test echo
            print("\n🔄 Testing echo...")
            echo_message = {"type": "test", "content": "Hello WebSocket!"}
            await websocket.send(json.dumps(echo_message))
            
            try:
                echo_response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                echo_data = json.loads(echo_response)
                print(f"🔄 Echo response: {echo_data.get('type', 'unknown')}")
            except asyncio.TimeoutError:
                print("⏰ Echo timeout")
            except json.JSONDecodeError:
                print(f"🔄 Echo (raw): {echo_response}")
            
            print("\n✅ WebSocket test completed successfully!")
            return True
            
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ WebSocket connection failed with HTTP {e.status_code}")
        if e.status_code == 404:
            print("💡 This usually means the WebSocket endpoint is not found")
            print("   Check that your FastAPI server is running on localhost:8000")
            print("   Check that the /ws endpoint is properly defined in main.py")
        return False
        
    except ConnectionRefusedError:
        print("❌ Connection refused - is the API server running?")
        print("💡 Start the server with: python main.py")
        return False
        
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        return False

async def test_multiple_connections():
    """Test multiple WebSocket connections"""
    print("\n🔗 Testing multiple WebSocket connections...")
    
    connections = []
    try:
        # Create 3 connections
        for i in range(3):
            uri = f"ws://localhost:8000/ws?user_id=test_user_{i}"
            websocket = await websockets.connect(uri)
            connections.append(websocket)
            print(f"✅ Connection {i+1} established")
        
        # Send a message from each connection
        for i, websocket in enumerate(connections):
            message = {"type": "ping", "from": f"user_{i}"}
            await websocket.send(json.dumps(message))
            
            response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
            print(f"📨 Response from connection {i+1}: {len(response)} chars")
        
        print("✅ Multiple connections test passed!")
        
    except Exception as e:
        print(f"❌ Multiple connections test failed: {e}")
        
    finally:
        # Close all connections
        for websocket in connections:
            try:
                await websocket.close()
            except:
                pass

def check_api_server():
    """Check if API server is running"""
    import requests
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API server is running (status: {data.get('status', 'unknown')})")
            return True
        else:
            print(f"⚠️  API server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server on localhost:8000")
        print("💡 Start the server with: python main.py")
        return False
    except Exception as e:
        print(f"❌ Error checking API server: {e}")
        return False

async def main():
    """Main test function"""
    print("🔌 tokenTalk WebSocket Test")
    print("=" * 40)
    
    # Check if API server is running
    if not check_api_server():
        print("\n❌ Cannot test WebSocket - API server not available")
        return
    
    # Test basic WebSocket connection
    success = await test_websocket_connection()
    
    if success:
        # Test multiple connections
        await test_multiple_connections()
        
        print("\n🎉 All WebSocket tests passed!")
        print("\n💡 Your WebSocket endpoint is working correctly!")
        print("   You can now connect from frontend applications")
        print("   Example: ws://localhost:8000/ws?user_id=YOUR_USER_ID")
    else:
        print("\n❌ WebSocket tests failed")
        print("\n🔧 Troubleshooting tips:")
        print("1. Make sure the API server is running: python main.py")
        print("2. Check that FastAPI includes the WebSocket endpoint")
        print("3. Verify no firewall is blocking port 8000")
        print("4. Try restarting the API server")

if __name__ == "__main__":
    asyncio.run(main())
