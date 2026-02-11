# Autonomous Chimera System Restoration

## Overview

The **Autonomous Chimera System Restoration** workflow is designed to scan, analyze, and restore all platform connections and autonomous operations across the entire infrastructure. This workflow addresses the need for a comprehensive system recovery and reconfiguration process.

## Purpose

This workflow:
- Scans all platforms (GitHub repositories, Railway app, and connected services)
- Analyzes system configuration and identifies issues
- Compares current state vs required state for full operations
- Generates a restoration plan for autonomous systems
- Executes reconfiguration tasks automatically
- Re-establishes connections with bots, platforms, and data sources
- Restores trading operations, freelance AI jobs, and crypto-related operations
- Validates all systems are operating at maximum capacity

## Workflow: `chimera-system-restore.yml`

### Triggering the Workflow

The workflow can be manually triggered from GitHub Actions:

1. Go to **Actions** tab in the repository
2. Select **Autonomous Chimera System Restoration** workflow
3. Click **Run workflow**
4. Configure the following options:
   - **Scan mode**: `full`, `quick`, or `critical-only`
   - **Auto fix**: Enable to automatically fix identified issues
   - **Restore trading**: Enable to restore trading operations
   - **Restore freelance**: Enable to restore freelance AI operations
   - **Restore bots**: Enable to restore bot connections

### Workflow Jobs

#### 1. Scan Platforms
- Scans GitHub repositories for missing files, disabled workflows, and configuration issues
- Checks Railway deployments and configuration
- Scans all connected platforms and services
- Analyzes system state and identifies issues
- Outputs: Scan results artifact

#### 2. Generate Restoration Plan
- Analyzes scan results
- Generates comprehensive restoration plan with prioritized tasks
- Identifies dependencies between restoration tasks
- Outputs: Restoration plan artifact

#### 3. Execute Restoration
- Restores system configuration with backups
- Re-establishes bot connections
- Restores trading operations (in paper mode by default)
- Restores freelance AI operations
- Re-establishes platform connections
- Restores workflow configurations
- Validates restored system
- Commits changes back to repository
- Outputs: Restoration results artifact

#### 4. Verify Operations
- Verifies Chimera system operational
- Verifies bot connections
- Verifies trading operations
- Verifies freelance operations
- Checks system capacity
- Generates final restoration report
- Outputs: Final report artifact

#### 5. Notify Completion
- Creates workflow summary with restoration details
- Provides system status overview
- Lists next steps for manual verification

## Supporting Scripts

### 1. `backend/system_restoration.py`

Main Python orchestrator for system restoration. Provides commands:

```bash
# Analyze system and generate scan results
python backend/system_restoration.py analyze --output scan_results.json

# Generate restoration plan
python backend/system_restoration.py plan \
  --input scan_results.json \
  --output restoration_plan.json \
  --trading=true --freelance=true --bots=true

# Restore system configuration
python backend/system_restoration.py restore-config \
  --plan restoration_plan.json \
  --backup-dir .restoration-backups/

# Restore bot connections
python backend/system_restoration.py restore-bots --plan restoration_plan.json

# Restore trading operations
python backend/system_restoration.py restore-trading \
  --plan restoration_plan.json \
  --mode paper

# Restore freelance operations
python backend/system_restoration.py restore-freelance --plan restoration_plan.json

# Restore platform connections
python backend/system_restoration.py restore-platforms --plan restoration_plan.json

# Validate system
python backend/system_restoration.py validate \
  --plan restoration_plan.json \
  --output validation_results.json

# Verify individual components
python backend/system_restoration.py verify-bots
python backend/system_restoration.py verify-trading
python backend/system_restoration.py verify-freelance

# Check system capacity
python backend/system_restoration.py check-capacity --output capacity_report.json

# Generate final report
python backend/system_restoration.py report \
  --validation validation_results.json \
  --capacity capacity_report.json \
  --output RESTORATION_REPORT.md
```

### 2. `automation/system_scanner.py`

Platform scanner for identifying issues:

```bash
# Scan GitHub repositories
python automation/system_scanner.py --platform github --mode full

# Scan Railway deployments
python automation/system_scanner.py --platform railway --mode full

# Scan all platforms
python automation/system_scanner.py --platform all --mode full --output scan.json
```

### 3. `automation/restore_workflows.sh`

Bash script to restore disabled workflow configurations:

