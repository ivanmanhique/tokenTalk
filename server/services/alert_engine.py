# services/alert_engine.py - Real-time alert monitoring engine
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

from database import Database, Alert
from services.redstone_client import RedStoneClient
# from services.notification_service import NotificationService
from config import settings
from services.enhanced_notification_service import EnhancedNotificationService

logger = logging.getLogger(__name__)

class AlertEngine:
    def __init__(self):
        self.db = Database()
        self.redstone = RedStoneClient()
        self.notifications = EnhancedNotificationService()
        self.running = False
        self.monitoring_interval = 30  # seconds
        self.price_cache = {}
        self.last_price_fetch = None
        self.stats = {
            "alerts_checked": 0,
            "alerts_triggered": 0,
            "last_run": None,
            "errors": 0
        }
    
    async def start_monitoring(self):
        """Start the real-time monitoring loop"""
        self.running = True
        logger.info("🚨 Alert Engine started - monitoring every %d seconds", self.monitoring_interval)
        
        while self.running:
            try:
                await self._monitoring_cycle()
                await asyncio.sleep(self.monitoring_interval)
            except Exception as e:
                logger.error(f"Alert monitoring error: {e}")
                self.stats["errors"] += 1
                await asyncio.sleep(5)  # Short delay on error
    
    def stop_monitoring(self):
        """Stop the monitoring loop"""
        self.running = False
        logger.info("🛑 Alert Engine stopped")
    
    async def _monitoring_cycle(self):
        """Single monitoring cycle - check all alerts"""
        cycle_start = datetime.now()
        
        try:
            # Get all active alerts
            alerts = await self.db.get_active_alerts()
            
            if not alerts:
                logger.debug("No active alerts to monitor")
                return
            
            # Get unique tokens from all alerts
            tokens_needed = set()
            for alert in alerts:
                tokens_needed.update(alert.condition.tokens)
            
            # Fetch current prices
            await self._update_price_cache(list(tokens_needed))
            
            # Check each alert
            alerts_triggered = 0
            for alert in alerts:
                try:
                    if await self._evaluate_alert(alert):
                        await self._trigger_alert(alert)
                        alerts_triggered += 1
                        
                    self.stats["alerts_checked"] += 1
                    
                except Exception as e:
                    logger.error(f"Error evaluating alert {alert.id[:8]}: {e}")
                    self.stats["errors"] += 1
            
            # Update stats
            cycle_duration = (datetime.now() - cycle_start).total_seconds()
            self.stats["last_run"] = cycle_start.isoformat()
            self.stats["alerts_triggered"] += alerts_triggered
            
            logger.info(f"✅ Monitoring cycle: {len(alerts)} alerts checked, {alerts_triggered} triggered ({cycle_duration:.2f}s)")
            
        except Exception as e:
            logger.error(f"Monitoring cycle failed: {e}")
            self.stats["errors"] += 1
    
    async def _update_price_cache(self, tokens: List[str]):
        """Update price cache for required tokens"""
        try:
            # Use multiple prices endpoint for efficiency
            prices = await self.redstone.get_multiple_prices(tokens)
            
            for symbol, data in prices.items():
                if not data.get("error") and data.get("price", 0) > 0:
                    self.price_cache[symbol] = {
                        "price": data["price"],
                        "timestamp": data.get("timestamp", datetime.now().timestamp() * 1000),
                        "updated_at": datetime.now()
                    }
            
            self.last_price_fetch = datetime.now()
            logger.debug(f"Updated prices for {len(prices)} tokens")
            
        except Exception as e:
            logger.error(f"Error updating price cache: {e}")
            raise
    
    async def _evaluate_alert(self, alert: Alert) -> bool:
        """Evaluate if an alert condition is met"""
        condition = alert.condition
        
        try:
            if condition.condition_type == "price_above":
                return await self._check_price_above(alert)
            elif condition.condition_type == "price_below":
                return await self._check_price_below(alert)
            elif condition.condition_type == "price_change":
                return await self._check_price_change(alert)
            elif condition.condition_type == "relative_change":
                return await self._check_relative_change(alert)
            else:
                logger.warning(f"Unknown condition type: {condition.condition_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error evaluating alert condition: {e}")
            return False
    
    async def _check_price_above(self, alert: Alert) -> bool:
        """Check if token price is above threshold"""
        condition = alert.condition
        
        for token in condition.tokens:
            if token not in self.price_cache:
                logger.warning(f"No price data for {token}")
                continue
                
            current_price = self.price_cache[token]["price"]
            
            if current_price >= condition.threshold:
                logger.info(f"🔔 Price alert triggered: {token} ${current_price:,.2f} >= ${condition.threshold:,.2f}")
                return True
        
        return False
    
    async def _check_price_below(self, alert: Alert) -> bool:
        """Check if token price is below threshold"""
        condition = alert.condition
        
        for token in condition.tokens:
            if token not in self.price_cache:
                logger.warning(f"No price data for {token}")
                continue
                
            current_price = self.price_cache[token]["price"]
            
            if current_price <= condition.threshold:
                logger.info(f"🔔 Price alert triggered: {token} ${current_price:,.2f} <= ${condition.threshold:,.2f}")
                return True
        
        return False
    
    async def _check_price_change(self, alert: Alert) -> bool:
        """Check if token price change percentage threshold is met"""
        condition = alert.condition
        
        # For price change alerts, we need historical data
        # For hackathon simplicity, we'll use a basic implementation
        for token in condition.tokens:
            if token not in self.price_cache:
                continue
            
            # Get price from 24h ago (simplified - in production, use proper historical data)
            current_price = self.price_cache[token]["price"]
            
            # For demo purposes, simulate 24h price by checking against a reference
            # In production, you'd store historical prices in database
            historical_price = await self._get_historical_price(token, condition.timeframe)
            
            if historical_price:
                price_change = (current_price - historical_price) / historical_price
                
                # Check if change exceeds threshold (negative threshold for drops)
                if condition.threshold < 0 and price_change <= condition.threshold:
                    logger.info(f"🔔 Price drop alert: {token} dropped {abs(price_change)*100:.1f}%")
                    return True
                elif condition.threshold > 0 and price_change >= condition.threshold:
                    logger.info(f"🔔 Price rise alert: {token} rose {price_change*100:.1f}%")
                    return True
        
        return False
    
    async def _check_relative_change(self, alert: Alert) -> bool:
        """Check complex relative change conditions"""
        condition = alert.condition
        
        # Check primary condition (e.g., "DeFi tokens drop 15%")
        primary_triggered = False
        
        for token in condition.tokens:
            if token not in self.price_cache:
                continue
                
            # Simplified implementation for hackathon
            current_price = self.price_cache[token]["price"]
            historical_price = await self._get_historical_price(token, condition.timeframe)
            
            if historical_price:
                price_change = (current_price - historical_price) / historical_price
                
                if price_change <= condition.threshold:  # Usually negative for drops
                    primary_triggered = True
                    break
        
        if not primary_triggered:
            return False
        
        # Check secondary condition (e.g., "while BTC stays stable")
        if condition.secondary_condition:
            secondary_token = condition.secondary_condition.get("token", "BTC")
            stability_threshold = condition.secondary_condition.get("threshold", 0.03)
            
            if secondary_token in self.price_cache:
                current_price = self.price_cache[secondary_token]["price"]
                historical_price = await self._get_historical_price(secondary_token, condition.timeframe)
                
                if historical_price:
                    price_change = abs((current_price - historical_price) / historical_price)
                    
                    if price_change <= stability_threshold:  # BTC stayed stable
                        logger.info(f"🔔 Complex alert triggered: DeFi drop while {secondary_token} stable")
                        return True
        
        return False
    
    async def _get_historical_price(self, token: str, timeframe: str) -> Optional[float]:
        """Get historical price for comparison (simplified for hackathon)"""
        # In production, this would query your database for historical prices
        # For hackathon demo, we'll simulate with some basic logic
        
        if token not in self.price_cache:
            return None
        
        current_price = self.price_cache[token]["price"]
        
        # Simulate some price volatility for demo purposes
        # In reality, you'd have actual historical data
        import random
        volatility = random.uniform(0.95, 1.05)  # ±5% random historical price
        simulated_historical = current_price * volatility
        
        return simulated_historical
    
    async def _trigger_alert(self, alert: Alert):
        """Trigger an alert - send notifications and update status"""
        try:
            # Prepare alert data
            alert_data = {
                "alert_id": alert.id,
                "user_id": alert.user_id,
                "user_email":alert.user_email,
                "message": alert.message,
                "condition": {
                    "type": alert.condition.condition_type,
                    "tokens": alert.condition.tokens,
                    "threshold": alert.condition.threshold
                },
                "triggered_at": datetime.now().isoformat(),
                "prices": {}
            }
            
            # Add current prices to alert data
            for token in alert.condition.tokens:
                if token in self.price_cache:
                    alert_data["prices"][token] = {
                        "current_price": self.price_cache[token]["price"],
                        "formatted": f"${self.price_cache[token]['price']:,.2f}"
                    }
            
            # Send notification
            await self.notifications.send_alert_notification(alert_data)
            
            # Update alert status in database
            await self.db.update_alert_status(alert.id, "triggered")
            
            # Log the alert trigger for audit
            await self.db.log_alert_trigger(alert.id, alert_data["prices"])
            
            logger.info(f"🔔 Alert {alert.id[:8]} triggered for user {alert.user_id}")
            
        except Exception as e:
            logger.error(f"Error triggering alert {alert.id[:8]}: {e}")
            raise
    
    async def get_monitoring_stats(self) -> Dict:
        """Get current monitoring statistics"""
        return {
            "running": self.running,
            "monitoring_interval": self.monitoring_interval,
            "stats": self.stats.copy(),
            "price_cache_size": len(self.price_cache),
            "last_price_fetch": self.last_price_fetch.isoformat() if self.last_price_fetch else None,
            "cached_tokens": list(self.price_cache.keys())
        }
    
    async def force_check_alert(self, alert_id: str) -> Dict:
        """Force check a specific alert (for testing)"""
        try:
            # Get the alert
            alerts = await self.db.get_active_alerts()
            target_alert = None
            
            for alert in alerts:
                if alert.id == alert_id:
                    target_alert = alert
                    break
            
            if not target_alert:
                return {"error": "Alert not found or not active"}
            
            # Update prices for this alert's tokens
            await self._update_price_cache(target_alert.condition.tokens)
            
            # Evaluate the alert
            triggered = await self._evaluate_alert(target_alert)
            
            result = {
                "alert_id": alert_id,
                "evaluated": True,
                "triggered": triggered,
                "current_prices": {}
            }
            
            # Add current prices
            for token in target_alert.condition.tokens:
                if token in self.price_cache:
                    result["current_prices"][token] = self.price_cache[token]["price"]
            
            if triggered:
                await self._trigger_alert(target_alert)
                result["notification_sent"] = True
            
            return result
            
        except Exception as e:
            logger.error(f"Error force checking alert: {e}")
            return {"error": str(e)}

# Global alert engine instance
alert_engine = AlertEngine()