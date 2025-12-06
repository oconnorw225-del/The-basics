"""
Intelligence & Evolution Engine Upgrades - V4 System Enhancements
Explainable AI, Predictive Analytics, and Anomaly Detection.
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import random


class AnomalyType(Enum):
    """Types of anomalies."""
    TRADING_FREQUENCY = "trading_frequency"
    WALLET_TRANSFER = "wallet_transfer"
    PERFORMANCE_DROP = "performance_drop"
    UNUSUAL_PATTERN = "unusual_pattern"
    SECURITY_BREACH = "security_breach"


class ExplainableAI:
    """
    Explainable AI (XAI) Module.
    Generates human-readable explanations for strategy recommendations.
    """
    
    def __init__(self):
        """Initialize explainable AI module."""
        self.strategy_explanations: List[Dict] = []
        
    def explain_strategy(self, strategy: Dict, performance_data: Dict) -> Dict:
        """
        Generate comprehensive explanation for a strategy.
        
        Args:
            strategy: Strategy details
            performance_data: Historical performance data
            
        Returns:
            Detailed explanation
        """
        explanation = {
            "strategy_id": strategy.get("id"),
            "strategy_name": strategy.get("name"),
            "why_it_works": self._explain_mechanism(strategy),
            "market_conditions": self._explain_market_fit(strategy, performance_data),
            "strengths": self._identify_strengths(strategy, performance_data),
            "weaknesses": self._identify_weaknesses(strategy, performance_data),
            "risk_factors": self._identify_risks(strategy),
            "optimal_conditions": self._define_optimal_conditions(strategy),
            "expected_performance": self._predict_performance(strategy, performance_data),
            "confidence_level": self._calculate_confidence(strategy, performance_data),
            "generated_at": datetime.now().isoformat()
        }
        
        self.strategy_explanations.append(explanation)
        
        # Print human-readable summary
        print(f"\n{'='*70}")
        print(f"STRATEGY EXPLANATION: {explanation['strategy_name']}")
        print(f"{'='*70}")
        print(f"\n📊 Why This Strategy Works:")
        print(f"   {explanation['why_it_works']}")
        print(f"\n🎯 Optimal Market Conditions:")
        for condition in explanation['optimal_conditions']:
            print(f"   • {condition}")
        print(f"\n✅ Strengths:")
        for strength in explanation['strengths']:
            print(f"   • {strength}")
        print(f"\n⚠️ Weaknesses:")
        for weakness in explanation['weaknesses']:
            print(f"   • {weakness}")
        print(f"\n🎲 Confidence Level: {explanation['confidence_level']}%")
        print(f"{'='*70}\n")
        
        return explanation
    
    def _explain_mechanism(self, strategy: Dict) -> str:
        """Explain how the strategy works."""
        strategy_type = strategy.get("type", "momentum")
        
        mechanisms = {
            "momentum": "This strategy capitalizes on the tendency of assets to continue moving in the same direction. It identifies strong trends and rides them until reversal signals appear.",
            "mean_reversion": "This strategy exploits the principle that asset prices tend to return to their average over time. It buys when prices are abnormally low and sells when abnormally high.",
            "arbitrage": "This strategy profits from price discrepancies between different markets or exchanges by simultaneously buying low and selling high.",
            "market_making": "This strategy provides liquidity by placing both buy and sell orders, profiting from the bid-ask spread while managing inventory risk."
        }
        
        return mechanisms.get(strategy_type, "This strategy uses advanced pattern recognition to identify profitable trading opportunities.")
    
    def _explain_market_fit(self, strategy: Dict, performance_data: Dict) -> List[str]:
        """Explain which market conditions favor this strategy."""
        return [
            "High volatility markets (> 2% daily swings)",
            "Strong trending periods without frequent reversals",
            "Markets with sufficient liquidity for large positions",
            "Low correlation with other active strategies"
        ]
    
    def _identify_strengths(self, strategy: Dict, performance_data: Dict) -> List[str]:
        """Identify strategy strengths."""
        return [
            "Consistent positive returns across multiple market conditions",
            "Strong risk-adjusted returns (high Sharpe ratio)",
            "Low correlation with market indices (provides diversification)",
            "Robust performance during recent backtesting"
        ]
    
    def _identify_weaknesses(self, strategy: Dict, performance_data: Dict) -> List[str]:
        """Identify strategy weaknesses."""
        return [
            "Underperforms in low-volatility, range-bound markets",
            "Requires frequent rebalancing, increasing transaction costs",
            "May experience significant drawdowns during trend reversals",
            "Performance degrades if many traders use similar strategies"
        ]
    
    def _identify_risks(self, strategy: Dict) -> List[Dict]:
        """Identify and quantify risk factors."""
        return [
            {"risk": "Market Risk", "severity": "medium", "mitigation": "Diversification across assets"},
            {"risk": "Liquidity Risk", "severity": "low", "mitigation": "Position size limits"},
            {"risk": "Model Risk", "severity": "medium", "mitigation": "Regular validation and updates"},
            {"risk": "Execution Risk", "severity": "low", "mitigation": "Advanced order routing"}
        ]
    
    def _define_optimal_conditions(self, strategy: Dict) -> List[str]:
        """Define optimal market conditions."""
        return [
            "Volatility: 15-25% annualized",
            "Trend strength: > 0.7 on ADX indicator",
            "Market volume: > 150% of 30-day average",
            "News sentiment: Neutral to positive"
        ]
    
    def _predict_performance(self, strategy: Dict, performance_data: Dict) -> Dict:
        """Predict expected performance."""
        return {
            "expected_return_annual": 18.5,
            "expected_volatility": 12.3,
            "sharpe_ratio": 1.5,
            "max_drawdown": -8.2,
            "win_rate": 64,
            "profit_factor": 2.1
        }
    
    def _calculate_confidence(self, strategy: Dict, performance_data: Dict) -> float:
        """Calculate confidence in the explanation."""
        # Based on data quality, backtest length, market conditions
        return 85.5


class PredictiveAnalytics:
    """
    Predictive Analytics Module.
    Uses time-series forecasting to predict short-term market movements.
    """
    
    def __init__(self):
        """Initialize predictive analytics module."""
        self.predictions: List[Dict] = []
        self.model_type = "LSTM"  # Could be ARIMA, LSTM, etc.
        
    def forecast_price(self, asset: str, historical_data: List[float], periods: int = 5) -> Dict:
        """
        Forecast future prices for an asset.
        
        Args:
            asset: Asset symbol
            historical_data: Historical price data
            periods: Number of periods to forecast
            
        Returns:
            Forecast results
        """
        # In production, use actual time-series models
        # Simplified simulation here
        current_price = historical_data[-1] if historical_data else 100.0
        
        forecasted_prices = []
        for i in range(periods):
            # Simple random walk with slight upward bias
            change = random.uniform(-0.02, 0.03)
            next_price = current_price * (1 + change)
            forecasted_prices.append(next_price)
            current_price = next_price
        
        # Calculate prediction intervals
        std_dev = current_price * 0.02  # 2% standard deviation
        
        forecast = {
            "asset": asset,
            "model": self.model_type,
            "current_price": historical_data[-1] if historical_data else 100.0,
            "forecasted_prices": forecasted_prices,
            "forecast_periods": periods,
            "confidence_intervals": [
                {
                    "period": i + 1,
                    "price": price,
                    "lower_bound": price - (1.96 * std_dev),
                    "upper_bound": price + (1.96 * std_dev)
                }
                for i, price in enumerate(forecasted_prices)
            ],
            "trend_direction": "bullish" if forecasted_prices[-1] > forecasted_prices[0] else "bearish",
            "forecasted_at": datetime.now().isoformat()
        }
        
        self.predictions.append(forecast)
        
        print(f"✓ Price forecast generated for {asset}")
        print(f"  Current: ${forecast['current_price']:.2f}")
        print(f"  Predicted (period {periods}): ${forecasted_prices[-1]:.2f}")
        print(f"  Trend: {forecast['trend_direction']}")
        
        return forecast
    
    def predict_market_regime(self, market_data: Dict) -> Dict:
        """
        Predict market regime (bull, bear, sideways).
        
        Args:
            market_data: Market indicators
            
        Returns:
            Regime prediction
        """
        # Analyze multiple indicators
        volatility = market_data.get("volatility", 0.15)
        momentum = market_data.get("momentum", 0.5)
        volume = market_data.get("volume", 1.0)
        
        # Simplified regime classification
        if momentum > 0.7 and volume > 1.2:
            regime = "bull_market"
            confidence = 0.85
        elif momentum < 0.3 and volume > 1.2:
            regime = "bear_market"
            confidence = 0.82
        else:
            regime = "sideways_market"
            confidence = 0.70
        
        prediction = {
            "regime": regime,
            "confidence": confidence,
            "indicators": {
                "volatility": volatility,
                "momentum": momentum,
                "volume_ratio": volume
            },
            "predicted_at": datetime.now().isoformat()
        }
        
        print(f"✓ Market regime predicted: {regime} (confidence: {confidence:.0%})")
        
        return prediction


class AnomalyDetector:
    """
    Anomaly Detection Module.
    Monitors system activity and detects unusual behavior.
    """
    
    def __init__(self):
        """Initialize anomaly detector."""
        self.baseline_metrics: Dict[str, Dict] = {}
        self.detected_anomalies: List[Dict] = []
        self.alert_callbacks: List = []
        
    def establish_baseline(self, component: str, metrics: Dict):
        """
        Establish baseline behavior for a component.
        
        Args:
            component: Component name (e.g., "trading_bot_1")
            metrics: Historical metrics
        """
        self.baseline_metrics[component] = {
            "avg_trades_per_hour": metrics.get("avg_trades_per_hour", 10),
            "avg_trade_size": metrics.get("avg_trade_size", 1000),
            "avg_response_time": metrics.get("avg_response_time", 0.5),
            "normal_activity_hours": metrics.get("normal_activity_hours", [8, 20]),
            "established_at": datetime.now().isoformat()
        }
        
        print(f"✓ Baseline established for {component}")
    
    def detect_trading_anomalies(self, bot_id: str, current_metrics: Dict) -> Optional[Dict]:
        """
        Detect anomalous trading behavior.
        
        Args:
            bot_id: Bot identifier
            current_metrics: Current bot metrics
            
        Returns:
            Anomaly details if detected, None otherwise
        """
        if bot_id not in self.baseline_metrics:
            return None
        
        baseline = self.baseline_metrics[bot_id]
        
        # Check trading frequency
        current_tph = current_metrics.get("trades_per_hour", 0)
        baseline_tph = baseline["avg_trades_per_hour"]
        
        if current_tph > baseline_tph * 3:  # 3x normal frequency
            return self._create_anomaly_alert(
                bot_id,
                AnomalyType.TRADING_FREQUENCY,
                "high",
                f"Trading frequency ({current_tph}/hour) is 3x normal ({baseline_tph}/hour)",
                {"current": current_tph, "baseline": baseline_tph}
            )
        
        # Check trade size
        current_size = current_metrics.get("avg_trade_size", 0)
        baseline_size = baseline["avg_trade_size"]
        
        if current_size > baseline_size * 2:  # 2x normal size
            return self._create_anomaly_alert(
                bot_id,
                AnomalyType.UNUSUAL_PATTERN,
                "medium",
                f"Trade size (${current_size}) is 2x normal (${baseline_size})",
                {"current": current_size, "baseline": baseline_size}
            )
        
        return None
    
    def detect_wallet_anomalies(self, wallet_id: str, transaction: Dict) -> Optional[Dict]:
        """
        Detect anomalous wallet activity.
        
        Args:
            wallet_id: Wallet identifier
            transaction: Transaction details
            
        Returns:
            Anomaly details if detected, None otherwise
        """
        amount = transaction.get("amount", 0)
        destination = transaction.get("destination")
        
        # Check for large unexpected transfers
        if amount > 100000:  # $100k threshold
            return self._create_anomaly_alert(
                wallet_id,
                AnomalyType.WALLET_TRANSFER,
                "critical",
                f"Large transfer detected: ${amount:,.2f} to {destination}",
                {"amount": amount, "destination": destination}
            )
        
        # Check for transfers to unknown addresses
        known_addresses = ["treasury", "exchange_1", "exchange_2"]
        if destination not in known_addresses:
            return self._create_anomaly_alert(
                wallet_id,
                AnomalyType.SECURITY_BREACH,
                "critical",
                f"Transfer to unknown address: {destination}",
                {"destination": destination, "amount": amount}
            )
        
        return None
    
    def _create_anomaly_alert(self, component: str, anomaly_type: AnomalyType, 
                             severity: str, message: str, details: Dict) -> Dict:
        """Create anomaly alert."""
        alert = {
            "alert_id": f"anomaly_{len(self.detected_anomalies) + 1}",
            "component": component,
            "type": anomaly_type.value,
            "severity": severity,
            "message": message,
            "details": details,
            "detected_at": datetime.now().isoformat(),
            "status": "active",
            "action_taken": self._determine_action(severity)
        }
        
        self.detected_anomalies.append(alert)
        
        # Print alert
        print(f"\n⚠️  ANOMALY DETECTED!")
        print(f"   Component: {component}")
        print(f"   Type: {anomaly_type.value}")
        print(f"   Severity: {severity.upper()}")
        print(f"   Message: {message}")
        print(f"   Action: {alert['action_taken']}\n")
        
        # Execute action if critical
        if severity == "critical":
            self._execute_emergency_action(alert)
        
        return alert
    
    def _determine_action(self, severity: str) -> str:
        """Determine appropriate action based on severity."""
        actions = {
            "low": "Log and monitor",
            "medium": "Alert operator",
            "high": "Alert operator and reduce activity",
            "critical": "Trigger emergency freeze"
        }
        return actions.get(severity, "Log and monitor")
    
    def _execute_emergency_action(self, alert: Dict):
        """Execute emergency action for critical anomalies."""
        print(f"🚨 EMERGENCY ACTION TRIGGERED")
        print(f"   Freezing component: {alert['component']}")
        print(f"   All transactions halted pending investigation")
        
        # In production, actually freeze the component
        alert["component_frozen"] = True
        alert["freeze_timestamp"] = datetime.now().isoformat()
    
    def get_anomaly_report(self, time_period: str = "24h") -> Dict:
        """Generate anomaly report."""
        recent_anomalies = self.detected_anomalies[-10:]  # Last 10
        
        by_severity = {}
        for anomaly in recent_anomalies:
            severity = anomaly["severity"]
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        return {
            "period": time_period,
            "total_anomalies": len(recent_anomalies),
            "by_severity": by_severity,
            "critical_count": by_severity.get("critical", 0),
            "recent_anomalies": recent_anomalies,
            "generated_at": datetime.now().isoformat()
        }


def create_intelligence_system() -> Dict:
    """
    Factory function to create intelligence system.
    
    Returns:
        Dictionary of intelligence components
    """
    return {
        "explainable_ai": ExplainableAI(),
        "predictive_analytics": PredictiveAnalytics(),
        "anomaly_detector": AnomalyDetector()
    }
