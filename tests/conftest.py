"""Pytest configuration and fixtures."""
import pytest
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_config():
    """Mock configuration for tests."""
    return {
        "enabled": False,
        "auto_trigger": False,
        "manual_override_allowed": True
    }

@pytest.fixture
def mock_bot_limits():
    """Mock bot limits for tests."""
    return {
        "ndax": {
            "max_daily_loss": 100,
            "max_position_size": 1000
        },
        "global_limits": {
            "total_max_loss": 500,
            "total_max_exposure": 5000
        }
    }
