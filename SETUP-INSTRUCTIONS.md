# Setup Instructions

Complete setup guide for the NDAX Quantum Engine trading system.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** 18 or higher ([Download](https://nodejs.org/))
- **Python** 3.9 or higher ([Download](https://python.org/))
- **Git** ([Download](https://git-scm.com/))
- **npm** (comes with Node.js)

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/oconnorw225-del/The-basics.git
cd The-basics
```

### 2. Run Setup Script

```bash
./setup.sh
```

This will:
- Install Node.js dependencies
- Create directory structure
- Generate `.env` configuration file
- Set up development environment

### 3. Install Python Dependencies (Optional)

If you want to use the Python backend:

```bash
pip install fastapi uvicorn pydantic python-dotenv
```

Or using requirements.txt:

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Edit the `.env` file created by setup:

```env
# Trading Mode
TRADING_MODE=paper  # Start with paper trading!
AUTO_START=false
MAX_TRADES=5
RISK_LEVEL=low

# API Keys (optional for paper trading)
# NDAX_API_KEY=your_api_key_here
# NDAX_API_SECRET=your_api_secret_here
```

### 5. Start Development

#### Option A: Start Everything
```bash
./start.sh
```

#### Option B: Start Components Separately

**Frontend (React + Vite):**
```bash
npm run dev
```
Visit: http://localhost:5173

**Backend (Python FastAPI):**
```bash
python3 backend/server.py
```
Visit: http://localhost:8000

**Node.js Server:**
```bash
npm start
```
Visit: http://localhost:3000

**Trading Bot:**
```bash
node bot.js
```
Status: http://localhost:9000/status

## Detailed Setup

### Frontend Development

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

3. **Build for production:**
   ```bash
   npm run build
   ```

4. **Preview production build:**
   ```bash
   npm run preview
   ```

### Backend Development

1. **Python dependencies:**
   ```bash
   pip install fastapi uvicorn pydantic python-dotenv
   ```

2. **Start backend:**
   ```bash
   python3 backend/server.py
   ```

3. **API documentation:**
   Visit http://localhost:8000/docs for interactive API documentation

### Trading Bot

1. **Configure bot settings in `.env`:**
   ```env
   BOT_PORT=9000
   TRADING_MODE=paper
   AUTO_START=false
   ```

2. **Start the bot:**
   ```bash
   node bot.js
   ```

3. **Check bot status:**
   ```bash
   curl http://localhost:9000/status
   ```

## Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Node.js Configuration
NODE_ENV=development
PORT=3000

# Python Backend
PYTHON_PORT=8000

# Trading Configuration
TRADING_MODE=paper
AUTO_START=false
MAX_TRADES=5
RISK_LEVEL=low

# Bot Configuration
BOT_PORT=9000

# Frontend API URL
VITE_API_URL=http://localhost:8000

# Optional: NDAX API Credentials
# NDAX_API_KEY=
# NDAX_API_SECRET=
```

### Trading Modes

- **Paper Trading** (Recommended for testing)
  - No real money
  - Simulated market data
  - Safe to experiment
  - Default mode

- **Live Trading** (Use with caution)
  - Real money
  - Real market data
  - Requires API keys
  - Monitor carefully

## Deployment

### AWS

1. Configure GitHub Secrets with AWS credentials
2. Push to repository
3. GitHub Actions automatically deploys to AWS

See [`DEPLOYMENT.md`](DEPLOYMENT.md) for complete AWS deployment instructions.

### Docker

```bash
docker build -t ndax-quantum-engine .
docker run -p 3000:3000 ndax-quantum-engine
```

### Manual Deployment

1. Build frontend:
   ```bash
   npm run build
   ```

2. Start production server:
   ```bash
   NODE_ENV=production npm start
   ```

## Testing

### Run Tests
```bash
npm test
```

### Lint Code
```bash
npm run lint
```

### Type Checking
```bash
npm run type-check
```

## Troubleshooting

### Port Already in Use

If ports are already in use, change them in `.env`:

```env
PORT=3001
PYTHON_PORT=8001
BOT_PORT=9001
```

### Dependencies Issues

Clear and reinstall:
```bash
rm -rf node_modules package-lock.json
npm install
```

### Python Module Not Found

Install requirements:
```bash
pip install -r requirements.txt
```

### Build Errors

Clear build cache:
```bash
rm -rf dist .vite
npm run build
```

## Development Workflow

1. **Make changes** to source code
2. **Test locally** with `npm run dev`
3. **Lint code** with `npm run lint`
4. **Build** with `npm run build`
5. **Commit** changes
6. **Push** to GitHub
7. **Deploy** automatically (if configured)

## Getting Help

- Check [QUICK_START.md](QUICK_START.md) for quick reference
- Review [CHANGELOG.md](CHANGELOG.md) for recent changes
- See [SECURITY.md](SECURITY.md) for security guidelines
- Open an issue on GitHub for support

## Next Steps

After setup:

1. ✅ Explore the dashboard at http://localhost:5173
2. ✅ Check API docs at http://localhost:8000/docs
3. ✅ Review trading settings in `.env`
4. ✅ Test with paper trading mode
5. ✅ Read the documentation
6. ✅ Start building!

---

**Ready to trade!** 🚀
