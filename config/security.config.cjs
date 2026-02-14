module.exports = {
  // Rate Limiting
  rateLimit: {
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // Max requests per window
    message: 'Too many requests, please try again later.'
  },
  
  // CORS Configuration
  cors: {
    origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
    credentials: true,
    optionsSuccessStatus: 200
  },
  
  // Session Security
  session: {
    secret: (() => {
      if (process.env.NODE_ENV === 'production' && !process.env.SESSION_SECRET) {
        throw new Error('SESSION_SECRET environment variable is required in production. Generate one with: node -e "console.log(require(\'crypto\').randomBytes(32).toString(\'hex\'))"');
      }
      return process.env.SESSION_SECRET || require('crypto').randomBytes(32).toString('hex');
    })(),
    resave: false,
    saveUninitialized: false,
    cookie: {
      secure: process.env.NODE_ENV === 'production', // HTTPS only in production
      httpOnly: true,
      maxAge: 24 * 60 * 60 * 1000, // 24 hours
      sameSite: 'strict'
    }
  },
  
  // Helmet Security Headers
  helmet: {
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        styleSrc: ["'self'", "'unsafe-inline'"],
        scriptSrc: ["'self'"],
        imgSrc: ["'self'", "data:", "https:"],
        // Allow HTTP localhost in development for backend API connections
        // In production, this falls back to 'self' (HTTPS only)
        connectSrc: ["'self'", process.env.API_URL || (process.env.NODE_ENV === 'production' ? "'self'" : "http://localhost:8000")],
        fontSrc: ["'self'"],
        objectSrc: ["'none'"],
        mediaSrc: ["'self'"],
        frameSrc: ["'none'"],
      },
    },
    hsts: {
      maxAge: 31536000, // 1 year
      includeSubDomains: true,
      preload: true
    }
  },
  
  // API Security
  api: {
    timeout: 30000, // 30 seconds
    maxPayloadSize: '10kb',
    enableCORS: true
  }
};
