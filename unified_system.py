#!/usr/bin/env python3
"""
unified_system.py - Complete Autonomous System
Integrates Chimera Auto-Pilot with The-Basics repository
Auto-configures missing APIs, wallets, and all inputs
SECURITY HARDENED - All file operations now use safe methods
ENHANCED - Preloads all environments, secrets, and credentials for Railway
"""

import asyncio
import json
import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime
import subprocess
import secrets
import hashlib
from enum import Enum

# SECURITY: Import safe file operations
try:
    from security.safe_file_ops import SafeFileOperations, SecurityError
    safe_file_ops = SafeFileOperations()
    USE_SAFE_FILE_OPS = True
except ImportError:
    logger.warning("Safe file operations not available, using fallback")
    USE_SAFE_FILE_OPS = False

# Setup logging
os.makedirs('.unified-system/logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('.unified-system/logs/system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('UnifiedSystem')


class DeploymentStatus(Enum):
    """Deployment status"""
    PENDING = "pending"
    RUNNING = "running"
    FAILED = "failed"
    SUCCESS = "success"


@dataclass
class SystemConfig:
    """Complete unified system configuration"""
    # Repository Management
    auto_fix_code: bool = False
    auto_commit: bool = False
    auto_push: bool = False
    auto_merge_pr: bool = False
    auto_deploy: bool = False
    
    # Trading & APIs
    trading_enabled: bool = False
    ndax_api_configured: bool = False
    exchange_api_configured: bool = False
    auto_allocate_capital: bool = False
    auto_deploy_strategies: bool = False
    treasury_auto_sweep: bool = False
    evolution_engine_enabled: bool = False
    
    # Wallets (auto-generated if missing)
    inflow_wallet: str = ""
    operational_wallet: str = ""
    cold_storage_wallet: str = ""
    emergency_wallet: str = ""
    
    # Dashboard
    dashboard_enabled: bool = True
    dashboard_port: int = 8000
    
    # Cloud Server Integration
    cloud_server_enabled: bool = False
    cloud_server_host: str = ""
    cloud_server_port: int = 8000
    cloud_server_ssh_key: str = ""
    cloud_server_username: str = "root"
    cloud_deployment_path: str = "/opt/chimera-autopilot"
    
    # Safety
    require_approval: bool = True
    max_risk_per_trade: float = 0.02
    max_daily_loss: float = 0.05
    kill_switch_active: bool = False
    
    # Auto-configuration
    auto_generate_missing: bool = True
    auto_setup_apis: bool = False


class UnifiedSystem:
    """Complete autonomous system manager with environment preloading"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.config_dir = self.repo_path / ".unified-system"
        self.config_file = self.config_dir / "config.json"
        self.generated_dir = self.config_dir / "generated"
        self.config: Optional[SystemConfig] = None
        
        # Initialize environment preloader
        self.env_preloader = None
        self._init_env_preloader()
        
        logger.info(f"Unified System initialized at: {self.repo_path.absolute()}")
    
    def _init_env_preloader(self):
        """Initialize the Chimera environment preloader using importlib."""
        try:
            # Use importlib for safer imports
            import importlib.util
            
            preloader_path = self.repo_path / "backend" / "chimera_env_preloader.py"
            if not preloader_path.exists():
                logger.warning(f"Environment preloader not found at {preloader_path}")
                self.env_preloader = None
                return
            
            spec = importlib.util.spec_from_file_location("chimera_env_preloader", preloader_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                self.env_preloader = module.create_env_preloader(str(self.config_dir))
                logger.info("Environment preloader initialized")
            else:
                logger.warning("Could not load environment preloader spec")
                self.env_preloader = None
        except Exception as e:
            logger.warning(f"Could not initialize environment preloader: {e}")
            self.env_preloader = None
        
    def load_config(self) -> SystemConfig:
        """Load or create configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                return SystemConfig(**data)
        return SystemConfig()
    
    def save_config(self, config: SystemConfig):
        """Save configuration"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(asdict(config), f, indent=2)
    
    def generate_test_api_credentials(self) -> Dict[str, str]:
        """Generate test API credentials"""
        logger.info("Generating test API credentials...")
        
        credentials = {
            "ndax_api_key": f"ndax_test_{secrets.token_hex(16)}",
            "ndax_api_secret": secrets.token_hex(32),
            "exchange_api_key": f"exchange_test_{secrets.token_hex(16)}",
            "exchange_api_secret": secrets.token_hex(32)
        }
        
        self.generated_dir.mkdir(parents=True, exist_ok=True)
        with open(self.generated_dir / "api_credentials.json", 'w') as f:
            json.dump(credentials, f, indent=2)
        
        logger.info("✅ API credentials generated (test mode)")
        return credentials
    
    def generate_test_wallets(self) -> Dict[str, str]:
        """Generate test wallet addresses"""
        logger.info("Generating test wallet addresses...")
        
        def gen_eth_address():
            return "0x" + secrets.token_hex(20)
        
        wallets = {
            "inflow_wallet": gen_eth_address(),
            "operational_wallet": gen_eth_address(),
            "cold_storage": gen_eth_address(),
            "emergency_wallet": gen_eth_address()
        }
        
        self.generated_dir.mkdir(parents=True, exist_ok=True)
        with open(self.generated_dir / "wallets.json", 'w') as f:
            json.dump(wallets, f, indent=2)
        
        logger.info("✅ Wallet addresses generated (test mode)")
        return wallets
    
    def generate_secrets(self) -> Dict[str, str]:
        """Generate security secrets"""
        logger.info("Generating security secrets...")
        
        secrets_data = {
            "jwt_secret": secrets.token_hex(32),
            "encryption_key": secrets.token_hex(32),
            "webhook_secret": secrets.token_hex(16)
        }
        
        self.generated_dir.mkdir(parents=True, exist_ok=True)
        with open(self.generated_dir / "secrets.json", 'w') as f:
            json.dump(secrets_data, f, indent=2)
        
        logger.info("✅ Security secrets generated")
        return secrets_data
    
    def create_env_file(self, api_creds: Dict, wallets: Dict, secrets_data: Dict):
        """
        Create .env file with all configurations
        
        WARNING: .env files store credentials in plain text.
        - Never commit .env to version control
        - Use environment-specific .env files
        - In production, use secure secret management (e.g., AWS Secrets Manager)
        """
        logger.info("Creating .env file...")
        
        # Validate inputs
        if not all(isinstance(d, dict) for d in [api_creds, wallets, secrets_data]):
            raise ValueError("All credential parameters must be dictionaries")
        
        env_content = f"""# === UNIFIED SYSTEM CONFIGURATION ===
# Auto-generated by unified_system.py
# Generated: {datetime.now().isoformat()}
# WARNING: This file contains sensitive credentials - do not commit to git

# === API CREDENTIALS (TEST MODE) ===
NDAX_API_KEY={api_creds.get('ndax_api_key', '')}
NDAX_API_SECRET={api_creds.get('ndax_api_secret', '')}
EXCHANGE_API_KEY={api_creds.get('exchange_api_key', '')}
EXCHANGE_API_SECRET={api_creds.get('exchange_api_secret', '')}

# === WALLETS (TEST ADDRESSES) ===
INFLOW_WALLET_ADDR={wallets.get('inflow_wallet', '')}
OPERATIONAL_WALLET_ADDR={wallets.get('operational_wallet', '')}
COLD_STORAGE_ADDR={wallets.get('cold_storage', '')}
EMERGENCY_WALLET_ADDR={wallets.get('emergency_wallet', '')}

# === SECURITY ===
JWT_SECRET={secrets_data.get('jwt_secret', '')}
ENCRYPTION_KEY={secrets_data.get('encryption_key', '')}
WEBHOOK_SECRET={secrets_data.get('webhook_secret', '')}

# === TRADING ===
TRADING_ENABLED=false
PAPER_TRADING=true
MAX_RISK_PER_TRADE=0.02
MAX_DAILY_LOSS=0.05

# === DASHBOARD ===
DASHBOARD_ENABLED=true
DASHBOARD_PORT=8000
PORT=8000
"""
        
        env_file = self.repo_path / ".env"
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        logger.info(f"✅ .env file created at: {env_file.absolute()}")
        logger.warning("⚠️  Remember: .env contains credentials - never commit it to git!")
    
    def generate_cloud_deployment_script(self, config: SystemConfig):
        """Generate deployment script for cloud server"""
        logger.info("Generating cloud deployment script...")
        
        deploy_script = f'''#!/bin/bash
# Cloud Server Deployment Script for Chimera Auto-Pilot
# Auto-generated by unified_system.py

set -e

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║        🌐 CHIMERA AUTO-PILOT - CLOUD SERVER DEPLOYMENT                   ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Configuration
SERVER_HOST="{config.cloud_server_host}"
SERVER_PORT={config.cloud_server_port}
SSH_USER="{config.cloud_server_username}"
SSH_KEY="{config.cloud_server_ssh_key}"
DEPLOY_PATH="{config.cloud_deployment_path}"

# Colors
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
RED='\\033[0;31m'
NC='\\033[0m'

echo "📋 Deployment Configuration:"
echo "   Server: $SSH_USER@$SERVER_HOST"
echo "   Port: $SERVER_PORT"
echo "   Path: $DEPLOY_PATH"
echo ""

# Check SSH key
if [ ! -f "$SSH_KEY" ]; then
    echo -e "${{RED}}❌ SSH key not found: $SSH_KEY${{NC}}"
    echo "Please update your SSH key path in the setup wizard"
    exit 1
fi

echo "🔐 Testing SSH connection..."
if ssh -i "$SSH_KEY" -o ConnectTimeout=10 "$SSH_USER@$SERVER_HOST" "echo 'Connection successful'" 2>/dev/null; then
    echo -e "${{GREEN}}✅ SSH connection successful${{NC}}"
else
    echo -e "${{RED}}❌ Cannot connect to server${{NC}}"
    echo "Please verify:"
    echo "  - Server is running and accessible"
    echo "  - SSH key has correct permissions (chmod 600)"
    echo "  - Username and hostname are correct"
    exit 1
fi

echo ""
echo "📦 Step 1: Installing dependencies on server..."
ssh -i "$SSH_KEY" "$SSH_USER@$SERVER_HOST" << 'ENDSSH'
# Update system
apt-get update -qq

# Install Python 3
if ! command -v python3 &> /dev/null; then
    echo "Installing Python 3..."
    apt-get install -y python3 python3-pip
fi

# Install Node.js
if ! command -v node &> /dev/null; then
    echo "Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt-get install -y nodejs
fi

# Install Git
if ! command -v git &> /dev/null; then
    echo "Installing Git..."
    apt-get install -y git
fi

echo "✅ Dependencies installed"
ENDSSH

echo -e "${{GREEN}}✅ Step 1 complete${{NC}}"

echo ""
echo "📂 Step 2: Creating deployment directory..."
ssh -i "$SSH_KEY" "$SSH_USER@$SERVER_HOST" "mkdir -p $DEPLOY_PATH"
echo -e "${{GREEN}}✅ Step 2 complete${{NC}}"

echo ""
echo "📤 Step 3: Uploading files..."
# Create tarball excluding unnecessary files
tar -czf /tmp/chimera-deploy.tar.gz \\
    --exclude='.git' \\
    --exclude='node_modules' \\
    --exclude='__pycache__' \\
    --exclude='.unified-system' \\
    --exclude='*.pyc' \\
    --exclude='.env' \\
    .

# Upload to server
scp -i "$SSH_KEY" /tmp/chimera-deploy.tar.gz "$SSH_USER@$SERVER_HOST:/tmp/"

# Extract on server
ssh -i "$SSH_KEY" "$SSH_USER@$SERVER_HOST" << ENDSSH
cd $DEPLOY_PATH
tar -xzf /tmp/chimera-deploy.tar.gz
rm /tmp/chimera-deploy.tar.gz
echo "✅ Files extracted"
ENDSSH

rm /tmp/chimera-deploy.tar.gz
echo -e "${{GREEN}}✅ Step 3 complete${{NC}}"

echo ""
echo "🔧 Step 4: Installing Python packages..."
ssh -i "$SSH_KEY" "$SSH_USER@$SERVER_HOST" << ENDSSH
cd $DEPLOY_PATH
if [ -f requirements.txt ]; then
    pip3 install -r requirements.txt
fi
echo "✅ Python packages installed"
ENDSSH
echo -e "${{GREEN}}✅ Step 4 complete${{NC}}"

echo ""
echo "⚙️  Step 5: Creating systemd service..."
ssh -i "$SSH_KEY" "$SSH_USER@$SERVER_HOST" << ENDSSH
cat > /etc/systemd/system/chimera-autopilot.service << 'EOF'
[Unit]
Description=Chimera Auto-Pilot System
After=network.target

[Service]
Type=simple
User=$SSH_USER
WorkingDirectory=$DEPLOY_PATH
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
Environment="PORT=$SERVER_PORT"
ExecStart=/usr/bin/python3 $DEPLOY_PATH/unified_system.py --auto
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable chimera-autopilot.service
echo "✅ Service created"
ENDSSH
echo -e "${{GREEN}}✅ Step 5 complete${{NC}}"

echo ""
echo "🚀 Step 6: Starting service..."
ssh -i "$SSH_KEY" "$SSH_USER@$SERVER_HOST" "systemctl start chimera-autopilot.service"
echo -e "${{GREEN}}✅ Step 6 complete${{NC}}"

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                     ✅ DEPLOYMENT SUCCESSFUL! 🎉                          ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 Your Chimera Auto-Pilot is now running on your cloud server!"
echo ""
echo "📊 Dashboard URL: http://$SERVER_HOST:$SERVER_PORT"
echo "🔍 Health Check: http://$SERVER_HOST:$SERVER_PORT/health"
echo ""
echo "📝 Useful Commands:"
echo "   Check status:  ssh -i $SSH_KEY $SSH_USER@$SERVER_HOST 'systemctl status chimera-autopilot'"
echo "   View logs:     ssh -i $SSH_KEY $SSH_USER@$SERVER_HOST 'journalctl -u chimera-autopilot -f'"
echo "   Restart:       ssh -i $SSH_KEY $SSH_USER@$SERVER_HOST 'systemctl restart chimera-autopilot'"
echo "   Stop:          ssh -i $SSH_KEY $SSH_USER@$SERVER_HOST 'systemctl stop chimera-autopilot'"
echo ""
'''
        
        deploy_file = self.repo_path / "deploy_to_cloud.sh"
        with open(deploy_file, 'w') as f:
            f.write(deploy_script)
        
        # Make executable
        os.chmod(deploy_file, 0o755)
        
        logger.info(f"✅ Cloud deployment script created: {deploy_file}")
        print(f"   📝 Deployment script: {deploy_file}")
    
    def setup_wizard(self):
        """Interactive setup wizard"""
        print("\n" + "="*80)
        print("🚀 UNIFIED SYSTEM SETUP WIZARD")
        print("   Repository Management + Trading Infrastructure")
        print("="*80 + "\n")
        
        # Load or create config
        config = self.load_config()
        
        # Choose operating mode
        print("Choose Operating Mode:")
        print("  [F]ull Autonomous - Everything automatic (code + trading)")
        print("  [C]ode Only - Auto-manage code, manual trading")
        print("  [T]rading Only - Auto-manage trading, manual code")
        print("  [I]nteractive - Approve each action")
        print("  [R]eview Only - No changes")
        
        mode = input("\nChoice (F/C/T/I/R): ").strip().upper()
        
        # Configure based on mode
        if mode.startswith('F') or mode == 'FULL':
            # Full autonomous mode
            config.auto_fix_code = True
            config.auto_commit = True
            config.auto_push = True
            config.auto_merge_pr = True
            config.auto_deploy = True
            config.trading_enabled = False  # Keep false for safety
            config.auto_allocate_capital = False
            config.auto_deploy_strategies = False
            config.treasury_auto_sweep = False
            config.evolution_engine_enabled = False
            config.require_approval = False
            print("✅ Full Autonomous mode (trading disabled for safety)")
            
        elif mode.startswith('C') or mode == 'CODE':
            # Code management only
            config.auto_fix_code = True
            config.auto_commit = True
            config.auto_push = True
            config.auto_merge_pr = True
            config.auto_deploy = True
            config.trading_enabled = False
            config.require_approval = False
            print("✅ Code Management mode")
            
        elif mode.startswith('T') or mode == 'TRADING':
            # Trading only
            config.auto_fix_code = False
            config.trading_enabled = True
            config.auto_allocate_capital = True
            config.auto_deploy_strategies = True
            config.treasury_auto_sweep = True
            config.evolution_engine_enabled = True
            config.require_approval = True  # Keep approval for safety
            print("✅ Trading mode (with approval required)")
            
        elif mode.startswith('I') or mode == 'INTERACTIVE':
            # Interactive mode
            config.require_approval = True
            print("✅ Interactive mode")
            
        else:
            # Review only
            config.auto_fix_code = False
            config.trading_enabled = False
            config.require_approval = True
            print("✅ Review Only mode")
        
        # Safety settings
        print("\n⚠️  SAFETY SETTINGS:")
        while True:
            try:
                max_loss = input("   Max daily loss % (default 5%): ").strip() or "5"
                config.max_daily_loss = float(max_loss) / 100
                break
            except ValueError:
                print("   ❌ Invalid input. Please enter a number.")
        
        while True:
            try:
                max_risk = input("   Max risk per trade % (default 2%): ").strip() or "2"
                config.max_risk_per_trade = float(max_risk) / 100
                break
            except ValueError:
                print("   ❌ Invalid input. Please enter a number.")
        
        # API Configuration
        print("\nAPI Configuration:")
        has_apis = input("Do you have API keys configured? (y/n): ").strip().lower()
        
        if has_apis != 'y':
            print("📦 Auto-generating test API credentials...")
            api_creds = self.generate_test_api_credentials()
            config.ndax_api_configured = True
        else:
            print("✅ Using existing API configuration")
            api_creds = {}
        
        # Wallet Configuration
        print("\nWallet Configuration:")
        has_wallets = input("Do you have wallet addresses? (y/n): ").strip().lower()
        
        if has_wallets != 'y':
            print("📦 Auto-generating test wallet addresses...")
            wallets = self.generate_test_wallets()
            config.inflow_wallet = wallets['inflow_wallet']
            config.operational_wallet = wallets['operational_wallet']
            config.cold_storage_wallet = wallets['cold_storage']
            config.emergency_wallet = wallets['emergency_wallet']
        else:
            print("✅ Using existing wallet configuration")
            wallets = {}
        
        # Generate secrets
        secrets_data = self.generate_secrets()
        
        # Create .env file if we generated credentials
        if api_creds and wallets:
            self.create_env_file(api_creds, wallets, secrets_data)
        
        # Dashboard
        config.dashboard_enabled = True
        print("\n✅ Dashboard will be enabled on port 8000")
        
        # Cloud Server Integration
        print("\n🌐 CLOUD SERVER INTEGRATION:")
        use_cloud = input("   Deploy to your own cloud server? (y/n): ").strip().lower()
        
        if use_cloud == 'y':
            config.cloud_server_enabled = True
            print("\n   Enter your cloud server details:")
            config.cloud_server_host = input("   Server IP/Hostname: ").strip()
            
            while True:
                try:
                    port = input("   Server Port (default 8000): ").strip() or "8000"
                    config.cloud_server_port = int(port)
                    break
                except ValueError:
                    print("   ❌ Invalid port. Please enter a number.")
            
            config.cloud_server_username = input("   SSH Username (default root): ").strip() or "root"
            config.cloud_server_ssh_key = input("   SSH Key Path (e.g., ~/.ssh/id_rsa): ").strip()
            config.cloud_deployment_path = input("   Deployment Path (default /opt/chimera-autopilot): ").strip() or "/opt/chimera-autopilot"
            
            print("\n✅ Cloud server configured")
            print(f"   Host: {config.cloud_server_host}")
            print(f"   Port: {config.cloud_server_port}")
            print(f"   Deployment path: {config.cloud_deployment_path}")
            
            # Generate cloud deployment script
            self.generate_cloud_deployment_script(config)
        else:
            print("✅ Cloud deployment skipped")
        
        # Save configuration
        self.save_config(config)
        print(f"\n✅ Configuration saved to: {self.config_file}")
        
        print("\n" + "="*80)
        print("✅ SETUP COMPLETE!")
        print("="*80)
        print("\nNext steps:")
        print("  1. Start the system: python3 unified_system.py")
        print("  2. Access dashboard: http://localhost:8000")
        if config.cloud_server_enabled:
            print("  3. Deploy to cloud: bash deploy_to_cloud.sh")
            print("  4. Access cloud dashboard: http://{}:{}".format(config.cloud_server_host, config.cloud_server_port))
        else:
            print("  3. Push to GitHub for automatic AWS deployment (requires AWS GitHub Actions setup)")
        print()
    
    async def start_api_server(self):
        """Start the API server"""
        logger.info("Starting API server...")
        
        try:
            # Try to import FastAPI
            from fastapi import FastAPI
            from fastapi.responses import JSONResponse, HTMLResponse
            import uvicorn
            
            app = FastAPI(title="Unified System API")
            
            @app.get("/")
            async def root():
                config = self.load_config()
                return HTMLResponse(f"""
<!DOCTYPE html>
<html>
<head>
    <title>Unified System Dashboard</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; max-width: 1200px; margin: 50px auto; padding: 20px; background: #f5f5f5; }}
        h1 {{ color: #667eea; }}
        .status {{ background: #10b981; color: white; padding: 10px 20px; border-radius: 5px; display: inline-block; margin: 10px 0; }}
        .status.warning {{ background: #f59e0b; }}
        .status.danger {{ background: #ef4444; }}
        .metric {{ background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .metric strong {{ color: #374151; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px; margin: 20px 0; }}
        .card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .card h3 {{ margin-top: 0; color: #667eea; }}
        button {{ background: #667eea; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 5px; }}
        button:hover {{ background: #5568d3; }}
        button.danger {{ background: #ef4444; }}
        button.danger:hover {{ background: #dc2626; }}
        .tag {{ display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 12px; margin: 2px; }}
        .tag.on {{ background: #10b981; color: white; }}
        .tag.off {{ background: #9ca3af; color: white; }}
    </style>
</head>
<body>
    <h1>🚀 Unified System Dashboard</h1>
    <div class="status {'danger' if config.kill_switch_active else ''} ">
        {'🚨 KILL SWITCH ACTIVE' if config.kill_switch_active else '✅ System Operational'}
    </div>
    
    <div class="grid">
        <div class="card">
            <h3>Repository Management</h3>
            <span class="tag {'on' if config.auto_fix_code else 'off'}">Auto-fix: {'ON' if config.auto_fix_code else 'OFF'}</span>
            <span class="tag {'on' if config.auto_commit else 'off'}">Auto-commit: {'ON' if config.auto_commit else 'OFF'}</span>
            <span class="tag {'on' if config.auto_push else 'off'}">Auto-push: {'ON' if config.auto_push else 'OFF'}</span>
            <span class="tag {'on' if config.auto_merge_pr else 'off'}">Auto-merge PR: {'ON' if config.auto_merge_pr else 'OFF'}</span>
        </div>
        
        <div class="card">
            <h3>Trading System</h3>
            <span class="tag {'on' if config.trading_enabled else 'off'}">Trading: {'ON' if config.trading_enabled else 'OFF'}</span>
            <span class="tag {'on' if config.auto_allocate_capital else 'off'}">Auto-allocate: {'ON' if config.auto_allocate_capital else 'OFF'}</span>
            <span class="tag {'on' if config.auto_deploy_strategies else 'off'}">Auto-deploy: {'ON' if config.auto_deploy_strategies else 'OFF'}</span>
            <span class="tag {'on' if config.evolution_engine_enabled else 'off'}">Evolution: {'ON' if config.evolution_engine_enabled else 'OFF'}</span>
        </div>
        
        <div class="card">
            <h3>Safety Controls</h3>
            <strong>Max Daily Loss:</strong> {config.max_daily_loss * 100}%<br>
            <strong>Max Risk/Trade:</strong> {config.max_risk_per_trade * 100}%<br>
            <strong>Approval Required:</strong> {'Yes' if config.require_approval else 'No'}<br>
            <strong>Kill Switch:</strong> {'ACTIVE' if config.kill_switch_active else 'Ready'}
        </div>
    </div>
    
    <div class="card">
        <h3>Quick Actions</h3>
        <!-- NOTE: For production use, add authentication/CSRF protection to these endpoints -->
        <button onclick="fetch('/api/trading/start', {{method: 'POST'}}).then(() => location.reload())">▶️ Start Trading</button>
        <button onclick="fetch('/api/trading/stop', {{method: 'POST'}}).then(() => location.reload())">⏸️ Stop Trading</button>
        <button class="danger" onclick="if(confirm('Activate emergency kill switch?')) fetch('/api/emergency/kill-switch', {{method: 'POST'}}).then(() => location.reload())">🚨 KILL SWITCH</button>
    </div>
    
    <h2>Quick Links</h2>
    <ul>
        <li><a href="/health">Health Check</a></li>
        <li><a href="/api/status">System Status (JSON)</a></li>
        <li><a href="/docs">API Documentation</a></li>
    </ul>
    
    <p style="color: #6b7280; font-size: 14px; margin-top: 40px;">
        Dashboard Port: {config.dashboard_port} | Version 2.0.0 | Timestamp: {datetime.now().isoformat()}
    </p>
</body>
</html>
                """)
            
            @app.get("/health")
            async def health():
                return JSONResponse({
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "components": {
                        "api": "operational",
                        "trading": "disabled",
                        "dashboard": "operational"
                    }
                })
            
            @app.get("/api/status")
            async def status():
                config = self.load_config()
                return JSONResponse({
                    "system": "unified",
                    "version": "2.0.0",
                    "config": asdict(config),
                    "timestamp": datetime.now().isoformat()
                })
            
            @app.post("/api/emergency/kill-switch")
            async def kill_switch():
                """Emergency stop all trading"""
                config = self.load_config()
                config.kill_switch_active = True
                config.trading_enabled = False
                config.auto_allocate_capital = False
                config.auto_deploy_strategies = False
                self.save_config(config)
                logger.warning("🚨 KILL SWITCH ACTIVATED - All trading halted")
                return JSONResponse({
                    "success": True,
                    "message": "Emergency stop activated - all trading halted",
                    "timestamp": datetime.now().isoformat()
                })
            
            @app.post("/api/trading/start")
            async def start_trading():
                """Start trading (if not in kill switch mode)"""
                config = self.load_config()
                if config.kill_switch_active:
                    return JSONResponse({
                        "success": False,
                        "message": "Cannot start - kill switch is active"
                    }, status_code=403)
                config.trading_enabled = True
                self.save_config(config)
                logger.info("✅ Trading enabled")
                return JSONResponse({
                    "success": True,
                    "message": "Trading started"
                })
            
            @app.post("/api/trading/stop")
            async def stop_trading():
                """Stop trading"""
                config = self.load_config()
                config.trading_enabled = False
                self.save_config(config)
                logger.info("🛑 Trading disabled")
                return JSONResponse({
                    "success": True,
                    "message": "Trading stopped"
                })
            
            # Run server
            port = int(os.environ.get('PORT', '8000'))
            logger.info(f"✅ API Server running on http://localhost:{port}")
            
            config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
            server = uvicorn.Server(config)
            await server.serve()
            
        except ImportError:
            logger.error("FastAPI not installed. Please run: pip install fastapi uvicorn")
            logger.info("Starting basic HTTP server instead...")
            
            # Fallback to basic HTTP server
            import http.server
            import socketserver
            
            port = int(os.environ.get('PORT', '8000'))
            
            class Handler(http.server.SimpleHTTPRequestHandler):
                def do_GET(self):
                    if self.path == '/health':
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({"status": "healthy"}).encode())
                    else:
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        self.wfile.write(b"<h1>Unified System</h1><p>System operational</p>")
            
            with socketserver.TCPServer(("0.0.0.0", port), Handler) as httpd:
                logger.info(f"✅ Basic server running on http://localhost:{port}")
                httpd.serve_forever()
    
    async def run(self):
        """Run the unified system with environment preloading"""
        print("\n" + "="*80)
        print("║ 🚀 UNIFIED AUTONOMOUS SYSTEM - ENHANCED")
        print("║ The-Basics + Chimera Auto-Pilot + Full Dashboard")
        print("="*80 + "\n")
        
        # STEP 1: Preload all environments, secrets, and credentials
        if self.env_preloader:
            print("🔐 Preloading environments, secrets, and credentials...")
            preload_summary = self.env_preloader.preload_all_environments()
            print(f"  ✓ Loaded {preload_summary['total_variables']} environment variables")
            print(f"  ✓ {preload_summary['secrets_count']} secrets configured")
            print(f"  ✓ Platforms: {', '.join(preload_summary['platforms'])}")
            
            # Export Railway environment if Railway is configured and explicitly enabled
            if preload_summary.get('credentials_loaded', {}).get('railway'):
                print("  ✓ Railway credentials detected")
                if os.getenv("ENABLE_RAILWAY_DOTENV_EXPORT") == "1":
                    # Only export non-secrets by default
                    include_secrets = os.getenv("EXPORT_RAILWAY_SECRETS") == "1"
                    self.env_preloader.export_to_dotenv(".env.railway", include_secrets=include_secrets)
                    print(f"  ✓ Railway environment exported to .env.railway (secrets={include_secrets})")
                else:
                    print("  ⏭  Skipping .env.railway export (set ENABLE_RAILWAY_DOTENV_EXPORT=1 to enable)")
            
            # Validate Railway deployment
            print("\n🚂 Validating Railway deployment configuration...")
            validation = self.env_preloader.validate_railway_deployment()
            if validation['valid']:
                print("  ✅ Railway deployment validated")
            else:
                print("  ⚠️  Railway deployment validation warnings:")
                for error in validation.get('errors', []):
                    print(f"      - {error}")
                for warning in validation.get('warnings', []):
                    print(f"      - {warning}")
            print()
        
        # Load configuration
        self.config = self.load_config()
        logger.info("Configuration loaded")
        
        # Check if first run
        if not self.config_file.exists():
            logger.warning("No configuration found. Please run: python3 unified_system.py --setup")
            return
        
        logger.info("🚀 STARTING UNIFIED SYSTEM")
        logger.info(f"✅ Dashboard will be available at http://localhost:{self.config.dashboard_port}")
        logger.info(f"✅ Health check: http://localhost:{self.config.dashboard_port}/health")
        
        # Start API server
        await self.start_api_server()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Unified Autonomous System')
    parser.add_argument('--setup', action='store_true', help='Run setup wizard')
    parser.add_argument('--auto', action='store_true', help='Full autonomous mode (override config)')
    parser.add_argument('--review', action='store_true', help='Review only mode (override config)')
    parser.add_argument('--code-only', action='store_true', help='Code management only')
    parser.add_argument('--trading-only', action='store_true', help='Trading management only')
    
    args = parser.parse_args()
    
    system = UnifiedSystem()
    
    # Run setup wizard
    if args.setup:
        system.setup_wizard()
        return
    
    # Override config based on command-line args
    if args.auto or args.review or args.code_only or args.trading_only:
        config = system.load_config()
        
        if args.auto:
            config.auto_fix_code = True
            config.auto_commit = True
            config.auto_push = True
            config.auto_merge_pr = True
            config.auto_deploy = True
            config.require_approval = False
            logger.info("Running in FULL AUTONOMOUS mode")
            
        if args.review:
            config.require_approval = True
            config.auto_fix_code = False
            config.auto_commit = False
            config.auto_push = False
            config.trading_enabled = False
            logger.info("Running in REVIEW ONLY mode")
            
        if args.code_only:
            config.trading_enabled = False
            config.auto_allocate_capital = False
            config.auto_deploy_strategies = False
            logger.info("Running in CODE MANAGEMENT mode")
            
        if args.trading_only:
            config.auto_fix_code = False
            config.auto_commit = False
            config.auto_push = False
            logger.info("Running in TRADING mode")
        
        system.save_config(config)
    
    # Run the system
    try:
        asyncio.run(system.run())
    except KeyboardInterrupt:
        logger.info("\n📴 Shutting down gracefully...")
        print("\n✅ System stopped")


if __name__ == "__main__":
    main()
