# test_chat.py - Test the chat interface
import asyncio
import aiohttp
import json

async def test_chat_interface():
    """Test the chat interface"""
    base_url = "http://localhost:8000"
    
    test_messages = [
        "Alert me when ETH hits $4000",
        "Tell me when BTC drops below $90000",
        "Notify me when AAVE goes above $350",
        "ETH drops 15%",
        "Hello there, how are you?",  # Should not parse
        "When bitcoin reaches 100000"
    ]
    
    print("🧪 Testing Chat Interface...")
    
    async with aiohttp.ClientSession() as session:
        for message in test_messages:
            print(f"\n💬 Testing: '{message}'")
            
            # Test parsing only
            async with session.post(
                f"{base_url}/api/chat/test-parsing",
                params={"message": message}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   Parsed: {data['parsed_condition']}")
                    print(f"   Response: {data['response']}")
                    print(f"   Would create alert: {data['would_create_alert']}")
                else:
                    print(f"   Error: {response.status}")
    
    print("\n✅ Chat interface testing completed!")

if __name__ == "__main__":
    asyncio.run(test_chat_interface())