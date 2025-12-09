# 🌐 Cloud Deployment Quick Reference

## What Was Added

### 1. Cloud Server Configuration
New fields in `SystemConfig`:
- `cloud_server_enabled` - Enable/disable cloud deployment
- `cloud_server_host` - Your server's IP or hostname
- `cloud_server_port` - Dashboard port (default: 8000)
- `cloud_server_ssh_key` - Path to SSH private key
- `cloud_server_username` - SSH username (default: root)
- `cloud_deployment_path` - Installation directory (default: /opt/chimera-autopilot)

### 2. Automated Deployment
**File**: `deploy_to_cloud.sh` (auto-generated during setup)

**What it does**:
1. ✅ Tests SSH connection to your server
2. ✅ Installs system dependencies (Python 3, Node.js, Git)
3. ✅ Creates deployment directory
4. ✅ Uploads all your code (excludes .git, node_modules, etc.)
5. ✅ Installs Python packages from requirements.txt
6. ✅ Creates systemd service for auto-start
7. ✅ Starts the Chimera Auto-Pilot in full autonomous mode

### 3. Enhanced Setup Wizard
During `python3 unified_system.py --setup`, you'll be asked:
- Deploy to your own cloud server? (y/n)
- Server IP/Hostname
- Server Port
- SSH Username
- SSH Key Path
- Deployment Path

### 4. Production-Ready Service
The deployment creates a systemd service that:
- Starts automatically on server boot
- Restarts automatically if it crashes
- Runs in full autonomous mode (`--auto`)
- Logs to journalctl

## Quick Start

### Step 1: Setup
```bash
python3 unified_system.py --setup
```

When asked about cloud deployment:
```
Deploy to your own cloud server? y
Server IP: 203.0.113.5
Port: 8000
Username: root
SSH Key: ~/.ssh/my-server-key.pem
Path: /opt/chimera-autopilot
```

### Step 2: Deploy
```bash
bash deploy_to_cloud.sh
```

### Step 3: Access
```
http://203.0.113.5:8000
```

## Server Management

### Check Status
```bash
ssh -i ~/.ssh/your-key.pem user@server 'systemctl status chimera-autopilot'
```

### View Logs
```bash
ssh -i ~/.ssh/your-key.pem user@server 'journalctl -u chimera-autopilot -f'
```

### Restart
```bash
ssh -i ~/.ssh/your-key.pem user@server 'systemctl restart chimera-autopilot'
```

### Update Code
After making local changes:
```bash
bash deploy_to_cloud.sh
```

## Supported Cloud Providers

✅ **AWS EC2** - Amazon Web Services
✅ **Google Cloud Platform (GCP)** - Google Compute Engine
✅ **Microsoft Azure** - Azure Virtual Machines
✅ **DigitalOcean** - Droplets
✅ **Linode** - VPS
✅ **Vultr** - Cloud Compute
✅ **Any VPS** - Ubuntu 20.04+ or Debian

## System Requirements

**Minimum:**
- 2 CPU cores
- 2GB RAM
- 20GB storage
- Ubuntu 20.04 LTS or newer

**Recommended (Full Autonomous):**
- 8+ CPU cores
- 16GB+ RAM
- 100GB+ storage
- SSD storage

## Security Features

✅ SSH key-based authentication (no passwords)
✅ Automatic firewall configuration
✅ Systemd service isolation
✅ Secure credential storage
✅ HTTPS support (via Nginx + Let's Encrypt)

## Full Documentation

📖 **Complete Guide**: [CLOUD_DEPLOYMENT_GUIDE.md](CLOUD_DEPLOYMENT_GUIDE.md)

Includes:
- Detailed setup for each cloud provider
- Security best practices
- HTTPS configuration
- Performance optimization
- Troubleshooting guide
- Advanced configuration options

## Benefits of Cloud Deployment

🚀 **Always Available**: Runs 24/7 on your server
⚡ **Better Performance**: Dedicated resources, no throttling
🔒 **More Secure**: Isolated environment, no local dependencies
📊 **Better Monitoring**: System logs, health checks, uptime tracking
🌐 **Access Anywhere**: Dashboard accessible from any device
💰 **Cost Effective**: Pay only for what you use

---

**Your Chimera Auto-Pilot is now cloud-ready! 🎉**
