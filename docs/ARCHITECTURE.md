# 🏗️ tokenTalk Architecture Documentation

## Overview

tokenTalk is a microservice-based cryptocurrency monitoring platform built with a modern, scalable architecture. The system combines real-time data processing, AI-powered natural language understanding, blockchain storage, and multi-channel notifications into a cohesive platform.

## Table of Contents
- [System Architecture](#system-architecture)
- [Core Components](#core-components)
- [Data Flow](#data-flow)
- [Technology Stack](#technology-stack)
- [Design Patterns](#design-patterns)
- [Security Architecture](#security-architecture)
- [Scalability Considerations](#scalability-considerations)
- [Deployment Architecture](#deployment-architecture)

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          Client Layer                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │  React SPA  │  │  Mobile App │  │   CLI Tool  │            │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘            │
└─────────┼─────────────────┼─────────────────┼──────────────────┘
          │                 │                 │
          └─────────────────┼─────────────────┘
                           │
                    ┌──────▼──────┐
                    │  API Gateway │
                    │   (FastAPI)  │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────▼────────┐ ┌───────▼────────┐ ┌──────▼──────┐
│  Alert Service │ │  Price Service │ │ Chat Service│
└───────┬────────┘ └───────┬────────┘ └──────┬──────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                    ┌──────▼──────┐
                    │   Core Bus   │
                    └──────┬──────┘
                           │
     ┌─────────────────────┼─────────────────────┐
     │                     │                     │
┌────▼─────┐      ┌────────▼────────┐    ┌──────▼──────┐
│  SQLite  │      │     GolemDB     │    │  RedStone   │
│    DB    │      │   (Blockchain)  │    │   Oracle    │
└──────────┘      └─────────────────┘    └─────────────┘
```

### Component Layers

#### 1. **Presentation Layer**
- **React Frontend**: Single-page application with responsive design
- **WebSocket Client**: Real-time bidirectional communication
- **RESTful API Client**: Standard HTTP communication

#### 2. **API Gateway Layer**
- **FastAPI Framework**: High-performance async API gateway
- **CORS Middleware**: Cross-origin resource sharing
- **Rate Limiting**: Request throttling and protection
- **Authentication**: User identification and session management

#### 3. **Service Layer**
- **Alert Engine**: Continuous monitoring and alert triggering
- **NLP Service**: Natural language processing for chat interface
- **Notification Service**: Multi-channel notification delivery
- **Price Service**: Cryptocurrency price data aggregation

#### 4. **Data Layer**
- **SQLite**: Local persistent storage for alerts and user data
- **GolemDB**: Blockchain-based distributed storage
- **RedStone Oracle**: External price data provider
- **Cache Layer**: In-memory caching for performance

## Core Components

### Backend Components

#### 1. **Main Application (main.py)**
```python
# Key Responsibilities:
- Application lifecycle management
- Service initialization
- Dependency injection
- Route registration
- Middleware configuration
```

**Features:**
- Modern FastAPI lifespan handler
- Graceful startup/shutdown
- Service health monitoring
- Global error handling

#### 2. **Alert Engine (alert_engine.py)**
```python
# Key Responsibilities:
- Continuous price monitoring
- Alert condition evaluation
- Trigger notification dispatch
- Performance metrics collection
```

**Architecture:**
- Async/await pattern for non-blocking operations
- Background task execution
- Event-driven alert processing
- Configurable monitoring intervals

#### 3. **NLP Service (nlp_service.py)**
```python
# Key Responsibilities:
- Natural language understanding
- Intent classification
- Entity extraction
- Response generation
```

**Integration:**
- Ollama for local LLM processing
- Optional cloud API support (Claude/OpenAI)
- Context-aware processing
- Multi-turn conversation support

#### 4. **GolemDB Service (golemdb_service.py)**
```python
# Key Responsibilities:
- Blockchain data persistence
- User profile management
- Audit trail creation
- Cross-platform sync
```

**Features:**
- Hybrid database approach (SQLite + Blockchain)
- Mock mode for development
- Transaction management
- Data encryption

#### 5. **Notification Service (notification_service.py)**
```python
# Key Responsibilities:
- Multi-channel delivery
- Message formatting
- Delivery tracking
- Retry logic
```

**Channels:**
- WebSocket (real-time)
- Email (Resend API)
- In-app notifications
- Future: SMS, Push notifications

### Frontend Components

#### 1. **App Router (App.jsx)**
```javascript
// Key Responsibilities:
- Route management
- Component lazy loading
- Navigation guards
- State preservation
```

#### 2. **Dashboard Component**
```javascript
// Features:
- Real-time price display
- Alert management UI
- User statistics
- WebSocket integration
```

#### 3. **Chat Interface**
```javascript
// Features:
- Natural language input
- Conversation history
- AI response display
- Context management
```

## Data Flow

### 1. **Alert Creation Flow**

```
User Input → NLP Processing → Intent Extraction → Alert Creation → 
Database Storage → GolemDB Sync → Confirmation Response
```

**Detailed Steps:**
1. User sends natural language request
2. NLP service processes and extracts intent
3. Alert parameters validated
4. Alert stored in SQLite
5. Profile synced to GolemDB
6. WebSocket notification sent
7. Email confirmation dispatched

### 2. **Price Monitoring Flow**

```
RedStone API → Price Service → Cache Update → Alert Engine → 
Condition Check → Trigger Notification → User Delivery
```

**Detailed Steps:**
1. Periodic price fetch from RedStone
2. Price data cached in memory
3. Alert engine evaluates conditions
4. Triggered alerts queued
5. Notifications dispatched via channels
6. Delivery status tracked

### 3. **WebSocket Communication Flow**

```
Client Connect → Auth Validation → Subscription → 
Real-time Updates → Bidirectional Messaging → Graceful Disconnect
```

**Message Types:**
- Price updates
- Alert triggers
- System notifications
- Heartbeat/ping-pong

## Technology Stack

### Backend Technologies

| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | FastAPI | High-performance async API |
| Language | Python 3.8+ | Backend development |
| Database | SQLite | Local data persistence |
| Blockchain | GolemDB | Distributed storage |
| AI/ML | Ollama | Local LLM processing |
| Price Data | RedStone | Oracle service |
| Email | Resend | Email delivery |
| Async | asyncio | Concurrent operations |
| HTTP Client | aiohttp | Async HTTP requests |

### Frontend Technologies

| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | React 18+ | UI framework |
| Build Tool | Vite | Fast development builds |
| Styling | Tailwind CSS | Utility-first CSS |
| Routing | React Router | SPA navigation |
| Icons | Lucide React | Icon library |
| State | React Hooks | State management |
| WebSocket | Native WS | Real-time communication |

## Design Patterns

### 1. **Repository Pattern**
```python
class AlertRepository:
    async def create(self, alert: Alert) -> Alert
    async def get(self, alert_id: str) -> Alert
    async def update(self, alert: Alert) -> Alert
    async def delete(self, alert_id: str) -> bool
```

### 2. **Service Layer Pattern**
```python
class AlertService:
    def __init__(self, repository: AlertRepository):
        self.repository = repository
    
    async def create_alert(self, params: dict) -> Alert:
        # Business logic here
        return await self.repository.create(alert)
```

### 3. **Observer Pattern (Alert Engine)**
```python
class AlertEngine:
    def __init__(self):
        self.observers = []
    
    def attach(self, observer: AlertObserver):
        self.observers.append(observer)
    
    async def notify(self, alert: Alert):
        for observer in self.observers:
            await observer.update(alert)
```

### 4. **Factory Pattern (Notification Channels)**
```python
class NotificationFactory:
    @staticmethod
    def create_channel(channel_type: str) -> NotificationChannel:
        if channel_type == "email":
            return EmailChannel()
        elif channel_type == "websocket":
            return WebSocketChannel()
        # ... more channels
```

### 5. **Singleton Pattern (Database Connection)**
```python
class Database:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

## Security Architecture

### Authentication & Authorization
- **User Identification**: Simple user_id system (upgradeable to JWT)
- **API Key Management**: Secure storage in environment variables
- **Session Management**: WebSocket session tracking

### Data Security
- **Encryption at Rest**: Sensitive data encrypted in database
- **Encryption in Transit**: HTTPS for all API communications
- **Blockchain Security**: Immutable audit trails
- **Private Key Protection**: Secure key storage for GolemDB

### API Security
- **Rate Limiting**: Prevent abuse and DDoS
- **Input Validation**: Comprehensive request validation
- **CORS Policy**: Restricted origin access
- **Error Handling**: Secure error messages (no stack traces)

### Best Practices
```python
# Environment variable usage
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")

# Input sanitization
def sanitize_input(user_input: str) -> str:
    return bleach.clean(user_input)

# Secure error handling
try:
    # ... operation
except Exception as e:
    logger.error(f"Operation failed: {e}")
    return {"error": "An error occurred"}
```

## Scalability Considerations

### Horizontal Scaling

#### 1. **Stateless Services**
- All services designed to be stateless
- Session data stored in shared cache
- No local file dependencies

#### 2. **Load Balancing**
```nginx
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}
```

#### 3. **Database Scaling**
- Read replicas for query distribution
- Write master for data consistency
- GolemDB for distributed storage

### Vertical Scaling

#### 1. **Async Operations**
```python
async def process_alerts():
    tasks = [process_alert(a) for a in alerts]
    await asyncio.gather(*tasks)
```

#### 2. **Connection Pooling**
```python
async def create_pool():
    return await aiosqlite.create_pool(
        database="tokenTalk.db",
        max_connections=20
    )
```

#### 3. **Caching Strategy**
```python
@cache(ttl=60)  # Cache for 60 seconds
async def get_price(symbol: str):
    return await fetch_from_redstone(symbol)
```

### Performance Optimization

#### 1. **Database Optimization**
- Indexed columns for frequent queries
- Batch operations for bulk updates
- Query optimization and analysis

#### 2. **API Optimization**
- Response compression
- Pagination for large datasets
- Field filtering in responses

#### 3. **Frontend Optimization**
- Code splitting and lazy loading
- Asset optimization and CDN
- Service worker for offline support

## Deployment Architecture

### Development Environment
```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  backend:
    build: ./server
    environment:
      - DEBUG=True
      - GOLEMDB_MOCK_MODE=True
    volumes:
      - ./server:/app
    ports:
      - "8000:8000"
  
  frontend:
    build: ./client
    environment:
      - NODE_ENV=development
    volumes:
      - ./client:/app
    ports:
      - "5173:5173"
```

### Production Environment
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  backend:
    image: tokentalk/backend:latest
    environment:
      - DEBUG=False
      - GOLEMDB_MOCK_MODE=False
    deploy:
      replicas: 3
      restart_policy:
        condition: on-failure
  
  frontend:
    image: tokentalk/frontend:latest
    deploy:
      replicas: 2
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

### CI/CD Pipeline
```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          python -m pytest server/tests/
          npm test --prefix client
  
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          docker build -t tokentalk/backend ./server
          docker push tokentalk/backend
          kubectl apply -f k8s/
```

### Monitoring & Observability

#### 1. **Logging**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
```

#### 2. **Metrics Collection**
```python
from prometheus_client import Counter, Histogram

alert_counter = Counter('alerts_triggered', 'Number of alerts triggered')
response_time = Histogram('response_time_seconds', 'Response time')
```

#### 3. **Health Checks**
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "database": await check_database(),
            "golemdb": await check_golemdb(),
            "redstone": await check_redstone()
        }
    }
```

## Database Schema

### SQLite Schema
```sql
-- Users table
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    preferences JSON
);

-- Alerts table
CREATE TABLE alerts (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    symbol TEXT NOT NULL,
    condition TEXT NOT NULL,
    target_price REAL NOT NULL,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    triggered_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Price history table
CREATE TABLE price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    price REAL NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol_timestamp (symbol, timestamp)
);

-- Notifications table
CREATE TABLE notifications (
    id TEXT PRIMARY KEY,
    alert_id TEXT NOT NULL,
    channel TEXT NOT NULL,
    status TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (alert_id) REFERENCES alerts(id)
);
```

### GolemDB Schema
```json
{
  "user_profile": {
    "user_id": "string",
    "email": "string",
    "preferences": {
      "notification_channels": ["email", "websocket"],
      "currency": "USD",
      "timezone": "UTC"
    },
    "alerts": [
      {
        "id": "string",
        "symbol": "string",
        "condition": "string",
        "target_price": "number"
      }
    ],
    "metadata": {
      "created_at": "timestamp",
      "updated_at": "timestamp",
      "sync_version": "number"
    }
  }
}
```

## Future Architecture Enhancements

### Planned Improvements

1. **Microservices Migration**
   - Separate services into independent containers
   - Service mesh implementation (Istio/Linkerd)
   - Independent scaling and deployment

2. **Message Queue Integration**
   - RabbitMQ/Kafka for async processing
   - Event sourcing for audit trails
   - CQRS pattern implementation

3. **Advanced Caching**
   - Redis for distributed caching
   - Cache invalidation strategies
   - Edge caching with CDN

4. **Machine Learning Pipeline**
   - Price prediction models
   - Alert pattern recognition
   - User behavior analysis

5. **Enhanced Security**
   - OAuth 2.0/JWT authentication
   - API Gateway with Kong/Traefik
   - Web Application Firewall (WAF)

6. **Observability Stack**
   - Prometheus for metrics
   - Grafana for visualization
   - ELK stack for log aggregation
   - Jaeger for distributed tracing

## Conclusion

The tokenTalk architecture is designed to be modular, scalable, and maintainable. The use of modern patterns and technologies ensures that the system can handle growth while maintaining performance and reliability. The hybrid approach of combining traditional databases with blockchain storage provides both performance and security benefits, while the microservice-oriented design allows for independent scaling and development of components.
