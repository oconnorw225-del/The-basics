# Production Control Dashboard Documentation

## Overview

The Production Control Dashboard is a comprehensive React-based web interface that provides full control over all systems in The Basics repository. It features real-time monitoring, control panels for different services, and a modern, responsive design with dark mode support.

## Features

### System Status Panel
- **Real-time Health Monitoring**: Displays the status of API, Trading Bot, AI Bot, and AWS services
- **System Metrics**: Shows CPU usage, memory consumption, active processes, and system uptime
- **Auto-refresh**: Updates every 5 seconds to provide current system state

### Trading Control Panel
- **Start/Stop Trading Bot**: Control the trading bot operation
- **View Trading History**: Access historical trading data
- **Manual Trade Entry**: Execute manual trades with custom parameters
- **View Open Positions**: Monitor currently open trading positions
- **Emergency Stop**: Immediately halt all trading activities

### AI/Freelance Control Panel
- **Start/Stop AI Bot**: Control AI and freelance automation
- **View Active Tasks**: See currently running tasks
- **Submit New Task**: Add tasks to the queue for processing
- **View Task Queue**: Monitor pending tasks
- **Configure Providers**: Set up connections to MTurk, Appen, and other platforms

### AWS Deployment Panel
- **Deploy to AWS**: Trigger new deployments to AWS infrastructure
- **View Deployment Status**: Monitor ongoing and past deployments
- **Health Check AWS**: Verify AWS service health (ECS, RDS, S3)
- **View CloudWatch Logs**: Access AWS CloudWatch logs
- **Scale ECS Services**: Adjust ECS task counts
- **Rollback Deployment**: Revert to previous deployment

### System Management Panel
- **Start/Stop All Services**: Control all system services at once
- **Restart System**: Perform a complete system restart
- **View Logs**: Access system-wide logs
- **Health Check All**: Verify health of all services
- **Feature Toggles**: Enable/disable system features

### Monitoring Panel
- **View System Logs**: Access detailed system logs with filtering
- **Error Dashboard**: View and analyze system errors
- **Performance Metrics**: Monitor system performance indicators
- **Export Metrics**: Download metrics data in JSON or CSV format
- **Alert Configuration**: Set up and manage system alerts

### Configuration Panel
- **View Environment Variables**: Display current environment configuration
- **Update Credentials**: Securely update API credentials
- **Feature Flags Management**: Control feature availability
- **Test API Connections**: Verify connectivity to external services
- **Backup Configuration**: Create configuration backups

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.9+
- npm or yarn

### Installation

1. **Install Frontend Dependencies**
```bash
cd frontend
npm install
```

2. **Install Backend Dependencies**
```bash
pip install -r requirements.txt
```

### Running the Dashboard

1. **Start the Backend Server**
```bash
cd backend
python server.py
# Backend will start on http://localhost:8000
```

2. **Start the Frontend Development Server**
```bash
cd frontend
npm run dev
# Frontend will start on http://localhost:5173
```

3. **Access the Dashboard**
Open your browser and navigate to: http://localhost:5173

### Building for Production

```bash
cd frontend
npm run build
```

The built files will be in `dist/frontend/` directory.

## Architecture

### Frontend Stack
- **React 18.2**: UI framework
- **TypeScript**: Type-safe development
- **Vite**: Fast build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client for API calls
- **Socket.io-client**: WebSocket client for real-time updates
- **Lucide React**: Icon library
- **Recharts**: Charting library (for future enhancements)

### Backend Stack
- **FastAPI**: Modern Python web framework
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server

## API Endpoints

All API endpoints are prefixed with `/api/`

### Trading
- `POST /api/trading/start` - Start trading bot
- `POST /api/trading/stop` - Stop trading bot
- `GET /api/trading/positions` - Get open positions
- `POST /api/trading/execute` - Execute manual trade
- `GET /api/trading/history` - Get trading history
- `POST /api/trading/emergency-stop` - Emergency stop all trading

