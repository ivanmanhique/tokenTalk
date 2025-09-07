# services/enhanced_notification_service.py - GolemDB-powered notifications
import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

from config import settings
from services.golemdb_service import TokenTalkGolemService

logger = logging.getLogger(__name__)

class EnhancedNotificationService:
    """Notification service enhanced with GolemDB insights"""
    
    def __init__(self, golem_service: Optional[TokenTalkGolemService] = None):
        self.golem_service = golem_service
        self.notifications = []
        self.user_connections = {}
        self.email_stats = {"sent": 0, "failed": 0, "last_sent": None}
        
        # Enhanced features
        self.user_insights = {}
        self.notification_preferences = {}
    
    async def send_alert_notification(self, alert_data: Dict):
        """Enhanced alert notification with GolemDB insights"""
        try:
            user_id = alert_data["user_id"]
            
            # Get user insights from GolemDB
            insights = await self._get_user_insights(user_id)
            
            # Personalize notification based on insights
            notification = await self._create_personalized_notification(alert_data, insights)
            
            # Store notification with enhanced data
            enhanced_notification = {
                "id": len(self.notifications) + 1,
                "alert_id": alert_data["alert_id"],
                "user_id": user_id,
                "user_email": alert_data["user_email"],
                "message": notification["message"],
                "type": "alert_triggered",
                "timestamp": datetime.now().isoformat(),
                "data": alert_data,
                "insights": insights,
                "personalization": notification.get("personalization", {})
            }
            
            self.notifications.append(enhanced_notification)
            
            # Send via multiple channels
            await self._send_to_user_websockets(user_id, notification)
            await self._send_enhanced_email(alert_data, notification, insights)
            await self._send_console_notification(notification)
            
            # Log to GolemDB for cross-platform sync
            if self.golem_service:
                await self._log_notification_to_golemdb(enhanced_notification)
            
            logger.info(f"📨 Enhanced notification sent for alert {alert_data['alert_id'][:8]}")
            
        except Exception as e:
            logger.error(f"Error sending enhanced notification: {e}")
            raise
    
    async def _get_user_insights(self, user_id: str) -> Dict:
        """Get user insights from GolemDB"""
        if not self.golem_service:
            return {"source": "none"}
        
        try:
            # Get user analytics from GolemDB
            analytics = await self.golem_service.get_user_analytics(user_id)
            
            insights = {
                "source": "golemdb",
                "total_alerts": len([a for a in analytics if a.get("type") == "alert_config"]),
                "total_triggers": len([a for a in analytics if a.get("event_type") == "alert_triggered"]),
                "favorite_tokens": self._extract_favorite_tokens(analytics),
                "alert_frequency": self._calculate_alert_frequency(analytics),
                "success_rate": self._calculate_success_rate(analytics),
                "last_activity": self._get_last_activity(analytics)
            }
            
            # Cache insights for performance
            self.user_insights[user_id] = {
                "data": insights,
                "cached_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(minutes=30)
            }
            
            return insights
            
        except Exception as e:
            logger.debug(f"Error getting user insights: {e}")
            return {"source": "error", "error": str(e)}
    
    def _extract_favorite_tokens(self, analytics: List[Dict]) -> List[str]:
        """Extract user's favorite tokens from their history"""
        token_counts = {}
        
        for event in analytics:
            if event.get("type") == "alert_config":
                condition = event.get("condition", {})
                tokens = condition.get("tokens", [])
                for token in tokens:
                    token_counts[token] = token_counts.get(token, 0) + 1
        
        # Return top 3 most watched tokens
        sorted_tokens = sorted(token_counts.items(), key=lambda x: x[1], reverse=True)
        return [token for token, count in sorted_tokens[:3]]
    
    def _calculate_alert_frequency(self, analytics: List[Dict]) -> str:
        """Calculate how often user creates alerts"""
        alert_configs = [a for a in analytics if a.get("type") == "alert_config"]
        
        if len(alert_configs) < 2:
            return "new_user"
        
        # Calculate average days between alerts
        dates = []
        for config in alert_configs:
            try:
                created_at = datetime.fromisoformat(config.get("created_at", ""))
                dates.append(created_at)
            except:
                continue
        
        if len(dates) < 2:
            return "unknown"
        
        dates.sort()
        avg_days = sum(
            (dates[i] - dates[i-1]).days for i in range(1, len(dates))
        ) / (len(dates) - 1)
        
        if avg_days < 1:
            return "very_active"
        elif avg_days < 7:
            return "active"
        elif avg_days < 30:
            return "regular"
        else:
            return "occasional"
    
    def _calculate_success_rate(self, analytics: List[Dict]) -> float:
        """Calculate alert success rate (triggered vs created)"""
        alerts_created = len([a for a in analytics if a.get("type") == "alert_config"])
        alerts_triggered = len([a for a in analytics if a.get("event_type") == "alert_triggered"])
        
        if alerts_created == 0:
            return 0.0
        
        return min(alerts_triggered / alerts_created, 1.0)  # Cap at 100%
    
    def _get_last_activity(self, analytics: List[Dict]) -> Optional[str]:
        """Get user's last activity timestamp"""
        if not analytics:
            return None
        
        latest_event = max(
            analytics,
            key=lambda x: x.get("created_at", x.get("timestamp", "1970-01-01")),
            default=None
        )
        
        return latest_event.get("created_at", latest_event.get("timestamp")) if latest_event else None
    
    async def _create_personalized_notification(self, alert_data: Dict, insights: Dict) -> Dict:
        """Create personalized notification based on user insights"""
        condition = alert_data["condition"]
        prices = alert_data["prices"]
        
        # Base notification
        notification = self._format_basic_alert_notification(alert_data)
        
        # Add personalization based on insights
        personalization = {}
        
        # Frequency-based personalization
        frequency = insights.get("alert_frequency", "unknown")
        if frequency == "very_active":
            personalization["tone"] = "concise"
            notification["title"] = f"🚀 {notification['title']}"
        elif frequency == "new_user":
            personalization["tone"] = "helpful"
            notification["message"] += "\n\n💡 Tip: You can create more alerts by chatting with tokenTalk!"
        elif frequency == "occasional":
            personalization["tone"] = "encouraging"
            notification["message"] += f"\n\n👋 Welcome back! This is your latest alert."
        
        # Token-based personalization
        favorite_tokens = insights.get("favorite_tokens", [])
        current_tokens = condition.get("tokens", [])
        
        if any(token in favorite_tokens for token in current_tokens):
            personalization["token_preference"] = "favorite"
            notification["title"] = notification["title"].replace("🔥", "⭐")
        
        # Success rate personalization
        success_rate = insights.get("success_rate", 0)
        if success_rate > 0.8:
            personalization["user_type"] = "expert"
            notification["message"] += f"\n\n🎯 Great timing! Your alerts have a {success_rate*100:.0f}% success rate."
        elif success_rate < 0.2 and insights.get("total_alerts", 0) > 3:
            personalization["user_type"] = "learning"
            notification["message"] += "\n\n📈 Consider adjusting your thresholds for better results."
        
        # Add current portfolio context if available
        if len(favorite_tokens) > 0:
            portfolio_context = f"\n\n📊 Your watched tokens: {', '.join(favorite_tokens)}"
            notification["message"] += portfolio_context
        
        notification["personalization"] = personalization
        return notification
    
    def _format_basic_alert_notification(self, alert_data: Dict) -> Dict:
        """Basic alert formatting (from your existing code)"""
        condition = alert_data["condition"]
        prices = alert_data["prices"]
        
        price_messages = []
        for token, price_data in prices.items():
            price_messages.append(f"{token}: {price_data['formatted']}")
        price_text = ", ".join(price_messages)
        
        if condition["type"] == "price_above":
            title = f"🔥 Price Alert: {', '.join(condition['tokens'])} Above Target!"
            message = f"{', '.join(condition['tokens'])} has reached ${condition['threshold']:,.2f}!\n\nCurrent prices: {price_text}"
        elif condition["type"] == "price_below":
            title = f"📉 Price Alert: {', '.join(condition['tokens'])} Below Target!"
            message = f"{', '.join(condition['tokens'])} has dropped to ${condition['threshold']:,.2f}!\n\nCurrent prices: {price_text}"
        else:
            title = f"🚨 Alert Triggered!"
            message = f"Alert condition met for {', '.join(condition['tokens'])}\n\nCurrent prices: {price_text}"
        
        return {"title": title, "message": message, "type": "alert", "priority": "high"}
    
    async def _send_enhanced_email(self, alert_data: Dict, notification: Dict, insights: Dict):
        """Send enhanced email with GolemDB insights"""
        if not settings.ENABLE_EMAIL_NOTIFICATIONS or not settings.has_resend_key():
            return
        
        try:
            from database import db
            # user_email = await db.get_user_email(alert_data["user_email"])
            logger.info("user data :{", alert_data,"}")
            user_email = await db.get_user_email(alert_data["user_id"])
            logger.info("the email is being sent to: ", user_email)
            if not user_email:
                return
            
            import resend
            resend.api_key = settings.RESEND_API_KEY
            
            # Create enhanced HTML email
            html_content = self._create_enhanced_email_html(notification, alert_data, insights)
            
            params = {
                "from": settings.FROM_EMAIL,
                "to": [user_email],
                "subject": notification["title"],
                "html": html_content,
                "text": notification["message"]
            }
            
            response = resend.Emails.send(params)
            
            self.email_stats["sent"] += 1
            self.email_stats["last_sent"] = datetime.now().isoformat()
            
            logger.info(f"📧 Enhanced email sent to {user_email}")
            
        except Exception as e:
            logger.error(f"Failed to send enhanced email: {e}")
            self.email_stats["failed"] += 1
    
    def _create_enhanced_email_html(self, notification: Dict, alert_data: Dict, insights: Dict) -> str:
        """Create enhanced HTML email with insights"""
        prices_html = ""
        for token, price_data in alert_data.get("prices", {}).items():
            prices_html += f"<li><strong>{token}:</strong> {price_data['formatted']}</li>"
        
        # Add insights section
        insights_html = ""
        if insights.get("source") == "golemdb":
            favorite_tokens = insights.get("favorite_tokens", [])
            success_rate = insights.get("success_rate", 0)
            total_alerts = insights.get("total_alerts", 0)
            
            insights_html = f"""
            <div class="insights" style="background-color: #f0f8ff; padding: 15px; border-radius: 5px; margin: 15px 0;">
                <h3 style="color: #2c3e50;">📊 Your tokenTalk Insights</h3>
                <ul style="margin: 10px 0;">
                    <li><strong>Total Alerts Created:</strong> {total_alerts}</li>
                    <li><strong>Success Rate:</strong> {success_rate*100:.0f}%</li>
                    {f'<li><strong>Favorite Tokens:</strong> {", ".join(favorite_tokens)}</li>' if favorite_tokens else ''}
                </ul>
                <p style="font-size: 12px; color: #666;">
                    💎 Your data is stored securely on GolemDB blockchain for cross-platform access.
                </p>
            </div>
            """
        
        # Personalization badge
        personalization = notification.get("personalization", {})
        user_type = personalization.get("user_type", "")
        badge_html = ""
        
        if user_type == "expert":
            badge_html = '<span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 3px; font-size: 12px;">🎯 Expert Trader</span>'
        elif user_type == "learning":
            badge_html = '<span style="background: #ffc107; color: black; padding: 3px 8px; border-radius: 3px; font-size: 12px;">📈 Learning Mode</span>'
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>tokenTalk Alert</title>
        </head>
        <body style="font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; text-align: center;">
                    <h1>🪨 tokenTalk</h1>
                    <h2>{notification["title"]}</h2>
                    {badge_html}
                </div>
                <div style="padding: 20px;">
                    <p>Your personalized crypto price alert has been triggered!</p>
                    <p><strong>Alert Message:</strong> {alert_data.get("message", "Price alert triggered")}</p>
                    
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
                        <h3>💰 Current Prices:</h3>
                        <ul>{prices_html}</ul>
                    </div>
                    
                    {insights_html}
                    
                    <p><strong>Triggered at:</strong> {alert_data.get("triggered_at", datetime.now().isoformat())}</p>
                    <p>Stay ahead of the market with tokenTalk's AI-powered alerts! 🚀</p>
                </div>
                <div style="text-align: center; color: #666; font-size: 12px; padding-top: 20px; border-top: 1px solid #eee;">
                    <p>This alert was sent by tokenTalk - AI-powered crypto alerts with blockchain-secured insights</p>
                    <p>Powered by RedStone oracles • GolemDB blockchain • Delivered via Resend</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    async def _log_notification_to_golemdb(self, notification: Dict):
        """Log notification to GolemDB for cross-platform sync"""
        if not self.golem_service:
            return
        
        try:
            # Store notification event
            await self.golem_service.log_event(
                event_type="notification_sent",
                event_data={
                    "notification_id": notification["id"],
                    "user_id": notification["user_id"],
                    "alert_id": notification["alert_id"],
                    "type": notification["type"],
                    "personalization": notification.get("personalization", {}),
                    "channels": ["websocket", "email", "console"]
                },
                user_id=notification["user_id"]
            )
            
            logger.debug(f"📝 Notification logged to GolemDB: {notification['id']}")
            
        except Exception as e:
            logger.debug(f"Failed to log notification to GolemDB: {e}")
    
    async def _send_to_user_websockets(self, user_id: str, notification: Dict):
        """Send to WebSocket connections (from your existing code)"""
        user_websockets = self.user_connections.get(user_id, [])
        
        if not user_websockets:
            return
            
        active_connections = []
        for websocket in user_websockets:
            try:
                await websocket.send_text(json.dumps({
                    "type": "enhanced_alert_notification",
                    "data": notification
                }))
                active_connections.append(websocket)
            except:
                pass
        
        self.user_connections[user_id] = active_connections
    
    async def _send_console_notification(self, notification: Dict):
        """Enhanced console notification"""
        personalization = notification.get("personalization", {})
        user_type = personalization.get("user_type", "")
        
        print(f"\n{'='*60}")
        print(f"🚨 ENHANCED ALERT TRIGGERED! {f'({user_type})' if user_type else ''}")
        print(f"{'='*60}")
        print(f"Title: {notification['title']}")
        print(f"Message: {notification['message']}")
        if personalization:
            print(f"Personalization: {personalization}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
    
    # Keep existing methods for compatibility
    def add_websocket_connection(self, websocket, user_id: str = "anonymous"):
        """Add WebSocket connection"""
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        self.user_connections[user_id].append(websocket)
    
    def remove_websocket_connection(self, websocket, user_id: str = None):
        """Remove WebSocket connection"""
        if user_id and user_id in self.user_connections:
            if websocket in self.user_connections[user_id]:
                self.user_connections[user_id].remove(websocket)
        else:
            for uid, connections in list(self.user_connections.items()):
                if websocket in connections:
                    connections.remove(websocket)
                    break
    
    async def get_recent_notifications(self, user_id: str = None, limit: int = 10) -> List[Dict]:
        """Get recent notifications with insights"""
        if user_id:
            user_notifications = [
                notif for notif in self.notifications 
                if notif["user_id"] == user_id
            ]
            return user_notifications[-limit:]
        return self.notifications[-limit:]
    
    async def get_service_status(self) -> Dict:
        """Get enhanced service status"""
        total_connections = sum(len(conns) for conns in self.user_connections.values())
        
        return {
            "service": "Enhanced Notification Service",
            "total_websocket_connections": total_connections,
            "active_users": len(self.user_connections),
            "total_notifications": len(self.notifications),
            "email_stats": self.email_stats,
            "golemdb_integration": bool(self.golem_service),
            "cached_insights": len(self.user_insights),
            "capabilities": {
                "websocket": True,
                "console": True,
                "email": settings.has_resend_key(),
                "personalization": bool(self.golem_service),
                "insights": bool(self.golem_service),
                "cross_platform_sync": bool(self.golem_service)
            }
        }

# Create enhanced notification service instance
def create_enhanced_notification_service(golem_service: TokenTalkGolemService = None):
    """Factory function for enhanced notification service"""
    return EnhancedNotificationService(golem_service)