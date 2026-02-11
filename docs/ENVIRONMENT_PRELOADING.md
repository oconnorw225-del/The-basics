# Chimera Environment & Secrets Preloading Guide

## Overview

The Chimera Autonomous Learning System now includes an advanced environment and secrets preloading mechanism that automatically configures all necessary credentials, environment variables, and platform linkages for optimized Railway deployment strategy.

## Features

### 🔐 Automatic Secret Management
- Preloads all environment variables on system startup
- Manages credentials across multiple platforms (Railway, GitHub, AWS, etc.)
- Secure credential caching with proper permissions
- Validates deployment readiness before deployment

### 🚂 Railway Integration
- Automatic Railway environment configuration
- Credential validation for Railway deployments
- Export environment variables in Railway-compatible format
- Platform-to-platform authentication

### 🔄 Platform Linkage
- Continuous linkage between GitHub and Railway
- Automatic credential synchronization
- Optimized deployment strategy and running order
- Multi-platform deployment coordination

### 🛡️ Security
- Secrets never committed to git
- Secure file permissions (0600/0700)
- Encrypted credential storage
- Audit logging for credential access

## Quick Start

### 1. Configure Secrets

Copy the secrets template and fill in your credentials:

```bash
cp config/secrets.template.yaml config/secrets.yaml
# Edit config/secrets.yaml with your actual credentials
```

**IMPORTANT:** Never commit `secrets.yaml` to git! It's already in `.gitignore`.

### 2. Set GitHub Secrets

Set required secrets in your GitHub repository:

```bash
# Using GitHub CLI
gh secret set RAILWAY_TOKEN --body "your-railway-token"
gh secret set SECRET_KEY --body "$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
gh secret set JWT_SECRET --body "$(python3 -c 'import secrets; print(secrets.token_hex(32))')"

# Optional: Trading API credentials
gh secret set NDAX_API_KEY --body "your-ndax-api-key"
gh secret set NDAX_API_SECRET --body "your-ndax-api-secret"

# Optional: Database URLs
gh secret set DATABASE_URL --body "postgresql://user:pass@host:port/db"
gh secret set REDIS_URL --body "redis://host:port"
```

### 3. Run the System

The environment preloader runs automatically on system startup:

```bash
# Start the unified system
python3 unified_system.py
```

Output will show:
```
🔐 Preloading environments, secrets, and credentials...
  ✓ Loaded 15 environment variables
  ✓ 7 secrets configured
  ✓ Platforms: railway, github
  ✓ Railway credentials detected
  ✓ Railway environment exported to .env.railway

🚂 Validating Railway deployment configuration...
  ✅ Railway deployment validated
```

## Environment Preloader API

### Python Usage

```python
from backend.chimera_env_preloader import create_env_preloader

# Create preloader instance
preloader = create_env_preloader()

# Preload all environments
summary = preloader.preload_all_environments()
print(f"Loaded {summary['total_variables']} variables")

# Get Railway-specific environment
railway_env = preloader.get_railway_environment()
railway_secrets = preloader.get_railway_secrets()

# Validate Railway deployment
validation = preloader.validate_railway_deployment()
if validation['valid']:
    print("✅ Ready for Railway deployment")

# Export to .env file for Railway
preloader.export_to_dotenv(".env.railway")
```

### Command Line Usage

Test the preloader directly:

```bash
# Run the demonstration
python3 backend/chimera_env_preloader.py
```

## Railway Deployment

### Automatic Deployment via GitHub Actions

The workflow automatically:
1. Preloads all environment variables and secrets
2. Validates Railway deployment configuration
3. Exports environment to `.env.railway`
4. Deploys to Railway with all credentials configured

### Manual Railway Deployment

```bash
# Install Railway CLI
curl -fsSL https://railway.app/install.sh | sh

# Preload environment
python3 unified_system.py  # Creates .env.railway

# Deploy to Railway
railway up --service chimera-system
```

### Setting Railway Environment Variables

Option 1: Via Railway Dashboard
1. Go to your Railway project
2. Select your service
3. Navigate to "Variables" tab
4. Add variables from `.env.railway`

Option 2: Via Railway CLI
```bash
# Set variables from .env.railway
railway variables set NODE_ENV=production
railway variables set PYTHON_ENV=production
railway variables set API_PORT=8000
# ... etc
```

## Environment Variables

### Core Application Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `NODE_ENV` | `production` | Node.js environment |
| `PYTHON_ENV` | `production` | Python environment |
| `API_PORT` | `8000` | API server port |
| `API_HOST` | `0.0.0.0` | API server host |

### Trading Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `TRADING_MODE` | `paper` | Trading mode: paper or live |
| `RISK_TOLERANCE` | `0.05` | Risk tolerance level (5%) |
| `MAX_POSITION_SIZE` | `0.1` | Maximum position size (10%) |

### Security Settings

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | Application secret key |
| `JWT_SECRET` | Yes | JWT token secret |
| `WEBHOOK_SECRET` | No | Webhook signature secret |
| `ENCRYPTION_KEY` | No | Data encryption key |

### Database Settings (Optional)

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection URL |
| `REDIS_URL` | Redis connection URL |
| `MONGODB_URL` | MongoDB connection URL |