### AI/Freelance
- `POST /api/ai/start` - Start AI bot
- `POST /api/ai/stop` - Stop AI bot
- `GET /api/ai/tasks/active` - Get active tasks
- `POST /api/ai/tasks` - Submit new task
- `GET /api/ai/queue` - Get task queue
- `PUT /api/ai/providers` - Configure providers

### AWS
- `POST /api/aws/deploy` - Deploy to AWS
- `GET /api/aws/status` - Get deployment status
- `GET /api/aws/health` - AWS health check
- `GET /api/aws/logs` - Get CloudWatch logs
- `POST /api/aws/scale` - Scale ECS services
- `POST /api/aws/rollback` - Rollback deployment

### System Management
- `POST /api/system/start` - Start all services
- `POST /api/system/stop` - Stop all services
- `POST /api/system/restart` - Restart system
- `GET /api/system/health` - System health check
- `GET /api/system/logs` - Get system logs
- `GET /api/system/features` - Get feature flags
- `PUT /api/system/features/{name}` - Toggle feature

### Monitoring
- `GET /api/monitoring/metrics` - Get system metrics
- `GET /api/monitoring/errors` - Get errors
- `GET /api/monitoring/export` - Export metrics
- `GET /api/monitoring/alerts` - Get alert config
- `PUT /api/monitoring/alerts` - Update alert config

### Configuration
- `GET /api/config/env` - Get environment variables
- `PUT /api/config/credentials` - Update credentials
- `POST /api/config/test/{service}` - Test API connection
- `POST /api/config/backup` - Backup configuration

## UI Components

### Base Components (in `components/ui/`)
- **Button**: Configurable button with variants (primary, success, warning, danger, secondary)
- **Card**: Container component for panels
- **Badge**: Status indicator with color coding
- **Alert**: Message display with type-based styling

### Panel Components (in `components/`)
- **SystemStatusPanel**: Overall system status display
- **TradingControlPanel**: Trading operations control
- **AIControlPanel**: AI/Freelance operations control
- **AWSControlPanel**: AWS deployment control
- **SystemManagementPanel**: System-wide management
- **MonitoringPanel**: Monitoring and analytics
- **ConfigurationPanel**: System configuration

## Theming

The dashboard supports both light and dark modes:
- Toggle using the sun/moon icon in the header
- Preference is saved to localStorage
- Uses Tailwind's dark mode classes

### Color Scheme
- **Primary**: Blue (#3B82F6)
- **Success**: Green (#10B981)
- **Warning**: Yellow (#F59E0B)
- **Danger**: Red (#EF4444)
- **Dark**: Gray (#1F2937)

## Security Considerations

- Authentication tokens stored in localStorage
- API requests include Bearer token authentication
- Confirmation dialogs for destructive actions
- Role-based access control (admin vs user)
- Credentials are never displayed in plain text

## Future Enhancements

- [ ] Real-time WebSocket updates implementation
- [ ] Advanced charting with Recharts
- [ ] User authentication UI
- [ ] Advanced filtering for logs and metrics
- [ ] Export functionality for trading history
- [ ] Customizable dashboard layouts
- [ ] Keyboard shortcuts implementation
- [ ] Mobile app support
- [ ] Multi-language support

## Troubleshooting

### Frontend not connecting to backend
- Ensure backend is running on port 8000
- Check Vite proxy configuration in `vite.config.ts`
- Verify CORS settings in backend

### Build errors
- Clear node_modules: `rm -rf node_modules && npm install`
- Clear build cache: `rm -rf dist`
- Ensure TypeScript is properly configured

### WebSocket connection issues
- Verify WebSocket server is running
- Check firewall settings
- Ensure correct WebSocket URL in `websocket.ts`

## Contributing

When adding new features:
1. Create new components in appropriate directories
2. Update type definitions in `types/index.ts`
3. Add API endpoints to `services/api.ts`
4. Update backend `server.py` with corresponding routes
5. Document new features in this file

## License

MIT License - See LICENSE file for details

## Support

For issues or questions, please open an issue in the repository.
