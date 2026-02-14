# Bot Operations Guide

## Overview

This guide explains how the three trading bots work together under the coordination system.

## Bot Architecture

### Bot Hierarchy

```
Bot Coordinator (Master)
├── NDAX Bot (Primary Exchange)
├── Quantum Bot (Strategy Engine)
└── ShadowForge Bot (AI Trading)
```

### Bot Roles

#### NDAX Bot
- **Primary Function**: Direct trading on NDAX exchange
- **Startup Order**: 1st (Foundation)
- **Dependencies**: None
- **Responsibilities**:
  - Execute trades on NDAX exchange
  - Manage order book interactions
  - Handle account balance management
  - Provide trading execution services

#### Quantum Bot
- **Primary Function**: Quantum-enhanced trading strategies
- **Startup Order**: 2nd
- **Dependencies**: NDAX Bot (for execution)
- **Responsibilities**:
  - Generate trading signals using quantum algorithms
  - Analyze market microstructure
  - Optimize trade timing
  - Send trade requests to NDAX Bot

#### ShadowForge Bot
- **Primary Function**: AI-powered trading and arbitrage
- **Startup Order**: 3rd (Last)
- **Dependencies**: NDAX Bot, Quantum Bot
- **Responsibilities**:
  - Machine learning based predictions
  - Cross-exchange arbitrage detection
  - Sentiment analysis
  - Advanced pattern recognition

## Sequential Startup Process

### 1. Pre-Start Checks

Before starting any bot, the coordinator verifies:
- Configuration files are valid
- API credentials are present (if live trading)
- Network connectivity is available
- No active kill switch
- Sufficient system resources

### 2. NDAX Bot Startup

```python
# Coordinator initiates NDAX bot
coordinator.start_bot('ndax')

# Verification steps:
1. Load NDAX configuration
2. Initialize API connection
3. Verify account access
4. Test order placement (paper mode)
5. Set status to RUNNING
```

**Wait Time**: 5 seconds before next bot

### 3. Quantum Bot Startup

```python
# Start Quantum bot after NDAX is running
coordinator.start_bot('quantum')

# Verification steps:
1. Verify NDAX bot is healthy
2. Load quantum strategy configuration
3. Initialize strategy engine
4. Connect to NDAX bot API
5. Set status to RUNNING
```

**Wait Time**: 5 seconds before next bot

### 4. ShadowForge Bot Startup

```python
# Start ShadowForge bot last
coordinator.start_bot('shadowforge')

# Verification steps:
1. Verify NDAX and Quantum bots are healthy
2. Load AI models
3. Initialize arbitrage scanner
4. Connect to both previous bots
5. Set status to RUNNING
```

## Bot Communication

### Message Flow

```
ShadowForge Bot → Signal → Quantum Bot → Order → NDAX Bot → Exchange
```

### Communication Methods

#### 1. REST API
- Bot status queries
- Trading signals
- Order submissions

#### 2. WebSocket (Future)
- Real-time market data
- Order updates
- Position changes

#### 3. Shared State
- Redis cache (future)
- File-based state (current)

### Example Trade Flow

1. **Signal Generation**
   ```
   ShadowForge detects arbitrage opportunity
   → Sends signal to Quantum Bot
   ```

2. **Strategy Validation**
   ```
   Quantum Bot receives signal
   → Validates against strategy rules
   → Optimizes entry/exit timing
   → Forwards to NDAX Bot
   ```

3. **Execution**
   ```
   NDAX Bot receives order
   → Checks position limits
   → Validates against safety rules
   → Executes on exchange
   → Reports back to coordinators
   ```

## Bot Coordination

### Health Monitoring

The coordinator continuously monitors:
- Bot process status
- API response times
- Error rates
- Memory/CPU usage
- Trading performance

**Check Interval**: Every 60 seconds

### State Synchronization

Bots maintain synchronized state:
- Active positions
- Available capital
- Open orders
- Trading limits

### Conflict Prevention

The coordinator prevents:
- Duplicate orders on same asset
- Over-leveraging across bots
- Conflicting trades (long vs short)
- Limit violations

## Operating Modes

### Paper Trading Mode (Default)

```bash
TRADING_MODE=paper
```

- No real money at risk
- Full system functionality
- Simulated order execution
- Real market data
- Performance tracking

**Use For**: Testing, development, strategy validation

### Live Trading Mode

```bash
TRADING_MODE=live
```

- Real money trading
- Actual order execution
- Real profit/loss
- Full risk management

**Requirements**:
- Valid API credentials
- Verified exchange account
- Sufficient balance
- Completed testing in paper mode

## Safety Mechanisms

### 1. Position Limits

