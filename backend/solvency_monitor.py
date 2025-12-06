"""
Solvency Monitoring Module
Provides financial health monitoring and solvency checks for trading accounts.
"""

from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class SolvencyStatus(Enum):
    """Solvency status enumeration."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    INSOLVENT = "insolvent"


class SolvencyMonitor:
    """
    Monitor and assess financial solvency of trading accounts.
    Ensures accounts maintain adequate capital and liquidity.
    """
    
    def __init__(self, 
                 min_capital_ratio: float = 0.3,
                 min_liquidity_ratio: float = 0.2,
                 max_leverage: float = 3.0):
        """
        Initialize the solvency monitor.
        
        Args:
            min_capital_ratio: Minimum capital ratio (default 30%)
            min_liquidity_ratio: Minimum liquidity ratio (default 20%)
            max_leverage: Maximum allowed leverage (default 3x)
        """
        self.min_capital_ratio = min_capital_ratio
        self.min_liquidity_ratio = min_liquidity_ratio
        self.max_leverage = max_leverage
        self.alerts: List[Dict] = []
        
    def check_solvency(self, account_data: Dict) -> Dict:
        """
        Perform comprehensive solvency check on an account.
        
        Args:
            account_data: Dictionary containing account financial data
            
        Returns:
            Solvency assessment dictionary
        """
        timestamp = datetime.now().isoformat()
        
        # Extract account metrics
        total_assets = account_data.get("total_assets", 0)
        total_liabilities = account_data.get("total_liabilities", 0)
        liquid_assets = account_data.get("liquid_assets", 0)
        equity = total_assets - total_liabilities
        
        # Calculate ratios
        capital_ratio = equity / total_assets if total_assets > 0 else 0
        liquidity_ratio = liquid_assets / total_assets if total_assets > 0 else 0
        leverage = total_assets / equity if equity > 0 else float('inf')
        
        # Determine solvency status
        status = self._determine_status(capital_ratio, liquidity_ratio, leverage)
        
        # Check for violations
        violations = self._check_violations(capital_ratio, liquidity_ratio, leverage)
        
        assessment = {
            "timestamp": timestamp,
            "status": status.value,
            "metrics": {
                "total_assets": total_assets,
                "total_liabilities": total_liabilities,
                "equity": equity,
                "liquid_assets": liquid_assets,
                "capital_ratio": capital_ratio,
                "liquidity_ratio": liquidity_ratio,
                "leverage": leverage if leverage != float('inf') else "undefined"
            },
            "thresholds": {
                "min_capital_ratio": self.min_capital_ratio,
                "min_liquidity_ratio": self.min_liquidity_ratio,
                "max_leverage": self.max_leverage
            },
            "violations": violations,
            "recommendations": self._generate_recommendations(violations, status)
        }
        
        # Log alert if status is concerning
        if status in [SolvencyStatus.WARNING, SolvencyStatus.CRITICAL, SolvencyStatus.INSOLVENT]:
            self._log_alert(assessment)
            
        return assessment
    
    def _determine_status(self, capital_ratio: float, liquidity_ratio: float, 
                         leverage: float) -> SolvencyStatus:
        """Determine overall solvency status based on ratios."""
        if capital_ratio <= 0:
            return SolvencyStatus.INSOLVENT
            
        if (capital_ratio < self.min_capital_ratio * 0.5 or 
            liquidity_ratio < self.min_liquidity_ratio * 0.5 or
            leverage > self.max_leverage * 1.5):
            return SolvencyStatus.CRITICAL
            
        if (capital_ratio < self.min_capital_ratio or 
            liquidity_ratio < self.min_liquidity_ratio or
            leverage > self.max_leverage):
            return SolvencyStatus.WARNING
            
        return SolvencyStatus.HEALTHY
    
    def _check_violations(self, capital_ratio: float, liquidity_ratio: float,
                         leverage: float) -> List[str]:
        """Check for threshold violations."""
        violations = []
        
        if capital_ratio < self.min_capital_ratio:
            violations.append(
                f"Capital ratio {capital_ratio:.2%} below minimum {self.min_capital_ratio:.2%}"
            )
            
        if liquidity_ratio < self.min_liquidity_ratio:
            violations.append(
                f"Liquidity ratio {liquidity_ratio:.2%} below minimum {self.min_liquidity_ratio:.2%}"
            )
            
        if leverage > self.max_leverage:
            violations.append(
                f"Leverage {leverage:.2f}x exceeds maximum {self.max_leverage:.2f}x"
            )
            
        return violations
    
    def _generate_recommendations(self, violations: List[str], 
                                 status: SolvencyStatus) -> List[str]:
        """Generate recommendations based on violations and status."""
        recommendations = []
        
        if status == SolvencyStatus.INSOLVENT:
            recommendations.append("URGENT: Cease all trading immediately")
            recommendations.append("Liquidate positions to cover liabilities")
            recommendations.append("Seek immediate capital injection")
            
        elif status == SolvencyStatus.CRITICAL:
            recommendations.append("Reduce position sizes immediately")
            recommendations.append("Close high-risk positions")
            recommendations.append("Increase liquid asset reserves")
            recommendations.append("Halt new position entries")
            
        elif status == SolvencyStatus.WARNING:
            recommendations.append("Monitor account closely")
            recommendations.append("Consider reducing leverage")
            recommendations.append("Maintain higher cash reserves")
            recommendations.append("Review risk management parameters")
            
        else:
            recommendations.append("Maintain current risk management practices")
            recommendations.append("Continue regular solvency monitoring")
            
        return recommendations
    
    def _log_alert(self, assessment: Dict):
        """Log a solvency alert."""
        alert = {
            "timestamp": assessment["timestamp"],
            "status": assessment["status"],
            "violations": assessment["violations"]
        }
        self.alerts.append(alert)
        print(f"SOLVENCY ALERT [{assessment['status']}]: {assessment['violations']}")
    
    def get_alerts(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get recent solvency alerts.
        
        Args:
            limit: Maximum number of alerts to return
            
        Returns:
            List of alert dictionaries
        """
        if limit:
            return self.alerts[-limit:]
        return self.alerts
    
    def monitor_portfolio(self, portfolio_data: Dict) -> Dict:
        """
        Monitor solvency across an entire portfolio.
        
        Args:
            portfolio_data: Dictionary containing portfolio information
            
        Returns:
            Portfolio solvency assessment
        """
        accounts = portfolio_data.get("accounts", [])
        
        assessments = []
        critical_count = 0
        warning_count = 0
        
        for account in accounts:
            assessment = self.check_solvency(account)
            assessments.append(assessment)
            
            if assessment["status"] in ["critical", "insolvent"]:
                critical_count += 1
            elif assessment["status"] == "warning":
                warning_count += 1
                
        portfolio_status = "healthy"
        if critical_count > 0:
            portfolio_status = "critical"
        elif warning_count > 0:
            portfolio_status = "warning"
            
        return {
            "timestamp": datetime.now().isoformat(),
            "portfolio_status": portfolio_status,
            "total_accounts": len(accounts),
            "critical_accounts": critical_count,
            "warning_accounts": warning_count,
            "healthy_accounts": len(accounts) - critical_count - warning_count,
            "account_assessments": assessments
        }


def create_solvency_monitor(config: Optional[Dict] = None) -> SolvencyMonitor:
    """
    Factory function to create a solvency monitor instance.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        SolvencyMonitor instance
    """
    if config:
        return SolvencyMonitor(
            min_capital_ratio=config.get("min_capital_ratio", 0.3),
            min_liquidity_ratio=config.get("min_liquidity_ratio", 0.2),
            max_leverage=config.get("max_leverage", 3.0)
        )
    return SolvencyMonitor()
