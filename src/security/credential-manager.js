/**
 * credential-manager.js - Secure Credential Management
 * 
 * Centralized credential storage, encrypted .env handling, API key validation,
 * and secret rotation for The-basics system.
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { EventEmitter } = require('events');

class CredentialManager extends EventEmitter {
  constructor(options = {}) {
    super();
    
    this.options = {
      envPath: options.envPath || path.join(process.cwd(), '.env'),
      encryptionKey: options.encryptionKey || process.env.ENCRYPTION_KEY,
      validateOnLoad: options.validateOnLoad !== false,
      autoRotate: options.autoRotate || false,
      rotationInterval: options.rotationInterval || 30 * 24 * 60 * 60 * 1000, // 30 days
      ...options
    };
    
    this.credentials = new Map();
    this.validators = new Map();
    this.lastRotation = new Map();
    
    this.setupValidators();
    this.loadCredentials();
    
    console.log('[CredentialManager] Initialized');
  }
  
  setupValidators() {
    // API Key validators
    this.validators.set('NDAX_API_KEY', (value) => {
      return value && value.length >= 32;
    });
    
    this.validators.set('NDAX_API_SECRET', (value) => {
      return value && value.length >= 32;
    });
    
    this.validators.set('HUGGINGFACE_API_KEY', (value) => {
      return value && value.startsWith('hf_');
    });
    
    this.validators.set('OPENAI_API_KEY', (value) => {
      return value && value.startsWith('sk-');
    });
    
    this.validators.set('STRIPE_SECRET_KEY', (value) => {
      return value && (value.startsWith('sk_test_') || value.startsWith('sk_live_'));
    });
    
    // Wallet validators
    this.validators.set('WALLET_ADDRESS', (value) => {
      return value && /^0x[a-fA-F0-9]{40}$/.test(value);
    });
    
    this.validators.set('PRIVATE_KEY', (value) => {
      return value && /^(0x)?[a-fA-F0-9]{64}$/.test(value);
    });
    
    // AWS validators
    this.validators.set('AWS_ACCESS_KEY_ID', (value) => {
      return value && /^AKIA[A-Z0-9]{16}$/.test(value);
    });
    
    this.validators.set('AWS_SECRET_ACCESS_KEY', (value) => {
      return value && value.length === 40;
    });
    
    // Generic validators
    this.validators.set('JWT_SECRET', (value) => {
      return value && value.length >= 32;
    });
    
    this.validators.set('ENCRYPTION_KEY', (value) => {
      return value && value.length === 64; // 32 bytes hex
    });
  }
  
  loadCredentials() {
    try {
      if (!fs.existsSync(this.options.envPath)) {
        console.warn('[CredentialManager] .env file not found');
        return;
      }
      
      const envContent = fs.readFileSync(this.options.envPath, 'utf8');
      const lines = envContent.split('\n');
      
      for (const line of lines) {
        const trimmed = line.trim();
        
        // Skip comments and empty lines
        if (!trimmed || trimmed.startsWith('#')) continue;
        
        const [key, ...valueParts] = trimmed.split('=');
        const value = valueParts.join('=').trim();
        
        if (key && value) {
          this.credentials.set(key.trim(), this.decrypt(value));
          
          // Validate if required
          if (this.options.validateOnLoad) {
            this.validate(key.trim());
          }
        }
      }
      
      console.log('[CredentialManager] Loaded', this.credentials.size, 'credentials');
      
    } catch (error) {
      console.error('[CredentialManager] Failed to load credentials:', error.message);
      this.emit('error', { type: 'load', error });
    }
  }
  
  /**
   * Get a credential value
   */
  get(key, defaultValue = null) {
    // First check in-memory credentials
    if (this.credentials.has(key)) {
      return this.credentials.get(key);
    }
    
    // Fall back to process.env
    if (process.env[key]) {
      return process.env[key];
    }
    
    return defaultValue;
  }
  
  /**
   * Set a credential value
   */
  set(key, value, options = {}) {
    if (!key || value === null || value === undefined) {
      throw new Error('Invalid credential key or value');
    }
    
    // Validate if validator exists
    if (this.validators.has(key)) {
      const isValid = this.validate(key, value);
      if (!isValid && !options.skipValidation) {
        throw new Error(`Invalid credential format for: ${key}`);
      }
    }
    
    this.credentials.set(key, value);
    
    // Also set in process.env for compatibility
    process.env[key] = value;
    
    // Track rotation if enabled
    if (this.options.autoRotate) {
      this.lastRotation.set(key, Date.now());
    }
    
    this.emit('credentialSet', { key, timestamp: new Date().toISOString() });
    
    // Save if requested
    if (options.persist !== false) {
      this.save();
    }
    
    return true;
  }
  
  /**
   * Validate a credential
   */
  validate(key, value = null) {
    const validator = this.validators.get(key);
    
    if (!validator) {
      // No validator defined, consider it valid
      return true;
    }
    
    const credValue = value || this.get(key);
    
    if (!credValue) {
      console.warn(`[CredentialManager] Missing credential: ${key}`);
      return false;
    }
    
    try {
      const isValid = validator(credValue);
      
      if (!isValid) {
        console.error(`[CredentialManager] Validation failed for: ${key}`);
        this.emit('validationFailed', { key, timestamp: new Date().toISOString() });
      }
      
      return isValid;
      
    } catch (error) {
      console.error(`[CredentialManager] Validation error for ${key}:`, error.message);
      return false;
    }
  }
  
  /**
   * Validate all credentials
   */
  validateAll() {
    const results = {
      total: 0,
      valid: 0,
      invalid: 0,
      missing: 0,
      details: []
    };
    
    for (const [key, validator] of this.validators.entries()) {
      results.total++;
      
      const value = this.get(key);
      
      if (!value) {
        results.missing++;
        results.details.push({ key, status: 'missing' });
        continue;
      }
      
      const isValid = this.validate(key, value);
      
      if (isValid) {
        results.valid++;
        results.details.push({ key, status: 'valid' });
      } else {
        results.invalid++;
        results.details.push({ key, status: 'invalid' });
      }
    }
    
    return results;
  }
  
  /**
   * Encrypt a value
   */
  encrypt(value) {
    if (!this.options.encryptionKey) {
      // No encryption key, return as-is
      return value;
    }
    
    try {
      const algorithm = 'aes-256-gcm';
      const key = Buffer.from(this.options.encryptionKey, 'hex');
      const iv = crypto.randomBytes(16);
      
      const cipher = crypto.createCipheriv(algorithm, key, iv);
      
      let encrypted = cipher.update(value, 'utf8', 'hex');
      encrypted += cipher.final('hex');
      
      const authTag = cipher.getAuthTag();
      
      // Return format: iv:authTag:encrypted
      return `${iv.toString('hex')}:${authTag.toString('hex')}:${encrypted}`;
      
    } catch (error) {
      console.error('[CredentialManager] Encryption failed:', error.message);
      return value;
    }
  }
  
  /**
   * Decrypt a value
   */
  decrypt(value) {
    if (!this.options.encryptionKey || !value.includes(':')) {
      // Not encrypted or no key
      return value;
    }
    
    try {
      const parts = value.split(':');
      if (parts.length !== 3) {
        // Not in encrypted format
        return value;
      }
      
      const [ivHex, authTagHex, encrypted] = parts;
      const algorithm = 'aes-256-gcm';
      const key = Buffer.from(this.options.encryptionKey, 'hex');
      const iv = Buffer.from(ivHex, 'hex');
      const authTag = Buffer.from(authTagHex, 'hex');
      
      const decipher = crypto.createDecipheriv(algorithm, key, iv);
      decipher.setAuthTag(authTag);
      
      let decrypted = decipher.update(encrypted, 'hex', 'utf8');
      decrypted += decipher.final('utf8');
      
      return decrypted;
      
    } catch (error) {
      console.error('[CredentialManager] Decryption failed:', error.message);
      return value;
    }
  }
  
  /**
   * Save credentials to .env file
   */
  save(encrypt = false) {
    try {
      const lines = ['# The-basics System Credentials', '# Auto-generated - Do not edit manually', ''];
      
      // Group credentials by category
      const categories = {
        'Node.js': ['NODE_ENV', 'PORT'],
        'Python': ['PYTHON_PORT'],
        'Trading': ['TRADING_MODE', 'AUTO_START', 'MAX_TRADES', 'RISK_LEVEL', 'NDAX_API_KEY', 'NDAX_API_SECRET', 'NDAX_USER_ID'],
        'AI Platforms': ['HUGGINGFACE_API_KEY', 'OPENAI_API_KEY', 'MTURK_ACCESS_KEY', 'MTURK_SECRET_KEY', 'APPEN_API_KEY', 'RAPIDAPI_KEY'],
        'Freelance': ['UPWORK_CLIENT_ID', 'UPWORK_CLIENT_SECRET', 'FIVERR_API_KEY', 'FREELANCER_API_KEY'],
        'Blockchain': ['WALLET_ADDRESS', 'PRIVATE_KEY', 'WALLET_SEED_PHRASE'],
        'AWS': ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_REGION'],
        'Payments': ['STRIPE_SECRET_KEY', 'STRIPE_WEBHOOK_SECRET'],
        'Security': ['ENCRYPTION_KEY', 'JWT_SECRET'],
        'Database': ['DATABASE_URL'],
        'Frontend': ['VITE_API_URL']
      };
      
      for (const [category, keys] of Object.entries(categories)) {
        const categoryHasValues = keys.some(key => this.credentials.has(key));
        
        if (categoryHasValues) {
          lines.push(`# ${category}`);
          
          for (const key of keys) {
            if (this.credentials.has(key)) {
              const value = this.credentials.get(key);
              const finalValue = encrypt ? this.encrypt(value) : value;
              lines.push(`${key}=${finalValue}`);
            }
          }
          
          lines.push('');
        }
      }
      
      // Add any other credentials not in categories
      for (const [key, value] of this.credentials.entries()) {
        const isInCategory = Object.values(categories).some(keys => keys.includes(key));
        if (!isInCategory) {
          const finalValue = encrypt ? this.encrypt(value) : value;
          lines.push(`${key}=${finalValue}`);
        }
      }
      
      fs.writeFileSync(this.options.envPath, lines.join('\n'), 'utf8');
      console.log('[CredentialManager] Credentials saved');
      
      this.emit('saved', { timestamp: new Date().toISOString() });
      
    } catch (error) {
      console.error('[CredentialManager] Failed to save credentials:', error.message);
      this.emit('error', { type: 'save', error });
    }
  }
  
  /**
   * Rotate a credential (generate new value)
   */
  rotate(key, generator = null) {
    const defaultGenerator = () => {
      return crypto.randomBytes(32).toString('hex');
    };
    
    const newValue = generator ? generator() : defaultGenerator();
    
    this.set(key, newValue);
    this.lastRotation.set(key, Date.now());
    
    console.log(`[CredentialManager] Rotated credential: ${key}`);
    this.emit('rotated', { key, timestamp: new Date().toISOString() });
    
    return newValue;
  }
  
  /**
   * Check which credentials need rotation
   */
  getRotationStatus() {
    const needsRotation = [];
    
    for (const [key, lastRotated] of this.lastRotation.entries()) {
      const age = Date.now() - lastRotated;
      
      if (age > this.options.rotationInterval) {
        needsRotation.push({
          key,
          lastRotated: new Date(lastRotated).toISOString(),
          age: Math.floor(age / (24 * 60 * 60 * 1000)) + ' days'
        });
      }
    }
    
    return needsRotation;
  }
  
  /**
   * Get credential statistics
   */
  getStats() {
    return {
      total: this.credentials.size,
      validated: this.validators.size,
      validationResults: this.validateAll(),
      rotationStatus: this.getRotationStatus()
    };
  }
  
  /**
   * Check if all required credentials are present
   */
  checkRequired(required = []) {
    const missing = [];
    
    for (const key of required) {
      if (!this.get(key)) {
        missing.push(key);
      }
    }
    
    return {
      complete: missing.length === 0,
      missing
    };
  }
}

// Singleton instance
let instance = null;

module.exports = {
  CredentialManager,
  getInstance: (options) => {
    if (!instance) {
      instance = new CredentialManager(options);
    }
    return instance;
  },
  createManager: (options) => new CredentialManager(options)
};
