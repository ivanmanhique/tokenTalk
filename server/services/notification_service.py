# services/notification_service.py - Updated with Resend email support
import asyncio
import logging
from typing import Dict, List
from datetime import datetime
import json

from config import settings

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.notifications = []  # In-memory store for demo
        self.user_connections = {}  # Store WebSocket connections by user_id
        self.email_stats = {
            "sent": 0,
            "failed": 0,
            "last_sent": None
        }
        
    async def send_alert_notification(self, alert_data: Dict):
        """Send alert notification via multiple channels"""
        try:
            # Format the notification message
            notification = self._format_alert_notification(alert_data)
            
            # Store notification (in production, you'd use a proper queue)
            self.notifications.append({
                "id": len(self.notifications) + 1,
                "alert_id": alert_data["alert_id"],
                "user_id": alert_data["user_id"], 
                "user_email": alert_data["user_email"],
                "message": notification["message"],
                "type": "alert_triggered",
                "timestamp": datetime.now().isoformat(),
                "data": alert_data
            })
            
            # Send via WebSocket (real-time) to specific user
            await self._send_to_user_websockets(alert_data["user_id"], notification)
            
            # Send via Email (Resend)
            await self._send_email_notification(alert_data, notification)
            
            # Console notification (for development)
            await self._send_console_notification(notification)
            
            logger.info(f"📨 Notification sent for alert {alert_data['alert_id'][:8]}")
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            raise
    
    def _format_alert_notification(self, alert_data: Dict) -> Dict:
        """Format alert data into a user-friendly notification"""
        condition = alert_data["condition"]
        prices = alert_data["prices"]
        
        # Build price message
        price_messages = []
        for token, price_data in prices.items():
            price_messages.append(f"{token}: {price_data['formatted']}")
        
        price_text = ", ".join(price_messages)
        
        # Format based on condition type
        if condition["type"] == "price_above":
            title = f"🔥 Price Alert: {', '.join(condition['tokens'])} Above Target!"
            message = f"{', '.join(condition['tokens'])} has reached ${condition['threshold']:,.2f}!\n\nCurrent prices: {price_text}"
            
        elif condition["type"] == "price_below":
            title = f"📉 Price Alert: {', '.join(condition['tokens'])} Below Target!"
            message = f"{', '.join(condition['tokens'])} has dropped to ${condition['threshold']:,.2f}!\n\nCurrent prices: {price_text}"
            
        elif condition["type"] == "price_change":
            percentage = abs(condition['threshold'] * 100)
            direction = "dropped" if condition['threshold'] < 0 else "increased"
            title = f"📊 Price Change Alert: {', '.join(condition['tokens'])} {direction.title()}!"
            message = f"{', '.join(condition['tokens'])} has {direction} by {percentage}%!\n\nCurrent prices: {price_text}"
            
        elif condition["type"] == "relative_change":
            title = f"🎯 Complex Alert Triggered!"
            message = f"Your complex alert condition has been met!\n\nCurrent prices: {price_text}"
            
        else:
            title = f"🚨 Alert Triggered!"
            message = f"Alert condition met for {', '.join(condition['tokens'])}\n\nCurrent prices: {price_text}"
        
        return {
            "title": title,
            "message": message,
            "type": "alert",
            "priority": "high",
            "action_url": f"/alerts/{alert_data['alert_id']}"
        }
    
    async def _send_email_notification(self, alert_data: Dict, notification: Dict):
        """Send email notification via Resend"""
        if not settings.ENABLE_EMAIL_NOTIFICATIONS or not settings.has_resend_key():
            logger.debug("Email notifications disabled or no Resend key")
            return
        
        try:
            # Get user email from database
            from database import db
            user_email = await db.get_user_email(alert_data["user_email"])
            
            if not user_email:
                logger.debug(f"No email address for user {alert_data['user_email']}")
                return
            
            # Import Resend
            import resend
            resend.api_key = settings.RESEND_API_KEY
            
            # Create HTML email content
            html_content = self._create_email_html(notification, alert_data)
            
            # Send email
            params = {
                "from": settings.FROM_EMAIL,
                "to": [user_email],
                "subject": notification["title"],
                "html": html_content,
                "text": notification["message"]  # Fallback text version
            }
            
            # Send the email
            response = resend.Emails.send(params)
            
            # Update stats
            self.email_stats["sent"] += 1
            self.email_stats["last_sent"] = datetime.now().isoformat()
            
            logger.info(f"📧 Email sent to {user_email} via Resend (ID: {response.get('id', 'unknown')})")
            
        except ImportError:
            logger.error("Resend package not installed. Run: pip install resend")
            self.email_stats["failed"] += 1
        except Exception as e:
            logger.error(f"Failed to send email via Resend: {e}")
            self.email_stats["failed"] += 1
    
    def _create_email_html(self, notification: Dict, alert_data: Dict) -> str:
        """Create HTML email content"""
        prices_html = ""
        for token, price_data in alert_data.get("prices", {}).items():
            prices_html += f"<li><strong>{token}:</strong> {price_data['formatted']}</li>"
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>tokenTalk Alert</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; text-align: center; }}
                .content {{ padding: 20px; }}
                .prices {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                .footer {{ text-align: center; color: #666; font-size: 12px; padding-top: 20px; border-top: 1px solid #eee; }}
                .btn {{ display: inline-block; background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🪨 tokenTalk</h1>
                    <h2>{notification["title"]}</h2>
                </div>
                <div class="content">
                    <p>Your crypto price alert has been triggered!</p>
                    <p><strong>Alert Message:</strong> {alert_data.get("message", "Price alert triggered")}</p>
                    
                    <div class="prices">
                        <h3>💰 Current Prices:</h3>
                        <ul>
                            {prices_html}
                        </ul>
                    </div>
                    
                    <p><strong>Triggered at:</strong> {alert_data.get("triggered_at", datetime.now().isoformat())}</p>
                    
                    <p>Stay on top of your crypto investments with tokenTalk!</p>
                </div>
                <div class="footer">
                    <p>This alert was sent by tokenTalk - AI-powered crypto price alerts</p>
                    <p>Powered by RedStone oracles and delivered via Resend</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    async def _send_to_user_websockets(self, user_id: str, notification: Dict):
        """Send notification to specific user's WebSocket connections"""
        user_websockets = self.user_connections.get(user_id, [])
        
        if not user_websockets:
            logger.debug(f"No WebSocket connections for user {user_id}")
            return
            
        # Remove closed connections and send to active ones
        active_connections = []
        for websocket in user_websockets:
            try:
                await websocket.send_text(json.dumps({
                    "type": "alert_notification",
                    "data": notification
                }))
                active_connections.append(websocket)
            except:
                # Connection closed, don't re-add to active list
                pass
        
        self.user_connections[user_id] = active_connections
        logger.debug(f"Sent notification to {len(active_connections)} connections for user {user_id}")
    
    async def _send_console_notification(self, notification: Dict):
        """Send notification to console (for development)"""
        print(f"\n{'='*60}")
        print(f"🚨 ALERT TRIGGERED!")
        print(f"{'='*60}")
        print(f"Title: {notification['title']}")
        print(f"Message: {notification['message']}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
    
    def add_websocket_connection(self, websocket, user_id: str = "anonymous"):
        """Add a WebSocket connection for a specific user"""
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        
        self.user_connections[user_id].append(websocket)
        logger.info(f"Added WebSocket for user {user_id}. Total connections: {sum(len(conns) for conns in self.user_connections.values())}")
    
    def remove_websocket_connection(self, websocket, user_id: str = None):
        """Remove a WebSocket connection"""
        if user_id and user_id in self.user_connections:
            if websocket in self.user_connections[user_id]:
                self.user_connections[user_id].remove(websocket)
                if not self.user_connections[user_id]:  # Remove empty user entry
                    del self.user_connections[user_id]
        else:
            # Remove from all users if user_id not specified
            for uid, connections in list(self.user_connections.items()):
                if websocket in connections:
                    connections.remove(websocket)
                    if not connections:
                        del self.user_connections[uid]
                    break
        
        total_connections = sum(len(conns) for conns in self.user_connections.values())
        logger.info(f"Removed WebSocket connection. Total connections: {total_connections}")
    
    async def get_recent_notifications(self, user_id: str = None, limit: int = 10) -> List[Dict]:
        """Get recent notifications for a user or all users"""
        if user_id:
            user_notifications = [
                notif for notif in self.notifications 
                if notif["user_id"] == user_id
            ]
            return user_notifications[-limit:]
        
        return self.notifications[-limit:]
    
    async def get_service_status(self) -> Dict:
        """Get notification service status"""
        total_connections = sum(len(conns) for conns in self.user_connections.values())
        
        return {
            "service": "Notification Service",
            "total_websocket_connections": total_connections,
            "active_users": len(self.user_connections),
            "total_notifications": len(self.notifications),
            "user_connections": {uid: len(conns) for uid, conns in self.user_connections.items()},
            "email_stats": self.email_stats,
            "capabilities": {
                "websocket": True,
                "console": True,
                "email": settings.has_resend_key(),
                "resend_configured": settings.has_resend_key(),
                "push": False,   
                "sms": False     
            }
        }

# Global notification service instance
notification_service = NotificationService()