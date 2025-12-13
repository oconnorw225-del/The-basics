# Credential Management Guide

## Overview

The credential management system provides secure storage, validation, and rotation of API keys, secrets, and credentials for The-basics system.

## Features

- **Centralized Storage**: All credentials in one place
- **Encryption**: AES-256-GCM encryption for sensitive data
- **Validation**: Format validation for common credential types
- **Rotation**: Automatic credential rotation support
- **Environment Management**: Multiple environment support (dev, staging, prod)

## Credential Manager

### Initialization

```javascript
const { CredentialManager } = require('./src/security/credential-manager');

const credentialManager = CredentialManager.getInstance({
  envPath: '.env',
  encryptionKey: process.env.ENCRYPTION_KEY,
  validateOnLoad: true,
  autoRotate: false,
  rotationInterval: 30 * 24 * 60 * 60 * 1000  // 30 days
});
```

### Basic Usage

```javascript
// Get a credential
const apiKey = credentialManager.get('NDAX_API_KEY');

// Set a credential
credentialManager.set('NDAX_API_KEY', 'your-api-key-here', {
  persist: true  // Save to .env file
});

// Check if credential exists
const hasKey = credentialManager.get('OPENAI_API_KEY') !== null;

// Get with default value
const port = credentialManager.get('PORT', '3000');
```

### Validation

```javascript
// Validate a specific credential
const isValid = credentialManager.validate('WALLET_ADDRESS');

// Validate all credentials
const results = credentialManager.validateAll();
console.log('Valid:', results.valid);
console.log('Invalid:', results.invalid);
console.log('Missing:', results.missing);
console.log('Details:', results.details);

// Example output:
// {
//   total: 10,
//   valid: 7,
//   invalid: 1,
//   missing: 2,
//   details: [
//     { key: 'NDAX_API_KEY', status: 'valid' },
//     { key: 'WALLET_ADDRESS', status: 'invalid' },
//     { key: 'OPENAI_API_KEY', status: 'missing' }
//   ]
// }
```

### Encryption

```javascript
// Credentials are automatically encrypted when saved
credentialManager.set('PRIVATE_KEY', '0x1234...', { persist: true });

// The .env file will contain encrypted value:
// PRIVATE_KEY=a1b2c3d4:e5f6g7h8:encrypted_data

// Decryption happens automatically when loading
const privateKey = credentialManager.get('PRIVATE_KEY');
// Returns decrypted value: 0x1234...

// Save with encryption
credentialManager.save(true);  // encrypt=true
```

### Credential Rotation

```javascript
// Rotate a credential (generates new value)
const newSecret = credentialManager.rotate('JWT_SECRET');

// Rotate with custom generator
credentialManager.rotate('API_KEY', () => {
  return generateCustomApiKey();
});

// Check rotation status
const needsRotation = credentialManager.getRotationStatus();
needsRotation.forEach(item => {
  console.log(`${item.key} needs rotation (age: ${item.age})`);
});

// Example output:
// [
//   {
//     key: 'JWT_SECRET',
//     lastRotated: '2024-01-01T00:00:00Z',
//     age: '45 days'
//   }
// ]
```

### Statistics and Monitoring

```javascript
// Get credential statistics
const stats = credentialManager.getStats();
console.log('Total credentials:', stats.total);
console.log('Validated:', stats.validated);
console.log('Validation results:', stats.validationResults);
console.log('Rotation status:', stats.rotationStatus);

// Check required credentials
const required = ['NDAX_API_KEY', 'NDAX_API_SECRET', 'JWT_SECRET'];
const check = credentialManager.checkRequired(required);

if (!check.complete) {
  console.error('Missing credentials:', check.missing);
}
```

### Events

```javascript
// Listen to credential events
credentialManager.on('credentialSet', ({ key, timestamp }) => {
  console.log(`Credential set: ${key} at ${timestamp}`);
});

credentialManager.on('validationFailed', ({ key, timestamp }) => {
  console.error(`Validation failed for ${key}`);
});

credentialManager.on('rotated', ({ key, timestamp }) => {
  console.log(`Credential rotated: ${key}`);
});

credentialManager.on('saved', ({ timestamp }) => {
  console.log(`Credentials saved at ${timestamp}`);
});

credentialManager.on('error', ({ type, error }) => {
  console.error(`Error (${type}):`, error);
});
```

## Credential Types and Validation

### Trading APIs

```javascript
// NDAX
NDAX_API_KEY=your_api_key_here          // Must be >= 32 characters
NDAX_API_SECRET=your_api_secret_here    // Must be >= 32 characters
NDAX_USER_ID=12345
```

### AI Platform APIs

