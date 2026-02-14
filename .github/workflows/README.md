# GitHub Actions Workflows

This repository uses modern, purpose-built workflows for the bot coordination system.

## Active Workflows

### 🚀 Bot System Workflows

1. **bot-startup.yml** - Start the bot coordination system
   - Manual trigger with environment and bot selection
   - Verifies kill switch before starting
   - Supports staging and production environments
   - Allows starting all bots or individual bots (NDAX, Quantum, ShadowForge)

2. **bot-health-monitor.yml** - Continuous health monitoring
   - Runs automatically every 15 minutes
   - Checks all bot health endpoints
   - Triggers recovery workflow if bots fail
   - Manual trigger available for on-demand checks

3. **kill-switch-monitor.yml** - Kill switch status checks
   - Runs automatically every 5 minutes
   - Monitors kill switch status
   - Displays current bot limits
   - Manual trigger available

4. **bot-recovery.yml** - Automated bot recovery
   - Triggered automatically by health monitor failures
   - Manual trigger available for emergency recovery
   - Implements recovery procedures

### 🧪 CI/CD Workflows

1. **ci-test-bots.yml** - Automated testing on PRs and commits
   - Validates all config files as valid JSON
   - Runs pytest tests if available
   - Lints Python files (non-blocking)
   - Runs on pull requests and pushes to main

2. **deploy-production.yml** - Production deployment
   - Manual trigger only
   - Requires typing "DEPLOY" to confirm
   - Runs pre-deployment checks (kill switch verification)
   - Safe deployment with verification steps

### 🛠️ Utility Workflows

1. **auto-fix-and-deploy.yml** - Automated fixes and deployment
2. **chimera-system-restore.yml** - Chimera system restoration
3. **security-audit.yml** - Security auditing

## How to Use

### Starting the Bot System
1. Go to Actions → "Start Bot Coordination System"
2. Click "Run workflow"
3. Select environment (staging/production)
4. Select which bots to start (all/ndax/quantum/shadowforge)
5. Click "Run workflow" to start

### Monitoring
- Health checks run automatically every 15 minutes
- Kill switch monitoring runs every 5 minutes
- Check the Actions tab for latest status
- Failed health checks automatically trigger recovery

### Deploying to Production
1. Go to Actions → "Deploy Bot System to Production"
2. Click "Run workflow"
3. Type "DEPLOY" in the confirmation field
4. Click "Run workflow"
5. System will run pre-deployment checks and deploy

## Removed Workflows

The following redundant workflows have been deleted to prevent conflicts:

**CRITICAL REMOVAL:**
- ✅ `consolidate.yml` - Was overwriting new code by cloning external repos

**AWS Deployment Workflows (7 files):**
- ✅ `blank.yml.disabled` - Demo workflow
- ✅ `deploy-to-aws.yml.disabled`
- ✅ `complete-aws-setup.yml.disabled`
- ✅ `setup-aws-infrastructure.yml.disabled`
- ✅ `monitor-aws.yml.disabled`

**Branch Cleanup Workflows (3 files):**
- ✅ `cleanup-branches.yml.disabled`
- ✅ `cleanup-stale-branches.yml.disabled`
- ✅ `CLEANUP_STALE_BRANCHES_README.md`

## Architecture

### Bot System Components

**Backend Bots:**
- `backend/quantum_bot.py` - Quantum-inspired trading bot
- `backend/shadowforge_bot.py` - AI-driven strategy bot
- `backend/ndax_bot.js` - NDAX exchange integration bot
- `backend/bot-coordinator.py` - Main coordinator managing all bots

**Configuration:**
- `config/bot-limits.json` - Trading limits per bot
- `config/kill-switch.json` - Emergency stop configuration
- `config/api-endpoints.json` - Service endpoints and health checks
- `config/recovery-settings.json` - Recovery procedures
- `config/notification-config.json` - Alert configuration

### Workflow Dependencies

```
bot-health-monitor.yml (every 15 min)
    ↓ (on failure)
bot-recovery.yml (auto-triggered)

kill-switch-monitor.yml (every 5 min)
    ↓ (monitors)
config/kill-switch.json

ci-test-bots.yml (on PR/push)
    ↓ (validates)
All config files + backend code
```

## Configuration

### Environment Variables

For production deployment, configure these environment variables (see `.env.example`):

**Required:**
- `NDAX_API_KEY` - NDAX exchange API key
- `NDAX_API_SECRET` - NDAX exchange API secret

**Optional (for notifications):**
- `SLACK_WEBHOOK_URL` - Slack notifications
- `DISCORD_WEBHOOK_URL` - Discord notifications
- `API_HOST` - API server host (default: 0.0.0.0)
- `API_PORT` - API server port (default: 8000)
- `ENVIRONMENT` - Deployment environment (staging/production)

### Secrets Configuration

Add secrets in repository Settings → Secrets and variables → Actions:
1. `NDAX_API_KEY` - For NDAX trading
2. `NDAX_API_SECRET` - For NDAX trading
3. `SLACK_WEBHOOK_URL` - For Slack alerts (optional)
4. `DISCORD_WEBHOOK_URL` - For Discord alerts (optional)

## Design Principles

All workflows follow these principles:

1. **Minimal Conflicts** - No cloning of external repos that overwrite work
2. **Safety First** - Kill switch checks before critical operations
3. **Automated Recovery** - Failed bots trigger automatic recovery
4. **Clear Monitoring** - Regular health checks with visible status
5. **Manual Controls** - Critical actions require manual confirmation
6. **Comprehensive Testing** - CI validates configs and runs tests

## Troubleshooting

### Bot health checks failing
1. Check bot health monitor workflow logs
2. Verify bots are running and accessible
3. Check `config/api-endpoints.json` for correct URLs
4. Recovery workflow should trigger automatically

### Kill switch is active
1. Check `config/kill-switch.json` for reason
2. Review kill switch monitor logs
3. Resolve the issue that triggered it
4. Manually update kill switch to inactive

### Deployment blocked
1. Verify kill switch is inactive
2. Check pre-deployment checks in workflow logs
3. Ensure all config files are valid JSON
4. Run CI tests locally first

### Config validation errors
Run locally:
```bash
python -c "import json; json.load(open('config/bot-limits.json'))"
python -c "import json; json.load(open('config/kill-switch.json'))"
# etc for all config files
```

## Best Practices

When modifying workflows:

1. ✅ Test locally before committing
2. ✅ Validate YAML syntax
3. ✅ Add appropriate error handling
4. ✅ Include clear log messages
5. ✅ Use conditional execution for optional steps
6. ✅ Document any new environment variables
7. ✅ Test both success and failure scenarios

## Security

- All workflows use pinned action versions (e.g., `@v4`, `@v5`)
- No secrets are exposed in logs
- Kill switch provides emergency stop capability
- CodeQL security scanning on all workflows
- Pre-deployment checks prevent unsafe deployments

## Support

For issues:
1. Check workflow logs in Actions tab
2. Review troubleshooting section above
3. Verify configuration files are valid JSON
4. Check bot health status in monitoring logs

---

**Last Updated**: 2026-02-14
**Status**: ✅ Modern bot coordination system with 5 new workflows, redundant workflows removed
