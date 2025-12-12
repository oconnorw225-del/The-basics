"""
Test suite for autonomous trading module.
"""

import unittest
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.autonomous_trading import AutonomousTrader, create_autonomous_trader


class TestAutonomousTrader(unittest.TestCase):
    """Test cases for AutonomousTrader class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.trader = AutonomousTrader(risk_tolerance=0.05, max_position_size=0.1)
        
    def test_initialization(self):
        """Test trader initialization."""
        self.assertEqual(self.trader.risk_tolerance, 0.05)
        self.assertEqual(self.trader.max_position_size, 0.1)
        self.assertFalse(self.trader.active)
        self.assertEqual(len(self.trader.positions), 0)
        
    def test_activation(self):
        """Test trader activation."""
        result = self.trader.activate()
        self.assertTrue(result)
        self.assertTrue(self.trader.active)
        
    def test_deactivation(self):
        """Test trader deactivation."""
        self.trader.activate()
        result = self.trader.deactivate()
        self.assertTrue(result)
        self.assertFalse(self.trader.active)
        
    def test_analyze_opportunity_inactive(self):
        """Test analysis when trader is inactive."""
        market_data = {"price": 50000, "volume": 1000000}
        signal = self.trader.analyze_opportunity(market_data)
        self.assertIsNone(signal)
        
    def test_analyze_opportunity_bullish(self):
        """Test analysis with bullish market data."""
        self.trader.activate()
        market_data = {
            "price": 50000,
            "volume": 1000000,
            "trend": "bullish",
            "avg_volume": 800000,
            "volatility": 0.02,
            "liquidity": 1.0
        }
        signal = self.trader.analyze_opportunity(market_data)
        
        self.assertIsNotNone(signal)
        self.assertEqual(signal["action"], "buy")
        self.assertGreater(signal["confidence"], 0)
        self.assertIn("risk_assessment", signal)
        
    def test_analyze_opportunity_bearish(self):
        """Test analysis with bearish market data."""
        self.trader.activate()
        market_data = {
            "price": 50000,
            "volume": 1000000,
            "trend": "bearish",
            "avg_volume": 800000,
            "volatility": 0.02,
            "liquidity": 1.0
        }
        signal = self.trader.analyze_opportunity(market_data)
        
        self.assertIsNotNone(signal)
        self.assertEqual(signal["action"], "sell")
        
    def test_risk_assessment(self):
        """Test risk assessment calculation."""
        market_data = {
            "volatility": 0.03,
            "liquidity": 1.5
        }
        risk = self.trader._assess_risk(market_data)
        
        self.assertIn("risk_score", risk)
        self.assertIn("volatility", risk)
        self.assertIn("liquidity", risk)
        self.assertIn("acceptable", risk)
        
    def test_execute_trade_inactive(self):
        """Test trade execution when inactive."""
        signal = {"action": "buy", "risk_assessment": {"acceptable": True}}
        result = self.trader.execute_trade(signal)
        
        self.assertEqual(result["status"], "error")
        
    def test_execute_trade_high_risk(self):
        """Test trade execution with high risk."""
        self.trader.activate()
        signal = {"action": "buy", "risk_assessment": {"acceptable": False}}
        result = self.trader.execute_trade(signal)
        
        self.assertEqual(result["status"], "rejected")
        
    def test_execute_trade_success(self):
        """Test successful trade execution."""
        self.trader.activate()
        signal = {
            "action": "buy",
            "confidence": 0.8,
            "reason": "Test trade",
            "risk_assessment": {"acceptable": True}
        }
        result = self.trader.execute_trade(signal)
        
        self.assertEqual(result["status"], "executed")
        self.assertEqual(result["action"], "buy")
        self.assertEqual(len(self.trader.positions), 1)
        
    def test_get_status(self):
        """Test getting trader status."""
        status = self.trader.get_status()
        
        self.assertIn("active", status)
        self.assertIn("risk_tolerance", status)
        self.assertIn("max_position_size", status)
        self.assertIn("open_positions", status)
        self.assertIn("philosophy", status)
        
    def test_factory_function_default(self):
        """Test factory function with default config."""
        trader = create_autonomous_trader()
        self.assertIsInstance(trader, AutonomousTrader)
        
    def test_factory_function_custom(self):
        """Test factory function with custom config."""
        config = {"risk_tolerance": 0.03, "max_position_size": 0.15}
        trader = create_autonomous_trader(config)
        
        self.assertEqual(trader.risk_tolerance, 0.03)
        self.assertEqual(trader.max_position_size, 0.15)


if __name__ == '__main__':
    unittest.main()
