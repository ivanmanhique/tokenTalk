# services/golemdb_service.py - Production GolemDB Integration for tokenTalk
import asyncio
import logging
import json
import uuid
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# GolemDB imports
try:
    from golem_base_sdk import (
        GolemBaseClient, 
        GolemBaseCreate, 
        GolemBaseUpdate,
        GolemBaseDelete,
        Annotation
    )
    from dotenv import load_dotenv
    GOLEM_AVAILABLE = True
except ImportError:
    GOLEM_AVAILABLE = False

from database import AlertCondition, User, Alert

logger = logging.getLogger(__name__)
load_dotenv()

@dataclass
class GolemConfig:
    """GolemDB configuration"""
    private_key: str = os.getenv("GOLEM_PRIVATE_KEY", "")
    rpc_url: str = os.getenv("GOLEM_RPC_URL", "https://ethwarsaw.holesky.golemdb.io/rpc")
    ws_url: str = os.getenv("GOLEM_WS_URL", "wss://ethwarsaw.holesky.golemdb.io/rpc/ws")
    chain_id: int = int(os.getenv("GOLEM_CHAIN_ID", "60138453033"))
    btl_default: int = 7200  # ~4 hours default expiration
    btl_permanent: int = 525600  # ~1 year for important data

class TokenTalkGolemService:
    """Production GolemDB service for tokenTalk"""
    
    def __init__(self, config: GolemConfig = None):
        self.config = config or GolemConfig()
        self.client: Optional[GolemBaseClient] = None
        self.connected = False
        self.mock_mode = False
        
        # Local fallback storage
        self.local_entities = {}
        
        # Metrics
        self.metrics = {
            "entities_created": 0,
            "entities_updated": 0,
            "entities_queried": 0,
            "events_logged": 0,
            "errors": 0,
            "blockchain_operations": 0
        }
    
    async def initialize(self) -> bool:
        """Initialize GolemDB connection"""
        logger.info("🚀 Initializing TokenTalk GolemDB Service...")
        
        if not GOLEM_AVAILABLE:
            logger.warning("⚠️ GolemDB SDK not available, using mock mode")
            self.mock_mode = True
            return True
        
        if not self.config.private_key:
            logger.warning("⚠️ No GOLEM_PRIVATE_KEY configured, using mock mode")
            self.mock_mode = True
            return True
        
        try:
            # Convert private key
            private_key_hex = self.config.private_key.replace("0x", "")
            private_key_bytes = bytes.fromhex(private_key_hex)
            
            # Create client
            self.client = await GolemBaseClient.create_rw_client(
                rpc_url=self.config.rpc_url,
                ws_url=self.config.ws_url,
                private_key=private_key_bytes
            )
            
            # Test connection
            owner_address = self.client.get_account_address()
            balance = await self.client.http_client().eth.get_balance(owner_address)
            
            if balance == 0:
                logger.warning("⚠️ GolemDB account has 0 ETH - operations will fail")
                self.mock_mode = True
            else:
                self.connected = True
                logger.info(f"✅ GolemDB connected: {owner_address} ({balance / 10**18:.4f} ETH)")
                
                # Setup event monitoring
                await self._setup_event_monitoring()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ GolemDB initialization failed: {e}")
            self.mock_mode = True
            return True  # Still return True for graceful fallback
    
    async def _setup_event_monitoring(self):
        """Setup real-time event monitoring"""
        try:
            def on_created(entity_key):
                logger.debug(f"📝 GolemDB entity created: {entity_key}")
            
            def on_updated(entity_key):
                logger.debug(f"📝 GolemDB entity updated: {entity_key}")
            
            def on_deleted(entity_key):
                logger.debug(f"🗑️ GolemDB entity deleted: {entity_key}")
            
            await self.client.watch_logs(
                label="tokenTalk",
                create_callback=on_created,
                update_callback=on_updated,
                delete_callback=on_deleted
            )
            
            logger.info("👀 GolemDB event monitoring enabled")
            
        except Exception as e:
            logger.warning(f"Event monitoring setup failed: {e}")
    
    # User Operations
    async def create_user_profile(self, user_id: str, email: str = None, **metadata) -> str:
        """Store user profile on GolemDB"""
        try:
            profile_data = {
                "user_id": user_id,
                "email": email,
                "created_at": datetime.now().isoformat(),
                "preferences": metadata.get("preferences", {"email_notifications": True}),
                "app": "tokenTalk",
                "version": "1.0"
            }
            
            if self.mock_mode:
                entity_id = f"user_{user_id}"
                self.local_entities[entity_id] = profile_data
                logger.info(f"🔄 User profile stored in mock mode: {user_id}")
                self.metrics["entities_created"] += 1
                return entity_id
            
            # Create on GolemDB
            entity = GolemBaseCreate(
                data=json.dumps(profile_data).encode('utf-8'),
                btl=self.config.btl_permanent,  # Long-lived user data
                string_annotations=[
                    Annotation(key="type", value="user_profile"),
                    Annotation(key="app", value="tokenTalk"),
                    Annotation(key="user_id", value=user_id),
                    Annotation(key="email", value=email or ""),
                ],
                numeric_annotations=[
                    Annotation(key="created_timestamp", value=int(datetime.now().timestamp())),
                    Annotation(key="version", value=1)
                ]
            )
            
            receipts = await self.client.create_entities([entity])
            entity_key = receipts[0].entity_key
            
            self.metrics["entities_created"] += 1
            self.metrics["blockchain_operations"] += 1
            
            logger.info(f"✅ User profile created on GolemDB: {user_id}")
            return str(entity_key)
            
        except Exception as e:
            logger.error(f"Error creating user profile: {e}")
            self.metrics["errors"] += 1
            return None
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile from GolemDB"""
        try:
            if self.mock_mode:
                entity_id = f"user_{user_id}"
                profile = self.local_entities.get(entity_id)
                if profile:
                    self.metrics["entities_queried"] += 1
                return profile
            
            # Query GolemDB
            results = await self.client.query_entities(
                f'type="user_profile" && user_id="{user_id}" && app="tokenTalk"'
            )
            
            if results:
                profile_data = json.loads(results[0].storage_value.decode('utf-8'))
                self.metrics["entities_queried"] += 1
                return profile_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            self.metrics["errors"] += 1
            return None
    
    async def update_user_email(self, user_id: str, new_email: str) -> bool:
        """Update user email on GolemDB"""
        try:
            if self.mock_mode:
                entity_id = f"user_{user_id}"
                if entity_id in self.local_entities:
                    self.local_entities[entity_id]["email"] = new_email
                    self.local_entities[entity_id]["updated_at"] = datetime.now().isoformat()
                    logger.info(f"🔄 User email updated in mock mode: {user_id}")
                    return True
                return False
            
            # Find existing profile
            results = await self.client.query_entities(
                f'type="user_profile" && user_id="{user_id}" && app="tokenTalk"'
            )
            
            if not results:
                return False
            
            # Update with new email
            entity_key = results[0].entity_key
            old_data = json.loads(results[0].storage_value.decode('utf-8'))
            
            updated_data = old_data.copy()
            updated_data["email"] = new_email
            updated_data["updated_at"] = datetime.now().isoformat()
            
            update = GolemBaseUpdate(
                entity_key=entity_key,
                data=json.dumps(updated_data).encode('utf-8'),
                btl=self.config.btl_permanent,
                string_annotations=[
                    Annotation(key="type", value="user_profile"),
                    Annotation(key="app", value="tokenTalk"),
                    Annotation(key="user_id", value=user_id),
                    Annotation(key="email", value=new_email),
                ],
                numeric_annotations=[
                    Annotation(key="updated_timestamp", value=int(datetime.now().timestamp())),
                    Annotation(key="version", value=old_data.get("version", 1) + 1)
                ]
            )
            
            await self.client.update_entities([update])
            
            self.metrics["entities_updated"] += 1
            self.metrics["blockchain_operations"] += 1
            
            logger.info(f"✅ User email updated on GolemDB: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating user email: {e}")
            self.metrics["errors"] += 1
            return False
    
    # Alert Operations
    async def store_alert_config(self, alert_id: str, user_id: str, condition: AlertCondition, message: str) -> bool:
        """Store alert configuration as audit trail"""
        try:
            alert_data = {
                "alert_id": alert_id,
                "user_id": user_id,
                "condition": asdict(condition),
                "message": message,
                "created_at": datetime.now().isoformat(),
                "app": "tokenTalk",
                "type": "alert_config"
            }
            
            if self.mock_mode:
                self.local_entities[f"alert_{alert_id}"] = alert_data
                self.metrics["entities_created"] += 1
                return True
            
            entity = GolemBaseCreate(
                data=json.dumps(alert_data).encode('utf-8'),
                btl=self.config.btl_default,
                string_annotations=[
                    Annotation(key="type", value="alert_config"),
                    Annotation(key="app", value="tokenTalk"),
                    Annotation(key="alert_id", value=alert_id),
                    Annotation(key="user_id", value=user_id),
                    Annotation(key="condition_type", value=condition.condition_type),
                ],
                numeric_annotations=[
                    Annotation(key="threshold", value=int(condition.threshold * 100)),  # Store as cents
                    Annotation(key="created_timestamp", value=int(datetime.now().timestamp()))
                ]
            )
            
            await self.client.create_entities([entity])
            
            self.metrics["entities_created"] += 1
            self.metrics["blockchain_operations"] += 1
            
            return True
            
        except Exception as e:
            logger.error(f"Error storing alert config: {e}")
            self.metrics["errors"] += 1
            return False
    
    async def log_alert_trigger(self, alert_id: str, trigger_data: Dict) -> bool:
        """Log alert trigger event"""
        try:
            event_data = {
                "event_type": "alert_triggered",
                "alert_id": alert_id,
                "trigger_data": trigger_data,
                "timestamp": datetime.now().isoformat(),
                "app": "tokenTalk"
            }
            
            if self.mock_mode:
                event_id = f"trigger_{alert_id}_{int(datetime.now().timestamp())}"
                self.local_entities[event_id] = event_data
                self.metrics["events_logged"] += 1
                return True
            
            entity = GolemBaseCreate(
                data=json.dumps(event_data).encode('utf-8'),
                btl=self.config.btl_permanent,  # Keep trigger history
                string_annotations=[
                    Annotation(key="type", value="alert_trigger"),
                    Annotation(key="app", value="tokenTalk"),
                    Annotation(key="alert_id", value=alert_id),
                    Annotation(key="event_type", value="alert_triggered"),
                ],
                numeric_annotations=[
                    Annotation(key="trigger_timestamp", value=int(datetime.now().timestamp()))
                ]
            )
            
            await self.client.create_entities([entity])
            
            self.metrics["events_logged"] += 1
            self.metrics["blockchain_operations"] += 1
            
            return True
            
        except Exception as e:
            logger.error(f"Error logging alert trigger: {e}")
            self.metrics["errors"] += 1
            return False
    
    # Analytics Operations
    async def store_price_analytics(self, symbol: str, price: float, volume: float = None, **metadata) -> bool:
        """Store price data for analytics"""
        try:
            price_data = {
                "symbol": symbol,
                "price": price,
                "volume": volume,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata,
                "app": "tokenTalk"
            }
            
            if self.mock_mode:
                price_id = f"price_{symbol}_{int(datetime.now().timestamp())}"
                self.local_entities[price_id] = price_data
                return True
            
            entity = GolemBaseCreate(
                data=json.dumps(price_data).encode('utf-8'),
                btl=self.config.btl_default,
                string_annotations=[
                    Annotation(key="type", value="price_data"),
                    Annotation(key="app", value="tokenTalk"),
                    Annotation(key="symbol", value=symbol),
                    Annotation(key="source", value=metadata.get("source", "redstone")),
                ],
                numeric_annotations=[
                    Annotation(key="price_cents", value=int(price * 100)),
                    Annotation(key="timestamp", value=int(datetime.now().timestamp()))
                ]
            )
            
            await self.client.create_entities([entity])
            self.metrics["blockchain_operations"] += 1
            return True
            
        except Exception as e:
            logger.debug(f"Error storing price analytics: {e}")  # Debug level since this is non-critical
            return False
    
    async def get_user_analytics(self, user_id: str, limit: int = 100) -> List[Dict]:
        """Get user's alert history and analytics"""
        try:
            if self.mock_mode:
                results = []
                for key, entity in self.local_entities.items():
                    if entity.get("user_id") == user_id:
                        results.append(entity)
                return results[-limit:]
            
            # Query user's alerts and triggers
            alert_results = await self.client.query_entities(
                f'app="tokenTalk" && user_id="{user_id}"'
            )
            
            analytics = []
            for result in alert_results:
                data = json.loads(result.storage_value.decode('utf-8'))
                analytics.append(data)
            
            return analytics[-limit:]
            
        except Exception as e:
            logger.error(f"Error getting user analytics: {e}")
            return []
    
    # Status and Management
    async def get_status(self) -> Dict:
        """Get service status"""
        status = {
            "service": "TokenTalk GolemDB Service",
            "connected": self.connected,
            "mock_mode": self.mock_mode,
            "sdk_available": GOLEM_AVAILABLE,
            "config": {
                "rpc_url": self.config.rpc_url,
                "has_private_key": bool(self.config.private_key),
                "btl_default": self.config.btl_default,
                "btl_permanent": self.config.btl_permanent
            },
            "metrics": self.metrics.copy()
        }
        
        if self.connected and self.client:
            try:
                owner_address = self.client.get_account_address()
                balance = await self.client.http_client().eth.get_balance(owner_address)
                
                status["blockchain"] = {
                    "address": owner_address,
                    "balance_eth": balance / 10**18,
                    "balance_wei": balance
                }
            except Exception as e:
                status["blockchain"] = {"error": str(e)}
        
        if self.mock_mode:
            status["mock_data"] = {
                "entities_stored": len(self.local_entities),
                "entity_types": list(set(
                    entity.get("type", "unknown") 
                    for entity in self.local_entities.values()
                ))
            }
        
        return status
    
    async def export_mock_data(self) -> Dict:
        """Export mock data for analysis"""
        return {
            "entities": self.local_entities.copy(),
            "metrics": self.metrics.copy(),
            "export_timestamp": datetime.now().isoformat()
        }
    
    async def close(self):
        """Close service"""
        if self.client:
            try:
                await self.client.disconnect()
                logger.info("🔌 GolemDB connection closed")
            except:
                pass

