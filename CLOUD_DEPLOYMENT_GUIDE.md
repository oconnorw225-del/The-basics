# 🌐 Cloud Server Deployment Guide

## Overview
This guide helps you deploy the complete Chimera Auto-Pilot system to your own cloud server for enhanced performance and optimization.

## Prerequisites

### Your Cloud Server Requirements
- **Operating System**: Ubuntu 20.04 LTS or newer (recommended)
- **RAM**: Minimum 2GB, recommended 4GB+
- **Storage**: Minimum 20GB free space
- **CPU**: 2+ cores recommended
- **Network**: Public IP address and open port (default 8000)

### Local Machine Requirements
- SSH access to your cloud server
- SSH key configured for passwordless login
- Git installed

## Supported Cloud Providers
- ✅ AWS EC2
- ✅ Google Cloud Platform (GCP)
- ✅ Microsoft Azure
- ✅ DigitalOcean
- ✅ Linode
- ✅ Vultr
- ✅ Any VPS with Ubuntu/Debian

## Quick Start

### Step 1: Run Setup Wizard
```bash
python3 unified_system.py --setup
```

When prompted for cloud server integration:
1. Answer **yes** to "Deploy to your own cloud server?"
2. Enter your server details:
   - **Server IP/Hostname**: Your cloud server's IP or domain
   - **Server Port**: Port for the dashboard (default: 8000)
   - **SSH Username**: Usually `root` or `ubuntu`
   - **SSH Key Path**: Path to your SSH private key (e.g., `~/.ssh/id_rsa`)
   - **Deployment Path**: Where to install on server (default: `/opt/chimera-autopilot`)

### Step 2: Deploy to Cloud
```bash
bash deploy_to_cloud.sh
```

This script will:
1. ✅ Test SSH connection
2. ✅ Install system dependencies (Python, Node.js, Git)
3. ✅ Upload your code to the server
4. ✅ Install Python packages
5. ✅ Create systemd service for auto-start
6. ✅ Start the Chimera Auto-Pilot system

### Step 3: Access Your Cloud Dashboard
Open your browser:
```
http://YOUR_SERVER_IP:8000
```

## Detailed Setup Instructions

### For AWS EC2

1. **Launch an EC2 Instance**
   ```bash
   # Choose Ubuntu 20.04 LTS AMI
   # Instance type: t2.medium or larger
   # Configure Security Group to allow:
   - SSH (port 22) from your IP
   - HTTP (port 8000) from anywhere or your IP
   ```

2. **Connect and Configure**
   ```bash
   # Download your .pem key
   chmod 400 your-key.pem
   
   # Test connection
   ssh -i your-key.pem ubuntu@your-ec2-public-ip
   ```

3. **Run Setup**
   ```bash
   python3 unified_system.py --setup
   
   # When prompted:
   Server IP: <your-ec2-public-ip>
   SSH Username: ubuntu
   SSH Key: ~/.ssh/your-key.pem
   ```

### For DigitalOcean

1. **Create a Droplet**
   ```bash
   # Choose Ubuntu 20.04 LTS
   # Plan: Basic - 2GB RAM minimum
   # Add your SSH key during creation
   ```

2. **Configure Firewall**
   ```bash
   # In DigitalOcean dashboard, create firewall:
   - Allow SSH (22)
   - Allow Custom TCP (8000)
   ```

3. **Run Setup**
   ```bash
   python3 unified_system.py --setup
   
   # When prompted:
   Server IP: <your-droplet-ip>
   SSH Username: root
   SSH Key: ~/.ssh/id_rsa
   ```

### For Google Cloud Platform (GCP)

1. **Create a VM Instance**
   ```bash
   # Compute Engine > VM instances > Create
   # Machine type: e2-medium or larger
   # Boot disk: Ubuntu 20.04 LTS
   # Firewall: Allow HTTP and HTTPS traffic
   ```

2. **Add Firewall Rule**
   ```bash
   # VPC Network > Firewall > Create rule
   - Name: allow-chimera
   - Targets: All instances
   - Source IP ranges: 0.0.0.0/0 (or your IP)
   - Protocols: tcp:8000
   ```

3. **Set up SSH**
   ```bash
   # Generate SSH key if needed
   ssh-keygen -t rsa -b 4096
   
   # Add key to GCP metadata
   # Compute Engine > Metadata > SSH Keys
   ```

## Post-Deployment

### Check System Status
```bash
ssh -i ~/.ssh/your-key.pem user@server-ip 'systemctl status chimera-autopilot'
```

### View Live Logs
```bash
ssh -i ~/.ssh/your-key.pem user@server-ip 'journalctl -u chimera-autopilot -f'
```

### Restart System
```bash
ssh -i ~/.ssh/your-key.pem user@server-ip 'systemctl restart chimera-autopilot'
```

### Update Deployment
After making code changes locally:
```bash
bash deploy_to_cloud.sh
```

## Configuration

### Environment Variables
The system uses the `.env` file generated during setup. To modify on the server:

```bash
ssh -i ~/.ssh/your-key.pem user@server-ip
cd /opt/chimera-autopilot
nano .env
systemctl restart chimera-autopilot
```

### System Configuration
Modify `.unified-system/config.json` on the server:

```bash
ssh -i ~/.ssh/your-key.pem user@server-ip
cd /opt/chimera-autopilot
nano .unified-system/config.json
systemctl restart chimera-autopilot
```

## Security Best Practices

