# api/prices.py - Complete Price API endpoints
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict
from services.redstone_client import RedStoneClient

router = APIRouter()

@router.get("/current/{symbol}")
async def get_current_price(symbol: str):
    """Get current price for a single token"""
    try:
        async with RedStoneClient() as client:
            price_data = await client.get_token_price(symbol.upper())
            
            if price_data.get("error"):
                raise HTTPException(status_code=404, detail=f"Could not fetch price for {symbol}: {price_data['error']}")
            
            return {
                "symbol": price_data["symbol"],
                "price": price_data["price"],
                "timestamp": price_data.get("timestamp"),
                "source": price_data["source"],
                "formatted": f"${price_data['price']:,.2f}" if price_data['price'] > 0 else "N/A"
            }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching price: {str(e)}")

@router.get("/multiple")
async def get_multiple_prices(
    symbols: str = Query(..., description="Comma-separated token symbols: ETH,BTC,AAVE")
):
    """Get prices for multiple tokens (comma-separated)"""
    try:
        # Parse and validate symbols
        symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
        
        if not symbol_list:
            raise HTTPException(status_code=400, detail="No valid symbols provided")
        
        if len(symbol_list) > 20:  # Limit for performance
            raise HTTPException(status_code=400, detail="Too many symbols. Maximum 20 allowed.")
        
        async with RedStoneClient() as client:
            prices = await client.get_multiple_prices(symbol_list)
            
            # Format response
            formatted_prices = {}
            for symbol, data in prices.items():
                formatted_prices[symbol] = {
                    "symbol": symbol,
                    "price": data.get("price", 0),
                    "timestamp": data.get("timestamp"),
                    "source": data.get("source", "redstone"),
                    "formatted": f"${data.get('price', 0):,.2f}" if data.get('price', 0) > 0 else "N/A",
                    "error": data.get("error")
                }
            
            return {
                "symbols": symbol_list,
                "count": len(formatted_prices),
                "prices": formatted_prices,
                "timestamp": max([p.get("timestamp", 0) for p in formatted_prices.values()] or [0])
            }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching multiple prices: {str(e)}")

@router.get("/defi")
async def get_defi_prices():
    """Get prices for popular DeFi tokens"""
    try:
        async with RedStoneClient() as client:
            defi_tokens = await client.get_defi_tokens()
            prices = await client.get_multiple_prices(defi_tokens)
            
            # Format for DeFi dashboard
            defi_data = {}
            for symbol, data in prices.items():
                defi_data[symbol] = {
                    "symbol": symbol,
                    "price": data.get("price", 0),
                    "formatted": f"${data.get('price', 0):,.2f}" if data.get('price', 0) > 0 else "N/A",
                    "error": data.get("error")
                }
            
            return {
                "category": "DeFi Tokens",
                "tokens": defi_tokens,
                "count": len(defi_data),
                "prices": defi_data
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching DeFi prices: {str(e)}")

@router.get("/")
async def price_info():
    """Get information about available price endpoints"""
    return {
        "message": "RedStone Price API",
        "endpoints": {
            "/current/{symbol}": "Get current price for a token",
            "/multiple?symbols=ETH,BTC": "Get multiple token prices",
            "/defi": "Get popular DeFi token prices"
        },
        "supported_tokens": "ETH, BTC, AAVE, UNI, SUSHI, COMP, MKR, SNX, CRV, 1INCH, and 100+ more",
        "data_source": "RedStone Oracles"
    }