```javascript
// HuggingFace
HUGGINGFACE_API_KEY=hf_xxxxx           // Must start with 'hf_'

// OpenAI
OPENAI_API_KEY=sk-xxxxx                // Must start with 'sk-'

// Amazon MTurk
MTURK_ACCESS_KEY=AKIAxxxxx             // AWS access key format
MTURK_SECRET_KEY=xxxxx                 // 40 characters

// Appen
APPEN_API_KEY=your_api_key

// RapidAPI
RAPIDAPI_KEY=your_api_key
```

### Blockchain/Wallet

```javascript
// Ethereum wallet address
WALLET_ADDRESS=0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
// Must be 0x followed by 40 hex characters

// Private key
PRIVATE_KEY=0x1234567890abcdef...
// Must be 0x followed by 64 hex characters (or 64 hex without 0x)

// Seed phrase
WALLET_SEED_PHRASE=word1 word2 word3...
// 12 or 24 words
```

### AWS Credentials

```javascript
// AWS Access Key
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
// Must match pattern: AKIA[A-Z0-9]{16}

// AWS Secret Access Key
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
// Must be exactly 40 characters
```

### Payment Processing

```javascript
// Stripe
STRIPE_SECRET_KEY=sk_test_xxxxx        // Must start with sk_test_ or sk_live_
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
```

### Security Keys

```javascript
// JWT Secret
JWT_SECRET=your_secure_random_string_here
// Must be at least 32 characters

// Encryption Key
ENCRYPTION_KEY=64_character_hex_string_here
// Must be exactly 64 hex characters (32 bytes)
```

## .env File Structure

### Complete Example

```bash
# The-basics System Credentials
# Auto-generated - Do not edit manually

# Node.js
NODE_ENV=development
PORT=3000

# Python
PYTHON_PORT=8000

# Trading
TRADING_MODE=paper
AUTO_START=false
MAX_TRADES=5
RISK_LEVEL=low
NDAX_API_KEY=your_key_here
NDAX_API_SECRET=your_secret_here
NDAX_USER_ID=12345

# AI Platforms
HUGGINGFACE_API_KEY=hf_your_token
OPENAI_API_KEY=sk_your_key
MTURK_ACCESS_KEY=AKIAXXXXXX
MTURK_SECRET_KEY=your_secret
APPEN_API_KEY=your_key
RAPIDAPI_KEY=your_key

# Freelance
UPWORK_CLIENT_ID=your_id
UPWORK_CLIENT_SECRET=your_secret
FIVERR_API_KEY=your_key
FREELANCER_API_KEY=your_key

# Blockchain
WALLET_ADDRESS=0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
PRIVATE_KEY=0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef
WALLET_SEED_PHRASE=word1 word2 word3 word4 word5 word6 word7 word8 word9 word10 word11 word12

# AWS
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1

# Payments
STRIPE_SECRET_KEY=sk_test_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx

# Security
ENCRYPTION_KEY=0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
JWT_SECRET=your_secure_random_string_at_least_32_characters_long
```

## Security Best Practices

### 1. Never Commit Credentials

```bash
# Always add .env to .gitignore
echo ".env" >> .gitignore

# Use .env.example as a template
cp .env.example .env
# Then fill in actual values
```

### 2. Use Environment-Specific Files

```bash
# Development
.env.development

# Staging
.env.staging

# Production
.env.production

# Load based on NODE_ENV
const envFile = `.env.${process.env.NODE_ENV || 'development'}`;
```

### 3. Encrypt Sensitive Credentials

```javascript
// Generate encryption key
const crypto = require('crypto');
const key = crypto.randomBytes(32).toString('hex');
console.log('ENCRYPTION_KEY=' + key);

// Set in .env
ENCRYPTION_KEY=your_generated_key

// Use encryption when saving
credentialManager.save(true);
```

### 4. Rotate Credentials Regularly

```javascript
// Enable auto-rotation
const cm = CredentialManager.getInstance({
  autoRotate: true,
  rotationInterval: 30 * 24 * 60 * 60 * 1000  // 30 days
});

// Or manually rotate
setInterval(() => {
  const needsRotation = cm.getRotationStatus();
  needsRotation.forEach(item => {
    if (item.key.includes('SECRET') || item.key.includes('KEY')) {
      cm.rotate(item.key);
      console.log(`Rotated ${item.key}`);
    }
  });
}, 7 * 24 * 60 * 60 * 1000);  // Check weekly
```

### 5. Validate Before Use

```javascript
// Always validate before using credentials
function getApiKey(keyName) {
  const key = credentialManager.get(keyName);
  
  if (!key) {
    throw new Error(`Missing credential: ${keyName}`);
  }
  
  if (!credentialManager.validate(keyName)) {
    throw new Error(`Invalid credential format: ${keyName}`);
  }
  
  return key;
}
```

### 6. Use Secrets Managers in Production

For production deployments, consider using:

