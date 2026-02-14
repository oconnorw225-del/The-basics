# Autonomous Bot Dashboard

Real-time monitoring and control dashboard for the autonomous bot system.

## 🏗️ Architecture

### Frontend
- **Framework:** Next.js 14 with React 18
- **Styling:** Tailwind CSS
- **Real-time:** WebSocket connection
- **TypeScript:** Full type safety

### Backend
- **Framework:** FastAPI
- **WebSocket:** Real-time updates every 5 seconds
- **API:** RESTful endpoints for bot control
- **Python:** 3.11+

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
# Navigate to backend directory
cd dashboard/backend

# Install dependencies
pip install -r requirements.txt

# Start the server
python main.py
```

The API will be available at:
- **API:** http://localhost:8000
- **Docs:** http://localhost:8000/docs
- **WebSocket:** ws://localhost:8000/ws

### Frontend Setup

```bash
# Navigate to frontend directory
cd dashboard/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The dashboard will be available at:
- **Dashboard:** http://localhost:3000

## 📡 API Endpoints

### Bots
- `GET /api/bots` - Get all bots
- `GET /api/bots/{bot_id}` - Get specific bot
- `POST /api/bots/{bot_id}/{action}` - Control bot (start/stop/restart)

### System Stats
- `GET /api/stats` - Get system statistics
- `GET /api/credentials` - Get credential pool status
- `GET /api/recovery` - Get asset recovery status
- `GET /api/notifications` - Get notification status

### WebSocket
- `WS /ws` - Real-time updates

## 🔄 WebSocket Messages

### Sent by Server
```json
{
  "type": "stats_update",
  "data": {
    "bots": {...},
    "credentials": {...},
    "recovery": {...},
    "notifications": {...}
  },
  "timestamp": "2024-01-01T00:00:00"
}
```

```json
{
  "type": "bot_status_update",
  "bot_id": "quantum_bot_1",
  "status": "active",
  "action": "start",
  "timestamp": "2024-01-01T00:00:00"
}
```

### Sent by Client
```json
{
  "type": "ping"
}
```

## 🎨 Component Structure

```
dashboard/frontend/src/
├── app/
│   ├── page.tsx          # Main dashboard page
│   ├── layout.tsx        # App layout
│   └── globals.css       # Global styles
├── components/
│   ├── BotGrid.tsx       # Grid layout for bots
│   ├── BotCard.tsx       # Individual bot card
│   └── bots/             # Auto-generated bot components
└── hooks/
    └── useWebSocket.ts   # WebSocket hook
```

## 🤖 Auto-Generated Components

Chimera V8 automatically generates React components for each discovered bot:

```typescript
// dashboard/frontend/src/components/bots/{bot_id}.tsx
export const BotComponent: React.FC<Props> = ({ botData, onAction }) => {
  // Auto-generated UI for specific bot
}
```

## 📊 Dashboard Features

1. **Real-Time Updates**
   - WebSocket connection for live data
   - Auto-refresh every 5 seconds
   - Connection status indicator

2. **Bot Grid**
   - Visual grid of all discovered bots
   - Color-coded by type
   - Status indicators
   - Control buttons (start/stop/restart)

3. **System Stats**
   - Total bots count
   - Credentials count
   - Recovery scans
   - Pending notifications

4. **Bot Cards**
   - Bot name and ID
   - Type badge
   - Status indicator
   - Capabilities list
   - File path
   - Action buttons

5. **System Information**
   - Email recipient (hardcoded)
   - Assets recovered
   - Credential requests
   - Notifications sent

## 🔧 Configuration

### Frontend

The frontend automatically connects to the backend API at `http://localhost:8000`. To change this, update:

```javascript
// dashboard/frontend/next.config.js
async rewrites() {
  return [
    {
      source: '/api/:path*',
      destination: 'http://your-backend:8000/api/:path*',
    },
  ];
}
```

### Backend

The backend can be configured via environment variables:

```bash
# API host and port
HOST=0.0.0.0
PORT=8000

# CORS origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## 🔒 Security

- **Email:** Hardcoded to `oconnorw225@gmail.com` - cannot be changed
- **CORS:** Configured for localhost only by default
- **Credentials:** Never exposed in API responses
- **WebSocket:** No authentication (local development only)

## 🚀 Production Deployment

### Backend

```bash
# Install dependencies
pip install -r requirements.txt

# Start with Gunicorn
gunicorn dashboard.backend.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Frontend

```bash
# Build for production
npm run build

# Start production server
npm start
```

Or deploy to Vercel/Netlify:
```bash
vercel deploy
```

## 📝 Development

### Hot Reload

Both frontend and backend support hot reload:

```bash
# Backend (auto-reload on file changes)
python main.py

# Frontend (auto-reload on file changes)
npm run dev
```

### Type Checking

```bash
# Frontend TypeScript check
npm run type-check

# Backend (using mypy)
mypy dashboard/backend/
```

## 🐛 Troubleshooting

### WebSocket Connection Failed
- Ensure backend is running on port 8000
- Check CORS configuration
- Verify WebSocket URL in frontend

### Bots Not Showing
- Run bot discovery: `python backend/chimera_dashboard_writer.py`
- Check bot registry: `python backend/bot_registry.py`
- Verify backend is connected to bot registry

### API Errors
- Check backend logs
- Verify Python dependencies installed
- Ensure backend modules are in Python path

## 📦 Dependencies

### Backend
- fastapi==0.109.1
- uvicorn[standard]==0.27.0
- websockets==12.0
- python-dotenv==1.0.0
- aiohttp==3.13.3

### Frontend
- next@14.1.0
- react@18.2.0
- socket.io-client@4.8.1
- lucide-react@0.561.0
- tailwindcss@4.1.18

## 🔗 Related

- **Backend System:** [../backend/](../backend/)
- **Bot Registry:** [../backend/bot_registry.py](../backend/bot_registry.py)
- **Email Notifier:** [../backend/email_notifier.py](../backend/email_notifier.py)
- **Complete Integration:** [../backend/complete_integration.py](../backend/complete_integration.py)
