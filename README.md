# the-basics

Autonomous Chimera system with comprehensive infrastructure for trading, freelance AI operations, and platform integration.

Automated consolidation of best parts from:
- ndax-quantum-engine
- quantum-engine-dashb
- shadowforge-ai-trader
- repository-web-app
- The-new-ones

## Quick Start

### System Restoration

To restore and reconfigure the autonomous Chimera system:

1. Go to **Actions** > **Autonomous Chimera System Restoration**
2. Click **Run workflow**
3. Configure restoration options:
   - **Scan mode**: Choose `full` for comprehensive scan
   - **Auto fix**: Enable to automatically fix issues
   - **Restore trading**: Enable to restore trading operations
   - **Restore freelance**: Enable to restore freelance AI jobs
   - **Restore bots**: Enable to restore bot connections
4. Review restoration report in workflow artifacts

See [Chimera Restoration Guide](docs/CHIMERA_RESTORATION.md) for detailed instructions.

### Consolidation

To consolidate code from source repositories:

1. Go to **Actions** > **Consolidate Best Parts**
2. Click **Run workflow**
3. Review and use your unified repo!

## Workflows

### 🤖 Autonomous Chimera System Restoration
**File**: `.github/workflows/chimera-system-restore.yml`

Comprehensive system restoration workflow that:
- Scans all platforms (GitHub, Railway, connected services)
- Analyzes configuration and identifies issues
- Generates and executes restoration plan
- Re-establishes bot connections and platform integrations
- Restores trading operations (paper mode)
- Restores freelance AI operations
- Validates system at maximum capacity

**Usage**: Manually trigger from Actions tab with configuration options.

**Documentation**: [docs/CHIMERA_RESTORATION.md](docs/CHIMERA_RESTORATION.md)

### 📦 Consolidate Best Parts
**File**: `.github/workflows/consolidate.yml`

Consolidates code from multiple source repositories into unified structure.

**Usage**: Manually trigger from Actions tab.

## Contents
- `/api` — consolidated APIs
- `/backend` — backend logic including Chimera system
- `/frontend` — UI components
- `/docs` — comprehensive documentation
- `/tests` — test suites
- `/automation` — scripts for consolidation and restoration
- `/backups` — archived original sources
- `/freelance_engine` — AI-based freelance job system
- `/chimera_core` — core Chimera autonomous system

## Documentation

- [Chimera Restoration Guide](docs/CHIMERA_RESTORATION.md) - System restoration and recovery
- [Architecture](docs/ARCHITECTURE.md) - System architecture overview
- [Entry Points](docs/ENTRY_POINTS.md) - System entry points guide
- [Runbook](RUNBOOK.md) - Operations runbook
- [Deployment](DEPLOYMENT.md) - Deployment guide

## System Components

### Autonomous Chimera System
Multi-version autonomous system (V4-V8) with:
- Autonomous trading operations
- Self-learning AI
- Multi-chain crypto operations
- Treasury management
- Solvency monitoring

### Freelance Engine
AI-based freelance job operations:
- Job prospecting
- Automated bidding
- Internal coding agent
- Payment handling

### Bot Operations
Automated bot systems for:
- Trading automation
- Platform monitoring
- Task automation

## Configuration

Copy `.env.example` to `.env` and configure:
- API keys for exchanges
- Platform tokens (Railway, GitHub)
- Trading parameters
- Bot configurations

## Safety

- Trading operations default to **paper mode**
- All configuration changes are backed up
- Comprehensive validation before declaring success
- Manual approval required for critical operations
