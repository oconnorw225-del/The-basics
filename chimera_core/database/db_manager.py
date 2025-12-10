"""
Database Manager - Critical Gap #1
Production-grade database integration with PostgreSQL, MongoDB, and Redis
Provides persistent storage for all trading data, analytics, and system state
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
import json

try:
    import asyncpg
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    logging.warning("asyncpg not installed - PostgreSQL unavailable")

try:
    from motor import motor_asyncio
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    logging.warning("motor not installed - MongoDB unavailable")

try:
    import aioredis
    REDIS_AVAILABLE = True
except ImportError:
    try:
        import redis.asyncio as aioredis
        REDIS_AVAILABLE = True
    except ImportError:
        REDIS_AVAILABLE = False
        logging.warning("aioredis not installed - Redis unavailable")

logger = logging.getLogger(__name__)


# Default configuration
DATABASE_CONFIG = {
    'postgres': {
        'host': 'localhost',
        'port': 5432,
        'user': 'chimera',
        'password': 'changeme',
        'database': 'chimera_trading'
    },
    'mongodb': {
        'uri': 'mongodb://localhost:27017',
        'database': 'chimera_timeseries'
    },
    'redis': {
        'uri': 'redis://localhost:6379/0'
    }
}


class DatabaseManager:
    """Unified database manager for all data persistence needs"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.postgres_pool: Optional[Any] = None
        self.mongodb_client: Optional[Any] = None
        self.mongodb_db: Optional[Any] = None
        self.redis_client: Optional[Any] = None
        self.is_connected = False
        
    async def initialize(self):
        """Initialize all database connections"""
        logger.info("🔌 Initializing database connections...")
        
        # PostgreSQL for structured data (trades, positions, accounts)
        if POSTGRES_AVAILABLE:
            try:
                pg_config = self.config.get('postgres', {})
                
                # SECURITY: Validate password is set properly
                password = pg_config.get('password')
                if not password or password in ['changeme', 'password', 'test', 'demo']:
                    logger.error("❌ SECURITY: Database password not configured properly!")
                    logger.error("Set via environment: DATABASE_PASSWORD=<secure_password>")
                    raise ValueError(
                        "SECURITY: Database password must be set via environment variable. "
                        "Never use default passwords in production!"
                    )
                
                self.postgres_pool = await asyncpg.create_pool(
                    host=pg_config.get('host', 'localhost'),
                    port=pg_config.get('port', 5432),
                    user=pg_config.get('user', 'chimera'),
                    password=password,
                    database=pg_config.get('database', 'chimera_trading'),
                    min_size=5,
                    max_size=20
                )
                await self._create_postgres_schema()
                logger.info("✅ PostgreSQL connected")
            except ValueError as e:
                # Re-raise security errors
                raise e
            except Exception as e:
                logger.error(f"❌ PostgreSQL connection failed: {e}")
        
        # MongoDB for time-series and unstructured data
        if MONGODB_AVAILABLE:
            try:
                mongo_config = self.config.get('mongodb', {})
                self.mongodb_client = motor_asyncio.AsyncIOMotorClient(
                    mongo_config.get('uri', 'mongodb://localhost:27017')
                )
                self.mongodb_db = self.mongodb_client[
                    mongo_config.get('database', 'chimera_timeseries')
                ]
                # Test connection
                await self.mongodb_client.admin.command('ping')
                logger.info("✅ MongoDB connected")
            except Exception as e:
                logger.error(f"❌ MongoDB connection failed: {e}")
        
        # Redis for caching and real-time data
        if REDIS_AVAILABLE:
            try:
                redis_config = self.config.get('redis', {})
                self.redis_client = await aioredis.from_url(
                    redis_config.get('uri', 'redis://localhost:6379/0')
                )
                await self.redis_client.ping()
                logger.info("✅ Redis connected")
            except Exception as e:
                logger.error(f"❌ Redis connection failed: {e}")
        
        self.is_connected = True
        logger.info("✅ Database manager initialized")
    
    async def _create_postgres_schema(self):
        """Create database schema if not exists"""
        if not self.postgres_pool:
            return
        
        schema = """
        -- Trades table
        CREATE TABLE IF NOT EXISTS trades (
            id SERIAL PRIMARY KEY,
            trade_id VARCHAR(100) UNIQUE NOT NULL,
            exchange VARCHAR(50) NOT NULL,
            symbol VARCHAR(20) NOT NULL,
            side VARCHAR(10) NOT NULL,
            order_type VARCHAR(20) NOT NULL,
            quantity DECIMAL(20, 8) NOT NULL,
            price DECIMAL(20, 8) NOT NULL,
            cost DECIMAL(20, 8),
            status VARCHAR(20) NOT NULL,
            strategy VARCHAR(50),
            pnl DECIMAL(20, 8),
            fees DECIMAL(20, 8),
            timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
            metadata JSONB
        );
        
        -- Positions table
        CREATE TABLE IF NOT EXISTS positions (
            id SERIAL PRIMARY KEY,
            exchange VARCHAR(50) NOT NULL,
            symbol VARCHAR(20) NOT NULL,
            side VARCHAR(10) NOT NULL,
            quantity DECIMAL(20, 8) NOT NULL,
            entry_price DECIMAL(20, 8) NOT NULL,
            current_price DECIMAL(20, 8),
            unrealized_pnl DECIMAL(20, 8),
            opened_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
            UNIQUE(exchange, symbol, side)
        );
        
        -- Balances table
        CREATE TABLE IF NOT EXISTS balances (
            id SERIAL PRIMARY KEY,
            exchange VARCHAR(50) NOT NULL,
            currency VARCHAR(20) NOT NULL,
            total DECIMAL(20, 8) NOT NULL,
            available DECIMAL(20, 8) NOT NULL,
            locked DECIMAL(20, 8) NOT NULL,
            timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
            UNIQUE(exchange, currency)
        );
        
        -- Solvency checks table
        CREATE TABLE IF NOT EXISTS solvency_checks (
            id SERIAL PRIMARY KEY,
            total_assets DECIMAL(20, 8) NOT NULL,
            total_liabilities DECIMAL(20, 8) NOT NULL,
            net_worth DECIMAL(20, 8) NOT NULL,
            solvency_ratio DECIMAL(10, 6) NOT NULL,
            risk_level VARCHAR(20) NOT NULL,
            metadata JSONB,
            timestamp TIMESTAMP NOT NULL DEFAULT NOW()
        );
        
        -- System events table
        CREATE TABLE IF NOT EXISTS system_events (
            id SERIAL PRIMARY KEY,
            event_type VARCHAR(50) NOT NULL,
            component VARCHAR(100) NOT NULL,
            severity VARCHAR(20) NOT NULL,
            message TEXT NOT NULL,
            metadata JSONB,
            timestamp TIMESTAMP NOT NULL DEFAULT NOW()
        );
        
        -- Indexes for performance
        CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON trades(timestamp DESC);
        CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol, timestamp DESC);
        CREATE INDEX IF NOT EXISTS idx_trades_strategy ON trades(strategy, timestamp DESC);
        CREATE INDEX IF NOT EXISTS idx_events_component ON system_events(component, timestamp DESC);
        CREATE INDEX IF NOT EXISTS idx_solvency_timestamp ON solvency_checks(timestamp DESC);
        """
        
        async with self.postgres_pool.acquire() as conn:
            await conn.execute(schema)
        
        logger.info("✅ PostgreSQL schema created")
    
    # Trade Operations
    async def save_trade(self, trade: Dict[str, Any]):
        """Save trade to database"""
        if not self.postgres_pool:
            logger.warning("PostgreSQL not available - trade not saved")
            return
        
        async with self.postgres_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO trades 
                (trade_id, exchange, symbol, side, order_type, quantity, price, cost, status, strategy, pnl, fees, timestamp, metadata)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                ON CONFLICT (trade_id) DO UPDATE SET
                    status = EXCLUDED.status,
                    pnl = EXCLUDED.pnl,
                    metadata = EXCLUDED.metadata
            """,
                trade.get('trade_id', f"T{int(datetime.now().timestamp())}"),
                trade.get('exchange', 'unknown'),
                trade.get('symbol', ''),
                trade.get('side', ''),
                trade.get('order_type', 'market'),
                float(trade.get('quantity', 0)),
                float(trade.get('price', 0)),
                float(trade.get('cost', trade.get('quantity', 0) * trade.get('price', 0))),
                trade.get('status', 'unknown'),
                trade.get('strategy'),
                float(trade.get('pnl', 0)),
                float(trade.get('fees', 0)),
                trade.get('timestamp', datetime.now()),
                json.dumps(trade.get('metadata', {}))
            )
    
    async def get_trades(self, limit: int = 100, symbol: Optional[str] = None) -> List[Dict]:
        """Get recent trades"""
        if not self.postgres_pool:
            return []
        
        query = "SELECT * FROM trades"
        params = []
        
        if symbol:
            query += " WHERE symbol = $1"
            params.append(symbol)
        
        query += " ORDER BY timestamp DESC LIMIT " + str(limit)
        
        async with self.postgres_pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            return [dict(row) for row in rows]
    
    # Position Operations
    async def save_position(self, position: Dict[str, Any]):
        """Save or update position"""
        if not self.postgres_pool:
            return
        
        async with self.postgres_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO positions 
                (exchange, symbol, side, quantity, entry_price, current_price, unrealized_pnl, opened_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (exchange, symbol, side) DO UPDATE SET
                    quantity = EXCLUDED.quantity,
                    current_price = EXCLUDED.current_price,
                    unrealized_pnl = EXCLUDED.unrealized_pnl,
                    updated_at = EXCLUDED.updated_at
            """,
                position.get('exchange', ''),
                position.get('symbol', ''),
                position.get('side', ''),
                float(position.get('quantity', 0)),
                float(position.get('entry_price', 0)),
                float(position.get('current_price', 0)),
                float(position.get('unrealized_pnl', 0)),
                position.get('opened_at', datetime.now()),
                datetime.now()
            )
    
    async def get_positions(self) -> List[Dict]:
        """Get all open positions"""
        if not self.postgres_pool:
            return []
        
        async with self.postgres_pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM positions ORDER BY opened_at DESC")
            return [dict(row) for row in rows]
    
    # Balance Operations
    async def save_balance(self, balance: Dict[str, Any]):
        """Save balance snapshot"""
        if not self.postgres_pool:
            return
        
        async with self.postgres_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO balances (exchange, currency, total, available, locked, timestamp)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (exchange, currency) DO UPDATE SET
                    total = EXCLUDED.total,
                    available = EXCLUDED.available,
                    locked = EXCLUDED.locked,
                    timestamp = EXCLUDED.timestamp
            """,
                balance.get('exchange', ''),
                balance.get('currency', ''),
                float(balance.get('total', 0)),
                float(balance.get('available', 0)),
                float(balance.get('locked', 0)),
                datetime.now()
            )
    
    async def get_balances(self, exchange: Optional[str] = None) -> List[Dict]:
        """Get balances"""
        if not self.postgres_pool:
            return []
        
        query = "SELECT * FROM balances"
        params = []
        
        if exchange:
            query += " WHERE exchange = $1"
            params.append(exchange)
        
        async with self.postgres_pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            return [dict(row) for row in rows]
    
    # Solvency Operations
    async def save_solvency_check(self, solvency: Dict[str, Any]):
        """Save solvency check"""
        if not self.postgres_pool:
            return
        
        async with self.postgres_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO solvency_checks 
                (total_assets, total_liabilities, net_worth, solvency_ratio, risk_level, metadata, timestamp)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
                float(solvency.get('total_assets', 0)),
                float(solvency.get('total_liabilities', 0)),
                float(solvency.get('net_worth', 0)),
                float(solvency.get('solvency_ratio', 0)),
                solvency.get('risk_level', 'unknown'),
                json.dumps(solvency.get('metadata', {})),
                datetime.now()
            )
    
    # Market Data Operations (MongoDB for time-series)
    async def save_market_data(self, symbol: str, data: Dict[str, Any]):
        """Save market data to MongoDB"""
        if not self.mongodb_db:
            return
        
        collection = self.mongodb_db[f"market_{symbol.replace('/', '_')}"]
        document = {
            **data,
            'timestamp': datetime.now()
        }
        await collection.insert_one(document)
    
    async def get_market_data(self, symbol: str, limit: int = 100) -> List[Dict]:
        """Get market data from MongoDB"""
        if not self.mongodb_db:
            return []
        
        collection = self.mongodb_db[f"market_{symbol.replace('/', '_')}"]
        cursor = collection.find().sort('timestamp', -1).limit(limit)
        return await cursor.to_list(length=limit)
    
    # Cache Operations (Redis)
    async def cache_set(self, key: str, value: Any, ttl: int = 60):
        """Set cache value with TTL"""
        if not self.redis_client:
            return
        
        await self.redis_client.setex(
            key,
            ttl,
            json.dumps(value) if not isinstance(value, str) else value
        )
    
    async def cache_get(self, key: str) -> Optional[Any]:
        """Get cache value"""
        if not self.redis_client:
            return None
        
        value = await self.redis_client.get(key)
        if value:
            try:
                return json.loads(value)
            except:
                return value
        return None
    
    # Event Logging
    async def log_event(self, event_type: str, component: str, severity: str, message: str, metadata: Optional[Dict] = None):
        """Log system event"""
        if not self.postgres_pool:
            logger.info(f"[{severity}] {component}: {message}")
            return
        
        async with self.postgres_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO system_events (event_type, component, severity, message, metadata, timestamp)
                VALUES ($1, $2, $3, $4, $5, $6)
            """,
                event_type,
                component,
                severity,
                message,
                json.dumps(metadata or {}),
                datetime.now()
            )
    
    async def close(self):
        """Close all database connections"""
        logger.info("🔌 Closing database connections...")
        
        if self.postgres_pool:
            await self.postgres_pool.close()
        
        if self.mongodb_client:
            self.mongodb_client.close()
        
        if self.redis_client:
            await self.redis_client.close()
        
        self.is_connected = False
        logger.info("✅ Database connections closed")


# Convenience function
async def get_database() -> DatabaseManager:
    """Get initialized database manager"""
    db = DatabaseManager(DATABASE_CONFIG)
    await db.initialize()
    return db
