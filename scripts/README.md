# Scripts Directory

This directory contains automation scripts for environment setup, configuration, and deployment.

## Quick Reference

### Setup & Initialization

```bash
# Complete system initialization (recommended)
python3 scripts/complete_init.py

# Or run individual scripts:
python3 scripts/setup_env.py          # Generate .env from .env.example
python3 scripts/init_bot_configs.py   # Create bot configuration files
python3 scripts/inject_secrets.py     # Inject CI/CD secrets (for deployment)
```

### Shell Scripts

```bash
./setup.sh                 # Full environment setup (calls Python scripts)
./setup_infrastructure.sh  # Infrastructure setup
./auto_install.sh          # Automatic installation
```

## Script Descriptions

### Python Scripts

#### `setup_env.py`
**Purpose:** Auto-generates `.env` file from `.env.example` with intelligent defaults

**Features:**
- Auto-generates secure secrets (SECRET_KEY, JWT_SECRET, etc.)
- Sets sensible defaults for ports, URLs, database connections
- Identifies API keys that need manual configuration
- Sets secure file permissions (600)

**Usage:**
```bash
python3 scripts/setup_env.py          # Generate .env
python3 scripts/setup_env.py --force  # Force overwrite
```

---

#### `init_bot_configs.py`
**Purpose:** Creates comprehensive bot configuration files

**Usage:**
```bash
python3 scripts/init_bot_configs.py         # Create configs
python3 scripts/init_bot_configs.py --force # Overwrite existing
```

**Output:**
- `config/bot-config.json` - Bot operational settings
- `config/credentials.template.json` - Credential structure
- `config/automation-settings.json` - Automation rules

---

#### `inject_secrets.py`
**Purpose:** Injects secrets from CI/CD environment into config files

**Usage:**
```bash
python3 scripts/inject_secrets.py                    # Auto-detect & inject
python3 scripts/inject_secrets.py --validate-only    # Validate only
```

---

#### `complete_init.py`
**Purpose:** Master initialization script that runs everything

**Usage:**
```bash
python3 scripts/complete_init.py         # Full initialization
python3 scripts/complete_init.py --force # Force overwrite all
```

---

### Shell Scripts

#### `setup.sh`
Main setup script for development environment

#### `setup_wallet_system.sh`
Sets up wallet management system

#### `common.sh`
Shared utility functions for shell scripts

---

## Development Workflow

### First Time Setup

```bash
# 1. Run complete initialization
python3 scripts/complete_init.py

# 2. Review and customize
nano .env                        # Add your API keys
nano config/credentials.json     # Add platform credentials

# 3. Start the system
npm run fia                      # Full system startup
```

### CI/CD Pipeline

```yaml
# Example GitHub Actions workflow
- name: Setup Environment
  run: |
    python3 scripts/inject_secrets.py
  env:
    SECRET_KEY: ${{ secrets.SECRET_KEY }}
    JWT_SECRET: ${{ secrets.JWT_SECRET }}
```

---

## Security Best Practices

### ✅ DO:
- Use `setup_env.py` to auto-generate secrets
- Keep `.env` and `credentials.json` in `.gitignore`
- Use environment variables in CI/CD
- Set secure file permissions (600 for secrets)

### ❌ DON'T:
- Commit `.env` or `credentials.json` to git
- Share secrets in plain text
- Use weak or predictable secrets

---

## Support

For issues with scripts, check file permissions and ensure Python 3.7+ and Node.js 16+ are installed.
