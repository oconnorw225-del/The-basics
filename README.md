# NDAX Quantum Trading Engine 🚀

Advanced autonomous trading system combining quantum-inspired algorithms with modern web technologies.

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/oconnorw225-del/The-basics)

## 🌟 Features

### Trading System
- **Quantum-Inspired Algorithms** - Advanced trading strategies using quantum computing concepts
- **Autonomous Trading** - Fully automated trading with configurable risk levels
- **Paper Trading Mode** - Safe testing environment with simulated trades
- **Live Trading Mode** - Production-ready real trading capabilities
- **Real-time Dashboard** - Monitor trades, metrics, and system health
- **Multi-Strategy Support** - Run multiple trading strategies simultaneously

### Technology Stack
- **Frontend**: React 18 + Vite + React Router
- **Backend**: Python FastAPI + Node.js Express
- **Trading Bot**: Autonomous Node.js bot
- **Styling**: Modern CSS with dark theme
- **Deployment**: Railway, Docker, or custom hosting

### Security & Safety
- Paper trading by default (no real money at risk)
- Input validation on all endpoints
- Environment-based configuration
- Secure API key management
- Risk limits and safety controls

## 📦 Quick Start

### Prerequisites
- Node.js 18+ ([Download](https://nodejs.org/))
- Python 3.9+ ([Download](https://python.org/))
- Git ([Download](https://git-scm.com/))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/oconnorw225-del/The-basics.git
   cd The-basics
   ```

2. **Run setup**
   ```bash
   ./setup.sh
   ```

3. **Start the system**
   ```bash
   ./start.sh
   ```

4. **Access the application**
   - Frontend: http://localhost:5173
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Bot Status: http://localhost:9000/status

### Manual Setup

```bash
# Install Node.js dependencies
npm install

# Install Python dependencies
pip install fastapi uvicorn pydantic python-dotenv

# Start frontend dev server
npm run dev

# Start Python backend (in another terminal)
python3 backend/server.py

# Start trading bot (in another terminal)
node bot.js
```

## 📁 Project Structure

```
The-basics/
├── .github/              # GitHub Actions workflows
├── api/                  # API endpoints
├── automation/           # Automation scripts
├── backend/              # Python FastAPI backend
│   └── server.py        # Backend server
├── docs/                 # Documentation
├── frontend/             # Legacy frontend (if any)
├── paid-ai-bot/         # AI bot features
├── scripts/             # Utility scripts
├── src/                 # React application source
│   ├── autonomous/      # Autonomous trading components
│   ├── components/      # React UI components
│   ├── models/          # Data models
│   ├── quantum/         # Quantum trading algorithms
│   ├── routes/          # Application routes
│   ├── services/        # API services
│   ├── shared/          # Shared utilities
│   ├── styles/          # CSS styles
│   ├── utils/           # Utility functions
│   ├── App.jsx          # Main React app
│   ├── main.jsx         # React entry point
│   └── index.js         # Alternative entry
├── tests/               # Test suites
├── testing/             # Additional testing
├── bot.js               # Trading bot
├── index.html           # HTML entry point
├── package.json         # Node.js configuration
├── vite.config.js       # Vite configuration
├── setup.sh             # Setup script
├── start.sh             # Start script
├── unified_system.py    # Unified system (legacy)
└── README.md            # This file
```

## 🎮 Usage

### Trading Modes

**Paper Trading (Default)**
- Simulated trades with fake money
- Perfect for testing and learning
- No real risk
- No API keys required

```bash
# Set in .env
TRADING_MODE=paper
```

**Live Trading**
- Real trades with real money
- Requires NDAX API keys
- Use with caution
- Monitor actively

```bash
# Set in .env
TRADING_MODE=live
NDAX_API_KEY=your_key
NDAX_API_SECRET=your_secret
```

### Dashboard Features

1. **Overview**
   - Total trades
   - Active strategies
   - Profit/Loss
   - System health

2. **Quantum Engine**
   - Entanglement metrics
   - Superposition analysis
   - Optimization scores

3. **Autonomous Trading**
   - Real-time trade feed
   - Mode selection (paper/live)
   - Start/stop controls

## 🔧 Configuration

Create a `.env` file (or copy from `.env.example`):

```env
# Trading Configuration
TRADING_MODE=paper
AUTO_START=false
MAX_TRADES=5
RISK_LEVEL=low

# Ports
PORT=3000
PYTHON_PORT=8000
BOT_PORT=9000

# API
VITE_API_URL=http://localhost:8000

# Optional: NDAX API Credentials
# NDAX_API_KEY=your_api_key
# NDAX_API_SECRET=your_api_secret
```

## 🚀 Deployment

### Railway

1. Connect repository to Railway
2. Configure environment variables
3. Deploy automatically

### Docker

```bash
docker build -t ndax-quantum-engine .
docker run -p 3000:3000 ndax-quantum-engine
```

### Manual

```bash
npm run build
NODE_ENV=production npm start
```

## 📚 Documentation

- [Setup Instructions](SETUP-INSTRUCTIONS.md) - Detailed setup guide
- [Quick Start](QUICK_START.md) - Quick reference
- [Security Policy](SECURITY.md) - Security guidelines
- [Changelog](CHANGELOG.md) - Version history
- [Copilot Branches FAQ](docs/COPILOT_BRANCHES_FAQ.md) - Branch management

## 🧪 Development

### Available Scripts

```bash
npm run dev      # Start Vite dev server
npm run build    # Build for production
npm run preview  # Preview production build
npm start        # Start Node.js server
npm run unified  # Start Python unified system
npm run lint     # Lint code
npm test         # Run tests
```

### Testing

```bash
# Run all tests
npm test

# Lint code
npm run lint
```

## 🔒 Security

- Never commit API keys or secrets
- Use `.env` for local configuration
- Review [SECURITY.md](SECURITY.md) for best practices
- Start with paper trading
- Set conservative risk limits
- Monitor continuously

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- GitHub Issues: Report bugs or request features
- Documentation: Check the docs/ folder
- Security: See SECURITY.md for reporting vulnerabilities

## 🙏 Acknowledgments

Consolidated from:
- ndax-quantum-engine
- quantum-engine-dashboard
- shadowforge-ai-trader
- repository-web-app
- The-new-ones

---

**⚠️ Disclaimer**: This software is for educational purposes. Trading cryptocurrencies carries risk. Always start with paper trading and never trade more than you can afford to lose.

**Built with ❤️ for the trading community** 🚀
