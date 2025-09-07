# database.py - Updated with user email storage
import sqlite3
import aiosqlite
import asyncio
import json
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid

@dataclass
class AlertCondition:
    tokens: List[str]
    condition_type: str  # "price_above", "price_below", "price_change", "relative_change"
    threshold: float
    timeframe: str = "24h"
    secondary_condition: Optional[Dict] = None  # For complex conditions like "while BTC stays stable"

@dataclass
class Alert:
    id: str
    user_id: str
    user_email : str
    condition: AlertCondition
    status: str = "active"  # active, paused, triggered, expired
    created_at: datetime = None
    triggered_at: Optional[datetime] = None
    message: str = ""  # Human readable description
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class User:
    user_id: str
    email: Optional[str] = None
    created_at: datetime = None
    email_notifications: bool = True
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class Database:
    def __init__(self, db_path: str = "tokenTalk.db"):
        self.db_path = db_path
    
    async def init_database(self):
        """Initialize SQLite database with required tables"""
        async with aiosqlite.connect(self.db_path) as db:
            # Users table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    email TEXT,
                    email_notifications BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Alerts table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    user_email TEXT,
                    condition_json TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    triggered_at TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(user_id)
                )
            """)
            
            # Create indexes separately for alerts table
            await db.execute("CREATE INDEX IF NOT EXISTS idx_alerts_user_id ON alerts(user_id)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status)")
            
            # Price history table (for analytics later)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    price REAL NOT NULL,
                    timestamp INTEGER NOT NULL,
                    source TEXT DEFAULT 'redstone'
                )
            """)
            
            # Create indexes for price history
            await db.execute("CREATE INDEX IF NOT EXISTS idx_price_symbol_timestamp ON price_history(symbol, timestamp)")
            
            # Alert triggers table (for tracking when alerts fire)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS alert_triggers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_id TEXT NOT NULL,
                    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    price_data TEXT,
                    FOREIGN KEY(alert_id) REFERENCES alerts(id)
                )
            """)
            
            await db.commit()
            print("✅ Database initialized successfully")
    
    async def get_or_create_user(self, user_id: str, email: str = None) -> User:
        """Get existing user or create new one"""
        async with aiosqlite.connect(self.db_path) as db:
            # Try to get existing user
            async with db.execute(
                "SELECT user_id, email, email_notifications, created_at FROM users WHERE user_id = ?",
                (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                
                if row:
                    return User(
                        user_id=row[0],
                        email=row[1],
                        email_notifications=bool(row[2]),
                        created_at=datetime.fromisoformat(row[3]) if row[3] else datetime.now()
                    )
            
            # Create new user
            await db.execute(
                "INSERT INTO users (user_id, email) VALUES (?, ?)",
                (user_id, email)
            )
            await db.commit()
            
            return User(user_id=user_id, email=email)
    
    async def update_user_email(self, user_id: str, email: str) -> bool:
        """Update user's email address"""
        async with aiosqlite.connect(self.db_path) as db:
            # Create user if doesn't exist
            await self.get_or_create_user(user_id, email)
            
            # Update email
            cursor = await db.execute(
                "UPDATE users SET email = ? WHERE user_id = ?",
                (email, user_id)
            )
            await db.commit()
            return cursor.rowcount > 0
    
    async def get_user_email(self, user_id: str) -> Optional[str]:
        """Get user's email address"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT email FROM users WHERE user_id = ?",
                (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None
    
    async def create_alert(self, user_id: str, user_email:str,condition: AlertCondition, message: str = "") -> str:
        """Create a new alert"""
        alert_id = str(uuid.uuid4())
        condition_json = json.dumps(asdict(condition))
        
        async with aiosqlite.connect(self.db_path) as db:
            # Ensure user exists
            await self.get_or_create_user(user_id)
            
            # Create alert
            await db.execute("""
                INSERT INTO alerts (id, user_id, user_email,condition_json, message)
                VALUES (?, ?, ?, ?, ?)
            """, (alert_id, user_id, user_email ,condition_json, message))
            await db.commit()
            
        print(f"✅ Created alert {alert_id[:8]} for user {user_id}")
        return alert_id
    

    async def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""
        async with aiosqlite.connect(self.db_path) as db:
            # ✅ UPDATED QUERY - Added JOIN to get email
            async with db.execute("""
                SELECT a.id, a.user_id, a.condition_json, a.status, a.message, a.created_at, a.triggered_at, u.email
                FROM alerts a
                LEFT JOIN users u ON a.user_id = u.user_id
                WHERE a.status = 'active'
                ORDER BY a.created_at DESC
            """) as cursor:
                alerts = []
                async for row in cursor:
                    condition_dict = json.loads(row[2])
                    condition = AlertCondition(**condition_dict)
                    
                    alert = Alert(
                        id=row[0],
                        user_id=row[1],
                        user_email=row[7] or "",  # ✅ Now row[7] exists (u.email)
                        condition=condition,
                        status=row[3],
                        message=row[4],
                        created_at=datetime.fromisoformat(row[5]) if row[5] else datetime.now(),
                        triggered_at=datetime.fromisoformat(row[6]) if row[6] else None
                    )
                    alerts.append(alert)
                
                return alerts
    
    async def get_user_alerts(self, user_id: str) -> List[Alert]:
        """Get all alerts for a specific user"""
        async with aiosqlite.connect(self.db_path) as db:
            # ✅ UPDATED QUERY - Added JOIN to get email
            async with db.execute("""
                SELECT a.id, a.user_id, a.condition_json, a.status, a.message, a.created_at, a.triggered_at, u.email
                FROM alerts a
                LEFT JOIN users u ON a.user_id = u.user_id
                WHERE a.user_id = ?
                ORDER BY a.created_at DESC
            """, (user_id,)) as cursor:
                alerts = []
                async for row in cursor:
                    condition_dict = json.loads(row[2])
                    condition = AlertCondition(**condition_dict)
                    
                    alert = Alert(
                        id=row[0],
                        user_id=row[1],
                        user_email=row[7] or "",  # ✅ Now row[7] exists (u.email)
                        condition=condition,
                        status=row[3],
                        message=row[4],
                        created_at=datetime.fromisoformat(row[5]) if row[5] else datetime.now(),
                        triggered_at=datetime.fromisoformat(row[6]) if row[6] else None
                    )
                    alerts.append(alert)
            
            return alerts
    
    async def update_alert_status(self, alert_id: str, status: str):
        """Update alert status (active, paused, triggered, expired)"""
        async with aiosqlite.connect(self.db_path) as db:
            if status == "triggered":
                await db.execute("""
                    UPDATE alerts 
                    SET status = ?, triggered_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (status, alert_id))
            else:
                await db.execute("""
                    UPDATE alerts 
                    SET status = ?
                    WHERE id = ?
                """, (status, alert_id))
            await db.commit()
    
    async def delete_alert(self, alert_id: str, user_id: str) -> bool:
        """Delete an alert (only if user owns it)"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                DELETE FROM alerts 
                WHERE id = ? AND user_id = ?
            """, (alert_id, user_id))
            await db.commit()
            return cursor.rowcount > 0
    
    async def log_price_data(self, symbol: str, price: float, timestamp: int):
        """Log price data for analytics"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO price_history (symbol, price, timestamp)
                VALUES (?, ?, ?)
            """, (symbol, price, timestamp))
            await db.commit()
    
    async def log_alert_trigger(self, alert_id: str, price_data: Dict):
        """Log when an alert triggers"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO alert_triggers (alert_id, price_data)
                VALUES (?, ?)
            """, (alert_id, json.dumps(price_data)))
            await db.commit()

# Database instance
db = Database()

def get_database():
    return db