import openai
import httpx
import json
import re
from typing import Dict, List, Optional, Union
import asyncio
from dataclasses import dataclass
import os
from datetime import datetime

from config import settings

@dataclass
class ParsedCondition:
    condition_type: str  # "price_above", "price_below", "price_change", "relative_change"
    tokens: List[str]
    threshold: float
    timeframe: str = "24h"
    secondary_condition: Optional[Dict] = None
    confidence: float = 0.0
    explanation: str = ""

class OpenAINLPService:
    def __init__(self):
        http_client = httpx.Client()
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY, http_client=http_client)
        self.token_mapping = {
            "bitcoin": "BTC", "btc": "BTC",
            "ethereum": "ETH", "eth": "ETH", "ether": "ETH",
            "aave": "AAVE", "uniswap": "UNI", "uni": "UNI",
            "sushi": "SUSHI", "sushiswap": "SUSHI",
            "compound": "COMP", "comp": "COMP",
            "maker": "MKR", "mkr": "MKR",
            "synthetix": "SNX", "snx": "SNX",
            "curve": "CRV", "crv": "CRV",
            "1inch": "1INCH", "oneinch": "1INCH"
        }
        
        # DeFi token groups for complex queries
        self.defi_tokens = ["AAVE", "UNI", "SUSHI", "COMP", "MKR", "SNX", "CRV", "1INCH"]
    
    async def parse_message(self, message: str, user_context: Optional[Dict] = None) -> Optional[ParsedCondition]:
        """Parse natural language message using OpenAI"""
        try:
            # Create enhanced prompt for OpenAI
            system_prompt = self._create_system_prompt()
            user_prompt = self._create_user_prompt(message, user_context)
            
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            # Parse the JSON response
            response_text = response.choices[0].message.content.strip()
            
            # Clean up the response (remove markdown if present)
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()
            
            parsed_data = json.loads(response_text)
            
            # Validate and create ParsedCondition
            if parsed_data.get("intent") == "create_alert" and parsed_data.get("valid"):
                condition_data = parsed_data["condition"]
                
                # Normalize token names
                normalized_tokens = []
                for token in condition_data["tokens"]:
                    normalized = self.token_mapping.get(token.lower(), token.upper())
                    normalized_tokens.append(normalized)
                
                # Handle special token groups
                if "defi" in message.lower() or "any defi" in message.lower():
                    normalized_tokens = self.defi_tokens
                
                return ParsedCondition(
                    condition_type=condition_data["condition_type"],
                    tokens=normalized_tokens,
                    threshold=condition_data["threshold"],
                    timeframe=condition_data.get("timeframe", "24h"),
                    secondary_condition=condition_data.get("secondary_condition"),
                    confidence=parsed_data.get("confidence", 0.0),
                    explanation=parsed_data.get("explanation", "")
                )
            
            return None
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response was: {response_text}")
            return None
        except Exception as e:
            print(f"OpenAI parsing error: {e}")
            # Fallback to basic parsing
            return await self._fallback_parse(message)
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for OpenAI"""
        return """You are a crypto price alert parser. Parse user messages into structured alert conditions.

SUPPORTED CONDITION TYPES:
- price_above: Token price goes above a threshold
- price_below: Token price goes below a threshold  
- price_change: Token price changes by percentage (positive or negative)
- relative_change: Complex condition with multiple tokens and secondary conditions

SUPPORTED TOKENS: BTC, ETH, AAVE, UNI, SUSHI, COMP, MKR, SNX, CRV, 1INCH
SPECIAL GROUPS: "DeFi tokens" = [AAVE, UNI, SUSHI, COMP, MKR, SNX, CRV, 1INCH]

RESPONSE FORMAT (JSON only, no markdown):
{
  "intent": "create_alert" | "question" | "other",
  "valid": true | false,
  "condition": {
    "condition_type": "price_above|price_below|price_change|relative_change",
    "tokens": ["BTC", "ETH"],
    "threshold": 4000.0,
    "timeframe": "24h",
    "secondary_condition": {
      "token": "BTC",
      "condition": "stable",
      "threshold": 0.03
    }
  },
  "confidence": 0.9,
  "explanation": "Will alert when ETH price goes above $4000"
}

