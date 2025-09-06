# services/nlp_service.py - Ollama-focused with easy API switching
import aiohttp
import json
import re
from typing import Dict, List, Optional
import asyncio
from dataclasses import dataclass
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

class NLPService:
    def __init__(self):
        self.session = None
        self.ollama_available = False
        self.ollama_model = None
        
        # Token mapping
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
        
        self.defi_tokens = ["AAVE", "UNI", "SUSHI", "COMP", "MKR", "SNX", "CRV", "1INCH"]
    
    async def init(self):
        """Initialize the service and check Ollama availability"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        await self._check_ollama()
    
    async def close(self):
        """Close the session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def _check_ollama(self):
        """Check if Ollama is available and get models"""
        try:
            async with self.session.get(
                f"{settings.OLLAMA_URL}/api/tags", 
                timeout=3
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    models = [model["name"] for model in data.get("models", [])]
                    
                    if models:
                        self.ollama_available = True
                        self.ollama_model = models[0]  # Use first available
                        print(f"✅ Ollama connected: {self.ollama_model}")
                        return True
                    else:
                        print("⚠️ Ollama running but no models installed")
                        
        except Exception as e:
            print(f"⚠️ Ollama not available: {e}")
        
        self.ollama_available = False
        return False
    
    async def parse_message(self, message: str, user_context: Optional[Dict] = None) -> Optional[ParsedCondition]:
        """Parse message using best available method"""
        if not self.session:
            await self.init()
        
        # Try Ollama first
        if self.ollama_available:
            try:
                return await self._parse_with_ollama(message, user_context)
            except Exception as e:
                print(f"Ollama parsing failed, falling back to basic: {e}")
        
        # Easy switch point for APIs - just change this condition
        if settings.USE_CLOUD_API and settings.has_api_key():
            try:
                return await self._parse_with_cloud_api(message, user_context)
            except Exception as e:
                print(f"Cloud API parsing failed, falling back to basic: {e}")
        
        # Always fallback to basic patterns
        return await self._parse_with_basic(message)
    
    async def _parse_with_ollama(self, message: str, user_context: Optional[Dict] = None) -> Optional[ParsedCondition]:
        """Parse using Ollama"""
        system_prompt = self._create_system_prompt()
        user_prompt = self._create_user_prompt(message, user_context)
        
        payload = {
            "model": self.ollama_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 500
            }
        }
        
        async with self.session.post(
            f"{settings.OLLAMA_URL}/api/chat",
            json=payload,
            timeout=30
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                response_text = data["message"]["content"].strip()
                return self._parse_json_response(response_text)
            else:
                raise Exception(f"Ollama API error: {resp.status}")
    
    async def _parse_with_cloud_api(self, message: str, user_context: Optional[Dict] = None) -> Optional[ParsedCondition]:
        """Parse using cloud API (Claude/OpenAI) - Easy to switch"""
        
        # Claude API example (uncomment to use)
        if settings.CLAUDE_API_KEY:
            return await self._parse_with_claude(message, user_context)
        
        # OpenAI API example (uncomment to use)
        # if settings.OPENAI_API_KEY:
        #     return await self._parse_with_openai(message, user_context)
        
        raise Exception("No cloud API configured")
    
    async def _parse_with_claude(self, message: str, user_context: Optional[Dict] = None) -> Optional[ParsedCondition]:
        """Parse using Claude API"""
        system_prompt = self._create_system_prompt()
        user_prompt = self._create_user_prompt(message, user_context)
        
        headers = {
            "x-api-key": settings.CLAUDE_API_KEY,
            "content-type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 500,
            "messages": [{"role": "user", "content": f"{system_prompt}\n\n{user_prompt}"}]
        }
        
        async with self.session.post(
            "https://api.anthropic.com/v1/messages",
            json=payload,
            headers=headers,
            timeout=30
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                response_text = data["content"][0]["text"].strip()
                return self._parse_json_response(response_text)
            else:
                raise Exception(f"Claude API error: {resp.status}")
    
    async def _parse_with_basic(self, message: str) -> Optional[ParsedCondition]:
        """Fallback basic pattern matching"""
        message_lower = message.lower()
        
        # Simple regex patterns for common cases
        patterns = {
            "price_above": [
                r"(\w+)\s+(?:hits|reaches|goes above|above|over)\s+\$?(\d+\.?\d*)",
                r"when\s+(\w+)\s+\$?(\d+\.?\d*)",
                r"(?:alert|notify|tell).*?(\w+).*?(\d+\.?\d*)"
            ],
            "price_below": [
                r"(\w+)\s+(?:drops|falls|goes below|below|under)\s+\$?(\d+\.?\d*)"
            ],
            "price_change": [
                r"(\w+)\s+(?:drops|falls)\s+(\d+)%"
            ]
        }
        
        for condition_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, message_lower, re.IGNORECASE)
                if match:
                    token_raw = match.group(1).upper()
                    value = float(match.group(2))
                    
                    # Normalize token name
                    token = self.token_mapping.get(token_raw.lower(), token_raw)
                    
                    # Convert percentage to decimal for price_change
                    if condition_type == "price_change":
                        value = -value / 100  # Make negative for drops
                    
                    return ParsedCondition(
                        condition_type=condition_type,
                        tokens=[token],
                        threshold=value,
                        timeframe="24h",
                        confidence=0.7,
                        explanation=f"Pattern match: {condition_type} for {token}"
                    )
        
        return None
    
    def _parse_json_response(self, response_text: str) -> Optional[ParsedCondition]:
        """Parse JSON response from AI models"""
        try:
            # Clean up response (remove markdown if present)
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            elif response_text.startswith("```") and response_text.endswith("```"):
                response_text = response_text[3:-3].strip()
            
            # Find JSON object
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                response_text = response_text[json_start:json_end]
            
            parsed_data = json.loads(response_text)
            
            # Validate response structure
            if not parsed_data.get("valid", False):
                return None
            
            if parsed_data.get("intent") != "create_alert":
                return None
            
            condition_data = parsed_data.get("condition", {})
            if not condition_data:
                return None
            
            # Normalize tokens
            raw_tokens = condition_data.get("tokens", [])
            normalized_tokens = []
            
            for token in raw_tokens:
                normalized = self.token_mapping.get(token.lower(), token.upper())
                normalized_tokens.append(normalized)
            
            # Handle special cases
            if any("defi" in str(token).lower() for token in raw_tokens):
                normalized_tokens = self.defi_tokens
            
            return ParsedCondition(
                condition_type=condition_data.get("condition_type", ""),
                tokens=normalized_tokens,
                threshold=float(condition_data.get("threshold", 0)),
                timeframe=condition_data.get("timeframe", "24h"),
                secondary_condition=condition_data.get("secondary_condition"),
                confidence=float(parsed_data.get("confidence", 0.8)),
                explanation=parsed_data.get("explanation", "")
            )
            
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            print(f"Response: {response_text[:200]}...")
            return None
        except Exception as e:
            print(f"Response parsing error: {e}")
            return None
    
    def _create_system_prompt(self) -> str:
        """System prompt for AI models"""
        return """You are a crypto price alert parser. Convert natural language into structured JSON alerts.

SUPPORTED CONDITIONS:
- price_above: Token goes above price threshold  
- price_below: Token goes below price threshold
- price_change: Token changes by percentage (negative for drops)
- relative_change: Complex multi-token conditions

TOKENS: BTC, ETH, AAVE, UNI, SUSHI, COMP, MKR, SNX, CRV, 1INCH
GROUPS: "DeFi tokens" = all DeFi tokens above

REQUIRED JSON FORMAT:
{
  "intent": "create_alert",
  "valid": true,
  "condition": {
    "condition_type": "price_above|price_below|price_change|relative_change",
    "tokens": ["ETH"],
    "threshold": 4000.0,
    "timeframe": "24h"
  },
  "confidence": 0.9,
  "explanation": "Will alert when ETH goes above $4000"
}

EXAMPLES:
- "Alert when ETH hits $4000" → price_above, ["ETH"], 4000
- "Bitcoin drops 15%" → price_change, ["BTC"], -0.15
- "I want ethereum at five thousand" → price_above, ["ETH"], 5000

Return ONLY valid JSON. For non-alerts, set "valid": false."""

    def _create_user_prompt(self, message: str, user_context: Optional[Dict] = None) -> str:
        """User prompt with optional context"""
        context_str = ""
        if user_context:
            context_str = f" Context: {json.dumps(user_context)}"
        
        return f'Parse: "{message}"{context_str}'
    
    async def generate_response(self, parsed_condition: Optional[ParsedCondition], original_message: str) -> str:
        """Generate friendly response"""
        if not parsed_condition:
            return """I didn't understand that. Try:
- "Alert me when ETH hits $4000"
- "Tell me when BTC drops below $90000"  
- "Notify me when any DeFi token drops 15%"

I can set up crypto price alerts! 📈"""
        
        # Try Ollama for response generation if available
        if self.ollama_available:
            try:
                return await self._generate_ollama_response(parsed_condition, original_message)
            except:
                pass
        
        # Fallback to simple response
        return self._generate_simple_response(parsed_condition)
    async def _generate_ollama_response(self, condition: ParsedCondition, original_message: str) -> str:
        """Generate response using Ollama"""
        prompt = f"""Generate a friendly crypto alert confirmation (under 50 words):

        Alert: {condition.condition_type}
        Tokens: {condition.tokens}  
        Threshold: {condition.threshold}
        Message: "{original_message}"

        Reply with ✅ emoji and confirmation. Do not include thinking steps or explanations."""

        payload = {
            "model": self.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": 100, "temperature": 0.3}
        }

        async with self.session.post(f"{settings.OLLAMA_URL}/api/generate", json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                response = data["response"].strip()
                
                # Clean up reasoning traces from deepseek models
                if "<think>" in response:
                    # Extract only the final response after thinking
                    if "</think>" in response:
                        response = response.split("</think>")[-1].strip()
                    else:
                        # Fallback to simple response
                        return self._generate_simple_response(condition)
                
                # Ensure it starts with checkmark
                if not response.startswith("✅"):
                    response = "✅ " + response
                    
                return response

        raise Exception("Ollama response generation failed")
#     async def _generate_ollama_response(self, condition: ParsedCondition, original_message: str) -> str:
#         """Generate response using Ollama"""
#         prompt = f"""Generate a friendly crypto alert confirmation (under 50 words):

# Alert: {condition.condition_type}
# Tokens: {condition.tokens}  
# Threshold: {condition.threshold}
# Message: "{original_message}"

# Reply with ✅ emoji and confirmation."""

#         payload = {
#             "model": self.ollama_model,
#             "prompt": prompt,
#             "stream": False,
#             "options": {"num_predict": 100, "temperature": 0.3}
#         }
        
#         async with self.session.post(f"{settings.OLLAMA_URL}/api/generate", json=payload) as resp:
#             if resp.status == 200:
#                 data = await resp.json()
#                 response = data["response"].strip()
                
#                 # Ensure it starts with checkmark
#                 if not response.startswith("✅"):
#                     response = "✅ " + response
                    
#                 return response
        
#         raise Exception("Ollama response generation failed")
    
    def _generate_simple_response(self, condition: ParsedCondition) -> str:
        """Simple response fallback"""
        tokens_str = ", ".join(condition.tokens)
        
        if condition.condition_type == "price_above":
            return f"✅ I'll alert you when {tokens_str} goes above ${condition.threshold:,.2f}"
        elif condition.condition_type == "price_below":
            return f"✅ I'll alert you when {tokens_str} drops below ${condition.threshold:,.2f}"
        elif condition.condition_type == "price_change":
            percentage = abs(condition.threshold * 100)
            direction = "drops" if condition.threshold < 0 else "rises"
            return f"✅ I'll alert you when {tokens_str} {direction} {percentage}%"
        elif condition.condition_type == "relative_change":
            return f"✅ Complex alert set for {tokens_str}"
        else:
            return f"✅ Alert created for {tokens_str}!"
    
    async def get_status(self) -> Dict:
        """Get service status"""
        if not self.session:
            await self.init()
        
        return {
            "service": "NLP Service",
            "ollama_available": self.ollama_available,
            "ollama_model": self.ollama_model,
            "cloud_api_enabled": settings.USE_CLOUD_API,
            "fallback_available": True,
            "capabilities": {
                "natural_language": self.ollama_available or settings.USE_CLOUD_API,
                "complex_conditions": self.ollama_available or settings.USE_CLOUD_API,
                "unlimited_usage": self.ollama_available
            }
        }

# Global service instance
nlp_service = NLPService()