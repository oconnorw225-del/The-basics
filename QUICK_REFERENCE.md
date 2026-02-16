# Quick Reference - PR #140 Enhancements

## 🚀 One-Line Setup

```bash
# Complete system initialization
python3 scripts/complete_init.py
```

That's it! This will:
- Generate `.env` with secure defaults
- Create all bot configuration files
- Set proper file permissions
- Show you what to configure next

---

## 📋 Common Commands

### Setup & Initialization

```bash
# Generate .env file only
python3 scripts/setup_env.py

# Create bot configs only
python3 scripts/init_bot_configs.py

# Inject CI/CD secrets
python3 scripts/inject_secrets.py

# Traditional shell setup
./setup.sh
```

### Validation

```bash
# Validate secrets without writing files
python3 scripts/inject_secrets.py --validate-only

# Check Python syntax
python3 -m py_compile scripts/*.py

# Check JavaScript syntax
node -c bot.js
```

### Force Overwrite

```bash
# Force regenerate .env
python3 scripts/setup_env.py --force

# Force recreate configs
python3 scripts/init_bot_configs.py --force

# Force complete init
python3 scripts/complete_init.py --force
```

---

## 🔧 Configuration Files

### Where Things Live

```
The-basics/
├── .env                                    # Your environment (auto-generated)
├── config/
│   ├── bot-config.json                     # Bot settings (auto-generated)
│   ├── credentials.template.json           # Credential template (auto-generated)
│   ├── credentials.json                    # Your credentials (YOU create this)
│   └── automation-settings.json            # Automation config (auto-generated)
└── scripts/
    ├── setup_env.py                        # Env generator
    ├── init_bot_configs.py                 # Config creator
    ├── complete_init.py                    # Master init
    └── inject_secrets.py                   # Secret injector
```

### What to Edit

**DO edit these:**
- `.env` - Add your API keys
- `config/credentials.json` - Add your platform credentials (copy from template)

**DON'T edit these (they're templates):**
- `.env.example`
- `config/credentials.template.json`

---

## 🔐 Secrets & Security

### Auto-Generated Secrets

These are automatically created with secure random values:
- `SECRET_KEY` (64 characters)
- `JWT_SECRET` (32 characters)
- `SESSION_SECRET` (32 characters)
- `ENCRYPTION_KEY` (64 characters)

### Manual Configuration Needed

Add these to `.env` yourself:
- `NDAX_API_KEY`
- `NDAX_API_SECRET`
- `STRIPE_API_KEY`
- `STRIPE_SECRET_KEY`
- Platform-specific tokens

### File Permissions

Scripts automatically set:
- `.env` → 600 (owner read/write only)
- `credentials.json` → 600
- Secrets directory → 700

---

## 🤖 Bot Features

### New Endpoint: Bot Sync

```http
POST http://localhost:9000/api/bot/sync
Content-Type: application/json

{
  "bot_id": "my-bot-instance",
  "timestamp": 1708122000000,
  "status": {
    "trading": true,
    "freelance": true,
    "ai": true,
    "uptime": 3600000
  }
}
```

### Discovery Ports

Bots discover each other on these ports:
- 9000 (main bot)
- 9001 (instance 1)
- 9002 (instance 2)
- 9003 (instance 3)

Configure in `config/bot-config.json`

---

## 🌐 CI/CD Integration

### GitHub Actions

```yaml
- name: Setup Environment
  run: python3 scripts/inject_secrets.py
  env:
    SECRET_KEY: ${{ secrets.SECRET_KEY }}
    JWT_SECRET: ${{ secrets.JWT_SECRET }}
    NDAX_API_KEY: ${{ secrets.NDAX_API_KEY }}
```

### Railway

```bash
# Railway auto-injects environment variables
railway run python3 scripts/inject_secrets.py
```

### Environment Variables to Set

In your CI/CD platform, set:
- `SECRET_KEY` (required)
- `JWT_SECRET` (required)
- `NDAX_API_KEY` (optional)
- `NDAX_API_SECRET` (optional)
- `DATABASE_URL` (optional)
- `REDIS_URL` (optional)

---

## 🎯 Quick Troubleshooting

### Problem: .env not created

**Solution:**
```bash
# Force regenerate
python3 scripts/setup_env.py --force
```

### Problem: Missing permissions

**Solution:**
```bash
chmod +x scripts/*.py
chmod +x *.sh
```

### Problem: Config files not created

**Solution:**
```bash
# Recreate all configs
python3 scripts/init_bot_configs.py --force
```

### Problem: Secrets not injected in CI/CD

**Solution:**
```bash
# Validate what's available
python3 scripts/inject_secrets.py --validate-only

# Check GitHub secrets in repo settings
# Check Railway env vars in dashboard
```

---

## 📖 Full Documentation

- `scripts/README.md` - Script usage guide
- `freelance_engine/README.md` - Platform integration
- `PR_140_ENHANCEMENT_COMPLETE.md` - Full feature list
- `VALIDATION_REPORT_PR140.md` - Validation details
- `TASK_COMPLETE.md` - Executive summary

---

## 🆘 Need Help?

1. Check if `.env.example` exists
2. Verify Python 3.7+ installed: `python3 --version`
3. Check Node.js 16+ installed: `node --version`
4. Review script output for errors
5. Check file permissions: `ls -la .env`

---

## ✅ Checklist for First Time Setup

- [ ] Clone repository
- [ ] Run `python3 scripts/complete_init.py`
- [ ] Review `.env` file
- [ ] Add your API keys to `.env`
- [ ] Copy `config/credentials.template.json` to `config/credentials.json`
- [ ] Add your credentials to `config/credentials.json`
- [ ] Run `npm install`
- [ ] Start with `npm run fia` or `node bot.js`
- [ ] Verify bot starts successfully
- [ ] Check `/status` endpoint works

---

**Last Updated:** 2026-02-16  
**Version:** 1.0 (PR #140 Enhancement)
