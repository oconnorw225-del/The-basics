# Entry Point Documentation

This document explains the different entry points in this repository and when to use each one.

## Overview

The repository has two main Python entry points with different purposes:

### 1. `start_system.py` - Production System Orchestrator

**Purpose**: Lightweight production orchestrator for starting and monitoring system components.

**When to use**:
- Production deployments
- When you need full monitoring and health checks
- When running with existing `src/` components
- When you need graceful shutdown and crash recovery

**Features**:
- Component orchestration (logger, config, error handler, health monitor, etc.)
- Process management for backend and Node.js services
- Health monitoring with configurable intervals
- Crash detection and recovery
- API gateway integration
- Graceful shutdown with signal handling

**Usage**:
```bash
python3 start_system.py
```

**Requirements**:
- Components in `src/` directory must be available
- Configuration in `.env` file
- Node.js installed for frontend/backend services

---

### 2. `unified_system.py` - Autonomous Configuration System

**Purpose**: Comprehensive autonomous system with auto-configuration, security hardening, and deployment automation.

**When to use**:
- First-time setup and configuration
- When you need auto-configuration of APIs and wallets
- When deploying to cloud servers
- When you need security-hardened file operations
- For Chimera Auto-Pilot integration

**Features**:
- Auto-configuration of missing APIs, wallets, and inputs
- Security-hardened file operations
- Cloud server deployment automation
- Treasury management and trading configuration
- Dashboard setup
- Railway/cloud deployment integration
- Kill switch and safety controls
- Evolution engine management

**Usage**:
```bash
python3 unified_system.py
```

**Requirements**:
- Can run standalone with auto-configuration
- Optional: `security/safe_file_ops.py` for hardened operations
- Optional: Cloud server credentials for deployment

---

## Comparison

| Feature | start_system.py | unified_system.py |
|---------|----------------|-------------------|
| **Lines of Code** | ~416 | ~881 |
| **Purpose** | Production orchestrator | Autonomous configuration |
| **Dependencies** | Requires src/ components | Can auto-configure |
| **Security** | Standard | Hardened file ops |
| **Configuration** | Manual via .env | Auto-generates missing |
| **Deployment** | Local only | Cloud deployment support |
| **Monitoring** | Yes (health checks) | Basic |
| **Auto-setup** | No | Yes |
| **Trading** | Via components | Built-in management |
| **Best for** | Production runtime | Initial setup & automation |

## Which One Should I Use?

### Use `start_system.py` if:
- ✅ You have already configured the system
- ✅ You need robust monitoring and health checks
- ✅ You're running in production
- ✅ You want component-based architecture
- ✅ You need crash recovery

### Use `unified_system.py` if:
- ✅ You're setting up for the first time
- ✅ You need auto-configuration
- ✅ You're deploying to cloud servers
- ✅ You want integrated trading management
- ✅ You need security-hardened operations
- ✅ You're using Chimera Auto-Pilot features

## Running Both Together

These systems can complement each other:

1. **First run**: Use `unified_system.py` to auto-configure everything
2. **Production**: Use `start_system.py` for day-to-day operations

```bash
# Setup phase
python3 unified_system.py  # Auto-configures system

# Production phase
python3 start_system.py    # Runs with monitoring
```

## Shell Script Entry Points

In addition to Python entry points, there are shell script entry points:

### `setup.sh`
- Initial project setup
- Installs Node.js dependencies
- Creates directory structure
- Generates .env file
- One-time setup script

### `start.sh`
- Quick start for development
- Starts Python backend + Node.js server + Vite frontend
- Uses common.sh utilities for logging
- Good for local development

### `auto_install.sh`
- Complete automated installation
- Installs system dependencies (PostgreSQL, MongoDB, Redis)
- Creates systemd services
- Production deployment setup
- Requires root/sudo access

## Recommendations

1. **For new users**: Start with `./setup.sh`, then use `unified_system.py` for configuration
2. **For developers**: Use `./start.sh` for quick local development
3. **For production**: Use `python3 start_system.py` with proper monitoring
4. **For deployment**: Use `auto_install.sh` on fresh server, then `start_system.py`

## Notes

- All shell scripts now use shared utilities from `scripts/common.sh` for consistent logging
- Both Python entry points can coexist - they serve different purposes
- Choose based on your use case and stage of deployment
