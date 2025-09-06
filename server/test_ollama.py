# test_ollama.py - Simple Ollama test script
import asyncio
import aiohttp
import json

async def test_ollama_integration():
    """Test Ollama integration with StoneWatch"""
    
    base_url = "http://localhost:8000"
    
    # Test cases to show Ollama's capabilities
    test_cases = [
        {
            "message": "Alert me when ETH hits $4000",
            "category": "Simple",
            "expected": "Basic price alert"
        },
        {
            "message": "I want to be notified when ethereum reaches five thousand dollars",
            "category": "Natural Language",
            "expected": "ETH above $5000"
        },
        {
            "message": "Hey, can you watch ETH for me and let me know if it drops below 3k?",
            "category": "Conversational",
            "expected": "ETH below $3000"
        },
        {
            "message": "Please tell me if bitcoin goes over one hundred thousand",
            "category": "Natural Numbers",
            "expected": "BTC above $100000"
        },
        {
            "message": "Alert me when any DeFi token drops 15% while BTC stays stable",
            "category": "Complex",
            "expected": "Complex condition"
        },
        {
            "message": "What's the weather like?",
            "category": "Non-Alert",
            "expected": "Should not parse"
        }
    ]
    
    print("🦙 Testing StoneWatch + Ollama Integration")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        # First check status
        print("📊 Checking Service Status...")
        try:
            async with session.get(f"{base_url}/api/chat/status") as resp:
                if resp.status == 200:
                    status = await resp.json()
                    print(f"   Backend: {status['configuration']['active_backend']}")
                    print(f"   Ollama Available: {status['nlp_service']['ollama_available']}")
                    print(f"   Model: {status['nlp_service'].get('ollama_model', 'Unknown')}")
                    print(f"   Natural Language: {status['capabilities']['natural_language']}")
                    print()
                else:
                    print(f"   ❌ Status check failed: {resp.status}")
                    return
        except Exception as e:
            print(f"   ❌ Could not connect to API: {e}")
            print("   💡 Make sure to run: python main.py")
            return
        
        # Test each case
        for i, test_case in enumerate(test_cases, 1):
            message = test_case["message"]
            category = test_case["category"]
            
            print(f"{i}. {category.upper()}")
            print(f"   Input: '{message}'")
            
            try:
                # Test parsing
                async with session.post(
                    f"{base_url}/api/chat/test-parsing",
                    params={"message": message, "include_explanation": "true"}
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        
                        if data["parsed_successfully"]:
                            condition = data["parsed_condition"]
                            print(f"   ✅ Parsed: {condition['condition_type']}")
                            print(f"      Tokens: {condition['tokens']}")
                            print(f"      Threshold: {condition['threshold']}")
                            print(f"      Confidence: {condition['confidence']:.2f}")
                            
                            if data.get("explanation"):
                                print(f"      Explanation: {data['explanation']}")
                        else:
                            print(f"   ❌ Not parsed (expected for non-alerts)")
                        
                        print(f"   Response: {data['response']}")
                        print(f"   Backend: {data['backend']}")
                    else:
                        print(f"   ❌ API Error: {resp.status}")
                        
            except Exception as e:
                print(f"   ❌ Exception: {e}")
            
            print("-" * 40)

async def quick_ollama_test():
    """Quick test to verify Ollama is working"""
    print("🔍 Quick Ollama Test")
    print("-" * 25)
    
    # Test Ollama directly
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:11434/api/tags", timeout=3) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    models = [model["name"] for model in data.get("models", [])]
                    print(f"✅ Ollama running with models: {models}")
                else:
                    print(f"❌ Ollama error: {resp.status}")
    except Exception as e:
        print(f"❌ Ollama not running: {e}")
        print("💡 Start Ollama with: ollama serve")
        print("💡 Install model with: ollama pull phi")
        return False
    
    # Test StoneWatch API
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/health", timeout=3) as resp:
                if resp.status == 200:
                    print("✅ StoneWatch API running")
                else:
                    print(f"❌ StoneWatch API error: {resp.status}")
    except Exception as e:
        print(f"❌ StoneWatch API not running: {e}")
        print("💡 Start with: python main.py")
        return False
    
    return True

if __name__ == "__main__":
    print("🪨 StoneWatch + Ollama Test Suite")
    
    # Quick test first
    asyncio.run(quick_ollama_test())
    
    # Ask what to run
    response = input("\nRun full integration test? (y/n): ")
    if response.lower() == 'y':
        asyncio.run(test_ollama_integration())
    
    print("\n🎉 Testing completed!")
    print("\n💡 Setup reminder:")
    print("1. ollama serve")
    print("2. ollama pull phi")
    print("3. python main.py")
    print("4. Unlimited AI-powered alerts! 🚀")