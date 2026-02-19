# Bot Public Access System

## Quick Start

This system provides public access to platform information for bots while protecting sensitive data.

### For Bots

**Get public platform information:**
```bash
curl http://localhost:8000/api/public/platform
```

**List all public endpoints:**
```bash
curl http://localhost:8000/api/public/endpoints
```

**View product information:**
```bash
curl http://localhost:8000/api/public/products
```

**Check system capabilities:**
```bash
curl http://localhost:8000/api/public/capabilities
```

**View documentation:**
```bash
curl http://localhost:8000/api/public/documentation
```

### What Bots Can See (Public)

✅ **Safe to expose:**
- Service metadata (name, version, status)
- Health status
- Public metrics
- Product information
- Platform capabilities
- Documentation
- API specifications
- Public market data
- Bot registry summary

### What Bots Cannot See (Private)

❌ **Protected:**
- Credentials (API keys, passwords)
- Secrets and tokens
- Private keys
- Wallet addresses
- User identity
- Personal information
- Trading positions
- Account balances
- Security settings

### Access Levels

1. **Public Bots** - No authentication, public endpoints only
2. **Registered Bots** - API key required, limited private access
3. **Trusted Bots** - API key required, most endpoints
4. **Admin Bots** - Full access with admin key

### For Developers

**Enable access control in API Gateway:**
```python
from src.api.gateway import create_api_gateway

# Create gateway with access control
gateway = create_api_gateway(enable_access_control=True)
```

**Test access control:**
```bash
cd /home/runner/work/The-basics/The-basics
python src/middleware/bot_access_control.py
```

**Test public bot API:**
```bash
python api/public_bot_api.py
```

### Configuration

Edit `/config/bot-public-access.json` to:
- Add/remove public endpoints
- Modify private endpoints
- Update access levels
- Change security rules

### Documentation

Full documentation: `docs/BOT_PUBLIC_ACCESS.md`

### Security

- All private endpoints require authentication
- Rate limiting applied based on bot type
- Access attempts are logged
- Error messages are sanitized
- Credentials are never exposed publicly

---

**Version:** 1.0.0  
**Last Updated:** 2026-02-16
