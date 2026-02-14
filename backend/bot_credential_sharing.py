"""
BOT COLLABORATIVE CREDENTIAL SHARING
Bots share discovered credentials with each other through a shared pool.
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class BotCredentialSharing:
    """Manages credential sharing between bots."""
    
    def __init__(self):
        self.config_dir = Path("/home/runner/work/The-basics/The-basics/config")
        self.config_dir.mkdir(exist_ok=True)
        
        self.shared_pool_file = self.config_dir / "shared_credential_pool.json"
        self.credential_requests_file = self.config_dir / "credential_requests.json"
        
        self.shared_pool: Dict[str, Any] = self._load_shared_pool()
        self.credential_requests: List[Dict] = self._load_requests()
    
    def _load_shared_pool(self) -> Dict[str, Any]:
        """Load the shared credential pool."""
        if self.shared_pool_file.exists():
            return json.loads(self.shared_pool_file.read_text())
        return {
            "credentials": {},
            "discovery_log": [],
            "last_updated": datetime.now().isoformat()
        }
    
    def _save_shared_pool(self) -> None:
        """Save the shared credential pool."""
        self.shared_pool["last_updated"] = datetime.now().isoformat()
        self.shared_pool_file.write_text(json.dumps(self.shared_pool, indent=2))
    
    def _load_requests(self) -> List[Dict]:
        """Load pending credential requests."""
        if self.credential_requests_file.exists():
            return json.loads(self.credential_requests_file.read_text())
        return []
    
    def _save_requests(self) -> None:
        """Save credential requests."""
        self.credential_requests_file.write_text(json.dumps(self.credential_requests, indent=2))
    
    def bot_discovered_credential(
        self, 
        bot_id: str, 
        credential_type: str, 
        credential_key: str, 
        credential_value: str,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        A bot shares a newly discovered credential with the network.
        
        Args:
            bot_id: ID of the bot that discovered the credential
            credential_type: Type of credential (api_key, token, etc.)
            credential_key: Key/name of the credential
            credential_value: The actual credential value
            metadata: Optional metadata about the credential
            
        Returns:
            Result of sharing the credential
        """
        cred_id = f"{credential_type}_{credential_key}".lower().replace(" ", "_")
        
        # Add to shared pool
        self.shared_pool["credentials"][cred_id] = {
            "type": credential_type,
            "key": credential_key,
            "value": credential_value,
            "discovered_by": bot_id,
            "discovered_at": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        # Log the discovery
        self.shared_pool["discovery_log"].append({
            "bot_id": bot_id,
            "credential_id": cred_id,
            "timestamp": datetime.now().isoformat()
        })
        
        self._save_shared_pool()
        
        # Broadcast to other bots
        self._broadcast_credential(cred_id)
        
        # Try to fulfill pending requests
        self._fulfill_requests(credential_type)
        
        print(f"✅ Bot {bot_id} shared {credential_type}: {credential_key}")
        
        return {
            "success": True,
            "credential_id": cred_id,
            "shared_at": datetime.now().isoformat()
        }
    
    def bot_request_credential(
        self, 
        bot_id: str, 
        credential_type: str, 
        credential_key: Optional[str] = None,
        required: bool = True
    ) -> Dict[str, Any]:
        """
        A bot requests a credential from the shared pool.
        
        Args:
            bot_id: ID of the requesting bot
            credential_type: Type of credential needed
            credential_key: Specific key if known (optional)
            required: Whether the credential is required for bot operation
            
        Returns:
            The credential if found, or request confirmation if not
        """
        # Search shared pool for matching credential
        for cred_id, cred_data in self.shared_pool["credentials"].items():
            if cred_data["type"] == credential_type:
                if credential_key is None or cred_data["key"] == credential_key:
                    print(f"✅ Fulfilled request from {bot_id} for {credential_type}")
                    return {
                        "success": True,
                        "credential": cred_data,
                        "credential_id": cred_id
                    }
        
        # Credential not found - add to request queue
        request = {
            "bot_id": bot_id,
            "credential_type": credential_type,
            "credential_key": credential_key,
            "required": required,
            "requested_at": datetime.now().isoformat(),
            "fulfilled": False
        }
        
        self.credential_requests.append(request)
        self._save_requests()
        
        print(f"⏳ Queued request from {bot_id} for {credential_type}")
        
        return {
            "success": False,
            "message": "Credential not available - request queued",
            "request": request
        }
    
    def auto_fill_bot_config(self, bot_id: str, required_credentials: List[str]) -> Dict[str, Any]:
        """
        Auto-configure a bot with credentials from the shared pool.
        
        Args:
            bot_id: ID of the bot to configure
            required_credentials: List of required credential types
            
        Returns:
            Configuration with available credentials
        """
        bot_config = {
            "bot_id": bot_id,
            "configured_at": datetime.now().isoformat(),
            "credentials": {},
            "missing_credentials": []
        }
        
        for cred_type in required_credentials:
            result = self.bot_request_credential(bot_id, cred_type, required=True)
            
            if result["success"]:
                bot_config["credentials"][cred_type] = result["credential"]
            else:
                bot_config["missing_credentials"].append(cred_type)
        
        # Save bot-specific config
        bot_config_file = self.config_dir / f"{bot_id}_auto_config.json"
        bot_config_file.write_text(json.dumps(bot_config, indent=2))
        
        print(f"🤖 Auto-configured {bot_id} with {len(bot_config['credentials'])} credentials")
        
        return bot_config
    
    def _broadcast_credential(self, credential_id: str) -> None:
        """Broadcast a credential to all interested bots."""
        # In a real system, this would use WebSockets or message queue
        # For now, it's a placeholder that updates the shared pool
        pass
    
    def _fulfill_requests(self, credential_type: str) -> None:
        """Try to fulfill pending requests for a credential type."""
        fulfilled = []
        
        for idx, request in enumerate(self.credential_requests):
            if not request["fulfilled"] and request["credential_type"] == credential_type:
                # Try to fulfill this request
                result = self.bot_request_credential(
                    request["bot_id"],
                    credential_type,
                    request.get("credential_key")
                )
                
                if result["success"]:
                    request["fulfilled"] = True
                    request["fulfilled_at"] = datetime.now().isoformat()
                    fulfilled.append(idx)
        
        if fulfilled:
            self._save_requests()
            print(f"✅ Fulfilled {len(fulfilled)} pending requests")
    
    def get_shared_pool_status(self) -> Dict[str, Any]:
        """Get status of the shared credential pool."""
        return {
            "total_credentials": len(self.shared_pool["credentials"]),
            "pending_requests": len([r for r in self.credential_requests if not r["fulfilled"]]),
            "total_discoveries": len(self.shared_pool["discovery_log"]),
            "last_updated": self.shared_pool["last_updated"]
        }
    
    def import_from_scanner(self, scanner_credentials: Dict[str, Any]) -> int:
        """
        Import credentials discovered by the autonomous scanner.
        
        Args:
            scanner_credentials: Credentials from autonomous_credential_scanner
            
        Returns:
            Number of credentials imported
        """
        imported = 0
        
        for cred_id, cred_data in scanner_credentials.items():
            if cred_id not in self.shared_pool["credentials"]:
                self.bot_discovered_credential(
                    bot_id="autonomous_scanner",
                    credential_type=cred_data.get("type", "unknown"),
                    credential_key=cred_data.get("key", cred_id),
                    credential_value=cred_data.get("value", ""),
                    metadata={
                        "source": cred_data.get("source", "scanner"),
                        "discovered_at": cred_data.get("discovered_at")
                    }
                )
                imported += 1
        
        print(f"📥 Imported {imported} credentials from scanner")
        
        return imported


# Global instance
credential_sharing = BotCredentialSharing()


async def main():
    """Test credential sharing."""
    # Test bot discovering a credential
    result1 = credential_sharing.bot_discovered_credential(
        bot_id="quantum_bot",
        credential_type="api_key",
        credential_key="NDAX_API_KEY",
        credential_value="test_key_12345"
    )
    print(f"Discovery result: {result1}")
    
    # Test bot requesting a credential
    result2 = credential_sharing.bot_request_credential(
        bot_id="shadowforge_bot",
        credential_type="api_key"
    )
    print(f"Request result: {result2}")
    
    # Test auto-fill
    result3 = credential_sharing.auto_fill_bot_config(
        bot_id="new_bot",
        required_credentials=["api_key", "secret_key"]
    )
    print(f"Auto-fill result: {result3}")
    
    # Get status
    status = credential_sharing.get_shared_pool_status()
    print(f"Pool status: {status}")


if __name__ == "__main__":
    asyncio.run(main())
