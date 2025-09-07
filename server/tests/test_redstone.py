import asyncio
from services.redstone_client import RedStoneClient

async def test_redstone():
    """Test RedStone API connection"""
    print("Testing RedStone API connection...")
    
    async with RedStoneClient() as client:
        # Test single token
        btc_data = await client.get_token_price("BTC")
        print(f"BTC: {btc_data}")
        
        # Test multiple tokens
        tokens = ["ETH", "BTC", "AAVE", "UNI"]
        prices = await client.get_multiple_prices(tokens)
        
        print("\nMultiple token prices:")
        for symbol, data in prices.items():
            price = data.get("price", 0)
            print(f"{symbol}: ${price:,.2f}")

if __name__ == "__main__":
    asyncio.run(test_redstone())