# 🔐 Environment Auto-Populator

Automatically generates secure environment configurations with pre-loaded settings.

## Features

✅ **Cryptographically Secure Secrets**
- Generates 64-character JWT secrets
- Generates 32-character session secrets
- Uses Python's `secrets` module for cryptographic strength

✅ **Smart Defaults**
- Database connection strings (dev/prod)
- Security settings (HTTPS, authentication, rate limiting)
- Bot configuration
- Trading parameters

✅ **API Key Detection**
- Scans templates for required API keys
- Marks them as placeholders with clear warnings
- Lists all keys that need manual configuration

✅ **Multiple Environments**
- Development (.env)
- Production (.env.production)
- Supports both in one run

## Quick Start

### Interactive Mode

```bash
# Run the setup wizard
./scripts/setup_env.sh
```

This will:
1. Ask which environment(s) to configure
2. Generate secure secrets automatically
3. Create .env and/or .env.production files
4. List API keys that need your attention

### Automatic Mode

```bash
# Generate both dev and production configs
./scripts/setup_env.sh --auto

# Or use Python directly
python3 scripts/setup_env.py --auto
```

### Integrated with Main Setup

The environment auto-populator is integrated into the main setup script:

```bash
# Run the main setup (includes auto-population)
./scripts/setup.sh
```

## What Gets Generated

### Development Environment (.env)

```bash
# Auto-generated header with metadata
JWT_SECRET=<64-char hex token>
DATABASE_URL=postgresql://user:pass@localhost:5432/ndax_dev
# ... all other settings with defaults
```

### Production Environment (.env.production)

```bash
# Auto-generated header with metadata
JWT_SECRET=<64-char hex token>
SESSION_SECRET=<32-char hex token>
DATABASE_URL=postgresql://username:password@localhost:5432/ndax_prod
FORCE_HTTPS=true
ENABLE_AUTH=true
# ... all other production settings
```

## Generated Secrets

### JWT Secret (64 chars)
- Used for JSON Web Token signing
- Cryptographically secure random hex
- Example: `a1b2c3d4...` (128 hex digits)

### Session Secret (32 chars)
- Used for session encryption
- Cryptographically secure random hex
- Example: `x1y2z3...` (64 hex digits)

### Database URLs
- **Development**: `postgresql://user:pass@localhost:5432/ndax_dev`
- **Production**: `postgresql://username:password@localhost:5432/ndax_prod`

## API Keys to Fill In

After generation, you'll need to manually add these API keys:

### Required for Trading
- `NDAX_API_KEY` - Your NDAX exchange API key
- `NDAX_API_SECRET` - Your NDAX exchange API secret
- `NDAX_USER_ID` - Your NDAX user ID

### Optional Services
- `SENDGRID_API_KEY` - For email notifications
- `OPENAI_API_KEY` - For AI features
- `ANTHROPIC_API_KEY` - For Claude AI features

## Security Features

✅ **File Permissions**
- Generated files have `600` permissions (owner read/write only)
- Prevents unauthorized access

✅ **Git Protection**
- .env and .env.production are in .gitignore
- Secrets never committed to version control

✅ **Clear Warnings**
- Header comments explain what was auto-generated
- Lists all API keys that need manual configuration
- Security reminders in output

## GitHub Actions Integration

You can also generate environment configurations via GitHub Actions:

1. Go to **Actions** → **Preload Environment Configuration**
2. Click **Run workflow**
3. Select environment (dev/prod/both)
4. Generated files available as artifacts

## Advanced Usage

### Regenerate Secrets

To generate new secrets (e.g., after a security incident):

```bash
# This will overwrite existing files (asks for confirmation)
./scripts/setup_env.sh
```

### Custom Environment

You can modify the Python script to add your own environment logic:

```python
# scripts/setup_env.py
def generate_custom_setting(self):
    # Your custom logic here
    pass
```

## Verification

Check that secrets were properly generated:

```bash
# Check JWT secret is present and strong
grep "^JWT_SECRET=" .env | wc -c  # Should be ~140 chars

# Check database URL is configured
grep "^DATABASE_URL=" .env

# List all API keys that need filling
grep "PLACEHOLDER" .env
```

## Troubleshooting

### "Python3 not found"
Install Python 3.11+:
```bash
# Ubuntu/Debian
sudo apt-get install python3

# macOS
brew install python3
```

### "Permission denied"
Make scripts executable:
```bash
chmod +x scripts/setup_env.sh
chmod +x scripts/setup_env.py
```

### "File already exists"
The script will ask for confirmation before overwriting. To force regeneration:
```bash
rm .env .env.production
./scripts/setup_env.sh --auto
```

## Best Practices

1. **Never commit .env files** - They're in .gitignore for a reason
2. **Regenerate secrets regularly** - Especially after team changes
3. **Use different secrets per environment** - Don't copy prod secrets to dev
4. **Store prod secrets securely** - Use a password manager or secrets vault
5. **Review generated files** - Make sure all settings match your needs

## Integration with Other Tools

### Docker
```bash
# Generate .env before building
./scripts/setup_env.sh --auto
docker-compose up
```

### CI/CD
```bash
# In your CI pipeline
python3 scripts/setup_env.py --auto
# Then run tests with generated config
npm test
```

### Kubernetes
```bash
# Generate and create k8s secret
./scripts/setup_env.sh --prod
kubectl create secret generic app-secrets --from-env-file=.env.production
```

## What's Next

After generating your environment:

1. ✅ Review .env file
2. ✅ Fill in API keys
3. ✅ Test database connection
4. ✅ Start the application:
   ```bash
   npm start  # or
   python backend/bot-coordinator.py
   ```

## Support

If you encounter issues:
1. Check the script output for specific error messages
2. Verify Python 3.11+ is installed
3. Ensure you have write permissions in the directory
4. Review the generated file headers for hints

---

**Security Note**: The auto-generated secrets are cryptographically secure and suitable for production use. However, always review security settings and adjust for your specific deployment requirements.
