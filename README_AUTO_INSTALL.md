# 🚀 Chimera Auto-Pilot - One-Command Installation

## Quick Start

Deploy the entire Chimera Auto-Pilot trading system with a single command!

```bash
curl -fsSL https://raw.githubusercontent.com/oconnorw225-del/The-basics/main/auto_install.sh | sudo bash
```

Or for fully automated installation:

```bash
curl -fsSL https://raw.githubusercontent.com/oconnorw225-del/The-basics/main/auto_install.sh | sudo bash -s -- --auto
```

---

## What Gets Installed

The auto-installer handles everything:

### 1. ✅ System Dependencies
- Python 3.11+
- Node.js 18+
- Git, curl, build tools
- System utilities

### 2. ✅ Databases (Optional)
- PostgreSQL 14+ (structured data)
- MongoDB 6.0+ (time-series data)
- Redis 7.0+ (caching)

### 3. ✅ Chimera Components
- Core trading engine
- Autonomous AI system
- Solvency monitoring
- Freelance automation
- Dashboard interface

### 4. ✅ Configuration
- Auto-generated config files
- Database setup with secure passwords
- Environment variables
- Systemd service

### 5. ✅ Monitoring & Management
- Health check system
- Log rotation
- Prometheus metrics (production mode)
- Helper scripts for easy management

---

## Installation Options

### Interactive Mode (Default)
```bash
sudo bash auto_install.sh
```
- Pauses at each step
- Shows progress
- Allows verification

### Fully Automated Mode
```bash
sudo bash auto_install.sh --auto
```
- No user interaction
- Perfect for scripts/CI
- Runs all steps automatically

### Production Mode
```bash
sudo bash auto_install.sh --auto --production
```
- Includes Prometheus monitoring
- Enhanced security settings
- Production-optimized configuration

### Skip Databases (Lightweight)
```bash
sudo bash auto_install.sh --skip-databases
```
- Installs core system only
- No PostgreSQL/MongoDB/Redis
- Useful for testing or resource-constrained servers

---

## Usage After Installation

### Start/Stop/Restart

```bash
# Using systemctl
sudo systemctl start chimera-autopilot
sudo systemctl stop chimera-autopilot
sudo systemctl restart chimera-autopilot
sudo systemctl status chimera-autopilot

# Using helper scripts
sudo /opt/chimera-autopilot/start.sh
sudo /opt/chimera-autopilot/stop.sh
sudo /opt/chimera-autopilot/restart.sh
sudo /opt/chimera-autopilot/status.sh
```

### Monitor System

```bash
# View logs
sudo tail -f /var/log/chimera/chimera.log

# Check status
sudo /opt/chimera-autopilot/monitor.sh

# View service status
sudo systemctl status chimera-autopilot
```

### Update System

```bash
sudo /opt/chimera-autopilot/update.sh
```

---

## Configuration

### Main Configuration File

Edit `/etc/chimera/config.yaml` to configure:

- Trading settings
- Exchange API keys
- Risk management
- Dashboard port
- Monitoring options

```bash
sudo nano /etc/chimera/config.yaml
```

### Example Configuration

```yaml
# Trading Configuration
trading:
  enabled: true  # Set to true after adding API keys
  symbols:
    - BTC/CAD
    - ETH/CAD
  interval: 60
  default_quantity: 0.001

# Exchange APIs (ADD YOUR KEYS HERE)
exchanges:
  ndax:
    enabled: true
    api_key: "YOUR_API_KEY"
    api_secret: "YOUR_API_SECRET"
    user_id: "YOUR_USER_ID"
    account_id: "YOUR_ACCOUNT_ID"
    testnet: true  # Set to false for production

# Safety Settings
safety:
  require_approval: true
  max_risk_per_trade: 0.02  # 2%
  max_daily_loss: 0.05      # 5%
```

After editing, restart:

```bash
sudo systemctl restart chimera-autopilot
```

---

## Access Dashboard

Once installed, access the dashboard at:

```
http://YOUR_SERVER_IP:8000
```

Or locally:

```
http://localhost:8000
```

---

## File Locations

| Component | Location |
|-----------|----------|
| Installation | `/opt/chimera-autopilot/` |
| Configuration | `/etc/chimera/config.yaml` |
| Logs | `/var/log/chimera/` |
| Data | `/var/lib/chimera/` |
| Service | `/etc/systemd/system/chimera-autopilot.service` |
| Helper Scripts | `/opt/chimera-autopilot/*.sh` |

---

## Troubleshooting

### Service Won't Start

```bash
# Check logs
sudo journalctl -u chimera-autopilot -n 50

# Check detailed logs
sudo tail -n 100 /var/log/chimera/chimera-error.log

# Verify configuration
sudo python3 -m py_compile /etc/chimera/config.yaml
```

### Database Connection Issues

```bash
# Check PostgreSQL
sudo systemctl status postgresql

# Check MongoDB
sudo systemctl status mongod

# Check Redis
sudo systemctl status redis-server

# View database credentials
sudo cat /etc/chimera/db_credentials.json
```

