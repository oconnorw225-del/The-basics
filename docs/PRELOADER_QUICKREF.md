# Chimera Environment Preloader - Quick Reference

## Commands

### Test Preloader
```bash
python3 backend/chimera_env_preloader.py
```

### Run Unified System (with preloading)
```bash
python3 unified_system.py
```

### Generate Secret Keys
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### Set GitHub Secrets
```bash
# Railway token
gh secret set RAILWAY_TOKEN --body "your-token"

# Application secrets
gh secret set SECRET_KEY --body "$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
gh secret set JWT_SECRET --body "$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
```

## Environment Variables

### Core (Required)
- `NODE_ENV=production`
- `PYTHON_ENV=production`
- `API_PORT=8000`
- `API_HOST=0.0.0.0`

### Security (Required)
- `SECRET_KEY=<generated>`
- `JWT_SECRET=<generated>`

### Trading (Defaults)
- `TRADING_MODE=paper`
- `RISK_TOLERANCE=0.05`
- `MAX_POSITION_SIZE=0.1`

### Optional
- `DATABASE_URL` - PostgreSQL URL
- `REDIS_URL` - Redis URL
- `NDAX_API_KEY` - NDAX key
- `NDAX_API_SECRET` - NDAX secret

## Files

### Configuration
- `config/secrets.template.yaml` - Template
- `config/secrets.yaml` - Your secrets (git-ignored)
- `.env.railway` - Railway env (generated, git-ignored)

### Preloader Cache
- `.unified-system/secrets/` - Credential storage
- `.unified-system/cache/preload_cache.json` - Cache metadata

## Python API

```python
from backend.chimera_env_preloader import create_env_preloader

# Create preloader
preloader = create_env_preloader()

# Preload environments
summary = preloader.preload_all_environments()

# Get Railway environment
railway_env = preloader.get_railway_environment()
railway_secrets = preloader.get_railway_secrets()

# Validate deployment
validation = preloader.validate_railway_deployment()

# Export to file
preloader.export_to_dotenv(".env.railway")
```

## Workflow Integration

### GitHub Actions
```yaml
- name: Preload environment
  run: |
    python3 -c "
    from backend.chimera_env_preloader import create_env_preloader
    preloader = create_env_preloader()
    preloader.preload_all_environments()
    preloader.export_to_dotenv('.env.railway')
    "
```

### Railway Deployment
```bash
# Install Railway CLI
curl -fsSL https://railway.app/install.sh | sh

# Deploy with preloaded config
railway up --service chimera-system
```

## Security Checklist

- [ ] secrets.yaml in .gitignore
- [ ] .env.railway in .gitignore
- [ ] GitHub secrets configured
- [ ] Railway token set
- [ ] File permissions set (700/600)
- [ ] Secrets not in git history
- [ ] Audit logging enabled

## Troubleshooting

### RAILWAY_TOKEN not configured
```bash
gh secret set RAILWAY_TOKEN --body "your-token"
```

### Missing required variables
```bash
gh secret set SECRET_KEY --body "$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
```

### Permission denied
```bash
chmod 700 .unified-system/secrets
chmod 700 .unified-system/cache
```

### Validation failed
```bash
# Check Railway CLI
railway login
railway whoami
```

## Support

- 📖 [Full Documentation](ENVIRONMENT_PRELOADING.md)
- ⚙️ [Secrets Template](../config/secrets.template.yaml)
- 🔒 [Security Policy](../SECURITY.md)
- 📘 [Deployment Guide](../DEPLOYMENT.md)
