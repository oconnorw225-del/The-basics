"""
API endpoints for autonomous trading and solvency monitoring.
Provides REST API interface for the autonomous trading and solvency features.
"""

from typing import Dict, Optional
from datetime import datetime


class TradingAPI:
    """API wrapper for autonomous trading functionality."""
    
    def __init__(self):
        """Initialize the trading API."""
        self.autonomous_trader = None
        self.active_sessions = {}
        
    def create_session(self, config: Dict) -> Dict:
        """
        Create a new autonomous trading session.
        
        Args:
            config: Configuration for the trading session
            
        Returns:
            Session information
        """
        from backend.autonomous_trading import create_autonomous_trader
        
        session_id = f"session_{datetime.now().timestamp()}"
        trader = create_autonomous_trader(config)
        
        self.active_sessions[session_id] = trader
        
        return {
            "session_id": session_id,
            "status": "created",
            "config": config,
            "timestamp": datetime.now().isoformat()
        }
    
    def activate_trading(self, session_id: str) -> Dict:
        """
        Activate autonomous trading for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Activation result
        """
        if session_id not in self.active_sessions:
            return {"status": "error", "message": "Session not found"}
            
        trader = self.active_sessions[session_id]
        trader.activate()
        
        return {
            "session_id": session_id,
            "status": "activated",
            "timestamp": datetime.now().isoformat()
        }
    
    def deactivate_trading(self, session_id: str) -> Dict:
        """
        Deactivate autonomous trading for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Deactivation result
        """
        if session_id not in self.active_sessions:
            return {"status": "error", "message": "Session not found"}
            
        trader = self.active_sessions[session_id]
        trader.deactivate()
        
        return {
            "session_id": session_id,
            "status": "deactivated",
            "timestamp": datetime.now().isoformat()
        }
    
    def analyze_market(self, session_id: str, market_data: Dict) -> Dict:
        """
        Analyze market data using autonomous trader.
        
        Args:
            session_id: Session identifier
            market_data: Market data to analyze
            
        Returns:
            Analysis result
        """
        if session_id not in self.active_sessions:
            return {"status": "error", "message": "Session not found"}
            
        trader = self.active_sessions[session_id]
        signal = trader.analyze_opportunity(market_data)
        
        return {
            "session_id": session_id,
            "signal": signal,
            "timestamp": datetime.now().isoformat()
        }
    
    def execute_signal(self, session_id: str, signal: Dict) -> Dict:
        """
        Execute a trading signal.
        
        Args:
            session_id: Session identifier
            signal: Trading signal to execute
            
        Returns:
            Execution result
        """
        if session_id not in self.active_sessions:
            return {"status": "error", "message": "Session not found"}
            
        trader = self.active_sessions[session_id]
        result = trader.execute_trade(signal)
        
        return result
    
    def get_session_status(self, session_id: str) -> Dict:
        """
        Get status of a trading session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session status
        """
        if session_id not in self.active_sessions:
            return {"status": "error", "message": "Session not found"}
            
        trader = self.active_sessions[session_id]
        status = trader.get_status()
        
        return {
            "session_id": session_id,
            "trader_status": status,
            "timestamp": datetime.now().isoformat()
        }


class SolvencyAPI:
    """API wrapper for solvency monitoring functionality."""
    
    def __init__(self):
        """Initialize the solvency API."""
        self.monitor = None
        
    def initialize_monitor(self, config: Optional[Dict] = None) -> Dict:
        """
        Initialize the solvency monitor.
        
        Args:
            config: Optional configuration
            
        Returns:
            Initialization result
        """
        from backend.solvency_monitor import create_solvency_monitor
        
        self.monitor = create_solvency_monitor(config)
        
        return {
            "status": "initialized",
            "config": config or "default",
            "timestamp": datetime.now().isoformat()
        }
    
    def check_account_solvency(self, account_data: Dict) -> Dict:
        """
        Check solvency of an account.
        
        Args:
            account_data: Account financial data
            
        Returns:
            Solvency assessment
        """
        if not self.monitor:
            from backend.solvency_monitor import create_solvency_monitor
            self.monitor = create_solvency_monitor()
            
        assessment = self.monitor.check_solvency(account_data)
        
        return assessment
    
    def monitor_portfolio_solvency(self, portfolio_data: Dict) -> Dict:
        """
        Monitor solvency across a portfolio.
        
        Args:
            portfolio_data: Portfolio data
            
        Returns:
            Portfolio solvency assessment
        """
        if not self.monitor:
            from backend.solvency_monitor import create_solvency_monitor
            self.monitor = create_solvency_monitor()
            
        assessment = self.monitor.monitor_portfolio(portfolio_data)
        
        return assessment
    
    def get_alerts(self, limit: Optional[int] = 10) -> Dict:
        """
        Get recent solvency alerts.
        
        Args:
            limit: Maximum number of alerts
            
        Returns:
            Alerts list
        """
        if not self.monitor:
            return {"alerts": [], "message": "Monitor not initialized"}
            
        alerts = self.monitor.get_alerts(limit)
        
        return {
            "alerts": alerts,
            "count": len(alerts),
            "timestamp": datetime.now().isoformat()
        }


# API instances
trading_api = TradingAPI()
solvency_api = SolvencyAPI()


# Endpoint functions
def autonomous_trading_endpoints():
    """Get autonomous trading API endpoints description."""
    return {
        "create_session": "POST /api/autonomous/session",
        "activate_trading": "POST /api/autonomous/activate/{session_id}",
        "deactivate_trading": "POST /api/autonomous/deactivate/{session_id}",
        "analyze_market": "POST /api/autonomous/analyze/{session_id}",
        "execute_signal": "POST /api/autonomous/execute/{session_id}",
        "get_status": "GET /api/autonomous/status/{session_id}"
    }


def solvency_monitoring_endpoints():
    """Get solvency monitoring API endpoints description."""
    return {
        "initialize_monitor": "POST /api/solvency/initialize",
        "check_account": "POST /api/solvency/check/account",
        "monitor_portfolio": "POST /api/solvency/check/portfolio",
        "get_alerts": "GET /api/solvency/alerts"
    }
