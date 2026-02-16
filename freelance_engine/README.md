# Freelance Platform Integration Guide

This document explains how the freelance platform connectors work and how to integrate them with real APIs.

## Current Status

**Implementation Status:** Mock/Template Mode

The freelance platform connectors are currently implemented as **template/mock implementations** that provide the structure and interface for real API integration. They demonstrate how the system would work with real freelance platform APIs.

## Why Mock Implementations?

1. **API Access Requirements**: Most freelance platforms (Fiverr, Freelancer, Toptal, etc.) require:
   - Business accounts or approved developer accounts
   - OAuth authentication flows
   - Platform approval for API access
   - Rate limiting and compliance with ToS

2. **Legal Considerations**: Automated bidding and job scanning may violate platform Terms of Service
3. **Security**: Real API keys should never be committed to public repositories
4. **Flexibility**: Mock implementations allow testing the system without platform dependencies

## How to Integrate Real APIs

### Step 1: Obtain API Credentials

For each platform you want to integrate:

#### Fiverr
- Apply for Fiverr API access: https://developers.fiverr.com/
- Obtain API key and OAuth credentials
- Review their API documentation and ToS

#### Freelancer.com
- Register for API access: https://www.freelancer.com/api
- Get your API token
- Review rate limits and allowed operations

#### Toptal
- Contact Toptal for API partnership
- Note: Toptal has strict screening processes

#### Guru
- Visit https://www.guru.com/api
- Register your application

#### PeoplePerHour
- Contact PeoplePerHour for API access

### Step 2: Configure Credentials

Add your credentials to `config/credentials.json`:

```json
{
  "freelance_platforms": {
    "fiverr": {
      "api_key": "your_fiverr_api_key",
      "api_secret": "your_secret",
      "enabled": true
    },
    "freelancer": {
      "api_key": "your_freelancer_token",
      "enabled": true
    }
  }
}
```

### Step 3: Implement Real API Calls

Replace the mock implementations in `freelance_engine/platform_connectors.py`:

#### Example: Fiverr Integration

```python
class FiverrConnector(BasePlatformConnector):
    async def scan(self) -> List[Dict]:
        """Scan Fiverr for buyer requests using real API."""
        if not self.api_key:
            logger.warning("Fiverr API key not configured")
            return []
        
        # Real API call
        async with aiohttp.ClientSession() as session:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            async with session.get(
                'https://api.fiverr.com/v1/buyer-requests',
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_fiverr_jobs(data)
                else:
                    logger.error(f"Fiverr API error: {response.status}")
                    return []
```

#### Example: Freelancer.com Integration

```python
class FreelancerConnector(BasePlatformConnector):
    async def scan(self) -> List[Dict]:
        """Scan Freelancer.com using real API."""
        if not self.api_key:
            return []
        
        async with aiohttp.ClientSession() as session:
            params = {
                'oauth_consumer_key': self.api_key,
                'limit': 20,
                'job_status': 'open'
            }
            
            async with session.get(
                'https://www.freelancer.com/api/projects/0.1/projects/',
                params=params
            ) as response:
                data = await response.json()
                return self._parse_freelancer_jobs(data)
```

### Step 4: Add Error Handling

Implement robust error handling for:
- Rate limiting (HTTP 429)
- Authentication errors (HTTP 401/403)
- Network timeouts
- API changes

### Step 5: Respect Rate Limits

Add rate limiting to your implementations:

```python
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, max_calls: int, time_window: timedelta):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
    
    def can_make_call(self) -> bool:
        now = datetime.now()
        # Remove old calls outside time window
        self.calls = [c for c in self.calls if now - c < self.time_window]
        
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        return False
```

## Mock Implementation Features

The current mock implementations demonstrate:

### ✅ Implemented Features
- **Job Scanning**: Template for retrieving jobs from platforms
- **Bid Submission**: Structure for submitting proposals
- **Work Submission**: Interface for completing projects
- **Job Parsing**: Converting platform-specific formats to standard format
- **Error Handling**: Basic error handling structure
- **Async Operations**: Async/await patterns for I/O operations
- **Logging**: Comprehensive logging of all operations

### 🔄 Mock Behavior
- Returns simulated job listings
- Simulates successful bid submissions
- Simulates work completion
- No actual API calls made
- Safe for testing without credentials

## Testing the System

You can test the freelance system with mock data:

```bash
# Run the freelance orchestrator
python3 -m freelance_engine.orchestrator

# The system will:
# - Scan for jobs (mock data)
# - Evaluate opportunities
# - Make bid decisions
# - Log all operations
```

## Security Best Practices

When implementing real APIs:

1. **Never commit credentials**: Use environment variables
2. **Rotate API keys regularly**: Implement key rotation
3. **Use HTTPS only**: All API calls over secure connections
4. **Validate responses**: Always validate API responses
5. **Audit logging**: Log all API interactions for compliance
6. **Respect ToS**: Ensure your usage complies with platform Terms of Service

## Production Deployment

Before deploying with real APIs:

1. ✅ Obtain proper API access from each platform
2. ✅ Review and comply with each platform's Terms of Service
3. ✅ Implement proper error handling and retry logic
4. ✅ Add comprehensive logging and monitoring
5. ✅ Test with rate limiting in place
6. ✅ Implement credential rotation
7. ✅ Set up alerts for API failures
8. ✅ Have manual approval workflow for high-value jobs

## Legal Disclaimer

**IMPORTANT**: Automated bidding and job scanning may violate the Terms of Service of freelance platforms. Before implementing real API integrations:

- Review each platform's Terms of Service
- Ensure automated actions are permitted
- Consider requiring manual approval for all bids
- Implement human-in-the-loop workflows
- Consult with legal counsel if necessary

## Support

For questions or issues:
- Review platform API documentation
- Check platform developer forums
- Ensure compliance with platform ToS
- Test thoroughly in development before production

## Future Enhancements

Planned improvements:
- WebSocket connections for real-time job notifications
- Machine learning for bid optimization
- Multi-platform job comparison
- Automated skill matching
- Revenue tracking and analytics
- Client relationship management
