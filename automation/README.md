# Automation System Documentation

## Overview

The `automation/` directory contains scripts for intelligent repository consolidation, security auditing, and maintenance of the unified codebase.

## Main Scripts

### consolidate.sh

**Purpose**: Consolidates 5 source repositories into the unified `the-basics` codebase.

**What it does**:

1. Clones all source repositories into `source/` directory
2. Creates timestamped tar.gz backups in `backups/`
3. Intelligently copies files to appropriate destinations
4. Generates consolidation report

**Usage**:

```bash
bash automation/consolidate.sh
```

**Source Repository Mapping**:

| Source Repository       | Destination                              | Content                         |
| ----------------------- | ---------------------------------------- | ------------------------------- |
| `ndax-quantum-engine`   | `api/ndax/`                              | Trading API, bot.js             |
| `quantum-engine-dashb`  | `frontend/dashboard/`                    | React/TypeScript dashboard      |
| `shadowforge-ai-trader` | `backend/`, `backend/chimera/`           | AI trading system, Chimera core |
| `repository-web-app`    | `frontend/web-app/`, `backend/api/`      | Full-stack web application      |
| `The-new-ones`          | `config/recovered/`, `scripts/recovery/` | Recovery configurations         |

### audit.py

**Purpose**: Security audit and sensitive data detection.

**Features**:

- Scans for API keys, private keys, secrets
- Detects cryptocurrency wallet addresses
- Identifies code quality issues
- Generates `audit_report.json`

**Usage**:

```bash
python3 automation/audit.py
```

### repo_analyzer.py

**Purpose**: Analyzes repository structure and dependencies.

**Features**:

- Detects frameworks and languages
- Maps directory structure
- Identifies dependencies
- Generates `analysis.json`

**Usage**:

```bash
python3 automation/repo_analyzer.py
```

### check-btc-balance.sh

**Purpose**: Read-only Bitcoin balance checker for multiple addresses.

**Features**:

- Queries public blockchain explorer APIs (Blockstream, Blockchain.info, Blockchair)
- Checks balances for multiple Bitcoin addresses from a file
- Generates timestamped JSON reports
- Displays human-readable summary
- **Read-only**: Does NOT require or accept private keys, seeds, or credentials
- Safe for security auditing and compliance checking

**Usage**:

```bash
./automation/check-btc-balance.sh addresses.txt
```

Where `addresses.txt` contains one Bitcoin address per line.

**Example addresses.txt**:
```
1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh
```

**Output**:
- JSON report saved to `reports/btc_balances/balances_<timestamp>.json`
- Human-readable summary printed to console

**Dependencies**:
- `curl` (for API requests)
- `jq` (JSON processor)

**Security Note**: This script only performs read-only queries to public APIs. It never requests, stores, or transmits private keys or sensitive credentials.

### consolidate_repos.sh

**Purpose**: Legacy consolidation script with enhanced features.

**Features**:

- Colored output and progress indicators
- Backup creation
- Error handling
- Detailed logging

### smart_consolidate.sh

**Purpose**: Interactive consolidation with user prompts.

**Features**:

- Interactive mode for selective consolidation
- Conflict detection and resolution
- Rollback capability

## Consolidation Process

### Step-by-Step Workflow

1. **Initialization**
   - Creates directory structure
   - Sets up logging
   - Validates prerequisites

2. **Repository Cloning**
   - Clones all 5 source repositories
   - Pulls latest changes if already cloned
   - Validates successful cloning

3. **Backup Creation**
   - Creates timestamped tar.gz archives
   - Stores in `backups/` directory
   - Logs backup sizes

4. **File Consolidation**
   - Copies files using intelligent conflict resolution
   - Preserves timestamps and permissions
   - Uses rsync when available, falls back to cp

5. **Report Generation**
   - Creates `CONSOLIDATION_REPORT.md`
   - Logs all operations
   - Provides next steps

## Conflict Resolution Strategy

The consolidation system uses the **"newer wins"** strategy:

- When files exist in both source and destination
- Compares modification timestamps
- Keeps the newer file
- Logs all conflicts for review

**Implementation**:

- Primary: `rsync -av --update` (preserves newer files)
- Fallback: `cp -ru` (update mode)

## Adding New Source Repositories

To add a new source repository to consolidation:

1. **Update config file**: `config/consolidation-config.json`

```json
{
  "name": "new-repo-name",
  "owner": "oconnorw225-del",
  "url": "https://github.com/oconnorw225-del/new-repo-name.git",
  "paths": {
    "src": "destination/path/"
  }
}
```

2. **Update consolidate.sh**: Add new consolidation function

