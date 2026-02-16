# Bot Public Access Configuration

## Overview

This document explains the public access configuration for bots in the Autonomous Chimera System. It defines what information bots can access publicly versus what requires authentication, ensuring security while providing transparency.

## Purpose

The bot public access system serves two key purposes:

1. **Security**: Protect sensitive data (credentials, private keys, user identity) from unauthorized access
2. **Transparency**: Provide bots with clear access to public information (product info, platform capabilities, documentation)

## Configuration File

**Location**: `/config/bot-public-access.json`

This file defines:
- Public endpoints (no authentication required)
- Private endpoints (authentication required)
- Data classification (public vs private)
- Bot access levels
- Security rules

## Public Endpoints

Bots can access these endpoints WITHOUT authentication:

### System Information
- `GET /` - Service information
- `GET /health` - Health check
- `GET /status` - System status
- `GET /metrics` - Public performance metrics

### Public Information
- `GET /api/info` - API information and documentation
- `GET /api/products` - Product information and catalog
- `GET /api/platform/info` - Platform capabilities and features
- `GET /api/bots/registry` - Bot registry public summary
- `GET /api/market/public` - Public market data
- `GET /docs` - Public documentation

### Public Bot API
- `GET /api/public/platform` - Platform information
- `GET /api/public/endpoints` - List of all public endpoints
- `GET /api/public/products` - Product catalog
- `GET /api/public/capabilities` - System capabilities
- `GET /api/public/access-levels` - Information about access levels
- `GET /api/public/documentation` - Documentation links

## Private Endpoints

These endpoints require authentication and are NOT publicly accessible:

### Credentials and Secrets
- `/api/credentials/*` - API keys, secrets, passwords
- `/api/wallet/*` - Wallet addresses, private keys, balances

### User Information
- `/api/user/*` - User identity, email, personal data

### Operations
- `POST /api/trading/execute` - Trade execution
- `/api/admin/*` - Administrative functions
- `/api/backup/*` - Backup operations
- `POST /control` - Bot control operations
- `/kill-switch` - Emergency kill switch

## Data Classification

### Public Data (Safe to Expose)
- Service metadata
- Health status
- Public metrics
- Product information
- Platform capabilities
- Documentation
- API specifications
- Public market data
- Bot registry summary

### Private Data (Protected)
- Credentials (API keys, passwords)
- Secrets and tokens
- Private keys
- Wallet addresses
- User identity
- Personal information
- Email addresses
- Trading positions
- Account balances
- Transaction history
- Security settings
- Backup data
- Internal configuration

## Bot Access Levels

### Public Bots
- **Description**: External/untrusted bots
- **Authentication**: Not required
- **Access**: Public endpoints only
- **Rate Limit**: 100 requests/minute

### Registered Bots
- **Description**: Internal system bots
- **Authentication**: Required (API key)
- **Access**: Public endpoints + limited private access
- **Rate Limit**: 500 requests/minute
- **Additional Access**: Bot status, coordination heartbeat

### Trusted Bots
- **Description**: Trading and operation bots (NDAX, Quantum, ShadowForge)
- **Authentication**: Required (API key)
- **Access**: Most endpoints except admin-only
- **Rate Limit**: 1000 requests/minute
- **Additional Access**: Trading status, private market data

### Admin Bots
- **Description**: Full system access
- **Authentication**: Required (admin API key)
- **Access**: All endpoints
- **Rate Limit**: Unlimited

## How Bots Should Use This

### For Public Bots

1. Access public information without authentication:
```bash
curl http://localhost:8000/api/public/platform
curl http://localhost:8000/api/public/endpoints
curl http://localhost:8000/api/public/products
```

2. Check what capabilities are available:
```bash
curl http://localhost:8000/api/public/capabilities
```

3. View documentation:
```bash
curl http://localhost:8000/api/public/documentation
```

### For Registered/Trusted Bots

1. Include bot type and API key in headers:
```bash
curl -H "X-Bot-Type: trusted" \
     -H "X-API-Key: your-api-key" \
     http://localhost:8000/api/trading/status
```

2. Check access level requirements:
```bash
curl http://localhost:8000/api/public/access-levels
```

## Security Rules

1. **No Credentials in Public**: Credentials, API keys, and secrets are NEVER exposed in public endpoints
2. **No Identity Leakage**: User identity and personal information is protected
3. **No Wallet Exposure**: Wallet addresses and private keys are never public
4. **Sanitized Errors**: Error messages don't leak sensitive information
5. **Rate Limiting**: All endpoints have rate limits to prevent abuse
6. **Access Logging**: All private endpoint access is logged

## Integration Examples

### Using with API Gateway

```python
from src.api.gateway import APIGateway
from src.middleware.bot_access_control import create_access_control_middleware, access_control_middleware

# Create access control
access_control = create_access_control_middleware()

# Create API gateway
gateway = APIGateway()

# Add access control middleware
gateway.add_middleware(access_control_middleware(access_control))
```

### Using with FastAPI

```python
from fastapi import FastAPI
from api.public_bot_api import register_public_bot_routes

app = FastAPI()

# Register public bot routes
register_public_bot_routes(app)
```

### Testing Access Control

```python
from src.middleware.bot_access_control import create_access_control_middleware

access_control = create_access_control_middleware()

# Test public endpoint
result = access_control.check_access("/health", "GET", "public")
print(f"Allowed: {result['allowed']}")  # True

# Test private endpoint without auth
result = access_control.check_access("/api/credentials/list", "GET", "public")
print(f"Allowed: {result['allowed']}")  # False

# Test with trusted bot
result = access_control.check_access("/api/trading/status", "GET", "trusted", api_key="key")
print(f"Allowed: {result['allowed']}")  # True
```

## Updating Configuration

To modify public/private access:

1. Edit `/config/bot-public-access.json`
2. Add/remove endpoints from `public_endpoints` or `private_endpoints`
3. Update data classification if needed
4. Restart services to apply changes

## Monitoring

Access attempts are logged for security monitoring:
- All failed access attempts to private endpoints are logged
- Includes: timestamp, client_id, bot_type, path, method, result

## Best Practices

1. **Default to Private**: When in doubt, make an endpoint private
2. **Minimize Exposure**: Only expose what's necessary for public access
3. **Sanitize Responses**: Always sanitize responses to remove sensitive data
4. **Use Authentication**: Use API keys for registered/trusted/admin bots
5. **Rate Limit**: Apply appropriate rate limits based on bot type
6. **Monitor Access**: Review access logs regularly
7. **Update Documentation**: Keep this documentation in sync with config changes

## Support

For questions or issues:
- Check documentation: `/api/public/documentation`
- Review configuration: `/config/bot-public-access.json`
- View public endpoints: `GET /api/public/endpoints`
- GitHub: https://github.com/oconnorw225-del/The-basics

## Version History

- **1.0.0** (2026-02-16): Initial bot public access configuration
  - Public/private endpoint classification
  - Bot access levels
  - Security rules
  - Public bot API endpoints
  - Access control middleware
