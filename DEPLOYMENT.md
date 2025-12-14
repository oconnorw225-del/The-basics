# Deployment Guide - Chimera System

Complete guide for deploying Chimera across all supported platforms.

## 🚀 Quick Deployment Options

Choose the deployment method that best fits your needs:

| Method | Best For | Setup Time | Monthly Cost | Complexity |
|--------|----------|------------|--------------|------------|
| [AWS Auto-Deploy](#aws-deployment-recommended) | Production | 5 min | ~$50-150 | Low |
| [Docker](#docker-deployment) | Self-Hosting | 5 min | Variable | Medium |
| [Local Development](#local-development) | Development | 3 min | $0 | Low |

---

## AWS Deployment (Recommended) ⭐

**Best for**: Production environments with auto-scaling and monitoring

### Features
- ✅ Automated CI/CD with GitHub Actions
- ✅ Auto-scaling based on load
- ✅ Built-in monitoring and logging
- ✅ High availability across multiple zones
- ✅ Production-ready security

### Quick Start

**Prerequisites:**
- AWS account
- GitHub repository access

**Setup (5 minutes):**

1. **Create IAM User** in AWS with these policies:
   - `AmazonEC2ContainerRegistryFullAccess`
   - `AmazonECS_FullAccess`
   - `CloudWatchFullAccess`

2. **Add GitHub Secrets** (Settings → Secrets → Actions):
   ```
   AWS_ACCESS_KEY_ID=your-key
   AWS_SECRET_ACCESS_KEY=your-secret
   AWS_REGION=us-east-1
   ```

3. **Deploy:**
   ```bash
   git push origin main
   ```

That's it! GitHub Actions automatically deploys to AWS.

### Detailed Documentation

- **Quick Start**: [`aws/QUICKSTART.md`](aws/QUICKSTART.md) - 5-minute setup guide
- **Full Guide**: [`aws/README_AWS_DEPLOYMENT.md`](aws/README_AWS_DEPLOYMENT.md) - Complete documentation
- **Terraform**: [`aws/terraform/main.tf`](aws/terraform/main.tf) - Infrastructure as code
- **Monitoring**: [`aws/monitor-dashboard.html`](aws/monitor-dashboard.html) - Real-time dashboard
- **Cost Calculator**: [`aws/cost-calculator.py`](aws/cost-calculator.py) - Estimate costs

### Manual Server Setup

For a single EC2 instance:

```bash
# SSH into your EC2 instance
ssh ubuntu@your-ec2-ip

# Download and run setup script
wget https://raw.githubusercontent.com/oconnorw225-del/The-basics/main/aws/setup-server.sh
sudo bash setup-server.sh --auto
```

### Cost Estimate

```bash
python aws/cost-calculator.py
```

**Typical costs:**
- Minimal setup: ~$50/month
- Standard production: ~$150/month
- High-traffic: ~$400/month

---

## Docker Deployment

**Best for**: Self-hosting on your own infrastructure

### Features
- ✅ Portable across any platform
- ✅ Consistent environments
- ✅ Easy scaling with Docker Compose
- ✅ Full control over infrastructure

### Quick Start

1. **Build the Docker image:**
   ```bash
   docker build -t chimera-system .
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     --name chimera \
     -p 8000:8000 \
     -e NODE_ENV=production \
     -e PYTHON_ENV=production \
     chimera-system
   ```

3. **Access the application:**
   ```
   http://localhost:8000
   ```

### Using Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  chimera:
    build: .
    ports:
      - "8000:8000"
    environment:
      - NODE_ENV=production
      - PYTHON_ENV=production
    restart: unless-stopped
    
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: chimera
      POSTGRES_USER: chimera
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

Then run:
```bash
docker-compose up -d
```

### Dockerfile

The project includes a production-ready [`Dockerfile`](Dockerfile).

---

## Local Development

**Best for**: Development and testing

### Features
- ✅ No cloud costs
- ✅ Full development environment
- ✅ Easy debugging
- ✅ Quick iteration

### Setup

#### Option 1: Automated Installation (Recommended)

```bash
# Clone repository
git clone https://github.com/oconnorw225-del/The-basics.git
cd The-basics

# Run auto installer
sudo bash auto_install.sh --auto
```

This script:
- Installs all dependencies
- Sets up databases (PostgreSQL, Redis)
- Configures the system
- Creates systemd services
- Starts the application

#### Option 2: Manual Setup

1. **Install dependencies:**
   ```bash
   # Python
   python3 -m pip install -r requirements.txt
   
   # Node.js
   npm install
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Start the system:**
   ```bash
   # Using unified system
   python3 unified_system.py
   
   # Or using Node.js server
   npm start
   ```

#### Option 3: Production System Setup

For a complete production setup with all services:

```bash
sudo bash install_chimera_production.sh
```

This creates the full Chimera production system with:
- 25+ service files
- Platform executors (Honeygain, Earnapp, etc.)
- Complete orchestration system
- Configuration files
- Testing suite

### Development Modes

```bash
# Full autonomous mode
python3 unified_system.py --auto

# Code management only
python3 unified_system.py --code-only

# Trading management only
python3 unified_system.py --trading-only

# Interactive mode
python3 unified_system.py

# Review mode
python3 unified_system.py --review
```

### Cloud Server Deployment

Deploy to your own cloud server (DigitalOcean, Linode, etc.):

```bash
# Run setup wizard
python3 unified_system.py --setup

# Follow prompts for cloud server details
# Then deploy
bash deploy_to_cloud.sh
```

See [`CLOUD_DEPLOYMENT_GUIDE.md`](CLOUD_DEPLOYMENT_GUIDE.md) for details.

---

## Comparison Matrix

| Feature | AWS | Docker | Local |
|---------|-----|--------|-------|
| Auto-scaling | ✅ | ⚠️ Manual | ❌ |
| SSL/HTTPS | ✅ | ⚠️ Manual | ❌ |
| Monitoring | ✅ Built-in | ⚠️ Manual | ⚠️ Manual |
| Cost | $50-150/mo | Variable | $0 |
| Setup Time | 5 min | 5 min | 3 min |
| Maintenance | Low | Medium | High |
| Control | High | Very High | Very High |
| Production Ready | ✅ | ✅ | ❌ |

---

## Environment Variables

All deployment methods support these environment variables:

### Application Settings
```bash
NODE_ENV=production          # Node.js environment
PYTHON_ENV=production        # Python environment
API_PORT=8000               # API server port
API_HOST=0.0.0.0           # API server host
```

### Database Settings
```bash
DATABASE_URL=postgresql://user:pass@host:5432/chimera
REDIS_URL=redis://host:6379
```

### Security Settings
```bash
SECRET_KEY=your-secret-key
JWT_SECRET=your-jwt-secret
```

### Trading Settings (Optional)
```bash
TRADING_MODE=paper          # paper or live
RISK_TOLERANCE=0.05         # 5% risk tolerance
MAX_POSITION_SIZE=0.1       # 10% max position
```

### AWS Settings (AWS deployment only)
```bash
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=123456789012
```

---

## Deployment Workflows

### GitHub Actions

The repository includes automated workflows:

- **[`deploy-to-aws.yml`](.github/workflows/deploy-to-aws.yml)**: Automatic AWS deployment
- **[`monitor-aws.yml`](.github/workflows/monitor-aws.yml)**: AWS health monitoring
- **[`unified-system.yml`](.github/workflows/unified-system.yml)**: CI/CD pipeline

### Manual Deployment

For manual deployments without GitHub Actions:

```bash
# Build
docker build -t chimera-system .

# Tag for registry
docker tag chimera-system registry.example.com/chimera-system:latest

# Push to registry
docker push registry.example.com/chimera-system:latest

# Deploy to your infrastructure
kubectl apply -f k8s-deployment.yaml
# or
docker-compose up -d
```

---

## Post-Deployment

### Verify Deployment

1. **Check application status:**
   ```bash
   curl http://your-deployment-url/health
   ```

2. **View logs:**
   ```bash
   # Docker
   docker logs -f chimera
   
   # AWS
   aws logs tail /ecs/chimera-system --follow
   
   # Local
   tail -f /var/log/chimera/chimera.log
   ```

3. **Monitor performance:**
   - AWS: Use CloudWatch or `aws/monitor-dashboard.html`
   - Docker: Use `docker stats`
   - Local: Use `htop` or system monitoring tools

### Enable HTTPS

#### AWS
```bash
# Use AWS Certificate Manager
# Attach certificate to ALB listener
```

#### Docker/Local
```bash
# Use Let's Encrypt with Certbot
sudo certbot --nginx
```

### Set Up Domain

1. **Point your domain to deployment:**
   - AWS: Create Route 53 record pointing to ALB
   - Docker/Local: Point A record to server IP

2. **Update DNS:**
   ```
   A     @      your-ip-or-lb
   CNAME www    @
   ```

---

## Troubleshooting

### Common Issues

#### Application won't start
```bash
# Check logs
docker logs chimera
# or
tail -f /var/log/chimera/chimera.log

# Verify environment variables are set
printenv | grep -E "(NODE_ENV|PYTHON_ENV|DATABASE_URL)"
```

#### Database connection errors
```bash
# Verify database is running
docker ps | grep postgres
# or
systemctl status postgresql

# Test connection
psql -h localhost -U chimera -d chimera
```

#### Port already in use
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

#### Out of memory
```bash
# Check memory usage
free -h

# Increase Docker memory limit
# Edit docker-compose.yml:
services:
  chimera:
    mem_limit: 2g
```

---

## Security Best Practices

1. **Never commit secrets** to Git
2. **Use environment variables** for sensitive data
3. **Enable HTTPS** for production deployments
4. **Restrict database access** to application only
5. **Use strong passwords** for all services
6. **Keep dependencies updated**
7. **Enable firewall** on servers
8. **Use least-privilege IAM policies** (AWS)
9. **Enable MFA** for cloud accounts
10. **Regular security audits**

---

## Monitoring & Maintenance

### AWS
- Built-in CloudWatch monitoring
- Automated health checks every 15 minutes
- Custom dashboard: `aws/monitor-dashboard.html`

### Docker/Local
- Set up monitoring with Prometheus + Grafana
- Configure log rotation
- Schedule regular backups

---

## Backup & Recovery

### Database Backups

```bash
# PostgreSQL backup
pg_dump -U chimera chimera > backup.sql

# Restore
psql -U chimera chimera < backup.sql
```

### Application Backups

```bash
# Backup configuration
tar -czf config-backup.tar.gz .env config/

# Backup data directory
tar -czf data-backup.tar.gz /var/lib/chimera/
```

### Automated Backups

Add to crontab:
```bash
# Daily database backup at 2 AM
0 2 * * * pg_dump -U chimera chimera | gzip > /backups/chimera-$(date +\%Y\%m\%d).sql.gz
```

---

## Support & Resources

### Documentation
- **AWS Deployment**: [`aws/README_AWS_DEPLOYMENT.md`](aws/README_AWS_DEPLOYMENT.md)
- **Quick Start**: [`aws/QUICKSTART.md`](aws/QUICKSTART.md)
- **Cloud Guide**: [`CLOUD_DEPLOYMENT_GUIDE.md`](CLOUD_DEPLOYMENT_GUIDE.md)
- **Main README**: [`README.md`](README.md)

### Scripts & Tools
- **Auto Installer**: [`auto_install.sh`](auto_install.sh)
- **Production Setup**: [`install_chimera_production.sh`](install_chimera_production.sh)
- **Cost Calculator**: [`aws/cost-calculator.py`](aws/cost-calculator.py)
- **Setup Script**: [`aws/setup-server.sh`](aws/setup-server.sh)

### Getting Help
- **GitHub Issues**: Report bugs or request features
- **Workflow Logs**: Check GitHub Actions for deployment issues
- **AWS Console**: Monitor AWS resources

---

## Next Steps

1. Choose your deployment method
2. Follow the setup guide
3. Configure environment variables
4. Deploy your application
5. Set up monitoring
6. Enable HTTPS
7. Configure backups

**Recommended**: Start with [AWS Auto-Deploy](#aws-deployment-recommended) for production deployments.

---

**Status**: Production Ready ✅  
**Last Updated**: 2025-12-12  
**Version**: 2.0
