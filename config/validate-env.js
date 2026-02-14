const requiredEnvVars = [
  'NODE_ENV',
  'DATABASE_URL',
  'API_KEY',
  'SESSION_SECRET'
];

const optionalEnvVars = [
  'PORT',
  'LOG_LEVEL',
  'ALLOWED_ORIGINS',
  'AWS_ACCESS_KEY_ID',
  'AWS_SECRET_ACCESS_KEY'
];

function validateEnvironment() {
  const missing = [];
  const warnings = [];
  
  // Check required variables
  requiredEnvVars.forEach(varName => {
    if (!process.env[varName]) {
      missing.push(varName);
    }
  });
  
  // Check for insecure values
  const insecureValues = ['changeme', 'password', 'test', 'admin', '12345'];
  Object.keys(process.env).forEach(key => {
    if (key.includes('PASSWORD') || key.includes('SECRET') || key.includes('KEY')) {
      if (insecureValues.includes(process.env[key]?.toLowerCase())) {
        warnings.push(`${key} appears to use an insecure default value`);
      }
    }
  });
  
  // Report results
  if (missing.length > 0) {
    console.error('❌ SECURITY ERROR: Missing required environment variables:');
    missing.forEach(v => console.error(`  - ${v}`));
    process.exit(1);
  }
  
  if (warnings.length > 0) {
    console.warn('⚠️  SECURITY WARNING:');
    warnings.forEach(w => console.warn(`  - ${w}`));
  }
  
  console.log('✅ Environment validation passed');
  return true;
}

module.exports = { validateEnvironment };

// Run validation if executed directly
if (require.main === module) {
  validateEnvironment();
}
