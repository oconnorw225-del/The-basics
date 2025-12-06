"""
Test suite for solvency monitoring module.
"""

import unittest
import sys
sys.path.insert(0, '/home/runner/work/The-basics/The-basics')

from backend.solvency_monitor import SolvencyMonitor, create_solvency_monitor, SolvencyStatus


class TestSolvencyMonitor(unittest.TestCase):
    """Test cases for SolvencyMonitor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.monitor = SolvencyMonitor(
            min_capital_ratio=0.3,
            min_liquidity_ratio=0.2,
            max_leverage=3.0
        )
        
    def test_initialization(self):
        """Test monitor initialization."""
        self.assertEqual(self.monitor.min_capital_ratio, 0.3)
        self.assertEqual(self.monitor.min_liquidity_ratio, 0.2)
        self.assertEqual(self.monitor.max_leverage, 3.0)
        self.assertEqual(len(self.monitor.alerts), 0)
        
    def test_healthy_account(self):
        """Test solvency check for healthy account."""
        account_data = {
            "total_assets": 100000,
            "total_liabilities": 40000,
            "liquid_assets": 30000
        }
        
        assessment = self.monitor.check_solvency(account_data)
        
        self.assertEqual(assessment["status"], "healthy")
        self.assertEqual(len(assessment["violations"]), 0)
        self.assertGreater(assessment["metrics"]["capital_ratio"], self.monitor.min_capital_ratio)
        
    def test_warning_account(self):
        """Test solvency check for warning-level account."""
        account_data = {
            "total_assets": 100000,
            "total_liabilities": 75000,
            "liquid_assets": 15000
        }
        
        assessment = self.monitor.check_solvency(account_data)
        
        self.assertEqual(assessment["status"], "warning")
        self.assertGreater(len(assessment["violations"]), 0)
        
    def test_critical_account(self):
        """Test solvency check for critical account."""
        account_data = {
            "total_assets": 100000,
            "total_liabilities": 90000,
            "liquid_assets": 5000
        }
        
        assessment = self.monitor.check_solvency(account_data)
        
        self.assertEqual(assessment["status"], "critical")
        self.assertGreater(len(assessment["violations"]), 0)
        self.assertGreater(len(assessment["recommendations"]), 0)
        
    def test_insolvent_account(self):
        """Test solvency check for insolvent account."""
        account_data = {
            "total_assets": 100000,
            "total_liabilities": 120000,
            "liquid_assets": 10000
        }
        
        assessment = self.monitor.check_solvency(account_data)
        
        self.assertEqual(assessment["status"], "insolvent")
        self.assertIn("URGENT", assessment["recommendations"][0])
        
    def test_capital_ratio_violation(self):
        """Test detection of capital ratio violation."""
        account_data = {
            "total_assets": 100000,
            "total_liabilities": 75000,
            "liquid_assets": 30000
        }
        
        assessment = self.monitor.check_solvency(account_data)
        
        # Capital ratio is 25% (below 30% minimum)
        capital_ratio = assessment["metrics"]["capital_ratio"]
        self.assertLess(capital_ratio, self.monitor.min_capital_ratio)
        
        # Should have violation
        violations = [v for v in assessment["violations"] if "Capital ratio" in v]
        self.assertGreater(len(violations), 0)
        
    def test_liquidity_ratio_violation(self):
        """Test detection of liquidity ratio violation."""
        account_data = {
            "total_assets": 100000,
            "total_liabilities": 40000,
            "liquid_assets": 10000
        }
        
        assessment = self.monitor.check_solvency(account_data)
        
        # Liquidity ratio is 10% (below 20% minimum)
        liquidity_ratio = assessment["metrics"]["liquidity_ratio"]
        self.assertLess(liquidity_ratio, self.monitor.min_liquidity_ratio)
        
        # Should have violation
        violations = [v for v in assessment["violations"] if "Liquidity ratio" in v]
        self.assertGreater(len(violations), 0)
        
    def test_leverage_violation(self):
        """Test detection of leverage violation."""
        account_data = {
            "total_assets": 100000,
            "total_liabilities": 80000,
            "liquid_assets": 25000
        }
        
        assessment = self.monitor.check_solvency(account_data)
        
        # Leverage is 5x (above 3x maximum)
        leverage = assessment["metrics"]["leverage"]
        self.assertGreater(leverage, self.monitor.max_leverage)
        
        # Should have violation
        violations = [v for v in assessment["violations"] if "Leverage" in v]
        self.assertGreater(len(violations), 0)
        
    def test_portfolio_monitoring(self):
        """Test portfolio-wide solvency monitoring."""
        portfolio_data = {
            "accounts": [
                {"total_assets": 100000, "total_liabilities": 40000, "liquid_assets": 30000},
                {"total_assets": 50000, "total_liabilities": 20000, "liquid_assets": 15000},
                {"total_assets": 75000, "total_liabilities": 60000, "liquid_assets": 10000}
            ]
        }
        
        portfolio_assessment = self.monitor.monitor_portfolio(portfolio_data)
        
        self.assertEqual(portfolio_assessment["total_accounts"], 3)
        self.assertIn("portfolio_status", portfolio_assessment)
        self.assertIn("account_assessments", portfolio_assessment)
        
    def test_alerts_logging(self):
        """Test that alerts are logged for concerning status."""
        initial_alerts = len(self.monitor.alerts)
        
        # Create warning-level account
        account_data = {
            "total_assets": 100000,
            "total_liabilities": 75000,
            "liquid_assets": 15000
        }
        
        self.monitor.check_solvency(account_data)
        
        # Alert should be logged
        self.assertGreater(len(self.monitor.alerts), initial_alerts)
        
    def test_factory_function_default(self):
        """Test factory function with default config."""
        monitor = create_solvency_monitor()
        self.assertIsInstance(monitor, SolvencyMonitor)
        
    def test_factory_function_custom(self):
        """Test factory function with custom config."""
        config = {
            "min_capital_ratio": 0.35,
            "min_liquidity_ratio": 0.25,
            "max_leverage": 2.5
        }
        monitor = create_solvency_monitor(config)
        
        self.assertEqual(monitor.min_capital_ratio, 0.35)
        self.assertEqual(monitor.min_liquidity_ratio, 0.25)
        self.assertEqual(monitor.max_leverage, 2.5)


if __name__ == '__main__':
    unittest.main()
