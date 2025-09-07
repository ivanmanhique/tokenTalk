# 🚀 tokenTalk

**AI-powered cryptocurrency price alerts with blockchain-secured user data**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)

## 📋 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [API Documentation](#api-documentation)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

tokenTalk is a sophisticated cryptocurrency monitoring platform that combines real-time price tracking with AI-powered natural language processing to create intelligent price alerts. The platform leverages blockchain technology through GolemDB for secure, immutable user data storage and features an enhanced notification system with personalized insights.

### Key Highlights
- **Natural Language Alert Creation**: Create alerts using plain English like "Tell me when Bitcoin drops below $30,000"
- **Blockchain-Secured Data**: User profiles and preferences stored on the blockchain via GolemDB
- **Real-time Monitoring**: Continuous price tracking with WebSocket notifications
- **AI-Powered Analysis**: Intelligent alert parsing and personalized notification insights
- **Multi-Channel Notifications**: Support for WebSocket, email (via Resend), and in-app notifications

## ✨ Features

### Core Features
- 📊 **Real-time Price Monitoring**: Track cryptocurrency prices using RedStone oracle integration
- 🤖 **AI Natural Language Processing**: Create alerts using conversational language
- 🔗 **Blockchain Integration**: Secure user data storage with GolemDB
- 📧 **Email Notifications**: Alert delivery via Resend email service
- 🔌 **WebSocket Support**: Real-time bidirectional communication
- 📈 **User Analytics**: Track alert performance and user engagement
- 🎨 **Modern UI**: Responsive React frontend with Tailwind CSS

### Enhanced Features
- 🧠 **Personalized Notifications**: AI-driven insights based on user behavior
- 📝 **Immutable Audit Trails**: Blockchain-backed transaction history
- 🔄 **Cross-Platform Sync**: Seamless data synchronization across devices
- 🛡️ **Secure Authentication**: User management with encrypted credentials
- 📊 **Analytics Dashboard**: Comprehensive monitoring and statistics

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (React)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │Dashboard │  │  Alerts  │  │   Chat   │  │  Profile │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP/WebSocket
┌─────────────────────────▼───────────────────────────────────┐
│                    Backend (FastAPI)                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    API Layer                          │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │  │
│  │  │  Alerts  │  │  Prices  │  │   Chat   │          │  │
│  │  └──────────┘  └──────────┘  └──────────┘          │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                 Service Layer                         │  │
│  │  ┌────────────┐  ┌─────────────┐  ┌──────────────┐ │  │
│  │  │Alert Engine│  │NLP Service  │  │Notification  │ │  │
│  │  └────────────┘  └─────────────┘  └──────────────┘ │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                  Data Layer                           │  │
│  │  ┌────────────┐  ┌─────────────┐  ┌──────────────┐ │  │
│  │  │  SQLite    │  │  GolemDB    │  │  RedStone    │ │  │
│  │  └────────────┘  └─────────────┘  └──────────────┘ │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.8+)
- **Database**: SQLite + GolemDB (blockchain storage)
- **AI/ML**: Ollama (local LLM) with optional cloud API support
- **Price Oracle**: RedStone Finance API
- **Email Service**: Resend
- **WebSocket**: Native FastAPI WebSocket support
- **Async**: asyncio, aiohttp

### Frontend
- **Framework**: React 18+ with Vite
- **Routing**: React Router v6
- **Styling**: Tailwind CSS v4
- **Icons**: Lucide React
- **State Management**: React Hooks

### Infrastructure
- **Blockchain**: Golem Network (via GolemDB)
- **Container**: Docker support (optional)
- **Process Manager**: PM2 (recommended for production)

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Node.js 16+ and npm/yarn
- Ollama (for local AI) or API keys for cloud services
- Git

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/ivanmanhique/tokenTalk.git
cd tokenTalk
```

2. **Backend Setup**
```bash
cd server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your configuration

# Start the server
python main.py
```

3. **Frontend Setup**
```bash
cd ../client

# Install dependencies
npm install

# Start development server
npm run dev
```

4. **Access the application**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 📚 API Documentation

### Main Endpoints

#### Health Check
```http
GET /health
```

#### Price Monitoring
```http
GET /api/prices/?symbols=BTC,ETH
GET /api/prices/history?symbol=BTC&interval=1h
```

#### Alert Management
```http
GET /api/alerts/
POST /api/alerts/
DELETE /api/alerts/{alert_id}
```

#### Natural Language Chat
```http
POST /api/chat/
{
  "message": "Alert me when Bitcoin drops below $30,000",
  "user_id": "user123"
}
```

#### WebSocket Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws?user_id=user123');
```

For detailed API documentation, visit http://localhost:8000/docs when the server is running.

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the server directory:

```env
# Ollama Configuration (for local AI)
OLLAMA_URL=http://localhost:11434

# Optional Cloud API Keys
USE_CLOUD_API=False
CLAUDE_API_KEY=your_claude_key_here
OPENAI_API_KEY=your_openai_key_here

# Email Notifications (Resend)
RESEND_API_KEY=your_resend_key_here
FROM_EMAIL=notifications@yourdomain.com
ENABLE_EMAIL_NOTIFICATIONS=True

# GolemDB Configuration
GOLEMDB_MOCK_MODE=True  # Set to False for blockchain mode
GOLEMDB_PRIVATE_KEY=your_ethereum_private_key
GOLEMDB_RPC_URL=https://polygon-mumbai.g.alchemy.com/v2/your_key

# Debug Mode
DEBUG=True
```

## 🧪 Testing

### Run Backend Tests
```bash
cd server
python -m pytest tests/
```

### Run Frontend Tests
```bash
cd client
npm test
```

## 📁 Project Structure

```
tokenTalk/
├── client/                 # React frontend
│   ├── src/
│   │   ├── Dashboard/     # Dashboard components
│   │   ├── LandingPage/   # Landing page
│   │   ├── assets/        # Static assets
│   │   └── App.jsx        # Main app component
│   └── package.json
├── server/                 # FastAPI backend
│   ├── api/               # API endpoints
│   │   ├── alerts.py
│   │   ├── chat.py
│   │   ├── prices.py
│   │   └── users.py
│   ├── services/          # Business logic
│   │   ├── alert_engine.py
│   │   ├── nlp_service.py
│   │   ├── golemdb_service.py
│   │   └── notification_service.py
│   ├── tests/             # Test files
│   ├── main.py            # Application entry point
│   ├── config.py          # Configuration
│   ├── database.py        # Database models
│   └── requirements.txt
├── docs/                  # Documentation
└── README.md
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use ESLint configuration for JavaScript/React
- Write tests for new features
- Update documentation for API changes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [RedStone Finance](https://redstone.finance/) for price oracle services
- [Golem Network](https://www.golem.network/) for blockchain infrastructure
- [Ollama](https://ollama.ai/) for local LLM capabilities
- [Resend](https://resend.com/) for email delivery services

## 📞 Contact

- **Project Link**: [https://github.com/ivanmanhique/tokenTalk](https://github.com/ivanmanhique/tokenTalk)
- **Issues**: [https://github.com/ivanmanhique/tokenTalk/issues](https://github.com/ivanmanhique/tokenTalk/issues)

---

<p align="center">Built with ❤️ by the tokenTalk team</p>
