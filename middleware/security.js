const rateLimit = require('express-rate-limit');
const helmet = require('helmet');
const securityConfig = require('../config/security.config');

// HTTPS Enforcement
function enforceHTTPS(req, res, next) {
  if (process.env.NODE_ENV === 'production' && !req.secure && req.get('x-forwarded-proto') !== 'https') {
    return res.redirect(301, `https://${req.get('host')}${req.url}`);
  }
  next();
}

// Security Headers
function securityHeaders() {
  return helmet(securityConfig.helmet);
}

// Rate Limiting
function rateLimiting() {
  return rateLimit(securityConfig.rateLimit);
}

// CORS Configuration
function corsConfig() {
  return require('cors')(securityConfig.cors);
}

module.exports = {
  enforceHTTPS,
  securityHeaders,
  rateLimiting,
  corsConfig
};