Each bot has individual position limits:
```json
{
  "ndax_bot": {
    "max_position_size": 1000,
    "max_concurrent_positions": 5
  }
}
```

### 2. Loss Limits

Daily loss limits per bot and globally:
```json
{
  "ndax_bot": {
    "max_daily_loss": 100
  },
  "global_limits": {
    "total_max_daily_loss": 400
  }
}
```

### 3. Trading Frequency

Limits on trade frequency:
```json
{
  "ndax_bot": {
    "max_daily_trades": 50
  }
}
```

### 4. Emergency Stop

Automatic stop conditions:
- Daily loss limit reached
- 5 consecutive losing trades
- 30% account equity drop
- 10 API errors in 15 minutes

## Manual Operations

### Starting Individual Bot

Via API:
```bash
curl -X POST http://localhost:8000/start \
  -H "Content-Type: application/json" \
  -d '{"bot": "ndax"}'
```

Via Dashboard:
1. Navigate to http://localhost:8080
2. Find bot card
3. Click "Start" button

### Stopping Individual Bot

Via API:
```bash
curl -X POST http://localhost:8000/stop \
  -H "Content-Type: application/json" \
  -d '{"bot": "ndax", "reason": "manual stop"}'
```

### Pausing Trading

Pause without full shutdown:
```bash
curl -X POST http://localhost:8000/pause \
  -H "Content-Type: application/json" \
  -d '{"bot": "all"}'
```

### Checking Status

```bash
curl http://localhost:8000/status
```

Response:
```json
{
  "kill_switch_active": false,
  "bots": {
    "ndax": {
      "status": "running",
      "health": 100,
      "error_count": 0
    }
  }
}
```

## Bot Handoff Mechanism

### Task Coordination

Bots can coordinate on multi-step tasks:

1. **Bot A** completes analysis
2. **Bot A** signals completion to coordinator
3. **Coordinator** verifies state
4. **Coordinator** activates **Bot B**
5. **Bot B** accesses shared state
6. **Bot B** continues workflow

### Shared State Storage

```python
# Bot A writes state
coordinator.set_shared_state('task_123', {
    'signal': 'BUY',
    'asset': 'BTC',
    'confidence': 0.85
})

# Bot B reads state
state = coordinator.get_shared_state('task_123')
```

### Handoff Example

```python
# ShadowForge identifies opportunity
shadowforge.analyze_market()
shadowforge.publish_signal({
    'type': 'arbitrage',
    'exchanges': ['NDAX', 'Binance'],
    'spread': 0.5,
    'asset': 'ETH'
})

# Quantum validates and optimizes
quantum.receive_signal(signal)
quantum.optimize_timing()
quantum.forward_to_executor()

# NDAX executes
ndax.receive_order(order)
ndax.execute_trade()
ndax.report_result()
```

## Performance Monitoring

### Key Metrics

1. **Bot Health**: 0-100 score based on:
   - Successful requests
   - Error rate
   - Response time
   - Resource usage

2. **Trading Performance**:
   - Win rate
   - Profit/Loss
   - Sharpe ratio
   - Max drawdown

3. **System Performance**:
   - Uptime
   - API latency
   - Trade execution time

### Accessing Metrics

Via Dashboard:
- http://localhost:8080

Via API:
```bash
curl http://localhost:8080/metrics
```

Via Logs:
```bash
tail -f logs/bot-coordinator.log
```

## Scaling Operations

### Adding New Bot

1. Create bot configuration in `config/api-endpoints.json`
2. Add limits to `config/bot-limits.json`
3. Update coordinator bot list
4. Restart coordinator

### Load Balancing

For high-frequency trading:
- Run multiple instances of same bot type
- Use load balancer
- Shared state via Redis
- Coordinated position tracking

## Best Practices

### DO
✅ Start bots in sequence
✅ Monitor health continuously  
✅ Use paper mode for testing
✅ Set conservative limits initially
✅ Keep kill switch enabled
✅ Review logs regularly
✅ Test recovery procedures

### DON'T
❌ Start all bots simultaneously
❌ Disable safety mechanisms
❌ Ignore error logs
❌ Run without monitoring
❌ Skip paper trading phase
❌ Use high leverage initially
❌ Disable kill switch

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed troubleshooting.

## Related Documentation

- [SETUP.md](SETUP.md) - Initial setup
- [SAFETY-PROTOCOLS.md](SAFETY-PROTOCOLS.md) - Safety procedures
- [API-REFERENCE.md](API-REFERENCE.md) - API documentation
- [RECOVERY-PROCEDURES.md](RECOVERY-PROCEDURES.md) - Recovery procedures