### API Credentials (Optional)

| Variable | Description |
|----------|-------------|
| `NDAX_API_KEY` | NDAX exchange API key |
| `NDAX_API_SECRET` | NDAX exchange API secret |
| `EXCHANGE_API_KEY` | Generic exchange API key |
| `EXCHANGE_API_SECRET` | Generic exchange API secret |

### Wallet Addresses (Optional)

| Variable | Description |
|----------|-------------|
| `INFLOW_WALLET_ADDR` | Inflow wallet address |
| `OPERATIONAL_WALLET_ADDR` | Operational wallet address |
| `COLD_STORAGE_ADDR` | Cold storage wallet address |
| `EMERGENCY_WALLET_ADDR` | Emergency wallet address |

## Security Best Practices

### 1. Never Commit Secrets

```bash
# Verify secrets.yaml is ignored
git check-ignore config/secrets.yaml
# Should output: config/secrets.yaml

# Verify .env.railway is ignored
git check-ignore .env.railway
# Should output: .env.railway
```

### 2. Use Environment-Specific Configuration

```bash
# Development
cp .env.example .env

# Staging
cp .env.example .env.staging

# Production
cp .env.example .env.production
```

### 3. Rotate Credentials Regularly

```bash
# Generate new secret keys
python3 -c "import secrets; print(secrets.token_hex(32))"

# Update in GitHub secrets
gh secret set SECRET_KEY --body "new-secret-key"
```

### 4. Enable Audit Logging

Set in `config/secrets.yaml`:
```yaml
security:
  audit_logging: true
  encrypt_at_rest: true
  auto_rotate_credentials: true
  rotation_interval_days: 90
```

## Troubleshooting

### Railway Token Not Found

```
❌ RAILWAY_TOKEN not configured
```

**Solution:** Set the RAILWAY_TOKEN secret in GitHub:
```bash
gh secret set RAILWAY_TOKEN --body "your-railway-token"
```

### Missing Required Variables

```
⚠️ Missing required environment variables: ['SECRET_KEY', 'JWT_SECRET']
```

**Solution:** Generate and set the required secrets:
```bash
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
JWT_SECRET=$(python3 -c 'import secrets; print(secrets.token_hex(32))')

gh secret set SECRET_KEY --body "$SECRET_KEY"
gh secret set JWT_SECRET --body "$JWT_SECRET"
```

### Permission Denied on Secrets Directory

```
❌ Could not set directory permissions
```

**Solution:** Ensure you have write permissions:
```bash
chmod 700 .unified-system/secrets
chmod 700 .unified-system/cache
```

### Railway Deployment Validation Failed

```
⚠️ Railway deployment validation warnings:
    - RAILWAY_TOKEN not configured
```

**Solution:** Verify your Railway token is valid:
```bash
# Test Railway CLI
railway login

# Verify token
railway whoami
```

## Advanced Configuration

### Custom Platform Credentials

```python
from backend.chimera_env_preloader import (
    ChimeraEnvPreloader, 
    PlatformType, 
    PlatformCredentials
)

preloader = ChimeraEnvPreloader()

# Add custom platform
custom_creds = PlatformCredentials(
    platform=PlatformType.CUSTOM,
    api_token="your-custom-token",
    project_id="your-project",
    api_url="https://api.custom.com"
)

preloader.platform_credentials[PlatformType.CUSTOM] = custom_creds
```

### Custom Environment Variables

```python
from backend.chimera_env_preloader import EnvironmentVariable, PlatformType

# Define custom variable
custom_var = EnvironmentVariable(
    key="CUSTOM_API_KEY",
    value="your-api-key",
    platform=PlatformType.RAILWAY,
    is_secret=True,
    required=True,
    description="Custom API key"
)

preloader.env_cache["CUSTOM_API_KEY"] = custom_var
```

## Integration with Chimera System

The environment preloader integrates seamlessly with the Chimera autonomous learning system:

1. **System Initialization:** Preloads all environments on startup
2. **Railway Deployment:** Exports configuration for Railway
3. **Credential Validation:** Ensures all required credentials are present
4. **Platform Linkage:** Maintains continuous synchronization

### Chimera Component Integration

```python
from backend.chimera_base import ChimeraComponentBase
from backend.chimera_env_preloader import create_env_preloader

class MyChimeraComponent(ChimeraComponentBase):
    def __init__(self):
        super().__init__()
        self.env_preloader = create_env_preloader()
        
        # Preload environments
        self.env_preloader.preload_all_environments()
        
        # Use credentials
        railway_env = self.env_preloader.get_railway_environment()
        self.log_success(f"Loaded {len(railway_env)} variables")
```

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review logs in `.unified-system/logs/system.log`
3. Run the preloader demo: `python3 backend/chimera_env_preloader.py`
4. Check GitHub Actions logs for deployment issues

## See Also

- [Security Policy](../SECURITY.md)
- [Deployment Guide](../DEPLOYMENT.md)
- [Railway Deployment Runbook](../RUNBOOK.md)
- [Secrets Configuration Template](../config/secrets.template.yaml)
