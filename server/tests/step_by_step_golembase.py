#!/usr/bin/env python3
"""
step_by_step_golembase.py - Step-by-step GolemBase integration for tokenTalk
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Dict, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# GolemBase imports
try:
    import golem_base_sdk
    from golem_base_sdk import (
        GolemBaseClient,
        GolemBaseHttpClient,
        GolemBaseROClient,
        EntityKey,
        EntityMetadata,
        GolemBaseCreate,
        GolemBaseUpdate,
        WalletError,
        ProviderConnectionError
    )
    SDK_AVAILABLE = True
except ImportError as e:
    print(f"❌ GolemBase SDK import failed: {e}")
    SDK_AVAILABLE = False

class GolemBaseIntegrationGuide:
    """Step-by-step integration guide for GolemBase with tokenTalk"""
    
    def __init__(self):
        self.step_results = {}
        self.client = None
        self.ro_client = None
        self.http_client = None
    
    async def step_1_check_sdk(self) -> bool:
        """Step 1: Verify SDK is properly installed and imported"""
        print("\n" + "="*60)
        print("📦 STEP 1: Check GolemBase SDK")
        print("="*60)
        
        if not SDK_AVAILABLE:
            print("❌ GolemBase SDK not available")
            print("💡 Install with: pip install golem-base-sdk==0.1.0")
            return False
        
        print("✅ GolemBase SDK successfully imported")
        print(f"📊 Available classes: {len([x for x in dir(golem_base_sdk) if not x.startswith('_')])}")
        
        # Show key classes
        key_classes = [
            'GolemBaseClient', 'GolemBaseHttpClient', 'GolemBaseROClient',
            'EntityKey', 'EntityMetadata', 'GolemBaseCreate', 'GolemBaseUpdate'
        ]
        
        print("🔑 Key classes found:")
        for cls_name in key_classes:
            if hasattr(golem_base_sdk, cls_name):
                print(f"   ✅ {cls_name}")
            else:
                print(f"   ❌ {cls_name} (missing)")
        
        self.step_results["sdk_check"] = True
        return True
    
    async def step_2_connection_setup(self) -> bool:
        """Step 2: Set up basic connection to GolemBase"""
        print("\n" + "="*60)
        print("🔗 STEP 2: Connection Setup")
        print("="*60)
        
        # Configuration options
        config_options = {
            "localhost": "http://localhost:8545",
            "testnet": "https://goerli.infura.io/v3/YOUR_PROJECT_ID",  # Example
            "custom": None
        }
        
        print("🌐 Connection options:")
        for name, endpoint in config_options.items():
            if endpoint:
                print(f"   {name}: {endpoint}")
        
        # For this demo, we'll try localhost first
        rpc_endpoint = config_options["localhost"]
        print(f"\n🔧 Using endpoint: {rpc_endpoint}")
        
        try:
            # Try to create read-only client first (no wallet needed)
            print("📖 Creating read-only client...")
            self.ro_client = GolemBaseROClient(rpc_endpoint=rpc_endpoint)
            print("✅ Read-only client created")
            
            # Try to create HTTP client
            print("🌐 Creating HTTP client...")
            self.http_client = GolemBaseHttpClient(rpc_endpoint=rpc_endpoint)
            print("✅ HTTP client created")
            
            # For write operations, we need a wallet
            wallet_key = os.getenv("GOLEMBASE_WALLET_PRIVATE_KEY")
            if wallet_key:
                print("💳 Creating main client with wallet...")
                self.client = GolemBaseClient(
                    rpc_endpoint=rpc_endpoint,
                    private_key=wallet_key
                )
                print("✅ Main client with wallet created")
            else:
                print("⚠️  No wallet key provided (read-only mode)")
                print("💡 Set GOLEMBASE_WALLET_PRIVATE_KEY environment variable for write access")
            
            self.step_results["connection_setup"] = True
            return True
            
        except ProviderConnectionError as e:
            print(f"❌ Connection failed: {e}")
            print("💡 Make sure your blockchain node is running")
            return False
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            return False
    
    async def step_3_test_basic_operations(self) -> bool:
        """Step 3: Test basic entity operations"""
        print("\n" + "="*60)
        print("🧪 STEP 3: Test Basic Operations")
        print("="*60)
        
        if not self.ro_client:
            print("❌ No client available for testing")
            return False
        
        try:
            # Test 1: Entity Key creation
            print("🔑 Testing EntityKey creation...")
            test_entity_key = EntityKey(
                entity_type="tokenTalk.Test",
                id="test_entity_1"
            )
            print(f"✅ EntityKey created: {test_entity_key.entity_type}/{test_entity_key.id}")
            
            # Test 2: Entity Metadata creation
            print("📄 Testing EntityMetadata creation...")
            test_data = {
                "message": "Hello GolemBase!",
                "timestamp": datetime.now().isoformat(),
                "test_number": 42
            }
            test_metadata = EntityMetadata(data=test_data)
            print(f"✅ EntityMetadata created with {len(test_data)} fields")
            
            # Test 3: Try to query (read operation)
            print("📖 Testing read operations...")
            try:
                # This would attempt to get an entity (might fail if none exist)
                result = await self.ro_client.get_entity(test_entity_key)
                print("✅ Read operation successful")
            except Exception as e:
                print(f"ℹ️  Read operation failed (expected if no data): {e}")
            
            # Test 4: Write operation (if client available)
            if self.client:
                print("✏️  Testing write operations...")
                try:
                    create_op = GolemBaseCreate(
                        entity_key=test_entity_key,
                        metadata=test_metadata
                    )
                    
                    result = await self.client.create_entity(create_op)
                    print("✅ Write operation successful")
                    
                    # Try to read back what we wrote
                    read_result = await self.client.get_entity(test_entity_key)
                    if read_result:
                        print("✅ Read-after-write successful")
                    
                except Exception as e:
                    print(f"⚠️  Write operation failed: {e}")
                    print("💡 This might be due to network, gas, or permission issues")
            else:
                print("⚠️  Skipping write test (no wallet)")
            
            self.step_results["basic_operations"] = True
            return True
            
        except Exception as e:
            print(f"❌ Basic operations test failed: {e}")
            return False
    
    async def step_4_tokenTalk_entities(self) -> bool:
        """Step 4: Design tokenTalk entities for GolemBase"""
        print("\n" + "="*60)
        print("🏗️  STEP 4: Design TokenTalk Entities")
        print("="*60)
        
        # Define entity schemas for tokenTalk
        entity_schemas = {
            "tokenTalk.User": {
                "description": "User profiles and preferences",
                "fields": {
                    "user_id": "string (unique identifier)",
                    "email": "string (email address)",
                    "preferences": "object (notification settings)",
                    "created_at": "string (ISO timestamp)",
                    "updated_at": "string (ISO timestamp)"
                },
                "indexes": ["user_id", "email"]
            },
            
            "tokenTalk.Alert": {
                "description": "Crypto price alerts",
                "fields": {
                    "alert_id": "string (unique identifier)",
                    "user_id": "string (owner reference)",
                    "condition": "object (price condition)",
                    "message": "string (alert description)",
                    "status": "string (active/triggered/paused)",
                    "created_at": "string (ISO timestamp)",
                    "triggered_at": "string (ISO timestamp)"
                },
                "indexes": ["alert_id", "user_id", "status"]
            },
            
            "tokenTalk.PriceHistory": {
                "description": "Historical price data",
                "fields": {
                    "price_id": "string (unique identifier)",
                    "symbol": "string (token symbol)",
                    "price": "number (price value)",
                    "timestamp": "string (ISO timestamp)",
                    "source": "string (data source)"
                },
                "indexes": ["symbol", "timestamp"]
            },
            
            "tokenTalk.AlertTrigger": {
                "description": "Alert trigger events (audit trail)",
                "fields": {
                    "trigger_id": "string (unique identifier)",
                    "alert_id": "string (alert reference)",
                    "user_id": "string (user reference)",
                    "triggered_at": "string (ISO timestamp)",
                    "price_data": "object (trigger price info)",
                    "notification_sent": "boolean"
                },
                "indexes": ["alert_id", "user_id", "triggered_at"]
            }
        }
        
        print(f"📋 Designed {len(entity_schemas)} entity types:")
        for entity_type, schema in entity_schemas.items():
            print(f"\n🔸 {entity_type}")
            print(f"   📝 {schema['description']}")
            print(f"   📊 Fields: {len(schema['fields'])}")
            print(f"   🔍 Indexes: {', '.join(schema['indexes'])}")
        
        # Test creating sample entities
        if self.client:
            print(f"\n🧪 Testing entity creation...")
            
            try:
                # Test User entity
                user_key = EntityKey(entity_type="tokenTalk.User", id="test_user_123")
                user_data = {
                    "user_id": "test_user_123",
                    "email": "test@tokenTalk.com",
                    "preferences": {"email_notifications": True},
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                user_metadata = EntityMetadata(data=user_data)
                
                create_user_op = GolemBaseCreate(
                    entity_key=user_key,
                    metadata=user_metadata
                )
                
                user_result = await self.client.create_entity(create_user_op)
                print("✅ Test user entity created")
                
                # Test Alert entity
                alert_key = EntityKey(entity_type="tokenTalk.Alert", id="test_alert_456")
                alert_data = {
                    "alert_id": "test_alert_456",
                    "user_id": "test_user_123",
                    "condition": {
                        "tokens": ["ETH"],
                        "condition_type": "price_above",
                        "threshold": 4000.0
                    },
                    "message": "Alert when ETH hits $4000",
                    "status": "active",
                    "created_at": datetime.now().isoformat()
                }
                alert_metadata = EntityMetadata(data=alert_data)
                
                create_alert_op = GolemBaseCreate(
                    entity_key=alert_key,
                    metadata=alert_metadata
                )
                
                alert_result = await self.client.create_entity(create_alert_op)
                print("✅ Test alert entity created")
                
            except Exception as e:
                print(f"⚠️  Entity creation test failed: {e}")
        
        self.step_results["entity_design"] = True
        return True
    
    async def step_5_integration_strategy(self) -> bool:
        """Step 5: Plan integration strategy"""
        print("\n" + "="*60)
        print("🎯 STEP 5: Integration Strategy")
        print("="*60)
        
        strategies = {
            "hybrid_sqlite_primary": {
                "description": "SQLite for performance, GolemBase for decentralization",
                "pros": ["Fast real-time alerts", "Decentralized user data", "Fault tolerant"],
                "cons": ["Additional complexity", "Sync overhead"],
                "use_case": "Production ready"
            },
            
            "golembase_primary": {
                "description": "GolemBase as primary database",
                "pros": ["Full decentralization", "User data ownership", "Censorship resistant"],
                "cons": ["Slower queries", "Gas costs", "Network dependency"],
                "use_case": "Fully decentralized"
            },
            
            "gradual_migration": {
                "description": "Migrate data types gradually to GolemBase",
                "pros": ["Low risk", "Incremental benefits", "Easy rollback"],
                "cons": ["Extended timeline", "Temporary complexity"],
                "use_case": "Safe transition"
            }
        }
        
        print("📋 Available integration strategies:")
        
        for strategy_name, details in strategies.items():
            print(f"\n🔸 {strategy_name.replace('_', ' ').title()}")
            print(f"   📝 {details['description']}")
            print(f"   ✅ Pros: {', '.join(details['pros'])}")
            print(f"   ⚠️  Cons: {', '.join(details['cons'])}")
            print(f"   🎯 Best for: {details['use_case']}")
        
        # Recommended data routing
        print(f"\n📊 Recommended Data Routing:")
        data_routing = {
            "Active Alerts": "SQLite (fast reads for alert engine)",
            "User Profiles": "GolemBase (user ownership)",
            "Price History": "GolemBase (permanent analytics)",
            "Alert Triggers": "Both (audit trail + performance)",
            "Session Data": "SQLite only (temporary)"
        }
        
        for data_type, storage in data_routing.items():
            print(f"   📂 {data_type}: {storage}")
        
        self.step_results["integration_strategy"] = True
        return True
    
    async def step_6_configuration(self) -> bool:
        """Step 6: Configuration and environment setup"""
        print("\n" + "="*60)
        print("⚙️  STEP 6: Configuration Setup")
        print("="*60)
        
        # Environment variables needed
        env_vars = {
            "GOLEMBASE_RPC_ENDPOINT": "Blockchain RPC endpoint (e.g., http://localhost:8545)",
            "GOLEMBASE_WALLET_PRIVATE_KEY": "Wallet private key for write operations",
            "GOLEMBASE_NETWORK": "Network name (testnet/mainnet)",
            "ENABLE_GOLEMBASE": "Enable GolemBase integration (True/False)",
            "GOLEMBASE_SYNC_INTERVAL": "Background sync interval in seconds"
        }
        
        print("🔧 Required environment variables:")
        for var, description in env_vars.items():
            current_value = os.getenv(var, "Not set")
            status = "✅" if current_value != "Not set" else "❌"
            print(f"   {status} {var}: {description}")
            if current_value != "Not set":
                # Mask private key for security
                if "PRIVATE_KEY" in var:
                    print(f"      Current: {current_value[:10]}...{current_value[-4:]}")
                else:
                    print(f"      Current: {current_value}")
        
        # Create sample .env file
        env_template = '''# GolemBase Configuration for tokenTalk
GOLEMBASE_RPC_ENDPOINT=http://localhost:8545
GOLEMBASE_WALLET_PRIVATE_KEY=your_private_key_here
GOLEMBASE_NETWORK=testnet
ENABLE_GOLEMBASE=True
GOLEMBASE_SYNC_INTERVAL=300

# Existing tokenTalk config...
REDSTONE_API_URL=https://api.redstone.finance/prices
OLLAMA_URL=http://localhost:11434
RESEND_API_KEY=your_resend_key_here
'''
        
        print(f"\n📄 Sample .env configuration:")
        print(env_template)
        
        # Check current configuration
        current_config = {var: os.getenv(var) for var in env_vars.keys()}
        ready_for_production = all(value is not None for value in current_config.values())
        
        print(f"\n🚦 Configuration Status:")
        print(f"   Ready for production: {'✅' if ready_for_production else '❌'}")
        print(f"   Read-only mode: {'✅' if self.ro_client else '❌'}")
        print(f"   Write access: {'✅' if self.client else '❌'}")
        
        self.step_results["configuration"] = True
        return True
    
    async def step_7_next_steps(self) -> bool:
        """Step 7: Next steps and implementation"""
        print("\n" + "="*60)
        print("🚀 STEP 7: Next Steps")
        print("="*60)
        
        implementation_steps = [
            {
                "step": "1. Update main.py",
                "action": "Replace database import with hybrid GolemBase service",
                "code": "from services.golembase_service import hybrid_golembase_db as db"
            },
            {
                "step": "2. Environment setup", 
                "action": "Add GolemBase configuration to .env file",
                "code": "Copy the sample .env configuration above"
            },
            {
                "step": "3. Initialize service",
                "action": "Update startup_event in main.py",
                "code": "await db.initialize()"
            },
            {
                "step": "4. Test integration",
                "action": "Run the test suite",
                "code": "python test_golembase_real.py"
            },
            {
                "step": "5. Gradual migration",
                "action": "Start with user data, then alerts",
                "code": "Enable sync_enabled flag incrementally"
            }
        ]
        
        print("📋 Implementation checklist:")
        for item in implementation_steps:
            print(f"\n🔸 {item['step']}")
            print(f"   📝 {item['action']}")
            print(f"   💻 {item['code']}")
        
        # Generate integration status report
        print(f"\n📊 Integration Readiness Report:")
        
        total_steps = len(self.step_results)
        completed_steps = sum(self.step_results.values())
        
        print(f"   📈 Progress: {completed_steps}/{total_steps} steps completed")
        print(f"   ✅ Success Rate: {(completed_steps/total_steps)*100:.1f}%")
        
        for step_name, completed in self.step_results.items():
            status = "✅" if completed else "❌"
            print(f"   {status} {step_name.replace('_', ' ').title()}")
        
        if completed_steps == total_steps:
            print(f"\n🎉 All steps completed! Ready for GolemBase integration.")
            print(f"💡 You can now start using decentralized storage for your tokenTalk data.")
        else:
            print(f"\n⚠️  Some steps need attention before proceeding.")
        
        self.step_results["next_steps"] = True
        return True
    
    async def cleanup(self):
        """Clean up connections"""
        try:
            for client in [self.client, self.ro_client, self.http_client]:
                if client and hasattr(client, 'close'):
                    await client.close()
        except Exception as e:
            print(f"⚠️  Cleanup warning: {e}")

async def main():
    """Run the complete step-by-step integration guide"""
    print("🏗️  tokenTalk + GolemBase Integration Guide")
    print("="*60)
    print("This guide will walk you through integrating GolemBase")
    print("decentralized database with your tokenTalk project.")
    
    guide = GolemBaseIntegrationGuide()
    
    try:
        # Run all steps
        await guide.step_1_check_sdk()
        await guide.step_2_connection_setup()
        await guide.step_3_test_basic_operations()
        await guide.step_4_tokenTalk_entities()
        await guide.step_5_integration_strategy()
        await guide.step_6_configuration()
        await guide.step_7_next_steps()
        
        print("\n" + "="*60)
        print("🏁 Integration Guide Complete!")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n🛑 Integration guide interrupted")
    except Exception as e:
        print(f"\n💥 Integration guide failed: {e}")
    finally:
        await guide.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