### 1. Firewall Configuration
```bash
# Only allow necessary ports
ufw allow 22/tcp    # SSH
ufw allow 8000/tcp  # Dashboard
ufw enable
```

### 2. SSH Key Security
```bash
# Set correct permissions
chmod 600 ~/.ssh/your-key.pem
```

### 3. Restrict Dashboard Access
Edit your cloud firewall to only allow your IP:
```bash
# Instead of 0.0.0.0/0, use your IP
# Example: 203.0.113.5/32
```

### 4. Enable HTTPS (Recommended)
Install Nginx and Let's Encrypt:
```bash
ssh -i ~/.ssh/your-key.pem user@server-ip << 'EOF'
apt-get install -y nginx certbot python3-certbot-nginx

# Get certificate (replace with your domain)
certbot --nginx -d your-domain.com

# Configure Nginx to proxy to port 8000
cat > /etc/nginx/sites-available/chimera << 'NGINX'
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
NGINX

ln -s /etc/nginx/sites-available/chimera /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
EOF
```

## Monitoring

### System Resources
```bash
ssh -i ~/.ssh/your-key.pem user@server-ip 'htop'
```

### Application Logs
```bash
ssh -i ~/.ssh/your-key.pem user@server-ip 'tail -f /opt/chimera-autopilot/.unified-system/logs/system.log'
```

### Service Health
```bash
# Check if service is running
ssh -i ~/.ssh/your-key.pem user@server-ip 'systemctl is-active chimera-autopilot'

# Check service health endpoint
curl http://your-server-ip:8000/health
```

## Troubleshooting

### Deployment Fails
```bash
# Check SSH connection
ssh -i ~/.ssh/your-key.pem user@server-ip 'echo "Connection OK"'

# Verify server requirements
ssh -i ~/.ssh/your-key.pem user@server-ip << 'EOF'
python3 --version
node --version
git --version
df -h
free -h
EOF
```

### Service Won't Start
```bash
# Check service status
ssh -i ~/.ssh/your-key.pem user@server-ip 'systemctl status chimera-autopilot'

# Check logs for errors
ssh -i ~/.ssh/your-key.pem user@server-ip 'journalctl -u chimera-autopilot -n 100'

# Verify Python dependencies
ssh -i ~/.ssh/your-key.pem user@server-ip 'cd /opt/chimera-autopilot && pip3 list'
```

### Can't Access Dashboard
```bash
# Check if service is running
ssh -i ~/.ssh/your-key.pem user@server-ip 'systemctl status chimera-autopilot'

# Check if port is open
ssh -i ~/.ssh/your-key.pem user@server-ip 'netstat -tlnp | grep 8000'

# Verify firewall allows port 8000
ssh -i ~/.ssh/your-key.pem user@server-ip 'ufw status'
```

## Advanced Configuration

### Run in Full Autonomous Mode
The deployment script automatically starts in `--auto` mode (full autonomous).

To change modes:
```bash
ssh -i ~/.ssh/your-key.pem user@server-ip
cd /opt/chimera-autopilot

# Stop service
systemctl stop chimera-autopilot

# Edit service file
nano /etc/systemd/system/chimera-autopilot.service

# Change ExecStart line:
# For review mode: ExecStart=/usr/bin/python3 ... --review
# For code-only: ExecStart=/usr/bin/python3 ... --code-only
# For trading-only: ExecStart=/usr/bin/python3 ... --trading-only

# Reload and restart
systemctl daemon-reload
systemctl start chimera-autopilot
```

### Backup and Restore
```bash
# Backup configuration
ssh -i ~/.ssh/your-key.pem user@server-ip 'tar -czf chimera-backup.tar.gz /opt/chimera-autopilot/.unified-system'
scp -i ~/.ssh/your-key.pem user@server-ip:chimera-backup.tar.gz ./

# Restore
scp -i ~/.ssh/your-key.pem chimera-backup.tar.gz user@server-ip:/tmp/
ssh -i ~/.ssh/your-key.pem user@server-ip 'cd /opt/chimera-autopilot && tar -xzf /tmp/chimera-backup.tar.gz'
```

### Auto-Updates
Create a cron job on the server:
```bash
ssh -i ~/.ssh/your-key.pem user@server-ip << 'EOF'
(crontab -l 2>/dev/null; echo "0 2 * * * cd /opt/chimera-autopilot && git pull && systemctl restart chimera-autopilot") | crontab -
EOF
```

## Performance Optimization

### Recommended Server Specs by Use Case

**Development/Testing:**
- 2 CPU cores
- 2GB RAM
- 20GB storage

**Production (Code Only):**
- 2 CPU cores
- 4GB RAM
- 40GB storage

**Production (Trading Enabled):**
- 4 CPU cores
- 8GB RAM
- 80GB storage

**Full Autonomous (All Features):**
- 8+ CPU cores
- 16GB+ RAM
- 100GB+ storage

## Support

### Getting Help
- Check logs: `/opt/chimera-autopilot/.unified-system/logs/system.log`
- Service status: `systemctl status chimera-autopilot`
- Health check: `curl http://localhost:8000/health`

### Useful Resources
- System dashboard: `http://your-server-ip:8000`
- API status: `http://your-server-ip:8000/api/status`
- API docs: `http://your-server-ip:8000/docs`

---

**Your Chimera Auto-Pilot system is now running in the cloud! 🚀**

*Complete autonomous management, optimized for cloud deployment.*
