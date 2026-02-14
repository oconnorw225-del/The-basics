"""
AUTONOMOUS CREDENTIAL SCANNER
Scans all GitHub repositories, workflow artifacts, and environment for credentials.
Auto-configures all bots with discovered credentials.
"""

import os
import json
import re
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import aiohttp


class AutonomousCredentialScanner:
    """Scans for credentials across all sources and auto-configures bots."""
    
    def __init__(self):
        self.config_dir = Path("/home/runner/work/The-basics/The-basics/config")
        self.config_dir.mkdir(exist_ok=True)
        
        self.repos_to_scan = [
            "ndax-quantum-engine",
            "quantum-engine-dashb", 
            "shadowforge-ai-trader",
            "repository-web-app",
            "The-new-ones"
        ]
        
        self.credential_patterns = {
            "api_key": r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\']?([a-zA-Z0-9_-]{20,})["\']?',
            "access_token": r'(?i)(access[_-]?token|token)\s*[:=]\s*["\']?([a-zA-Z0-9_.-]{20,})["\']?',
            "secret_key": r'(?i)(secret[_-]?key|secret)\s*[:=]\s*["\']?([a-zA-Z0-9_-]{20,})["\']?',
            "wallet_seed": r'(?i)(seed|mnemonic)\s*[:=]\s*["\']?([a-z\s]{50,})["\']?',
            "private_key": r'(?i)(private[_-]?key|priv[_-]?key)\s*[:=]\s*["\']?([a-fA-F0-9]{64})["\']?',
            "mtgox_claim": r'(?i)(mtgox|claim[_-]?id)\s*[:=]\s*["\']?([a-zA-Z0-9-]{10,})["\']?',
            "exchange_key": r'(?i)(ndax|binance|coinbase)[_-]?(api[_-]?key|key)\s*[:=]\s*["\']?([a-zA-Z0-9_-]{20,})["\']?',
        }
        
        self.discovered_credentials: Dict[str, Any] = {}
        self.gatekeeper_credentials = ["github_token", "main_wallet_key"]
        
    async def scan_everything(self) -> Dict[str, Any]:
        """Main scan orchestrator - scans all sources for credentials."""
        print("🔍 Starting comprehensive credential scan...")
        
        results = {
            "scan_time": datetime.now().isoformat(),
            "credentials_found": 0,
            "sources_scanned": 0,
            "gatekeeper_status": {},
            "auto_configured_bots": []
        }
        
        # Scan all sources in parallel
        scan_tasks = [
            self.scan_github_repos(),
            self.scan_environment_variables(),
            self.scan_local_config_files(),
            self.scan_workflow_artifacts(),
        ]
        
        scan_results = await asyncio.gather(*scan_tasks, return_exceptions=True)
        
        # Process results
        for result in scan_results:
            if isinstance(result, Exception):
                print(f"⚠️ Scan error: {result}")
                continue
            if result:
                results["sources_scanned"] += result.get("sources", 0)
                results["credentials_found"] += result.get("found", 0)
        
        # Save discovered credentials
        await self.save_discovered_credentials()
        
        # Auto-configure bots
        configured = await self.auto_configure_bots()
        results["auto_configured_bots"] = configured
        
        # Check gatekeeper credentials
        results["gatekeeper_status"] = self.check_gatekeeper_credentials()
        
        print(f"✅ Scan complete: {results['credentials_found']} credentials from {results['sources_scanned']} sources")
        
        return results
    
    async def scan_github_repos(self) -> Dict[str, Any]:
        """Scan GitHub repositories for credentials."""
        print("📂 Scanning GitHub repositories...")
        
        result = {"sources": len(self.repos_to_scan), "found": 0}
        github_token = os.getenv("GITHUB_TOKEN")
        
        if not github_token:
            print("⚠️ No GITHUB_TOKEN found - skipping repo scan")
            return result
        
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        async with aiohttp.ClientSession(headers=headers) as session:
            for repo in self.repos_to_scan:
                try:
                    # Scan repo files
                    found = await self._scan_repo_files(session, repo)
                    result["found"] += found
                except Exception as e:
                    print(f"⚠️ Error scanning {repo}: {e}")
        
        return result
    
    async def _scan_repo_files(self, session: aiohttp.ClientSession, repo: str) -> int:
        """Scan files in a repository for credentials."""
        owner = "oconnorw225-del"  # Your GitHub username
        url = f"https://api.github.com/repos/{owner}/{repo}/contents"
        
        found_count = 0
        
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    files = await response.json()
                    
                    # Look for common config files
                    config_files = [f for f in files if f.get("name") in [
                        ".env", ".env.example", "config.json", "credentials.json",
                        "secrets.json", ".env.local", "config.yaml"
                    ]]
                    
                    for file in config_files:
                        if file.get("type") == "file":
                            file_url = file.get("download_url")
                            if file_url:
                                async with session.get(file_url) as file_resp:
                                    if file_resp.status == 200:
                                        content = await file_resp.text()
                                        found = self._extract_credentials(content, f"{repo}/{file['name']}")
                                        found_count += found
        
        except Exception as e:
            print(f"Error scanning repo {repo}: {e}")
        
        return found_count
    
    def _extract_credentials(self, content: str, source: str) -> int:
        """Extract credentials from content using regex patterns."""
        found_count = 0
        
        for cred_type, pattern in self.credential_patterns.items():
            matches = re.finditer(pattern, content)
            for match in matches:
                if len(match.groups()) >= 2:
                    key = match.group(1)
                    value = match.group(2)
                    
                    if value and len(value) > 10:  # Minimum length check
                        cred_id = f"{cred_type}_{key}".lower().replace(" ", "_")
                        
                        self.discovered_credentials[cred_id] = {
                            "type": cred_type,
                            "key": key,
                            "value": value,
                            "source": source,
                            "discovered_at": datetime.now().isoformat()
                        }
                        
                        found_count += 1
                        print(f"  ✓ Found {cred_type} from {source}")
        
        return found_count
    
    async def scan_environment_variables(self) -> Dict[str, Any]:
        """Scan environment variables for credentials."""
        print("🔐 Scanning environment variables...")
        
        result = {"sources": 1, "found": 0}
        
        # Look for credential-related env vars
        cred_env_vars = [
            "GITHUB_TOKEN", "SENDGRID_API_KEY", "NDAX_API_KEY", "NDAX_SECRET",
            "BINANCE_API_KEY", "BINANCE_SECRET", "WALLET_SEED", "PRIVATE_KEY",
            "MTGOX_CLAIM_ID", "DATABASE_URL", "REDIS_URL"
        ]
        
        for env_var in cred_env_vars:
            value = os.getenv(env_var)
            if value:
                self.discovered_credentials[env_var.lower()] = {
                    "type": "environment_variable",
                    "key": env_var,
                    "value": value,
                    "source": "environment",
                    "discovered_at": datetime.now().isoformat()
                }
                result["found"] += 1
                print(f"  ✓ Found {env_var}")
        
        return result
    
    async def scan_local_config_files(self) -> Dict[str, Any]:
        """Scan local configuration files for credentials."""
        print("📋 Scanning local config files...")
        
        result = {"sources": 0, "found": 0}
        
        # Scan current directory and common config locations
        base_path = Path("/home/runner/work/The-basics/The-basics")
        config_files = [
            base_path / ".env",
            base_path / ".env.local",
            base_path / "config" / "credentials.json",
            base_path / "config" / "secrets.json",
        ]
        
        for config_file in config_files:
            if config_file.exists():
                result["sources"] += 1
                try:
                    content = config_file.read_text()
                    found = self._extract_credentials(content, str(config_file.name))
                    result["found"] += found
                except Exception as e:
                    print(f"⚠️ Error reading {config_file}: {e}")
        
        return result
    
    async def scan_workflow_artifacts(self) -> Dict[str, Any]:
        """Scan GitHub Actions workflow artifacts for credentials."""
        print("⚙️ Scanning workflow artifacts...")
        
        result = {"sources": 0, "found": 0}
        
        # Note: Actual artifact scanning requires GitHub API access
        # This is a placeholder for the scanning logic
        github_token = os.getenv("GITHUB_TOKEN")
        
        if not github_token:
            print("⚠️ No GITHUB_TOKEN - skipping artifact scan")
            return result
        
        # In a real implementation, this would:
        # 1. List workflow runs
        # 2. Download artifacts
        # 3. Scan artifact contents
        # For now, we'll note this capability exists
        
        return result
    
    async def save_discovered_credentials(self) -> None:
        """Save discovered credentials to config files."""
        print("💾 Saving discovered credentials...")
        
        # Save all discovered credentials
        creds_file = self.config_dir / "auto_discovered_credentials.json"
        creds_file.write_text(json.dumps(self.discovered_credentials, indent=2))
        
        # Extract and save wallets
        wallets = {k: v for k, v in self.discovered_credentials.items() 
                   if "wallet" in k or "address" in k or "seed" in k}
        if wallets:
            wallets_file = self.config_dir / "wallets.json"
            wallets_file.write_text(json.dumps(wallets, indent=2))
        
        # Extract and save MtGox credentials
        mtgox = {k: v for k, v in self.discovered_credentials.items() 
                 if "mtgox" in k or "claim" in k}
        if mtgox:
            mtgox_file = self.config_dir / "mtgox_credentials.json"
            mtgox_file.write_text(json.dumps(mtgox, indent=2))
        
        # Extract and save exchange credentials
        for exchange in ["ndax", "binance", "coinbase"]:
            exchange_creds = {k: v for k, v in self.discovered_credentials.items() 
                             if exchange in k.lower()}
            if exchange_creds:
                exchange_file = self.config_dir / f"{exchange}_config.json"
                exchange_file.write_text(json.dumps(exchange_creds, indent=2))
        
        print(f"  ✓ Saved {len(self.discovered_credentials)} credentials to config/")
    
    async def auto_configure_bots(self) -> List[str]:
        """Auto-configure bots with discovered credentials."""
        print("🤖 Auto-configuring bots...")
        
        configured_bots = []
        
        # Create a general bot config with all credentials
        bot_config = {
            "auto_configured": True,
            "configured_at": datetime.now().isoformat(),
            "credentials": self.discovered_credentials
        }
        
        config_file = self.config_dir / "bot_auto_config.json"
        config_file.write_text(json.dumps(bot_config, indent=2))
        
        configured_bots.append("general_bot_config")
        
        print(f"  ✓ Configured {len(configured_bots)} bot configs")
        
        return configured_bots
    
    def check_gatekeeper_credentials(self) -> Dict[str, bool]:
        """Check if critical gatekeeper credentials are present."""
        status = {}
        
        for gatekeeper in self.gatekeeper_credentials:
            # Check if credential exists in discovered credentials
            found = any(gatekeeper.lower() in key.lower() 
                       for key in self.discovered_credentials.keys())
            status[gatekeeper] = found
            
            if not found:
                print(f"⚠️ Missing gatekeeper credential: {gatekeeper}")
        
        return status
    
    async def rescan(self) -> Dict[str, Any]:
        """Perform a rescan of all sources."""
        print("🔄 Performing credential rescan...")
        return await self.scan_everything()


# Global instance
credential_scanner = AutonomousCredentialScanner()


async def main():
    """Test the credential scanner."""
    result = await credential_scanner.scan_everything()
    print(f"\n📊 Scan Results:")
    print(f"  • Credentials found: {result['credentials_found']}")
    print(f"  • Sources scanned: {result['sources_scanned']}")
    print(f"  • Bots configured: {len(result['auto_configured_bots'])}")
    print(f"  • Gatekeeper status: {result['gatekeeper_status']}")


if __name__ == "__main__":
    asyncio.run(main())