```bash
bash automation/restore_workflows.sh
```

## Manual Usage

You can also run the restoration process manually:

### Step 1: Scan the System

```bash
# Scan all platforms
python automation/system_scanner.py --platform all --mode full --output scan_results.json

# Review scan results
cat scan_results.json | jq '.'
```

### Step 2: Generate Restoration Plan

```bash
# Generate plan
python backend/system_restoration.py analyze --output scan_results.json
python backend/system_restoration.py plan \
  --input scan_results.json \
  --output restoration_plan.json \
  --trading=true --freelance=true --bots=true

# Review plan
cat restoration_plan.json | jq '.'
```

### Step 3: Execute Restoration

```bash
# Restore configuration
python backend/system_restoration.py restore-config \
  --plan restoration_plan.json

# Restore bots
python backend/system_restoration.py restore-bots --plan restoration_plan.json

# Restore trading (paper mode)
python backend/system_restoration.py restore-trading \
  --plan restoration_plan.json --mode paper

# Restore freelance operations
python backend/system_restoration.py restore-freelance --plan restoration_plan.json

# Restore platforms
python backend/system_restoration.py restore-platforms --plan restoration_plan.json
```

### Step 4: Validate and Report

```bash
# Validate system
python backend/system_restoration.py validate \
  --plan restoration_plan.json \
  --output validation_results.json

# Verify components
python backend/system_restoration.py verify-bots
python backend/system_restoration.py verify-trading
python backend/system_restoration.py verify-freelance

# Check capacity
python backend/system_restoration.py check-capacity --output capacity_report.json

# Generate report
python backend/system_restoration.py report \
  --validation validation_results.json \
  --capacity capacity_report.json \
  --output RESTORATION_REPORT.md

# View report
cat RESTORATION_REPORT.md
```

## Safety Features

- **Backups**: All configuration changes are backed up before restoration
- **Paper Mode**: Trading operations restored in paper mode by default
- **Validation**: Comprehensive validation before declaring success
- **Manual Review**: Option to review plan before execution
- **Logging**: Detailed logs in `.restoration-logs/` directory
- **Artifacts**: All results saved as workflow artifacts

## System Components

The restoration workflow handles:

1. **Chimera System**: Core autonomous system (chimera_master.py, chimera_base.py)
2. **Trading Operations**: Autonomous trading system
3. **Bot Connections**: Discord bots, trading bots, automation bots
4. **Freelance Engine**: AI-based freelance job system
5. **Platform Integrations**: GitHub, Railway, and other services
6. **Workflows**: GitHub Actions workflows
7. **Configuration Files**: System configuration and environment variables

## Next Steps After Restoration

1. **Monitor System**: Watch logs and performance for 24-48 hours
2. **Review Artifacts**: Download and review scan results and restoration reports
3. **Verify Operations**: Manually test critical operations
4. **Enable Live Trading**: Only after successful paper trading validation
5. **Configure Secrets**: Ensure all required secrets are properly configured
6. **Schedule Regular Scans**: Run restoration workflow periodically to maintain health

## Troubleshooting

### Workflow Fails During Scan
- Check that Python dependencies are installed
- Verify repository structure is intact
- Review `.restoration-logs/` for detailed error messages

### Restoration Tasks Fail
- Review restoration plan for dependency issues
- Check file permissions and directory structure
- Verify all required files exist in repository

### Validation Warnings
- Review specific warnings in validation results
- Address warnings that affect critical operations
- Re-run validation after fixes

### System Not at Full Capacity
- Check capacity report for offline components
- Verify all required files and directories exist
- Re-run specific restoration steps as needed

## Configuration

### Required Secrets

- `GITHUB_TOKEN`: Automatically provided by GitHub Actions
- `RAILWAY_TOKEN`: Required for Railway deployment scanning (optional)

### Environment Variables

All environment variables can be configured in `.env` file or GitHub repository secrets.

## Related Documentation

- [Chimera System Architecture](../SYSTEM_ARCHITECTURE.md)
- [Entry Points Guide](./ENTRY_POINTS.md)
- [Runbook](../RUNBOOK.md)
- [Deployment Guide](../DEPLOYMENT.md)

## Support

For issues or questions:
1. Check workflow run logs in GitHub Actions
2. Review artifacts for detailed reports
3. Check `.restoration-logs/` directory for detailed logs
4. Review this documentation for manual execution steps