# Enhanced Hybrid Database for tokenTalk
class TokenTalkHybridDatabase:
    """Production-ready hybrid database with GolemDB integration"""
    
    def __init__(self, sqlite_db, golem_config: GolemConfig = None):
        self.sqlite_db = sqlite_db
        self.golem = TokenTalkGolemService(golem_config)
        self.golem_enabled = False
        
        # Integration settings
        self.sync_user_profiles = True
        self.log_alert_triggers = True
        self.store_price_analytics = False  # Optional for performance
    
    async def initialize(self) -> bool:
        """Initialize hybrid database"""
        logger.info("🚀 Initializing TokenTalk Hybrid Database...")
        
        # SQLite first (critical for alerts)
        await self.sqlite_db.init_database()
        logger.info("✅ SQLite database ready")
        
        # GolemDB second (graceful fallback)
        try:
            golem_success = await self.golem.initialize()
            if golem_success:
                self.golem_enabled = True
                status = await self.golem.get_status()
                mode = "mock mode" if status["mock_mode"] else "blockchain mode"
                logger.info(f"✅ GolemDB ready in {mode}")
            else:
                logger.warning("⚠️ GolemDB initialization failed")
        except Exception as e:
            logger.warning(f"⚠️ GolemDB error: {e}")
        
        logger.info("🎯 Hybrid database initialized successfully")
        return True
    
    # Enhanced User Operations
    async def get_or_create_user(self, user_id: str, email: str = None) -> User:
        """Create/get user with GolemDB sync"""
        # Primary: SQLite (fast, reliable)
        sqlite_user = await self.sqlite_db.get_or_create_user(user_id, email)
        
        # Secondary: GolemDB sync (user data ownership)
        if self.golem_enabled and self.sync_user_profiles:
            try:
                # Check if profile exists
                profile = await self.golem.get_user_profile(user_id)
                if not profile:
                    # Create profile on GolemDB
                    await self.golem.create_user_profile(user_id, email)
                    logger.info(f"👤 User profile synced to GolemDB: {user_id}")
            except Exception as e:
                logger.warning(f"GolemDB user sync failed: {e}")
        
        return sqlite_user
    
    async def update_user_email(self, user_id: str, email: str) -> bool:
        """Update user email in both systems"""
        # Primary: SQLite
        sqlite_success = await self.sqlite_db.update_user_email(user_id, email)
        
        # Secondary: GolemDB sync
        if self.golem_enabled and sqlite_success and self.sync_user_profiles:
            try:
                await self.golem.update_user_email(user_id, email)
                logger.info(f"📧 Email updated on GolemDB: {user_id}")
            except Exception as e:
                logger.warning(f"GolemDB email update failed: {e}")
        
        return sqlite_success
    
    # Enhanced Alert Operations
    async def create_alert(self, user_id: str, user_email: str, condition: AlertCondition, message: str) -> str:
        """Create alert with GolemDB audit trail"""
        # Primary: SQLite (needed for real-time engine)
        alert_id = await self.sqlite_db.create_alert(user_id, user_email, condition, message)
        
        # Secondary: GolemDB audit trail
        if self.golem_enabled:
            try:
                await self.golem.store_alert_config(alert_id, user_id, condition, message)
                logger.info(f"📝 Alert config stored on GolemDB: {alert_id[:8]}")
            except Exception as e:
                logger.warning(f"GolemDB alert storage failed: {e}")
        
        return alert_id
    
    async def log_alert_trigger(self, alert_id: str, price_data: Dict):
        """Log alert trigger with immutable audit trail"""
        # Primary: SQLite
        await self.sqlite_db.log_alert_trigger(alert_id, price_data)
        
        # Secondary: GolemDB (immutable audit)
        if self.golem_enabled and self.log_alert_triggers:
            try:
                await self.golem.log_alert_trigger(alert_id, price_data)
                logger.info(f"🔥 Alert trigger logged on GolemDB: {alert_id[:8]}")
            except Exception as e:
                logger.warning(f"GolemDB trigger logging failed: {e}")
    
    # Analytics Operations
    async def log_price_data(self, symbol: str, price: float, timestamp: int):
        """Log price data with optional GolemDB analytics"""
        # Primary: SQLite
        await self.sqlite_db.log_price_data(symbol, price, timestamp)
        
        # Secondary: GolemDB analytics (optional)
        if self.golem_enabled and self.store_price_analytics:
            try:
                await self.golem.store_price_analytics(symbol, price)
            except Exception as e:
                logger.debug(f"GolemDB price analytics failed: {e}")
    
    async def get_user_analytics(self, user_id: str) -> Dict:
        """Get comprehensive user analytics"""
        # Get SQLite data
        sqlite_alerts = await self.sqlite_db.get_user_alerts(user_id)
        
        analytics = {
            "user_id": user_id,
            "sqlite_alerts": len(sqlite_alerts),
            "recent_alerts": [
                {
                    "id": alert.id,
                    "status": alert.status,
                    "created_at": alert.created_at.isoformat(),
                    "condition_type": alert.condition.condition_type,
                    "tokens": alert.condition.tokens
                }
                for alert in sqlite_alerts[:10]
            ]
        }
        
        # Enhance with GolemDB data if available
        if self.golem_enabled:
            try:
                golem_analytics = await self.golem.get_user_analytics(user_id)
                analytics["golem_events"] = len(golem_analytics)
                analytics["blockchain_history"] = golem_analytics[:5]  # Recent events
            except Exception as e:
                logger.warning(f"GolemDB analytics failed: {e}")
                analytics["golem_events"] = "unavailable"
        
        return analytics
    
    # Status and Management
    async def get_status(self) -> Dict:
        """Get comprehensive hybrid status"""
        # SQLite status
        sqlite_healthy = True
        try:
            await self.sqlite_db.get_active_alerts()
        except:
            sqlite_healthy = False
        
        # GolemDB status
        golem_status = await self.golem.get_status() if self.golem_enabled else {"status": "disabled"}
        
        return {
            "service": "TokenTalk Hybrid Database",
            "sqlite": {
                "healthy": sqlite_healthy,
                "role": "primary (performance + alerts)"
            },
            "golemdb": {
                "enabled": self.golem_enabled,
                "status": golem_status,
                "role": "secondary (decentralization + audit)"
            },
            "features": {
                "sync_user_profiles": self.sync_user_profiles,
                "log_alert_triggers": self.log_alert_triggers,
                "store_price_analytics": self.store_price_analytics
            },
            "benefits": [
                "Real-time alerts (SQLite)",
                "User data ownership (GolemDB)",
                "Immutable audit trails",
                "Cross-platform data sync",
                "Decentralized backup",
                "Fault tolerance"
            ]
        }
    
    async def close(self):
        """Close hybrid database"""
        await self.golem.close()

# Easy integration function
async def create_tokenTalk_golem_hybrid(sqlite_db, golem_config: GolemConfig = None):
    """Create enhanced hybrid database with GolemDB"""
    hybrid_db = TokenTalkHybridDatabase(sqlite_db, golem_config)
    await hybrid_db.initialize()
    return hybrid_db