EXAMPLES:
- "Alert me when ETH hits $4000" → price_above, tokens: ["ETH"], threshold: 4000
- "Tell me when BTC drops 15%" → price_change, tokens: ["BTC"], threshold: -0.15
- "When any DeFi token drops 15% while BTC stays stable" → relative_change with secondary_condition

For non-alert messages, set "intent": "question" and "valid": false."""

    def _create_user_prompt(self, message: str, user_context: Optional[Dict] = None) -> str:
        """Create the user prompt with context"""
        context_info = ""
        if user_context:
            context_info = f"\nUser context: {json.dumps(user_context)}"
        
        return f"""Parse this message: "{message}"{context_info}

Return only valid JSON matching the format specified."""

    async def _fallback_parse(self, message: str) -> Optional[ParsedCondition]:
        """Fallback to basic regex parsing if OpenAI fails"""
        message_lower = message.lower()
        
        # Simple patterns as fallback
        patterns = {
            "price_above": [
                r"(\w+)\s+(?:hits|reaches|goes above|above|over)\s+\$?(\d+\.?\d*)",
                r"when\s+(\w+)\s+\$?(\d+\.?\d*)"
            ],
            "price_below": [
                r"(\w+)\s+(?:drops|falls|goes below|below|under)\s+\$?(\d+\.?\d*)"
            ],
            "price_change": [
                r"(\w+)\s+drops?\s+(\d+)%"
            ]
        }
        
        for condition_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, message_lower, re.IGNORECASE)
                if match:
                    token = match.group(1).upper()
                    value = float(match.group(2))
                    
                    # Normalize token
                    token = self.token_mapping.get(token.lower(), token)
                    
                    if condition_type == "price_change":
                        value = -value / 100  # Convert to negative decimal
                    
                    return ParsedCondition(
                        condition_type=condition_type,
                        tokens=[token],
                        threshold=value,
                        timeframe="24h",
                        confidence=0.6,
                        explanation=f"Fallback parsing: {condition_type} for {token}"
                    )
        
        return None
    
    async def generate_response(self, parsed_condition: Optional[ParsedCondition], original_message: str) -> str:
        """Generate a natural response using OpenAI"""
        if not parsed_condition:
            return await self._generate_help_response(original_message)
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a helpful crypto price alert assistant. Generate friendly, concise confirmation messages."
                    },
                    {
                        "role": "user", 
                        "content": f"""Generate a confirmation message for this alert:
Condition: {parsed_condition.condition_type}
Tokens: {parsed_condition.tokens}
Threshold: {parsed_condition.threshold}
Original message: "{original_message}"

Keep it under 50 words and use emojis. Start with ✅ or 🚨."""
                    }
                ],
                temperature=0.3,
                max_tokens=100
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Response generation error: {e}")
            return self._generate_fallback_response(parsed_condition)
    
    async def _generate_help_response(self, original_message: str) -> str:
        """Generate a helpful response for unrecognized messages"""
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful crypto alert assistant. The user's message wasn't recognized as an alert request. Provide helpful examples."
                    },
                    {
                        "role": "user",
                        "content": f"""The user said: "{original_message}"

This doesn't seem like an alert request. Provide 2-3 helpful examples of how to create alerts. Keep it under 100 words."""
                    }
                ],
                temperature=0.5,
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return """I didn't understand that. Try something like:
• "Alert me when ETH hits $4000"
• "Tell me when BTC drops below $90000"  
• "Notify me when any DeFi token drops 15%"
• "When AAVE goes above $350"

I can help you set up price alerts for crypto tokens! 📈"""
    
    def _generate_fallback_response(self, parsed_condition: ParsedCondition) -> str:
        """Generate fallback response without OpenAI"""
        condition = parsed_condition
        token_str = ", ".join(condition.tokens)
        
        if condition.condition_type == "price_above":
            return f"✅ I'll alert you when {token_str} goes above ${condition.threshold:,.2f}"
        elif condition.condition_type == "price_below":
            return f"✅ I'll alert you when {token_str} drops below ${condition.threshold:,.2f}"
        elif condition.condition_type == "price_change":
            percentage = abs(condition.threshold * 100)
            direction = "drops" if condition.threshold < 0 else "rises"
            return f"✅ I'll alert you when {token_str} {direction} {percentage}%"
        elif condition.condition_type == "relative_change":
            return f"✅ Complex alert set up for {token_str} with custom conditions"
        
        return "✅ Alert created successfully!"
