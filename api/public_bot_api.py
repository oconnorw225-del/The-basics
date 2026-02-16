#!/usr/bin/env python3
"""
Public Bot API Endpoints
Provides public information that bots can access without authentication
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import json
from pathlib import Path
from datetime import datetime

# Create router
router = APIRouter(prefix="/api/public", tags=["public"])


def load_public_access_config() -> Dict[str, Any]:
    """Load bot public access configuration."""
    config_path = Path(__file__).parent.parent / "config" / "bot-public-access.json"
    
    if not config_path.exists():
        return {}
    
    with open(config_path, 'r') as f:
        return json.load(f)


@router.get("/")
async def public_root():
    """Public API root."""
    return {
        "name": "Public Bot API",
        "version": "1.0.0",
        "description": "Public endpoints accessible to all bots",
        "documentation": "/api/public/endpoints",
        "platform_info": "/api/public/platform"
    }


@router.get("/platform")
async def get_platform_info():
    """
    Get public platform information.
    Safe for bots to access - no sensitive data.
    """
    config = load_public_access_config()
    platform_info = config.get('platform_info', {})
    
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "platform": platform_info
    }


@router.get("/endpoints")
async def get_public_endpoints():
    """
    Get list of all public endpoints.
    Shows bots what they can access.
    """
    config = load_public_access_config()
    public_endpoints = config.get('public_endpoints', {})
    
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "description": public_endpoints.get('description', ''),
        "endpoints": public_endpoints.get('endpoints', []),
        "total": len(public_endpoints.get('endpoints', []))
    }


@router.get("/products")
async def get_product_info():
    """
    Get product information.
    Public product catalog - safe for bots.
    """
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "products": [
            {
                "name": "Autonomous Trading System",
                "description": "AI-powered trading bot for cryptocurrency markets",
                "features": [
                    "24/7 automated trading",
                    "Quantum-enhanced strategies",
                    "Risk management",
                    "Multi-exchange support"
                ],
                "supported_exchanges": ["NDAX"]
            },
            {
                "name": "Freelance AI Engine",
                "description": "Autonomous freelance job automation",
                "features": [
                    "Job prospecting",
                    "Automated bidding",
                    "AI-powered coding",
                    "Multi-platform support"
                ],
                "supported_platforms": ["Fiverr", "Freelancer", "Toptal", "Guru", "PeoplePerHour"]
            },
            {
                "name": "Bot Coordination System",
                "description": "Centralized bot management and coordination",
                "features": [
                    "Multi-bot orchestration",
                    "Health monitoring",
                    "Credential sharing",
                    "Recovery automation"
                ]
            }
        ]
    }


@router.get("/capabilities")
async def get_system_capabilities():
    """
    Get system capabilities.
    Shows what the platform can do - safe for public access.
    """
    config = load_public_access_config()
    platform_info = config.get('platform_info', {})
    
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "capabilities": platform_info.get('capabilities', []),
        "supported_platforms": platform_info.get('supported_platforms', []),
        "bot_types": platform_info.get('bot_types', [])
    }


@router.get("/access-levels")
async def get_access_levels():
    """
    Get information about different bot access levels.
    Helps bots understand what permissions they need.
    """
    config = load_public_access_config()
    bot_access_levels = config.get('bot_access_levels', {})
    
    # Return sanitized version (without internal details)
    levels = {}
    for level_name, level_info in bot_access_levels.get('levels', {}).items():
        levels[level_name] = {
            "description": level_info.get('description', ''),
            "authentication_required": level_info.get('authentication_required', False),
            "rate_limit": level_info.get('rate_limit', '')
        }
    
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "description": bot_access_levels.get('description', ''),
        "levels": levels
    }


@router.get("/data-classification")
async def get_data_classification():
    """
    Get information about public vs private data.
    Helps bots understand what data is accessible.
    """
    config = load_public_access_config()
    data_classification = config.get('data_classification', {})
    
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "public_data": {
            "description": data_classification.get('public', {}).get('description', ''),
            "categories": data_classification.get('public', {}).get('categories', [])
        },
        "private_data": {
            "description": data_classification.get('private', {}).get('description', ''),
            "note": "Private data requires authentication and appropriate access levels"
        }
    }


@router.get("/documentation")
async def get_documentation_links():
    """
    Get links to public documentation.
    """
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "documentation": {
            "api_reference": "/api/docs",
            "platform_info": "/api/public/platform",
            "endpoints": "/api/public/endpoints",
            "capabilities": "/api/public/capabilities",
            "github": "https://github.com/oconnorw225-del/The-basics",
            "readme": "https://github.com/oconnorw225-del/The-basics/blob/main/README.md"
        }
    }


@router.get("/health")
async def public_health_check():
    """
    Public health check endpoint.
    Shows system status without exposing sensitive information.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Public Bot API",
        "components": {
            "api": "operational",
            "documentation": "available",
            "platform_info": "available"
        }
    }


# Helper function to integrate with FastAPI app
def register_public_bot_routes(app):
    """
    Register public bot routes with FastAPI app.
    
    Args:
        app: FastAPI application instance
    """
    app.include_router(router)
    print("✅ Registered public bot API routes")


if __name__ == "__main__":
    # Test the endpoints
    import asyncio
    
    async def test_endpoints():
        print("🧪 Testing Public Bot API Endpoints")
        print("=" * 60)
        
        print("\n📋 Platform Info:")
        info = await get_platform_info()
        print(json.dumps(info, indent=2))
        
        print("\n🔌 Public Endpoints:")
        endpoints = await get_public_endpoints()
        print(f"Total public endpoints: {endpoints['total']}")
        for endpoint in endpoints['endpoints'][:3]:
            print(f"  • {endpoint['path']} - {endpoint['description']}")
        
        print("\n📦 Products:")
        products = await get_product_info()
        for product in products['products']:
            print(f"  • {product['name']}: {product['description']}")
        
        print("\n🎯 Capabilities:")
        capabilities = await get_system_capabilities()
        print(f"Capabilities: {', '.join(capabilities['capabilities'][:3])}")
        
        print("\n🔐 Access Levels:")
        levels = await get_access_levels()
        for level_name, level_info in levels['levels'].items():
            print(f"  • {level_name}: {level_info['description']}")
        
        print("\n" + "=" * 60)
    
    asyncio.run(test_endpoints())