### Port Already in Use

```bash
# Change dashboard port in config
sudo nano /etc/chimera/config.yaml

# Find line: dashboard.port: 8000
# Change to different port: dashboard.port: 8080

# Restart service
sudo systemctl restart chimera-autopilot
```

### Memory Issues

```bash
# Check memory usage
free -h

# Reduce concurrent workers in config
sudo nano /etc/chimera/config.yaml
# Add: workers: 2

# Restart
sudo systemctl restart chimera-autopilot
```

---

## Security Best Practices

### 1. Secure API Keys

```bash
# Never commit API keys to git
# Store in config file with restricted permissions
sudo chmod 600 /etc/chimera/config.yaml
sudo chmod 600 /etc/chimera/db_credentials.json
```

### 2. Enable Firewall

```bash
# The installer configures UFW automatically
# To check:
sudo ufw status

# Allow only necessary ports
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 8000/tcp # Dashboard
```

### 3. Use Testnet First

Always test with testnet before enabling production:

```yaml
exchanges:
  ndax:
    testnet: true  # Keep this true until ready
```

### 4. Set Conservative Limits

```yaml
safety:
  max_risk_per_trade: 0.01  # 1% max per trade
  max_daily_loss: 0.03      # 3% max daily loss
```

---

## Advanced Options

### Custom Installation Directory

```bash
# Modify INSTALL_DIR in script before running
export INSTALL_DIR="/custom/path"
sudo -E bash auto_install.sh
```

### Manual Installation

If you prefer manual control:

```bash
# 1. Clone repository
git clone https://github.com/oconnorw225-del/The-basics.git
cd The-basics

# 2. Run installer
sudo bash auto_install.sh
```

### Distributed Installation

For multiple servers:

```bash
# On each server
curl -fsSL https://your-domain.com/auto_install.sh | sudo bash -s -- --auto --skip-databases

# Setup one central database server
# Configure all servers to connect to it
```

---

## Uninstall

To completely remove Chimera:

```bash
# Stop service
sudo systemctl stop chimera-autopilot
sudo systemctl disable chimera-autopilot

# Remove files
sudo rm -rf /opt/chimera-autopilot
sudo rm -rf /var/log/chimera
sudo rm -rf /var/lib/chimera
sudo rm -rf /etc/chimera
sudo rm /etc/systemd/system/chimera-autopilot.service

# Reload systemd
sudo systemctl daemon-reload

# Optional: Remove databases
sudo apt-get remove --purge postgresql mongodb-org redis-server
```

---

## Support

- **Documentation**: See `/opt/chimera-autopilot/docs/`
- **Logs**: Check `/var/log/chimera/chimera.log`
- **Configuration**: `/etc/chimera/config.yaml`
- **Status**: Run `sudo /opt/chimera-autopilot/monitor.sh`

---

## What Happens During Installation

1. **System Check** - Verifies CPU, memory, disk space, network
2. **Package Install** - Installs Python, Node.js, Git, dependencies
3. **Database Setup** - Installs and configures PostgreSQL, MongoDB, Redis
4. **Directory Creation** - Creates all necessary directories
5. **Chimera Install** - Copies files, creates virtual environment
6. **Configuration** - Auto-generates config files with secure defaults
7. **Service Setup** - Creates systemd service for auto-start
8. **Monitoring** - Sets up logging and health checks
9. **Testing** - Runs basic import and functionality tests
10. **Activation** - Enables and starts the service

Total installation time: **5-10 minutes** (depending on system speed)

---

## Requirements

### Minimum
- Ubuntu 20.04+ or Debian 11+
- 2 CPU cores
- 2GB RAM
- 10GB disk space
- Internet connection

### Recommended
- Ubuntu 22.04 LTS
- 4 CPU cores
- 4GB RAM
- 20GB SSD
- 10 Mbps+ connection

---

## Post-Installation Checklist

- [ ] Service is running: `sudo systemctl status chimera-autopilot`
- [ ] Dashboard accessible: `http://YOUR_IP:8000`
- [ ] Logs are writing: `sudo tail /var/log/chimera/chimera.log`
- [ ] Configuration updated with API keys
- [ ] Trading enabled (if desired): `trading.enabled: true`
- [ ] Testnet mode confirmed (until ready for production)
- [ ] Firewall configured properly
- [ ] Monitoring script works: `sudo /opt/chimera-autopilot/monitor.sh`

---

## 🎉 You're Ready!

The Chimera Auto-Pilot system is now:
- ✅ Fully installed
- ✅ Auto-configured
- ✅ Running as a service
- ✅ Monitoring itself
- ✅ Ready for optimization
- ✅ Ready to trade (after adding API keys)

**Next:** Add your exchange API keys and enable trading!

```bash
sudo nano /etc/chimera/config.yaml
# Add your API keys
# Set trading.enabled: true
sudo systemctl restart chimera-autopilot
```

Happy trading! 🚀📈
