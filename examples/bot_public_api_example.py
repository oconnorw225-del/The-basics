#!/usr/bin/env python3
"""
Example Bot Script - Public API Access
Demonstrates how bots can access public platform information
"""

import requests
import json
from typing import Dict, Any


class BotPublicAPIClient:
    """
    Simple client for accessing public bot API endpoints.
    No authentication required for public endpoints.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize client.
        
        Args:
            base_url: Base URL of the API (default: http://localhost:8000)
        """
        self.base_url = base_url.rstrip('/')
    
    def get_platform_info(self) -> Dict[str, Any]:
        """
        Get public platform information.
        
        Returns:
            Platform information dict
        """
        url = f"{self.base_url}/api/public/platform"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_public_endpoints(self) -> Dict[str, Any]:
        """
        Get list of all public endpoints.
        
        Returns:
            Public endpoints dict
        """
        url = f"{self.base_url}/api/public/endpoints"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_products(self) -> Dict[str, Any]:
        """
        Get product information.
        
        Returns:
            Products dict
        """
        url = f"{self.base_url}/api/public/products"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get system capabilities.
        
        Returns:
            Capabilities dict
        """
        url = f"{self.base_url}/api/public/capabilities"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_access_levels(self) -> Dict[str, Any]:
        """
        Get information about access levels.
        
        Returns:
            Access levels dict
        """
        url = f"{self.base_url}/api/public/access-levels"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_documentation(self) -> Dict[str, Any]:
        """
        Get documentation links.
        
        Returns:
            Documentation dict
        """
        url = f"{self.base_url}/api/public/documentation"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()


def main():
    """Example usage of the public bot API."""
    print("🤖 Bot Public API Client Example")
    print("=" * 60)
    
    # Create client
    client = BotPublicAPIClient()
    
    # Get platform information
    print("\n📋 Platform Information:")
    try:
        platform_info = client.get_platform_info()
        platform = platform_info.get('platform', {})
        print(f"  Name: {platform.get('name')}")
        print(f"  Type: {platform.get('type')}")
        print(f"  Version: {platform.get('version')}")
        print(f"  Capabilities: {len(platform.get('capabilities', []))} available")
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️ Error: {e}")
        print("  Note: Make sure the API server is running")
    
    # Get products
    print("\n📦 Available Products:")
    try:
        products_data = client.get_products()
        products = products_data.get('products', [])
        for product in products:
            print(f"  • {product['name']}")
            print(f"    {product['description']}")
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️ Error: {e}")
    
    # Get capabilities
    print("\n🎯 System Capabilities:")
    try:
        capabilities_data = client.get_capabilities()
        capabilities = capabilities_data.get('capabilities', [])
        for cap in capabilities[:5]:  # Show first 5
            print(f"  • {cap}")
        if len(capabilities) > 5:
            print(f"  ... and {len(capabilities) - 5} more")
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️ Error: {e}")
    
    # Get access levels
    print("\n🔐 Access Levels:")
    try:
        access_data = client.get_access_levels()
        levels = access_data.get('levels', {})
        for level_name, level_info in levels.items():
            auth_required = "🔑 Auth Required" if level_info.get('authentication_required') else "🔓 No Auth"
            print(f"  • {level_name}: {level_info.get('description')} - {auth_required}")
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️ Error: {e}")
    
    # Get documentation
    print("\n📚 Documentation:")
    try:
        docs_data = client.get_documentation()
        docs = docs_data.get('documentation', {})
        print(f"  • API Reference: {docs.get('api_reference')}")
        print(f"  • Platform Info: {docs.get('platform_info')}")
        print(f"  • GitHub: {docs.get('github')}")
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️ Error: {e}")
    
    # Get public endpoints
    print("\n🔌 Public Endpoints:")
    try:
        endpoints_data = client.get_public_endpoints()
        endpoints = endpoints_data.get('endpoints', [])
        print(f"  Total: {len(endpoints)} public endpoints")
        print("  First 5:")
        for endpoint in endpoints[:5]:
            print(f"    • {endpoint['method']} {endpoint['path']}")
            print(f"      {endpoint['description']}")
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Public API access example complete")
    print("\nNote: This example uses only public endpoints.")
    print("No authentication or API keys required!")


if __name__ == "__main__":
    main()
