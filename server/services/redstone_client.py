import aiohttp
import asyncio
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)
# https://api.redstone.finance/prices?symbol=USDC&provider=redstone
class RedStoneClient:
    def __init__(self):
        self.base_url = "https://api.redstone.finance/prices"
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_token_price(self, symbol: str) -> Dict:
        """Get current price data for a token"""
        if not self.session:
            self.session = aiohttp.ClientSession()
            
        try:
            url = f"{self.base_url}?symbol={symbol.upper()}&provider=redstone"
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json(content_type=None)

                    if isinstance(data, list) and len(data) > 0:
                        entry = data[0]
                        return {
                            "symbol": entry.get("symbol", symbol.upper()),
                            "price": entry.get("value", 0),
                            "timestamp": entry.get("timestamp"),
                            "source": "redstone"
                        }
                    else:
                        return {"symbol": symbol.upper(), "price": 0, "error": "empty_response"}
                else:
                    logger.error(f"Failed to fetch {symbol}: {response.status}")
                    return {"symbol": symbol.upper(), "price": 0, "error": "fetch_failed"}
                    
        except asyncio.TimeoutError:
            logger.error(f"Timeout fetching price for {symbol}")
            return {"symbol": symbol.upper(), "price": 0, "error": "timeout"}
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {e}")
            return {"symbol": symbol.upper(), "price": 0, "error": str(e)}
    
    async def get_multiple_prices(self, symbols: List[str]) -> Dict[str, Dict]:
        """Get prices for multiple tokens efficiently"""
        tasks = [self.get_token_price(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        prices = {}
        for i, result in enumerate(results):
            symbol = symbols[i].upper()
            if isinstance(result, Exception):
                prices[symbol] = {"price": 0, "error": str(result)}
            else:
                prices[symbol] = result
                
        return prices
    
    async def get_defi_tokens(self) -> List[str]:
        """Get list of popular DeFi tokens (hardcoded for hackathon speed)"""
        return ["AAVE", "UNI", "SUSHI", "COMP", "MKR", "SNX", "CRV", "1INCH"]