```bash
consolidate_new_repo() {
    log_step "Consolidating new-repo-name..."
    local repo_path="${SOURCE_DIR}/new-repo-name"

    if [ ! -d "$repo_path" ]; then
        log_warning "Repository new-repo-name not found"
        return
    fi

    # Copy logic here
    copy_with_conflict_resolution "$repo_path/src/" "${REPO_ROOT}/destination/" "Description"

    log_success "new-repo-name consolidated"
}
```

3. **Call function in main()**: Add to consolidation sequence

4. **Update GitHub Actions workflow**: Add to repository list in `.github/workflows/consolidate.yml`

## Directory Structure After Consolidation

```
the-basics/
├── api/                    # API endpoints from all sources
│   ├── ndax/              # NDAX trading API
│   └── ...
├── backend/               # Backend logic and strategies
│   ├── api/               # Web app API
│   ├── chimera/           # Chimera intelligence core
│   ├── shadowforge/       # AI trading system
│   ├── strategy/          # Trading strategies
│   ├── bot.js             # NDAX bot
│   └── unified_system.py  # Unified system
├── frontend/              # Frontend applications
│   ├── dashboard/         # Trading dashboard
│   └── web-app/           # Repository web app
├── docs/                  # Documentation from all sources
│   ├── ndax/
│   ├── dashboard/
│   ├── shadowforge/
│   ├── web-app/
│   └── recovery/
├── tests/                 # Combined test suites
│   ├── ndax/
│   └── shadowforge/
├── config/                # Configuration files
│   ├── recovered/         # Recovery configurations
│   └── ...
├── scripts/               # Utility scripts
│   └── recovery/          # Recovery scripts
├── backups/               # Timestamped backups
│   └── *.tar.gz
└── source/                # Cloned source repositories (temporary)
```

## Backup Management

### Backup Location

All backups are stored in `backups/` directory with timestamp format:

```
backups/
├── ndax-quantum-engine_20260103_120000.tar.gz
├── quantum-engine-dashb_20260103_120000.tar.gz
├── shadowforge-ai-trader_20260103_120000.tar.gz
├── repository-web-app_20260103_120000.tar.gz
└── The-new-ones_20260103_120000.tar.gz
```

### Restoring from Backup

To restore a specific repository from backup:

```bash
# Extract backup
tar -xzf backups/ndax-quantum-engine_20260103_120000.tar.gz -C /tmp/

# Review contents
ls -la /tmp/ndax-quantum-engine/

# Manually copy needed files back
cp -r /tmp/ndax-quantum-engine/src/* api/ndax/
```

### Backup Retention

- Backups are kept for 90 days in GitHub Actions artifacts
- Local backups should be cleaned up manually
- Consider moving old backups to external storage

## Troubleshooting

### Issue: Repository clone fails

**Solution**:

```bash
# Check network connectivity
ping github.com

# Try manual clone
git clone https://github.com/oconnorw225-del/ndax-quantum-engine.git

# Check if repository is private (requires authentication)
```

### Issue: rsync not available

**Solution**: Script automatically falls back to `cp -ru`. To install rsync:

```bash
# Ubuntu/Debian
sudo apt-get install rsync

# macOS
brew install rsync
```

### Issue: Permission denied during copy

**Solution**:

```bash
# Make script executable
chmod +x automation/consolidate.sh

# Check file permissions
ls -la automation/

# Run with appropriate permissions
```

### Issue: Out of disk space

**Solution**:

```bash
# Check disk space
df -h

# Clean up old backups
rm backups/*_old_timestamp.tar.gz

# Clean up source directory
rm -rf source/
```

## Best Practices

1. **Always review logs**: Check `consolidation_*.log` after each run

2. **Test before production**: Run consolidation in a test environment first

3. **Keep backups**: Don't delete backups immediately after consolidation

4. **Monitor conflicts**: Review files where timestamps indicate conflicts

5. **Regular consolidation**: Run consolidation weekly to keep codebase updated

6. **Version control**: Always commit changes after reviewing consolidation results

7. **Security first**: Run `audit.py` after consolidation to check for exposed secrets

## Automation via GitHub Actions

The consolidation can be triggered automatically via GitHub Actions:

1. Go to repository **Actions** tab
2. Select **"Repository Consolidation & Security Audit"**
3. Click **"Run workflow"**
4. Wait for completion
5. Download artifacts to review backups and reports

See `.github/workflows/consolidate.yml` for workflow configuration.

## Maintenance

### Weekly Tasks

- Run consolidation to pull latest changes
- Review audit reports
- Clean up old backups

### Monthly Tasks

- Update source repository list if needed
- Review and optimize consolidation mappings
- Update documentation

### Quarterly Tasks

- Full security audit
- Review and update conflict resolution strategy
- Optimize directory structure

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review consolidation logs
3. Consult main README.md
4. Check individual source repository documentation

---

_Last updated: 2026-01-03_  
_Powered by Project Chimera V8.0_
