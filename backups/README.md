# Backups Directory

This directory stores archived versions of source repositories and system backups.

## Structure

```
backups/
├── ndax-quantum-engine.tar.gz      # NDAX trading engine backup
├── quantum-engine-dashb.tar.gz     # Dashboard backup
├── shadowforge-ai-trader.tar.gz    # ShadowForge AI backup
├── repository-web-app.tar.gz       # Web app backup
├── The-new-ones.tar.gz             # Additional components backup
└── pre-deploy/                     # Pre-deployment backups
    └── backup-YYYYMMDD-HHMMSS.tar.gz
```

## Automatic Backups

The consolidation workflow (`/.github/workflows/consolidate.yml`) automatically creates backups when consolidating source repositories.

Pre-deployment backups are created by the auto-fix-and-deploy workflow before any deployment.

## Manual Backup

To create a manual backup:

```bash
# Backup entire system
tar -czf backups/manual-backup-$(date +%Y%m%d-%H%M%S).tar.gz \
  --exclude=backups \
  --exclude=.git \
  --exclude=node_modules \
  --exclude=venv \
  .

# Backup configuration only
tar -czf backups/config-backup-$(date +%Y%m%d-%H%M%S).tar.gz config/
```

## Restore from Backup

To restore from a backup:

```bash
# List available backups
ls -lth backups/*.tar.gz

# Extract to temporary location first
mkdir -p /tmp/restore
tar -xzf backups/backup-YYYYMMDD-HHMMSS.tar.gz -C /tmp/restore

# Review contents
ls -la /tmp/restore

# Copy specific files back
cp /tmp/restore/config/*.json config/
```

## Retention Policy

- Keep last 7 daily backups
- Keep last 4 weekly backups (end of week)
- Keep monthly backups for 6 months
- Archive older backups or delete as needed

## Automated Cleanup

Add to crontab for automatic cleanup of old backups:

```bash
# Clean backups older than 30 days (except monthly)
find backups/ -name "backup-*.tar.gz" -mtime +30 -delete
```

## Security Notes

⚠️ **Important**:
- Backups may contain sensitive information
- Keep backups secure and encrypted if possible
- Do not commit backups to git
- Store critical backups off-site
- Regularly test backup restoration

## .gitignore

Backups are excluded from git by default:

```
backups/*.tar.gz
backups/pre-deploy/*.tar.gz
```

Only the directory structure (.gitkeep) is tracked in version control.
