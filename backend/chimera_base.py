"""
PROJECT CHIMERA - BASE CLASSES
Common functionality shared across all Chimera versions
"""

from typing import Dict, List, Optional, Any
from datetime import datetime


class ChimeraComponentBase:
    """
    Base class for all Chimera components across all versions.
    Provides common initialization and utility methods.
    """
    
    def __init__(self):
        """Initialize base component."""
        self.created_at = datetime.now().isoformat()
        self.status = "initialized"
    
    def log_success(self, message: str, details: Optional[Dict] = None):
        """
        Log a success message with optional details.
        
        Args:
            message: Success message to display
            details: Optional dictionary of details to print
        """
        print(f"✓ {message}")
        if details:
            for key, value in details.items():
                print(f"  {key}: {value}")
    
    def log_info(self, message: str):
        """Log an informational message."""
        print(f"ℹ {message}")
    
    def log_error(self, message: str):
        """Log an error message."""
        print(f"✗ {message}")
    
    def get_status(self) -> Dict:
        """Get component status."""
        return {
            "status": self.status,
            "created_at": self.created_at,
            "component_type": self.__class__.__name__
        }


class SystemVersion:
    """
    Base class for system version metadata and initialization.
    """
    
    def __init__(self, version: str, components: List[Any]):
        """
        Initialize system version.
        
        Args:
            version: Version string (e.g., "4.0", "5.0")
            components: List of component instances
        """
        self.version = version
        self.components = components
        self.created_at = datetime.now().isoformat()
        self.status = "operational"
    
    def get_system_info(self) -> Dict:
        """Get comprehensive system information."""
        return {
            "version": self.version,
            "status": self.status,
            "created_at": self.created_at,
            "num_components": len(self.components),
            "component_types": [c.__class__.__name__ for c in self.components]
        }
    
    def print_banner(self, title: str, features: List[str]):
        """
        Print a formatted system banner.
        
        Args:
            title: Version title
            features: List of key features
        """
        print("\n" + "="*70)
        print(f"🚀 {title}")
        print("="*70)
        print(f"Version: {self.version}")
        print(f"Status: {self.status}")
        print("\nKey Features:")
        for feature in features:
            print(f"  • {feature}")
        print("="*70 + "\n")


def create_system_dict(version: str, components: Dict[str, Any], **kwargs) -> Dict:
    """
    Create a standardized system dictionary.
    
    Args:
        version: Version string
        components: Dictionary of component name -> component instance
        **kwargs: Additional system attributes
        
    Returns:
        Dictionary with standardized system structure
    """
    system_dict = {
        **components,
        "version": version,
        "status": "operational",
        "created_at": datetime.now().isoformat()
    }
    system_dict.update(kwargs)
    return system_dict


# Common data structures for demonstrations

class DemoData:
    """Common demo data used across versions."""
    
    @staticmethod
    def get_sample_market_data() -> Dict:
        """Get sample market data for demonstrations."""
        return {
            "BTC": {"price": 45000, "volume": 1200000000, "change_24h": 2.5},
            "ETH": {"price": 3000, "volume": 800000000, "change_24h": 3.2},
            "SOL": {"price": 120, "volume": 500000000, "change_24h": -1.5}
        }
    
    @staticmethod
    def get_sample_opportunities() -> List[Dict]:
        """Get sample job opportunities for demonstrations."""
        return [
            {
                "job_id": "FL-001",
                "title": "Python Trading Bot Development",
                "budget": 5000,
                "duration": "2 weeks",
                "skills": ["Python", "Trading", "API Integration"],
                "match_score": 0.95,
                "platform": "Upwork"
            },
            {
                "job_id": "FL-002",
                "title": "Smart Contract Audit",
                "budget": 3000,
                "duration": "1 week",
                "skills": ["Solidity", "Security", "Blockchain"],
                "match_score": 0.88,
                "platform": "Freelancer"
            }
        ]
