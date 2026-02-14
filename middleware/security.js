import rateLimit from 'express-rate-limit';
import helmet from 'helmet';
import cors from 'cors';

// Default security configuration (can be overridden by importing config)
const securityConfig = {
  helmet: {
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        styleSrc: ["'self'", "'unsafe-inline'"],
        scriptSrc: ["'self'"],
        imgSrc: ["'self'", "data:", "https:"],
        connectSrc: ["'self'", process.env.API_URL || (process.env.NODE_ENV === 'production' ? "'self'" : "http://localhost:8000")],
        fontSrc: ["'self'"],
        objectSrc: ["'none'"],
        mediaSrc: ["'self'"],
        frameSrc: ["'none'"],
      },
    },
    hsts: {
      maxAge: 31536000,
      includeSubDomains: true,
      preload: true
    }
  },
  rateLimit: {
    windowMs: 15 * 60 * 1000,
    max: 100,
    message: 'Too many requests, please try again later.'
  },
  cors: {
    origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
    credentials: true,
    optionsSuccessStatus: 200
  }
};

// Export constants for testing
export const RATE_LIMIT_MAX = securityConfig.rateLimit.max;

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
  return cors(securityConfig.cors);
}

export {
  enforceHTTPS,
  securityHeaders,
  rateLimiting,
  corsConfig
};