- **AWS Secrets Manager**
- **HashiCorp Vault**
- **Azure Key Vault**
- **Google Cloud Secret Manager**

```javascript
// Example: AWS Secrets Manager integration
const AWS = require('aws-sdk');
const secretsManager = new AWS.SecretsManager({ region: 'us-east-1' });

async function loadFromSecretsManager() {
  const secret = await secretsManager.getSecretValue({
    SecretId: 'the-basics/production'
  }).promise();
  
  const credentials = JSON.parse(secret.SecretString);
  
  for (const [key, value] of Object.entries(credentials)) {
    credentialManager.set(key, value, { persist: false });
  }
}
```

## Credential Setup Script

Automate credential setup:

```bash
#!/bin/bash
# setup-credentials.sh

# Generate encryption key
ENCRYPTION_KEY=$(openssl rand -hex 32)

# Generate JWT secret
JWT_SECRET=$(openssl rand -hex 32)

# Create .env from template
cp .env.example .env

# Add generated keys
echo "ENCRYPTION_KEY=$ENCRYPTION_KEY" >> .env
echo "JWT_SECRET=$JWT_SECRET" >> .env

echo "Credentials initialized!"
echo "Please edit .env and add your API keys"
```

## Validation Script

Validate all credentials:

```bash
#!/bin/bash
# validate-credentials.sh

node -e "
const { CredentialManager } = require('./src/security/credential-manager');
const cm = CredentialManager.getInstance();

const results = cm.validateAll();

console.log('Credential Validation Results:');
console.log('==============================');
console.log('Total:', results.total);
console.log('Valid:', results.valid);
console.log('Invalid:', results.invalid);
console.log('Missing:', results.missing);
console.log('');

if (results.invalid > 0 || results.missing > 0) {
  console.log('Issues:');
  results.details
    .filter(d => d.status !== 'valid')
    .forEach(d => console.log(\`  - \${d.key}: \${d.status}\`));
  process.exit(1);
} else {
  console.log('✓ All credentials are valid!');
}
"
```

## Troubleshooting

### Missing Credentials

```bash
# Check which credentials are missing
./scripts/validate-system.sh

# Or programmatically
const required = [
  'NDAX_API_KEY',
  'NDAX_API_SECRET',
  'JWT_SECRET',
  'ENCRYPTION_KEY'
];

const check = credentialManager.checkRequired(required);
if (!check.complete) {
  console.error('Missing:', check.missing);
}
```

### Invalid Format

```bash
# Validate specific credential
if (!credentialManager.validate('WALLET_ADDRESS')) {
  console.error('Invalid wallet address format');
  console.log('Expected: 0x followed by 40 hex characters');
}
```

### Decryption Failures

```bash
# If decryption fails, credentials were encrypted with different key
# Solution: Re-save credentials with correct encryption key

# 1. Backup current .env
cp .env .env.backup

# 2. Set correct ENCRYPTION_KEY
# 3. Re-save credentials
node -e "
const cm = require('./src/security/credential-manager').getInstance();
cm.save(false);  // Save without encryption first
"
```

## Migration Guide

### From Plain .env to Encrypted

```javascript
// 1. Load existing credentials
const cm = CredentialManager.getInstance({
  encryptionKey: null  // No encryption initially
});

// 2. Generate encryption key
const crypto = require('crypto');
const encryptionKey = crypto.randomBytes(32).toString('hex');

// 3. Re-initialize with encryption
const cmEncrypted = CredentialManager.createManager({
  encryptionKey
});

// 4. Copy all credentials
for (const [key, value] of cm.credentials.entries()) {
  cmEncrypted.set(key, value, { persist: false });
}

// 5. Save encrypted
cmEncrypted.save(true);

// 6. Add ENCRYPTION_KEY to .env
console.log('Add this to your .env:');
console.log(`ENCRYPTION_KEY=${encryptionKey}`);
```

## API Reference

### Methods

- `get(key, defaultValue)` - Get credential value
- `set(key, value, options)` - Set credential value
- `validate(key, value)` - Validate credential format
- `validateAll()` - Validate all credentials
- `encrypt(value)` - Encrypt a value
- `decrypt(value)` - Decrypt a value
- `save(encrypt)` - Save credentials to .env
- `rotate(key, generator)` - Rotate a credential
- `getRotationStatus()` - Check rotation status
- `getStats()` - Get statistics
- `checkRequired(required)` - Check required credentials

### Events

- `credentialSet` - Credential was set
- `validationFailed` - Validation failed
- `rotated` - Credential was rotated
- `saved` - Credentials were saved
- `error` - Error occurred

## Support

For credential management issues:
1. Check .env file exists and is readable
2. Verify ENCRYPTION_KEY if using encryption
3. Run validation script
4. Check credential format requirements
5. Review error logs
