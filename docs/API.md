# 📚 tokenTalk API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
Currently, the API uses a simple user_id based system. In production, this should be replaced with proper JWT authentication.

## Table of Contents
- [Health & Status Endpoints](#health--status-endpoints)
- [Price Monitoring API](#price-monitoring-api)
- [Alert Management API](#alert-management-api)
- [Chat/NLP API](#chatnlp-api)
- [User Management API](#user-management-api)
- [GolemDB API](#golemdb-api)
- [WebSocket API](#websocket-api)
- [Error Responses](#error-responses)

---

## Health & Status Endpoints

### Root Endpoint
```http
GET /
```

**Response:**
```json
{
  "message": "🪨 tokenTalk API with GolemDB!",
  "version": "1.0.0",
  "description": "AI-powered crypto price alerts with blockchain-secured user data",
  "endpoints": {
    "docs": "/docs",
    "health": "/health",
    "alerts": "/api/alerts/",
    "prices": "/api/prices/",
    "chat": "/api/chat/",
    "users": "/api/users/",
    "golemdb_status": "/api/golemdb/status",
    "golemdb_analytics": "/api/golemdb/analytics/{user_id}",
    "websocket": "/ws?user_id=YOUR_USER_ID",
    "monitoring": "/api/monitoring/services"
  },
  "features": [
    "Real-time crypto price monitoring",
    "Natural language alert creation",
    "Blockchain-secured user profiles",
    "Enhanced personalized notifications",
    "Immutable audit trails",
    "Cross-platform data sync",
    "WebSocket notifications",
    "Email notifications via Resend",
    "RedStone oracle integration"
  ]
}
```

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "alert_engine": {
    "running": true,
    "active_alerts": 15,
    "monitoring_stats": {
      "checks_performed": 1250,
      "alerts_triggered": 8,
      "last_check": "2025-09-07T06:50:00Z"
    }
  },
  "golemdb": {
    "enabled": true,
    "mode": "blockchain",
    "status": "connected"
  },
  "nlp_service": "ready",
  "notification_channels": {
    "websocket": "active",
    "email": "configured"
  }
}
```

### Service Monitoring
```http
GET /api/monitoring/services
```

**Response:**
```json
{
  "services": {
    "alert_engine": {
      "status": "running",
      "uptime_seconds": 3600,
      "last_check": "2025-09-07T06:52:00Z"
    },
    "golemdb": {
      "status": "connected",
      "operations_count": 542,
      "last_sync": "2025-09-07T06:51:30Z"
    },
    "redstone": {
      "status": "available",
      "response_time_ms": 120
    },
    "ollama": {
      "status": "ready",
      "model": "llama2",
      "requests_handled": 234
    }
  }
}
```

---

## Price Monitoring API

### Get Current Prices
```http
GET /api/prices/?symbols=BTC,ETH,SOL
```

**Query Parameters:**
- `symbols` (string, required): Comma-separated list of cryptocurrency symbols

**Response:**
```json
{
  "prices": {
    "BTC": {
      "symbol": "BTC",
      "value": 45250.50,
      "currency": "USD",
      "timestamp": "2025-09-07T06:52:30Z",
      "change_24h": 2.5,
      "change_percent_24h": 5.7
    },
    "ETH": {
      "symbol": "ETH",
      "value": 2450.30,
      "currency": "USD",
      "timestamp": "2025-09-07T06:52:30Z",
      "change_24h": 120.5,
      "change_percent_24h": 5.2
    }
  },
  "source": "redstone",
  "cached": false
}
```

### Get Price History
```http
GET /api/prices/history?symbol=BTC&interval=1h&limit=24
```

**Query Parameters:**
- `symbol` (string, required): Cryptocurrency symbol
- `interval` (string, optional): Time interval (1m, 5m, 15m, 1h, 4h, 1d)
- `limit` (integer, optional): Number of data points (default: 100)

**Response:**
```json
{
  "symbol": "BTC",
  "interval": "1h",
  "data": [
    {
      "timestamp": "2025-09-07T06:00:00Z",
      "open": 44980.0,
      "high": 45300.0,
      "low": 44950.0,
      "close": 45250.50,
      "volume": 1234567890
    }
  ]
}
```

### Get Supported Symbols
```http
GET /api/prices/symbols
```

**Response:**
```json
{
  "symbols": [
    "BTC", "ETH", "BNB", "SOL", "ADA", "DOT", "MATIC",
    "LINK", "UNI", "AAVE", "CRV", "MKR", "SNX"
  ],
  "total": 13
}
```

---

## Alert Management API

### List Alerts
```http
GET /api/alerts/?user_id=user123&status=active
```

**Query Parameters:**
- `user_id` (string, optional): Filter by user ID
- `status` (string, optional): Filter by status (active, triggered, paused, deleted)

**Response:**
```json
{
  "alerts": [
    {
      "id": "alert_abc123",
      "user_id": "user123",
      "symbol": "BTC",
      "condition": "below",
      "target_price": 30000,
      "current_price": 45250.50,
      "status": "active",
      "created_at": "2025-09-06T10:30:00Z",
      "triggered_at": null,
      "notification_channels": ["email", "websocket"],
      "description": "Alert when Bitcoin drops below $30,000"
    }
  ],
  "total": 1,
  "active_count": 1
}
```

### Create Alert
```http
POST /api/alerts/
```

**Request Body:**
```json
{
  "user_id": "user123",
  "symbol": "BTC",
  "condition": "below",
  "target_price": 30000,
  "notification_channels": ["email", "websocket"],
  "description": "Bitcoin discount alert"
}
```

**Response:**
```json
{
  "alert": {
    "id": "alert_xyz789",
    "user_id": "user123",
    "symbol": "BTC",
    "condition": "below",
    "target_price": 30000,
    "status": "active",
    "created_at": "2025-09-07T06:55:00Z",
    "notification_channels": ["email", "websocket"]
  },
  "message": "Alert created successfully"
}
```

### Update Alert
```http
PUT /api/alerts/{alert_id}
```

**Request Body:**
```json
{
  "target_price": 28000,
  "status": "paused"
}
```

**Response:**
```json
{
  "alert": {
    "id": "alert_xyz789",
    "target_price": 28000,
    "status": "paused",
    "updated_at": "2025-09-07T06:56:00Z"
  },
  "message": "Alert updated successfully"
}
```

### Delete Alert
```http
DELETE /api/alerts/{alert_id}
```

**Response:**
```json
{
  "message": "Alert deleted successfully",
  "alert_id": "alert_xyz789"
}
```

### Get Alert Statistics
```http
GET /api/alerts/stats?user_id=user123
```

**Response:**
```json
{
  "user_id": "user123",
  "stats": {
    "total_alerts": 15,
    "active_alerts": 8,
    "triggered_today": 2,
    "triggered_this_week": 5,
    "most_tracked_symbol": "BTC",
    "average_response_time_ms": 250
  }
}
```

---

## Chat/NLP API

### Process Natural Language Request
```http
POST /api/chat/
```

**Request Body:**
```json
{
  "message": "Alert me when Bitcoin drops below $30,000",
  "user_id": "user123",
  "context": {
    "previous_messages": [],
    "user_preferences": {}
  }
}
```

**Response:**
```json
{
  "response": "I've created an alert for you. You'll be notified when Bitcoin (BTC) drops below $30,000.",
  "action_taken": "alert_created",
  "alert_details": {
    "id": "alert_abc456",
    "symbol": "BTC",
    "condition": "below",
    "target_price": 30000
  },
  "parsed_intent": {
    "type": "create_alert",
    "confidence": 0.95,
    "entities": {
      "cryptocurrency": "Bitcoin",
      "symbol": "BTC",
      "condition": "below",
      "price": 30000
    }
  }
}
```

### Get Chat History
```http
GET /api/chat/history?user_id=user123&limit=50
```

**Response:**
```json
{
  "messages": [
    {
      "id": "msg_123",
      "user_id": "user123",
      "message": "What's the current price of Ethereum?",
      "response": "The current price of Ethereum (ETH) is $2,450.30, up 5.2% in the last 24 hours.",
      "timestamp": "2025-09-07T06:40:00Z",
      "intent": "price_query"
    }
  ],
  "total": 1
}
```

---

## User Management API

### Get User Profile
```http
GET /api/users/{user_id}
```

**Response:**
```json
{
  "user": {
    "id": "user123",
    "email": "user@example.com",
    "created_at": "2025-09-01T10:00:00Z",
    "preferences": {
      "notification_channels": ["email", "websocket"],
      "email_frequency": "instant",
      "timezone": "UTC",
      "currency": "USD"
    },
    "stats": {
      "total_alerts": 15,
      "active_alerts": 8,
      "alerts_triggered": 42
    },
    "golemdb_profile": {
      "blockchain_address": "0x1234...5678",
      "data_synced": true,
      "last_sync": "2025-09-07T06:50:00Z"
    }
  }
}
```

### Create User
```http
POST /api/users/
```

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "preferences": {
    "notification_channels": ["email"],
    "currency": "USD",
    "timezone": "America/New_York"
  }
}
```

**Response:**
```json
{
  "user": {
    "id": "user456",
    "email": "newuser@example.com",
    "created_at": "2025-09-07T07:00:00Z"
  },
  "golemdb": {
    "profile_created": true,
    "blockchain_tx": "0xabc...def"
  },
  "message": "User created successfully"
}
```

### Update User Preferences
```http
PUT /api/users/{user_id}/preferences
```

**Request Body:**
```json
{
  "notification_channels": ["email", "websocket", "sms"],
  "email_frequency": "daily_digest",
  "currency": "EUR"
}
```

**Response:**
```json
{
  "preferences": {
    "notification_channels": ["email", "websocket", "sms"],
    "email_frequency": "daily_digest",
    "currency": "EUR",
    "updated_at": "2025-09-07T07:02:00Z"
  },
  "message": "Preferences updated successfully"
}
```

### Delete User
```http
DELETE /api/users/{user_id}
```

**Response:**
```json
{
  "message": "User deleted successfully",
  "data_archived": true,
  "golemdb_archived": true
}
```

---

## GolemDB API

### Get GolemDB Status
```http
GET /api/golemdb/status
```

**Response:**
```json
{
  "golemdb": {
    "enabled": true,
    "status": {
      "connected": true,
      "mock_mode": false,
      "blockchain": {
        "network": "polygon-mumbai",
        "address": "0x1234...5678",
        "balance_eth": 0.5432,
        "transaction_count": 156
      }
    },
    "statistics": {
      "total_users": 234,
      "total_operations": 1567,
      "data_size_mb": 12.5,
      "last_sync": "2025-09-07T06:52:00Z"
    }
  }
}
```

### Get User Analytics
```http
GET /api/golemdb/analytics/{user_id}
```

**Response:**
```json
{
  "user_id": "user123",
  "analytics": {
    "engagement_score": 85,
    "alert_patterns": {
      "most_tracked": ["BTC", "ETH"],
      "average_target_deviation": 15.5,
      "preferred_conditions": ["below", "above"]
    },
    "notification_performance": {
      "delivery_rate": 0.98,
      "response_time_avg_ms": 245,
      "channels_used": {
        "email": 45,
        "websocket": 120
      }
    },
    "blockchain_activity": {
      "transactions": 45,
      "data_writes": 120,
      "last_activity": "2025-09-07T06:45:00Z"
    }
  }
}
```

### Sync User Data
```http
POST /api/golemdb/sync/{user_id}
```

**Response:**
```json
{
  "sync_status": "completed",
  "records_synced": 15,
  "blockchain_tx": "0xdef...123",
  "timestamp": "2025-09-07T07:05:00Z"
}
```

---

## WebSocket API

### Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws?user_id=user123');
```

### Message Types

#### Client to Server

**Subscribe to Price Updates:**
```json
{
  "type": "subscribe",
  "symbols": ["BTC", "ETH", "SOL"]
}
```

**Unsubscribe from Price Updates:**
```json
{
  "type": "unsubscribe",
  "symbols": ["SOL"]
}
```

**Heartbeat:**
```json
{
  "type": "ping"
}
```

#### Server to Client

**Price Update:**
```json
{
  "type": "price_update",
  "data": {
    "symbol": "BTC",
    "price": 45250.50,
    "timestamp": "2025-09-07T07:00:00Z",
    "change_24h": 2.5
  }
}
```

**Alert Triggered:**
```json
{
  "type": "alert_triggered",
  "data": {
    "alert_id": "alert_123",
    "symbol": "BTC",
    "condition": "below",
    "target_price": 30000,
    "current_price": 29950,
    "message": "Bitcoin has dropped below your target price of $30,000",
    "timestamp": "2025-09-07T07:10:00Z"
  }
}
```

**System Notification:**
```json
{
  "type": "notification",
  "data": {
    "level": "info",
    "message": "System maintenance scheduled for 2 AM UTC",
    "timestamp": "2025-09-07T07:00:00Z"
  }
}
```

**Heartbeat Response:**
```json
{
  "type": "pong",
  "timestamp": "2025-09-07T07:00:00Z"
}
```

### WebSocket Error Codes
- `1000`: Normal closure
- `1001`: Going away
- `1002`: Protocol error
- `1003`: Unsupported data
- `1006`: Abnormal closure
- `1007`: Invalid frame payload data
- `1008`: Policy violation
- `1009`: Message too big
- `1011`: Internal server error
- `4000`: Invalid user_id
- `4001`: Authentication failed
- `4002`: Rate limit exceeded

### Example WebSocket Client
```javascript
class TokenTalkWebSocket {
  constructor(userId) {
    this.userId = userId;
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }

  connect() {
    this.ws = new WebSocket(`ws://localhost:8000/ws?user_id=${this.userId}`);
    
    this.ws.onopen = () => {
      console.log('Connected to tokenTalk WebSocket');
      this.reconnectAttempts = 0;
      
      // Subscribe to prices
      this.subscribe(['BTC', 'ETH']);
    };
    
    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };
    
    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    this.ws.onclose = (event) => {
      console.log('WebSocket closed:', event.code, event.reason);
      this.handleReconnect();
    };
  }
  
  handleMessage(message) {
    switch(message.type) {
      case 'price_update':
        console.log('Price update:', message.data);
        break;
      case 'alert_triggered':
        console.log('Alert triggered!', message.data);
        // Show notification to user
        break;
      case 'notification':
        console.log('System notification:', message.data);
        break;
      case 'pong':
        console.log('Heartbeat acknowledged');
        break;
    }
  }
  
  subscribe(symbols) {
    if (this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'subscribe',
        symbols: symbols
      }));
    }
  }
  
  handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`);
      setTimeout(() => this.connect(), 5000 * this.reconnectAttempts);
    }
  }
  
  disconnect() {
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
    }
  }
}

// Usage
const client = new TokenTalkWebSocket('user123');
client.connect();
```

---

## Error Responses

### Standard Error Format
```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "The requested alert was not found",
    "details": {
      "alert_id": "alert_999",
      "timestamp": "2025-09-07T07:00:00Z"
    }
  }
}
```

### Common Error Codes
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Access denied
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource already exists
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service temporarily unavailable

### Error Code Reference
| Code | Description |
|------|-------------|
| `INVALID_SYMBOL` | Cryptocurrency symbol not supported |
| `INVALID_PRICE` | Target price is invalid or out of range |
| `USER_NOT_FOUND` | User ID does not exist |
| `ALERT_NOT_FOUND` | Alert ID does not exist |
| `DUPLICATE_ALERT` | Similar alert already exists |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `BLOCKCHAIN_ERROR` | GolemDB blockchain operation failed |
| `NLP_PARSE_ERROR` | Could not understand natural language input |
| `NOTIFICATION_FAILED` | Failed to send notification |
| `DATABASE_ERROR` | Database operation failed |

---

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Default limits:**
  - 100 requests per minute per IP
  - 1000 requests per hour per user
  
- **Endpoint-specific limits:**
  - Price queries: 200/minute
  - Alert creation: 20/minute
  - Chat/NLP: 30/minute
  - WebSocket messages: 100/minute

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1693900800
```

---

## API Versioning

The current API version is `v1`. Future versions will be accessible via:
- URL path: `/api/v2/...`
- Header: `Accept: application/vnd.tokentalk.v2+json`

---

## Testing the API

### Using cURL

**Get current price:**
```bash
curl -X GET "http://localhost:8000/api/prices/?symbols=BTC,ETH"
```

**Create an alert:**
```bash
curl -X POST "http://localhost:8000/api/alerts/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "symbol": "BTC",
    "condition": "below",
    "target_price": 30000
  }'
```

**Natural language alert:**
```bash
curl -X POST "http://localhost:8000/api/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me when Ethereum goes above $3000",
    "user_id": "user123"
  }'
```

### Using Python

```python
import requests
import json

# Base URL
BASE_URL = "http://localhost:8000"

# Get prices
response = requests.get(f"{BASE_URL}/api/prices/", params={"symbols": "BTC,ETH"})
prices = response.json()
print(f"Bitcoin price: ${prices['prices']['BTC']['value']}")

# Create alert
alert_data = {
    "user_id": "user123",
    "symbol": "BTC",
    "condition": "below",
    "target_price": 30000
}
response = requests.post(f"{BASE_URL}/api/alerts/", json=alert_data)
alert = response.json()
print(f"Alert created: {alert['alert']['id']}")

# Natural language request
chat_data = {
    "message": "What's the price of Bitcoin?",
    "user_id": "user123"
}
response = requests.post(f"{BASE_URL}/api/chat/", json=chat_data)
chat_response = response.json()
print(f"Response: {chat_response['response']}")
```

### Using JavaScript/Node.js

```javascript
// Using fetch API
const BASE_URL = 'http://localhost:8000';

// Get prices
async function getPrices() {
  const response = await fetch(`${BASE_URL}/api/prices/?symbols=BTC,ETH`);
  const data = await response.json();
  console.log('Prices:', data.prices);
}

// Create alert
async function createAlert() {
  const response = await fetch(`${BASE_URL}/api/alerts/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      user_id: 'user123',
      symbol: 'BTC',
      condition: 'below',
      target_price: 30000
    })
  });
  const data = await response.json();
  console.log('Alert created:', data.alert);
}

// Chat/NLP request
async function chatRequest() {
  const response = await fetch(`${BASE_URL}/api/chat/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message: 'Alert me when Bitcoin hits $50,000',
      user_id: 'user123'
    })
  });
  const data = await response.json();
  console.log('Chat response:', data.response);
}
```

---

## Support

For API support and questions:
- GitHub Issues: https://github.com/ivanmanhique/tokenTalk/issues
- API Status: http://localhost:8000/health
- Documentation: http://localhost:8000/docs (Swagger UI)
