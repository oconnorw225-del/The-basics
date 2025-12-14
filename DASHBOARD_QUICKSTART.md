# Production Control Dashboard - Quick Start Guide

## Overview

The Production Control Dashboard provides a centralized interface to manage all systems in The Basics repository including trading bots, AI/freelance automation, AWS deployments, and system monitoring.

## Quick Start

### 1. Start the Backend Server

```bash
cd backend
python server.py
```

The backend will start on `http://localhost:8000`
- API documentation available at: `http://localhost:8000/docs`

### 2. Start the Frontend Dashboard

```bash
cd frontend
npm install
npm run dev
```

The dashboard will be available at `http://localhost:5173`

### 3. Access the Dashboard

Open your browser and navigate to: http://localhost:5173

## Dashboard Features

### System Status Panel (Top)
Real-time monitoring of all services:
- ✅ API Service status
- ✅ Trading Bot status  
- ✅ AI Bot status
- ✅ AWS Services status
- 📊 CPU, Memory, Processes, Uptime metrics

### Trading Control
- **Start/Stop Trading Bot**: Toggle automated trading
- **Manual Trade Entry**: Execute manual trades with custom parameters
- **View Positions**: Monitor open trading positions
- **Trading History**: Access historical trade data
- **Emergency Stop**: Immediately halt all trading activities

### AI/Freelance Control
- **Start/Stop AI Bot**: Control AI automation
- **Submit Tasks**: Add new tasks to the queue
- **View Active Tasks**: Monitor running tasks
- **Task Queue**: View pending tasks
- **Configure Providers**: Set up MTurk, Appen, etc.

### AWS Deployment
- **Deploy**: Trigger new AWS deployments
- **Status**: Monitor deployment progress
- **Health Check**: Verify AWS service health
- **CloudWatch Logs**: Access AWS logs
- **Scale Services**: Adjust ECS task counts
- **Rollback**: Revert to previous deployment

### System Management
- **Start/Stop All Services**: Bulk service control
- **Restart System**: Full system restart
- **View Logs**: Access system-wide logs
- **Health Check**: Verify all service health
- **Feature Toggles**: Enable/disable features

### Monitoring
- **System Logs**: Detailed log viewing with filters
- **Error Dashboard**: Error tracking and analysis
- **Performance Metrics**: CPU, memory, process monitoring
- **Export Metrics**: Download data in JSON/CSV
- **Alert Configuration**: Set up system alerts

### Configuration
- **Environment Variables**: View current config
- **Update Credentials**: Securely manage API keys
- **Feature Flags**: Control feature availability
- **Test Connections**: Verify API connectivity
- **Backup Config**: Create configuration backups

## Using the Dashboard

### Making API Calls

All buttons in the dashboard trigger backend API calls:

1. **Click a control button** (e.g., "Start Trading Bot")
2. **Confirmation dialog** appears for destructive actions
3. **Action executes** and sends request to backend
4. **Success/Error alert** appears in the panel
5. **System status** updates automatically

### Dark Mode

Toggle dark mode using the sun/moon icon in the header. Your preference is saved automatically.

### Real-time Updates

The dashboard automatically:
- Updates system metrics every 5 seconds
- Refreshes service status continuously
- Shows real-time notifications for actions

## API Endpoints

### Trading
- `POST /api/trading/start` - Start trading bot
- `POST /api/trading/stop` - Stop trading bot
- `GET /api/trading/positions` - Get open positions
- `POST /api/trading/execute` - Execute trade
- `POST /api/trading/emergency-stop` - Emergency stop

### AI/Freelance
- `POST /api/ai/start` - Start AI bot
- `POST /api/ai/stop` - Stop AI bot
- `GET /api/ai/tasks/active` - Get active tasks
- `POST /api/ai/tasks` - Submit task
- `GET /api/ai/queue` - Get task queue

### AWS
- `POST /api/aws/deploy` - Deploy to AWS
- `GET /api/aws/status` - Get deployment status
- `GET /api/aws/health` - AWS health check
- `POST /api/aws/scale` - Scale ECS services

### System
- `POST /api/system/start` - Start all services
- `POST /api/system/stop` - Stop all services
- `POST /api/system/restart` - Restart system
- `GET /api/system/health` - Health check
- `GET /api/system/logs` - Get logs

### Monitoring
- `GET /api/monitoring/metrics` - Get system metrics
- `GET /api/monitoring/errors` - Get errors
- `GET /api/monitoring/export` - Export metrics

## Production Deployment

### Build the Frontend

```bash
cd frontend
npm run build
```

Built files will be in `dist/frontend/`

### Run Backend in Production

```bash
cd backend
python server.py
```

Or use a process manager like systemd or supervisor.

### Environment Variables

Set these environment variables for production:

```bash
export PYTHON_PORT=8000
export NODE_ENV=production
export API_URL=http://localhost:8000
```

## Troubleshooting

### Backend not starting
- Check Python version: `python --version` (requires 3.9+)
- Install dependencies: `pip install -r requirements.txt`
- Check port availability: `lsof -i :8000`

### Frontend not connecting
- Verify backend is running on port 8000
- Check proxy settings in `vite.config.ts`
- Clear browser cache and reload

### Build errors
- Clear node_modules: `rm -rf node_modules && npm install`
- Clear build cache: `rm -rf dist`
- Verify TypeScript: `npx tsc --version`

### API errors
- Check backend logs for errors
- Verify CORS settings allow frontend origin
- Test API endpoints with curl or Postman

## Security

- ✅ No known vulnerabilities in dependencies
- ✅ CodeQL security analysis passed
- ✅ Authentication support built-in (login required)
- ✅ Role-based access control ready
- ✅ Confirmation dialogs for destructive actions
- ✅ Credentials never logged or displayed

## Support

For issues or questions:
1. Check the full documentation: `frontend/README.md`
2. Review API docs: `http://localhost:8000/docs`
3. Open an issue in the repository

## Next Steps

1. ✅ Dashboard is ready to use
2. 🔄 Implement WebSocket for real-time updates
3. 🔄 Add user authentication UI
4. 🔄 Integrate with actual trading/AI systems
5. 🔄 Deploy to production environment

---

**Dashboard Version**: 1.0.0  
**Last Updated**: 2024-12-14
