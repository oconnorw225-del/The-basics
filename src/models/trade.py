"""
Trade model - Data structure for trading operations
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

class TradeType(Enum):
    BUY = "buy"
    SELL = "sell"

class TradeStatus(Enum):
    PENDING = "pending"
    EXECUTED = "executed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"

@dataclass
class Trade:
    """Trade data model"""
    pair: str
    trade_type: TradeType
    amount: float
    price: Optional[float] = None
    order_type: OrderType = OrderType.MARKET
    status: TradeStatus = TradeStatus.PENDING
    timestamp: datetime = None
    trade_id: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self):
        return {
            "trade_id": self.trade_id,
            "pair": self.pair,
            "type": self.trade_type.value,
            "amount": self.amount,
            "price": self.price,
            "order_type": self.order_type.value,
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
        }

@dataclass
class Position:
    """Trading position data model"""
    symbol: str
    amount: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    realized_pnl: float = 0.0
    
    def update_price(self, new_price: float):
        self.current_price = new_price
        self.unrealized_pnl = (new_price - self.entry_price) * self.amount
    
    def to_dict(self):
        return {
            "symbol": self.symbol,
            "amount": self.amount,
            "entry_price": self.entry_price,
            "current_price": self.current_price,
            "unrealized_pnl": self.unrealized_pnl,
            "realized_pnl": self.realized_pnl,
        }
